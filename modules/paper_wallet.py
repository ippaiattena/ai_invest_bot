import json
import os

class PaperWallet:
    def __init__(self, cash=1_000_000, holdings=None):
        self.cash = cash
        self.holdings = holdings if holdings else {}

    def buy(self, ticker, price):
        if self.cash < price:
            print(f"[PAPER ORDER] 現金不足で {ticker} の購入失敗: {price}")
            return
        self.cash -= price
        self.holdings[ticker] = self.holdings.get(ticker, 0) + 1

    def sell(self, ticker, price):
        if self.holdings.get(ticker, 0) <= 0:
            print(f"[PAPER ORDER] 保有なしで {ticker} の売却失敗")
            return
        self.holdings[ticker] -= 1
        self.cash += price

    def to_dict(self):
        return {"cash": self.cash, "holdings": self.holdings}

    def save(self, path="data/paper_wallet.json"):
        os.makedirs("data", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path="data/paper_wallet.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(cash=data.get("cash", 1_000_000), holdings=data.get("holdings", {}))
        return cls()