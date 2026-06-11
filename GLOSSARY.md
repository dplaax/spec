# Glossary

Non-normative. Each term is defined in a single table row; no explanatory prose is added.

| Term | Definition |
| --- | --- |
| dPLaaX / dplaax | Protocol name (display form) / wire namespace (the prefix of `dplaax.*.v1`, `did:dplaax`, etc.) |
| data pipeline (broad sense) | Any flow in which data is handed across boundaries; not limited to purpose-built pipeline products |
| process boundary | A boundary where a data handoff occurs; the unit at which records are issued |
| wire profile | The bundle of choices an implementation declares (algorithms, representation forms, etc.). What dPLaaX standardizes is structure and adjudication, not the choices themselves |
| conformance class | The unit that scopes rule applicability, expressed by a rule entry's `class` field |
| chain origin | A credential that carries no previousCredential and starts a new chain |
| component type | The classification of a boundary's behavior (FilterConvert / Origin Source / External Sink / Custom), determined by signing behavior on the wire |
| audit-reachable | An optional conformance class providing audit reachability across aggregation boundaries (see rules/commitment.yaml) |
| trust layering (L1/L2/L3) | L1 = per-credential self-consistency (the three confidence axes; see rules/confidence.yaml). L2 = audit reachability (tracing back to the consumed-source set via the source commitment; the audit-reachable class). L3 = semantic audit (whether the output was correctly derived from the declared sources). The protocol guarantees L1+L2; L3 is outside its decision scope (adapters / audit infrastructure) |
| attribution computation | The audit-side actor that maps a verified chain to responsibility: which Owner DID answers for which segment, and for everything preceding the chain origin (see rules/audit.yaml). A deterministic function of chain topology; it reads no payload content |
