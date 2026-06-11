# dPLaaX Specification (draft)

dPLaaX ("data PipeLine as a X") is a protocol that, whenever data crosses an
organizational or system boundary, records — in a tamper-detectable form at each
boundary — who received what, performed what action, and passed on what, so that
the resulting chain can be independently verified by third parties
(→ [concept.md](concept.md)).

> **Status: v0.1 (draft).** All rules are in `draft` state and will continue to
> evolve based on implementation feedback (→ [VERSIONING.md](VERSIONING.md)).
> **Public review and contributions are welcome** —
> see [CONTRIBUTING.md](CONTRIBUTING.md). Governance will be formalized
> incrementally as the contributor base grows (current state: maintainer
> discretion; discussions are public in Issues).

The normative spec for dPLaaX. **The source of truth for all normative content
is exactly the following three artifacts**; prose is non-normative.

| artifact | normative scope | format |
| --- | --- | --- |
| `rules/` | behavioral and judgment norms (rule catalog) | YAML |
| `schemas/` | wire shape norms | JSON Schema 2020-12 |
| `vectors/` | materialization of behavioral norms (conformance vectors) | JSON |

All markdown (this document, concept.md, GLOSSARY.md, etc.) is non-normative.
It references rule ids rather than re-expressing normative content. This
separation is mechanically enforced by `tools/lint.py`.

## Reading order

1. [concept.md](concept.md) — why dPLaaX exists (non-technical, non-normative)
2. [rules/](rules/) — the normative body
3. [schemas/](schemas/) / [vectors/](vectors/) — wire shapes and conformance vectors
4. [STATUS.md](STATUS.md) — current drafting state (temporary document, removed when stable)

## rule catalog format

Each entry in `rules/*.yaml`:

| field | convention |
| --- | --- |
| `id` | `<domain>.<topic>[.<name>]`. Provisional while `status: todo`; frozen on promotion to `draft` |
| `status` | `todo` (stub before transcription) / `draft` / `stable` |
| `class` | `core` (default) / `audit-reachable`. Conformance class membership |
| `statement` | The normative statement. A hard requirement for `draft` and above; at most 256 characters; contains at least one RFC 2119 normative keyword. One rule, one expression — re-expressing elsewhere is prohibited |
| `uses` | List of rule ids this rule depends on. Use cross-references instead of repeating normative text |
| `schemas` / `vectors` | References to corresponding artifact files |
| `notes` | Non-normative supplementary notes. Normative keywords in this field fail the lint |
| `source` | Temporary field recording the origin of a transcribed rule. Deleted upon transcription completion |

## Cross-cutting concerns

- **Dependency-type** (e.g., a credential depending on canonicalization) — reference
  via `uses`; do not repeat the text inline.
- **Principle-type** (design intent such as fail-closed) — not normative. Only
  individual rules that can be expressed as conformance vectors are normative.
  Design intent belongs in concept.md or `notes` as non-normative content.
- **Taxonomy-type** (conformance classes, etc.) — expressed via the `class` field.
- **File partitioning is non-normative** — the identity of an entry is carried by
  its `id`. Moving an entry between files leaves its normative meaning unchanged;
  resharding is a pure refactor.

## lint

```bash
python3 tools/lint.py
```

What is enforced: normative keywords outside rule statements fail the lint
(this covers the full markdown text and `notes` fields) / cross-file id
uniqueness / resolution of `uses`, `schemas`, and `vectors` references /
`status` and `class` enum values / statement length and normative keyword
presence. `STATUS.md` is excluded from scanning as it is a temporary working
document.

The structure (shape) of rule entries is defined by `tools/rule.schema.json`
and is bound to IDE validation via a modeline at the top of each `rules/*.yaml`
file. Content discipline is handled by lint; structural discipline by the schema.

## Versioning

→ [VERSIONING.md](VERSIONING.md)
