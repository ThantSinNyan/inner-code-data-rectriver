import swisseph as swe
import pytz
from datetime import datetime
import os

EPHE_PATH = "/app/ephe"
print(">>> Using EPHE_PATH:", EPHE_PATH)
print(">>> Files:", os.listdir(EPHE_PATH))
swe.set_ephe_path(EPHE_PATH)

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def parse_timezone_offset(tz_str: str) -> int:
    """
    Parse timezone string (+HH:MM or -HH:MM) into minutes offset.
    """
    sign = 1 if tz_str[0] == '+' else -1
    hours, minutes = map(int, tz_str[1:].split(':'))
    return sign * (hours * 60 + minutes)

def get_house(longitude: float, houses: list[float]) -> int:
    """
    Determine which house a given longitude belongs to.
    Uses Placidus houses.
    """
    for i in range(11):  # houses 1–11
        if houses[i] <= longitude < houses[i + 1]:
            return i + 1
    return 12  # wrap-around → house 12

def calculate_chiron_position(
    birth_date: str,
    birth_time: str,
    timezone: str,
    latitude: float,
    longitude: float
) -> dict:
    """
    Service method to calculate Chiron's zodiac sign and house placement.
    Optimized for FastAPI usage (minimal memory, efficient calls).
    """

    # Step 1: Convert local time → UTC
    local_tz_offset = parse_timezone_offset(timezone)
    local_tz = pytz.FixedOffset(local_tz_offset)
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    dt_local = local_tz.localize(dt)
    dt_utc = dt_local.astimezone(pytz.utc)

    # Step 2: Julian Day
    jd_ut = swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0
    )
    swe.set_ephe_path(EPHE_PATH)

    # Step 3: Chiron position
    chiron_data, _ = swe.calc_ut(jd_ut, swe.CHIRON)
    chiron_long = chiron_data[0]

    # Step 4: Zodiac sign
    sign_index = int(chiron_long // 30)
    zodiac_sign = SIGNS[sign_index]

    # Step 5: House placement (Placidus)
    houses, ascmc = swe.houses(jd_ut, latitude, longitude, b'P')
    chiron_house = get_house(chiron_long, houses)

    # Step 6: Return structured result
    return {
        "longitude": round(chiron_long, 2),
        "zodiac_sign": zodiac_sign,
        "house": chiron_house
    }
