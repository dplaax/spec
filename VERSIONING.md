# Versioning

- Current state: **0.1 (draft tag)**. The 0.1 tag conditions are met. While no
  consumer exists, the 0.1 tag is a milestone marker: vocabulary-level changes
  are absorbed by re-cutting the same tag (applied for the 2026-06-12 process
  type rename). The compatibility discipline below binds from the first
  consumed release onward.
- **Conditions for the 0.1 tag**: all entries in `rules/` are at `draft` or above / each `draft` rule has at least one conformance vector / lint green / all `source` fields removed (transcription complete).
- **Conditions for 1.0**: after full feature implementation, a period of real-world validation, and exhausting all breaking changes within 0.x.
- The unit of compatibility is the **`id` of a rule and the meaning of its `statement`**. File layout is outside the normative scope (→ [README.md](README.md)).
- Rule deletion and semantic changes are permitted within a minor release in 0.x. From 1.0 onward they are the sole justification for a major version increment.
- Adding vectors or schemas is always a minor change or smaller. Changing the expected value of an existing vector is treated as a semantic change to the corresponding rule.
