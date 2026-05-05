"""
config.py — Constants and configuration for the Astrology Predictor.
"""

import os

# ──────────────────────────────────────────────
# Application Metadata
# ──────────────────────────────────────────────
APP_NAME = "Astrology Predictor"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Astrology Project"

# ──────────────────────────────────────────────
# Date / Time Formats
# ──────────────────────────────────────────────
DATE_FORMAT = "%d-%m-%Y"          # DD-MM-YYYY
TIME_FORMAT = "%H:%M"             # HH:MM (24-hour)
DATETIME_FORMAT = "%d-%m-%Y %H:%M"

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INTERPRETATIONS_FILE = os.path.join(DATA_DIR, "interpretations.json")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# ──────────────────────────────────────────────
# Zodiac Sign Boundaries  (day, month) ranges
# Each tuple: (sign_name, start_day, start_month, end_day, end_month)
# ──────────────────────────────────────────────
ZODIAC_SIGNS = [
    ("Capricorn",  1,  1,  19,  1),
    ("Aquarius",   20, 1,  18,  2),
    ("Pisces",     19, 2,  20,  3),
    ("Aries",      21, 3,  19,  4),
    ("Taurus",     20, 4,  20,  5),
    ("Gemini",     21, 5,  20,  6),
    ("Cancer",     21, 6,  22,  7),
    ("Leo",        23, 7,  22,  8),
    ("Virgo",      23, 8,  22,  9),
    ("Libra",      23, 9,  22, 10),
    ("Scorpio",    23, 10, 21, 11),
    ("Sagittarius",22, 11, 21, 12),
    ("Capricorn",  22, 12, 31, 12),
]

# ──────────────────────────────────────────────
# Planets tracked in reports
# ──────────────────────────────────────────────
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Extended planets (optional / future use)
PLANETS_EXTENDED = PLANETS + ["Uranus", "Neptune", "Pluto"]

# ──────────────────────────────────────────────
# Zodiac sign degree boundaries (ecliptic longitude)
# Used for mapping a planet's ecliptic longitude → sign
# ──────────────────────────────────────────────
SIGN_NAMES_BY_DEGREE = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ──────────────────────────────────────────────
# Default geographic coordinates for common cities
# (latitude, longitude) — used when geocoding is unavailable
# ──────────────────────────────────────────────
CITY_COORDINATES = {
    "new delhi":    (28.6139,  77.2090),
    "delhi":        (28.6139,  77.2090),
    "mumbai":       (19.0760,  72.8777),
    "bangalore":    (12.9716,  77.5946),
    "bengaluru":    (12.9716,  77.5946),
    "chennai":      (13.0827,  80.2707),
    "kolkata":      (22.5726,  88.3639),
    "hyderabad":    (17.3850,  78.4867),
    "pune":         (18.5204,  73.8567),
    "ahmedabad":    (23.0225,  72.5714),
    "jaipur":       (26.9124,  75.7873),
    "lucknow":      (26.8467,  80.9462),
    "chandigarh":   (30.7333,  76.7794),
    "bhopal":       (23.2599,  77.4126),
    "patna":        (25.6093,  85.1376),
    "indore":       (22.7196,  75.8577),
    "nagpur":       (21.1458,  79.0882),
    "surat":        (21.1702,  72.8311),
    "varanasi":     (25.3176,  82.9739),
    "agra":         (27.1767,  78.0081),
    "thiruvananthapuram": (8.5241, 76.9366),
    "kochi":        (9.9312,   76.2673),
    "guwahati":     (26.1445,  91.7362),
    "bhubaneswar":  (20.2961,  85.8245),
    "dehradun":     (30.3165,  78.0322),
    "ranchi":       (23.3441,  85.3096),
    "shimla":       (31.1048,  77.1734),
    "gangtok":      (27.3389,  88.6065),
    "imphal":       (24.8170,  93.9368),
    "new york":     (40.7128, -74.0060),
    "london":       (51.5074,  -0.1278),
    "los angeles":  (34.0522, -118.2437),
    "tokyo":        (35.6762,  139.6503),
    "sydney":       (-33.8688, 151.2093),
    "dubai":        (25.2048,  55.2708),
    "singapore":    (1.3521,   103.8198),
    "paris":        (48.8566,  2.3522),
    "berlin":       (52.5200,  13.4050),
    "toronto":      (43.6532, -79.3832),
    "san francisco":(37.7749, -122.4194),
    "chicago":      (41.8781, -87.6298),
    "beijing":      (39.9042,  116.4074),
    "moscow":       (55.7558,  37.6173),
    "cairo":        (30.0444,  31.2357),
    "rio de janeiro":(-22.9068,-43.1729),
    "cape town":    (-33.9249, 18.4241),
}

# ──────────────────────────────────────────────
# CLI Theme / Display
# ──────────────────────────────────────────────
SEPARATOR = "═" * 56
SEPARATOR_THIN = "─" * 56
