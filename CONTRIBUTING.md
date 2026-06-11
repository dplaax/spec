# Contributing to the dPLaaX Specification

Contributions and public review of the dPLaaX spec are welcome.
This document explains how to submit proposals and the conventions specific
to this repository.

## Public review

- Questions, counterexamples, and ambiguity reports about normative content
  (rule statements, vector expected values) are accepted via **Issues**. The
  most valuable submissions are concrete cases such as "these two interpretations
  of this rule are both consistent with the text" or "this vector's expected
  value cannot be reproduced by this implementation".
- Objections to design decisions are processed most efficiently when they specify
  what breaks — which of interoperability, auditability, or decidability is
  affected, and how.

## Change proposals (Pull Requests)

1. **Normative content lives in exactly three artifacts** — `rules/` (behavior
   and judgment), `schemas/` (wire shape), `vectors/` (expected inputs and
   outputs). Markdown is non-normative; every normative change must be expressed
   as a change to a rule, schema, or vector (→ [README.md](README.md)).
2. **Rule statements are at most 256 characters, contain RFC 2119 normative
   keywords, and are not re-expressed anywhere else.** `notes` is non-normative
   — normative keywords there fail the lint.
3. **Behavioral norm changes require accompanying vectors** — new rules need at
   least one vector; semantic changes are expressed as changes to the expected
   values of existing vectors (which counts as a semantic change;
   → [VERSIONING.md](VERSIONING.md)).
4. **Keep lint green**: `python3 tools/lint.py`
5. Vector expected values (hashes, Merkle roots, etc.) must be derived from the
   spec rules; where possible, recompute them with an independent implementation.
   Include the derivation in the PR description.

## Unit of compatibility

Compatibility is measured by the **`id` of a rule and the meaning of its
`statement`**. File layout, line numbers, and markdown are outside the normative
scope. In 0.x, rule deletion and semantic changes are permitted within a minor
release — see [VERSIONING.md](VERSIONING.md) for details.

## Governance

Currently, decisions are made at maintainer discretion; all discussion happens
publicly in Issues and PRs. As the contributor base grows, the decision-making
process (rule promotion, breaking-change deliberation) will be formalized
incrementally. Open an Issue to propose changes to this process.

## License

Contributions are deemed submitted under the [Apache License 2.0](LICENSE).
