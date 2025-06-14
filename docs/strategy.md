# strategy.md

## 概要

このモジュールは `backtrader` を用いた自作戦略クラス `SmaRsiStrategy` を定義しています。
短期/長期SMA の交差と RSI 値の合同をもとに、BUY/その後の RSI 上昇による SELL を行います。収支は記録され、CSVやSlack通知で出力されます。

---

## ファイル

* `strategies/sma_rsi_strategy.py`

---

## クラス: `SmaRsiStrategy`

### パラメータ

```python
params = (
    ("sma_period_short", 20),
    ("sma_period_long", 50),
    ("rsi_period", 14),
    ("rsi_upper", 70),
)
```

* **sma\_period\_short / sma\_period\_long** : SMA の期間
* **rsi\_period** : RSI の計算期間
* **rsi\_upper** : SELL の切り替えトリガー

### `__init__()`

* SMA インディケータを生成
* RSI を計算
* 売買ログ用 list `trade_log` を用意
* BUY 直前の日付/価格を記録

### `next()`

* ポジション無し：

  * 短期SMA > 長期SMA 且 RSI < RSIトリガー なら BUY
* ポジションあり：

  * RSI > RSIトリガー なら SELL

### `notify_order(order)`

* BUY/SELL 完了時に動作
* 価格や日付を記録
* SELL 時は利益/profit や保有期間も給助

---

## ログ出力例

```
2023-07-06, BUY, 187.95
2023-07-20, SELL, 193.15
```

CSV 出力：

```csv
date,type,price,entry_date,entry_price,profit,holding_days
2023-07-06,BUY,187.95,,,,
2023-07-20,SELL,193.15,2023-07-06,187.95,5.20,14.0
```

---

## 今後の拡張例

* RSI下限も指定して「保有するべき状況」の検証
* SMAよりMACDへ切替
* 投資量やポートフォリオによるリスクコントロール
