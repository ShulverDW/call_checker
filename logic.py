# logic.py

import phonenumbers
from phonenumbers import geocoder, timezone
from datetime import datetime
import pytz

# --------------------------------------------------
# 1. Settings
# --------------------------------------------------

# Your / your friend's home timezone
# Change "Europe/London" if needed, e.g. "America/New_York"
HOME_TZ = pytz.timezone("Europe/London")

# Countries from your "Not Qualified" list (2-letter ISO country codes)
BLOCKED_COUNTRIES_BASE = {
    "IN",  # India
    "AF",  # Afghanistan
    "AL",  # Albania
    "BS",  # Bahamas
    "BD",  # Bangladesh
    "BY",  # Belarus
    "BZ",  # Belize
    "BT",  # Bhutan
    "BO",  # Bolivia
    "BA",  # Bosnia and Herzegovina
    "BN",  # Brunei
    "CO",  # Colombia
    "CY",  # Cyprus
    "DO",  # Dominican Republic
    "EC",  # Ecuador
    "SV",  # El Salvador
    "EE",  # Estonia
    "GT",  # Guatemala
    "HT",  # Haiti
    "HN",  # Honduras
    "JO",  # Jordan
    "JM",  # Jamaica
    "KZ",  # Kazakhstan
    "LV",  # Latvia
    "LB",  # Lebanon
    "NP",  # Nepal
    "NI",  # Nicaragua
    "MK",  # North Macedonia
    "PY",  # Paraguay
    "RU",  # Russia
    "ZA",  # South Africa
    "SY",  # Syria
    "TR",  # Turkey
    "UA",  # Ukraine
    "UY",  # Uruguay
    "UZ",  # Uzbekistan
    "VE",  # Venezuela
    "YE",  # Yemen
    "IR",  # Iran
    "MA",  # Morocco
    "MD",  # Moldova
    "TH",  # Thailand
    "VN",  # Vietnam
    "PK",  # Pakistan
    "PH",  # Philippines
    "MX",  # Mexico
    "MY",  # Malaysia
}

# All African countries (any country in Africa = not qualified)
AFRICAN_COUNTRIES = {
    "DZ","AO","BJ","BW","BF","BI","CM","CV","CF","TD","KM",
    "CG","CD","DJ","EG","GQ","ER","SZ","ET","GA","GM","GH",
    "GN","GW","CI","KE","LS","LR","LY","MG","MW","ML","MR",
    "MU","MZ","NA","NE","NG","RW","ST","SN","SC","SL","SO",
    "SS","SD","TZ","TG","TN","UG","ZM","ZW"
}

# Final set of blocked countries:
BLOCKED_COUNTRIES = BLOCKED_COUNTRIES_BASE.union(AFRICAN_COUNTRIES)


def is_allowed(region_code: str) -> bool:
    """
    Return True if a country (by 2-letter code, e.g. 'GB') is allowed.
    Any country in BLOCKED_COUNTRIES is NOT allowed.
    """
    if not region_code:
        # If we can't detect the country, best to treat as NOT allowed
        return False
    return region_code not in BLOCKED_COUNTRIES


# --------------------------------------------------
# 2. Main function used by the app
# --------------------------------------------------

def analyse_number(raw_number: str) -> dict:
    """
    Take a phone number string like '+447123456789' and return info about it.

    Returns a dictionary with keys like:
    - valid (bool)
    - error (str, if not valid)
    - country (name)
    - region (2-letter ISO code)
    - allowed (bool)
    - has_timezone (bool)
    - home_time (str)
    - dest_time (str)
    - diff_hours (float)
    """
    raw_number = raw_number.strip()

    # Try to parse the number
    try:
        number = phonenumbers.parse(raw_number, None)
    except phonenumbers.NumberParseException:
        return {
            "valid": False,
            "error": "Could not parse number. Make sure it includes country code, e.g. +447..."
        }

    # Check if it's a valid phone number
    if not phonenumbers.is_valid_number(number):
        return {
            "valid": False,
            "error": "This phone number is not a valid number."
        }

    # Country/region info
    region = geocoder.region_code_for_number(number)  # e.g. "GB"
    country_name = geocoder.country_name_for_number(number, "en") or "Unknown country"

    # Check if country is allowed
    allowed = is_allowed(region)

    # Timezone info
    timezones = timezone.time_zones_for_number(number)
    if not timezones:
        # No timezone available for this number
        return {
            "valid": True,
            "country": country_name,
            "region": region,
            "allowed": allowed,
            "has_timezone": False,
            "error": "No timezone information for this number."
        }

    dest_tz = pytz.timezone(timezones[0])

    # Current times in home and destination timezones
    now_home = datetime.now(HOME_TZ)
    now_dest = now_home.astimezone(dest_tz)

    # Time difference in hours
    diff_hours = (now_dest.utcoffset() - now_home.utcoffset()).total_seconds() / 3600

    return {
        "valid": True,
        "country": country_name,
        "region": region,
        "allowed": allowed,
        "has_timezone": True,
        "home_time": now_home.strftime("%Y-%m-%d %H:%M"),
        "dest_time": now_dest.strftime("%Y-%m-%d %H:%M"),
        "diff_hours": diff_hours,
    }
