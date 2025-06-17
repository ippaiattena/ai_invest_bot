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

def exit_by_dummy(screening_df, rsi_threshold=70):
    """
    すべて売却（テスト用）
    """
    return {row["Ticker"]: True for _, row in screening_df.iterrows()}

# ルール名に対応する関数辞書
EXIT_RULES = {
    "rsi": exit_by_rsi,
    "dummy_all": exit_by_dummy,
    # 今後: "holding_period": exit_by_holding_days, 等追加可能
}
