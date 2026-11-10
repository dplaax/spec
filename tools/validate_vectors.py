#!/usr/bin/env python3
"""dplaax vector-vs-schema validation — the schemas' teeth.

For every vector whose rule references a schema file (the rule's `schemas`
field) and whose outcome is SUCCESSFUL, the vector's credential fixtures are
validated against that schema (JSON Schema 2020-12, format assertions on):

  - successful means `expect == "accept"` OR an object expect (construction
    and verdict-object families encode success as an expected-output object;
    their input fixtures are full wire forms either way). `expect == "reject"`
    vectors are exempt: many rejections are behavioral (signature, hash
    equality, charset classes) and structurally well-formed — the schema is a
    necessary condition, never the whole rule.
  - fixtures checked: `input.credential` and each element of `input.sources`.
    A successful vector of a schema-referencing rule that yields NO fixture is
    an error (coverage cannot silently drop to zero), as is a non-object
    entry in `sources`.
  - carriers of a fixed schema (CARRIER_SCHEMAS): in every successful vector
    of a keybinding.* rule, whatever the rule references, `input.status_list`
    and `input.held` (the revocation list a key-binding verifier holds) are
    validated against the status-list schema.

Additionally, synthetic negative checks guard against under-strict drift: for
each schema, a known-good fixture is mutated by deleting each `required`
member (top level and one level down) and each mutation must FAIL validation;
and where a schema fixes which of its objects are exact and which are open
(MEMBER_CHECKS), adding an unknown member there must FAIL or PASS
accordingly.

Requires: pyyaml, jsonschema[format-nongpl] (see .github/workflows/lint.yml).
"""
import copy
import json
import sys
from pathlib import Path

import yaml

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    print("FAIL tools/validate_vectors.py requires the jsonschema package")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# Known-good fixture per schema, for the synthetic negative checks.
GOOD_FIXTURES = {
    "pipeline-pass-credential.json": ("commitment-001", "input.credential"),
    "delegation-credential.json": ("delegation-001", "input.credential"),
    "release-authorization.json": ("effect-001", "input.credential"),
    "quarantine-entry.json": ("effect-002", "input.credential"),
    "observation-record.json": ("effect-003", "input.credential"),
    "decision-record.json": ("effect-004", "input.credential"),
    "effect-status.json": ("effect-005", "input.credential"),
    "release-evidence-manifest.json": ("release-001", "input.credential"),
    "advisory-assessment.json": ("release-002", "input.credential"),
    "release-waiver.json": ("release-003", "input.credential"),
    "key-binding-credential.json": ("keybinding-001", "input.credential"),
    "status-list-credential.json": ("keybinding-011", "input.credential"),
}

# Input carriers that always hold the same kind of fixture, validated against
# their schema in every successful vector that carries them.
CARRIER_SCHEMAS = {
    "status_list": "status-list-credential.json",
    "held": "status-list-credential.json",
}
CARRIER_RULE_PREFIX = "keybinding."

# Per schema, the objects of its known-good fixture (dotted paths, "" the
# top level) that are exact, where an unknown member is refused, and those
# that are open, where it is kept.
MEMBER_CHECKS = {
    "key-binding-credential.json": {
        "exact": ["credentialStatus", "credentialSubject.key", "credentialSubject.key.publicKeyJwk"],
        "open": ["", "credentialSubject"],
    },
    "status-list-credential.json": {
        "exact": [],
        "open": ["", "credentialSubject"],
    },
}
UNKNOWN_MEMBER = "x-member-not-in-the-catalog"

errors: list[str] = []


def load_rule_schemas() -> dict[str, list[str]]:
    """rule id -> list of schema file names it references."""
    out: dict[str, list[str]] = {}
    for path in sorted((ROOT / "rules").glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        for entry in (doc or {}).get("rules") or []:
            rid = entry.get("id")
            refs = entry.get("schemas") or []
            if rid and refs:
                out[rid] = refs
    return out


def load_validators() -> dict[str, Draft202012Validator]:
    out: dict[str, Draft202012Validator] = {}
    checker = FormatChecker()
    for path in sorted((ROOT / "schemas").glob("*.json")):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        out[path.name] = Draft202012Validator(schema, format_checker=checker)
    return out


def is_successful(expect) -> bool:
    return expect == "accept" or isinstance(expect, dict)


def fixtures_of(name: str, vector: dict) -> list[tuple[str, dict]]:
    """(label, credential-object) pairs this vector carries. Appends errors
    for malformed carriers instead of silently skipping them."""
    out: list[tuple[str, dict]] = []
    inp = vector.get("input") or {}
    cred = inp.get("credential")
    if cred is not None:
        if isinstance(cred, dict):
            out.append(("input.credential", cred))
        else:
            errors.append(f"{name}: input.credential is not an object")
    sources = inp.get("sources")
    if sources is not None:
        if not isinstance(sources, list):
            errors.append(f"{name}: input.sources is not an array")
        else:
            for i, src in enumerate(sources):
                if isinstance(src, dict):
                    out.append((f"input.sources[{i}]", src))
                else:
                    errors.append(f"{name}: input.sources[{i}] is not an object")
    return out


def validate_carriers(name: str, vector: dict, validators) -> int:
    """Validates each CARRIER_SCHEMAS carrier the vector's input holds and
    returns how many it validated."""
    checked = 0
    inp = vector.get("input") or {}
    for carrier, ref in CARRIER_SCHEMAS.items():
        if carrier not in inp:
            continue
        fixture = inp[carrier]
        if not isinstance(fixture, dict):
            errors.append(f"{name}: input.{carrier} is not an object")
            continue
        for err in validators[ref].iter_errors(fixture):
            where = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"{name}: input.{carrier} vs {ref}: at {where}: {err.message}")
        checked += 1
    return checked


