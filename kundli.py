"""
kundli.py — Birth chart (Kundli) generation and planetary position calculation.

Uses pyswisseph (Swiss Ephemeris) for accurate planetary longitude calculations.
Provides chart generation, planet positions, ascendant, and house calculations.
"""

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False

from config import PLANETS, SIGN_NAMES_BY_DEGREE
from zodiac import get_sign_from_longitude, get_zodiac_sign
from utils import to_julian_day, longitude_to_sign, longitude_to_sign_degree


# ──────────────────────────────────────────────
# Swiss Ephemeris planet ID mapping
# ──────────────────────────────────────────────
SWISSEPH_PLANET_IDS = {
    "Sun":     0,   # swe.SUN
    "Moon":    1,   # swe.MOON
    "Mercury": 2,   # swe.MERCURY
    "Venus":   3,   # swe.VENUS
    "Mars":    4,   # swe.MARS
    "Jupiter": 5,   # swe.JUPITER
    "Saturn":  6,   # swe.SATURN
    "Uranus":  7,   # swe.URANUS
    "Neptune": 8,   # swe.NEPTUNE
    "Pluto":   9,   # swe.PLUTO
}


class BirthChart:
    """
    Represents a complete birth chart (Kundli).

    Attributes
    ----------
    birth_dt : datetime
        Combined date + time of birth.
    latitude : float
        Birth location latitude.
    longitude : float
        Birth location longitude.
    city : str
        Birth city name.
    planet_positions : dict
        {planet_name: {"longitude": float, "sign": str, "degree": str}}
    ascendant : dict
        {"longitude": float, "sign": str, "degree": str}
    houses : list
        List of 12 house cusps with sign info.
    sun_sign : str
    moon_sign : str
    """

    def __init__(self, birth_dt: datetime, latitude: float, longitude: float, city: str):
        self.birth_dt = birth_dt
        self.latitude = latitude
        self.longitude = longitude
        self.city = city

        self.planet_positions: Dict[str, dict] = {}
        self.ascendant: dict = {}
        self.houses: List[dict] = []
        self.sun_sign: str = ""
        self.moon_sign: str = ""

        # Generate the chart
        self._generate()

    def _generate(self) -> None:
        """Generate the full birth chart."""
        if SWE_AVAILABLE:
            self._calculate_with_swisseph()
        else:
            self._calculate_fallback()

    # ──────────────────────────────────────────
    # Primary: Swiss Ephemeris calculation
    # ──────────────────────────────────────────

    def _calculate_with_swisseph(self) -> None:
        """Use pyswisseph for accurate planetary calculations."""
        jd = to_julian_day(self.birth_dt)

        # Calculate planet positions
        for planet_name in PLANETS:
            pid = SWISSEPH_PLANET_IDS.get(planet_name)
            if pid is None:
                continue
            try:
                result = swe.calc_ut(jd, pid)
                # result is a tuple: ((lon, lat, dist, speed_lon, speed_lat, speed_dist), retflag)
                lon = result[0][0]
                sign = longitude_to_sign(lon)
                degree_str = longitude_to_sign_degree(lon)

                self.planet_positions[planet_name] = {
                    "longitude": round(lon, 4),
                    "sign": sign,
                    "degree": degree_str,
                }
            except Exception:
                self.planet_positions[planet_name] = {
                    "longitude": 0.0,
                    "sign": "Unknown",
                    "degree": "N/A",
                }

        # Calculate Ascendant and Houses
        try:
            houses_tuple = swe.houses(jd, self.latitude, self.longitude, b'P')
            # houses_tuple[0] = 12 house cusps, houses_tuple[1] = ascmc (Asc, MC, etc.)
            cusps = houses_tuple[0]
            ascmc = houses_tuple[1]

            asc_lon = ascmc[0]
            self.ascendant = {
                "longitude": round(asc_lon, 4),
                "sign": longitude_to_sign(asc_lon),
                "degree": longitude_to_sign_degree(asc_lon),
            }

            self.houses = []
            for i, cusp_lon in enumerate(cusps):
                self.houses.append({
                    "house": i + 1,
                    "longitude": round(cusp_lon, 4),
                    "sign": longitude_to_sign(cusp_lon),
                    "degree": longitude_to_sign_degree(cusp_lon),
                })

        except Exception:
            self._set_default_ascendant_houses()

        # Set Sun / Moon signs
        self.sun_sign = self.planet_positions.get("Sun", {}).get("sign", "Unknown")
        self.moon_sign = self.planet_positions.get("Moon", {}).get("sign", "Unknown")

    # ──────────────────────────────────────────
    # Fallback: approximation without swisseph
    # ──────────────────────────────────────────

    def _calculate_fallback(self) -> None:
        """
        Approximate planetary positions when pyswisseph is not installed.
        Uses simplified mean-longitude formulae — not astronomically precise,
        but good enough for demonstration purposes.
        """
        jd = to_julian_day(self.birth_dt)
        T = (jd - 2451545.0) / 36525.0  # Julian centuries from J2000

        # Approximate mean longitudes (simplified)
        mean_longitudes = {
            "Sun":     280.46646 + 36000.76983 * T,
            "Moon":    218.3165  + 481267.8813 * T,
            "Mercury": 252.2509  + 149472.6746 * T,
            "Venus":   181.9798  + 58517.8157  * T,
            "Mars":    355.4330  + 19140.2993  * T,
            "Jupiter": 34.3515   + 3034.9057   * T,
            "Saturn":  50.0774   + 1222.1138   * T,
        }

        for planet_name in PLANETS:
            lon = mean_longitudes.get(planet_name, 0.0) % 360.0
            sign = longitude_to_sign(lon)
            degree_str = longitude_to_sign_degree(lon)

            self.planet_positions[planet_name] = {
                "longitude": round(lon, 4),
                "sign": sign,
                "degree": degree_str,
            }

        # Approximate ascendant using ARMC + latitude
        self._approximate_ascendant(jd, T)

        # Generate approximate houses (equal house system)
        self._approximate_houses()

        # Set Sun / Moon signs
        self.sun_sign = self.planet_positions.get("Sun", {}).get("sign", "Unknown")
        self.moon_sign = self.planet_positions.get("Moon", {}).get("sign", "Unknown")

    def _approximate_ascendant(self, jd: float, T: float) -> None:
        """Approximate the Ascendant using Local Sidereal Time."""
        # Greenwich Mean Sidereal Time (in degrees)
        gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + T * T * (0.000387933 - T / 38710000.0)
        gmst = gmst % 360.0

        # Local Sidereal Time
        lst = (gmst + self.longitude) % 360.0

        # Obliquity of ecliptic (approx)
        obliquity = 23.4393 - 0.0130 * T
        obl_rad = math.radians(obliquity)
        lat_rad = math.radians(self.latitude)

        # Ascendant formula
        lst_rad = math.radians(lst)
        y = -math.cos(lst_rad)
        x = math.sin(lst_rad) * math.cos(obl_rad) + math.tan(lat_rad) * math.sin(obl_rad)
        asc_lon = math.degrees(math.atan2(y, x)) % 360.0

        self.ascendant = {
            "longitude": round(asc_lon, 4),
            "sign": longitude_to_sign(asc_lon),
            "degree": longitude_to_sign_degree(asc_lon),
        }

    def _approximate_houses(self) -> None:
        """Generate 12 equal-sized houses starting from the Ascendant."""
        asc_lon = self.ascendant.get("longitude", 0.0)
        self.houses = []
        for i in range(12):
            cusp_lon = (asc_lon + i * 30) % 360.0
            self.houses.append({
                "house": i + 1,
                "longitude": round(cusp_lon, 4),
                "sign": longitude_to_sign(cusp_lon),
                "degree": longitude_to_sign_degree(cusp_lon),
            })

    def _set_default_ascendant_houses(self) -> None:
        """Set defaults when house/ascendant calc fails."""
        self.ascendant = {
            "longitude": 0.0,
            "sign": "Aries",
            "degree": "00.00° Aries",
        }
        self._approximate_houses()

    # ──────────────────────────────────────────
    # Public helpers
    # ──────────────────────────────────────────

    def get_planet_sign(self, planet: str) -> str:
        """Return the zodiac sign for a given planet."""
        return self.planet_positions.get(planet, {}).get("sign", "Unknown")

    def get_summary_dict(self) -> dict:
        """Return a serialisable summary of the chart."""
        return {
            "birth_datetime": self.birth_dt.strftime("%d-%m-%Y %H:%M"),
            "city": self.city,
            "latitude": self.latitude,
            "longitude_geo": self.longitude,
            "sun_sign": self.sun_sign,
            "moon_sign": self.moon_sign,
            "ascendant": self.ascendant.get("sign", "Unknown"),
            "planets": {
                name: data.get("sign", "Unknown")
                for name, data in self.planet_positions.items()
            },
            "houses": [
                {"house": h["house"], "sign": h["sign"]}
                for h in self.houses
            ],
        }


# ──────────────────────────────────────────────
# Module-level convenience function
# ──────────────────────────────────────────────

def generate_birth_chart(birth_dt: datetime, latitude: float, longitude: float, city: str) -> BirthChart:
    """
    Create and return a BirthChart for the given birth details.

    Parameters
    ----------
    birth_dt : datetime
        Date and time of birth.
    latitude : float
        Birth location latitude.
    longitude : float
        Birth location longitude.
    city : str
        Birth city name.

    Returns
    -------
    BirthChart
        Fully computed birth chart object.
    """
    return BirthChart(birth_dt, latitude, longitude, city)
