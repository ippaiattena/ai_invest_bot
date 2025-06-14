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
        self.trade_log = []

        self.last_buy_price = None
        self.last_buy_date = None

    def next(self):
        if not self.position:
            if self.sma_short[0] > self.sma_long[0] and self.rsi[0] < self.p.rsi_upper:
                self.buy()
        else:
            if self.rsi[0] > self.p.rsi_upper:
                self.sell()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            dt = self.data.datetime.date(0)
            price = order.executed.price

            if order.isbuy():
                print(f"{dt}, BUY, {price}")
                self.last_buy_price = price
                self.last_buy_date = dt
                self.trade_log.append({
                    'date': dt,
                    'type': 'BUY',
                    'price': price
                })
            elif order.issell():
                holding_days = (dt - self.last_buy_date).days if self.last_buy_date else None
                profit = price - self.last_buy_price if self.last_buy_price is not None else None
                print(f"{dt}, SELL, {price}")
                self.trade_log.append({
                    'date': dt,
                    'type': 'SELL',
                    'price': price,
                    'entry_date': self.last_buy_date,
                    'entry_price': self.last_buy_price,
                    'profit': profit,
                    'holding_days': holding_days
                })

