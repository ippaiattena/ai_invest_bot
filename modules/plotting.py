import pandas as pd
import mplfinance as mpf
import os

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
