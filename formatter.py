"""Markdown briefing formatter using Jinja2 templates."""

from pathlib import Path
from typing import Optional, Union

import jinja2


def _emoji(value: Optional[float]) -> str:
    """Return up/down emoji based on value sign."""
    if value is None:
        return ""
    return "🔴" if value >= 0 else "🔵"


def _format_number(value: Optional[float], decimals: int = 2) -> str:
    """Format number with commas and sign."""
    if value is None:
        return "N/A"
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def _format_pct(value: Optional[float]) -> str:
    """Format percentage with sign and emoji."""
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{_emoji(value)} {sign}{value:.2f}%"


def _format_volume(value: Optional[int]) -> str:
    """Format large volume numbers in 억 units for Korean stocks."""
    if value is None:
        return "N/A"
    if value >= 100_000_000:
        return f"{value / 100_000_000:.1f}억"
    if value >= 10_000:
        return f"{value / 10_000:.0f}만"
    return f"{value:,}"


def _format_net_flow(value: Optional[int]) -> str:
    """Format investor net flow in 억원."""
    if value is None:
        return "N/A"
    billions = value / 100_000_000
    sign = "+" if billions >= 0 else ""
    emoji = _emoji(billions)
    return f"{emoji} {sign}{billions:,.0f}억원"


def render_briefing(data: dict, template_dir: Union[str, Path], date: str) -> str:
    """Render market data into markdown string using Jinja2 template."""
    template_dir = Path(template_dir)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        undefined=jinja2.Undefined,
        keep_trailing_newline=True,
    )

    # Register custom filters
    env.filters["emoji"] = _emoji
    env.filters["num"] = _format_number
    env.filters["pct"] = _format_pct
    env.filters["vol"] = _format_volume
    env.filters["flow"] = _format_net_flow

    template = env.get_template("briefing_template.md")
    return template.render(data=data, date=date)


def write_briefing(content: str, output_dir: Union[str, Path], date: str) -> Path:
    """Write briefing content to a markdown file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Single .md extension (fixes .md.md bug)
    filename = f"{date}_daily-briefing.md"
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path
