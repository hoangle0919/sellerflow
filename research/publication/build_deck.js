/* Builds RBF_DECK.pptx from the registered figures.
 *
 * Every number on a slide carries a source note naming the canonical artifact.
 * The claim-ledger rules are enforced here the same way they are in the paper:
 * seller burden never appears without provider recovery; f = 1.20 never appears
 * without f* = 1.0945; the RBF-G floor null never appears without the live
 * ceiling; and no slide asserts predictive validity, affordability, or default
 * prevention.
 *
 * Palette: Okabe-Ito categorical, the same colourblind-safe non-valenced set the
 * Simulation Lab uses (D-033). Colour distinguishes arms; it never encodes good
 * or bad.
 */
const pptxgen = require("pptxgenjs");

const INK = "1A1A1A", PAPER = "FFFFFF", MUTED = "6B6B6B", RULE = "D8D8D8";
const RBF = "0072B2";   // blue      — revenue-contingent
const FIXA = "E69F00";  // orange    — matched fixed
const FIXB = "009E73";  // green     — amortizing reference
const WARN = "D55E00";  // vermillion — failure cases

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                // 13.3 x 7.5
pres.author = "RBF research";
pres.title = "Revenue-Contingent Financing Under Volatile Sales";

const SRC = (s) => ({ text: s, options: { fontSize: 9, color: MUTED, italic: true } });

function darkSlide() { const s = pres.addSlide(); s.background = { color: INK }; return s; }
function lightSlide() { const s = pres.addSlide(); s.background = { color: PAPER }; return s; }

function title(s, t, color) {
  s.addText(t, { x: 0.7, y: 0.45, w: 11.9, h: 0.9, fontSize: 32, bold: true,
                 color: color || INK, fontFace: "Cambria", margin: 0 });
}
function source(s, t) {
  s.addText(t, { x: 0.7, y: 6.85, w: 11.9, h: 0.4, fontSize: 9, color: MUTED,
                 italic: true, fontFace: "Calibri", margin: 0 });
}

/* ─────────────────────────── 1. Title ─────────────────────────── */
{
  const s = darkSlide();
  s.addText("Revenue-Contingent Financing\nUnder Volatile Sales", {
    x: 0.9, y: 1.9, w: 11.5, h: 1.9, fontSize: 40, bold: true, color: PAPER,
    fontFace: "Cambria", lineSpacing: 46, margin: 0 });
  s.addText("Separating price from structure in a paired simulation study", {
    x: 0.9, y: 3.9, w: 11.5, h: 0.5, fontSize: 19, color: "CFCFCF",
    fontFace: "Calibri", margin: 0 });
  s.addShape(pres.ShapeType.rect, { x: 0.9, y: 4.7, w: 1.6, h: 0.045, fill: { color: RBF } });
  s.addText("All figures are simulation output under modelled assumptions.\nNo observed seller revenue, repayment or default outcome exists in this study.", {
    x: 0.9, y: 5.1, w: 11.5, h: 0.8, fontSize: 13, color: "9A9A9A",
    fontFace: "Calibri", lineSpacing: 20, margin: 0 });
  s.addNotes("Opening frame: this is a study of contract mechanics, not a claim about sellers. Say the disclaimer out loud — it is the reason the rest is credible.");
}

/* ───────────────── 2. One mechanism, two faces ───────────────── */
{
  const s = lightSlide();
  title(s, "One mechanism, seen from two sides");
  const card = (x, c, head, body) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.8, w: 5.6, h: 2.75, rectRadius: 0.08,
      fill: { color: "FAFAFA" }, line: { color: RULE, width: 1 } });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.45, y: 2.1, w: 0.5, h: 0.5, fill: { color: c } });
    s.addText(head, { x: x + 1.12, y: 2.14, w: 4.2, h: 0.42, fontSize: 19, bold: true,
      color: INK, fontFace: "Cambria", margin: 0 });
    s.addText(body, { x: x + 0.45, y: 2.72, w: 4.8, h: 1.6, fontSize: 14.5, color: "333333",
      fontFace: "Calibri", lineSpacing: 22, margin: 0 });
  };
  card(0.7, RBF, "For the seller",
       "Each payment is a fixed share of revenue, so the payment falls when revenue falls. Under adverse paths the payment burden stays roughly flat.");
  card(7.0, WARN, "For the financier",
       "The same mechanism delays recovery, and where revenue stops before the cap is reached, a contractual balance goes unrecovered.");
  s.addText("Reporting either side alone misstates the contract. This paper reports both, always.",
    { x: 0.7, y: 5.0, w: 11.9, h: 0.5, fontSize: 17, bold: true, color: INK,
      fontFace: "Calibri", margin: 0 });
  s.addNotes("The whole argument in one slide. The two cards are the same fact.");
}

