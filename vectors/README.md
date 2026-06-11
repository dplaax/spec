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
| `signer.*` / `confidence.*` / `component.*` / `resolver.*` | 起草時に本表へ追記する | 同上 |

- id 採番は `<family>-<3 桁連番>`、ファイル名は `<id>.json`
- description には「何の規範挙動を固定しているか」を 1 文で（実装名は書かない）
