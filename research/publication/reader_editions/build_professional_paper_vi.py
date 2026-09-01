#!/usr/bin/env python3
"""Build the Vietnamese reader-facing RBF paper without modifying the audited repository."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "rbf-paper-mpl"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent


def find_repo_root() -> Path:
    """Locate the checkout containing research/results, or use RBF_REPO_ROOT."""
    configured = os.environ.get("RBF_REPO_ROOT")
    candidates = [Path(configured).expanduser()] if configured else [HERE, *HERE.parents]
    for candidate in candidates:
        candidate = candidate.resolve()
        if (candidate / "research" / "results").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate research/results. Place this directory inside the SellerFlow "
        "checkout or set RBF_REPO_ROOT to the checkout root."
    )


REPO_ROOT = find_repo_root()
WORK = Path(os.environ.get("RBF_PAPER_WORK_DIR", HERE / "build")).expanduser().resolve()
CHARTS = WORK / "charts"
OUTPUT_DIR = Path(os.environ.get("RBF_PAPER_OUTPUT_DIR", HERE)).expanduser().resolve()
OUT = OUTPUT_DIR / "Tai_Tro_Hoan_Tra_Theo_Doanh_Thu_Bai_Nghien_Cuu.pdf"
RESULTS = Path(os.environ.get("RBF_RESULTS_DIR", REPO_ROOT / "research" / "results")).expanduser().resolve()

ILLUSTRATIVE = RESULTS / "baseline_v3_canonical.json"
EQUAL_COST = RESULTS / "baseline_equalcost_v2_canonical.json"
CLOSURE = RESULTS / "baseline_closure_v2_canonical.json"
CLOSURE_EQUAL = RESULTS / "baseline_closure_equalcost_v2_canonical.json"

EXPECTED_INPUT_SHA256 = {
    "baseline_v3_canonical.json": "363729016298b3d7307ec066c8df37c60e1c9aa2582db2c058c5cc74df894d55",
    "baseline_equalcost_v2_canonical.json": "b3ebfe6a5a7e7f48726d7e501295b02f84258a3fe9ee4e048875125b1270e0ee",
    "baseline_closure_v2_canonical.json": "21b8e207ff2db9ac866b8cb2bab47c8c2e434d2bff03d802eb6f53a66fdcea4b",
    "baseline_closure_equalcost_v2_canonical.json": "e1e6d81bbeeb60f0e923c27a8df44d26674f4b8ad788c6c9796c17ef40622665",
}

DARK = "#222222"
MID = "#777777"
PALE = "#B7B7B7"
LIGHT = "#E7E7E7"
INK = "#111111"

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "axes.titleweight": "normal",
    "axes.labelcolor": INK,
    "text.color": INK,
})


def load(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Required result artifact is missing: {path}")
    payload = path.read_bytes()
    expected = EXPECTED_INPUT_SHA256[path.name]
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        raise ValueError(
            f"Result artifact checksum mismatch for {path.name}: "
            f"expected {expected}, found {actual}"
        )
    return json.loads(payload)


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color("#777777")
    ax.spines["bottom"].set_color("#777777")
    ax.tick_params(colors="#333333", labelsize=8)
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)


def save(fig, name: str) -> Path:
    path = CHARTS / name
    fig.savefig(path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_mechanics() -> Path:
    months = np.arange(1, 14)
    revenue = np.array([185, 180, 170, 145, 105, 80, 72, 92, 112, 132, 150, 168, 182], dtype=float)
    fixed = np.repeat(17.076923, len(months))
    rbf = revenue * 0.097  # 10% of net sales with a 3% return deduction.

    fig, axes = plt.subplots(2, 1, figsize=(7.15, 4.3), sharex=True, gridspec_kw={"hspace": 0.20})
    ax = axes[0]
    ax.plot(months, revenue, color=MID, linewidth=1.8, marker="o", markersize=3.2)
    ax.fill_between(months, revenue, color=LIGHT, alpha=0.65)
    ax.set_ylabel("Doanh số tháng\n(triệu đồng)", fontsize=8.5)
    ax.set_ylim(0, 205)
    style_axes(ax)

    ax = axes[1]
    ax.plot(months, fixed, color=DARK, linewidth=2.0, linestyle="--", label="Khoản trả cố định")
    ax.plot(months, rbf, color=MID, linewidth=2.0, marker="o", markersize=3.0, label="Hoàn trả theo doanh thu")
    ax.set_ylabel("Khoản trả hàng tháng\n(triệu đồng)", fontsize=8.5)
    ax.set_xlabel("Tháng", fontsize=8.5)
    ax.set_xticks(months)
    ax.set_ylim(0, 22)
    style_axes(ax)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
    return save(fig, "figure_1_mechanics_vi.svg")


def make_severe(data: dict) -> Path:
    s = data["scenarios"]["severe_downturn"]
    colors = [MID, DARK]
    burden = [100 * s["RBF"]["burden_mean"], 100 * s["FIX-A"]["burden_mean"]]
    recovery = [100 * s["RBF"]["recovery_ratio"]["12"], 100 * s["FIX-A"]["recovery_ratio"]["12"]]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.75), gridspec_kw={"wspace": 0.28})
    for ax, vals, title, xmax, suffix in [
        (axes[0], burden, "Gánh nặng thanh toán bình quân", 20, "% doanh số tháng"),
        (axes[1], recovery, "Mức thu hồi đến tháng 12", 100, "% mục tiêu hoàn trả"),
    ]:
        x = np.arange(2)
        bars = ax.bar(x, vals, color=colors, width=0.54, zorder=2)
        ax.set_xticks(x, ["Theo\ndoanh thu", "Cố định,\ncùng chi phí"])
        ax.set_ylim(0, xmax)
        ax.set_title(title, loc="left", fontsize=10, fontweight="bold", color=INK)
        ax.set_ylabel(suffix, fontsize=8)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, v + xmax * 0.025, f"{v:.1f}%",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        style_axes(ax)
    return save(fig, "figure_2_severe_vi.svg")


def make_tradeoff(data: dict) -> Path:
    names = list(data["scenarios"].keys())
    label_map = {
        "disruption_1m": "Gián đoạn 1 tháng",
        "gradual_decline": "Suy giảm dần",
        "growth": "Tăng trưởng",
        "platform_outage": "Gián đoạn nền tảng",
        "returns_spike": "Tỷ lệ hoàn hàng tăng",
        "seasonal": "Mùa vụ",
        "seasonal_strong": "Mùa vụ mạnh",
        "severe_downturn": "Suy giảm nghiêm trọng",
        "stable": "Ổn định",
        "sustained_decline": "Suy giảm kéo dài",
    }
    xs, ys = [], []
    for name in names:
        row = data["scenarios"][name]
        xs.append(row["FIX-A"]["n_high_burden"]["0.15"] - row["RBF"]["n_high_burden"]["0.15"])
        ys.append(100 * (row["RBF"]["recovery_ratio"]["12"] - row["FIX-A"]["recovery_ratio"]["12"]))

    fig, ax = plt.subplots(figsize=(7.15, 4.0))
    ax.axhline(0, color="#999999", linewidth=1)
    ax.axvline(0, color="#999999", linewidth=1)
    markers = ["D" if n == "severe_downturn" else "o" for n in names]
    for n, x, y, marker in zip(names, xs, ys, markers):
        ax.scatter([x], [y], s=52 if n == "severe_downturn" else 42,
                   c=DARK if n == "severe_downturn" else MID, marker=marker,
                   edgecolor="white", linewidth=0.6, zorder=3)
    offsets = {
        "stable": (22, -11), "seasonal": (22, 10), "returns_spike": (22, -28),
        "growth": (8, 9), "disruption_1m": (18, 10), "platform_outage": (18, -18),
        "gradual_decline": (8, 8), "seasonal_strong": (20, 18),
        "sustained_decline": (8, 8), "severe_downturn": (-98, 5),
    }
    for n, x, y in zip(names, xs, ys):
        ox, oy = offsets.get(n, (5, 5))
        ax.annotate(
            label_map[n], (x, y), xytext=(ox, oy), textcoords="offset points",
            fontsize=6.9, color=INK,
            arrowprops={"arrowstyle": "-", "color": "#888888", "lw": 0.45},
        )
    ax.set_xlabel("Số tháng gánh nặng cao được tránh nhờ hoàn trả theo doanh thu\n(ngưỡng báo cáo 15%)", fontsize=9)
    ax.set_ylabel("Chênh lệch mức thu hồi đến tháng 12\n(theo doanh thu trừ cố định, điểm phần trăm)", fontsize=9)
    ax.set_xlim(-0.3, 7.4)
    ax.set_ylim(-31, 10)
    style_axes(ax)
    ax.text(7.25, 8.2, "giảm áp lực / thu hồi nhanh hơn", ha="right", va="top", fontsize=7.2, color="#555555", style="italic")
    ax.text(7.25, -20.8, "giảm áp lực / thu hồi chậm hơn", ha="right", va="bottom", fontsize=7.2, color="#555555", style="italic")
    return save(fig, "figure_3_tradeoff_vi.svg")


def make_pricing(illustrative: dict, equal: dict) -> Path:
    s1 = illustrative["scenarios"]["severe_downturn"]["RBF"]
    s2 = equal["scenarios"]["severe_downturn"]["RBF"]
    groups = [
        ("Mục tiêu hoàn trả\n(triệu đồng)", [illustrative["terms"]["cap"] / 1e6, equal["terms"]["cap"] / 1e6], 240, "{:.1f}"),
        ("Thu hồi đến tháng 12\n(% mục tiêu)", [100*s1["recovery_ratio"]["12"], 100*s2["recovery_ratio"]["12"]], 100, "{:.1f}%"),
        ("Thời gian hoàn tất bình quân\n(tháng)", [s1["duration_mean"], s2["duration_mean"]], 24, "{:.1f}"),
        ("APR hiệu dụng bình quân\n(các quỹ đạo xác định được lãi suất)", [100*s1["apr_mean"], 100*s2["apr_mean"]], 35, "{:.1f}%"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 3.2), gridspec_kw={"hspace": 0.78, "wspace": 0.45})
    for ax, (title, vals, xmax, fmt) in zip(axes.flat, groups):
        bars = ax.barh([0, 1], vals, color=[DARK, PALE], edgecolor=DARK, linewidth=0.6, height=0.48)
        bars[1].set_hatch("///")
        ax.set_yticks([0, 1], ["f = 1.20", "f* = 1.0945"])
        ax.invert_yaxis()
        ax.set_xlim(0, xmax)
        ax.set_title(title, fontsize=8.7, fontweight="bold", loc="left")
        for i, v in enumerate(vals):
            ax.text(v + xmax*0.025, i, fmt.format(v), va="center", fontsize=7.7, fontweight="bold")
        style_axes(ax)
        ax.tick_params(axis="x", labelsize=7)
    return save(fig, "figure_4_pricing_vi.svg")


def make_closure(closure: dict, equal: dict) -> Path:
    names = ["closure_m7", "closure_m13", "temp_closure"]
    labels = ["Ngừng hoạt động vĩnh viễn\ntừ tháng 7", "Ngừng hoạt động vĩnh viễn\ntừ tháng 13", "Tạm ngừng\n3 tháng"]
    v1 = [100 * closure["scenarios"][n]["RBF"]["completed_rate"] for n in names]
    v2 = [100 * equal["scenarios"][n]["RBF"]["completed_rate"] for n in names]
    x = np.arange(len(names))
    w = 0.34
    fig, ax = plt.subplots(figsize=(7.15, 3.25))
    b1 = ax.bar(x-w/2, v1, w, color=DARK, label="f = 1.20")
    b2 = ax.bar(x+w/2, v2, w, color=PALE, edgecolor=DARK, hatch="///", linewidth=0.6, label="f* = 1.0945")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 108)
    ax.set_ylabel("Quỹ đạo đạt mục tiêu hoàn trả trong 24 tháng (%)", fontsize=8.7)
    ax.legend(frameon=False, ncol=2, fontsize=8.5, loc="upper left")
    for bars in (b1, b2):
        for bar in bars:
            v = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, max(v+2, 2.5), f"{v:.1f}%", ha="center", va="bottom", fontsize=8.2, fontweight="bold")
    style_axes(ax)
    return save(fig, "figure_5_closure_vi.svg")


def data_uri(path: Path) -> str:
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    illustrative = load(ILLUSTRATIVE)
    equal = load(EQUAL_COST)
    closure = load(CLOSURE)
    closure_equal = load(CLOSURE_EQUAL)

    figures = {
        "{{FIGURE_1}}": make_mechanics(),
        "{{FIGURE_2}}": make_severe(illustrative),
        "{{FIGURE_3}}": make_tradeoff(illustrative),
        "{{FIGURE_4}}": make_pricing(illustrative, equal),
        "{{FIGURE_5}}": make_closure(closure, closure_equal),
    }
    template = (HERE / "academic_paper_vi_template.html").read_text(encoding="utf-8")
    for token in figures:
        count = template.count(token)
        if count != 1:
            raise ValueError(f"Expected exactly one {token} placeholder; found {count}")
    for token, path in figures.items():
        template = template.replace(token, data_uri(path))
    if "{{FIGURE_" in template:
        raise ValueError("An unresolved figure placeholder remains in the rendered HTML")
    html_path = WORK / "professional_paper_vi.html"
    html_path.write_text(template, encoding="utf-8")

    if os.environ.get("RBF_HTML_ONLY") == "1":
        print(html_path)
        return

    configured_chrome = os.environ.get("CHROME_BIN")
    chrome_candidates = [
        Path(configured_chrome).expanduser() if configured_chrome else None,
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path(shutil.which("google-chrome-stable") or ""),
        Path(shutil.which("google-chrome") or ""),
        Path(shutil.which("chromium") or ""),
        Path(shutil.which("chromium-browser") or ""),
    ]
    chrome = next((path for path in chrome_candidates if path and path.is_file()), None)
    if chrome is None:
        raise FileNotFoundError("Chrome/Chromium not found. Set CHROME_BIN to its executable path.")
    with tempfile.TemporaryDirectory(prefix="chrome-profile-", dir=str(WORK)) as profile:
        cmd = [
            str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--allow-file-access-from-files", "--no-pdf-header-footer",
            f"--user-data-dir={profile}", f"--print-to-pdf={OUT}",
            html_path.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=True)
    print(OUT)


if __name__ == "__main__":
    main()
