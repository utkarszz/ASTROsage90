"""
main.py — CLI entry point for the Astrology Predictor.

Provides an interactive menu to generate birth charts, view planetary
positions, and save reports. Uses the 'rich' library for colourful output
when available, otherwise falls back to plain text.
"""

import sys
import os
from datetime import datetime

# Ensure the project root is on sys.path so sibling modules import cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, SEPARATOR, SEPARATOR_THIN, PLANETS
from input_handler import collect_birth_details
from kundli import generate_birth_chart, BirthChart
from interpretation import generate_full_interpretation
from zodiac import get_zodiac_sign, get_sign_element, get_sign_quality, get_sign_ruler
from utils import (
    print_header,
    print_subheader,
    print_key_value,
    print_error,
    print_success,
    print_info,
    save_report,
)

# ──────────────────────────────────────────────
# Try importing 'rich' for colourful output
# ──────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None  # type: ignore


# ══════════════════════════════════════════════
#  Display helpers (rich vs plain)
# ══════════════════════════════════════════════

def show_banner() -> None:
    """Display the application banner."""
    if RICH_AVAILABLE:
        banner_text = Text()
        banner_text.append("✦ ", style="bright_yellow")
        banner_text.append(APP_NAME, style="bold bright_cyan")
        banner_text.append(f"  v{APP_VERSION}", style="dim")
        console.print(Panel(banner_text, border_style="bright_blue", padding=(1, 4)))
    else:
        print(f"\n{SEPARATOR}")
        print(f"  ✦  {APP_NAME}  v{APP_VERSION}")
        print(SEPARATOR)


def show_menu() -> None:
    """Display the main menu options."""
    if RICH_AVAILABLE:
        menu = Table(show_header=False, box=None, padding=(0, 2))
        menu.add_row("[bright_yellow]1.[/]", "[white]Generate Birth Chart[/]")
        menu.add_row("[bright_yellow]2.[/]", "[white]View Planetary Positions[/]")
        menu.add_row("[bright_yellow]3.[/]", "[white]Save Report to File[/]")
        menu.add_row("[bright_yellow]4.[/]", "[red]Exit[/]")
        console.print("\n")
        console.print(menu)
        console.print()
    else:
        print(f"\n  1. Generate Birth Chart")
        print(f"  2. View Planetary Positions")
        print(f"  3. Save Report to File")
        print(f"  4. Exit\n")


def display_birth_chart(chart: BirthChart, interpretation: dict) -> None:
    """Render the full birth chart report."""
    if RICH_AVAILABLE:
        _display_chart_rich(chart, interpretation)
    else:
        _display_chart_plain(chart, interpretation)


def display_planetary_positions(chart: BirthChart) -> None:
    """Render planetary positions in a table."""
    if RICH_AVAILABLE:
        _display_planets_rich(chart)
    else:
        _display_planets_plain(chart)


# ──────────────────────────────────────────────
# Rich (colourful) renderers
# ──────────────────────────────────────────────

def _display_chart_rich(chart: BirthChart, interp: dict) -> None:
    """Render birth chart using Rich library."""
    # Header
    console.print()
    console.print(Panel(
        f"[bold bright_cyan]Birth Chart Summary[/bold bright_cyan]\n"
        f"[dim]{chart.city} • {chart.birth_dt.strftime('%d %B %Y, %H:%M')}[/dim]",
        border_style="bright_blue",
        padding=(1, 3),
    ))

    # Core signs table
    core = Table(title="Core Signs", box=box.ROUNDED, border_style="cyan", title_style="bold bright_yellow")
    core.add_column("Placement", style="bright_white", justify="right")
    core.add_column("Sign", style="bright_green")
    core.add_column("Element", style="bright_magenta")
    core.add_column("Quality", style="bright_cyan")

    for label, sign in [("☀  Sun", chart.sun_sign), ("🌙 Moon", chart.moon_sign),
                        ("⬆  Ascendant", chart.ascendant.get("sign", "Unknown"))]:
        core.add_row(label, sign, get_sign_element(sign), get_sign_quality(sign))
    console.print(core)

    # Planetary positions table
    planets_table = Table(title="Planetary Positions", box=box.ROUNDED, border_style="cyan", title_style="bold bright_yellow")
    planets_table.add_column("Planet", style="bright_white", justify="right")
    planets_table.add_column("Sign", style="bright_green")
    planets_table.add_column("Position", style="dim")

    for planet in PLANETS:
        data = chart.planet_positions.get(planet, {})
        planets_table.add_row(planet, data.get("sign", "—"), data.get("degree", "—"))
    console.print(planets_table)

    # Houses table
    if chart.houses:
        houses_table = Table(title="Houses", box=box.ROUNDED, border_style="cyan", title_style="bold bright_yellow")
        houses_table.add_column("House", style="bright_white", justify="center")
        houses_table.add_column("Sign", style="bright_green")
        houses_table.add_column("Cusp", style="dim")

        for h in chart.houses:
            houses_table.add_row(str(h["house"]), h["sign"], h["degree"])
        console.print(houses_table)

    # Interpretation
    console.print()
    console.print(Panel("[bold bright_yellow]Interpretation[/bold bright_yellow]", border_style="bright_blue"))

    sun_info = interp.get("sun", {})
    if isinstance(sun_info, dict):
        console.print(f"\n  [bright_yellow]☀  Sun in {chart.sun_sign}[/bright_yellow]")
        console.print(f"     {sun_info.get('traits', '')}")
        console.print(f"     [green]Strengths:[/green] {sun_info.get('strengths', '')}")
        console.print(f"     [red]Weaknesses:[/red] {sun_info.get('weaknesses', '')}")

    moon_text = interp.get("moon", "")
    if moon_text:
        console.print(f"\n  [bright_cyan]🌙 Moon in {chart.moon_sign}[/bright_cyan]")
        console.print(f"     {moon_text}")

    asc_text = interp.get("ascendant", "")
    if asc_text:
        asc_sign = chart.ascendant.get("sign", "Unknown")
        console.print(f"\n  [bright_magenta]⬆  Ascendant in {asc_sign}[/bright_magenta]")
        console.print(f"     {asc_text}")

    planet_readings = interp.get("planets", {})
    for planet, reading in planet_readings.items():
        sign = chart.get_planet_sign(planet)
        console.print(f"\n  [bright_white]🪐 {planet} in {sign}[/bright_white]")
        console.print(f"     {reading}")

    console.print()


