from .base import BasePrompt
from pathlib import Path
from loguru import logger

class AudioPrompt(BasePrompt):
    """
    音声用プロンプトクラス
    音声データの分析に特化したプロンプトを管理します
    """
    def __init__(self):
        """
        初期化メソッド
        テンプレートファイルからプロンプトを読み込みます
        """
        try:
            # テンプレートファイルのパスを取得
            template_path = Path(__file__).parent / "templates" / "audio.txt"
            
            # テンプレートファイルを読み込み
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            # 親クラスの初期化
            super().__init__(template)
            
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            raise

    def format(self, **kwargs) -> str:
        """
        プロンプトをフォーマットするメソッド
        
        Returns:
            str: フォーマットされたプロンプト
        """
        try:
            # テンプレートをそのまま返す（フォーマット不要）
            return self.template
        except Exception as e:
            logger.error(f"Unexpected error formatting prompt: {e}")
            raise