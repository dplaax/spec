# バージョニング

- 現在: **0.2.0-alpha.1（pre-release）**。0.1 タグの条件は充足済み、0.2 タグの条件は未充足。実装はこの repo の conformance vector を取り込むので、tag は切り直さない: 変更は新しい版に入れ、以下の互換性規律が適用される（2026-07-17 に v0.1.0 を公開するまでは、2026-06-12 の process type rename のように、draft の変更に合わせて 0.1 タグを切り直した）。
- **pre-release**: `0.N.0-alpha.K` は、0.N タグの条件を満たす前に切る、0.N に向かう release を表す。`0.N.0` そのものは条件を満たしてから切る。0.x では rule の削除・意味変更を minor で許すので、`0.N.0-alpha.K` と `0.N.0` の間でも rule は変わりうる。
- **0.1 タグの条件**: rules/ の全 entry が `draft` 以上 / wire-core family（`chain` `credential` `delegation` `process` `registry` `resolver` `transfer`）の全 rule に 1 本以上の vector — `tools/lint.py` が強制するカバレッジ床 / lint green（rule↔vector の双方向参照を含む）/ `source` field の全廃（転記完了）。
- **0.2 タグの条件**: 全 family の各 `draft` rule に 1 本以上の vector（v0.1.0 で 101/242、0.2.0-alpha.1 で 118/257）。埋まった family から lint のカバレッジ床へ昇格させる（`did` は 0.2.0-alpha.1 で床に入った。`keybinding` は全 rule に vector があるが、まだ床に入っていない）。
- **1.0 の条件**: 全機能の実装と実用検証期間を経て、破壊の余地を 0.x で消化しきってから。
- 互換性の単位は **rule の `id` と `statement` の意味**。ファイル配置は規範外（→ [README.ja.md](README.ja.md)）。
- rule の削除・意味変更は 0.x では minor で許容する。1.0 以降は major の唯一の正当理由となる。
- vector・schema の追加は常に minor 以下。既存 vector の期待値変更は rule の意味変更とみなす。
