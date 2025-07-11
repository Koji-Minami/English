# English Learning Backend

## 概要
英語学習アプリケーションのバックエンドAPI。音声認識、AI対話、音声合成機能を提供するFastAPIサービス。

## 技術スタック
- **Framework**: FastAPI
- **AI/ML**: Google Gemini API, Google Cloud Speech-to-Text, Google Cloud Text-to-Speech
- **Language**: Python 3.9+
- **Package Manager**: uv
- **Testing**: pytest

## プロジェクト構造
```
backend/
├── app/
│   ├── api/              # APIエンドポイント
│   ├── config/           # 設定管理
│   ├── services/         # ビジネスロジック
│   ├── prompts/          # AIプロンプト
│   └── main.py          # アプリケーションエントリーポイント
├── tests/               # テストコード
└── logs/                # ログファイル
```

## 主要機能

### APIエンドポイント
- `POST /api/v1/transcribe` - 基本的な音声認識
- `GET /api/v1/gemini_audio` - セッション作成
- `POST /api/v1/gemini_audio/{session_id}` - AI対話付き音声処理
- `POST /api/v1/finish_session/{session_id}` - セッション終了

### サービス層
- **SpeechService**: 音声認識（Google Cloud Speech-to-Text）
- **GeminiAudioService**: AI音声処理（Gemini API）
- **TextToSpeechService**: 音声合成（Google Cloud TTS）
- **SessionManagerService**: セッション・会話履歴管理

## セットアップ

### 1. 環境準備
```bash
# 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -e .
```

### 2. 環境変数設定
`.env`ファイルを作成：
```env
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google_credentials.json
```

### 3. アプリケーション起動
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 使用方法

### 基本的な音声処理フロー
1. セッション作成: `GET /api/v1/gemini_audio`
2. 音声アップロード: `POST /api/v1/gemini_audio/{session_id}`
3. セッション終了: `POST /api/v1/finish_session/{session_id}`

### レスポンス形式
```json
{
  "gemini_response": [
    {
      "transcription": "音声の書き起こし",
      "response": "AIの英語返答",
      "speechflaws": "発音・文法の指摘",
      "nuanceinquiry": ["理解しづらい点の推測"],
      "alternativeexpressions": [["代替表現", "ニュアンス"]]
    }
  ],
  "audio_content": "base64エンコードされた音声データ"
}
```

## テスト
```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app --cov-report=html

# 特定テスト実行
pytest tests/api/test_transcription.py
```

## 開発ガイドライン

### コード規約
- 型ヒントの使用
- docstringの記述
- loguruによるログ出力
- 単一責任の原則

### エラーハンドリング
- 適切なHTTPステータスコード
- 詳細なエラーメッセージ
- ログ記録

### セキュリティ
- 環境変数による機密情報管理
- CORS設定
- 入力バリデーション

## ログ
- 出力先: `logs/app.log`
- レベル: INFO以上
- 形式: 構造化ログ

## トラブルシューティング

### よくある問題
1. **APIキーエラー**: 環境変数の設定確認
2. **音声処理エラー**: ファイル形式・サイズ確認
3. **セッションエラー**: セッションIDの有効性確認

### デバッグ方法
1. ログファイルの確認
2. テストの実行
3. APIレスポンスの詳細確認

## 今後の改善点
- [ ] 音声品質向上
- [ ] 多言語対応
- [ ] リアルタイム処理
- [ ] ユーザー認証
- [ ] パフォーマンス最適化 