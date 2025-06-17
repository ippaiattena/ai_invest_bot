def exit_by_rsi(screening_df, rsi_threshold=70):
    """
    RSIが閾値を超えたら売却シグナルを返す
    Returns: dict[ticker] = True（売却推奨）
    """
    exit_signals = {}
    for _, row in screening_df.iterrows():
        ticker = row["Ticker"]
        rsi = row.get("RSI")
        if rsi is not None and rsi > rsi_threshold:
            exit_signals[ticker] = True
    return exit_signals
