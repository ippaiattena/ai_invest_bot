
from abc import ABC
from modules.broker_base import BrokerBase

class ApiBrokerBase(BrokerBase, ABC):
    """
    APIベースのBroker共通クラス。
    Alpaca, BlueO などのAPI系ブローカーはこれを継承する。
    """
    def __init__(self, mode="virtual"):
        self.mode = mode
