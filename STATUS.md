# STATUS — 起草の現状（一時文書）

> 本ファイルは作業台帳であり spec の一部ではない。spec 安定後に削除する。
> tools/lint.py の走査対象外（規範語の引用が許される唯一の markdown）。
> (English) This file is the drafting ledger, kept in Japanese only. It is
> temporary — not part of the spec — and will be deleted once the spec
> stabilizes. The spec itself is English-primary.

## 現状宣言（2026-06-10）

- 構造を rule catalog 方式へ全面改組（rules/ + schemas/ + vectors/、規律は README.md 参照）。
- 旧 6 セクション skeleton（docs/）は削除。旧 Layer 構造での起草蓄積はブランチ
  `drafts/v1_001` / `drafts/v1_002` に保存されている。
- **未転記の規範内容の台帳は、各 rule stub の `source` field に移行した**。
  `status: todo` の entry を grep すれば未転記一覧になる。転記完了で `source` を削除する。
- **statement 転記は 2026-06-11 に完了**（旧 draft + provin.oss からの抽出・統合、todo 残なし）。
  component 領域はチェーン挙動を trigger ベースに統一して転記
  （type ベースの旧規定は置換、各 rule の notes 参照）。全 draft rule は vector 0 本（0.1 条件未達）。
- 名称: 本 repo は dplaax のみを定義する。旧 protocol 名・旧実装名の語彙は spec 本文に
  持ち込まない（実装側の「FirstDrop」は spec では「チェーン起点」と表記）。
- **2026-06-11: origin commitment → source commitment 改組を実施**。旧名がチェーン起点
  専用の概念化を生み、chain-preserving 境界の消費ソース集合を監査不可視にしていた
  （previous-XOR-origin invariant は verifier の MUST にも焼き込まれていた）。
  commitment を previousCredential と直交化し、commit 対象は**全消費分**（trigger
  先行イベント含む）で確定（→ `commitment.scope.all-consumed`、新規 rule）。
  spec 側: rules/origin.yaml → rules/commitment.yaml（id `origin.*` → `commitment.*`、
  7 rule 改名 + 1 rule 新設）。provin.oss 側: OriginCommitment → SourceCommitment、
  Builder/Verifier の XOR 解体、BuildChainPreserving に commitment 引数追加
  （lock-step 変更、build / vet / test green）。wire キー 3 種は中立語彙のため不変。
- **2026-06-11: transformationType → transformationClaim 再構成を実施**（base 語彙の
  解体）。形状（prev × SourceCommitment）は wire パラメタで自明であり、フィールドの
  非冗長な仕事は「情報源についての主張 (claim)」のみ、という 2 軸分離が論拠。
  protocol に残るのは文法（単一 `<namespace>:<label>`、無印値全廃、"+" 結合削除 —
  複合は profile が単一 label で定義）+ 開世界解釈デフォルト（未認識 claim から
  閉世界推論 = 除外推論を引き出さない MUST NOT）のみ。claim の意味（閉/開）は
  profile が釘付けし、**claim は位相を拘束しない**（aggregate-origin 規則は削除、
  位相は chain.trigger.* が単独で決める）。spec 側: `credential.transformation.*`
  4 rules → `credential.claim.*` 3 rules、subject rule 改名、component.yaml 4 箇所。
  provin.oss 側: TransformationClaim 型 + provin claim registry
  （provin:filter / convert / filter-convert / aggregate / enrich / **generate**）、
  wire キー transformationClaim、GLOSSARY。Paper 01 §4.3（ベース語彙 + "+"）との
  意図的乖離を `credential.claim.grammar` notes に記録。
  **generate の incubation draft は転記完了・削除** — claim 再構成により profile 層で
  完結（protocol 変更不要）、「常時 FirstDrop」問題は位相非拘束により解消。

