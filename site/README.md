# site/ — dPLaaX namespace documents

The publish root for `https://dplaax.dev`. Every directory here maps 1:1 to a
URL path: `site/oauth/grant-type/did/index.html` serves
`https://dplaax.dev/oauth/grant-type/did`.

These are **namespace documents**: human-readable pages hosted at the exact
URIs the protocol uses as wire identifiers (OAuth grant-type URIs, and — if
the context URI ever moves to the apex — JSON-LD contexts). The identifiers
themselves are compared byte-for-byte and never dereferenced at runtime;
these pages exist so that a URI a developer encounters on the wire resolves
to its own documentation.

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

Not yet live: the org is on the free plan and this repo is private, so
GitHub Pages cannot serve it. When the repo goes public, enable Pages
(publish `site/` via actions/deploy-pages or a `docs/`-style branch config)
and bind the `dplaax.dev` custom domain. Until then nothing breaks — no
identifier requires dereferencing.

## Current documents

| Path | Identifier | Status |
| --- | --- | --- |
| `oauth/grant-type/did/` | `https://dplaax.dev/oauth/grant-type/did` — the DID OAuth grant type | frozen (wire-live since 2026-07-12) |
