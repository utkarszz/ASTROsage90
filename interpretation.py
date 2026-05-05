"""
interpretation.py — Rule-based astrological interpretation engine.

Loads interpretations from data/interpretations.json and maps planetary
positions to human-readable personality insights.
"""

import json
import os
from typing import Dict, List, Optional

from config import INTERPRETATIONS_FILE, PLANETS
from kundli import BirthChart


def _load_interpretations() -> dict:
    """Load the interpretations JSON file. Returns empty dict on failure."""
    if not os.path.exists(INTERPRETATIONS_FILE):
        return {}
    try:
        with open(INTERPRETATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


# Cache at module level so we only load once
_INTERPRETATIONS: dict = _load_interpretations()


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def get_sun_sign_interpretation(sign: str) -> Optional[dict]:
    """
    Return the full sun-sign interpretation dict for *sign*.

    Keys: traits, strengths, weaknesses, element, ruling_planet.
    Returns None if the sign is not found.
    """
    return _INTERPRETATIONS.get("sun_signs", {}).get(sign)


def get_moon_sign_interpretation(sign: str) -> Optional[str]:
    """Return the moon-sign interpretation paragraph for *sign*."""
    return _INTERPRETATIONS.get("moon_signs", {}).get(sign)


def get_ascendant_interpretation(sign: str) -> Optional[str]:
    """Return the ascendant interpretation paragraph for *sign*."""
    return _INTERPRETATIONS.get("ascendant_signs", {}).get(sign)


def get_planet_interpretation(planet: str, sign: str) -> Optional[str]:
    """Return the interpretation for *planet* in *sign*."""
    planets_data = _INTERPRETATIONS.get("planets_in_signs", {})
    return planets_data.get(planet, {}).get(sign)


def generate_full_interpretation(chart: BirthChart) -> dict:
    """
    Generate a complete interpretation report from a BirthChart.

    Returns
    -------
    dict with keys:
        sun  : dict  — full sun-sign info
        moon : str   — moon-sign paragraph
        ascendant : str — ascendant paragraph
        planets : dict  — {planet_name: interpretation_str}
        summary : str   — combined narrative
    """
    result: Dict[str, object] = {}

    # ── Sun sign ──
    sun_info = get_sun_sign_interpretation(chart.sun_sign)
    result["sun"] = sun_info or {"traits": f"Sun in {chart.sun_sign}."}

    # ── Moon sign ──
    moon_text = get_moon_sign_interpretation(chart.moon_sign)
    result["moon"] = moon_text or f"Moon in {chart.moon_sign}."

    # ── Ascendant ──
    asc_sign = chart.ascendant.get("sign", "Unknown")
    asc_text = get_ascendant_interpretation(asc_sign)
    result["ascendant"] = asc_text or f"Ascendant in {asc_sign}."

    # ── Other planets ──
    planet_readings: Dict[str, str] = {}
    for planet in PLANETS:
        if planet in ("Sun", "Moon"):
            continue  # Already covered above
        sign = chart.get_planet_sign(planet)
        reading = get_planet_interpretation(planet, sign)
        planet_readings[planet] = reading or f"{planet} in {sign}."
    result["planets"] = planet_readings

    # ── Combined narrative summary ──
    summary_parts: List[str] = []

    if sun_info:
        summary_parts.append(f"☀  Sun in {chart.sun_sign}: {sun_info.get('traits', '')}")
    if moon_text:
        summary_parts.append(f"🌙 Moon in {chart.moon_sign}: {moon_text}")
    if asc_text:
        summary_parts.append(f"⬆  Ascendant in {asc_sign}: {asc_text}")

    for planet, reading in planet_readings.items():
        sign = chart.get_planet_sign(planet)
        summary_parts.append(f"🪐 {planet} in {sign}: {reading}")

    result["summary"] = "\n\n".join(summary_parts)

    return result
