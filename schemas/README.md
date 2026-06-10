# schemas/ — wire shape の SoT

JSON Schema 2020-12。wire 上の構造（field の有無・型・形式）の規範はここだけが持つ。
挙動・判定の規範は持たない（→ rules/）。

- ファイル名: `<topic>.json`（例: `pipeline-pass-credential.json`）
- 各 schema は対応する rule entry の `schemas` field から参照される
- schema の意図的な permissive / strict 箇所は、schema 内の `$comment` に記す

現状: 空。転記台帳は rules/ の `source` field（`status: todo` の entry）を参照。
