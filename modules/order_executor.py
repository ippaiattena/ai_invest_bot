from modules.config_loader import get_order_mode
from modules.local_wallet import LocalWallet

def place_order(ticker, price):
    mode = get_order_mode()

    if mode == "dummy":
        print(f"[DUMMY ORDER] {ticker} をダミー発注: {price}")

    elif mode == "local":
        wallet = LocalWallet.load()
        wallet.buy(ticker, price)
        wallet.save()
        print(f"[LOCAL ORDER] {ticker} をローカルペーパー発注: {price}")

    else:
        print(f"[ERROR] 未知の注文モード: {mode}")
