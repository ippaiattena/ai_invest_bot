import backtrader as bt

class SmaRsiStrategy(bt.Strategy):
    params = (
        ("sma_period_short", 20),
        ("sma_period_long", 50),
        ("rsi_period", 14),
        ("rsi_upper", 70),
    )

    def __init__(self):
        self.sma_short = bt.ind.SMA(period=self.p.sma_period_short)
        self.sma_long = bt.ind.SMA(period=self.p.sma_period_long)
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.trade_log = []  # ← 売買ログ用リスト

    def next(self):
        dt = self.datas[0].datetime.date(0)
        price = self.data.close[0]

        if not self.position:
            if self.sma_short[0] > self.sma_long[0] and self.rsi[0] < self.p.rsi_upper:
                self.buy()
                print(f"{dt}, BUY, {price}")
                self.trade_log.append({
                    'date': dt,
                    'type': 'BUY',
                    'price': float(price)
                })
        else:
            if self.rsi[0] > self.p.rsi_upper:
                self.sell()
                print(f"{dt}, SELL, {price}")
                self.trade_log.append({
                    'date': dt,
                    'type': 'SELL',
                    'price': float(price)
                })
