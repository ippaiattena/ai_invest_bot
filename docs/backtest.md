# Backtest

バックテストは、戦略の有効性を過去データに基づいて評価するためのモジュールです。主に以下の処理を担当します。

---

## 構成

- **使用戦略**：`SmaRsiStrategy`（SMAクロス＋RSI閾値）
- **ライブラリ**：`backtrader`, `yfinance`, `mplfinance`
- **対象銘柄**：configurable（例：AAPL）
- **対象期間**：configurable（例：2023-01-01 〜 2024-01-01）

---

## 実行内容

1. `yfinance`でデータ取得（OHLC）
2. `backtrader`でバックテスト実行
   - 初期資金、ポジションサイズ、分析器（Sharpe, DrawDownなど）
3. トレードの履歴（BUY/SELL）を記録・CSV出力
4. 結果のチャート描画（`mplfinance`でマーカー付き）
5. `Slack`へ結果を通知（トレードサマリー＋チャート画像）

---

## 出力物

- `data/backtest_trades_*.csv`：売買ログ
- `data/backtest_plot_*.png`：チャート画像
- Slack通知（成功時のみ）

---

## 使用例

```bash
python backtest.py
```

---

## 備考
- mplfinance による描画は matplotlib.use('Agg') で非表示化し、自動保存に対応。
- notify() モジュールと連携してSlack送信可能。
- チャートとログ出力はGitHub Actionsでも機能確認済み。
