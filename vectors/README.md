# vectors/ — materialization of behavioral norms (source of truth)

Conformance vectors. The behavioral and judgment norms of rules are ultimately
defined by the pairs of inputs and expected results contained here.

- File naming: `<vector-id>.json` (example: `chain-001.json`)
- Format:

```json
{
  "id": "chain-001",
  "rule": "chain.trigger.retention",
  "description": "one conformant preceding event → chain retained",
  "input": {},
  "expect": "accept"
}
```

- `rule`: the corresponding rule id (the lint verifies resolution). The rule's
  `vectors` field must also list the vector id (bidirectional).
- `expect`: `"accept"` / `"reject"` / an expected-output object (for
  construction-type rules)
- Implementation tests may serve as seeds, but must be rewritten from the spec
  rather than encoding implementation-specific behavior
- Numeric values and hashes in expected values must be derived from the spec
  and verified against an actual implementation (provin.oss) before being
  recorded

## Input/expect shape conventions (by family)

Because vector files are JSON, inputs requiring byte-level precision (duplicate
keys, invalid UTF-8, extraneous data, etc.) cannot be represented as parsed
objects. Shapes are fixed per family as follows:

| family | input | expect |
|---|---|---|
| `canon.*` | `{"document": <JSON text as string>}`. Only byte sequences that cannot be represented as a JSON string (invalid UTF-8, etc.) use `{"document_b64": <base64>}` | `"reject"` or `{"canonical": <string>}` — comparison is performed as UTF-8 bytes of the decoded strings |
| `credential.*` | `{"credential": <wire-format JSON object>}` | `"accept"` / `"reject"` |
| `chain.*` | `{"chain": [<credential>, ...]}` (chain origin first) | `"accept"` / `"reject"` |
| `commitment.*` | `{"credential": <object>, "sources": [<credential>, ...]}` | `{"confidence": "verified" \| "indeterminate" \| "failed"}`; construction-type yields an expected-output object |
| `chain.trigger.*` | `{"trigger": "single-conformant-event" \| "timer" \| ..., "credential": <object>}` (fan-out uses `"credentials"`; batch-of-one includes `"consumed_pending"`) | `"accept"` / `"reject"` (issuance behavior conformance) |
| `commitment.scope.*` | `{"credential": <object>, "predecessor": <object>}` | `"accept"` / `"reject"` |
| `commitment.source-root.*` (construction-type) | `{"sources": [<credential>, ...], "source_root_canonical": <id>}` | expected output object with `{"derived_from", "source_root", "source_root_canonical"}` |
| `signer.*` | `{"credential": <object>}` or registry operation `{"registry_op": {...}}` | `"accept"` / `"reject"` |
| `confidence.*` | synthesis-type `{"axes": {<axis>: <state>}}`; lifecycle-type `{"registry": [...], "cryptosuite", "proof_created"}` | `{"confidence": <state>}` |
| `process.*` | `{"process_type", "credential"?, "behavior"?, "sequence"?}` (issuance and verification behavior conformance) | `"accept"` / `"reject"` |
| `resolver.*` | format-type `{"key", "body"}`; state-type `{"resolver_state"}` → confidence; behavior-type `{"sequence": [...]}`; batch `{"request", "response"}`; encoding `{"entry"}` | `"accept"` / `"reject"` / `{"confidence"}` / `{"state"}` |
| persistence / append-only (`commitment.store.*` / `registry.*`) | `{"sequence": [{"op": ...}, ...]}` | `"reject"` or expected-state object |
| `audit.*` | `{"chain": [<credential>, ...], "controllers": {<DID>: <controller DID>, ...}}` (chain origin first; `controllers` is the controller-binding fixture — a DID absent from its keys is terminal, i.e. an Owner. Attribution traverses these bindings, never lexical DID truncation) | `{"attribution": {"segments": [{"index": <n>, "owner": <DID>}, ...], "pre_chain": <DID>}}` |

- Id numbering: `<family>-<3-digit sequence>`, file name: `<id>.json`
- `description` states in one sentence what normative behavior is being fixed
  (do not name specific implementations)
