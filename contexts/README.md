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
- This document does not change. New terms go in a branch context (below)
  or in the next base version. Implementations vendor it byte-exact (provin.oss
  `vc/contexts/`) and pin the sha256 above.
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
  `<stamp>` is a UTC time, `YYYYMMDDHHmm`, fixed in the pull request that adds
  the snapshot (not its merge or deploy time) and later than every snapshot
  the branch already has; a snapshot rebased past a newer one is restamped.
  The path without a stamp is not served, and there is no alias for the
  latest.
- **Frozen.** A snapshot is frozen from its merge into `develop`, the first
  point at which others vendor it, as `v1.jsonld` is frozen: a change is a
  new snapshot under a new stamp. Its sha256 is pinned in
  `contexts/branches/SHA256SUMS`, one line per snapshot, the path relative to
  `/vc/branches/` and without `.jsonld`. The deploy checks the served bytes
  against those pins, and never deletes a snapshot once uploaded.
- **Add only within a branch.** A later snapshot of a branch keeps every term
  of the earlier ones with the same definition and only adds terms, so every
  term an earlier snapshot defines means the same under the latest. A term
  whose meaning would change goes in a branch of another name.
- **One definition per name on a base.** A branch's terms do not redefine
  the base's, and a term name that several branches of a base define has the
  same definition in each, so the branches can be listed together and folded
  together. A document lists the base context, then the branch context: a key
  binding's `@context` is
  `[credentials v2, dplaax v1, …/vc/branches/v1/keybinding/<stamp>]`.
- **Into the next base version.** When a branch's rules are confirmed (their
  promotion to `stable` is the guide), its latest snapshot is folded into the
  next base version (`/vc/v2`) with the same IRIs. A branch whose rules are
  never confirmed is not folded. Snapshots once shipped stay served, and an
  implementation keeps the copies it embeds, so a credential that names one
  keeps its meaning.
- **Implementations.** An implementation that expands a credential as JSON-LD
  (an eddsa-rdfc-2022 verifier, for example) reads only the snapshots it
  embeds, byte-exact and pinned against `SHA256SUMS`, and never fetches a
  context (`signer.suite.rdfc-expansion-guard`): a credential that names a
  snapshot it does not embed cannot be expanded there. A verifier of a JCS
  proof (eddsa-jcs-2022) reads no context document, and a rule may let it
  accept any snapshot of a branch by its URI's form.
- **Checked.** `tools/lint.py` checks the paths and stamps, the pins, the add-
  only order, the one definition per name, and, against the ref a change is
  made on (`DPLAAX_BASE_REF`, set in CI), that no shipped snapshot changed.

| snapshot | sha256 |
|---|---|
| `https://dplaax.dev/vc/branches/v1/keybinding/202611101543` | `cc07379a021cad29b2e8f5c137a2d6c185e283cc523c7d59ef360b58f6594916` |

The key-binding branch defines `KeyBindingCredential` and its subject's
`kind`, `roles` (a `@set`, so one role stays an array), `audience` (an `@id`:
the relying party's DID), `keyClass`, `key`, `keyId` and `publicKeyJwk`
(`@json`: the JWK kept as it is). The values of `kind`, `roles`, `keyClass`
and `keyId` stay strings, never read as IRIs: the vocabularies of the first
three are the profile's, and a key id is a name. Its terms are full IRIs under
`https://dplaax.dev/vocab#`, as the base's are.
