from abc import ABC, abstractmethod
import pandas as pd
from typing import Callable, Optional

class BrokerBase(ABC):
    """
    ブローカー共通インターフェイス。
    local / api 問わず、このクラスに準拠する。
    """

    @abstractmethod
    def buy(self, ticker: str, price: float, size: int = 1):
        pass

    @abstractmethod
    def sell(self, ticker: str, price: float, size: int = 1):
        pass

    @abstractmethod
    def get_positions(self) -> dict:
        """現在のポジションを返す（ticker → dict）"""
        pass

    @abstractmethod
    def process_signals(self, df: pd.DataFrame):
        """スクリーニング結果を元に発注処理"""
        pass

    @abstractmethod
    def apply_exit_strategy(self, screening_df: pd.DataFrame, rule_func: Optional[Callable[[pd.DataFrame], dict[str, bool]]] = None):
        """Exitルールを適用して売却シグナル処理"""
        pass

    @abstractmethod
    def get_portfolio_summary(self) -> dict:
        """保有資産のサマリー（現金・株式・合計など）"""
        pass

    @abstractmethod
    def format_portfolio_summary(self) -> str:
        """Slack通知などに使える文字列形式のサマリー"""
        pass