- **2026-06-11: L2 監査モデルの仕分けを確定、audit domain を新設**（rules/audit.yaml、
  57 rules に）。仕分け: 帰責デフォルト規則 = protocol（`audit.attribution.segment` /
  `origin-default`、主体は「帰責計算 (attribution computation)」= GLOSSARY に定義。
  解釈規範を監査ツールの行為規範として規範化）。記録義務（emission stream / 購読記録 /
  ingress 保持の運用義務）= provin profile 側 — publisher/subscriber 語彙の protocol
  輸入を回避するため。第二実装出現時に「転送関係」抽象を設計して 0.x minor で昇格可。
  wireauth / RPC shape / 監査用列挙 API = provin サービス API 側。
  Paper 01 とは無衝突を原文突合で確認（論文は attestation scope に自己限定しており、
  帰責は意図的な拡張）。~~典拠アンカーは Paper 04 に明文化する~~ — **2026-06-11 解決**:
  Paper 04 ch3 §3.4「Responsibility attribution (default rule)」段落として明文化済み
  （en/ja、commitment-does-not-move-default を含む）。
  dplaas.oss の provenance.md 突合は帰責規則の目的では不要と user 判断（典拠ラインは
  Paper 01 + Paper 04 に一本化）。
  **2026-06-16 訂正 — Paper 04 を SoT から外す**: Paper 04 は旧 dplaas 設計を継承した
  in-progress 論文であり SoT としない。attribution 規則の典拠は catalog 自身の
  first-principles に再 grounding 済み（`rules/audit.yaml` の notes — owner-whitelist
  trust + did:dplaax の構造的 Owner 導出 + accountability-follows-the-last-cryptographic-link）。
  `attribution.segment` / `attribution.origin-default` から「anchored in Paper 04」を除去。
  origin-default は 2026-06-16 の独立 FCoT で sound 確認済み。Paper 04 §3.4/§4.7 は設計を
  追従して書き換える対象（別 task）。delegation も同様に Paper 04 由来の
  pipelineId/delegatedRole を捨て、構造的最小形へ（`rules/delegation.yaml`）。

## Ledger: process type rename（2026-06-12）

component 語彙を process 語彙へ全面 rename（user 承認済み。全参加者が Process DID を
持つため catalog の分類対象は process、型名は分類基準 = chain への署名挙動に従う）。
rule ID の対応表:

| 旧 ID | 新 ID |
| --- | --- |
| component.catalog | process.catalog |
| component.filter-convert.stateless | process.chained.stateless |
| component.origin-source.firstdrop | process.source.firstdrop |
| component.external-sink.verify | process.sink.verify |
| component.external-sink.receipt | process.sink.receipt |
| component.custom.interop | process.custom.interop |

- 型名: FilterConvert → Chained Process / Origin Source → Source Process /
  External Sink → Sink Process / Custom → Custom Process。傘: Pipeline Component →
  Pipeline Process。
- vectors: component-001..006 → process-001..006、fixture キー component_type →
  process_type。
- **wire 変更は 1 件のみ**: transformationClaim `provin:external-sink-receipt` →
  `provin:sink-receipt`（process-005 の期待値更新。型名由来の label は wire 上これが
  唯一だった）。他の claim 語彙（provin:filter / convert / filter-convert / enrich /
  aggregate）は transformation 名であり不変。
- v0.1 タグは本 rename を載せた commit に切り直し（consumer ゼロの間、タグは
  milestone marker — VERSIONING.md 冒頭参照）。

## 転記元の概観

- **provin.oss (branch poc)** — wire invariant の現行 SoT。コードコメント / README に契約として
  焼き込み済み。spec 言語への書き起こしが必要。所在の詳細は各 rule stub の `source`。
- **drafts/v1_001 / v1_002（本 repo のブランチ）** — 旧 Layer 構造での起草蓄積。
  特に `spec/5.specification/`（ppc / signer / schema_registry / vc_resolver / confidence 等）は
  spec 言語化済みの文面が多く、rule statement の下敷きにできる。
  `spec/1.concept/` は concept.md へ技術記述を除去して移植済み。
  v1_002 の `todo.md` は Layer 責務整理の作業メモ（Layer 2 → 3/4 への移送リスト）。
- **論文**（Zenodo、concept.md の References 参照）— rationale と完了条件の参照元。
  pre-1.0 正規化 backlog は実装論文の §8.1 (a)–(d)、conformance test suite の class 軸は §8.2。
- **dplaas.oss** — ⚠ 廃棄前 salvage: `docs/concepts/provenance.md` の origin 規範記述と
  L1/L2/L3 trust model の差分突合（大半は provin.oss / 論文に移植済みの見込み）。

## 未決

