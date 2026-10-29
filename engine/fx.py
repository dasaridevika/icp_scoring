"""
Currency FX Engine (Versioned).
Normalizes any native global or regional currency amount to USD without data corruption.
Last rate baseline audit: 2026-10-28.
"""

from typing import Dict, Tuple, Optional

# Authoritative pegged & benchmark FX exchange rates to USD (audited 2026-10-28)
FX_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.28,
    "INR": 0.012,
    "CAD": 0.74,
    "AUD": 0.66,
    "AED": 0.272,
    "SGD": 0.76,
    "JPY": 0.0068
}

FX_RATES_LAST_UPDATED = "2026-10-28"

SCALE_MULTIPLIERS: Dict[str, int] = {
    "Millions (M)": 1_000_000,
    "Crores (Cr)": 10_000_000,
    "Billions (B)": 1_000_000_000,
    "Lakhs (L)": 100_000,
    "Thousands (k)": 1_000,
    "Exact / Standard": 1
}


class FXEngine:
    @classmethod
    def normalize_to_usd(
        cls,
        amount: float,
        unit: str = "Exact / Standard",
        currency_code: str = "USD"
    ) -> Tuple[float, float]:
        if amount is None or amount <= 0:
            return 0.0, 0.0
        code = (currency_code or "USD").upper().strip()
        if code not in FX_RATES_TO_USD:
            raise ValueError(
                f"Unsupported or unknown currency code: '{code}'. "
                f"Supported currencies: {list(FX_RATES_TO_USD.keys())}"
            )
        mult = SCALE_MULTIPLIERS.get(unit, 1)
        native_total = float(amount) * mult
        fx_rate = FX_RATES_TO_USD[code]
        usd_total = native_total * fx_rate
        return native_total, usd_total
