def place_order(ticker, price, signal, mode="dummy"):
    if signal != "Buy":
        return

    if mode == "dummy":
        print(f"[DUMMY ORDER] {ticker} を仮想発注: {price}")
    elif mode == "paper":
        print(f"[PAPER ORDER] {ticker} をペーパー発注: {price}（未実装）")
        # ここに証券会社のペーパーAPI呼び出し処理を記述（後で実装）
    elif mode == "real":
        print(f"[REAL ORDER] {ticker} を本番発注: {price}（未実装・注意）")
        # 実際のお金を動かすAPI呼び出し（慎重に実装）
    else:
        print(f"[UNKNOWN ORDER MODE] モード: {mode}")
