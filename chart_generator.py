"""Chart generation module using matplotlib."""

import platform
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def _setup_style():
    """Configure matplotlib style for dark-themed Obsidian-friendly charts."""
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": "#1e1e2e",
        "axes.facecolor": "#1e1e2e",
        "axes.edgecolor": "#444466",
        "axes.grid": True,
        "grid.color": "#333355",
        "grid.alpha": 0.3,
        "text.color": "#cdd6f4",
        "xtick.color": "#a6adc8",
        "ytick.color": "#a6adc8",
        "figure.dpi": 150,
        "figure.figsize": (10, 5),
        "font.size": 10,
    })
    # Korean font setup
    system = platform.system()
    if system == "Darwin":
        plt.rcParams["font.family"] = "AppleGothic"
    elif system == "Linux":
        # GitHub Actions ubuntu - install fonts-nanum
        plt.rcParams["font.family"] = "NanumGothic"
    plt.rcParams["axes.unicode_minus"] = False


def generate_line_chart(
    series_dict: Dict[str, Dict],
    title: str,
    output_path: Path,
    ylabel: str = "",
    normalize: bool = False,
):
    """Generate a multi-line trend chart.

    Args:
        series_dict: {name: {"dates": [...], "values": [...]}}
        title: Chart title
        output_path: Where to save PNG
        ylabel: Y-axis label
        normalize: If True, normalize all series to 100 at start (for comparison)
    """
    _setup_style()
    fig, ax = plt.subplots()

    colors = ["#89b4fa", "#f38ba8", "#a6e3a1", "#fab387", "#cba6f7", "#f9e2af", "#94e2d5"]

    for i, (name, data) in enumerate(series_dict.items()):
        dates = data["dates"]
        values = data["values"]
        if normalize and len(values) > 0 and values[0] != 0:
            values = [v / values[0] * 100 for v in values]
        color = colors[i % len(colors)]
        ax.plot(dates, values, label=name, color=color, linewidth=2)

    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    if ylabel:
        ax.set_ylabel(ylabel)
    if normalize:
        ax.set_ylabel("기준 = 100")
        ax.axhline(y=100, color="#585b70", linestyle="--", alpha=0.5)

    ax.legend(loc="upper left", fontsize=9, framealpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), bbox_inches="tight")
    plt.close(fig)


def generate_bar_chart(
    names: List[str],
    values: List[float],
    title: str,
    output_path: Path,
    ylabel: str = "등락률 (%)",
):
    """Generate a horizontal bar chart for comparing changes.

    Args:
        names: Ticker/asset names
        values: Change percentages
        title: Chart title
        output_path: Where to save PNG
    """
    _setup_style()
    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.5 + 1)))

    colors = ["#a6e3a1" if v >= 0 else "#f38ba8" for v in values]
    y_pos = np.arange(len(names))

    bars = ax.barh(y_pos, values, color=colors, height=0.6, edgecolor="none")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlabel(ylabel)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.axvline(x=0, color="#585b70", linewidth=0.8)

    # Add value labels
    for bar, val in zip(bars, values):
        sign = "+" if val >= 0 else ""
        ax.text(
            bar.get_width() + (0.3 if val >= 0 else -0.3),
            bar.get_y() + bar.get_height() / 2,
            f"{sign}{val:.1f}%",
            va="center",
            ha="left" if val >= 0 else "right",
            fontsize=9,
            color="#cdd6f4",
        )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), bbox_inches="tight")
    plt.close(fig)
