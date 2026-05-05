"""
input_handler.py — User input collection and validation.

Handles robust prompting with retry logic for date, time, and location.
"""

from datetime import datetime
from typing import Tuple

from utils import parse_date, parse_time, get_coordinates, print_error


def get_birth_date() -> datetime:
    """Prompt the user for a valid date of birth (DD-MM-YYYY) with retry."""
    while True:
        raw = input("  📅 Enter Date of Birth (DD-MM-YYYY): ").strip()
        if not raw:
            print_error("Date cannot be empty. Please try again.")
            continue

        dt = parse_date(raw)
        if dt is None:
            print_error("Invalid date format. Please use DD-MM-YYYY (e.g. 15-08-1995).")
            continue

        # Sanity check: date should not be in the future
        if dt > datetime.now():
            print_error("Date of birth cannot be in the future.")
            continue

        return dt


def get_birth_time() -> datetime:
    """Prompt the user for a valid birth time (HH:MM, 24-hour) with retry."""
    while True:
        raw = input("  🕐 Enter Time of Birth (HH:MM, 24h): ").strip()
        if not raw:
            print_error("Time cannot be empty. Please try again.")
            continue

        tm = parse_time(raw)
        if tm is None:
            print_error("Invalid time format. Please use HH:MM in 24-hour format (e.g. 14:30).")
            continue

        return tm


def get_location() -> Tuple[str, float, float]:
    """
    Prompt the user for a birth city and resolve coordinates.
    Returns (city_name, latitude, longitude).
    """
    while True:
        city = input("  📍 Enter Birth Location (City): ").strip()
        if not city:
            print_error("Location cannot be empty. Please enter a city name.")
            continue

        coords = get_coordinates(city)
        if coords is None:
            print_error(
                f"Could not find coordinates for '{city}'.\n"
                "       Please try a well-known city name (e.g. Mumbai, New York, London)."
            )
            continue

        lat, lon = coords
        return city.title(), lat, lon


def collect_birth_details() -> dict:
    """
    Orchestrate the full input flow.
    Returns a dict with keys: date, time, city, latitude, longitude, datetime.
    """
    print("\n  Please provide your birth details:\n")

    birth_date = get_birth_date()
    birth_time = get_birth_time()
    city, lat, lon = get_location()

    # Combine date + time into a single datetime
    combined_dt = datetime(
        year=birth_date.year,
        month=birth_date.month,
        day=birth_date.day,
        hour=birth_time.hour,
        minute=birth_time.minute,
    )

    return {
        "date": birth_date,
        "time": birth_time,
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "datetime": combined_dt,
    }
