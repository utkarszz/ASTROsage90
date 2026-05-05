"""
utils.py — Helper / utility functions for the Astrology Predictor.

Provides date conversion, formatting, geocoding, and CLI display helpers.
"""

import os
from datetime import datetime
from typing import Optional, Tuple

from config import (
    DATE_FORMAT,
    TIME_FORMAT,
    CITY_COORDINATES,
    SEPARATOR,
    SEPARATOR_THIN,
    SIGN_NAMES_BY_DEGREE,
    REPORTS_DIR,
)


# ──────────────────────────────────────────────
# Date / Time helpers
# ──────────────────────────────────────────────

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string in DD-MM-YYYY format. Returns None on failure."""
    try:
        return datetime.strptime(date_str.strip(), DATE_FORMAT)
    except ValueError:
        return None


def parse_time(time_str: str) -> Optional[datetime]:
    """Parse a time string in HH:MM format. Returns None on failure."""
    try:
        return datetime.strptime(time_str.strip(), TIME_FORMAT)
    except ValueError:
        return None


def to_julian_day(dt: datetime) -> float:
    """
    Convert a datetime to a Julian Day Number (approximate).
    Good enough for Swiss Ephemeris input.
    """
    year = dt.year
    month = dt.month
    day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0

    if month <= 2:
        year -= 1
        month += 12

    A = int(year / 100)
    B = 2 - A + int(A / 4)

    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    return jd


def longitude_to_sign(longitude: float) -> str:
    """Convert ecliptic longitude (0-360°) to zodiac sign name."""
    index = int(longitude / 30) % 12
    return SIGN_NAMES_BY_DEGREE[index]


def longitude_to_sign_degree(longitude: float) -> str:
    """Convert ecliptic longitude to 'DD° Sign' format."""
    sign = longitude_to_sign(longitude)
    degree = longitude % 30
    return f"{degree:05.2f}° {sign}"


# ──────────────────────────────────────────────
# Geocoding
# ──────────────────────────────────────────────

def get_coordinates(city: str) -> Optional[Tuple[float, float]]:
    """
    Look up (latitude, longitude) for a city name.
    Uses the built-in city dictionary; falls back to geopy if available.
    """
    key = city.strip().lower()

    # 1. Try built-in dictionary
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]

    # 2. Try geopy (optional dependency)
    try:
        from geopy.geocoders import Nominatim  # type: ignore
        geolocator = Nominatim(user_agent="astrology_predictor")
        location = geolocator.geocode(city, timeout=10)
        if location:
            return (location.latitude, location.longitude)
    except ImportError:
        pass
    except Exception:
        pass

    return None


# ──────────────────────────────────────────────
# Display / Formatting helpers
# ──────────────────────────────────────────────

def print_header(title: str) -> None:
    """Print a styled section header."""
    print(f"\n{SEPARATOR}")
    print(f"  ✦  {title}")
    print(SEPARATOR)


def print_subheader(title: str) -> None:
    """Print a styled sub-section header."""
    print(f"\n{SEPARATOR_THIN}")
    print(f"  ▸ {title}")
    print(SEPARATOR_THIN)


def print_key_value(key: str, value: str, indent: int = 4) -> None:
    """Print a key → value pair with consistent alignment."""
    pad = " " * indent
    print(f"{pad}{key:<18} → {value}")


def print_error(message: str) -> None:
    """Print a styled error message."""
    print(f"\n  ✖  Error: {message}\n")


def print_success(message: str) -> None:
    """Print a styled success message."""
    print(f"\n  ✔  {message}\n")


def print_info(message: str) -> None:
    """Print a styled informational message."""
    print(f"\n  ℹ  {message}\n")


# ──────────────────────────────────────────────
# Report saving
# ──────────────────────────────────────────────

def save_report(content: str, filename: str) -> str:
    """Save a text report to the reports/ directory. Returns the file path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
