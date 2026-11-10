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
| `delegation.*` | `{"credential": <delegation credential JSON>}`; use-type (`delegation.use.*`) adds `"target"`, the DID of the identity a consumer is asked to act for | `"accept"` / `"reject"` (owner-signed authority delegation; the issuer is an Owner DID and the subject is structurally under it; for use-type, whether the delegation is authority for `target`) |
| `confidence.*` | synthesis-type `{"axes": {<axis>: <state>}}`; lifecycle-type `{"registry": [...], "cryptosuite", "proof_created"}` | `{"confidence": <state>}` |
| `process.*` | `{"process_type", "credential"?, "behavior"?, "sequence"?}` (issuance and verification behavior conformance) | `"accept"` / `"reject"` |
| `resolver.*` | format-type `{"key", "body"}`; state-type `{"resolver_state", "non_existence_authority"?}` → confidence (`non_existence_authority` marks whether the queried source is authoritative for non-existence in the identifier's namespace — required for `NotFound` inputs, whose mapping depends on it (→ `resolver.states`); omitted for states whose mapping is authority-independent); behavior-type `{"sequence": [...]}`; batch `{"request", "response"}`; encoding `{"entry"}` | `"accept"` / `"reject"` / `{"confidence"}` / `{"state"}` |
| persistence / append-only (`commitment.store.*` / `registry.*`) | `{"sequence": [{"op": ...}, ...]}` | `"reject"` or expected-state object |
| `transfer.*` | `{"sequence": [{"op": <event>}, ...]}` where `op` is one of `emit` / `receive` / `rewrite-recorded-ordinal` / `process-restart` / `enumerate` / `register-signed` / `lookup`. The driver builds real fixtures (like the persistence family); ops name the record events, not payloads | `"accept"` / `"reject"` / an expected-state object (`{"join"}` / `{"state"}`) — record-property assertions, not hashes |
| `audit.*` | `{"chain": [<credential>, ...], "controllers": {<DID>: <controller DID>, ...}}` (chain origin first; `controllers` is the controller-binding fixture — a DID absent from its keys is terminal, i.e. an Owner. Attribution traverses these bindings, never lexical DID truncation) | `{"attribution": {"segments": [{"index": <n>, "owner": <DID>}, ...], "pre_chain": <DID>}}` |
| `effect.*` / `claims.effect.*` | artifact-type `{"credential": <record object>}` — the record named by the rule's schema (ReleaseAuthorization / quarantine entry / ObservationRecord / DecisionRecord / effect-status record); judgment-type uses named carriers as needed: `{"authorization"?, "entry"?, "transition"?, "release_input"?, "decision_record"?, "legacy_receipt"?, "scope"?, "evidence"?, "sequence"?, ...}` | `"accept"` / `"reject"` / an expected-disposition object (e.g. `{"evidence", "policy_decision"}`) |
| `release.*` | artifact-type `{"credential": <ReleaseEvidenceManifest / AdvisoryAssessment / ReleaseWaiver>}`; judgment-type uses named carriers: `{"manifest"?, "scan"?, "assessment"?, "waiver"?, "workflow"?, "image_ref"?, "sequence"?, ...}` | `"accept"` / `"reject"` |
| `identity.*` | derivation-type `{"credential": <wire-form JSON object>}` or `{"variants": [<wire form>, ...]}` — the input is carried as an object, not text, because these rules digest the CANONICAL projection: the spelling it arrived in is what the id is defined to erase; store-type `{"sequence": [{"op": "put-variant" \| "get-variant" \| "list-variants" \| "legacy-put" \| "get", ...}]}`, where an op names a store event and `stored_bytes` (a JSON text) injects what storage holds when byte-level precision is the point | `"reject"` or an expected-output object (`{"canonical", "body_address", "wire_variant_id"}` for derivation; `{"variant_set", "exact_bytes"?, "projection_variant_id"?}` for store-type) |
| `keybinding.*` | binding-type `{"credential": <KeyBindingCredential>, "status_list": <the revocation list the verifier holds>, "anchor": {"issuer", "issuance_keys", "max_validity_seconds", "max_status_age_seconds"}, "verifier": {"audience", "skew_seconds"}, "at": <decision time>}`; list-type `{"credential": <revocation list read>, "held"?: <the list held of the same issuer and id>, "anchor", "verifier": {"skew_seconds"}, "at"}`; hash-type `{"credential": <revocation list>}`. `anchor` is the relying party's trust anchor for the issuer. Each `proofValue` is a placeholder: the driver signs each credential with a fixture key of the verification method its proof names | `"accept"` / `"reject"` (list-type accept: the verifier holds the list read, or keeps the held one when it is the same list); `keybinding.status-list.monotonic` rejections `{"result": "reject", "reason": "status-list-rewound" \| "status-list-revocation-cleared"}`; hash-type `{"contentHash": "sha256:<hex>"}` |

- Id numbering: `<family>-<3-digit sequence>`, file name: `<id>.json`
- `description` states in one sentence what normative behavior is being fixed
  (do not name specific implementations)
- The `identity-*` vectors are generated by `tools/gen_identity_vectors.py`
  (`--check` re-derives and diffs). Their hashes come from the rule text alone,
  never from an implementation's output — a KAT an implementation authored
  proves only that the code equals itself. Edit the generator, not the JSON.
- The `keybinding-*` vectors are generated by `tools/gen_keybinding_vectors.py`
  in the same way: each is one defect against a well-formed baseline, and the
  content hashes are computed from `keybinding.status-list.content-hash`
  alone. `--check` compares an `encodedList` by the bits it expands to, since
  another gzip writer may spell the same bits otherwise.
