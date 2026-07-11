# schemas/ — source of truth for wire shapes

JSON Schema 2020-12. This is the sole location of norms for wire-level structure
(field presence, types, and formats). Behavioral and judgment norms are not held
here (→ `rules/`).

- File naming: `<topic>.json` (example: `pipeline-pass-credential.json`)
- Each schema is referenced from the `schemas` field of the corresponding rule entry
- Intentionally permissive or strict areas of a schema are documented in
  `$comment` fields within the schema

## Files

| schema | wire shape | referenced by |
| --- | --- | --- |
| `pipeline-pass-credential.json` | PipelinePassCredential (envelope, credentialSubject incl. the source-commitment triple, proof) | `credential.*` shape rules, `signer.proof.structure`, `commitment.class.definition` / `.derived-from` / `.source-root.encode` |
| `delegation-credential.json` | DelegationCredential (owner-signed authority delegation) | `delegation.shape` / `.proof` / `.scope` |

Schema-design facts (behavioral norms stay in `rules/` — each inline
`$comment` points at its owning rule instead of paraphrasing it):

- `additionalProperties: true` everywhere — a design consequence of
  `credential.body-sot` and `credential.claim.open-world-accept`. A schema
  here is a necessary condition for conformance, never the whole rule.
- Constraints JSON Schema cannot express (Unicode character classes,
  set-ordering, cross-field equalities, signature judgments) stay with their
  rules and vectors.
- The envelope (protobuf `dplaax.pipeline.v1.Envelope`) is not duplicated
  here: its wire-shape source of truth is the proto file.

## Validation (the schemas' teeth)

`tools/validate_vectors.py` (CI: next to the lint) checks two directions:

- every successful vector (`expect: "accept"` or an expected-output object)
  of a schema-referencing rule has its credential fixtures
  (`input.credential`, `input.sources[]`) validate against the schema — a
  successful vector yielding no fixture is an error, so coverage cannot
  silently drop;
- synthetic negative checks: deleting any `required` member from a
  known-good fixture has to make validation fail, so an under-strict edit to
  a schema cannot land silently.

`expect: "reject"` vectors are exempt: many rejections are behavioral and
structurally well-formed.
