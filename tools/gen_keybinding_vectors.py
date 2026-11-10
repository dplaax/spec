#!/usr/bin/env python3
"""Regenerate vectors/keybinding-0{01..43}.json from the rule text.

Run: python3 tools/gen_keybinding_vectors.py [--check]

  (no flag)  rewrite the vector files
  --check    recompute and diff against what is committed (non-zero exit if a
             vector no longer matches its derivation)

Each vector is a scenario with one defect against a well-formed baseline (or
none, for an accept vector), and its expected result is the one the rule the
vector names gives for that defect. The content hash of
keybinding.status-list.content-hash is computed here from the rule text alone:

  content hash = "sha256:" + hex(sha256(RFC8785(list minus proof, with
                 credentialSubject.encodedList = "sha256:" + hex(sha256(bits)))))

An implementation must then agree with it. keybinding-015 and -016 hash the
list provin.oss's keybinding tests pin (knownHash), compressed by two gzip
writers (Go 1.26.8 and Go 1.27.1): the same bits, other bytes.

WHY json.dumps IS AN RFC 8785 CANONICALIZER FOR WHAT IS HASHED HERE. The list
body carries no JSON number, every key is ASCII (so sorting by code point is
sorting by UTF-16 code unit, RFC 8785 3.2.3), and no string needs an escape
beyond the forms both agree on. Adding a number or a non-BMP key to a list
invalidates this shortcut. The anchor and verifier carriers hold numbers but
are never hashed.

ENCODED LISTS. Lists other than the two pinned encodings are compressed here
with gzip at mtime 0. Another zlib may write other bytes for the same bits,
which is the point of the content hash, so --check compares an encodedList by
the bits it expands to, and a rewrite keeps a committed encoding whose bits
are unchanged.
"""
import argparse
import base64
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "vectors"

ISSUER = "did:dplaax:poc.dplaax.dev:org:acme"
OTHER = "did:dplaax:poc.dplaax.dev:org:other"
AUDIENCE = "did:dplaax:poc.dplaax.dev:org:bank"
LIST_ID = ISSUER + "#key-binding-status-list"
ENTRIES = 131072  # the W3C Bitstring Status List minimum, 16 KiB of bits

# The encodedLists provin.oss's tests pin for a list of ENTRIES marked at 3
# and 131071, as Go 1.26.8's and Go 1.27.1's gzip write them.
GO126 = "uH4sIAAAAAAAA_-zAMQEAAAgCMG1A_7TE4NlyAAAAAAAAAAAAAAAAAAAAwNg3AAD__-xSDbMAQAAA"
GO127 = "uH4sIAAAAAAAA_-zAMQEAAAgCMG1A_7TE4NlyAAAAAAAAAAAAAAAAAAAAwNh3AOxSDbMAQAAA"
BASE_MARKS = (3, 131071)

V2 = "https://www.w3.org/ns/credentials/v2"
DPLAAX_V1 = "https://dplaax.dev/vc/v1"
UNDEFINED_TERMS = "https://www.w3.org/ns/credentials/undefined-terms/v2"

# RFC 8037 A.2's Ed25519 public key.
JWK = {"kty": "OKP", "crv": "Ed25519", "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"}

PLACEHOLDER = "z5fixture0value0not0a0real0signature0fixture0value0not0real00"

ANCHOR = {
    "issuer": ISSUER,
    "issuance_keys": [ISSUER + "#issuer"],
    "max_validity_seconds": 172800,
    "max_status_age_seconds": 7200,
}
SKEW = 60


def t(hms: str, day: int = 6) -> str:
    return f"2026-11-{day:02d}T{hms}Z"


