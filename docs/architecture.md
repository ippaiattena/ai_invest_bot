# 📊 System Architecture

## プロジェクト概要

* 目的: AI を用いた株式スクリーニング、バックテスト、Slack通知、自動売買までを実現
* 構成:

  * `screening.py`: RSI を用いたスクリーニング
  * `backtest.py`: Backtrader によるバックテスト
  * `notifier.py`: Slack通知 & スプレッドシート記録
  * `main.py`: 一連の処理を組み合わせた入口

---

## データ流れ

1. **yfinance** で最新データ取得
2. `screening.py` でRSIに基づく技術分析
3. BUY/HOLD シグナルを Slack & Google Sheets に通知/記録
4. `backtest.py` で変数列を用いた戦略検討
5. 結果とチャートをSlackに通知
6. (未来)　Alpaca API などで実販売を行う

---

## 環境構成

* 実行環境:

  * ローカル: `.env` 管理
  * 本番: GitHub Actions + `secrets`

* 必要なSecrets:

  * `SLACK_WEBHOOK_URL`
  * `SLACK_BOT_TOKEN`
  * `GCP_CREDENTIALS_B64`

* 必要モジュール:

  * `slack_sdk`
  * `gspread`
  * `yfinance`
  * `backtrader`
  * `mplfinance`

---

## Slack通知構成

* Webhook: シグナル結果を文字で通知
* BotToken: チャート画像の送信 (v2 API)
* 通知内容:

  * 各株のシグナル(BUY/HOLD)
  * トレードサマリー結果
  * (未来)シグナル判断に基づく発注発火

---

## Google Sheets 連携

* `gspread` + サービスアカウント
* 行列記録: Ticker, Signal, Close, RSI, Date
* Sheet: `daily` タブに追記

---

## Backtest ロジック

* SMA短期/長期 + RSI による売買
* CSVログ保存
* Slackへのサマリ通知
* チャート画像保存 + 通知
* 扱う指標:

  * 給利率(CAGR)
  * 勝率 / 平均損益 / 平均保有日数

---

## 展望: 自動売買

* Alpaca API 連携 (従来の部分を抽象化)
* Botによる発注シグナルを検出
* Backtest の内容と一致した動作を再現
* 未来: 多株のポートフォリオ管理
