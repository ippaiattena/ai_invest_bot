import yfinance as yf
import pandas as pd

tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']
signals = []

for ticker in tickers:
    df = yf.download(ticker, period='6mo', auto_adjust=False, progress=False)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df = df.dropna()

    if df.empty:
        print(f"{ticker}: データ不足でスキップ")
        continue

    latest = df.iloc[-1]

    sma20 = latest['SMA20'].item() if hasattr(latest['SMA20'], 'item') else float(latest['SMA20'])
    sma50 = latest['SMA50'].item() if hasattr(latest['SMA50'], 'item') else float(latest['SMA50'])
    close_price = latest['Close'].item() if hasattr(latest['Close'], 'item') else float(latest['Close'])

    signal = 'Buy' if sma20 > sma50 else 'Hold'
    signals.append({
        'Ticker': ticker,
        'Signal': signal,
        'Close': round(close_price, 2)
    })

df_signals = pd.DataFrame(signals)
print(df_signals)
