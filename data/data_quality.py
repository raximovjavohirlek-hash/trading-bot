from __future__ import annotations
import time
from typing import Optional, Tuple
from core.config import settings
from core.logger import logger

class DataQualityEngine:
    def __init__(self):
        self.last_valid_price: Optional[float] = None
        self.last_tick_time: float = 0.0

    def validate_tick(self, tick: dict) -> Tuple[bool, str]:
        """
        Validates tick object. Returns (is_valid: bool, reason: str).
        """
        price = tick.get("price")
        bid = tick.get("bid")
        ask = tick.get("ask")
        spread = tick.get("spread", 0.0)
        ts = tick.get("timestamp", 0.0)
        now = time.time()

        # 1. Zero or negative price check
        if not price or price <= 0 or not bid or not ask:
            return False, "INVALID_ZERO_PRICE: Narx yoki bid/ask nol bo'lishi mumkin emas."

        # 2. Bid vs Ask order
        if ask < bid:
            return False, f"INVALID_SPREAD: Ask ({ask}) Bid ({bid}) dan kichik bo'lishi mumkin emas."

        # 3. Abnormal spread check
        if spread > settings.MAX_SPREAD_THRESHOLD:
            logger.warning(f"⚠️ Spred abnormal darajada yuqori: ${spread}")
            return False, f"ABNORMAL_SPREAD: Spred (${spread}) ruxsat etilgan limitdan (${settings.MAX_SPREAD_THRESHOLD}) yuqori."

        # 4. Stale price check
        if (now - ts) > settings.STALE_PRICE_SECONDS:
            return False, f"STALE_PRICE: Narx ma'lumoti eski ({int(now - ts)} soniya avvalgi)."

        # 5. Outlier price jump check (> 5% jump in a single tick)
        if self.last_valid_price and self.last_valid_price > 0:
            change_ratio = abs(price - self.last_valid_price) / self.last_valid_price
            if change_ratio > 0.05: # 5% spike in single tick
                return False, f"OUTLIER_SPIKE: Kutilmagan narx sakrashi ({round(change_ratio*100, 2)}%)."

        self.last_valid_price = price
        self.last_tick_time = now
        return True, "OK"

data_quality_engine = DataQualityEngine()
