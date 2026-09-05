"""The locked conversion table for the 2025-12-31 close."""
from decimal import Decimal

RATES_TO_USD = {
    "USD": Decimal("1"),
    "EUR": Decimal("1.0873"),
    "GBP": Decimal("1.2741"),
    "CAD": Decimal("0.7412"),
    "JPY": Decimal("0.00692"),
}