- ~~conformance vector の実体~~ — **2026-06-11 解決**: 全 55 rules に 1 本以上、
  計 78 vectors（当時。2026-07-02 現在 89 本。family 別形状規約は vectors/README.md）。
  canon / commitment / resolver の期待値は provin.oss（JCS・strict decoder・
  ComputeSourceRoot・Hash）で実検証した実値。**0.1 タグの vector 条件を充足**（全 entry
  draft / 各 rule ≥1 vector / lint green / source 全廃 — VERSIONING.md の 4 条件すべて成立）。
  - **2026-07-02 追記（full-review A-2/B-1 の修正で一部再生成）**: 上記「実検証した実値」の
    うち commitment-005 / commitment-007 の pinned root は「as-received literal bytes」解釈で
    生成されており、実装（proof 込み canonical 再直列化 — `ComputeSourceRoot`）の再計算と
    不一致だった（leaf 語義の確定 = canonical signed wire form に伴い実装出力で再生成、
    commitment-011 の claimed root も canonical 整合に補正）。また resolver-001 / resolver-003 は
    2026-06-16 のドメイン移行（83d60e9）で body のみ書き換わり key が旧 bytes のまま（hash 不一致で
    accept fixture の前提が破損。-001 は Codex spec-review が検出）、resolver-008 は base64 が
    opaque で移行漏れ（旧 .io ドメイン残存）だったため、resolver-001/002/003/008 を単一の
    synthetic 署名文書（.dev）から再生成（key = proof 除外 content hash / body = proof 込み
    canonical wire、`resolver.body.encoding` 改訂に整合。-003 の reject は whitespace 変異から
    content 変異に変更 — parse→canonical 再計算では whitespace は検出不能かつ無害のため）。
    commitment-006/008/009/010 は実装照合で一致・意図どおりを確認。壊れが機械未検出だったのは
    conformance harness 欠落（B-2）のため — FIX-4 で第 1 弾 CI 実行化予定。
- ~~vc_resolver 領域の rule file~~ — **2026-06-11 解決**: drafts/v1_002 vc_resolver 節
  から rules/resolver.yaml へ転記（6 rules: address.form / immutability / states /
  states.no-demotion / batch.shape / body.encoding）。
- ~~隣接クレデンシャル間の hash 連続性の規範化~~ — **2026-06-11 解決**: 出典は
  drafts/v1_001 conformance 節の L2 検証規則 "Input-output binding"。
  `chain.data-flow.continuity` として転記済み。
- ~~schema 参照の subject 内配置~~ — **2026-06-11 解決**: rationale を
  `credential.schema-ref` notes に明記。W3C credentialSchema は credential 自体の
  schema（VC tooling への処理指示）、本 object は subject が attest する**データ**の
  schema であり署名スコープ内の主張の一部。W3C 語の流用は VC processor に envelope を
  データ schema で検証させる誤動作を招くため、subject 配置が正。
- ~~cryptosuite lifecycle の補完候補 3 点~~ — **2026-06-11 解決**: no-op 禁止は
  provin.oss に実装済み（「対応なし」は stale だった）と判明、
  `signer.cryptosuite.no-op-rejected` として転記。allow-list（deployment 運用事項・
  出典未発見）と cutoff date（Sunset 遷移で表現可能・冗長）は不採用、
  理由は `confidence.cryptosuite-lifecycle` notes に記録。
- ~~claim token の文字集合が未 pin~~ — **2026-06-11 解決**: `credential.claim.charset`
  として rule 化（White_Space / Cc / Cf / "+" を MUST NOT、違反 credential は reject、
  property snapshot は **Unicode 15.0 に pin** — table 版差による受理 partition を防止、
  bump は 0.x minor 扱い）。vector cred-028（zero-width = 表示偽装）/ cred-029（"+" join
  復活阻止）。大文字・非 ASCII は意図的に profile の裁量に残す — claim 同一性は
  (接地 URL, label) の byte 比較なので、それ以上の受理差は発行可能 token を分けるだけで
  解釈は割らない。
- `registry.append-only` の出典は旧 draft のみ — provin.oss に対応実装が現れた時点で要突合。
- ~~監査用列挙 API（issuer / ingress set でのクエリ面）~~ — **2026-06-11 解決**:
  L2 監査モデルの仕分けにより provin 側（provin.oss docs/protocol、サービス API spec の
  指定席）と確定。spec scope 外。
