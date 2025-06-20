# app/services/README.md

# サービス層の構成

## 概要
このディレクトリには、アプリケーションの主要なビジネスロジックを実装するサービスクラスが含まれています。
各サービスは単一責任の原則に従い、特定の機能領域を担当します。

## サービス一覧

### 1. SessionManagerService
**目的**: ユーザーセッションの管理と会話履歴の保持
**主要機能**:
- セッションの作成と管理
- 会話履歴の保存と取得
- シングルトンパターンによる状態管理

### 2. GeminiAudioService
**目的**: Google Gemini APIを使用した音声処理とテキスト生成
**主要機能**:
- 音声ファイルの処理
- Gemini APIとの通信
- 会話履歴を考慮した応答生成

### 3. SpeechService
**目的**: テキストから音声への変換
**主要機能**:
- テキストの音声合成
- 音声ファイルの生成と管理
- 音声品質の最適化

### 4. IceBreakerService
**目的**: 会話の開始を促進するための質問生成
**主要機能**:
- 状況に応じた質問の生成
- 会話の流れの自然な開始
- ユーザーエンゲージメントの向上

## 設計原則
1. **単一責任の原則**: 各サービスは特定の機能領域に特化
2. **依存性注入**: サービス間の疎結合を実現
3. **エラーハンドリング**: 各サービスで適切なエラー処理を実装
4. **ロギング**: 詳細なログ記録による動作追跡
5. **テスト容易性**: 単体テストが可能な設計

## 使用例
```python
# セッション管理の例
session_manager = SessionManagerServiceFactory.create()
session_id = session_manager.create_session()

# 音声処理の例
audio_service = GeminiAudioService()
response = await audio_service.generate_text(audio_content, session_id)

# 音声合成の例
speech_service = SpeechService()
audio_file = await speech_service.text_to_speech(text)
```

## 注意事項
1. サービス間の依存関係を最小限に保つ
2. 適切なエラーハンドリングを実装する
3. パフォーマンスを考慮した実装を行う
4. セキュリティを考慮した実装を行う

## 今後の拡張
1. 新しい音声処理機能の追加
2. 会話履歴の永続化
3. パフォーマンス最適化
4. エラーハンドリングの強化