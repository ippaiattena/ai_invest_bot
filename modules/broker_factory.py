from modules.local_broker import LocalBroker
from modules.kabucom_broker import KabucomBroker
from modules.broker_base import BrokerBase
from modules.alpaca_broker import AlpacaBroker

def create_broker(mode: str, reset_wallet: bool = False) -> BrokerBase:
    """
    モードに応じて対応するBrokerインスタンスを返す。

    :param mode: 発注モード (dummy / local / alpaca_virtual / alpaca_real / kabucom)
    :return: AbstractBroker を継承したインスタンス
    """
    mode = mode.lower()

    if mode == "dummy":
        return LocalBroker(mode=mode)
    if mode == "local":
        return LocalBroker(mode=mode, reset_wallet=reset_wallet)
    elif mode == "kabucom":
        return KabucomBroker()
    elif mode == "alpaca_virtual":
        return AlpacaBroker(mode="virtual")
    elif mode == "alpaca_real":
        return AlpacaBroker(mode="real")
    else:
        raise ValueError(f"未対応のモードが指定されました: {mode}")
