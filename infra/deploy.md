# Deployment — dplaax.dev wire surface (S3 + CloudFront)

`dplaax.dev` serves the protocol's **machine-readable wire identifiers**. This
is a different surface from the human landing page at `www.dplaax.dev` (that
lives in `dplaax/site`, with its own bucket and distribution). **Nothing here is
executed automatically** — `.github/workflows/deploy.yml` ships disabled; this
file documents the target topology.

## Why not GitHub Pages

Pages derives `Content-Type` from the file extension only and offers no way to
override response headers. The frozen wire URI `/vc/v1` is extensionless, so
Pages serves it as `application/octet-stream`. S3 object metadata lets us set
`application/ld+json`. That single constraint is why this surface is on
CloudFront + S3 rather than Pages.

## Topology

```text
Route 53                 CloudFront                     S3
─────────                ──────────                     ──
dplaax.dev  ──ALIAS──▶ Distribution  ──OAC──▶  s3://wire.dplaax.dev
                          (private bucket, versioning on)
```

`www.dplaax.dev` (the LP) is a **separate** bucket and distribution. Do not
point `dplaax.dev` at the LP distribution, and never `aws s3 sync --delete` an
LP build into `wire.dplaax.dev` — that would erase the identifier documents.

## S3 bucket

- Name: `wire.dplaax.dev`
- Public access: **blocked** (CloudFront reads via OAC)
- Static website hosting: **off** (CloudFront + OAC, not the S3 website endpoint)
- Versioning: **on** (recover from an accidental sync delete)
- Holds only the assembled wire tree — no other content shares this bucket.

## Served object layout

| path (URI)                   | S3 key                 | Content-Type          |
| ---------------------------- | ---------------------- | --------------------- |
| `/vc/v1`                     | `vc/v1`                | `application/ld+json` |
| `/schemas/<name>.json` (×16) | `schemas/<name>.json`  | `application/json`    |
| `/oauth/grant-type/did`      | `oauth/grant-type/did` | `text/html`           |
| `/` (root)                   | `index.html`           | `text/html`           |
| 404                          | `404.html`             | `text/html`           |

The identifier paths (`/vc/v1`, `/oauth/grant-type/did`) are stored as
**extensionless objects** so their frozen URIs resolve directly, without a
directory-index rewrite. The deploy workflow sets their `Content-Type`
explicitly (S3 would otherwise guess `application/octet-stream`).

## CloudFront distribution

- Origin: `wire.dplaax.dev` via Origin Access Control (OAC)
- Default root object: `index.html`
- Custom error responses: `403`/`404` → `/404.html` (return HTTP 404)
- Compress objects: on; HTTP/2 + HTTP/3
- TLS: ACM certificate in `us-east-1` for `dplaax.dev`
- Alternate domain name (CNAME): `dplaax.dev`

## Migration from GitHub Pages (one-time)

`dplaax.dev` currently serves this tree from Pages
(`.github/workflows/pages.yml`). Cut over without dropping the live identifier:

1. Provision the bucket, cert, and distribution above.
2. Run the deploy (enable `deploy.yml`, or run the manual fallback) and verify on
   the distribution domain (`d….cloudfront.net`) **before** touching DNS:
   byte-exact `/vc/v1` (sha256 `9716bca…`) **and**
   `Content-Type: application/ld+json`.
3. Repoint `dplaax.dev` A/AAAA from the Pages IPs to the CloudFront alias.
4. Re-verify against `https://dplaax.dev/…`, then **retire `pages.yml`**.

## Manual deploy fallback

```bash
# from the repo root, with AWS creds for the wire account.
# fail fast: a partial assembly must never reach a --delete sync of the live
# bucket, and drift must never pass under the frozen URI.
set -euo pipefail

# assemble step mirrors .github/workflows/deploy.yml:
rm -rf _site && mkdir -p _site/vc _site/schemas _site/oauth/grant-type
cp site/index.html _site/index.html
cp site/404.html   _site/404.html
cp site/oauth/grant-type/did/index.html _site/oauth/grant-type/did
cp contexts/v1.jsonld _site/vc/v1
cp schemas/*.json _site/schemas/

# the same byte-exact guard the workflow enforces
expected=9716bca789bdb1042451746800cc463a616a57817008001a3a895e88c0aff25f
[ "$(shasum -a 256 _site/vc/v1 | cut -d' ' -f1)" = "$expected" ] \
  || { echo "vc/v1 drifted from the signing-scope pin"; exit 1; }

# extensionless identifier keys are excluded from the sync and uploaded once
# with the right type (same rationale as the workflow: no octet-stream window)
aws s3 sync _site/ s3://wire.dplaax.dev/ --delete \
  --exclude "vc/v1" --exclude "oauth/grant-type/did"
aws s3 cp _site/vc/v1 s3://wire.dplaax.dev/vc/v1 --content-type application/ld+json
aws s3 cp _site/oauth/grant-type/did s3://wire.dplaax.dev/oauth/grant-type/did --content-type text/html
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```

## CI deployment

`.github/workflows/deploy.yml` ships disabled (`if: false`). To enable:

1. Create an AWS IAM role trusted by GitHub OIDC
   (`token.actions.githubusercontent.com`) with S3 sync + CloudFront
   `create-invalidation` permissions on **this** bucket / distribution only.
2. Add repo secrets: `AWS_ROLE_TO_ASSUME`, `AWS_REGION`, `S3_BUCKET`
   (`wire.dplaax.dev`), `CLOUDFRONT_DISTRIBUTION_ID`.
3. Change `if: false` to `if: github.ref == 'refs/heads/main'`.