/* ───────────────── 3. Why a simulation ───────────────── */
{
  const s = lightSlide();
  title(s, "Why a simulation, and what it costs");
  s.addText([
    { text: "The question needs a counterfactual that does not exist.", options: { bold: true, breakLine: true } },
    { text: "Comparing seller burden and provider recovery under two contracts requires observing both contracts on the same seller, over the same realised revenue. Each seller takes at most one contract.", options: { breakLine: true } },
  ], { x: 0.7, y: 1.75, w: 7.3, h: 1.35, fontSize: 15, color: "333333", fontFace: "Calibri", lineSpacing: 22, margin: 0 });
  s.addText([
    { text: "A paired design supplies it by construction", options: { bold: true, bullet: true, breakLine: true } },
    { text: "every arm runs on the identical generated path; all comparisons are within-path", options: { bullet: true, breakLine: true } },
    { text: "500 paths per scenario, fixed seeds, specification frozen before any outcome analysis", options: { bullet: true, breakLine: true } },
    { text: "the cost: the revenue process is one we specified — results describe contract mechanics, not seller behaviour", options: { bullet: true } },
  ], { x: 0.7, y: 3.2, w: 7.3, h: 2.8, fontSize: 14, color: "333333", fontFace: "Calibri", paraSpaceAfter: 8, margin: 0 });

  s.addShape(pres.ShapeType.roundRect, { x: 8.5, y: 1.75, w: 4.1, h: 4.3, rectRadius: 0.08,
    fill: { color: "F4F4F4" }, line: { color: RULE, width: 1 } });
  s.addText("What we searched for and did not find", { x: 8.85, y: 2.0, w: 3.4, h: 0.4,
    fontSize: 14, bold: true, color: INK, fontFace: "Cambria", margin: 0 });
  s.addText([
    { text: "No head-to-head comparison of seller burden and provider recovery under revenue-contingent versus cost-matched fixed schedules for small-business financing.", options: { breakLine: true } },
    { text: "No peer-reviewed study of the US merchant cash advance market.", options: {} },
  ], { x: 8.85, y: 2.5, w: 3.4, h: 2.7, fontSize: 12, color: "333333", fontFace: "Calibri", lineSpacing: 17, paraSpaceAfter: 8, margin: 0 });
  s.addText("Scoped to searches documented through 2026-08-13 — a statement about our searches, not about the field.",
    { x: 8.85, y: 5.35, w: 3.4, h: 0.6, fontSize: 10, italic: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addNotes("Be precise about the negative claim. It is scoped to our searches, and that scoping is deliberate.");
}

/* ───────────────── 4. The design ───────────────── */
{
  const s = lightSlide();
  title(s, "Three arms, matched on cost");
  const arm = (x, c, name, def, note) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.85, w: 3.7, h: 3.3, rectRadius: 0.08,
      fill: { color: "FAFAFA" }, line: { color: RULE, width: 1 } });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.32, y: 2.12, w: 0.4, h: 0.4, fill: { color: c } });
    s.addText(name, { x: x + 0.88, y: 2.13, w: 2.6, h: 0.38, fontSize: 16, bold: true, color: INK, fontFace: "Cambria", margin: 0 });
    s.addText(def, { x: x + 0.32, y: 2.68, w: 3.06, h: 1.15, fontSize: 13, color: "333333", fontFace: "Calibri", lineSpacing: 19, margin: 0 });
    s.addText(note, { x: x + 0.32, y: 3.92, w: 3.06, h: 1.0, fontSize: 11, color: MUTED, italic: true, fontFace: "Calibri", lineSpacing: 16, margin: 0 });
  };
  arm(0.7, RBF, "Revenue-contingent", "Pays r × revenue each month until a cap of A × f is reached.", "Cap factor f is the price. r = 0.10.");
  arm(4.80, FIXA, "Matched fixed", "Fixed instalment. Same principal, same total, same term on the reference path.", "Only the timing of payments differs. This is the primary comparison.");
  arm(8.90, FIXB, "Illustrative reference", "18% nominal, 12-month amortizing schedule.", "The 18% is an assumed input — not a market rate, not observed.");
  s.addText("At f = 1.20 the matched term is 13 months at 17,076,923 VND/month; at f* = 1.0945 it is 12 months at 16,873,542 VND/month.",
    { x: 0.7, y: 5.35, w: 11.9, h: 0.5, fontSize: 14, bold: true, color: INK, fontFace: "Calibri", margin: 0 });
  source(s, "baseline_v2_canonical.json and baseline_equalcost_v1_canonical.json → /match_benchmark_a");
  s.addNotes("Matched on the reference path means principal, total and term are equal — so the comparison isolates timing.");
}

