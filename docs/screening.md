# Screening

銘柄スクリーニングは、複数の対象銘柄に対して戦略を適用し、投資判断（Buy/Hold/Sell）を判定する機能です。

---

## 構成

- **対象銘柄**：`config.yaml` に記載されたリスト（例：AAPL, MSFT, GOOG, etc）
- **戦略ロジック**：シンプルなRSIベース
  - RSIが閾値未満：Buy
  - RSIが閾値超過：Sell（通知上は Hold 扱い）
- **使用ライブラリ**：`yfinance`, `pandas`, `ta`

---

## 実行内容

1. `yfinance`で複数銘柄のデータ取得（最新30日程度）
2. 各銘柄に対してRSIを算出（デフォルト14日）
3. 閾値（デフォルト70）と比較し、Buy or Hold 判定
4. 結果をDataFrameにまとめて返す

---

## 出力形式

- `pandas.DataFrame`：
  - `Ticker`: 銘柄コード
  - `RSI`: 現在のRSI値（小数点1桁）
  - `Signal`: Buy または Hold
  - `Close`: 現在の終値

---

## 使用例

```bash
python main.py
```

---

## 備考

- RSI計算には ta.momentum.RSIIndicator を使用
- 戦略条件を追加・変更する場合は modules/screening.py を編集
- バックテストとは独立しており、実運用向けのスクリーニング機能を想定
