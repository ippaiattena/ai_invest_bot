import os
import json
from datetime import datetime
import pytz
import yfinance as yf

JST = pytz.timezone('Asia/Tokyo')

class PaperWallet:
    def __init__(self):
        self.cash = 1_000_000
        self.holdings = {}
        self.holding_dates = {}

    def reset_wallet(self):
        """ウォレットを初期状態に戻す"""
        self.cash = 1_000_000
        self.holdings = {}
        self.holding_dates = {}
        self.save()
        print("🔁 Paper wallet を初期化しました。")

    def get_position(self, ticker):
        """指定ティッカーの保有数を返す（未保有なら0）"""
        return self.holdings.get(ticker, 0)

    def get_all_positions(self):
        """すべての保有ポジションを返す"""
        return self.holdings.copy()

    def buy(self, ticker, price, size=1):
        cost = price * size
        if self.cash >= cost:
            self.cash -= cost
            self.holdings[ticker] = self.holdings.get(ticker, 0) + size
            self.holding_dates[ticker] = datetime.now(JST).isoformat()
            self.log_trade("BUY", ticker, price, size)
            self.save()
        else:
            print(f"❌ 資金不足: {ticker} {price} x {size}")

    def sell(self, ticker, price, size=1):
        if self.holdings.get(ticker, 0) >= size:
            self.holdings[ticker] -= size
            self.holding_dates.pop(ticker, None)
            self.cash += price * size
            self.log_trade("SELL", ticker, price, size)
            self.save()
            if self.holdings[ticker] == 0:
                del self.holdings[ticker]
        else:
            print(f"❌ 保有株不足: {ticker} 売却数={size}")

    def save(self):
        data = {
            "cash": self.cash,
            "holdings": self.holdings,
            "holding_dates": self.holding_dates
        }
        os.makedirs("local_trades", exist_ok=True)
        with open("local_trades/wallet.json", "w", encoding="utf-8") as f:
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

        os.makedirs("local_trades", exist_ok=True)
        log_path = f"local_trades/trade_log_{date_str}.json"

        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def print_holdings(self, verbose=True):
        if verbose:
            print(f"💰 現在のキャッシュ: ¥{self.cash:,.0f}")
            if not self.holdings:
                print("  （保有ポジションなし）")
            else:
                for ticker, size in self.holdings.items():
                    print(f"  - {ticker}: {size}株")
        return {
            "cash": self.cash,
            "holdings": self.holdings.copy()
        }

    def get_detailed_holdings(self):
        return {
            ticker: {
                "price": self.get_latest_price(ticker),
                "size": size,
                "value": self.get_latest_price(ticker) * size
            }
            for ticker, size in self.holdings.items()
        }

    def get_latest_price(self, ticker):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                return data["Close"].iloc[-1]
            else:
                print(f"⚠️ {ticker} の価格データが取得できませんでした（空のデータ）")
                return 100.0
        except Exception as e:
            print(f"⚠️ {ticker} の価格取得中にエラー発生: {e}")
            return 100.0

    def get_portfolio_value(self, price_lookup=None):
        """
        現在の保有資産の評価額と総資産を返す。
        price_lookup: 任意で価格取得関数を指定可能（例: lambda ticker: 最新株価）
        """
        total_stock_value = 0
        detailed = {}

        for ticker, size in self.holdings.items():
            if price_lookup:
                price = price_lookup(ticker)
            else:
                price = self.get_latest_price(ticker)
            value = price * size
            total_stock_value += value
            detailed[ticker] = {
                "size": size,
                "price": round(price, 2),
                "value": round(value, 2),
            }

        total_value = self.cash + total_stock_value

        return {
            "total_value": round(total_value, 2),
            "cash": round(self.cash, 2),
            "stock_value": round(total_stock_value, 2),
            "details": detailed,
        }

    def get_holding_days(self, ticker):
        """
        指定ティッカーの保有日数を返す（なければ0）
        """
        if ticker not in self.holding_dates:
            return 0
        try:
            buy_date = datetime.fromisoformat(self.holding_dates[ticker])
            now = datetime.now(JST)
            return (now - buy_date).days
        except Exception:
            return 0
        
    def get_unrealized_gain(self, ticker, current_price):
        """
        含み損益率 = (現在価格 - 平均取得価格) / 平均取得価格
        ※今回は取得価格を100円（仮）と仮定
        """
        if ticker not in self.holdings or self.holdings[ticker] == 0:
            return 0.0
        cost_price = 100.0  # TODO: 実際の平均取得価格に差し替え可
        return (current_price - cost_price) / cost_price
