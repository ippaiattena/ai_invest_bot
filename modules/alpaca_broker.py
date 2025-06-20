import os
import requests
from dotenv import load_dotenv
from modules.notifier import send_trade_notification
from modules.broker_base import BrokerBase

# .env からAPIキー等を読み込む
load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}


class AlpacaBroker(BrokerBase):
    def __init__(self, mode="alpaca"):
        self.mode = mode

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
            "type": "market",  # 成行注文
            "time_in_force": "gtc"  # 有効期限: Good-Till-Cancelled
        }
        response = requests.post(f"{BASE_URL}/v2/orders", json=order, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Alpaca order failed: {response.text}")
        else:
            print(f"✅ {side.upper()} order submitted: {symbol} x {qty}")

    def get_positions(self):
        response = requests.get(f"{BASE_URL}/v2/positions", headers=HEADERS)
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

    def format_portfolio_summary(self) -> str:
        # Alpacaは口座情報APIで総資産なども取れる
        account = requests.get(f"{BASE_URL}/v2/account", headers=HEADERS).json()
        positions = self.get_positions()

        total_value = float(account["portfolio_value"])
        cash = float(account["cash"])
        stock_value = total_value - cash

        lines = []
        lines.append("💼 *Alpaca保有資産サマリー*")
        lines.append(f"・総資産: ${total_value:,.2f}")
        lines.append(f"　├ 現金       : ${cash:,.2f}")
        lines.append(f"　└ 株式評価額 : ${stock_value:,.2f}")
        if positions:
            lines.append("　└ 保有内訳:")
            for ticker, info in positions.items():
                lines.append(f"　   - `{ticker}`: {info['size']}株 @ ${info['price']:.2f} → ${info['value']:,.2f}")
        else:
            lines.append("　（株式保有なし）")
        return "\n".join(lines)
