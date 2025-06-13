import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

def run_screening(tickers, rsi_threshold=70):
    """
    スクリーニングを実行し、上昇トレンドかつ買われすぎでない銘柄を抽出する。

    Parameters:
    tickers (list): 銘柄のティッカーリスト
    rsi_threshold (int): RSIの閾値（デフォルトは70）

    Returns:
    pd.DataFrame: スクリーニング結果のデータフレーム
    """
    signals = []

    for ticker in tickers:
        df = yf.download(ticker, period='6mo', auto_adjust=False, progress=False)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()

        # RSIの計算（期間14日）
        rsi = RSIIndicator(close=df['Close'].squeeze(), window=14)
        df['RSI'] = rsi.rsi()

        df = df.dropna()  # SMAとRSIがそろってからにする

        if df.empty:
            print(f"{ticker}: データ不足でスキップ")
            continue

        latest = df.iloc[-1]
        sma20 = float(latest['SMA20'].iloc[0])
        sma50 = float(latest['SMA50'].iloc[0])
        rsi_val = float(latest['RSI'].iloc[0])
        close_price = float(latest['Close'].iloc[0])

        # 条件：上昇トレンド＋買われすぎでない
        if sma20 > sma50 and rsi_val < 70:
            signal = 'Buy'
        else:
            signal = 'Hold'

        signals.append({
            'Ticker': ticker,
            'Signal': signal,
            'Close': round(close_price, 2),
            'RSI': round(rsi_val, 1)
        })

    return pd.DataFrame(signals)
