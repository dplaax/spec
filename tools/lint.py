#!/usr/bin/env python3
"""dplaax spec lint — SoT 規律の機械的強制。

チェック内容 (README.md「lint」節が人間向け記述):
  1. RFC 2119 規範語は rules/*.yaml の statement 内にのみ出現できる
     (markdown 全文と rule の notes では fail。STATUS.md は一時台帳のため対象外)
  2. rule id の全ファイル横断 uniqueness と形式
  3. uses / schemas / vectors 参照の解決
  4. status / class の enum
  5. statement: status が todo 以外なら必須・256 文字以内・規範語を 1 つ以上含む
  6. vector ファイルの rule 逆参照の解決
  7. rule↔vector の双方向一致 (vector が参照する rule は、その vector を列挙する)
  8. vector カバレッジ床: VECTOR_REQUIRED_FILES の family は全 rule が vector を持つ
  9. branch の context (contexts/branches/、contexts/README.md「Branch contexts」):
     path が <base>/<feature>/<YYYYMMDDHHmm>.jsonld で stamp は UTC の時刻、
     base の contexts/<base>.jsonld がある、SHA256SUMS が file と一対一で一致、
     base の語を定義し直さない、branch の中は stamp の順に足すだけ、同じ base の
     branch の間で同じ名前は同じ定義。環境変数 DPLAAX_BASE_REF があれば、その
     ref の SHA256SUMS の行 (出した snapshot) が変わらず残っている
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RFC2119 = re.compile(r"\b(?:MUST|SHALL|SHOULD|REQUIRED|RECOMMENDED|OPTIONAL|MAY)\b")
ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9-]+){1,3}$")
STATUSES = {"todo", "draft", "stable"}
CLASSES = {"core", "audit-reachable", "effect-gated"}
MD_EXCLUDE = {"STATUS.md"}
# 0.1 タグの vector カバレッジ床 (VERSIONING.md「0.1 タグの条件」と対)。
# 列挙された family は全 rule が 1 本以上の vector を持たなければならない。
# family の追加 = 0.2 に向けたカバレッジ拡大 (VERSIONING.md 側と同期して育てる)。
VECTOR_REQUIRED_FILES = {
    "chain.yaml",
    "credential.yaml",
    "delegation.yaml",
    "process.yaml",
    "registry.yaml",
    "resolver.yaml",
    "transfer.yaml",
}

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load_rules() -> dict[str, dict]:
    rules: dict[str, dict] = {}
    for path in sorted((ROOT / "rules").glob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            err(f"{path.name}: YAML parse error: {e}")
            continue
        for entry in (doc or {}).get("rules") or []:
            rid = entry.get("id")
            if not rid:
                err(f"{path.name}: id のない entry")
                continue
            if not ID_RE.match(rid):
                err(f"{path.name}: id 形式不正: {rid}")
            if rid in rules:
                err(f"{path.name}: id 重複: {rid} (既出: {rules[rid]['_file']})")
                continue
            entry["_file"] = path.name
            rules[rid] = entry
    return rules


def check_rules(rules: dict[str, dict]) -> None:
    vector_files = {p.stem for p in (ROOT / "vectors").glob("*.json")}
    schema_files = {p.name for p in (ROOT / "schemas").glob("*.json")}
    for rid, e in rules.items():
        where = f"{e['_file']}:{rid}"
        if e.get("status") not in STATUSES:
            err(f"{where}: status 不正: {e.get('status')}")
        if e.get("class") not in CLASSES:
            err(f"{where}: class 不正: {e.get('class')}")
        stmt = e.get("statement")
        if e.get("status") != "todo":
            if not isinstance(stmt, str) or not stmt.strip():
                err(f"{where}: status={e.get('status')} なのに statement がない")
            else:
                flat = " ".join(stmt.split())
                if len(flat) > 256:
                    err(f"{where}: statement が 256 文字超 ({len(flat)})")
                if not RFC2119.search(flat):
                    err(f"{where}: statement に規範語がない")
        notes = e.get("notes") or ""
        if RFC2119.search(notes):
            err(f"{where}: notes に規範語 (non-normative field での再表現は禁止)")
        for ref in e.get("uses") or []:
            if ref not in rules:
                err(f"{where}: uses が未解決: {ref}")
        for ref in e.get("schemas") or []:
            if ref not in schema_files:
                err(f"{where}: schemas が未解決: {ref}")
        for ref in e.get("vectors") or []:
            if ref not in vector_files:
                err(f"{where}: vectors が未解決: {ref}")
        if e["_file"] in VECTOR_REQUIRED_FILES and not e.get("vectors"):
            err(f"{where}: vector カバレッジ床の family なのに vectors が空")


def check_vectors(rules: dict[str, dict]) -> None:
    for path in sorted((ROOT / "vectors").glob("*.json")):
        try:
            v = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            err(f"vectors/{path.name}: JSON parse error: {e}")
            continue
        if v.get("id") != path.stem:
            err(f"vectors/{path.name}: id とファイル名の不一致: {v.get('id')}")
        rid = v.get("rule")
        if rid not in rules:
            err(f"vectors/{path.name}: rule が未解決: {rid}")
        elif path.stem not in (rules[rid].get("vectors") or []):
            err(f"vectors/{path.name}: rule {rid} の vectors に未登録 (双方向参照の破れ)")
        if "input" not in v or "expect" not in v:
            err(f"vectors/{path.name}: input / expect が必須")


def check_markdown() -> None:
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if rel.name in MD_EXCLUDE or rel.parts[0] in {".git", "tools"}:
            continue
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if RFC2119.search(line):
                err(f"{rel}:{n}: markdown に規範語 (規範は rules/ の statement のみ)")


BRANCH_PATH_RE = re.compile(r"^(v[0-9]+)/([a-z0-9-]+)/([0-9]{12})\.jsonld$")
SUMS_LINE_RE = re.compile(r"^([0-9a-f]{64})  (v[0-9]+/[a-z0-9-]+/[0-9]{12})$")


def context_terms(path: Path) -> dict:
    """Term definitions of a context document: its @context object without
    the keywords."""
    ctx = json.loads(path.read_text()).get("@context")
    if not isinstance(ctx, dict):
        raise ValueError("@context が object でない")
    return {k: v for k, v in ctx.items() if not k.startswith("@")}


def check_branch_contexts() -> None:
    branches = ROOT / "contexts" / "branches"
    if not branches.is_dir():
        return
    where = "contexts/branches"
    snapshots = {}  # (base, feature) -> [(stamp, served path, terms)]
    served = {}  # served path -> sha256 of the file
    for path in sorted(branches.rglob("*")):
        if path.is_dir() or path.name == "SHA256SUMS":
            continue
        rel = path.relative_to(branches).as_posix()
        m = BRANCH_PATH_RE.match(rel)
        if not m:
            err(f"{where}/{rel}: path が <base>/<feature>/<YYYYMMDDHHmm>.jsonld でない")
            continue
        base, feature, stamp = m.groups()
        try:
            datetime.strptime(stamp, "%Y%m%d%H%M")
        except ValueError:
            err(f"{where}/{rel}: stamp {stamp} が UTC の時刻 YYYYMMDDHHmm でない")
            continue
        base_path = ROOT / "contexts" / f"{base}.jsonld"
        if not base_path.is_file():
            err(f"{where}/{rel}: base の contexts/{base}.jsonld が無い")
            continue
        try:
            terms = context_terms(path)
            base_terms = context_terms(base_path)
        except (ValueError, json.JSONDecodeError) as e:
            err(f"{where}/{rel}: {e}")
            continue
        for name in sorted(set(terms) & set(base_terms)):
            err(f"{where}/{rel}: 語 {name} は base の contexts/{base}.jsonld が定義する (branch は base を定義し直さない)")
        served[rel[: -len(".jsonld")]] = hashlib.sha256(path.read_bytes()).hexdigest()
        snapshots.setdefault((base, feature), []).append((stamp, rel, terms))
    # SHA256SUMS: one line per snapshot, the served path and its sha256
    sums_path = branches / "SHA256SUMS"
    pinned = {}
    lines = sums_path.read_text().splitlines() if sums_path.is_file() else []
    for n, line in enumerate(lines, 1):
        m = SUMS_LINE_RE.match(line)
        if not m:
            err(f"{where}/SHA256SUMS:{n}: 行が '<sha256>  <base>/<feature>/<stamp>' でない")
            continue
        digest, target = m.groups()
        if target in pinned:
            err(f"{where}/SHA256SUMS:{n}: {target} の pin が 2 つある")
        pinned[target] = digest
    for target in sorted(set(served) - set(pinned)):
        err(f"{where}/SHA256SUMS: snapshot {target} の pin が無い")
    for target in sorted(set(pinned) - set(served)):
        err(f"{where}/SHA256SUMS: pin {target} の snapshot が無い")
    for target in sorted(set(served) & set(pinned)):
        if served[target] != pinned[target]:
            err(f"{where}/SHA256SUMS: {target} の sha256 が file と違う")
    # within a branch: add only, in stamp order
    for (base, feature), snaps in sorted(snapshots.items()):
        snaps.sort()
        for (s1, r1, t1), (s2, r2, t2) in zip(snaps, snaps[1:]):
            for name, definition in sorted(t1.items()):
                if name not in t2:
                    err(f"{where}/{r2}: 前の snapshot {s1} の語 {name} が無い (branch の中は足すだけ)")
                elif t2[name] != definition:
                    err(f"{where}/{r2}: 語 {name} の定義が前の snapshot {s1} と違う (branch の中は足すだけ)")
    # across the branches of a base: one definition per name
    seen = {}  # (base, name) -> (feature, definition, where)
    for (base, feature), snaps in sorted(snapshots.items()):
        for stamp, rel, terms in snaps:
            for name, definition in sorted(terms.items()):
                first = seen.setdefault((base, name), (feature, definition, rel))
                if first[0] != feature and first[1] != definition:
                    err(f"{where}/{rel}: 語 {name} の定義が {first[2]} と違う (同じ base の branch の間で同じ名前は同じ定義)")
    # snapshots once shipped stay as they were
    base_ref = os.environ.get("DPLAAX_BASE_REF")
    if base_ref:
        shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{base_ref}:contexts/branches/SHA256SUMS"],
                               capture_output=True, text=True)
        if shown.returncode == 0:
            for line in shown.stdout.splitlines():
                m = SUMS_LINE_RE.match(line)
                if m and pinned.get(m.group(2)) != m.group(1):
                    err(f"{where}/SHA256SUMS: {base_ref} で出した snapshot {m.group(2)} の pin が変わったか消えた (snapshot は凍結)")
        elif "does not exist" not in shown.stderr and "exists on disk, but not in" not in shown.stderr:
            err(f"{where}: DPLAAX_BASE_REF={base_ref} の SHA256SUMS が読めない: {shown.stderr.strip()[:120]}")


def main() -> int:
    rules = load_rules()
    check_rules(rules)
    check_vectors(rules)
    check_markdown()
    check_branch_contexts()
    n_todo = sum(1 for e in rules.values() if e.get("status") == "todo")
    if errors:
        for e in errors:
            print(f"FAIL {e}")
        print(f"\n{len(errors)} error(s)")
        return 1
    print(f"OK — {len(rules)} rules ({n_todo} todo), lint green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
