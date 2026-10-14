"""
report_dashboard.py  -  Multi-Row AI Agricultural Robot Farm Report (PNG)

Usage from the Webots controller:
    from report_dashboard import generate_dashboard
    generate_dashboard(results, DASHBOARD_PATH)

`results` is a list of dicts:
    {"plant": 1, "disease": "Healthy", "confidence": 98.2, "spray": "NO",
     "row": 1, "x": -1.60, "y": -0.50,
     "probs": {"Healthy": 98.2, "Early Blight": 1.1, "Late Blight": 0.7}}
"""
import matplotlib
matplotlib.use("Agg")  # headless: safe inside Webots
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Wedge, Circle, Patch

GREEN, ORANGE, RED = "#2e9e4f", "#f0a030", "#d64545"
BG, CARD, INK, MUTED = "#f3f6f4", "#ffffff", "#1f2d27", "#6b7a72"
CLASSES = ["Healthy", "Early Blight", "Late Blight"]
CLASS_COLOR = {"Healthy": GREEN, "Early Blight": ORANGE, "Late Blight": RED}


def _norm(label):
    k = str(label).replace("_", " ").strip().lower()
    if "healthy" in k:
        return "Healthy"
    if "early" in k:
        return "Early Blight"
    if "late" in k:
        return "Late Blight"
    return label


def _color(label):
    return CLASS_COLOR.get(_norm(label), RED)


def _card(ax, title):
    ax.set_facecolor(CARD)
    for s in ax.spines.values():
        s.set_color("#d9e0dc")
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold",
                 color=INK, pad=10)
    ax.tick_params(colors=MUTED, labelsize=9)


def health_score(results):
    """100 = all healthy. Early blight counts half, late blight zero."""
    if not results:
        return 0.0
    w = {"Healthy": 1.0, "Early Blight": 0.5, "Late Blight": 0.0}
    return 100.0 * sum(w.get(_norm(r["disease"]), 0.0) for r in results) / len(results)


