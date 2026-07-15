# vectors/ — 挙動規範の SoT 実体化

conformance vector。rule の挙動・判定は、最終的にここにある入力と期待結果の組が定義する。

- ファイル名: `<vector-id>.json`（例: `chain-001.json`）
- 形式:

```json
{
  "id": "chain-001",
  "rule": "chain.trigger.retention",
  "description": "conformant な前イベントが 1 件 → chain 保持",
  "input": {},
  "expect": "accept"
}
```

- `rule`: 対応する rule id（lint が解決を検証する）。rule 側の `vectors` field にも
  vector id を列挙する（双方向）
- `expect`: `"accept"` / `"reject"` / 期待出力 object（構築系 rule の場合）
- 実装のテストを seed にしてよいが、実装の癖を encode せず spec 起点で書き直す
- 期待値の数値・hash は spec 起点で導出し、実装（provin.oss）で実検証してから記載する

## input / expect の形状規約（family 別）

vector ファイル自体が JSON のため、バイト精度が要る入力（重複キー・無効 UTF-8・
余剰データ等）は parse 済みオブジェクトでは表現できない。family ごとに固定する:

| family | input | expect |
|---|---|---|
| `canon.*` | `{"document": <JSON テキストの文字列>}`。無効 UTF-8 等、JSON 文字列で表現不能なバイト列のみ `{"document_b64": <base64>}` | `"reject"` または `{"canonical": <文字列>}` — 比較は decode 後の文字列の UTF-8 バイト列同士 |
| `credential.*` | `{"credential": <wire 形式 JSON object>}` | `"accept"` / `"reject"` |
| `chain.*` | `{"chain": [<credential>, ...]}`（チェーン起点が先頭） | `"accept"` / `"reject"` |
| `commitment.*` | `{"credential": <object>, "sources": [<credential>, ...]}` | `{"confidence": "verified" \| "indeterminate" \| "failed"}`、構築系は期待出力 object |
| `chain.trigger.*` | `{"trigger": "single-conformant-event" \| "timer" \| ..., "credential": <object>}`（fan-out は `"credentials"`、batch-of-one は `"consumed_pending"` 付き） | `"accept"` / `"reject"`（発行挙動の適合性） |
| `commitment.scope.*` | `{"credential": <object>, "predecessor": <object>}` | `"accept"` / `"reject"` |
| `commitment.source-root.*`（構築系） | `{"sources": [<credential>, ...], "source_root_canonical": <id>}` | `{"derived_from", "source_root", "source_root_canonical"}` の期待出力 |
| `signer.*` | `{"credential": <object>}` または registry 操作 `{"registry_op": {...}}` | `"accept"` / `"reject"` |
| `confidence.*` | 合成系 `{"axes": {<軸>: <state>}}`、lifecycle 系 `{"registry": [...], "cryptosuite", "proof_created"}` | `{"confidence": <state>}` |
| `process.*` | `{"process_type", "credential"?, "behavior"?, "sequence"?}`（発行・検証挙動の適合性） | `"accept"` / `"reject"` |
| `resolver.*` | 形式系 `{"key", "body"}`、状態系 `{"resolver_state", "non_existence_authority"?}` → confidence（`non_existence_authority` は照会先が当該識別子 namespace の非存在 authority かを示す — mapping がこれに依存する `NotFound` 入力では必須（→ `resolver.states`）、authority 非依存の state では省略）、挙動系 `{"sequence": [...]}`、batch `{"request", "response"}`、encoding `{"entry"}` | `"accept"` / `"reject"` / `{"confidence"}` / `{"state"}` |
| 永続化・append-only 系（`commitment.store.*` / `registry.*`） | `{"sequence": [{"op": ...}, ...]}` | `"reject"` または期待状態 object |
| `identity.*` | 導出系 `{"credential": <wire 形式 JSON object>}` または `{"variants": [<wire 形式>, ...]}` — 入力をテキストでなく object で持つのは、これらの rule が **canonical 射影**を digest するため（到着時の綴りは id が定義上消し去るもの）。store 系 `{"sequence": [{"op": "put-variant" \| "get-variant" \| "list-variants" \| "legacy-put" \| "get", ...}]}` で、op は store 事象を指し、バイト精度が要点になる箇所は `stored_bytes`（JSON テキスト）で「storage が保持している内容」を注入する | `"reject"` または期待出力 object（導出系は `{"canonical", "body_address", "wire_variant_id"}`、store 系は `{"variant_set", "exact_bytes"?, "projection_variant_id"?}`） |

- id 採番は `<family>-<3 桁連番>`、ファイル名は `<id>.json`
- description には「何の規範挙動を固定しているか」を 1 文で（実装名は書かない）
- `identity-*` は `tools/gen_identity_vectors.py` が生成する（`--check` で再導出
  して差分検出）。hash は rule 本文だけから導出し、実装の出力からは取らない —
  実装が書いた KAT は「コードがコード自身と等しい」ことしか証明しないため。
  編集は JSON ではなく生成器に対して行う。
