from core.database import db_manager
from core.logger import logger

class PaperTradingEngine:
    def __init__(self):
        pass

    async def open_trade(self, symbol: str, trade_type: str, entry_price: float, sl: float, tp: float) -> dict:
        """Opens a paper trade for research hypothesis testing."""
        trade_id = await db_manager.save_paper_trade(
            symbol=symbol,
            trade_type=trade_type,
            entry_price=entry_price,
            sl=sl,
            tp=tp
        )
        logger.info(f"Paper Trade ochildi (#{trade_id}): {trade_type} @ {entry_price}, SL: {sl}, TP: {tp}")
        return {
            "trade_id": trade_id,
            "status": "OPEN",
            "type": trade_type,
            "entry_price": entry_price,
            "sl": sl,
            "tp": tp
        }

    async def update_open_trades(self, current_price: float):
        """Checks open paper trades against current price for TP/SL/Invalidation."""
        open_trades = await db_manager.get_open_paper_trades()
        for trade in open_trades:
            t_id = trade["id"]
            t_type = trade["type"]
            entry = trade["entry_price"]
            sl = trade["sl"]
            tp = trade["tp"]

            if t_type == "BUY":
                if current_price >= tp:
                    pnl = round((tp - entry) * 100, 2)
                    await db_manager.update_paper_trade(t_id, "CLOSED_TP", pnl)
                    logger.info(f"Paper Trade #{t_id} TP ga erishdi! PnL: ${pnl}")
                elif current_price <= sl:
                    pnl = round((sl - entry) * 100, 2)
                    await db_manager.update_paper_trade(t_id, "CLOSED_SL", pnl)
                    logger.info(f"Paper Trade #{t_id} SL bilan yopildi. PnL: ${pnl}")
            elif t_type == "SELL":
                if current_price <= tp:
                    pnl = round((entry - tp) * 100, 2)
                    await db_manager.update_paper_trade(t_id, "CLOSED_TP", pnl)
                    logger.info(f"Paper Trade #{t_id} TP ga erishdi! PnL: ${pnl}")
                elif current_price >= sl:
                    pnl = round((entry - sl) * 100, 2)
                    await db_manager.update_paper_trade(t_id, "CLOSED_SL", pnl)
                    logger.info(f"Paper Trade #{t_id} SL bilan yopildi. PnL: ${pnl}")

paper_engine = PaperTradingEngine()
