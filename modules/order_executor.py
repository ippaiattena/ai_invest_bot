from modules.config_loader import get_order_mode
from modules.local_wallet import PaperWallet

def place_order(ticker, price):
    mode = get_order_mode()

    if mode == "dummy":
        print(f"[DUMMY ORDER] {ticker} を仮想発注: {price}")

    elif mode == "local":
        wallet = PaperWallet.load()
        wallet.buy(ticker, price)
        wallet.save()
        print(f"[PAPER ORDER] {ticker} をペーパー発注: {price}")

    elif mode == "real":
        print(f"[REAL ORDER] {ticker} にリアル発注（未実装）")

    else:
        print(f"[ERROR] 未知の注文モード: {mode}")
