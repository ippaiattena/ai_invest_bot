from modules.paper_broker import PaperBroker
from modules.kabucom_broker import KabucomBroker
from modules.broker_base import AbstractBroker

def get_broker(mode: str) -> AbstractBroker:
    """
    モードに応じて対応するBrokerインスタンスを返す。

    :param mode: 発注モード (dummy / paper / kabucom / real)
    :return: AbstractBroker を継承したインスタンス
    """
    mode = mode.lower()

    if mode in ["dummy", "paper"]:
        return PaperBroker(mode=mode)
    elif mode == "kabucom":
        return KabucomBroker()
    elif mode == "real":
        # 将来の拡張。現時点では未対応
        raise NotImplementedError("Real取引モードは未実装です。")
    else:
        raise ValueError(f"未対応のモードが指定されました: {mode}")
