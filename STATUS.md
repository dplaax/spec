# STATUS — draft の現状と取り込み台帳

> この repo は dPLaaX protocol の normative spec の draft。Paper 04 §3.7 が指す
> `dpfp-spec/protocols` に相当する正本がここに育つ。
> 本ファイルは **未転記の規範的内容がどこに散在しているかの台帳** と
> **docs/ への取り込みマッピング**。spec への転記が完了した行から消していく。
> spec 本文が安定したら本ファイルは削除する（恒久ドキュメントではない）。

## 現状宣言

- docs/ は skeleton のみ（全セクション空）。normative 内容は下記ソースに分散したまま。
- 名称整理: 論文上の protocol 名は **DPFP**、wire の名前空間は **dplaax**
  （proto `dplaax.*.v1`、`did:dplaax`、JSON-LD context）。spec 本文でこの対応を最初に固定すること。
- 完了条件は Paper 04 §8.1 の pre-1.0 正規化 (a)–(d)。

## Source 台帳（転記元 → 転記先）

### 1. provin.oss (branch `poc`) — wire profile invariant の現行 SoT

コードコメント / README に契約として焼き込み済み。spec 言語（MUST/SHOULD/MAY）への
書き起こしが必要:

| 内容 | 現在の所在 | 転記先 |
|---|---|---|
| トリガー規則（chain 保持 iff conformant 前イベント 1 件、batch-of-1 規則、fan-out 許容） | `pipeline/README.md` | docs/4.specification |
| audit-reachable conformance class（`derived_from` / `source_root` / `source_root_canonical`、監査属性 ≠ 親リンク、emit は config 駆動、deployment profile で MUST 化可） | `pipeline/originsource/README.md`、`packages/vc/origin.go` | docs/4.specification（conformance class 節を新設） |
| source_root 構築手順（RFC 6962 + multihash: leaf SHA-256(0x00‖canon(VC))、content hash 昇順 sort、odd leaf 昇格、空集合 = SHA-256("")、f1220 encode） | `packages/vc/origin.go`（実装 + テスト済み） | docs/4.specification |
| equality property と fail-closed 規則（derived_from 配列内重複 / unknown canonicalization / chain 保持 VC 上の commitment 共存 → 拒否。同一 issuer 複数 source は合法、不完全性検出は issuer 粒度） | `packages/vc/origin.go` `VerifyOriginCommitment` | docs/4.specification |
| JCS 規約 + 意図的逸脱（json.Number の 64bit 整数リテラル verbatim emit — >2^53 精度保持。U+2028/29 raw、ES6 number 形式） | `packages/canon/jcs/jcs.go` package doc | docs/4.specification（Paper 04 §8.1 (a)） |
| StrictDecoder 規則（duplicate-key / trailing-data / invalid-Unicode・unpaired surrogate の fail-closed） | `packages/canon/strict.go` | docs/4.specification |
| body-as-SoT、previousCredential content-hash 形式、proof の as-received 忠実性（raw map 保持） | `packages/vc/credential.go`、`packages/vc/README.md` | docs/4.specification |
| 検証 3 規範軸 + 3 状態 confidence（failed ⊏ indeterminate ⊏ verified、最弱リンク）、lifecycle registry（proof.created キー、tlog 背面） | `packages/vc/confidence.go` / `lifecycle.go` / `verifier.go` | docs/4.specification |
| 永続 VC ストア前提（audit-reachable 時）と source 取得経路（commitment は root + issuer set のみ — 所在特定は wire 外、ingress store 経由） | `network/README.md`、`vcresolver/store.go` | docs/5.technical_concerns |

### 2. Paper 04 (y1o1.paper.data-pipeline, branch `poc`, 未公開)

- ch3 §3.4: Part I/II の構造、Q1–Q5（deliberate evolutions）。**spec の章構成はここに従う**。
- ch3 §3.4 Q5: audit-reachable class の動機・Paper 01 §4.8 整合の論証 — spec の
  rationale 節にそのまま使える。
- ch8 §8.1 (a)–(d): pre-1.0 正規化 backlog（= 本 repo の完了条件）。
- ch8 §8.2 (e): conformance test suite の class 軸 — reference vector の要件定義。

### 3. dplaas.oss — ⚠ 廃棄前に salvage 必須

- `docs/concepts/provenance.md` / `.ja.md` の「Origin Source VC のフィールド」節:
  `source_root` 構築手順・equality property・boundary translation precondition
  （外部 ecosystem VC は leaf に含めない）・外界 lookup の除外、の **元規範記述**。
  provin.oss / Paper 04 に大半は移植済みだが、廃棄前に差分がないか突合すること。
- L1/L2/L3 trust model 階層（同 doc §1）— L2 = audit reachability の定義元。
  docs/1.concept または 2.principal_and_approach へ。

### 4. 未着手・未決

- conformance vector の実体（provin.oss のテストを seed にできるが、spec 起点で
  書き直す — Paper 04 §8.2 の規律: 実装の癖を encode しない）。
- Part I（Federation Primitives: Chain / VCResolver / Schema Registry / Signer
  abstraction）の spec text — Paper 04 §3.3 が下敷き。
- 監査用列挙 API（issuer / ingress set でのクエリ面）— サービス API 側、未設計。
- JSON-LD context 文書の実体（`https://poc.dplaax.io/vc/v1`）— provin.oss
  `packages/vc/contexts/` も空。spec とどちらが先に持つか未決。

## docs/ セクションへの大まかな対応

| docs/ | 入るもの |
|---|---|
| 1.concept | trust model 階層（L1/L2/L3）、DPFP/dplaax の名称対応 |
| 2.principal_and_approach | 線形不変・判定可能性 over 賢さ・fail-closed・Paper 01 §4.8 整合 |
| 3.architecture | Part I/II 2 層構造、component type catalog |
| 4.specification | wire invariant 全部（上表）、conformance class、conformance vector |
| 5.technical_concerns | 永続化・遡及監査・omission の限界（integrity ≠ completeness） |
| 6.components | 参照実装（provin）との対応、profile choices |
