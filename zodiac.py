"""
zodiac.py — Zodiac sign determination from date of birth.

Provides the primary sun-sign lookup based on calendar date boundaries
and a helper to map ecliptic longitude to a zodiac sign.
"""

from datetime import datetime
from typing import Optional

from config import ZODIAC_SIGNS, SIGN_NAMES_BY_DEGREE


def get_zodiac_sign(dob: datetime) -> str:
    """
    Determine the Western zodiac (Sun) sign from a date of birth.

    Parameters
    ----------
    dob : datetime
        The date of birth.

    Returns
    -------
    str
        Zodiac sign name (e.g. "Aries", "Taurus").
    """
    day = dob.day
    month = dob.month

    for sign_name, start_day, start_month, end_day, end_month in ZODIAC_SIGNS:
        if start_month == end_month:
            if month == start_month and start_day <= day <= end_day:
                return sign_name
        else:
            # Handles the Capricorn wrap-around (Dec → Jan)
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day):
                return sign_name

    return "Unknown"


def get_sign_from_longitude(longitude: float) -> str:
    """
    Map an ecliptic longitude (0–360°) to its zodiac sign.

    Each sign spans 30°:
        0–30°  = Aries, 30–60° = Taurus, …, 330–360° = Pisces.
    """
    index = int(longitude / 30) % 12
    return SIGN_NAMES_BY_DEGREE[index]


def get_sign_element(sign: str) -> str:
    """Return the classical element (Fire, Earth, Air, Water) for a sign."""
    elements = {
        "Aries": "Fire",     "Leo": "Fire",        "Sagittarius": "Fire",
        "Taurus": "Earth",   "Virgo": "Earth",     "Capricorn": "Earth",
        "Gemini": "Air",     "Libra": "Air",       "Aquarius": "Air",
        "Cancer": "Water",   "Scorpio": "Water",   "Pisces": "Water",
    }
    return elements.get(sign, "Unknown")


def get_sign_quality(sign: str) -> str:
    """Return the quality / modality (Cardinal, Fixed, Mutable) for a sign."""
    qualities = {
        "Aries": "Cardinal",   "Cancer": "Cardinal",
        "Libra": "Cardinal",   "Capricorn": "Cardinal",
        "Taurus": "Fixed",     "Leo": "Fixed",
        "Scorpio": "Fixed",    "Aquarius": "Fixed",
        "Gemini": "Mutable",   "Virgo": "Mutable",
        "Sagittarius": "Mutable", "Pisces": "Mutable",
    }
    return qualities.get(sign, "Unknown")


def get_sign_ruler(sign: str) -> str:
    """Return the traditional ruling planet for a sign."""
    rulers = {
        "Aries": "Mars",       "Taurus": "Venus",
        "Gemini": "Mercury",   "Cancer": "Moon",
        "Leo": "Sun",          "Virgo": "Mercury",
        "Libra": "Venus",      "Scorpio": "Pluto",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn",
        "Aquarius": "Uranus",  "Pisces": "Neptune",
    }
    return rulers.get(sign, "Unknown")
