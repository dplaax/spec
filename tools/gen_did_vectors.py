#!/usr/bin/env python3
"""Regenerate vectors/did-0{01..21}.json from the rule text.

Run: python3 tools/gen_did_vectors.py [--check]

  (no flag)  rewrite the vector files
  --check    recompute and diff against what is committed (non-zero exit if a
             vector no longer matches its derivation)

did.dplaax.syntax vectors expect "accept" or "reject"; did.dplaax.hierarchy
vectors expect the level the DID's resource path gives, its Owner (the DID of
its first three segments), and, for a Process, its Pipeline (the DID of its
first five). Each expected value is derived here from the rule text by an
independent reading of the grammar, never from an implementation's output.
The 253- and 254-octet registries are built as DNS-shaped names (labels of at
most 63 octets) so that only their length decides.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "vectors"

PREFIX = "did:dplaax:"
SEGMENT = re.compile(r"[A-Za-z0-9._-]+")
MAX_REGISTRY = 253

OWNER = "did:dplaax:poc.dplaax.dev:org:acme"
PIPELINE = OWNER + ":pipeline:p1"
PROCESS = PIPELINE + ":process:x"


def registry_of(length: int) -> str:
    """A DNS-shaped name of exactly length octets: labels of 63, then the rest."""
    labels, left = [], length
    while left > 63:
        labels.append("a" * 63)
        left -= 64
    labels.append("b" * left)
    name = ".".join(labels)
    assert len(name) == length
    return name


def syntax_ok(did: str) -> bool:
    """did.dplaax.syntax, read from its statement."""
    if not did.startswith(PREFIX):
        return False
    segs = did[len(PREFIX):].split(":")
    if len(segs) < 3:
        return False
    for seg in segs:
        if not SEGMENT.fullmatch(seg) or set(seg) == {"."}:
            return False
    return len(segs[0].encode()) <= MAX_REGISTRY


def hierarchy(did: str) -> dict:
    """did.dplaax.hierarchy, read from its statement."""
    segs = did[len(PREFIX):].split(":")
    owner = PREFIX + ":".join(segs[:3])
    path = segs[3:]
    if not path:
        return {"level": "owner", "owner": owner}
    if len(path) == 2 and path[0] == "pipeline":
        return {"level": "pipeline", "owner": owner}
    if len(path) == 4 and path[0] == "pipeline" and path[2] == "process":
        return {"level": "process", "owner": owner, "pipeline": PREFIX + ":".join(segs[:5])}
    return {"level": "none", "owner": owner}


def build() -> list[dict]:
    v = []

    def add(rule, description, did, expect):
        v.append({
            "id": f"did-{len(v) + 1:03d}",
            "rule": rule,
            "description": description,
            "input": {"did": did},
            "expect": expect,
        })

    def syntax(description, did, want):
        got = "accept" if syntax_ok(did) else "reject"
        assert got == want, (did, got, want)
        add("did.dplaax.syntax", description, did, got)

    syntax("An Owner DID is a did:dplaax DID", OWNER, "accept")
    syntax("A Process DID, with four resource-path segments, is a did:dplaax DID", PROCESS, "accept")
    syntax("Segments may use dots, underscores and hyphens", "did:dplaax:poc.dplaax.dev:org:acme_co-1.x", "accept")
    syntax("A registry of exactly 253 octets is accepted",
           f"did:dplaax:{registry_of(253)}:org:acme", "accept")
    syntax("A DID of two segments after the method is refused", "did:dplaax:poc.dplaax.dev:org", "reject")
    syntax("A DID with an empty segment (a trailing colon) is refused", OWNER + ":", "reject")
    syntax("A segment made of dots only is refused", "did:dplaax:poc.dplaax.dev:org:..", "reject")
    syntax("A segment with a slash is refused", "did:dplaax:poc.dplaax.dev:org:ac/me", "reject")
    syntax("A segment with a space is refused", "did:dplaax:poc.dplaax.dev:org:ac me", "reject")
    syntax("A segment with a non-ASCII character is refused", "did:dplaax:poc.dplaax.dev:org:acmé", "reject")
    syntax("A segment with a percent-encoded octet is refused", "did:dplaax:poc.dplaax.dev:org:%41cme", "reject")
    syntax("A DID of another method is refused", "did:dplaaxx:poc.dplaax.dev:org:acme", "reject")
    syntax("A DID whose method is in upper case is refused", "did:DPLAAX:poc.dplaax.dev:org:acme", "reject")
    syntax("A registry of 254 octets is refused",
           f"did:dplaax:{registry_of(254)}:org:acme", "reject")

    def level(description, did):
        assert syntax_ok(did), did
        add("did.dplaax.hierarchy", description, did, hierarchy(did))

    level("A DID with no resource path is an Owner, its own Owner", OWNER)
    level("A DID with resource path pipeline:<id> is a Pipeline of the Owner of its first three segments", PIPELINE)
    level("A DID with resource path pipeline:<id>:process:<id> is a Process, its Pipeline the DID of its first five segments", PROCESS)
    level("A DID with resource path pipeline:<id>:<other>:<id> is none of the three and has no Pipeline", PIPELINE + ":step:x")
    level("A DID with a one-segment resource path is none of the three", OWNER + ":pipeline")
    level("A DID whose resource path names process before pipeline is none of the three", OWNER + ":process:x:pipeline:p1")
    level("pipeline is compared byte for byte, so a resource path of Pipeline:<id> is none of the three", OWNER + ":Pipeline:p1")
    return v


def dump(vector: dict) -> str:
    return json.dumps(vector, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="diff against the committed vectors instead of rewriting")
    args = ap.parse_args()
    bad = 0
    for vector in build():
        path = VECTORS / f"{vector['id']}.json"
        if args.check:
            if not path.exists() or json.loads(path.read_text()) != vector:
                print(f"FAIL {path.name}: does not match its derivation")
                bad += 1
            continue
        path.write_text(dump(vector))
    if args.check:
        print("OK — did vectors match their derivation" if not bad else f"\n{bad} vector(s) differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
