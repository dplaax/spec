# dPLaaX Specification (draft)

dPLaaX（"data PipeLine as a X"）は、データが組織やシステムの境界を越えるとき、
「誰が、何を受け取り、何を行い、何を渡したか」を境界ごとに改ざん検出可能な形で
記録し、その連なりを第三者が独立に確かめられるようにするプロトコルである
（→ [concept.md](concept.md)）。

> **Status: v0.1 (draft)。** すべての rule は `draft` であり、実装からの
> フィードバックで変わり続ける（→ [VERSIONING.md](VERSIONING.md)）。
> **Public review とコントリビューションを歓迎する** —
> [CONTRIBUTING.md](CONTRIBUTING.md) を参照。ガバナンスはコントリビュータの
> 増加に応じて段階的に整備する（現状: maintainer 裁量、議論は Issue で公開）。

dPLaaX の normative spec。**規範の SoT は次の 3 artifact のみ**であり、散文は規範を持たない。

| artifact | 担う規範 | 形式 |
| --- | --- | --- |
| `rules/` | 挙動・判定の規範（rule catalog） | YAML |
| `schemas/` | wire shape の規範 | JSON Schema 2020-12 |
| `vectors/` | 挙動規範の実体化（conformance vector） | JSON |

markdown（本書、concept.md、GLOSSARY.md 等）はすべて non-normative。規範を再表現せず、rule id を参照する。この分離は `tools/lint.py` が機械的に強制する。

## 読み順

1. [concept.md](concept.md) — なぜ dPLaaX が存在するか（非技術・non-normative）
2. [rules/](rules/) — 規範本体
3. [schemas/](schemas/) / [vectors/](vectors/) — shape と vector
4. [STATUS.md](STATUS.md) — 起草の現状（一時文書、安定後に削除）

## rule catalog の形式

`rules/*.yaml` の各 entry:

| field | 規約 |
| --- | --- |
| `id` | `<domain>.<topic>[.<name>]`。`status: todo` の間は仮 id、`draft` 昇格で凍結 |
| `status` | `todo`（転記前 stub）/ `draft` / `stable` |
| `class` | `core`（既定）/ `audit-reachable`。conformance class の所属 |
| `statement` | 規範文。`draft` 以上で必須、256 文字以内、RFC 2119 の規範語を 1 つ以上含む。1 rule = 1 表現で、他所での再表現は禁止 |
| `uses` | 依存する rule id の列。規範の再掲の代わりに参照する |
| `schemas` / `vectors` | 対応する artifact ファイルへの参照 |
| `notes` | non-normative の補足。規範語の使用は lint が拒否する |
| `source` | 転記元の所在を記す一時 field。転記完了で削除する |

## 横断関心の扱い

- **依存型**（例: credential が canonicalization に依存）— `uses` で参照する。本文を再掲しない。
- **原則型**（fail-closed 等の設計思想）— 規範化しない。vector 化可能な個別規則のみが規範。思想は concept.md / `notes` に non-normative で置く。
- **タクソノミー型**（conformance class 等）— `class` field で表現する。
- **ファイル分割は non-normative** — entry の identity は `id` が担う。entry をファイル間で動かしても規範は不変であり、再シャーディングは pure refactor。

## lint

```bash
python3 tools/lint.py
```

強制内容: 規範語が `rules/*.yaml` の `statement` 以外（markdown 全文・`notes`）に出現したら fail / id の全ファイル横断 uniqueness / `uses`・`schemas`・`vectors` 参照の解決 / `status`・`class` の enum / `statement` の長さ・規範語包含。STATUS.md は一時的な作業台帳のため走査対象外。

rule entry の構造（shape）は `tools/rule.schema.json` が定義し、各 `rules/*.yaml` 先頭の modeline で IDE 検証に束縛されている。内容規律は lint、構造は schema、と分担する。

## バージョニング

→ [VERSIONING.md](VERSIONING.md)
