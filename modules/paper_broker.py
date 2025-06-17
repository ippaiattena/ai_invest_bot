from modules.notifier import send_trade_notification

class PaperBroker:
    def __init__(self, mode="paper"):
        from modules.paper_wallet import PaperWallet
        self.wallet = PaperWallet()
        self.mode = mode  # "dummy", "paper", "real"

    def buy(self, ticker, price, size=1):
        self.wallet.buy(ticker, price, size)
        send_trade_notification("BUY", ticker, price, size)

    def sell(self, ticker, price, size=1):
        self.wallet.sell(ticker, price, size)
        send_trade_notification("SELL", ticker, price, size)

    def get_positions(self):
        """現在のポジションを 'ticker → dict(price, size)' の形式で返す"""
        return self.wallet.get_detailed_holdings()
    
    def process_signals(self, df):
        for _, row in df.iterrows():
            ticker = row["Ticker"]
            price = row["Close"]
            signal = row["Signal"]
            if self.mode == "dummy":
                print(f"[DUMMY ORDER] {signal} {ticker} @ {price}")
            elif self.mode == "paper":
                if signal == "Buy":
                    self.buy(ticker, price)
                elif signal == "Sell":
                    self.sell(ticker, price)
            elif self.mode == "real":
                print(f"[REAL ORDER] {signal} {ticker} @ {price}（未実装）")

    def apply_exit_strategy(self, screening_df, rsi_threshold=70):
        """
        RSIが閾値を超えていたら売却。
        """
        positions = self.get_positions()
        for ticker, info in positions.items():
            current_price = info["price"]
            match = screening_df[screening_df["Ticker"] == ticker]
            if not match.empty:
                rsi = match["RSI"].values[0]
                if rsi > rsi_threshold:
                    self.sell(ticker, current_price)

    def get_portfolio_summary(self):
        """
        現金・株式評価額・総資産を含むサマリーを返す
        """
        holdings = self.wallet.get_detailed_holdings()
        cash = self.wallet.cash
        stock_value = sum(info["price"] * info["size"] for info in holdings.values())
        total_value = cash + stock_value

        return {
            "cash": cash,
            "stock_value": stock_value,
            "total_value": total_value,
            "details": holdings
        }

    def format_portfolio_summary(self) -> str:
        summary = self.get_portfolio_summary()
        lines = []
        lines.append("💼 *保有資産サマリー*")
        lines.append(f"・総資産: ¥{summary['total_value']:,.0f}")
        lines.append(f"　├ 現金       : ¥{summary['cash']:,.0f}")
        lines.append(f"　└ 株式評価額 : ¥{summary['stock_value']:,.0f}")
        if summary["details"]:
            lines.append("　└ 保有内訳:")
            for ticker, info in summary["details"].items():
                lines.append(f"　   - `{ticker}`: {info['size']}株 @ ¥{info['price']:.2f} → ¥{info['value']:,.0f}")
        else:
            lines.append("　（株式保有なし）")
        return "\n".join(lines)
