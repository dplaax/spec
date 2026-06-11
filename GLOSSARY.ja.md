# Glossary

non-normative。用語は表の 1 行で定義し、説明文を書き足さない。

| 用語 | 定義 |
| --- | --- |
| dPLaaX / dplaax | プロトコル名（表記）/ wire 名前空間（`dplaax.*.v1`、`did:dplaax` 等の prefix） |
| 広義のデータパイプライン | データが境界を越えて受け渡される現象全般。設計されたパイプライン製品に限らない |
| プロセス境界 | データの受け渡しが発生し、記録の発行単位となる境界 |
| wire profile | 実装が宣言する選択の束（アルゴリズム・表現形式等）。dPLaaX が共通化するのは構造と判定であり、選択そのものではない |
| conformance class | rule の適用範囲を区切る単位。rule entry の `class` field で表現される |
| チェーン起点 | previousCredential を持たず、新しいチェーンを開始するクレデンシャル |
| process type | pipeline process の振る舞いの分類（Chained Process / Source Process / Sink Process / Custom Process）。判別は wire 上の署名挙動による: Source Process は chain を起こし（chain origin）、Chained Process は繋ぎ（previousCredential を運ぶ）、Sink Process は終える（検証する。デフォルトでは in-network に何も発行しない — wire profile は delivery receipt の発行を許可してよい、process.sink.receipt 参照）。全参加者は Process DID を持つ — catalog が分類するのは process。（旧称 component type: FilterConvert / Origin Source / External Sink / Custom — 0.x の間併記、GA で除去） |
| audit-reachable | 集約境界をまたぐ監査到達性を提供する optional な conformance class（→ rules/commitment.yaml） |
| trust layering（L1/L2/L3） | L1 = per-credential 自己整合（3 確信度軸、→ rules/confidence.yaml）、L2 = 監査到達性（source commitment による消費ソース集合への遡及、audit-reachable class）、L3 = 意味的監査（申告ソースから出力が正しく導出されたかの判定）。protocol が保証するのは L1+L2 まで — L3 は protocol の決定範囲外（adapter / 監査基盤の関心事） |