def rfc8785(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def bits_of(marks) -> bytes:
    b = bytearray(ENTRIES // 8)
    for i in marks:
        b[i // 8] |= 0x80 >> (i % 8)
    return bytes(b)


def expand(encoded: str) -> bytes:
    raw = base64.urlsafe_b64decode(encoded[1:] + "=" * (-len(encoded[1:]) % 4))
    return gzip.decompress(raw)


def encode(marks) -> str:
    bits = bits_of(marks)
    if bits == expand(GO126):
        return GO126
    gz = gzip.compress(bits, compresslevel=9, mtime=0)
    return "u" + base64.urlsafe_b64encode(gz).rstrip(b"=").decode()


def proof(vm: str, created: str) -> dict:
    return {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "created": created,
        "verificationMethod": vm,
        "proofPurpose": "assertionMethod",
        "proofValue": PLACEHOLDER,
    }


def status_list(valid_from: str, valid_until: str, marks=BASE_MARKS, *, issuer=ISSUER,
                list_id=LIST_ID, encoded=None, vm=None, extra=False) -> dict:
    out = {
        "@context": ["https://www.w3.org/ns/credentials/v2"],
        "type": ["VerifiableCredential", "BitstringStatusListCredential"],
        "id": list_id,
        "issuer": issuer,
        "validFrom": valid_from,
        "validUntil": valid_until,
        "credentialSubject": {
            "id": list_id + "-list",
            "type": "BitstringStatusList",
            "statusPurpose": "revocation",
            "encodedList": encoded or encode(marks),
        },
        "proof": proof(vm or issuer + "#issuer", valid_from),
    }
    if extra:
        out["name"] = "Key bindings of ACME staff"
        out["credentialSubject"]["description"] = "Revocations of ACME staff key bindings"
    return out


def binding(*, issuer=ISSUER, valid_from=t("00:00:00"), valid_until=t("00:00:00", 7),
            audience=AUDIENCE, index="7", list_id=None, vm=None, extra=None) -> dict:
    out = {
        "@context": ["https://www.w3.org/ns/credentials/v2", "https://dplaax.dev/vc/v1"],
        "type": ["VerifiableCredential", "KeyBindingCredential"],
        "issuer": issuer,
        "validFrom": valid_from,
        "validUntil": valid_until,
        "credentialStatus": {
            "type": "BitstringStatusListEntry",
            "statusPurpose": "revocation",
            "statusListIndex": index,
            "statusListCredential": list_id or issuer + "#key-binding-status-list",
        },
        "credentialSubject": {
            "id": "urn:acme:staff:42",
            "kind": "staff",
            "roles": ["checker"],
            "audience": audience,
            "keyClass": "passkey",
            "key": {"keyId": "credential-1", "publicKeyJwk": dict(JWK)},
        },
        "proof": proof(vm or issuer + "#issuer", valid_from),
    }
    if extra:
        # members credentials v2 defines (schema.org's name), not the catalog
        out["name"] = "Staff key of ACME"
        out["credentialSubject"]["name"] = "Staff 42"
    if extra == "undefined":
        # a member no context defines
        out["credentialSubject"]["displayName"] = "Staff 42"
    return out


def edited(cred: dict, edit) -> dict:
    """A copy of cred that edit has changed."""
    out = copy.deepcopy(cred)
    edit(out)
    return out


def content_hash(lst: dict) -> str:
    view = copy.deepcopy(lst)
    del view["proof"]
    bits = expand(view["credentialSubject"]["encodedList"])
    view["credentialSubject"]["encodedList"] = "sha256:" + hashlib.sha256(bits).hexdigest()
    return "sha256:" + hashlib.sha256(rfc8785(view)).hexdigest()


# The baseline: a binding valid from 2026-11-06T00:00:00Z for a day, decided
# at 01:00:00Z, under a list of the issuer valid from 00:59:00Z for an hour
# that marks 3 and 131071 (not the binding's 7).
AT = t("01:00:00")
LIST_FROM, LIST_UNTIL = t("00:59:00"), t("01:59:00")


def verifier() -> dict:
    return {"audience": AUDIENCE, "skew_seconds": SKEW}


def binding_case(cred, *, at=AT, held=None) -> dict:
    return {
        "credential": cred,
        "status_list": held or status_list(LIST_FROM, LIST_UNTIL),
        "anchor": copy.deepcopy(ANCHOR),
        "verifier": verifier(),
        "at": at,
    }


def list_case(cred, *, held=None, at=AT) -> dict:
    out = {"credential": cred}
    if held is not None:
        out["held"] = held
    out.update({"anchor": copy.deepcopy(ANCHOR), "verifier": {"skew_seconds": SKEW}, "at": at})
    return out


def rewound(reason: str) -> dict:
    return {"result": "reject", "reason": reason}


def build() -> list[dict]:
    v = []

    def add(rule, description, inp, expect):
        v.append({
            "id": f"keybinding-{len(v) + 1:03d}",
            "rule": rule,
            "description": description,
            "input": inp,
            "expect": expect,
        })

    # keybinding.shape
    add("keybinding.shape",
        "A well-formed key binding of a trusted issuer, for this relying party, valid now and unmarked in the issuer's current list, is accepted",
        binding_case(binding()), "accept")
    add("keybinding.shape",
        "A key binding whose validUntil equals its validFrom is rejected",
        binding_case(binding(valid_until=t("00:00:00")), at=t("00:00:30"),
                     held=status_list(t("23:59:00", 5), t("00:59:00"))),
        "reject")
    # keybinding.issuer
    add("keybinding.issuer",
        "A key binding signed with a key of its issuer that the trust anchor does not name as an issuance key is rejected",
        binding_case(binding(vm=ISSUER + "#signing")), "reject")
    add("keybinding.issuer",
        "A key binding of an issuer no trust anchor names, signed with that issuer's own key, is rejected",
        binding_case(binding(issuer=OTHER)), "reject")
    # keybinding.validity
    add("keybinding.validity",
        "A key binding decided at its validUntil plus the clock skew is rejected",
        binding_case(binding(), at=t("00:01:00", 7),
                     held=status_list(t("00:00:00", 7), t("01:00:00", 7))),
        "reject")
    add("keybinding.validity",
        "A key binding valid for one second longer than its trust anchor allows the issuer is rejected",
        binding_case(binding(valid_until=t("00:00:01", 8))), "reject")
    # keybinding.audience
    add("keybinding.audience",
        "A key binding for another relying party is rejected",
        binding_case(binding(audience=OTHER)), "reject")
    # keybinding.status.entry
    add("keybinding.status.entry",
        "A key binding whose statusListIndex has a leading zero is rejected",
        binding_case(binding(index="07")), "reject")
    add("keybinding.status.entry",
        "A key binding whose entry the issuer's current list marks is rejected",
        binding_case(binding(), held=status_list(LIST_FROM, LIST_UNTIL, (3, 7, 131071))), "reject")
    add("keybinding.status.entry",
        "A key binding naming a list of its issuer other than the one the verifier holds is rejected",
        binding_case(binding(list_id=ISSUER + "#another-list")), "reject")
    # keybinding.status-list.id
    add("keybinding.status-list.id",
        "A current revocation list of a trusted issuer, whose id is a DID URL of that issuer, is accepted",
        list_case(status_list(LIST_FROM, LIST_UNTIL)), "accept")
    add("keybinding.status-list.id",
        "A revocation list whose id is a relative #fragment is rejected",
        list_case(status_list(LIST_FROM, LIST_UNTIL, list_id="#key-binding-status-list")), "reject")
    add("keybinding.status-list.id",
        "A revocation list whose id is a URL of another DID than its issuer is rejected",
        list_case(status_list(LIST_FROM, LIST_UNTIL, list_id=OTHER + "#key-binding-status-list")), "reject")
    # keybinding.status-list.period
    add("keybinding.status-list.period",
        "A revocation list whose validUntil equals its validFrom is rejected when read",
        list_case(status_list(t("01:00:30"), t("01:00:30"))), "reject")
    # keybinding.status-list.content-hash
    pinned = status_list(LIST_FROM, LIST_UNTIL, encoded=GO126)
    add("keybinding.status-list.content-hash",
        "A revocation list's content hash is the SHA-256 of its RFC 8785 form without the proof, with encodedList replaced by the digest of the expanded bits",
        {"credential": pinned}, {"contentHash": content_hash(pinned)})
    other = status_list(LIST_FROM, LIST_UNTIL, encoded=GO127)
    add("keybinding.status-list.content-hash",
        "The same revocation list compressed by another gzip writer has the same content hash",
        {"credential": other}, {"contentHash": content_hash(other)})
    # keybinding.status-list.monotonic
    earlier = status_list(t("00:29:00"), t("01:29:00"))
    add("keybinding.status-list.monotonic",
        "A later revocation list that keeps every entry the held list marks, and marks one more, replaces it",
        list_case(status_list(LIST_FROM, LIST_UNTIL, (3, 4, 131071)), held=earlier), "accept")
    add("keybinding.status-list.monotonic",
        "The held revocation list compressed otherwise (the same validFrom and content hash) is the held list again, not a step back",
        list_case(status_list(LIST_FROM, LIST_UNTIL, encoded=GO127),
                  held=status_list(LIST_FROM, LIST_UNTIL, encoded=GO126)),
        "accept")
    add("keybinding.status-list.monotonic",
        "A revocation list earlier than the held one is rejected as status-list-rewound",
        list_case(earlier, held=status_list(LIST_FROM, LIST_UNTIL)), rewound("status-list-rewound"))
    add("keybinding.status-list.monotonic",
        "A revocation list of the held one's validFrom with another content hash is rejected as status-list-rewound",
        list_case(status_list(LIST_FROM, LIST_UNTIL, (3, 4, 131071)), held=status_list(LIST_FROM, LIST_UNTIL)),
        rewound("status-list-rewound"))
    add("keybinding.status-list.monotonic",
        "A later revocation list that unmarks an entry the held list marks is rejected as status-list-revocation-cleared",
        list_case(status_list(LIST_FROM, LIST_UNTIL, (131071,)), held=earlier),
        rewound("status-list-revocation-cleared"))
    # keybinding.status-list.fresh
    add("keybinding.status-list.fresh",
        "A key binding under a list whose validFrom lies one second further back than its trust anchor allows is rejected",
        binding_case(binding(), held=status_list(t("22:59:59", 5), t("01:59:00"))), "reject")
    add("keybinding.status-list.fresh",
        "A key binding under a list not yet valid at the decision plus the clock skew is rejected",
        binding_case(binding(), held=status_list(t("01:01:01"), t("02:01:01"))), "reject")
    # Members this catalog does not define, at the top level and in
    # credentialSubject (the schemas keep those two open).
    add("keybinding.shape",
        "A key binding carrying members the catalog does not define, at its top level and in credentialSubject, defined by credentials v2, is accepted",
        binding_case(binding(extra=True)), "accept")
    extended = status_list(LIST_FROM, LIST_UNTIL, encoded=GO126, extra=True)
    add("keybinding.status-list.content-hash",
        "A revocation list's content hash covers the members the catalog does not define, as it covers every other member but encodedList's compression",
        {"credential": extended}, {"contentHash": content_hash(extended)})
    # A list is signed under the trust anchor as a binding is.
    add("keybinding.issuer",
        "A revocation list signed with a key of its issuer that the trust anchor does not name as an issuance key is rejected",
        list_case(status_list(LIST_FROM, LIST_UNTIL, vm=ISSUER + "#signing")), "reject")
    add("keybinding.issuer",
        "A revocation list of an issuer no trust anchor names, signed with that issuer's own key, is rejected",
        list_case(status_list(LIST_FROM, LIST_UNTIL, issuer=OTHER, list_id=OTHER + "#key-binding-status-list")),
        "reject")
    # The clock skew and the bounds, on the accepting side.
    add("keybinding.validity",
        "A key binding decided 30 seconds before its validFrom, within the clock skew, is accepted",
        binding_case(binding(valid_from=t("01:00:30"), valid_until=t("01:00:30", 7))), "accept")
    add("keybinding.validity",
        "A key binding decided 59 seconds after its validUntil, within the clock skew, is accepted",
        binding_case(binding(), at=t("00:00:59", 7),
                     held=status_list(t("00:00:00", 7), t("01:00:00", 7))),
        "accept")
    add("keybinding.validity",
        "A key binding valid for exactly the longest its trust anchor allows the issuer is accepted",
        binding_case(binding(valid_until=t("00:00:00", 8))), "accept")
    add("keybinding.status-list.fresh",
        "A key binding under a list valid from 59 seconds after the decision, within the clock skew, is accepted",
        binding_case(binding(), held=status_list(t("01:00:59"), t("02:00:59"))), "accept")
    add("keybinding.status-list.fresh",
        "A key binding under a list whose validFrom is exactly the trust anchor's maximum age before the decision is accepted",
        binding_case(binding(), held=status_list(t("23:00:00", 5), t("01:59:00"))), "accept")
    # The entry and the members kept exact.
    add("keybinding.status.entry",
        "A key binding whose index lies past the end of the issuer's current list is rejected",
        binding_case(binding(index=str(ENTRIES))), "reject")
    add("keybinding.status.entry",
        "A key binding whose credentialStatus carries a statusSize is rejected",
        binding_case(edited(binding(), lambda b: b["credentialStatus"].update(statusSize="1"))), "reject")
    add("keybinding.shape",
        "A key binding whose key carries a member other than keyId and publicKeyJwk is rejected",
        binding_case(edited(binding(), lambda b: b["credentialSubject"]["key"].update(purpose="approval"))),
        "reject")
    add("keybinding.shape",
        "A key binding whose public JWK carries a member other than those its key type has is rejected",
        binding_case(edited(binding(), lambda b: b["credentialSubject"]["key"]["publicKeyJwk"].update(kid="credential-1"))),
        "reject")
    add("keybinding.status-list.fresh",
        "A key binding under a list decided at its validUntil plus the clock skew is rejected",
        binding_case(binding(), held=status_list(t("23:30:00", 5), t("00:59:00"))), "reject")
    # @context: credentials v2 first; a binding also holds dplaax v1; an
    # issuer that uses undefined members adds undefined-terms/v2 last.
    def contexts(*urls):
        return lambda c: c.update({"@context": list(urls)})
    add("keybinding.shape",
        "A key binding with a member no context defines, and the undefined-terms context last in its @context, is accepted",
        binding_case(edited(binding(extra="undefined"), contexts(V2, DPLAAX_V1, UNDEFINED_TERMS))), "accept")
    add("keybinding.status-list.id",
        "A revocation list with a member no context defines, and the undefined-terms context last in its @context, is accepted",
        list_case(edited(status_list(LIST_FROM, LIST_UNTIL),
                         lambda c: (c["credentialSubject"].update(issuerNote="kept for audit"),
                                    c.update({"@context": [V2, UNDEFINED_TERMS]})))),
        "accept")
    add("keybinding.shape",
        "A key binding whose @context does not open with the credentials v2 context is rejected",
        binding_case(edited(binding(), contexts(DPLAAX_V1, V2))), "reject")
    add("keybinding.shape",
        "A key binding whose @context does not hold the dplaax context is rejected",
        binding_case(edited(binding(), contexts(V2, UNDEFINED_TERMS))), "reject")
    add("keybinding.status-list.id",
        "A revocation list whose @context does not open with the credentials v2 context is rejected",
        list_case(edited(status_list(LIST_FROM, LIST_UNTIL), contexts(UNDEFINED_TERMS, V2))), "reject")
    # A list not yet valid when it is taken is not held.
    add("keybinding.status-list.fresh",
        "A revocation list valid only from after the time it is taken plus the clock skew is not held",
        list_case(status_list(t("01:01:01"), t("02:01:01"))), "reject")
    return v


PINNED = {GO126, GO127}


def normalized(vector: dict) -> dict:
    """The vector with every encodedList replaced by the digest of its bits,
    but for the two pinned encodings, which are compared as written."""
    out = copy.deepcopy(vector)

    def walk(x):
        if isinstance(x, dict):
            for k, val in x.items():
                if k == "encodedList" and isinstance(val, str) and val not in PINNED:
                    x[k] = "bits:" + hashlib.sha256(expand(val)).hexdigest()
                else:
                    walk(val)
        elif isinstance(x, list):
            for item in x:
                walk(item)

    walk(out)
    return out


def keep_committed_encodings(new: dict, old: dict) -> dict:
    """new, with each encodedList whose bits equal old's at the same place
    spelled as old spells it."""
    if isinstance(new, dict) and isinstance(old, dict):
        for k, val in new.items():
            if k == "encodedList" and isinstance(val, str) and isinstance(old.get(k), str):
                if val not in PINNED and expand(val) == expand(old[k]):
                    new[k] = old[k]
            elif k in old:
                keep_committed_encodings(val, old[k])
    elif isinstance(new, list) and isinstance(old, list):
        for a, b in zip(new, old):
            keep_committed_encodings(a, b)
    return new


def dump(vector: dict) -> str:
    return json.dumps(vector, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="diff against the committed vectors instead of rewriting")
    args = ap.parse_args()
    bad = 0
    for vector in build():
        path = VECTORS / f"{vector['id']}.json"
        old = json.loads(path.read_text()) if path.exists() else None
        if args.check:
            if old is None or normalized(old) != normalized(vector):
                print(f"FAIL {path.name}: does not match its derivation")
                bad += 1
            continue
        if old is not None:
            vector = keep_committed_encodings(vector, old)
        path.write_text(dump(vector))
    if args.check:
        print("OK — keybinding vectors match their derivation" if not bad else f"\n{bad} vector(s) differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
