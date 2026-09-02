class RiskEngine:
    def __init__(self):
        pass

    @staticmethod
    def calculate_lot_size(account_balance: float, risk_percent: float, entry_price: float, stop_loss_price: float) -> dict:
        """
        Calculates position size (lot) based on risk percentage and stop loss pips.
        Gold standard contract size: 1 Lot = 100 oz (1 pip / 0.10 move = $10 per lot).
        """
        if account_balance <= 0 or risk_percent <= 0 or entry_price <= 0 or stop_loss_price <= 0:
            return {"lots": 0.01, "risk_amount": 0.0, "sl_pips": 0.0}

        risk_amount = (account_balance * risk_percent) / 100.0
        sl_pips = abs(entry_price - stop_loss_price) # Difference in dollars

        if sl_pips == 0:
            return {"lots": 0.01, "risk_amount": risk_amount, "sl_pips": 0.0}

        # For Gold XAUUSD: 1 Lot 1.00 move = $100 profit/loss per 1 oz price change
        # So loss per 1 lot = sl_pips * 100
        lot_size = risk_amount / (sl_pips * 100.0)
        lot_size = round(max(0.01, min(lot_size, 10.0)), 2)

        return {
            "lots": lot_size,
            "risk_amount": round(risk_amount, 2),
            "sl_pips": round(sl_pips, 2)
        }

risk_engine = RiskEngine()
