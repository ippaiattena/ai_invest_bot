# デプロイ・運用手順（GitHub Actions）

本プロジェクトは GitHub Actions により毎日定時で自動実行されます。

## 実行タイミング

- 毎日 08:00 JST に実行（UTC 23:00）
- 任意実行（手動トリガー）も可能

## 主な処理内容

1. リポジトリの checkout
2. Python のセットアップ（3.10）
3. 必要ライブラリのインストール
4. GCP 認証ファイルの生成（Secrets から）
5. `main.py` 実行
   - スクリーン結果の Slack 通知
   - スプレッドシートへの保存
   - バックテストチャート送信

## Secrets 設定

以下の環境変数を GitHub Secrets に設定してください。

| Secret名             | 説明                                 |
|----------------------|--------------------------------------|
| `SLACK_WEBHOOK_URL`  | SlackのWebhook URL（テキスト通知用）|
| `SLACK_BOT_TOKEN`    | files.upload_v2 用のBotトークン     |
| `GCP_CREDENTIALS_B64`| credentials.json をbase64化した文字列|
