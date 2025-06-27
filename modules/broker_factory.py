from modules.local_broker import LocalBroker
from modules.kabucom_broker import KabucomBroker
from modules.broker_base import BrokerBase

def create_broker(mode: str, reset_wallet: bool = False) -> BrokerBase:
    """
    モードに応じて対応するBrokerインスタンスを返す。

    :param mode: 発注モード (dummy / local / kabucom / real)
    :return: AbstractBroker を継承したインスタンス
    """
    mode = mode.lower()

    if mode == "dummy":
        return LocalBroker(mode=mode)
    if mode == "local":
        return LocalBroker(mode=mode, reset_wallet=reset_wallet)
    elif mode == "kabucom":
        return KabucomBroker()
    elif mode == "real":
        # 将来の拡張。現時点では未対応
        raise NotImplementedError("Real取引モードは未実装です。")
    else:
        raise ValueError(f"未対応のモードが指定されました: {mode}")
