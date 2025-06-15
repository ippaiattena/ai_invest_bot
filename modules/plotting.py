import pandas as pd
import mplfinance as mpf
import os
import matplotlib.pyplot as plt

def plot_trade_chart(df, trade_log, ticker, save_path):
    df = df.copy()
    df.index = pd.to_datetime(df.index).normalize()
    df.index.name = 'Date'

    buy_dates = [pd.Timestamp(log['date']).normalize() for log in trade_log if log['type'] == 'BUY']
    sell_dates = [pd.Timestamp(log['date']).normalize() for log in trade_log if log['type'] == 'SELL']

    # マーカー初期化
    buy_markers = df['Close'].copy()
    buy_markers[:] = float('nan')
    buy_markers.loc[buy_dates] = df.loc[buy_dates, 'Close'].values

    sell_markers = df['Close'].copy()
    sell_markers[:] = float('nan')
    sell_markers.loc[sell_dates] = df.loc[sell_dates, 'Close'].values

    apds = [
        mpf.make_addplot(buy_markers, type='scatter', markersize=100, marker='^', color='green'),
        mpf.make_addplot(sell_markers, type='scatter', markersize=100, marker='v', color='red'),
    ]

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    mpf.plot(df, type='candle', style='charles', addplot=apds, volume=False, savefig=save_path)
    print(f"チャート画像を保存しました: {save_path}")

def plot_metric_trend(df, metric_name, save_path):
    df["Date"] = pd.to_datetime(df["Date"])
    pivot = df.pivot_table(index="Date", columns="Ticker", values=metric_name)

    plt.figure(figsize=(10, 6))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], label=col)
    plt.title(f"{metric_name} 推移")
    plt.xlabel("Date")
    plt.ylabel(metric_name)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"📊 {metric_name} チャート保存: {save_path}")
