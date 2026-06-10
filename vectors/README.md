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

- `rule`: 対応する rule id（lint が解決を検証する）
- `expect`: `"accept"` / `"reject"` / 期待出力 object（構築系 rule の場合）
- 実装のテストを seed にしてよいが、実装の癖を encode せず spec 起点で書き直す

現状: 空。