def generate_dashboard(results, path):
    results = sorted(results, key=lambda r: r.get("plant", 0))
    n = len(results)
    if n == 0:
        return path

    plants = [r.get("plant", i + 1) for i, r in enumerate(results)]
    conf = [r.get("confidence", 0.0) for r in results]
    labels = [_norm(r.get("disease", "Healthy")) for r in results]
    cols = [_color(l) for l in labels]
    counts = {c: labels.count(c) for c in CLASSES}
    score = health_score(results)
    sprayed = sum(1 for r in results if r.get("spray") == "YES")

    fig = plt.figure(figsize=(15, 24), facecolor=BG)
    gs = GridSpec(7, 2, figure=fig, height_ratios=[0.9, 3, 2.8, 2.6, 2.6, 2.8, 3.8],
                  hspace=0.55, wspace=0.18, left=0.06, right=0.96, top=0.97, bottom=0.03)

    # ---------- Title banner ----------
    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#17382b"))
    ax.text(0.5, 0.62, "AI AGRICULTURAL ROBOT TESTING FIELD REPORT", ha="center", va="center",
            color="white", fontsize=22, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.22, f"Total {n} leaves inspected across 7 crop rows  |  {sprayed} require precision spray  |  "
            f"Average confidence {sum(conf)/n:.1f}%", ha="center", va="center",
            color="#b9d8c6", fontsize=11, transform=ax.transAxes)

    # ---------- Disease distribution (pie) ----------
    ax = fig.add_subplot(gs[1, 0])
    _card(ax, "Disease Distribution")
    ax.set_xticks([]); ax.set_yticks([])
    pie_ax = ax.inset_axes([0.05, 0.05, 0.9, 0.85])
    present = [c for c in CLASSES if counts[c] > 0]
    if present:
        pie_ax.pie([counts[c] for c in present], colors=[CLASS_COLOR[c] for c in present],
                   autopct=lambda p: f"{p:.0f}%", startangle=90, pctdistance=0.78,
                   wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
                   textprops=dict(color="white", fontweight="bold", fontsize=11))
        pie_ax.legend([f"{c} ({counts[c]})" for c in present], loc="lower center",
                      bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)

    # ---------- Farm health gauge ----------
    ax = fig.add_subplot(gs[1, 1])
    _card(ax, "Field Health Index")
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.4, 1.3); ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])
    gcol = GREEN if score >= 70 else ORANGE if score >= 40 else RED
    ax.add_patch(Wedge((0, 0), 1.0, 0, 180, width=0.3, color="#e4e9e6"))
    ax.add_patch(Wedge((0, 0), 1.0, 180 - 180 * score / 100, 180, width=0.3, color=gcol))
    ax.text(0, 0.18, f"{score:.0f}/100", ha="center", fontsize=30,
            fontweight="bold", color=INK)
    status = "Healthy Crop Field" if score >= 70 else "Moderate Infection Risk" if score >= 40 else "Severe Disease Outbreak"
    ax.text(0, -0.2, status, ha="center", fontsize=13, color=gcol, fontweight="bold")

    # ---------- Confidence per plant ----------
    ax = fig.add_subplot(gs[2, :])
    _card(ax, f"AI Inspection Confidence per Leaf (1 to {n})")
    ax.bar(plants, conf, color=cols, width=0.7)
    # Add labels on subset if n is large
    step = 1 if n <= 24 else (2 if n <= 40 else 3)
    for i, (p, c) in enumerate(zip(plants, conf)):
        if i % step == 0:
            ax.text(p, c + 1.5, f"{c:.0f}%", ha="center", fontsize=7, color=INK)
    ax.set_ylim(0, 125)
    ax.set_xlim(0.5, n + 0.5)
    if n <= 30:
        ax.set_xticks(plants)
    else:
        ax.set_xticks(list(range(1, n + 1, 5)))
    ax.set_xlabel("Leaf Panel ID", color=MUTED); ax.set_ylabel("Confidence (%)", color=MUTED)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(handles=[Patch(color=CLASS_COLOR[c], label=c) for c in CLASSES],
              loc="upper right", frameon=False, ncol=3, fontsize=9)

    # ---------- Confidence trend ----------
    ax = fig.add_subplot(gs[3, :])
    _card(ax, "Inspection Sequence Confidence Trend")
    ax.plot(plants, conf, color="#2f6fb0", linewidth=1.8, zorder=2)
    ax.scatter(plants, conf, c=cols, s=40, zorder=3, edgecolor="white", linewidth=1.0)
    avg_c = sum(conf) / n
    ax.axhline(avg_c, color=MUTED, linestyle="--", linewidth=1)
    ax.text(plants[-1], avg_c + 1.5, f"Mean: {avg_c:.1f}%", ha="right", fontsize=9, color=MUTED)
    ax.set_ylim(max(0, min(conf) - 10), 105)
    ax.set_xlim(0.5, n + 0.5)
    if n <= 30:
        ax.set_xticks(plants)
    else:
        ax.set_xticks(list(range(1, n + 1, 5)))
    ax.set_xlabel("Inspection Sequence", color=MUTED); ax.set_ylabel("Confidence (%)", color=MUTED)
    ax.grid(alpha=0.25)

    # ---------- Disease confidence (avg probability per class) ----------
    ax = fig.add_subplot(gs[4, :])
    _card(ax, "Disease Confidence (average model probability per class)")
    if all("probs" in r and r["probs"] for r in results):
        avg = [sum(r["probs"].get(c, 0.0) for r in results) / n for c in CLASSES]
        note = "Mean probability across all inspected leaf panels"
    else:
        avg = [(sum(r["confidence"] for r, l in zip(results, labels) if l == c) / counts[c])
               if counts[c] else 0.0 for c in CLASSES]
        note = "Mean confidence of leaf panels predicted as this class"
    bars = ax.bar(CLASSES, avg, color=[CLASS_COLOR[c] for c in CLASSES], width=0.45)
    for b, v in zip(bars, avg):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.1f}%",
                ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.set_ylim(0, 115); ax.set_ylabel("%", color=MUTED)
    ax.set_xlabel(note, color=MUTED, fontsize=8)
    ax.grid(axis="y", alpha=0.25)

    # ---------- Spray analysis by row ----------
    ax = fig.add_subplot(gs[5, :])
    _card(ax, "Precision Spray Requirement Breakdown (by Crop Row)")
    
    # Group results by row
    row_groups = {}
    for r in results:
        rid = r.get("row", 1)
        key = f"Row {rid}"
        if key not in row_groups:
            row_groups[key] = []
        row_groups[key].append(r)
    
    if len(row_groups) > 1:
        row_groups["Total"] = results

    xs = range(len(row_groups))
    yes = [sum(1 for r in v if r.get("spray") == "YES") for v in row_groups.values()]
    no = [len(v) - y for v, y in zip(row_groups.values(), yes)]
    w = 0.35
    b1 = ax.bar([x - w / 2 for x in xs], yes, w, color=RED, label="Spray required (Disease)")
    b2 = ax.bar([x + w / 2 for x in xs], no, w, color=GREEN, label="No spray (Healthy)")
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.1,
                int(b.get_height()), ha="center", fontsize=9, color=INK)
    ax.set_xticks(list(xs)); ax.set_xticklabels(list(row_groups.keys()), fontsize=9)
    ax.set_ylabel("Leaves", color=MUTED); ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=9)

    # ---------- Farm disease map ----------
    ax = fig.add_subplot(gs[6, :])
    _card(ax, f"Full Field Disease Spatial Map ({n} Leaf Panels)")
    ax.set_facecolor("#8a6a4a")  # Rich Soil Ground Color
    
    for r in results:
        x = r.get("x")
        y = r.get("y")
        p = r.get("plant", 0)
        if x is not None and y is not None:
            ax.add_patch(Circle((x, y), 0.18, color=_color(r.get("disease", "Healthy")), ec="white", lw=1.5, zorder=3))
            ax.text(x, y, str(p), ha="center", va="center", color="white",
                    fontsize=8, fontweight="bold", zorder=4)

    # Draw row annotations
    row_labels = {
        -2.60: "Row 7 (South Buffer) →",
        -1.60: "← Row 6 (South Outer)",
        -0.50: "Row 1 (Active Bed 1) →",
         0.70: "← Row 2 (Active Bed 2)",
         1.90: "Row 3 (North Outer A) →",
         2.90: "← Row 4 (North Outer B)",
         3.90: "Row 5 (North Buffer) →",
    }
    for ry, txt in row_labels.items():
        ax.text(-2.5, ry, txt, color="#f8f4eb", va="center", ha="right", fontsize=8, fontweight="bold")

    ax.set_xlim(-4.2, 5.5); ax.set_ylim(-3.5, 4.8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])
    ax.legend(handles=[Patch(color=CLASS_COLOR[c], label=c) for c in CLASSES],
              loc="upper right", frameon=True, ncol=3, fontsize=9)

    fig.savefig(path, dpi=150, facecolor=BG)
    plt.close(fig)
    return path