def _display_planets_rich(chart: BirthChart) -> None:
    """Render only the planetary positions table using Rich."""
    console.print()
    console.print(Panel(
        f"[bold bright_cyan]Planetary Positions[/bold bright_cyan]\n"
        f"[dim]{chart.city} • {chart.birth_dt.strftime('%d %B %Y, %H:%M')}[/dim]",
        border_style="bright_blue",
        padding=(1, 3),
    ))

    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Planet", style="bright_white", justify="right")
    table.add_column("Sign", style="bright_green")
    table.add_column("Ecliptic Longitude", style="dim")
    table.add_column("Position", style="bright_yellow")

    for planet in PLANETS:
        data = chart.planet_positions.get(planet, {})
        table.add_row(
            planet,
            data.get("sign", "—"),
            f"{data.get('longitude', 0.0):.4f}°",
            data.get("degree", "—"),
        )
    console.print(table)

    # Ascendant
    asc = chart.ascendant
    console.print(f"\n  [bright_magenta]Ascendant:[/bright_magenta] {asc.get('sign', '—')}  ({asc.get('degree', '—')})")
    console.print()


# ──────────────────────────────────────────────
# Plain text renderers
# ──────────────────────────────────────────────

def _display_chart_plain(chart: BirthChart, interp: dict) -> None:
    """Render birth chart in plain text."""
    print_header("Birth Chart Summary")
    print(f"    Location: {chart.city}")
    print(f"    Date/Time: {chart.birth_dt.strftime('%d %B %Y, %H:%M')}")

    print_subheader("Core Signs")
    print_key_value("Sun Sign", chart.sun_sign)
    print_key_value("Moon Sign", chart.moon_sign)
    print_key_value("Ascendant", chart.ascendant.get("sign", "Unknown"))

    print_subheader("Planetary Positions")
    for planet in PLANETS:
        data = chart.planet_positions.get(planet, {})
        print_key_value(planet, f"{data.get('sign', '—')}  ({data.get('degree', '—')})")

    if chart.houses:
        print_subheader("Houses")
        for h in chart.houses:
            print_key_value(f"House {h['house']}", f"{h['sign']}  ({h['degree']})")

    print_subheader("Interpretation")

    sun_info = interp.get("sun", {})
    if isinstance(sun_info, dict):
        print(f"\n    ☀  Sun in {chart.sun_sign}")
        print(f"       {sun_info.get('traits', '')}")
        print(f"       Strengths: {sun_info.get('strengths', '')}")
        print(f"       Weaknesses: {sun_info.get('weaknesses', '')}")

    moon_text = interp.get("moon", "")
    if moon_text:
        print(f"\n    🌙 Moon in {chart.moon_sign}")
        print(f"       {moon_text}")

    asc_text = interp.get("ascendant", "")
    if asc_text:
        asc_sign = chart.ascendant.get("sign", "Unknown")
        print(f"\n    ⬆  Ascendant in {asc_sign}")
        print(f"       {asc_text}")

    planet_readings = interp.get("planets", {})
    for planet, reading in planet_readings.items():
        sign = chart.get_planet_sign(planet)
        print(f"\n    🪐 {planet} in {sign}")
        print(f"       {reading}")

    print()


def _display_planets_plain(chart: BirthChart) -> None:
    """Render only planetary positions in plain text."""
    print_header("Planetary Positions")
    print(f"    Location: {chart.city}")
    print(f"    Date/Time: {chart.birth_dt.strftime('%d %B %Y, %H:%M')}")
    print()

    for planet in PLANETS:
        data = chart.planet_positions.get(planet, {})
        print_key_value(planet, f"{data.get('sign', '—')}  ({data.get('degree', '—')})")

    asc = chart.ascendant
    print(f"\n    Ascendant: {asc.get('sign', '—')}  ({asc.get('degree', '—')})")
    print()


