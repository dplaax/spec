# site/ — dPLaaX namespace documents

The publish root for `https://dplaax.dev`. Every directory here maps 1:1 to a
URL path: `site/oauth/grant-type/did/index.html` serves
`https://dplaax.dev/oauth/grant-type/did`.

The apex `dplaax.dev` serves the protocol's **wire identifiers** — the OAuth
grant-type namespace document (`/oauth/grant-type/did`), the JSON-LD context
(`/vc/v1`), and the JSON Schemas (`/schemas/*.json`). The identifiers
themselves are compared byte-for-byte and never dereferenced at runtime;
these pages exist so that a URI a developer encounters on the wire resolves
to its own documentation.

The apex root (`/`) and any unmatched path redirect to **www.dplaax.dev**,
the separate project landing site (not in this repo). The identifier paths
above are real files, so they serve directly and are unaffected by the
redirect.

## Rules

- **Published documents are frozen.** Once a path has shipped in a release,
  its meaning never changes; editorial fixes are fine, semantic changes get a
  NEW path (`/v2`, a new grant name). JSON-LD contexts, if ever hosted here,
  are byte-frozen outright — they enter signature scopes.
- **Identifier paths live at the root** (`/oauth/...`, `/vc/...`), never
  under a site section like `/spec/` — identifiers name protocol elements,
  not places in a website. Human documentation sections may exist alongside
  (e.g. `/spec/...`) but identifiers do not point into them.
- **Self-contained pages only**: no external assets, no build step that
  rewrites bytes (no minification). `.nojekyll` keeps branch-based Pages
  publishing from touching content.

## Publishing

`.github/workflows/pages.yml` deploys to GitHub Pages (source: GitHub
Actions) on push to `develop`. It **assembles** the served tree rather than
serving `site/` verbatim: it copies `site/` as-is, then copies the
machine-readable identifiers in byte-for-byte from their canonical sources —
`contexts/v1.jsonld` → `/vc/v1`, `schemas/*.json` → `/schemas/*.json` — so
those payloads live in exactly one place and cannot drift. A build step fails
the deploy if the served `/vc/v1` sha256 ever diverges from the signing-scope
pin (`9716bca…`). The `CNAME` file binds `dplaax.dev`.

Not live until the repo is public: on the free plan GitHub Pages does not
serve a private repo. The workflow + `CNAME` make it ready; going public
activates it. Until then nothing breaks — no identifier requires
dereferencing (the context is embedded + sha256-pinned in provin.oss).

Caveat: GitHub Pages cannot set a custom `Content-Type`, so `/vc/v1`
(extensionless) is served with the host default rather than
`application/ld+json`. Acceptable because the context is never dereferenced
at runtime; if a strict media type is ever required, move the apex to an
S3+CloudFront origin (as `provin.dev` already uses).

## Current documents

| Path | Identifier | Status |
| --- | --- | --- |
| `oauth/grant-type/did/` | `https://dplaax.dev/oauth/grant-type/did` — the DID OAuth grant type | frozen (wire-live since 2026-07-12) |
| `vc/v1` (assembled from `contexts/v1.jsonld`) | `https://dplaax.dev/vc/v1` — the v0 credential JSON-LD context | frozen, sha256-pinned `9716bca…` |
| `schemas/*.json` (assembled from `schemas/`) | `https://dplaax.dev/schemas/<name>.json` — the 16 wire JSON Schemas | `$id`-addressed |
| `index.html`, `404.html` | apex root / fallback → redirect to `www.dplaax.dev` | — |
