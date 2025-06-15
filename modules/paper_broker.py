import os
import json
from datetime import datetime
from modules.notifier import send_trade_notification

class PaperBroker:
    def __init__(self, log_dir="paper_trades"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.positions = {}  # 現在の保有株（ティッカー → 平均取得単価）

    def buy(self, ticker, price, size=1):
        self.positions[ticker] = {"price": price, "size": size}
        self._log_trade("BUY", ticker, price, size)

    def sell(self, ticker, price, size=1):
        if ticker not in self.positions:
            print(f"[WARN] {ticker} は保有していません")
            return
        self._log_trade("SELL", ticker, price, size)
        del self.positions[ticker]

    def _log_trade(self, side, ticker, price, size):
        trade = {
            "time": datetime.now().isoformat(),
            "side": side,
            "ticker": ticker,
            "price": price,
            "size": size,
        }
        today = datetime.today().strftime("%Y-%m-%d")
        filepath = os.path.join(self.log_dir, f"{today}.json")

        trades = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                trades = json.load(f)

        trades.append(trade)
        with open(filepath, "w") as f:
            json.dump(trades, f, indent=2)

        print(f"[PAPER ORDER] {side} {ticker} @ {price} size={size}")

        # Slack通知追加
        send_trade_notification(side, ticker, price, size)
        