- **federation 層のスコープ判断** — 旧 draft conformance L3 の機構群（相互 allow-list /
  購読登録 / downstream receipt / append-only 発行ストリーム / control plane 署名検証）は
  現 catalog に対応 rule が無い。一方、audit-reachable class の申告漏れ検出は
  これらの記録を敵対的証拠として前提している（→ L2 の歯が依存）。本 catalog に
  入れるか、Chain primitive spec として別立てか、未決。実装が network 層に到達した
  時点で具体化する（2026-06-11 起票）。
- ~~JSON-LD context 文書の実体~~ — **2026-06-11 解決**: 所有は二層（Model A）。
  protocol context の正規は本 repo `contexts/v1.jsonld`（byte 単位）、provin.oss は
  byte-exact vendoring + sha256 固定テスト。詳細は contexts/README.md と
  `credential.field.context`。
- ~~`generate` のベース語彙昇格パス~~ — base 語彙の解体（2026-06-11）により消滅。
- ~~profile 識別の MUST 化~~ — **2026-06-11 解決**: 識別マーカーの MUST ではなく
  **namespace 接地の MUST**（`credential.claim.grounding`）として再構成。claim の
  同一性 = (接地 URL, label)、裸 prefix の衝突を署名スコープ内で排除。provin profile
  context（接地担体）の正規は provin.oss 側。
  **2026-06-11 ドメイン確定**: provin = `provin.dev`、protocol = `dplaax.dev`。
  profile context URI は `poc.provin.dev/vc/v1`（vectors / provin.oss とも反映済み）。
- **delegation credential の正規地位（controller chain の確立・証明機構）** — 2026-06-03 に
  deferred（retired memo `temp/technical_concerns/delegation_credential.ja.md`）のまま、
  「採用 / deliberately out of scope」どちらの結論も記録されず restructure に流れた。現 catalog に
  delegation rule は無いが、`rules/audit.yaml` / `credential.yaml` は attribution を「controller
  chain」で記述し（fixture は vectors/audit-* の `controllers` map）、その**確立・証明機構を
  指定していない**: (a) DID-Document `controller` field（DID-Core 級・補完的だが proof として
  弱い）/ (b) owner 署名 DelegationCredential VC（旧 spec Part II `PipelineDelegationCredential`、
  Paper 01 §4.7 / ch4 core 要素 / ch6 `RESOLVE_OWNER_VIA_DELEGATION`）/ (c) 両方（VC が field の
  主張を証明）。現状 provin.oss は (b) を de-facto 採用（`delegation` package + docs/GLOSSARY
  「reconstruct the controller chain」）だが旧 spec の half-migration: `delegatedRole`・`pipelineId`
  を落とし、pipeline 単位 scoping を owner 単位束縛（`subj.OwnerDID()==issuer`）に置換、
  `scope []string` は残すが grammar/registry 無し・`Verify()` 未検査。決定すべき: (1) (a)/(b)/(c)
  を選び `audit.yaml`/`credential.yaml` に機構を明示、(2) VC を正規とするなら shape を pin
  （scope grammar/registry / delegatedRole / pipeline-vs-owner scoping）して rule 化し provin.oss と
  reconcile、(3) 不採用なら "deliberately out of scope" を rationale 付きで確定し delegation 検証
  要件の代替を明記。確定まで provin.oss の delegation 公開 API は churn しない（API responsibility
  review の T3-1 = ungrounded scope / typed-struct vs body-as-SoT は本決定の下流）。（2026-06-15 起票）

## trust model（L1/L2/L3）の行き先

**2026-06-11 転記完了**（転記元: dplaas.oss `docs/concepts/provenance.md` §1）。
定義は GLOSSARY.md（trust layering entry）、L2 の位置づけと L3 の scope 外宣言は
`commitment.class.definition` notes、非技術の動機は concept.md（点の監査、線の現実 の
末尾段落）。L1 = confidence 3 軸、L2 = source commitment、L3 = 意味的監査（protocol 外）。
dplaas.oss の origin 規範記述本体は本 catalog の commitment.* rules に対応あり
（derived_from / source_root / source_root_canonical / 構築手順 / 外部参照の除外）。
