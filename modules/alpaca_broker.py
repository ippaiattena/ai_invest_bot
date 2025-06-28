import os
import requests
from dotenv import load_dotenv
import pandas as pd
from modules.api_broker_base import ApiBrokerBase
from modules.notifier import send_trade_notification
from typing import Callable, Optional

# .env からAPIキー等を読み込む
load_dotenv()

class AlpacaBroker(ApiBrokerBase):
    def __init__(self, mode="virtual"):
        super().__init__(mode)

        if self.mode == "real":
            self.base_url = "https://api.alpaca.markets"
            self.api_key = os.getenv("ALPACA_LIVE_KEY")
            self.secret_key = os.getenv("ALPACA_LIVE_SECRET")
        else:
            self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
            self.api_key = os.getenv("ALPACA_API_KEY")
            self.secret_key = os.getenv("ALPACA_SECRET_KEY")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }

    def buy(self, ticker, price, size=1):
        self._submit_order(ticker, qty=size, side="buy")
        send_trade_notification("BUY", ticker, price, size)

    def sell(self, ticker, price, size=1):
        self._submit_order(ticker, qty=size, side="sell")
        send_trade_notification("SELL", ticker, price, size)

    def _submit_order(self, symbol, qty, side):
        order = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": "market",
            "time_in_force": "gtc"
        }
        response = requests.post(f"{self.base_url}/v2/orders", json=order, headers=self.headers)
        if response.status_code != 200:
            print(f"❌ Alpaca order failed: {response.text}")
        else:
            print(f"✅ {side.upper()} order submitted: {symbol} x {qty}")

    def get_positions(self):
        response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch positions: {response.text}")
            return {}
        positions = response.json()
        return {
            pos["symbol"]: {
                "price": float(pos["current_price"]),
                "size": int(float(pos["qty"])),
                "value": float(pos["market_value"])
            }
            for pos in positions
        }

    def process_signals(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            ticker = row["Ticker"]
            price = row["Close"]
            signal = row["Signal"]
            if signal == "Buy":
                self.buy(ticker, price)
            elif signal == "Sell":
                self.sell(ticker, price)

    def apply_exit_strategy(self, screening_df: pd.DataFrame, rule_func: Optional[Callable[[pd.DataFrame], dict[str, bool]]] = None):
        if not rule_func:
            return

        exit_signals = rule_func(screening_df)
        positions = self.get_positions()

        for ticker, info in positions.items():
            if exit_signals.get(ticker):
                self.sell(ticker, info["price"], size=info["size"])

    def get_portfolio_summary(self) -> dict:
        account = requests.get(f"{self.base_url}/v2/account", headers=self.headers).json()
        positions = self.get_positions()

        total_value = float(account["portfolio_value"])
        cash = float(account["cash"])
        stock_value = total_value - cash

        return {
            "cash": cash,
            "stock_value": stock_value,
            "total_value": total_value,
            "details": positions
        }

    def format_portfolio_summary(self) -> str:
        summary = self.get_portfolio_summary()
        lines = []
        lines.append("💼 *Alpaca保有資産サマリー*")
        lines.append(f"・総資産: ${summary['total_value']:,.2f}")
        lines.append(f"　├ 現金       : ${summary['cash']:,.2f}")
        lines.append(f"　└ 株式評価額 : ${summary['stock_value']:,.2f}")
        if summary["details"]:
            lines.append("　└ 保有内訳:")
            for ticker, info in summary["details"].items():
                lines.append(f"　   - `{ticker}`: {info['size']}株 @ ${info['price']:.2f} → ${info['value']:,.2f}")
        else:
            lines.append("　（株式保有なし）")
        return "\n".join(lines)
