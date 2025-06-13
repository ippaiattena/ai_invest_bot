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

    def next(self):
        if not self.position:
            if self.sma_short[0] > self.sma_long[0] and self.rsi[0] < self.p.rsi_upper:
                self.buy()
        else:
            if self.rsi[0] > self.p.rsi_upper:
                self.sell()
