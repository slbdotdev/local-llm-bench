"""kestrel.zones: which pricing zone a country belongs to.

Zone letters are the rate card's (R3). Depots look the zone up by country
code; the calculator itself takes the zone letter directly.
"""
from __future__ import annotations

ZONE_BY_COUNTRY = {
    "DE": "A", "NL": "A", "BE": "A", "LU": "A",
    "FR": "B", "AT": "B", "DK": "B", "CZ": "B",
    "ES": "C", "PT": "C", "IT": "C", "IE": "C",
    "SE": "D", "FI": "D", "NO": "D", "PL": "D",
}


def zone_for(country_code):
    key = country_code.strip().upper()
    if key not in ZONE_BY_COUNTRY:
        raise ValueError("no pricing zone for country %r" % country_code)
    return ZONE_BY_COUNTRY[key]
