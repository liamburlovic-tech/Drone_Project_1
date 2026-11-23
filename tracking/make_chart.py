"""Draw tracking/progress.png: cumulative spend and requirement completion over time.

Inputs (edit these, then rerun or push; the GitHub Action redraws the chart):
  tracking/spend.csv         one row per purchase (date, BOM id, item, amount)
  tracking/requirements.csv  one row per requirement; set status=verified + date_verified when done
  tracking/gates.csv         milestone due dates (blank = not scheduled yet)
"""
import csv
import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
BUDGET = 1000          # stated budget target (spec C-1)
EST_TOTAL = 1377       # BOM grand-total estimate (docs/Drone_BOM_v1.xlsx)
START = dt.date(2026, 11, 17)  # project kickoff (spec rev A)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # categorical slots 1 and 2


def read(name):
    with open(HERE / name, newline="") as f:
        return list(csv.DictReader(f))


def d(s):
    return dt.date.fromisoformat(s.strip())


spend = sorted(read("spend.csv"), key=lambda r: r["date"])
reqs = read("requirements.csv")
gates = read("gates.csv")
gate_due = {g["gate"]: d(g["due_date"]) for g in gates if g["due_date"].strip()}

today = dt.date.today()
end = max([today] + list(gate_due.values())) + dt.timedelta(days=7)

# Cumulative spend as a step series that runs to today
sx, sy, total = [START], [0.0], 0.0
for r in spend:
    total += float(r["amount_usd"])
    sx.append(d(r["date"]))
    sy.append(total)
sx.append(today)
sy.append(total)


def completion(phase):
    items = [r for r in reqs if r["phase"] == str(phase)]
    done = sorted(d(r["date_verified"]) for r in items
                  if r["status"].strip().lower() == "verified" and r["date_verified"].strip())
    xs, ys = [START], [0.0]
    for i, day in enumerate(done, 1):
        xs.append(day)
        ys.append(100 * i / len(items))
    xs.append(today)
    ys.append(ys[-1])
    return xs, ys, len(items), len(done)


def planned(phase):
    items = [r for r in reqs if r["phase"] == str(phase) and r["gate"] in gate_due]
    n_all = sum(1 for r in reqs if r["phase"] == str(phase))
    xs, ys, cum = [START], [0.0], 0
    for g, due in sorted(gate_due.items(), key=lambda kv: kv[1]):
        cum += sum(1 for r in items if r["gate"] == g)
        if any(r["gate"] == g for r in items):
            xs.append(due)
            ys.append(100 * cum / n_all)
    return xs, ys


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, facecolor=SURFACE,
                               gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.35})
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for g, due in gate_due.items():
        ax.axvline(due, color=GRID, linewidth=1, zorder=0)
    ax.axvline(today, color=MUTED, linewidth=1, linestyle=":", zorder=0)

# Panel 1: spend
ax1.step(sx, sy, where="post", color=BLUE, linewidth=2)
ax1.axhline(BUDGET, color=INK2, linewidth=1, linestyle="--")
ax1.axhline(EST_TOTAL, color=MUTED, linewidth=1, linestyle=(0, (1, 2)))
ax1.text(end, BUDGET, f" Budget ${BUDGET:,}", va="center", ha="left", color=INK2, fontsize=9)
ax1.text(end, EST_TOTAL, f" BOM estimate ${EST_TOTAL:,}", va="center", ha="left", color=MUTED, fontsize=9)
ax1.annotate(f"${total:,.0f} spent", (today, total), xytext=(6, 8), textcoords="offset points",
             color=INK, fontsize=10, fontweight="bold")
ax1.set_ylim(0, max(EST_TOTAL, total) * 1.12)
ax1.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("${x:,.0f}"))
ax1.set_title("Cumulative spend", loc="left", color=INK, fontsize=12, fontweight="bold", pad=22)
for g, due in gate_due.items():
    ax1.text(due, ax1.get_ylim()[1], g, ha="center", va="bottom", color=INK2, fontsize=9)

# Panel 2: requirement completion
for phase, color in ((1, BLUE), (2, ORANGE)):
    xs, ys, n, done = completion(phase)
    ax2.step(xs, ys, where="post", color=color, linewidth=2, label=f"Phase {phase} verified ({done}/{n})")
    ax2.annotate(f"Phase {phase}: {done}/{n}", (xs[-1], ys[-1]), xytext=(6, 6 if phase == 1 else 20),
                 textcoords="offset points", color=INK, fontsize=9)
px, py = planned(1)
ax2.step(px, py, where="post", color=BLUE, linewidth=1.2, linestyle="--", alpha=0.6, label="Phase 1 plan (gate due dates)")
ax2.set_ylim(0, 105)
ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())
ax2.set_title("Requirements verified", loc="left", color=INK, fontsize=12, fontweight="bold")
ax2.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK2)
ax2.set_xlim(START, end)
ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

fig.text(0.01, 0.005, f"Updated {today:%Y-%m-%d} · dotted line = today · gray verticals = gate due dates",
         color=MUTED, fontsize=8)
fig.savefig(HERE / "progress.png", dpi=150, bbox_inches="tight", facecolor=SURFACE)
print(f"spend ${total:,.0f}; wrote {HERE / 'progress.png'}")