/* ───────────────── 5. The headline result — paired ───────────────── */
{
  const s = lightSlide();
  title(s, "Severe downturn: the trade-off, both halves");
  s.addChart(pres.ChartType.bar, [
    { name: "Months above 15% burden", labels: ["Revenue-contingent", "Matched fixed"], values: [0.0, 6.85] },
  ], { x: 0.7, y: 1.7, w: 5.7, h: 3.5, barDir: "col", chartColors: [RBF, FIXA],
       showTitle: true, title: "Seller: months above a 15% burden band", titleFontSize: 13, titleColor: INK,
       showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 13, dataLabelColor: INK,
       showLegend: false, catAxisLabelColor: "444444", valAxisLabelColor: "444444",
       valGridLine: { color: "EDEDED", size: 1 }, catGridLine: { style: "none" },
       valAxisMinVal: 0, valAxisMaxVal: 8, valAxisMajorUnit: 2,
       dataLabelFormatCode: "0.00",
       catAxisLabelFontSize: 11, valAxisLabelFontSize: 11 });
  s.addChart(pres.ChartType.bar, [
    { name: "Recovery by month 12 (%)", labels: ["Revenue-contingent", "Matched fixed"], values: [65.46, 92.31] },
  ], { x: 6.9, y: 1.7, w: 5.7, h: 3.5, barDir: "col", chartColors: [RBF, FIXA],
       showTitle: true, title: "Provider: share of target recovered by month 12", titleFontSize: 13, titleColor: INK,
       showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 13, dataLabelColor: INK,
       showLegend: false, catAxisLabelColor: "444444", valAxisLabelColor: "444444",
       valGridLine: { color: "EDEDED", size: 1 }, catGridLine: { style: "none" },
       valAxisMinVal: 0, valAxisMaxVal: 110, valAxisMajorUnit: 20,
       dataLabelFormatCode: "0.00",
       catAxisLabelFontSize: 11, valAxisLabelFontSize: 11 });
  s.addText("The burden reduction and the recovery delay are one mechanism. Mean duration extends 13 → 18.718 months.",
    { x: 0.7, y: 5.45, w: 11.9, h: 0.45, fontSize: 15, bold: true, color: INK, fontFace: "Calibri", margin: 0 });
  s.addText("15% is an illustrative reporting band chosen for this study, not a validated hardship cutoff. Burden is payment ÷ GMV. The fixed arm is scheduled recovery under an assumption of full, on-time payment.",
    { x: 0.7, y: 5.95, w: 11.9, h: 0.7, fontSize: 11, color: MUTED, fontFace: "Calibri", lineSpacing: 16, margin: 0 });
  source(s, "baseline_v2_canonical.json → /scenarios/severe_downturn   ·   claim-ledger S-1, I-3");
  s.addNotes("Never show the left chart without the right one. That pairing is the paper's central discipline.");
}

