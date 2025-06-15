from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePrompt(ABC):
    """
    プロンプトの基底クラス
    すべてのプロンプトクラスはこのクラスを継承します
    """
    def __init__(self, template: str):
        """
        初期化メソッド
        Args:
            template (str): プロンプトのテンプレート文字列
        """
        self.template = template

    @abstractmethod
    def format(self, **kwargs) -> str:
        """
        プロンプトをフォーマットする抽象メソッド
        継承先のクラスで必ず実装する必要があります
        
        Args:
            **kwargs: フォーマットに使用するキーワード引数
            
        Returns:
            str: フォーマットされたプロンプト文字列
        """
        pass 