# ══════════════════════════════════════════════
#  Report generation (save to file)
# ══════════════════════════════════════════════

def build_report_text(chart: BirthChart, interp: dict) -> str:
    """Build a plain-text version of the full report for saving."""
    lines = []
    lines.append(SEPARATOR)
    lines.append(f"  {APP_NAME} — Birth Chart Report")
    lines.append(SEPARATOR)
    lines.append(f"  Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}")
    lines.append(f"  Location:  {chart.city}")
    lines.append(f"  Birth:     {chart.birth_dt.strftime('%d %B %Y, %H:%M')}")
    lines.append(f"  Lat/Lon:   {chart.latitude:.4f}, {chart.longitude:.4f}")
    lines.append("")
    lines.append(SEPARATOR_THIN)
    lines.append("  Core Signs")
    lines.append(SEPARATOR_THIN)
    lines.append(f"    Sun Sign:   {chart.sun_sign}")
    lines.append(f"    Moon Sign:  {chart.moon_sign}")
    lines.append(f"    Ascendant:  {chart.ascendant.get('sign', 'Unknown')}")
    lines.append("")
    lines.append(SEPARATOR_THIN)
    lines.append("  Planetary Positions")
    lines.append(SEPARATOR_THIN)
    for planet in PLANETS:
        data = chart.planet_positions.get(planet, {})
        lines.append(f"    {planet:<12} → {data.get('sign', '—'):<14} ({data.get('degree', '—')})")
    lines.append("")

    if chart.houses:
        lines.append(SEPARATOR_THIN)
        lines.append("  Houses")
        lines.append(SEPARATOR_THIN)
        for h in chart.houses:
            lines.append(f"    House {h['house']:<4} → {h['sign']:<14} ({h['degree']})")
        lines.append("")

    lines.append(SEPARATOR_THIN)
    lines.append("  Interpretation")
    lines.append(SEPARATOR_THIN)

    sun_info = interp.get("sun", {})
    if isinstance(sun_info, dict):
        lines.append(f"\n    Sun in {chart.sun_sign}")
        lines.append(f"    {sun_info.get('traits', '')}")
        lines.append(f"    Strengths: {sun_info.get('strengths', '')}")
        lines.append(f"    Weaknesses: {sun_info.get('weaknesses', '')}")

    moon_text = interp.get("moon", "")
    if moon_text:
        lines.append(f"\n    Moon in {chart.moon_sign}")
        lines.append(f"    {moon_text}")

    asc_text = interp.get("ascendant", "")
    if asc_text:
        lines.append(f"\n    Ascendant in {chart.ascendant.get('sign', 'Unknown')}")
        lines.append(f"    {asc_text}")

    planet_readings = interp.get("planets", {})
    for planet, reading in planet_readings.items():
        sign = chart.get_planet_sign(planet)
        lines.append(f"\n    {planet} in {sign}")
        lines.append(f"    {reading}")

    lines.append("")
    lines.append(SEPARATOR)
    lines.append(f"  End of Report — {APP_NAME}")
    lines.append(SEPARATOR)

    return "\n".join(lines)


# ══════════════════════════════════════════════
#  Main application loop
# ══════════════════════════════════════════════

def main() -> None:
    """Run the Astrology Predictor CLI application."""
    show_banner()

    # Persistent state across menu cycles
    last_chart: BirthChart = None  # type: ignore
    last_interp: dict = {}

    while True:
        show_menu()

        try:
            choice = input("  ▶ Select an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            print_info("Goodbye! May the stars guide you. ✦")
            break

        if choice == "1":
            # ── Generate Birth Chart ──
            try:
                details = collect_birth_details()
            except (KeyboardInterrupt, EOFError):
                print_info("Input cancelled.")
                continue

            print_info("Calculating planetary positions …")

            chart = generate_birth_chart(
                birth_dt=details["datetime"],
                latitude=details["latitude"],
                longitude=details["longitude"],
                city=details["city"],
            )
            interp = generate_full_interpretation(chart)

            # Cache for reuse
            last_chart = chart
            last_interp = interp

            display_birth_chart(chart, interp)

        elif choice == "2":
            # ── View Planetary Positions ──
            if last_chart is None:
                print_error("No chart generated yet. Please generate a birth chart first (option 1).")
                continue
            display_planetary_positions(last_chart)

        elif choice == "3":
            # ── Save Report ──
            if last_chart is None:
                print_error("No chart generated yet. Please generate a birth chart first (option 1).")
                continue

            report_text = build_report_text(last_chart, last_interp)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"astrology_report_{stamp}.txt"

            try:
                filepath = save_report(report_text, filename)
                print_success(f"Report saved to: {filepath}")
            except Exception as e:
                print_error(f"Failed to save report: {e}")

        elif choice == "4":
            # ── Exit ──
            print_info("Goodbye! May the stars guide you. ✦")
            break

        else:
            print_error("Invalid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
