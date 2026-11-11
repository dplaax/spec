# Versioning

- Current state: **0.2.0-alpha.1 (pre-release)**. The 0.1 tag conditions are
  met; the 0.2 tag conditions are not yet. Implementations vendor this
  repository's conformance vectors, so a tag is never re-cut: a change goes
  into a new version, and the compatibility discipline below binds. (Until
  v0.1.0 was published on 2026-07-17, the tag was re-cut as the draft
  changed, as for the 2026-06-12 process type rename.)
- **Pre-releases**: a version `0.N.0-alpha.K` marks a release on the way to
  0.N, cut before the conditions for the 0.N tag are met. `0.N.0` itself is
  cut once they are.
- **Conditions for the 0.1 tag**: all entries in `rules/` are at `draft` or above / every rule in the wire-core families (`chain`, `credential`, `delegation`, `process`, `registry`, `resolver`, `transfer`) has at least one conformance vector — the coverage floor `tools/lint.py` enforces / lint green (including rule↔vector bidirectional references) / all `source` fields removed (transcription complete).
- **Conditions for the 0.2 tag**: every `draft` rule in every family has at least one conformance vector (101/242 at v0.1.0, 118/257 at 0.2.0-alpha.1). Families graduate into the lint coverage floor as they fill in; `did` joined it at 0.2.0-alpha.1.
- **Conditions for 1.0**: after full feature implementation, a period of real-world validation, and exhausting all breaking changes within 0.x.
- The unit of compatibility is the **`id` of a rule and the meaning of its `statement`**. File layout is outside the normative scope (→ [README.md](README.md)).
- Rule deletion and semantic changes are permitted within a minor release in 0.x. From 1.0 onward they are the sole justification for a major version increment.
- Adding vectors or schemas is always a minor change or smaller. Changing the expected value of an existing vector is treated as a semantic change to the corresponding rule.