def validate_vectors(rule_schemas, validators) -> int:
    checked = 0
    for path in sorted((ROOT / "vectors").glob("*.json")):
        try:
            v = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: JSON parse error: {e}")
            continue
        if not is_successful(v.get("expect")):
            continue
        if str(v.get("rule", "")).startswith(CARRIER_RULE_PREFIX):
            checked += validate_carriers(path.name, v, validators)
        refs = rule_schemas.get(v.get("rule"), [])
        if not refs:
            continue
        fixtures = fixtures_of(path.name, v)
        if not fixtures:
            errors.append(
                f"{path.name}: successful vector of a schema-referencing rule "
                "carries no credential fixture (coverage would silently drop)"
            )
            continue
        for ref in refs:
            validator = validators.get(ref)
            if validator is None:
                errors.append(f"{path.name}: rule references unknown schema {ref}")
                continue
            for label, fixture in fixtures:
                for err in validator.iter_errors(fixture):
                    where = "/".join(str(p) for p in err.absolute_path) or "(root)"
                    errors.append(
                        f"{path.name}: {label} vs {ref}: at {where}: {err.message}"
                    )
                checked += 1
    return checked


def required_deletion_mutants(schema: dict, fixture: dict):
    """Yield (description, mutant) for each deletion of a required member at
    the top level and one level down (objects only)."""
    for member in schema.get("required", []):
        m = copy.deepcopy(fixture)
        m.pop(member, None)
        yield f"missing {member}", m
    props = schema.get("properties", {})
    for prop, sub in props.items():
        subreq = sub.get("required")
        if not subreq or not isinstance(fixture.get(prop), dict):
            continue
        for member in subreq:
            m = copy.deepcopy(fixture)
            m[prop].pop(member, None)
            yield f"missing {prop}.{member}", m


def synthetic_negative_checks(validators) -> int:
    checked = 0
    for schema_name, (vec_id, fixture_path) in GOOD_FIXTURES.items():
        validator = validators.get(schema_name)
        vec_file = ROOT / "vectors" / f"{vec_id}.json"
        if validator is None or not vec_file.exists():
            errors.append(f"negative-checks: missing {schema_name} or {vec_id}")
            continue
        v = json.loads(vec_file.read_text())
        fixture = v
        for key in fixture_path.split("."):
            fixture = fixture[key]
        if list(validator.iter_errors(fixture)):
            errors.append(
                f"negative-checks: good fixture {vec_id} does not validate "
                f"against {schema_name} — cannot derive mutants"
            )
            continue
        schema = json.loads((ROOT / "schemas" / schema_name).read_text())
        for desc, mutant in required_deletion_mutants(schema, fixture):
            if not list(validator.iter_errors(mutant)):
                errors.append(
                    f"negative-checks: {schema_name}: mutant '{desc}' PASSED — "
                    "the schema no longer enforces that required member"
                )
            checked += 1
    return checked


def member_checks(validators) -> int:
    """Adds an unknown member at each MEMBER_CHECKS path of the schema's
    known-good fixture: refused where the object is exact, kept where open."""
    checked = 0
    for schema_name, paths in MEMBER_CHECKS.items():
        vec_id, fixture_path = GOOD_FIXTURES[schema_name]
        v = json.loads((ROOT / "vectors" / f"{vec_id}.json").read_text())
        fixture = v
        for key in fixture_path.split("."):
            fixture = fixture[key]
        validator = validators[schema_name]
        for kind in ("exact", "open"):
            for dotted in paths[kind]:
                mutant = copy.deepcopy(fixture)
                node = mutant
                for key in filter(None, dotted.split(".")):
                    node = node[key]
                node[UNKNOWN_MEMBER] = "x"
                refused = bool(list(validator.iter_errors(mutant)))
                if kind == "exact" and not refused:
                    errors.append(f"member-checks: {schema_name}: an unknown member at '{dotted}' PASSED, but that object is exact")
                if kind == "open" and refused:
                    errors.append(f"member-checks: {schema_name}: an unknown member at '{dotted or '(root)'}' is refused, but that object is open")
                checked += 1
    return checked


def main() -> int:
    rule_schemas = load_rule_schemas()
    validators = load_validators()
    checked = validate_vectors(rule_schemas, validators)
    negatives = synthetic_negative_checks(validators)
    members = member_checks(validators)

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        print(f"\n{len(errors)} error(s)")
        return 1
    print(
        f"OK — {checked} fixture/schema validations green, "
        f"{negatives} synthetic negative checks green, "
        f"{members} member checks green"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
