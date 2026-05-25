#!/usr/bin/env python3
"""Generate star history chart and save as PNG."""
import subprocess, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path

REPO = "irvinezhao/epic-booklet-downloader"
OUT = Path(__file__).resolve().parent.parent / "star_history.png"

def main():
    r = subprocess.run(
        ['gh', 'api', f'repos/{REPO}/stargazers',
         '-H', 'Accept: application/vnd.github.v3.star+json',
         '--paginate', '-q', '.[].starred_at'],
        capture_output=True, text=True
    )
    dates = [datetime.fromisoformat(d.strip().replace("Z", "+00:00"))
             for d in r.stdout.strip().split("\n") if d.strip()]
    if not dates:
        print("No stars"); sys.exit(1)

    counts = list(range(1, len(dates) + 1))
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fig.patch.set_facecolor('white'); ax.set_facecolor('white')
    ax.fill_between(dates, counts, alpha=0.12, color='#ff6b35')
    ax.plot(dates, counts, color='#ff6b35', linewidth=2.5, marker='o', markersize=6,
            markerfacecolor='white', markeredgecolor='#ff6b35', markeredgewidth=2, zorder=5)
    ax.set_ylabel('Stars', fontsize=11, fontweight='bold', color='#333')
    ax.set_title('Star History', fontsize=13, fontweight='bold', color='#333', pad=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(fontsize=9); plt.yticks(fontsize=9)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set_color('#ddd')
    ax.tick_params(colors='#666'); ax.grid(axis='y', alpha=0.25, linestyle='--')
    ax.annotate(f'{counts[-1]}', xy=(dates[-1], counts[-1]),
                xytext=(12,12), textcoords='offset points',
                fontsize=15, fontweight='bold', color='#ff6b35',
                arrowprops=dict(arrowstyle='->', color='#ff6b35', lw=1.5))
    plt.tight_layout()
    plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved {OUT} ({len(dates)} stars)")

if __name__ == "__main__":
    main()
