# utils.py モジュール概要

`utils.py` は、他モジュールから共通的に呼び出される補助的関数群を定義しています。主にファイル操作、チャート描画、日付処理などのユーティリティ機能を提供します。

## 主な関数

### `plot_trade_chart(trade_log_path: str, price_df: pd.DataFrame, save_path: str)`

- 説明：売買ログと価格データからチャートを描画し、ファイルとして保存します。
- 引数：
  - `trade_log_path`: 売買ログのCSVファイルパス
  - `price_df`: 株価のDataFrame（`Date` をインデックスとする）
  - `save_path`: 出力ファイルのパス
- 備考：mplfinanceを用いてcandlestickチャート上にBUY/SELLマーカーを追加描画します。

### 今後の追加予定
- ファイルパスの標準化
- ログ保存ヘルパー
