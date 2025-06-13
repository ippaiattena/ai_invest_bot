# backtest.py
import yfinance as yf
import backtrader as bt
from strategies.sma_rsi_strategy import SmaRsiStrategy
from datetime import datetime

TICKER = 'AAPL'
START = '2023-01-01'
END = '2024-01-01'

# データ取得
df = yf.download(TICKER, start=START, end=END)
df.columns = df.columns.get_level_values(0)
df.dropna(inplace=True)

# backtrader用に変換
data = bt.feeds.PandasData(dataname=df)

# Cerebro（脳）セットアップ
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaRsiStrategy)
cerebro.adddata(data)
cerebro.broker.set_cash(100000)
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# 実行＆結果表示
print(f"初期資金: {cerebro.broker.getvalue():.2f}")
cerebro.run()
print(f"最終資金: {cerebro.broker.getvalue():.2f}")

# バックテスト評価指標の追加
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

results = cerebro.run()
strategy = results[0]

print("=== バックテスト評価指標 ===")
print(f"累積リターン（Total Return）: {strategy.analyzers.returns.get_analysis()['rtot']:.2%}")
print(f"年率リターン（CAGR）        : {strategy.analyzers.returns.get_analysis()['rnorm']:.2%}")
sharpe = strategy.analyzers.sharpe.get_analysis().get('sharperatio')
if sharpe is not None:
    print(f"シャープレシオ              : {sharpe:.2f}")
else:
    print("シャープレシオ              : 計算不可（取引が少ないなど）")
print(f"最大ドローダウン           : {strategy.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")

# グラフ表示
cerebro.plot(style='candlestick')