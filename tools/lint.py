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
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RFC2119 = re.compile(r"\b(?:MUST|SHALL|SHOULD|REQUIRED|RECOMMENDED|OPTIONAL|MAY)\b")
ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9-]+){1,3}$")
STATUSES = {"todo", "draft", "stable"}
CLASSES = {"core", "audit-reachable"}
MD_EXCLUDE = {"STATUS.md"}

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


def check_vectors(rules: dict[str, dict]) -> None:
    for path in sorted((ROOT / "vectors").glob("*.json")):
        try:
            v = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            err(f"vectors/{path.name}: JSON parse error: {e}")
            continue
        if v.get("id") != path.stem:
            err(f"vectors/{path.name}: id とファイル名の不一致: {v.get('id')}")
        if v.get("rule") not in rules:
            err(f"vectors/{path.name}: rule が未解決: {v.get('rule')}")
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


def main() -> int:
    rules = load_rules()
    check_rules(rules)
    check_vectors(rules)
    check_markdown()
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
