from modules.broker_base import AbstractBroker
from modules.notifier import send_trade_notification


class KabucomBroker(AbstractBroker):
    def __init__(self):
        # ここで将来的にAPIキーの読み込みや認証処理を行う想定
        self.positions = {}  # 仮のローカル保持。実際にはAPIから取得する

    def buy(self, ticker, price, size=1):
        print(f"[KABUCOM BUY] {ticker} @ {price} x {size}（仮実装）")
        send_trade_notification("BUY", ticker, price, size)
        # 仮想ポジション更新（本来はAPIで発注＆ポジション確認）
        self.positions[ticker] = self.positions.get(ticker, 0) + size

    def sell(self, ticker, price, size=1):
        print(f"[KABUCOM SELL] {ticker} @ {price} x {size}（仮実装）")
        send_trade_notification("SELL", ticker, price, size)
        # 仮想ポジション更新（本来はAPIで発注＆ポジション確認）
        current = self.positions.get(ticker, 0)
        self.positions[ticker] = max(0, current - size)
        if self.positions[ticker] == 0:
            del self.positions[ticker]

    def get_positions(self):
        # 仮の形式：{ticker: {"price": 100.0, "size": 1}}
        return {
            ticker: {"price": 100.0, "size": size}
            for ticker, size in self.positions.items()
        }

    def process_signals(self, df):
        for _, row in df.iterrows():
            ticker = row["Ticker"]
            price = row["Close"]
            signal = row["Signal"]
            if signal == "Buy":
                self.buy(ticker, price)
            elif signal == "Sell":
                self.sell(ticker, price)

    def apply_exit_strategy(self, screening_df, rule_func=None):
        if not rule_func:
            return

        exit_signals = rule_func(screening_df)
        positions = self.get_positions()
        for ticker, info in positions.items():
            if exit_signals.get(ticker):
                current_price = info["price"]
                self.sell(ticker, current_price)

    def get_portfolio_summary(self):
        return {
            "cash": 0,
            "stock_value": 0,
            "total_value": 0,
            "details": self.get_positions()
        }

    def format_portfolio_summary(self) -> str:
        summary = self.get_portfolio_summary()
        lines = []
        lines.append("💼 *KabucomBroker: 保有資産サマリー（仮）*")
        lines.append("（API接続未実装）")
        if summary["details"]:
            lines.append("　└ 保有内訳:")
            for ticker, info in summary["details"].items():
                lines.append(
                    f"　   - `{ticker}`: {info['size']}株 @ ¥{info['price']:.2f} → ¥{info['price'] * info['size']:,.0f}"
                )
        else:
            lines.append("　（株式保有なし）")
        return "\n".join(lines)
