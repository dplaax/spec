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
   provin-line/profile.spec `contexts/v1.jsonld`. (Until that repository existed
   it was provin.oss `vc/contexts/provin-v1.jsonld` — the implementation standing
   in for a spec that had not been written. The document is unchanged; its owner
   is not.)

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
- This file is also **served** byte-exact at its own URI
  `https://dplaax.dev/vc/v1`: the deploy workflow (`.github/workflows/deploy.yml`)
  copies it to `/vc/v1` at deploy and fails the build if the served bytes'
  sha256 diverges from the pin above. So `contexts/v1.jsonld` is the single
  source for three consumers — this repo's served identifier, the provin.oss
  vendored copy, and any implementation embedding it — all sharing one sha256.

## Branch contexts (`/vc/branches/`)

A branch context holds the terms of one feature on a base version of the
protocol context, so that the base stays frozen while the feature's terms
are defined and tried.

- **Path.** `contexts/branches/<base>/<feature>/<stamp>.jsonld`, served
  byte-exact at `https://dplaax.dev/vc/branches/<base>/<feature>/<stamp>`.
  `<stamp>` is the UTC time the snapshot was frozen, as `YYYYMMDDHHmm`. The
  path without a stamp is not served.
- **Frozen.** Each snapshot is frozen once shipped, as `v1.jsonld` is: a
  change is a new snapshot under a new stamp. Its sha256 is pinned in
  `contexts/branches/SHA256SUMS`, which the deploy workflow checks the served
  bytes against.
- **Add only within a branch.** A later snapshot of a branch keeps every term
  of the earlier ones with the same definition and only adds terms, so a
  document under any snapshot of a branch means the same under its latest.
  A term whose meaning would change goes in a branch of another name.
- **Beside its base.** A branch's terms do not redefine the base's. A
  document lists the base context, then the branch context: a key binding's
  `@context` is `[credentials v2, dplaax v1, …/vc/branches/v1/keybinding/<stamp>]`.
- **Into the next base version.** When a branch's rules are confirmed (their
  promotion to `stable` is the guide), its latest snapshot is folded into the
  next base version (`/vc/v2`) with the same IRIs. Snapshots once shipped
  stay served, and an implementation keeps the copies it embeds, so a
  credential that names one keeps its meaning.
- **Vendoring.** An implementation that processes a branch's terms embeds
  each snapshot it reads byte-exact, pinned against `SHA256SUMS`.

| branch | snapshots | URI of the first | sha256 |
|---|---|---|---|
| `v1/keybinding` | `202611101543` | `https://dplaax.dev/vc/branches/v1/keybinding/202611101543` | `cc07379a021cad29b2e8f5c137a2d6c185e283cc523c7d59ef360b58f6594916` |

The key-binding branch defines `KeyBindingCredential` and its subject's
`kind`, `roles` (a `@set`, so one role stays an array), `audience` (an `@id`:
the relying party's DID), `keyClass`, `key`, `keyId` and `publicKeyJwk`
(`@json`: the JWK kept as it is). The values of `kind`, `roles`, `keyClass`
and `keyId` stay strings, never read as IRIs: the vocabularies of the first
three are the profile's, and a key id is a name. Its terms are full IRIs under
`https://dplaax.dev/vocab#`, as the base's are.