/* ───────────────── 6. Price vs structure ───────────────── */
{
  const s = lightSlide();
  title(s, "Price and payment rule are separable — and both matter");
  const box = (x, c, head, big, sub) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.8, w: 5.6, h: 2.5, rectRadius: 0.08,
      fill: { color: "FAFAFA" }, line: { color: RULE, width: 1 } });
    s.addText(head, { x: x + 0.4, y: 2.05, w: 4.8, h: 0.4, fontSize: 14, bold: true, color: c, fontFace: "Calibri", margin: 0 });
    s.addText(big, { x: x + 0.4, y: 2.5, w: 4.8, h: 0.9, fontSize: 40, bold: true, color: INK, fontFace: "Cambria", margin: 0 });
    s.addText(sub, { x: x + 0.4, y: 3.45, w: 4.8, h: 0.65, fontSize: 12, color: "444444", fontFace: "Calibri", lineSpacing: 17, margin: 0 });
  };
  box(0.7, RBF, "ILLUSTRATIVE CAP", "f = 1.20", "Substantially more expensive than the 18% amortizing reference.");
  box(7.0, FIXB, "NEAREST GRID MATCH", "f* = 1.0945", "19.537656% against the reference's 19.561817% — residual ≈ 0.02416pp. Not an exact match: duration is integer-valued.");
  s.addText([
    { text: "Unchanged by price:  ", options: { bold: true } },
    { text: "the pre-cap payment rule — each payment is the same share of net sales.", options: { breakLine: true } },
    { text: "Changed by price:  ", options: { bold: true } },
    { text: "the contractual target, and therefore completion timing, terminal clipping and the realised stream.", options: {} },
  ], { x: 0.7, y: 4.55, w: 11.9, h: 1.2, fontSize: 15, color: "333333", fontFace: "Calibri", lineSpacing: 23, margin: 0 });
  s.addText("Analytically separable — but they jointly determine outcomes. A cost ratio quoted at a single cap factor is a pricing result, not a property of revenue-contingent repayment.",
    { x: 0.7, y: 5.8, w: 11.9, h: 0.7, fontSize: 13, italic: true, color: INK, fontFace: "Calibri", lineSpacing: 18, margin: 0 });
  source(s, "validation_v1_canonical.json → /pricing   ·   claim-ledger P-1, P-2");
  s.addNotes("This is the contribution. Both halves of the last line matter — separable is not the same as outcome-independent.");
}

/* ───────────────── 7. The retraction ───────────────── */
{
  const s = lightSlide();
  title(s, "A retraction we report as part of the result");
  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 1.8, w: 11.9, h: 1.5, rectRadius: 0.08,
    fill: { color: "FDF3EF" }, line: { color: WARN, width: 1.5 } });
  s.addText('"RBF costs approximately 2.3× the interest of a conventional loan."', {
    x: 1.1, y: 2.05, w: 11.1, h: 0.5, fontSize: 20, italic: true, color: "6B2E12", fontFace: "Cambria", margin: 0 });
  s.addText("WITHDRAWN — and the reason is this slide deck's argument.", {
    x: 1.1, y: 2.65, w: 11.1, h: 0.4, fontSize: 14, bold: true, color: WARN, fontFace: "Calibri", margin: 0 });
  s.addText([
    { text: "It fixed f = 1.20 as though it were intrinsic — total contractual cost is proportional to f.", options: { bullet: true, breakLine: true } },
    { text: "It quoted one effective APR as though it were a contract property — APR is jointly determined by the price and the revenue path.", options: { bullet: true, breakLine: true } },
    { text: "It survived several drafts, written by authors actively trying to avoid exactly this error.", options: { bullet: true } },
  ], { x: 0.7, y: 3.55, w: 11.7, h: 1.9, fontSize: 15, color: "333333", fontFace: "Calibri", paraSpaceAfter: 10, margin: 0 });
  s.addText("We report the retraction rather than quietly correcting it, because it is the concrete instance of the conflation the paper argues against.",
    { x: 0.7, y: 5.45, w: 11.9, h: 0.7, fontSize: 14, bold: true, color: INK, fontFace: "Calibri", lineSpacing: 19, margin: 0 });
  s.addNotes("Interviewers respond well to this slide. It demonstrates the discipline rather than asserting it.");
}

