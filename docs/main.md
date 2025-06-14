# main.md

## 概要

`main.py` は、システム全体の処理を統括するエントリーポイントです。
主に以下のような処理を実行します:

* `config.yaml`から構成の読み込み
* スクリーニング処理の実行
* バックテストの実行
* Slack 通知 (message + chart)
* Google Sheets への登録
* ローカルとGitHub Actionsの両方対応

---

## 構成の読み込み

```python
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

tickers = config["tickers"]
rsi_threshold = config.get("rsi_threshold", 70)
```

* テスト対象のティッカーや RSI の阈値を config で設定可能

---

## モジュール実行

```python
results = screening.run_screening(tickers, rsi_threshold)
notifier.notify(results)
backtest.run_backtest()
```

* `screening.run_screening()`でBuy/Holdを判定
* `notifier.notify()`でSlack通知 + CSV/Sheets登録
* `backtest.run_backtest()`は売買ログ・チャート生成

---

## Slack通知テスト

```python
from slack_notifier import send_slack_message
send_slack_message("✅ Slack通知テスト: Botは正常に動いています。")
```

* 後半の繰り返しのような作用。
* 現状は実行性確認用のダミーメッセージ

---

## 環境変数と実行管理

```python
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
```

* `.env`を読み込み、SLACKなどの秘密情報を登録
* GitHub Actions とローカルの両方で同じコードを使用可

---

## 依存関係

* `screening.py`: メインのロジック
* `notifier.py`: Slack / CSV / Sheets 通知
* `backtest.py`: 売買ログ + チャート
* `slack_notifier.py`: 単純テスト通知
* `config.yaml`: 設定ファイル

---

## 他

* 少ない行数に凝縮されているが、機能分離が明確で操作性高い
* 今後の拡張性も確保された構成
* ロジックブロック化なども容易

---

## 今後の拡張案

* CLIパラメータ化 (`argparse`)
* エラーのログ出力
* `--test` モードで「Slack に通知しない」
* 資産を YAML 以外のフォーマット (CSV/DB/API) で読み込む
