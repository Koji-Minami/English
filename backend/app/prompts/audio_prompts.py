from pathlib import Path
from loguru import logger

class AudioPrompt:
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
                self.template = f.read()
            
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
            return self.template
        except Exception as e:
            logger.error(f"Unexpected error formatting prompt: {e}")
            raise

class AudioImmediatePrompt:
    """
    即座レスポンス用プロンプトクラス
    書き起こしと返事のみに特化したプロンプトを管理します
    """
    def __init__(self):
        """
        初期化メソッド
        テンプレートファイルからプロンプトを読み込みます
        """
        try:
            # テンプレートファイルのパスを取得
            template_path = Path(__file__).parent / "templates" / "audio_immediate.txt"
            
            # テンプレートファイルを読み込み
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = f.read()
            
        except Exception as e:
            logger.error(f"Error loading immediate prompt template: {e}")
            raise

    def format(self, **kwargs) -> str:
        """
        プロンプトをフォーマットするメソッド
        
        Returns:
            str: フォーマットされたプロンプト
        """
        try:
            return self.template
        except Exception as e:
            logger.error(f"Unexpected error formatting immediate prompt: {e}")
            raise

class TranscriptAnalysisPrompt:
    """
    文法分析用プロンプトクラス
    書き起こしテキストの分析に特化したプロンプトを管理します
    """
    def __init__(self):
        """
        初期化メソッド
        テンプレートファイルからプロンプトを読み込みます
        """
        try:
            # テンプレートファイルのパスを取得
            template_path = Path(__file__).parent / "templates" / "transcript_analysis.txt"
            
            # テンプレートファイルを読み込み
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = f.read()
            
        except Exception as e:
            logger.error(f"Error loading analysis prompt template: {e}")
            raise

    def format(self, transcription: str, **kwargs) -> str:
        """
        プロンプトをフォーマットするメソッド
        
        Args:
            transcription (str): 分析対象の書き起こしテキスト
            
        Returns:
            str: フォーマットされたプロンプト
        """
        try:
            if not transcription:
                raise ValueError("transcription parameter is required")
            
            return self.template.format(transcription=transcription)
        except Exception as e:
            logger.error(f"Unexpected error formatting analysis prompt: {e}")
            raise


class AudioAnalysisPrompt:
    """
    即座レスポンス用プロンプトクラス
    書き起こしと返事のみに特化したプロンプトを管理します
    """
    def __init__(self):
        """
        初期化メソッド
        テンプレートファイルからプロンプトを読み込みます
        """
        try:
            # テンプレートファイルのパスを取得
            template_path = Path(__file__).parent / "templates" / "audio_analysis.txt"
            
            # テンプレートファイルを読み込み
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = f.read()
            
        except Exception as e:
            logger.error(f"Error loading immediate prompt template: {e}")
            raise

    def format(self, **kwargs) -> str:
        """
        プロンプトをフォーマットするメソッド
        
        Returns:
            str: フォーマットされたプロンプト
        """
        try:
            return self.template
        except Exception as e:
            logger.error(f"Unexpected error formatting immediate prompt: {e}")
            raise