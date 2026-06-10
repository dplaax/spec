# バージョニング

- 現在: **pre-0.1**。すべて不安定であり、予告なく変わる。
- **0.1 タグの条件**: rules/ の全 entry が `draft` 以上 / 各 `draft` rule に 1 本以上の vector / lint green / `source` field の全廃（転記完了）。
- **1.0 の条件**: 全機能の実装と実用検証期間を経て、破壊の余地を 0.x で消化しきってから。
- 互換性の単位は **rule の `id` と `statement` の意味**。ファイル配置は規範外（→ [README.md](README.md)）。
- rule の削除・意味変更は 0.x では minor で許容する。1.0 以降は major の唯一の正当理由となる。
- vector・schema の追加は常に minor 以下。既存 vector の期待値変更は rule の意味変更とみなす。
