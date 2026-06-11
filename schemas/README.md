# schemas/ — source of truth for wire shapes

JSON Schema 2020-12. This is the sole location of norms for wire-level structure
(field presence, types, and formats). Behavioral and judgment norms are not held
here (→ `rules/`).

- File naming: `<topic>.json` (example: `pipeline-pass-credential.json`)
- Each schema is referenced from the `schemas` field of the corresponding rule entry
- Intentionally permissive or strict areas of a schema are documented in
  `$comment` fields within the schema

Current state: empty. The transcription backlog is tracked via the `source` field
in `rules/` (`status: todo` entries).
