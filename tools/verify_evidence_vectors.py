#!/usr/bin/env python3
"""Independent EvidenceView identity and decision-vector checker.

This implementation intentionally shares no code with provin.oss.  The
fixtures contain no JSON numbers and only ASCII object keys, so Python's
sorted, compact JSON projection is byte-identical to RFC 8785 for this bounded
manifest contract.  The checker rejects values outside that bounded domain
instead of pretending to be a general-purpose JCS implementation.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
VERSIONED = re.compile(r".+@[0-9]+$")
CONTENT_ADDRESS = re.compile(r"sha256:[0-9a-f]{64}$")


def reject_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate object key {key!r}")
        out[key] = value
    return out


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(), object_pairs_hook=reject_duplicate_keys)


def bounded_jcs(value: Any) -> bytes:
    def check(node: Any) -> None:
        if node is None or isinstance(node, (str, bool)):
            return
        if isinstance(node, (int, float)):
            raise ValueError("numeric manifest members require a full RFC 8785 implementation")
        if isinstance(node, list):
            for item in node:
                check(item)
            return
        if isinstance(node, dict):
            for key, item in node.items():
                if not isinstance(key, str) or any(ord(ch) > 0xFFFF for ch in key):
                    raise ValueError("manifest keys must be BMP strings in this bounded implementation")
                check(item)
            return
        raise ValueError(f"unsupported JSON value {type(node).__name__}")

    check(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def evidence_view_id(manifest: dict[str, Any]) -> tuple[str, str]:
    canonical = bounded_jcs(manifest)
    return canonical.decode("utf-8"), "sha256:" + hashlib.sha256(canonical).hexdigest()


def decide(profile_id: str, required: list[str], vector: list[dict[str, Any]]) -> str:
    if not VERSIONED.fullmatch(profile_id) or not required or len(required) != len(set(required)):
        raise ValueError("invalid decision profile")
    by_scope: dict[str, dict[str, Any]] = {}
    for entry in vector:
        scope = entry.get("scope")
        coverage = entry.get("coverage")
        has_truth = "truthState" in entry
        if not isinstance(scope, str) or scope in by_scope:
            raise ValueError("missing or duplicate scope")
        if coverage not in {"EVALUATED", "NOT_EVALUATED", "UNSUPPORTED"}:
            raise ValueError("invalid coverage")
        if has_truth != (coverage == "EVALUATED"):
            raise ValueError("truthState/coverage shape mismatch")
        if has_truth and entry["truthState"] not in {"FAILED", "INDETERMINATE", "VERIFIED"}:
            raise ValueError("invalid truthState")
        by_scope[scope] = entry

    selected = [by_scope.get(scope) for scope in required]
    if any(entry and entry.get("truthState") == "FAILED" for entry in selected):
        return "DENY"
    if any(
        entry is None
        or entry.get("coverage") != "EVALUATED"
        or entry.get("truthState") != "VERIFIED"
        for entry in selected
    ):
        return "QUARANTINE"
    return "ACCEPT"


def main() -> int:
    errors: list[str] = []

    identity = load(ROOT / "vectors" / "evidence-view-001.json")
    canonical, view_id = evidence_view_id(identity["input"]["credential"]["manifest"])
    if identity["expect"] != {"canonical": canonical, "evidenceViewId": view_id}:
        errors.append("evidence-view-001 expected canonical bytes or digest drifted")

    mismatch = load(ROOT / "vectors" / "evidence-view-002.json")
    supplied = mismatch["input"]["credential"]["evidenceViewId"]
    _, derived = evidence_view_id(mismatch["input"]["credential"]["manifest"])
    if supplied == derived or mismatch["expect"] != "reject":
        errors.append("evidence-view-002 no longer proves ID mismatch rejection")

    for name in ("claims-coverage-003", "claims-policy-001"):
        vector = load(ROOT / "vectors" / f"{name}.json")
        inp = vector["input"]
        actual = decide(inp["decisionProfileId"], inp["requiredScopes"], inp["vector"])
        expected = vector["expect"]
        if "decision" in expected and actual != expected["decision"]:
            errors.append(f"{name}: {actual} != {expected['decision']}")
        if "decisionNot" in expected and actual == expected["decisionNot"]:
            errors.append(f"{name}: unexpectedly produced {actual}")

    malformed = ["claims-coverage-002", "claims-coverage-004"]
    for name in malformed:
        vector = load(ROOT / "vectors" / f"{name}.json")
        entries = vector["input"]["credential"]["vector"]
        try:
            decide("shape-check@1", [entries[0]["scope"]], entries)
        except ValueError:
            continue
        errors.append(f"{name}: malformed coverage vector was accepted")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("OK — EvidenceView identity and appraisal vectors verified independently")
    return 0


if __name__ == "__main__":
    sys.exit(main())
