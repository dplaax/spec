# Glossary

non-normative。用語は表の 1 行で定義し、説明文を書き足さない。

| 用語 | 定義 |
|---|---|
| dPLaaX / dplaax | プロトコル名（表記）/ wire 名前空間（`dplaax.*.v1`、`did:dplaax` 等の prefix） |
| 広義のデータパイプライン | データが境界を越えて受け渡される現象全般。設計されたパイプライン製品に限らない |
| プロセス境界 | データの受け渡しが発生し、記録の発行単位となる境界 |
| wire profile | 実装が宣言する選択の束（アルゴリズム・表現形式等）。dPLaaX が共通化するのは構造と判定であり、選択そのものではない |
| conformance class | rule の適用範囲を区切る単位。rule entry の `class` field で表現される |
| audit-reachable | 集約境界をまたぐ監査到達性を提供する optional な conformance class（→ rules/origin.yaml） |