/* ───────────────── 8. Where recovery fails ───────────────── */
{
  const s = lightSlide();
  title(s, "Where recovery actually fails");
  s.addChart(pres.ChartType.bar, [
    { name: "f = 1.20", labels: ["Closure, month 7", "Closure, month 13", "Temporary closure"], values: [100.0, 76.2, 2.0] },
    { name: "f* = 1.0945", labels: ["Closure, month 7", "Closure, month 13", "Temporary closure"], values: [100.0, 7.6, 0.0] },
  ], { x: 0.7, y: 1.7, w: 11.9, h: 3.4, barDir: "col", chartColors: [RBF, FIXB],
       showTitle: true, title: "Share of simulated paths not reaching the contractual target (%)",
       titleFontSize: 13, titleColor: INK,
       showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: INK,
       showLegend: true, legendPos: "t", legendFontSize: 11,
       catAxisLabelColor: "444444", valAxisLabelColor: "444444",
       valGridLine: { color: "EDEDED", size: 1 }, catGridLine: { style: "none" },
       valAxisMinVal: 0, valAxisMaxVal: 110, valAxisMajorUnit: 20,
       dataLabelFormatCode: "0.0",
       catAxisLabelFontSize: 11, valAxisLabelFontSize: 11 });
  s.addText([
    { text: "Timing decides it, not zero revenue as such. ", options: { bold: true } },
    { text: "A temporary three-month cessation leaves 2.0% of paths incomplete at f = 1.20 and none at f*. Permanent closure before the 13-month matched term leaves every path incomplete.", options: {} },
  ], { x: 0.7, y: 5.3, w: 11.9, h: 0.9, fontSize: 14, color: "333333", fontFace: "Calibri", lineSpacing: 20, margin: 0 });
  source(s, "baseline_closure_v1 and baseline_closure_equalcost_v1 → /scenarios/*/RBF   ·   claim-ledger S-3, S-4");
  s.addNotes("Note the price effect: closure_m13 falls from 76.2% to 7.6% on the cap factor alone. Same structure, nearer threshold.");
}

