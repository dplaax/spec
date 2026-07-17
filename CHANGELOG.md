# Changelog

All notable changes to the dPLaaX protocol specification and namespace documents
are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

While the version is `0.x`, the specification and namespace-document URIs may
still change between minor releases. Published (byte-frozen) documents are
declared when the specification goes public.

## [0.1.0] - 2026-07-17

Initial public release of the specification draft.

### Added

- The `did:dplaax` DID method and registry model.
- The DID grant-type namespace document for
  `https://dplaax.dev/oauth/grant-type/did`, published at the wire-identifier
  path (the identifier is compared byte-for-byte).
- Conformance and protocol drafts for the provenance data plane, the audit /
  reconciliation model, and the cross-organization export seam.
- The first auth conformance vectors: kid-match, DID id-equality, and
  resolution failure-mapping.
- Namespace documents and JSON Schemas served at their production URIs under
  `https://dplaax.dev/`.

[0.1.0]: https://github.com/dplaax/spec/releases/tag/v0.1.0
