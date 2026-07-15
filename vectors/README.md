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
| --- | --- | --- |
| `canon.*` | `{"document": <JSON text as string>}`. Only byte sequences that cannot be represented as a JSON string (invalid UTF-8, etc.) use `{"document_b64": <base64>}` | `"reject"` or `{"canonical": <string>}` — comparison is performed as UTF-8 bytes of the decoded strings |
| `credential.*` | `{"credential": <wire-format JSON object>}` | `"accept"` / `"reject"` |
| `chain.*` | `{"chain": [<credential>, ...]}` (chain origin first) | `"accept"` / `"reject"` |
| `commitment.*` | `{"credential": <object>, "sources": [<credential>, ...]}` | `{"confidence": "verified" \| "indeterminate" \| "failed"}`; construction-type yields an expected-output object |
| `chain.trigger.*` | `{"trigger": "single-conformant-event" \| "timer" \| ..., "credential": <object>}` (fan-out uses `"credentials"`; batch-of-one includes `"consumed_pending"`) | `"accept"` / `"reject"` (issuance behavior conformance) |
| `commitment.scope.*` | `{"credential": <object>, "predecessor": <object>}` | `"accept"` / `"reject"` |
| `commitment.source-root.*` (construction-type) | `{"sources": [<credential>, ...], "source_root_canonical": <id>}` | expected output object with `{"derived_from", "source_root", "source_root_canonical"}` |
| `signer.*` | `{"credential": <object>}` or registry operation `{"registry_op": {...}}` | `"accept"` / `"reject"` |
| `delegation.*` | `{"credential": <delegation credential JSON>}` | `"accept"` / `"reject"` (owner-signed authority delegation; the issuer is an Owner DID and the subject is structurally under it) |
| `confidence.*` | synthesis-type `{"axes": {<axis>: <state>}}`; lifecycle-type `{"registry": [...], "cryptosuite", "proof_created"}` | `{"confidence": <state>}` |
| `process.*` | `{"process_type", "credential"?, "behavior"?, "sequence"?}` (issuance and verification behavior conformance) | `"accept"` / `"reject"` |
| `resolver.*` | format-type `{"key", "body"}`; state-type `{"resolver_state", "non_existence_authority"?}` → confidence (`non_existence_authority` marks whether the queried source is authoritative for non-existence in the identifier's namespace — required for `NotFound` inputs, whose mapping depends on it (→ `resolver.states`); omitted for states whose mapping is authority-independent); behavior-type `{"sequence": [...]}`; batch `{"request", "response"}`; encoding `{"entry"}` | `"accept"` / `"reject"` / `{"confidence"}` / `{"state"}` |
| persistence / append-only (`commitment.store.*` / `registry.*`) | `{"sequence": [{"op": ...}, ...]}` | `"reject"` or expected-state object |
| `transfer.*` | `{"sequence": [{"op": <event>}, ...]}` where `op` is one of `emit` / `receive` / `rewrite-recorded-ordinal` / `process-restart` / `enumerate` / `register-signed` / `lookup`. The driver builds real fixtures (like the persistence family); ops name the record events, not payloads | `"accept"` / `"reject"` / an expected-state object (`{"join"}` / `{"state"}`) — record-property assertions, not hashes |
| `audit.*` | `{"chain": [<credential>, ...], "controllers": {<DID>: <controller DID>, ...}}` (chain origin first; `controllers` is the controller-binding fixture — a DID absent from its keys is terminal, i.e. an Owner. Attribution traverses these bindings, never lexical DID truncation) | `{"attribution": {"segments": [{"index": <n>, "owner": <DID>}, ...], "pre_chain": <DID>}}` |
| `effect.*` / `claims.effect.*` | artifact-type `{"credential": <record object>}` — the record named by the rule's schema (ReleaseAuthorization / quarantine entry / ObservationRecord / DecisionRecord / effect-status record); judgment-type uses named carriers as needed: `{"authorization"?, "entry"?, "transition"?, "release_input"?, "decision_record"?, "legacy_receipt"?, "scope"?, "evidence"?, "sequence"?, ...}` | `"accept"` / `"reject"` / an expected-disposition object (e.g. `{"evidence", "policy_decision"}`) |
| `release.*` | artifact-type `{"credential": <ReleaseEvidenceManifest / AdvisoryAssessment / ReleaseWaiver>}`; judgment-type uses named carriers: `{"manifest"?, "scan"?, "assessment"?, "waiver"?, "workflow"?, "image_ref"?, "sequence"?, ...}` | `"accept"` / `"reject"` |

- Id numbering: `<family>-<3-digit sequence>`, file name: `<id>.json`
- `description` states in one sentence what normative behavior is being fixed
  (do not name specific implementations)