/* ───────────────── 9. Incomplete recovery ≠ principal loss ───────────────── */
{
  const s = lightSlide();
  title(s, "Incomplete recovery is not principal loss");
  const row = (y, label, rate, amt, verdict, c) => {
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 11.9, h: 1.15, rectRadius: 0.06,
      fill: { color: "FAFAFA" }, line: { color: RULE, width: 1 } });
    s.addShape(pres.ShapeType.ellipse, { x: 1.05, y: y + 0.36, w: 0.4, h: 0.4, fill: { color: c } });
    s.addText(label, { x: 1.65, y: y + 0.15, w: 2.9, h: 0.85, fontSize: 15, bold: true, color: INK, fontFace: "Cambria", valign: "middle", margin: 0 });
    s.addText(rate, { x: 4.6, y: y + 0.15, w: 2.4, h: 0.85, fontSize: 14, color: "333333", fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(amt, { x: 7.1, y: y + 0.15, w: 2.7, h: 0.85, fontSize: 14, color: "333333", fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(verdict, { x: 9.9, y: y + 0.15, w: 2.5, h: 0.85, fontSize: 13, bold: true, color: c, fontFace: "Calibri", valign: "middle", margin: 0 });
  };
  s.addText("Scenario", { x: 1.65, y: 1.78, w: 2.9, h: 0.3, fontSize: 11, bold: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addText("Not reaching target", { x: 4.6, y: 1.78, w: 2.4, h: 0.3, fontSize: 11, bold: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addText("Amount recovered", { x: 7.1, y: 1.78, w: 2.7, h: 0.3, fontSize: 11, bold: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addText("vs 185M advance", { x: 9.9, y: 1.78, w: 2.5, h: 0.3, fontSize: 11, bold: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  row(2.28, "Closure, month 13", "76.2% of paths", "≈ 214.3M VND", "principal covered", FIXB);
  row(3.78, "Closure, month 7", "100% of paths", "≈ 98.3M VND", "principal shortfall", WARN);
  s.addText([
    { text: "A 76.2% incomplete-recovery rate is not a 76.2% loss rate.", options: { bold: true, breakLine: true } },
    { text: "Incomplete recovery means the contractual target was not reached. Whether that touches principal depends on how much was recovered. Closure at month 7 recovers the same absolute amount at both cap factors — that path is revenue-limited, not cap-limited.", options: {} },
  ], { x: 0.7, y: 5.28, w: 11.9, h: 1.4, fontSize: 14, color: "333333", fontFace: "Calibri", lineSpacing: 20, margin: 0 });
  source(s, "recovery_ratio/24 × terms/cap, from both closure artifacts   ·   claim-ledger I-3");
  s.addNotes("This is the slide that stops the headline failure rate being misread as a loss rate.");
}

/* ───────────────── 10. Survivor statistics ───────────────── */
{
  const s = lightSlide();
  title(s, "What our own statistics leave out");
  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 1.8, w: 11.9, h: 1.35, rectRadius: 0.08,
    fill: { color: "F4F4F4" }, line: { color: RULE, width: 1 } });
  s.addText("Mean duration and mean effective APR are computed only over paths that reached the target. They estimate E[T | completion occurs by horizon H] — not E[T].",
    { x: 1.1, y: 2.0, w: 11.1, h: 0.95, fontSize: 15, color: INK, fontFace: "Calibri", lineSpacing: 21, valign: "middle", margin: 0 });
  s.addText("The reading rule this forces", { x: 0.7, y: 3.45, w: 11.9, h: 0.4, fontSize: 17, bold: true, color: INK, fontFace: "Cambria", margin: 0 });
  s.addText([
    { text: "A scenario with a short mean duration and a high incomplete-recovery rate is not a fast contract — it is one where the slow paths were dropped rather than counted.", options: { breakLine: true } },
  ], { x: 0.7, y: 3.95, w: 11.9, h: 0.8, fontSize: 15, color: "333333", fontFace: "Calibri", lineSpacing: 21, margin: 0 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 4.85, w: 11.9, h: 1.35, rectRadius: 0.08,
    fill: { color: "FDF3EF" }, line: { color: WARN, width: 1.5 } });
  s.addText("Closure at month 13, f = 1.20: mean duration 11.99 months — alongside 76.2% of paths never completing.",
    { x: 1.1, y: 5.05, w: 11.1, h: 0.95, fontSize: 15, bold: true, color: "6B2E12", fontFace: "Calibri", valign: "middle", margin: 0 });
  source(s, "baseline_closure_v1_canonical.json → /scenarios/closure_m13/RBF");
  s.addNotes("Reporting the 11.99 without the 76.2% would invert the finding. Survivor statistics describe the contracts that finished, not the portfolio.");
}

/* ───────────────── 11. What this does not claim ───────────────── */
{
  const s = lightSlide();
  title(s, "What this study does not claim");
  const items = [
    ["No predictive validity", "The demonstration risk score is trained on synthetic data whose label is a formula over the same features. Generating-function AUC 0.9098 vs reported ensemble 0.9182 — the figure measured the chosen noise variance, and is withdrawn."],
    ["No affordability claim", "Burden is measured against revenue, not against what the seller retains. Margins, costs, reserves and other obligations are outside the model."],
    ["No default claim, either way", "There is no default model here. The closure result disproves any guarantee of contractual completion — it does not show defaults or a default rate."],
    ["No causal or population claim", "Nothing here is evidence about Vietnamese sellers, or any seller. Vietnam is the motivating setting; no parameter was estimated from Vietnamese data."],
  ];
  let y = 1.75;
  items.forEach(([h, b]) => {
    s.addShape(pres.ShapeType.ellipse, { x: 0.75, y: y + 0.06, w: 0.34, h: 0.34, fill: { color: WARN } });
    s.addText(h, { x: 1.35, y: y - 0.03, w: 3.4, h: 0.42, fontSize: 15, bold: true, color: INK, fontFace: "Cambria", valign: "top", margin: 0 });
    s.addText(b, { x: 4.85, y: y - 0.03, w: 7.75, h: 1.05, fontSize: 12.5, color: "333333", fontFace: "Calibri", lineSpacing: 18, valign: "top", margin: 0 });
    y += 1.2;
  });
  s.addText("The fixed arm is modelled as paid in full and on time — an optimistic scheduled-recovery benchmark, which flatters the comparison against it.",
    { x: 0.7, y: 6.35, w: 11.9, h: 0.5, fontSize: 12, italic: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addNotes("Say this section out loud in any interview. The restraint is the credential.");
}

/* ───────────────── 12. Reproducibility ───────────────── */
{
  const s = lightSlide();
  title(s, "Every figure traces to a checksummed artifact");
  const stat = (x, big, lab) => {
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.8, w: 3.7, h: 1.75, rectRadius: 0.08,
      fill: { color: "FAFAFA" }, line: { color: RULE, width: 1 } });
    s.addText(big, { x: x + 0.32, y: 1.98, w: 3.06, h: 0.82, fontSize: 34, bold: true, color: RBF, fontFace: "Cambria", margin: 0 });
    s.addText(lab, { x: x + 0.32, y: 2.82, w: 3.06, h: 0.6, fontSize: 12, color: "444444", fontFace: "Calibri", lineSpacing: 16, valign: "top", margin: 0 });
  };
  stat(0.7,  "5",     "canonical artifacts, each with a\nregistered SHA-256");
  stat(4.80, "1,008", "tests passing — 379 backend,\n629 simulation");
  stat(8.90, "44",    "verified sources, with 6\nevidence gaps stated openly");
  s.addText("Reproducibility, stated at the strength the measurement supports", { x: 0.7, y: 3.85, w: 11.9, h: 0.4, fontSize: 16, bold: true, color: INK, fontFace: "Cambria", margin: 0 });
  s.addText([
    { text: "All five artifacts reproduce numerically at published precision on every platform tested.", options: { bullet: true, breakLine: true } },
    { text: "Byte equality holds within a fixed runtime, not across platforms — 3 of 5 byte-identical on macOS CPython 3.11.5, 5 of 5 on Linux 3.10.12.", options: { bullet: true, breakLine: true } },
    { text: "An earlier claim of unqualified byte-for-byte reproducibility rested on a step that re-hashed the committed file rather than regenerating it. Both the claim and the evidence were corrected.", options: { bullet: true } },
  ], { x: 0.7, y: 4.35, w: 11.9, h: 1.9, fontSize: 13, color: "333333", fontFace: "Calibri", paraSpaceAfter: 8, margin: 0 });
  s.addText("9 browser tests skip where no chromium build is available. They are reported as skips, never counted as passes.",
    { x: 0.7, y: 6.3, w: 11.9, h: 0.45, fontSize: 11, italic: true, color: MUTED, fontFace: "Calibri", margin: 0 });
  s.addNotes("The corrected reproducibility claim is a better credential than the overstated one would have been.");
}

/* ───────────────── 13. Close ───────────────── */
{
  const s = darkSlide();
  s.addText("What would change the conclusion", { x: 0.9, y: 1.6, w: 11.5, h: 0.75,
    fontSize: 32, bold: true, color: PAPER, fontFace: "Cambria", margin: 0 });
  s.addShape(pres.ShapeType.rect, { x: 0.9, y: 2.55, w: 1.6, h: 0.045, fill: { color: RBF } });
  s.addText([
    { text: "Observed seller revenue paired with adjudicated repayment outcomes would let us calibrate the revenue process and check whether the simulated magnitudes resemble anything real.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "It would not, on its own, deliver this comparison. Observational data cannot show both contracts on the same seller under the same realised path, because each seller takes at most one. That would still need randomisation, a credible quasi-experimental design, or a structural counterfactual.", options: {} },
  ], { x: 0.9, y: 3.0, w: 11.5, h: 2.4, fontSize: 16, color: "D8D8D8", fontFace: "Calibri", lineSpacing: 24, margin: 0 });
  s.addText("Calibration and causal identification are different problems. Observed data solves only the first.",
    { x: 0.9, y: 5.65, w: 11.5, h: 0.6, fontSize: 17, bold: true, color: PAPER, fontFace: "Calibri", margin: 0 });
  s.addNotes("Close on the limitation, not on the result. It is the most defensible note to end on.");
}

pres.writeFile({ fileName: "RBF_DECK.pptx" }).then(() => console.log("wrote RBF_DECK.pptx"));
