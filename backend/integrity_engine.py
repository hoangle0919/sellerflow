"""Application-integrity screening for merchant submissions.

Deterministic, rule-based checks for misrepresentation and first-party
fraud risk in self-reported merchant data. This is NOT a supervised fraud
model: no labeled fraud outcomes exist yet, so every check here is an
explainable consistency or plausibility rule, and is disclosed as such in
the API response. When adjudicated outcomes accumulate (see the outcomes
table), these rules become the feature seed for a learned fraud score.

Design rule: integrity findings never silently alter the credit decision.
They are a parallel screen surfaced to the lender alongside the credit
assessment — unification happens in the submission pipeline and the lender
view, not by quietly blending two unproven scores.
"""

DISCLOSURE = (
    "Rule-based integrity screening on self-reported data. Not a supervised "
    "fraud model — no labeled fraud outcomes exist yet. Checks are "
    "deterministic and each finding lists its evidence."
)


def _check(name, status, severity, evidence, why):
    return {
        "check": name,
        "status": status,          # "pass" | "flag"
        "severity": severity,      # "info" | "low" | "medium" | "high"
        "evidence": evidence,
        "why_it_matters": why,
    }


def revenue_reconciliation(features):
    """Claimed revenue should roughly equal orders x average order value."""
    implied = features["order_volume"] * features["avg_order_value"]
    claimed = features["monthly_revenue"]
    if implied <= 0:
        return _check(
            "Revenue reconciliation", "flag", "medium",
            "Order volume x average order value is zero — cannot reconcile claimed revenue.",
            "Revenue that cannot be reconstructed from order activity cannot be verified against platform data.",
        )
    ratio = claimed / implied
    evidence = (
        f"Claimed {claimed:,.0f} vs implied {implied:,.0f} "
        f"({features['order_volume']} orders x {features['avg_order_value']:,.0f} AOV) — ratio {ratio:.2f}"
    )
    if 0.55 <= ratio <= 1.75:
        return _check(
            "Revenue reconciliation", "pass", "info", evidence,
            "Claimed revenue is consistent with reported order activity.",
        )
    severity = "high" if (ratio > 2.5 or ratio < 0.35) else "medium"
    return _check(
        "Revenue reconciliation", "flag", severity, evidence,
        "Revenue far from orders x AOV suggests inflated revenue or misreported order data — "
        "the most common form of application misrepresentation in merchant financing.",
    )


def quality_consistency(features):
    """A near-perfect rating is contradicted by high returns or late shipments."""
    rating = features["rating"]
    ret = features["return_rate"]
    late = features["late_ship_rate"]
    contradictions = []
    if rating >= 4.7 and ret >= 0.12:
        contradictions.append(f"{rating:.1f} rating with {ret:.0%} returns")
    if rating >= 4.7 and late >= 0.10:
        contradictions.append(f"{rating:.1f} rating with {late:.0%} late shipments")
    if not contradictions:
        return _check(
            "Quality-signal consistency", "pass", "info",
            f"{rating:.1f} rating, {ret:.1%} returns, {late:.1%} late shipments.",
            "Customer-facing quality signals agree with each other.",
        )
    return _check(
        "Quality-signal consistency", "flag", "medium",
        "; ".join(contradictions),
        "Platforms rarely sustain near-perfect ratings alongside poor fulfillment — "
        "the combination suggests a manipulated or purchased rating.",
    )


def exposure_velocity(features):
    """New store already carrying stacked obligations, or implausible scale for its age."""
    days = features["days_active"]
    loans = features["previous_loans"]
    rev = features["monthly_revenue"]
    if days < 90 and loans >= 2:
        return _check(
            "Exposure velocity", "flag", "high",
            f"{loans} prior financing arrangements within {days:.0f} days of platform history.",
            "Rapid stacking of obligations on a young store is a classic first-party fraud "
            "pattern: raise as much as possible before the first default is visible.",
        )
    if days < 60 and rev > 500_000_000:
        return _check(
            "Exposure velocity", "flag", "medium",
            f"{rev:,.0f} monthly revenue claimed within {days:.0f} days of opening.",
            "Organic stores rarely reach this scale this quickly; sudden-scale claims need "
            "platform-verified payout data before they can support an advance.",
        )
    return _check(
        "Exposure velocity", "pass", "info",
        f"{days:.0f} days active, {loans} prior financing arrangement(s).",
        "Obligations and scale are proportionate to operating history.",
    )


def growth_plausibility(features):
    """Sustained hypergrowth claims on a mature store."""
    growth = features["revenue_growth"]
    days = features["days_active"]
    if growth >= 0.45 and days >= 720:
        return _check(
            "Growth plausibility", "flag", "low",
            f"{growth:+.0%} month-over-month claimed on a store {days:.0f} days old.",
            "Mature stores rarely sustain hypergrowth; the figure may be a one-month spike "
            "presented as a trend. Revenue history would resolve this.",
        )
    return _check(
        "Growth plausibility", "pass", "info",
        f"{growth:+.0%} month-over-month on {days:.0f} days of history.",
        "Reported growth is plausible for the store's age.",
    )


def resubmission_divergence(features, prior_submissions):
    """Same shop or phone resubmitted with materially different revenue figures.

    prior_submissions: iterable of dicts with at least monthly_revenue —
    the caller queries recent submissions matching shop name or phone.
    """
    if not prior_submissions:
        return _check(
            "Resubmission consistency", "pass", "info",
            "No prior submission on record for this shop name or phone.",
            "First-time submissions have no history to diverge from.",
        )
    claimed = features["monthly_revenue"]
    worst = None
    for prior in prior_submissions:
        prev = prior.get("monthly_revenue") or 0
        if prev <= 0:
            continue
        delta = abs(claimed - prev) / prev
        if worst is None or delta > worst[0]:
            worst = (delta, prev)
    if worst is None or worst[0] <= 0.30:
        return _check(
            "Resubmission consistency", "pass", "info",
            f"{len(prior_submissions)} prior submission(s); figures within 30% of history.",
            "Repeat submissions tell a consistent story.",
        )
    return _check(
        "Resubmission consistency", "flag", "high",
        f"Claimed {claimed:,.0f} vs {worst[1]:,.0f} on a prior submission "
        f"({worst[0]:.0%} divergence).",
        "The same merchant reporting materially different revenue across submissions "
        "is direct evidence of misreporting on at least one of them.",
    )


def screen_integrity(features, prior_submissions=None):
    """Run all checks. prior_submissions=None means the DB-backed check is
    unavailable (e.g. the keyless preview endpoint) and is skipped rather
    than silently passed."""
    checks = [
        revenue_reconciliation(features),
        quality_consistency(features),
        exposure_velocity(features),
        growth_plausibility(features),
    ]
    if prior_submissions is not None:
        checks.append(resubmission_divergence(features, prior_submissions))

    flags = [c for c in checks if c["status"] == "flag"]
    high = any(c["severity"] == "high" for c in flags)
    medium = any(c["severity"] == "medium" for c in flags)
    level = "high" if high else ("review" if medium else ("watch" if flags else "clear"))
    return {
        "level": level,               # clear | watch | review | high
        "checks_run": len(checks),
        "flags": len(flags),
        "checks": checks,
        "method": "deterministic_rules",
        "disclosure": DISCLOSURE,
    }
