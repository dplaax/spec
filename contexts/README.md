# contexts/ — source of truth for JSON-LD context documents

The canonical documents for the dplaax protocol context. **Canonical at the byte
level** — implementations embed a byte-exact copy from this directory at
compile time (runtime fetching is prohibited). The `@context` array operates as
a byte sequence within the signature scope, so byte differences between
implementations cause hash partitioning (partition trap). Vendoring targets must
prevent drift with sha256 pinning tests.

## Ownership model (Model A, finalized 2026-06-11)

Two-layer structure:

1. **Protocol context (this directory)** — mapping from dplaax wire keys to IRIs.
   Owned by the protocol; identical across profiles.
2. **Profile extension context (issued by each profile; canonical source is on
   the profile's side)** — terms for the profile-owned custom subject fields, and
   claim grounding (prefix → URL mapping, → `credential.claim.grounding`). Redefinition of protocol terms is not permitted (`@protected` mechanically enforces
   this as well). Example: the canonical source for the provin profile context is
   provin.oss `vc/contexts/provin-v1.jsonld`.

Claim values (e.g., `provin:filter`) are string values on the wire and are
outside the scope of the context — semantic grounding is handled by the profile's
claim registry (→ `credential.claim.*` in rules/credential.yaml).

## Files

| file | URI | sha256 |
|---|---|---|
| `v1.jsonld` | `https://dplaax.dev/vc/v1` | `9716bca789bdb1042451746800cc463a616a57817008001a3a895e88c0aff25f` |

- The URI `https://dplaax.dev/vc/v1` is frozen as the v0 wire vocabulary and is
  immutable. The `@context` array rides the signing scope as bytes, so
  repointing it would partition hashes across implementations — a next-MAJOR
  break, not a compatible change.
- `transformationClaim` is defined with `@type: "@vocab"` — claim values
  (compact IRIs) resolve to vocabulary IRIs under the grounding URL upon JSON-LD
  expansion, so the identity of (grounding URL, label) is mechanically established
  at the JSON-LD/RDF layer as well (→ `credential.claim.grounding`).
- After modifying this document, update the sha256 in the table above and
  synchronize the change byte-exact to the vendoring target
  (provin.oss `vc/contexts/`).
