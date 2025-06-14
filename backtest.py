import matplotlib
matplotlib.use('Agg')  # 表示せずに保存だけする

import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt
import os
import pandas as pd
from strategies.sma_rsi_strategy import SmaRsiStrategy

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

# バックテスト評価指標の追加
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

# 実行＆結果表示
print(f"初期資金: {cerebro.broker.getvalue():.2f}")
results = cerebro.run()
print(f"最終資金: {cerebro.broker.getvalue():.2f}")

#results = cerebro.run()
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

log_df = pd.DataFrame(strategy.trade_log)
if not log_df.empty:
    log_path = os.path.join("data", f"backtest_trades_{TICKER}_{START}_to_{END}.csv")
    log_df.to_csv(log_path, index=False)
    print(f"\n売買ログをCSV保存しました: {log_path}")
else:
    print("\n売買ログはありませんでした。")

# グラフ表示
import mplfinance as mpf

# 日付をインデックスに変換（mplfinance用に）
df.index = pd.to_datetime(df.index).normalize()
df.index.name = 'Date'

# 売買ポイント取得
buy_dates = [pd.Timestamp(log['date']).normalize() for log in strategy.trade_log if log['type'] == 'BUY']
sell_dates = [pd.Timestamp(log['date']).normalize() for log in strategy.trade_log if log['type'] == 'SELL']

# マーカー用のデータ（buy:↑, sell:↓）
# BUYマーカー
buy_markers = df['Close'].copy()
buy_markers[:] = float('nan')  # 全部NaNで初期化
buy_markers.loc[buy_dates] = df.loc[buy_dates, 'Close'].values

# SELLマーカー
sell_markers = df['Close'].copy()
sell_markers[:] = float('nan')
sell_markers.loc[sell_dates] = df.loc[sell_dates, 'Close'].values

apds = [
    mpf.make_addplot(buy_markers, type='scatter', markersize=100, marker='^', color='green'),
    mpf.make_addplot(sell_markers, type='scatter', markersize=100, marker='v', color='red'),
]

# チャート描画（保存のみ、表示しない）
plot_path = f"data/backtest_plot_mpl_{TICKER}.png"
mpf.plot(df, type='candle', style='charles', addplot=apds, volume=False, savefig=plot_path)
print(f"チャート画像を保存しました: {plot_path}")
