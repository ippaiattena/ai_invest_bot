import matplotlib
matplotlib.use('Agg')  # 表示せずに保存だけする

import matplotlib.pyplot as plt
import yfinance as yf
import backtrader as bt
import os
import pandas as pd
import mplfinance as mpf
from ai_invest_bot.strategies.sma_rsi_strategy import SmaRsiStrategy
from ai_invest_bot.modules.plotting import plot_trade_chart
# 今後追加される戦略クラスもここにインポートする
# 例: from strategies.ema_crossover_strategy import EmaCrossoverStrategy

# 戦略名とクラスのマッピング
strategy_map = {
    "sma_rsi": SmaRsiStrategy,
    # "ema_crossover": EmaCrossoverStrategy,
}

def run_backtest(ticker='AAPL', start='2023-01-01', end='2024-01-01', initial_cash=100000, strategy_name='sma_rsi'):

    # データ取得
    df = yf.download(ticker, start=start, end=end)
    df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)

    # backtrader用に変換
    data = bt.feeds.PandasData(dataname=df)

    # Cerebro（脳）セットアップ
    cerebro = bt.Cerebro()
    strategy_class = strategy_map.get(strategy_name)
    if strategy_class is None:
        raise ValueError(f"指定された戦略 '{strategy_name}' は存在しません")
    cerebro.addstrategy(strategy_class)
    cerebro.adddata(data)
    cerebro.broker.set_cash(initial_cash)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # バックテスト評価指標の追加
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    equity_curve = []

    # 実行＆結果表示
    print(f"初期資金: {cerebro.broker.getvalue():.2f}")
    #results = cerebro.run()
    # 日ごとの資産推移を記録するため、Observerを使う（または自前で記録）
    class EquityRecorder(bt.Strategy):
        def __init__(self):
            self.values = []

        def next(self):
            self.values.append((self.datas[0].datetime.date(0).isoformat(), self.broker.getvalue()))

    # strategy_classを使う代わりに一時的にラップ
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)
    cerebro.addstrategy(EquityRecorder)
    cerebro.adddata(data)
    cerebro.broker.set_cash(initial_cash)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    results = cerebro.run()
    strategy = results[0]  # 通常戦略
    recorder = results[1]  # EquityRecorder
    print(f"最終資金: {cerebro.broker.getvalue():.2f}")
    equity_curve = [{"date": d, "value": v} for d, v in recorder.values]

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

    os.makedirs("data", exist_ok=True)

    log_df = pd.DataFrame(strategy.trade_log)
    if not log_df.empty:
        log_path = os.path.join("data", f"backtest_trades_{ticker}_{start}_to_{end}.csv")
        log_df.to_csv(log_path, index=False)
        print(f"\n売買ログをCSV保存しました: {log_path}")
    else:
        print("\n売買ログはありませんでした。")

    metrics = {}
    if not log_df.empty and 'profit' in log_df.columns:
        # SELLのデータのみ分析対象
        sell_df = log_df[log_df['type'] == 'SELL'].copy()

        total_trades = len(sell_df)
        avg_profit = sell_df['profit'].mean()
        win_rate = (sell_df['profit'] > 0).mean() * 100  # 勝率（%）
        avg_hold_days = sell_df['holding_days'].mean()

        metrics = {
            "total_trades": total_trades,
            "avg_profit": avg_profit,
            "win_rate": win_rate,
            "avg_hold_days": avg_hold_days,
            "cagr": strategy.analyzers.returns.get_analysis()['rnorm'],
            "total_return": strategy.analyzers.returns.get_analysis()['rtot'],
            "sharpe": sharpe,
            "max_drawdown": strategy.analyzers.drawdown.get_analysis()['max']['drawdown']
        }

        print("\n=== トレードサマリー ===")
        print(f"総トレード回数      : {total_trades}")
        print(f"平均損益             : {avg_profit:.2f}")
        print(f"勝率                 : {win_rate:.2f}%")
        print(f"平均保有期間（日）   : {avg_hold_days:.2f}")
    else:
        print("\nトレードサマリーを出力できるデータがありませんでした。")

    # グラフ表示

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
    plot_path = f"data/backtest_plot_mpl_{ticker}.png"
    plot_trade_chart(df, strategy.trade_log, ticker, plot_path)

    return strategy, log_df, metrics, equity_curve

def run_backtest_multiple(tickers, start, end, initial_cash=100000, strategy_name='sma_rsi'):
    results = []
    for ticker in tickers:
        print(f"\n=== {ticker} のバックテスト開始 ===")
        strategy, log_df, metrics, equity_curve = run_backtest(
            ticker=ticker,
            start=start,
            end=end,
            initial_cash=initial_cash,
            strategy_name=strategy_name
        )
        if log_df is not None and not log_df.empty:
            result = {
                "ticker": ticker,
                "log": log_df,
                "chart": f"data/backtest_plot_mpl_{ticker}.png",
                "metrics": metrics,
                "equity_curve": equity_curve,
            }
            results.append(result)
        else:
            print(f"{ticker}: データなし or トレードなし")
    return results
