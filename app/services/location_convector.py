# services/astrology_service.py

import geonamescache
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz
from functools import lru_cache
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
import swisseph as swe

# ---------------------------
# Initialize global objects
# ---------------------------

gc = geonamescache.GeonamesCache()
cities_data = gc.get_cities()
countries_data = gc.get_countries()
geolocator = Nominatim(user_agent="my_app")
tf = TimezoneFinder()

# Swiss Ephemeris path (set once)
swe.set_ephe_path("ephe")  # make sure ephe folder contains ephemeris files

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# ---------------------------
# Prepare lookup structures
# ---------------------------

country_list = [country['name'] for country in countries_data.values()]

country_to_cities = {}
city_lookup = {}  # (country_iso, city_name) -> city_data
for city in cities_data.values():
    iso = city['countrycode']
    name = city['name']
    country_to_cities.setdefault(iso, []).append(name)
    city_lookup[(iso, name)] = city

iso_to_country = {iso: c['name'] for iso, c in countries_data.items()}

# ---------------------------
# Helper functions
# ---------------------------

def correct_name(input_name: str, choices: list[str]) -> str:
    """Fuzzy match input_name against a list of choices."""
    match = process.extractOne(input_name, choices, scorer=fuzz.WRatio)
    return match[0] if match else None

def timezone_offset_string(lat: float, lon: float, dt: datetime = None) -> str:
    """Return UTC offset as +HH:MM or -HH:MM string."""
    dt = dt or datetime.utcnow()
    tz_str = tf.timezone_at(lat=lat, lng=lon)
    if not tz_str:
        return None
    tz = pytz.timezone(tz_str)
    offset_sec = tz.utcoffset(dt).total_seconds()
    sign = '+' if offset_sec >= 0 else '-'
    offset_sec = abs(int(offset_sec))
    hours = offset_sec // 3600
    minutes = (offset_sec % 3600) // 60
    return f"{sign}{hours:02d}:{minutes:02d}"

def get_house(longitude: float, houses: list[float]) -> int:
    """Determine which Placidus house a given longitude belongs to."""
    for i in range(11):
        if houses[i] <= longitude < houses[i + 1]:
            return i + 1
    return 12

# ---------------------------
# Main service functions
# ---------------------------

@lru_cache(maxsize=5000)
def get_lat_lon_timezone(country_input: str, city_input: str) -> dict | None:
    """Get city/country lat/lon and UTC offset string."""
    country = correct_name(country_input, country_list)
    if not country:
        return None

    # Find ISO
    country_iso = next((iso for iso, c in countries_data.items() if c['name'] == country), None)
    if not country_iso:
        return None

    # Restrict cities to this country
    candidate_cities = country_to_cities.get(country_iso, [])
    city = correct_name(city_input, candidate_cities)
    if not city:
        return None

    # Try geonamescache first
    city_data = city_lookup.get((country_iso, city))
    if city_data and "latitude" in city_data and "longitude" in city_data:
        lat = city_data["latitude"]
        lon = city_data["longitude"]
    else:
        # Fallback to geopy
        location = geolocator.geocode(f"{city}, {country}")
        if location:
            lat = location.latitude
            lon = location.longitude
        else:
            return None

    offset_str = timezone_offset_string(lat, lon)
    return {
        "city": city,
        "country": country,
        "latitude": lat,
        "longitude": lon,
        "timezone_offset": offset_str
    }

def calculate_chiron(birth_date: str, birth_time: str, timezone_offset: str, latitude: float, longitude: float) -> dict:
    """Calculate Chiron's zodiac sign, longitude, and house (Placidus)."""

    # Convert local time to UTC
    sign = 1 if timezone_offset[0] == '+' else -1
    hours, minutes = map(int, timezone_offset[1:].split(":"))
    offset_min = sign * (hours * 60 + minutes)
    local_tz = pytz.FixedOffset(offset_min)

    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    dt_local = local_tz.localize(dt)
    dt_utc = dt_local.astimezone(pytz.utc)

    # Julian Day UT
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)

    # Chiron position
    chiron_data, _ = swe.calc_ut(jd_ut, swe.CHIRON)
    chiron_long = chiron_data[0]

    # Zodiac sign
    zodiac_sign = SIGNS[int(chiron_long // 30)]

    # House placement
    houses, ascmc = swe.houses(jd_ut, latitude, longitude, b'P')
    chiron_house = get_house(chiron_long, houses)

    return {
        "longitude": round(chiron_long, 2),
        "zodiac_sign": zodiac_sign,
        "house": chiron_house
    }

# ---------------------------
# Combined utility
# ---------------------------

def get_chiron_by_city(country_input: str, city_input: str, birth_date: str, birth_time: str) -> dict | None:
    """Full service: from city/country + birth data → Chiron info with timezone."""
    loc_info = get_lat_lon_timezone(country_input, city_input)
    if not loc_info:
        return None

    chiron_info = calculate_chiron(
        birth_date=birth_date,
        birth_time=birth_time,
        timezone_offset=loc_info["timezone_offset"],
        latitude=loc_info["latitude"],
        longitude=loc_info["longitude"]
    )

    return {
        "city": loc_info["city"],
        "country": loc_info["country"],
        "latitude": loc_info["latitude"],
        "longitude": loc_info["longitude"],
        "timezone_offset": loc_info["timezone_offset"],
        "chiron": chiron_info
    }
