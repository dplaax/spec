#!/usr/bin/env python3
"""Regenerate vectors/identity-00{1..7}.json from the rule text.

Run: python3 tools/gen_identity_vectors.py [--check]

  (no flag)  rewrite the vector files
  --check    recompute and diff against what is committed (CI-friendly:
             non-zero exit if a vector no longer matches its derivation)

WHY THIS EXISTS. identity-001/002 pin hashes, and a hash a conformance vector
asserts must not be whatever the implementation happened to print — that is a
KAT proving only that the code equals itself. Everything here is derived from
the rule text alone (identity.body-address, identity.wire-variant-id):

  body address = "sha256:" + hex(sha256(RFC8785(wire minus proof)))
  wire variant = "wire:v1:jcs-rfc8785:sha256:"
                 + hex(sha256(b"provin-wire-variant-v1\\x00" + RFC8785(wire)))

provin.oss must then AGREE with these values (its tests consume the vectors) —
which is the check the README asks for, in the one direction that can fail.

WHY json.dumps IS AN RFC 8785 CANONICALIZER FOR THESE FIXTURES — AND ONLY
THESE. The fixtures carry no JSON number, so RFC 8785's number formatting (the
part that needs a real implementation) never fires; every key is ASCII, so
sorting by code point equals sorting by UTF-16 code unit (RFC 8785 3.2.3); and
no string needs an escape beyond the forms both agree on. Adding a number or a
non-BMP key to a fixture invalidates this shortcut — use a real RFC 8785
implementation (not provin.oss's) if that day comes.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "vectors"
DOMAIN_TAG = b"provin-wire-variant-v1\x00"


def rfc8785(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def body_address(wire: dict) -> str:
    body = {k: v for k, v in wire.items() if k != "proof"}
    return "sha256:" + hashlib.sha256(rfc8785(body)).hexdigest()


def wire_variant_id(wire: dict) -> str:
    return "wire:v1:jcs-rfc8785:sha256:" + hashlib.sha256(DOMAIN_TAG + rfc8785(wire)).hexdigest()


BODY = {
    "@context": [
        "https://www.w3.org/ns/credentials/v2",
        "https://dplaax.dev/vc/v1",
        "https://provin.dev/vc/v1",
    ],
    "type": ["VerifiableCredential", "PipelinePassCredential"],
    "issuer": "did:dplaax:poc.dplaax.dev:org:factory:pipeline:line1:process:p1",
    "validFrom": "2026-07-01T00:00:00Z",
    "credentialSubject": {
        "pipelineId": "pl-line1",
        "processId": "proc-p1",
        "transformationClaim": "provin:convert",
        "outputHash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "previousCredential": None,
    },
}

PROOF_A = {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2026-07-01T00:00:01Z",
    "verificationMethod": "did:dplaax:poc.dplaax.dev:org:factory:pipeline:line1:process:p1#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z2fixtureProofValueAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
}

# The same body, re-issued: a different created + proofValue. Nothing in the
# body moves, which is the whole point of identity-002.
PROOF_B = dict(PROOF_A, created="2026-07-02T00:00:01Z", proofValue="z2fixtureProofValueBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")

WIRE_A = dict(BODY, proof=PROOF_A)
WIRE_B = dict(BODY, proof=PROOF_B)


def build() -> list[dict]:
    body = body_address(WIRE_A)
    var_a, var_b = wire_variant_id(WIRE_A), wire_variant_id(WIRE_B)
    canon_a, canon_b = rfc8785(WIRE_A).decode(), rfc8785(WIRE_B).decode()

    assert body_address(WIRE_B) == body, "fixture bug: re-issuing a proof moved the body address"
    assert var_a != var_b, "fixture bug: distinct wire bytes collided"

    # A variant SET is lexicographic, and which of the two sorts first is an
    # accident of the fixture's bytes — not something a rule says. Sorting here
    # keeps the expectation about the set, so changing an unrelated fixture
    # field cannot silently flip what these vectors assert.
    var_set = sorted([var_a, var_b])

    # The same document, non-canonically spelled: one space after the outermost
    # brace. It parses to the identical document — so it canonicalizes back to
    # this very id — while not being the canonical bytes. This is the shape a
    # digest-only read check cannot catch.
    noncanon_a = canon_a[:1] + " " + canon_a[1:]

    return [
        {
            "id": "identity-001",
            "rule": "identity.wire-variant-id",
            "description": "The WireVariantID digests the domain tag followed by the RFC 8785 canonical bytes of the full wire document — the canonical projection, so the id names the document rather than the octets it arrived in",
            "input": {"credential": WIRE_A},
            "expect": {"canonical": canon_a, "body_address": body, "wire_variant_id": var_a},
        },
        {
            "id": "identity-002",
            "rule": "identity.body-address",
            "description": "Re-issuing a proof over the same body leaves the body address unchanged (so successor links survive) while yielding a distinct WireVariantID",
            "input": {"variants": [WIRE_A, WIRE_B]},
            "expect": {"body_address": body, "wire_variant_ids": [var_a, var_b]},
        },
        {
            "id": "identity-003",
            "rule": "identity.variant.immutable-set",
            "description": "Re-submitting the same variant id carrying the same bytes is idempotent — the variant set keeps exactly one entry and the second admission is not an error",
            "input": {
                "sequence": [
                    {"op": "put-variant", "credential": WIRE_A},
                    {"op": "put-variant", "credential": WIRE_A},
                ]
            },
            "expect": {"variant_set": [var_a]},
        },
        {
            "id": "identity-004",
            "rule": "identity.variant.immutable-set",
            "description": "Bytes held at a variant id that are not the canonical projection are corruption, even though they parse to the same document and so canonicalize back to that same id — a digest-only check would serve them",
            "input": {
                "sequence": [
                    {"op": "put-variant", "credential": WIRE_A},
                    {
                        "op": "get-variant",
                        "body_address": body,
                        "wire_variant_id": var_a,
                        "stored_bytes": noncanon_a,
                    },
                ]
            },
            "expect": "reject",
        },
        {
            "id": "identity-005",
            "rule": "identity.variant.immutable-set",
            "description": "A second proof admitted for a body does not evict the first: the set is append-only and each variant still fetches its own bytes exactly (admission does not evaluate proofs, so a later invalid proof cannot displace an earlier valid one)",
            "input": {
                "sequence": [
                    {"op": "put-variant", "credential": WIRE_A},
                    {"op": "put-variant", "credential": WIRE_B},
                ]
            },
            "expect": {"variant_set": var_set, "exact_bytes": {var_a: canon_a, var_b: canon_b}},
        },
        {
            "id": "identity-006",
            "rule": "identity.variant.immutable-set",
            "description": "Admission order does not decide the set: a variant arriving first does not exclude a later one, so a front-running proof cannot permanently keep a legitimate proof out (same set as the reverse order)",
            "input": {
                "sequence": [
                    {"op": "put-variant", "credential": WIRE_B},
                    {"op": "put-variant", "credential": WIRE_A},
                ]
            },
            "expect": {"variant_set": var_set, "exact_bytes": {var_a: canon_a, var_b: canon_b}},
        },
        {
            "id": "identity-007",
            "rule": "identity.resolution.exact-vs-legacy",
            "description": "A pre-existing body-only entry reads as a one-element variant set: its bytes are exact-fetchable under their derived variant id, and the legacy body-only projection serves that same variant",
            "input": {
                "sequence": [
                    {"op": "legacy-put", "body_address": body, "stored_bytes": canon_a},
                    {"op": "list-variants", "body_address": body},
                    {"op": "get-variant", "body_address": body, "wire_variant_id": var_a},
                    {"op": "get", "body_address": body},
                ]
            },
            "expect": {"variant_set": [var_a], "exact_bytes": canon_a, "projection_variant_id": var_a},
        },
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="diff against the committed vectors instead of rewriting")
    args = ap.parse_args()

    drift = 0
    for v in build():
        path = VECTORS / f"{v['id']}.json"
        text = json.dumps(v, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            have = path.read_text() if path.exists() else ""
            if have != text:
                print(f"FAIL {path.name} does not match its derivation from the rule text")
                drift += 1
        else:
            path.write_text(text)
            print(f"wrote {path.name}")
    if args.check:
        print("OK — identity vectors match their derivation" if not drift else f"\n{drift} vector(s) drifted")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
