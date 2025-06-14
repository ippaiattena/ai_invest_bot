# Notifier

Slack通知やログ保存、Googleスプレッドシート出力など、実行結果の可視化・記録を担うモジュールです。

---

## 構成

- **Slack通知**：
  - Webhookによるテキスト通知
  - Bot Token + `files_upload_v2()` による画像送信（チャート）
- **CSV保存**：
  - スクリーニング結果のローカル保存（`data/`ディレクトリ）
- **Googleスプレッドシート書き出し**：
  - `credentials.json` による認証
  - `gspread`ライブラリと`set_with_dataframe()`による追記処理

---

## 機能詳細

### 1. `notify(df: pd.DataFrame)`

- スクリーニング結果（DataFrame）をSlackに送信
- 売買ログ（存在すれば）を読み込み、トレードサマリーを追加
- チャート画像が存在すれば、Slackへアップロード
- CSV保存・スプレッドシート保存もこの関数内で実行される

### 2. `save_to_csv(df: pd.DataFrame)`

- 日付ベースのファイル名でCSVを保存（`data/screening_log_YYYY-MM-DD.csv`）

### 3. `save_to_sheet(df: pd.DataFrame)`

- `credentials.json`を用いたサービスアカウント認証
- 指定シート（例：`daily`）にデータを追記
- ヘッダーの重複を避け、既存行の下に新規行を挿入

### 4. `send_chart_to_slack(filepath: str)`

- `slack_sdk.WebClient` を用いてチャート画像を送信
- チャンネルは環境変数 or 固定IDで指定（`channels=[...]`）

---

## 環境変数

- `SLACK_WEBHOOK_URL`: 通知用Webhook URL（簡易テキスト通知）
- `SLACK_BOT_TOKEN`: Bot Token（画像付き通知に必要）
- `GCP_CREDENTIALS_B64`: base64エンコードされたGoogle認証情報（GitHub Actions用）

---

## 使用例

```bash
python main.py
```

Slackにスクリーニング結果とチャートが通知され、結果がCSVとスプレッドシートに保存される。

---

## 備考

- チャート画像は backtest_plot_mpl_AAPL.png 固定で保存される想定（今後動的に変更も可）
- GitHub Actions対応済み（環境変数と.envの両対応）
- トレードログの読み込みファイル名は今後動的に変数化する予定
