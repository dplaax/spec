# バージョニング

- 現在: **0.1（draft タグ）**。0.1 タグの条件は充足済み。consumer が存在しない間、0.1 タグは milestone marker であり、語彙レベルの変更は同タグの切り直しで取り込む（2026-06-12 の process type rename で適用）。以下の互換性規律の本格適用は最初の consumed release から。
- **0.1 タグの条件**: rules/ の全 entry が `draft` 以上 / wire-core family（`chain` `credential` `delegation` `process` `registry` `resolver` `transfer`）の全 rule に 1 本以上の vector — `tools/lint.py` が強制するカバレッジ床 / lint green（rule↔vector の双方向参照を含む）/ `source` field の全廃（転記完了）。
- **0.2 タグの条件**: 全 family の各 `draft` rule に 1 本以上の vector（0.1 時点で 98/242）。埋まった family から lint のカバレッジ床へ昇格させる。
- **1.0 の条件**: 全機能の実装と実用検証期間を経て、破壊の余地を 0.x で消化しきってから。
- 互換性の単位は **rule の `id` と `statement` の意味**。ファイル配置は規範外（→ [README.ja.md](README.ja.md)）。
- rule の削除・意味変更は 0.x では minor で許容する。1.0 以降は major の唯一の正当理由となる。
- vector・schema の追加は常に minor 以下。既存 vector の期待値変更は rule の意味変更とみなす。
