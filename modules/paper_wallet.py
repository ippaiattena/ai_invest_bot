import os
import json
from datetime import datetime
import pytz

JST = pytz.timezone('Asia/Tokyo')

class PaperWallet:
    def __init__(self):
        self.cash = 1_000_000
        self.holdings = {}

    def buy(self, ticker, price, size=1):
        cost = price * size
        if self.cash >= cost:
            self.cash -= cost
            self.holdings[ticker] = self.holdings.get(ticker, 0) + size
            self.log_trade("BUY", ticker, price, size)
            self.save()
        else:
            print(f"❌ 資金不足: {ticker} {price} x {size}")

    def sell(self, ticker, price, size=1):
        if self.holdings.get(ticker, 0) >= size:
            self.holdings[ticker] -= size
            self.cash += price * size
            self.log_trade("SELL", ticker, price, size)
            self.save()
        else:
            print(f"❌ 保有株不足: {ticker} 売却数={size}")

    def save(self):
        data = {
            "cash": self.cash,
            "holdings": self.holdings
        }
        os.makedirs("paper_trades", exist_ok=True)
        with open("paper_trades/wallet.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def log_trade(self, trade_type, ticker, price, size):
        now_jst = datetime.now(JST)
        date_str = now_jst.strftime("%Y-%m-%d")
        time_str = now_jst.strftime("%Y-%m-%d %H:%M:%S")

        log = {
            "datetime": time_str,
            "type": trade_type,
            "ticker": ticker,
            "price": price,
            "size": size,
            "cash_after": self.cash,
            "holdings_after": self.holdings.get(ticker, 0)
        }

        os.makedirs("paper_trades", exist_ok=True)
        log_path = f"paper_trades/trade_log_{date_str}.json"

        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def print_holdings(self):
        print(f"💰 現在のキャッシュ: ¥{self.cash:,.0f}")
        for ticker, size in self.holdings.items():
            print(f"  - {ticker}: {size}株")
