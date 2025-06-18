from broker_base import AbstractBroker
from modules.paper_broker import PaperBroker
# from modules.kabucom_broker import KabucomBroker  # 将来用

def create_broker(mode: str) -> AbstractBroker:
    if mode == "paper":
        return PaperBroker()
    elif mode == "dummy":
        return PaperBroker(mode="dummy")
    elif mode == "real":
        return PaperBroker(mode="real")  # 将来は KabucomBroker()
    else:
        raise ValueError(f"Unknown broker mode: {mode}")
