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
- **2026-07-13: L6 spec-vs-impl 一括裁定（P0-11）— resolver.states の normative 変更を含む**。
  (a) `resolver.states` を **authority スコープ化**: NotFound→failed は照会先が当該
  namespace の非存在 authority（DID registry 等）である場合のみ。無スコープの旧文は
  第三者 store が保持したことのない content への NotFound 主張で definitive failed を
  鋳造できる audit-DoS レバーであり、commitment family の pin（commitment-009:
  未解決→indeterminate）とも矛盾していた。state は source-local 観測として定義し
  証拠力を分離。vector: resolver-005 に `non_existence_authority: true` を追加、
  resolver-009（false→indeterminate）を新設、vectors/README に input shape を定義。
  (b) `resolver.batch.shape` を条件形へ（「If an implementation or profile provides
  a batch lookup surface…」）+ reserved 宣言（dplaax.vc.v1 に batch surface 無し）。
  (c) `resolver.states.no-demotion` の notes を durable-history/retention 根拠へ補正
  （新定義下で content store の NotFound は global claim ではないため）。
  (d) `chain.trigger.retention` の notes に conformance projection を明記（wire 不変則
  pin が規範面、runtime classifier seam は非要求）。実装側（provin.oss）:
  `vc.Verifier.AttributeOwner` export（attribution 最小公開 API — 帰責計算の primitive、
  credential 検証は caller 前提）、conformance driver の authority 分岐 +
  attribution 実 walk 化 + registry Service 経路 test。Codex 二次意見 High2/Med2 反映済み
  （裁定 spec: scope repo `docs/draft/p0-11-l6-spec-vs-impl-rulings-2026-07-13.md`）。

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
    conformance harness 欠落（B-2）のため。**2026-07-09 更新: harness は実行化済み** —
    provin.oss `conformance/TestDplaaxAllVectors` が全 vector を driver 実行または理由付き
    skip として ledger 化し、coverage guard が未 driver/未 skip の vector で CI を赤にする。
    tranche 1（canon/cred/commitment/chain-verify/confidence/delegation/signer）が実行中、
    tranche 2（chain-issuance/process/audit/registry/resolver）は driver 実装が進行中。
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
- ~~`registry.append-only` の出典は旧 draft のみ — provin.oss に対応実装が現れた時点で要突合~~ —
  **2026-07-02 解決**（full-review A-1）: 実装（schemaregistry の deprecation = idempotent な
  flag flip・body 保持・atomic rewrite・Get は deprecated を隠さない）と突合し、不変性スコープを
  「登録コンテンツ（schema_format / schema_body / version 束縛）」に限定する契約解釈で statement を
  精緻化。lifecycle メタデータは (a) 取得可能性に影響しない（deprecated でも `(key, version)` で
  byte-identical 取得可能）(b) contentHash（`credential.schema-ref` の resolve-and-compare）に
  参加しない、の 2 条件で対象外。vector registry-002（commit → deprecate → get で contentHash
  不変 + flag 可視）を追加。覆す条件 = deprecation 状態自体を署名済み・第三者検証可能な事実として
  扱う要件が出た場合（その際は新エントリ or tlog 方式へ反転 — 実装側修正）。
- ~~監査用列挙 API（issuer / ingress set でのクエリ面）~~ — **2026-06-11 解決**:
  L2 監査モデルの仕分けにより provin 側（provin.oss docs/protocol、サービス API spec の
  指定席）と確定。spec scope 外。
- **`credential.schema-ref` の id（registry URI）形式が未 pin** — rule statement は
  「id (registry URI)」とのみ規定し、URI の具体形は未定義。provin.oss が schema
  validation のデータプレーン配線（2026-07-10）で canonical 形式
  `dplaax:schema/<name>@<version>`（name/version は url-safe `[A-Za-z0-9._-]`、node URL
  非依存で移設可能）を採用。cross-implementation の相互運用には spec 側での形式規範化が
  必要。resolve は id を registry の (name, version) に写像する（scheme は registry の
  所在ではなく識別子を名付ける）。次回 rule 改訂で `credential.schema-ref` に URI 文法を
  追記候補（provin.oss 実装が事実上の reference）。（2026-07-10 起票）
- ~~**federation 層のスコープ判断**~~ — **2026-07-11 解決**（起票時の具体化条件
  「実装が network 層に到達した時点」は network-slice 1–17r の landing で成立）:
  **hybrid 配置**で決着。旧 draft conformance L3 の 5 機構を「証拠を生む義務」と
  「証拠を運ぶ機構」に分解し、前者だけを新 domain `rules/transfer.yaml`
  （4 rules、全て class: audit-reachable）として本 catalog に入れた:
  `transfer.evidence.definition`（定義アンカー — audit-reachable の omission
  detection が突合する 3 記録クラスを束ね、「ingress store」語彙に定義上の家を
  与える）/ `transfer.emission.append-only`（append-only 発行ストリームの抽象 —
  emitter 側 emission record）/ `transfer.ingress.retention`（downstream receipt
  機構 1 = subscriber 保持の抽象で、**ingress store の定義 rule**）/
  `transfer.relationship.record`（購読登録の記録義務を転送関係の記録義務として
  抽象化）。後者の機構（相互 allow-list = admission control で証拠鎖外、
  control-plane RPC shape / wireauth、payload delivery mode 意味論）は
  2026-06-11 仕分けどおり provin profile / サービス API 側に留置。
  **これは 2026-06-11 仕分けの、証拠基盤に限定した明示的 amendment**（仕分けは
  記録義務を profile 側と明記していた — その一部を catalog に移す）。機構自体の
  昇格条件「第二実装出現時に 0.x minor で」は不変。命名は「転送関係」の直訳
  `transfer`（「federation」は旧 Conformance L3 / 現 trust layering / provin Auth
  Level の三重衝突、「chain」は chain.yaml PPC-linkage と旧 transport Chain
  primitive の衝突で回避）。relationship.record の証拠は「相手方署名済み要求 +
  当事者帰属の受理記録」までで、双方向 non-repudiation は現行 wire が応答側
  署名を持たないため主張しない（signed acceptance artifact は機構昇格時の
  profile hardening 候補）。commitment.class.definition / commitment.store.persistence
  / audit.attribution.origin-default の notes に transfer.yaml への pointer を追記。
  provin.oss 側 reconcile: chainmanager の関係記録を証拠品質に（署名済み登録 view
  と解決 DID snapshot を専用 tlog へ）、ingress store 突合、conformance driver。
  設計 spec は docs/draft/federation-transfer-evidence-spec-2026-07-11.md
  （provin_2 scope 側、spec repo 外）。
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
  profile context URI は `provin.dev/vc/v1`（vectors / provin.oss とも反映済み）。
- ~~**delegation credential の正規地位（controller chain の確立・証明機構）**~~ —
  **2026-07-06 解決**（full-review C-1）: (b) owner 署名 DelegationCredential VC を正規機構として
  採用し rule 化済み — `rules/delegation.yaml`（4 rules: `delegation.shape` / `.binding` /
  `.proof` / `.scope`、spec_draft `f63bbfe` で着地）。provin.oss は reconcile 済み
  （`delegation` package の Build/Verify が同 rule 群の実装 — oss `54bfa5b` 起点、conformance
  delegation-001..005 で vector 駆動）。下記の起票時論点（(a)/(b)/(c) の選択・shape pin・
  reconcile）は上記で充足。scope grammar/registry の将来拡張は delegation.yaml の notes が担う。
  **以下は起票時（2026-06-15）の記述をそのまま履歴として保持**（「現 catalog に delegation rule は
  無い」等は当時の状態）: 2026-06-03 に
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
- ~~commitment.verify family に verified vector が無い~~ — **2026-07-06 解決**: commitment-013
  を追加（credential は commitment-009 の aggregate 形、source_root は commitment-011 の
  全 3 source に対する実計算値 `f12209902a…` — provin.oss `NewSourceCommitment`/JCS を oracle に
  実検証、`VerifySourceCommitment` で verified を確認）。rule statement も verified 帰結を明文化
  （failed / indeterminate / verified の三値を列挙する形に圧縮改訂）。以下は起票時の記述:
  現行 vector は defect 系のみで、
  全解決 + root 一致 → verified の正例が catalog に無い（常時 Failed の縮退実装は
  commitment-009 でしか落ちない）。commitment-013（全 source 解決済み・root 一致 → verified）を
  追加候補として起票。provin.oss 側は unit test（TestVerifySourceCommitmentVerified）で
  同ケースを検証済みだが、cross-implementation の pin は vector が担う。（full-review FIX-4
  で検出、2026-07-06 起票）
- ~~`credential.field.valid-from` の受理側文言と `-00:00` の未 pin~~ — **2026-07-06 解決**:
  (a) statement を "Receivers MUST reject fractional seconds (issuers truncate before
  emission)" 形へ改訂し受理側 reject を明文化、(b) `-00:00` は **reject** に確定（RFC 3339 §4.3
  の unknown-local-offset は「offset 不明」の表明であり UTC の主張ではない — fail-closed
  profile は曖昧形を受理しない。`+00:00` は offset-0 の UTC 主張として引き続き受理）。
  cred-032（`-00:00` → reject）で pin。provin.oss は文字列レベルの `-00:00` reject を実装済み
  （parser は offset 0 に折り畳むため parse 後では判別不能）。以下は起票時の記述: cred-030/031（dd52bef）で
  非 UTC offset / 小数秒の reject は pin 済みだが、(a) statement の "Sub-second precision is
  truncated at issuance" は発行側 guidance と受理側 reject の関係が暗黙（Codex spec-review
  advisory: "fractional seconds MUST be rejected; issuers truncate before emission" 級の明文化を
  推奨）、(b) RFC 3339 §4.3 の `-00:00`（unknown local offset）を UTC として受理するか否かが
  vector 未 pin で実装間分岐の余地（provin.oss は offset==0 として受理）。statement 改訂と
  合わせて次回 rule 改訂時に処理。（2026-07-06 起票）

## trust model（L1/L2/L3）の行き先

**2026-06-11 転記完了**（転記元: dplaas.oss `docs/concepts/provenance.md` §1）。
定義は GLOSSARY.md（trust layering entry）、L2 の位置づけと L3 の scope 外宣言は
`commitment.class.definition` notes、非技術の動機は concept.md（点の監査、線の現実 の
末尾段落）。L1 = confidence 3 軸、L2 = source commitment、L3 = 意味的監査（protocol 外）。
dplaas.oss の origin 規範記述本体は本 catalog の commitment.* rules に対応あり
（derived_from / source_root / source_root_canonical / 構築手順 / 外部参照の除外）。

## 2026-07-14 — P0-0 / P0-1 Phase 0 転記（scoped evidence vector + variant identity）

FABLE↔SOL debate の Agreed 決定（ユーザー承認済み）の Phase 0（spec-first）を転記。
実装（provin.oss / provin.auth の additive・feature-off）は後続 slice。

**P0-0（A2 — Versioned, Durable, Policy-Gated Scoped Evidence Vector）**:
- `rules/claims.yaml` 新設（15 rule）。named scope catalog、`VERIFIED` 一文定義 + non-claims、
  coverage×truth-state 直積、decision profile 3 archetype、policy/evidence 分離、tlog/receipt/
  source-set-binding の scope 分離、offline snapshot = policy-only、catalog single-owner。
- `rules/confidence.yaml` に `confidence.lifecycle.input-semantics` 追加（registry unreachable=
  indeterminate / evaluator 不在=UNSUPPORTED / Sunset・unknown=failed）。
- `GLOSSARY.md`: `trust layering (L1/L2/L3)` を AUTH 文脈専用へ改訂し、named scope / evidence
  vector / coverage・truth-state / decision profile / WireVariantID / EvidenceViewID を追加。
  → 下の「trust model（L1/L2/L3）の行き先」節（2026-06-11）は **本転記で supersede**
  （provenance の L1/L2/L3 ラベルは named scope に置換。旧節は歴史記録として残置）。

**P0-1（B2.1 — immutable variant set + EvidenceViewID + PromotionRecord + quarantine）**:
- `rules/identity.yaml`（body-address / wire-variant-id / variant.immutable-set）、
  `rules/evidence-view.yaml`（`evidence.*` id: manifest / cache.exact-view / verified.is-relation /
  spine.bounded-dag / indeterminate.not-failed / bundle.v3 / bundle.reader-first）、
  `rules/promotion.yaml`（record.verified-only / durable-order / index.per-contract）、
  `rules/admission.yaml`（resolve-variant.exact / legacy-resolve.provisional / quarantine.class /
  verify-to-admit.backpressure / static-backend.closed-pilot / evict.tombstone / gc.reference-aware /
  catalog.no-launder）。
- `schemas/evidence-view.json`（EvaluationViewManifest + scoped evidence vector; coverage×truth-state
  を if/then/else で強制）、`schemas/bundle-v3.json`（variant spine + contract + snapshot refs +
  EvidenceViewID）新設。
- rule-id 制約メモ: id 第 1 segment はハイフン不可（`^[a-z0-9]+(\.[a-z0-9-]+){1,3}$`）。
  よって domain は `evidence.*`（file 名 `evidence-view.yaml` は非規範なので可）。

**P0-4 gating**: WireVariantID / `eddsa-jcs-2022` の canonical profile freeze は P0-4（canonicalization
決定、未着手）依存。Phase 0 では grammar・要件（domain separator / id version / canon profile /
hash algo を明示）を draft で規範化し、profile bytes の凍結は P0-4 後。`identity.wire-variant-id`
notes と両 schema の `$comment` に明記。

**Vector backlog（confirm-point 2: impl/P0-4 非依存分のみ今 author、残りは backlog）**:
- 今 author 済み: `claims-coverage-001/002/003`、`claims-policy-001`（coverage×truth-state 直積、
  required-scope fail-closed、INDETERMINATE→QUARANTINE。evidence-view.json を fixture で実 exercise）。
- backlog（Phase 1 storage/DAG 実装 or P0-4 後に materialize）: F-02 config-laundering（同 bytes を
  verifier-config 差で同 VERIFIED[LINEAR_ATTESTATION@1] にできない）、filelog→TLOG_INCLUSION 不能、
  valid→invalid overwrite、invalid front-run、two-valid-proof `V12/V20/H15`、snapshot-change 再利用不可、
  DAG budget exhaustion→Indeterminate、crash/fencing、evicted→NotFound launder 不可、legacy 流用不可、
  migration matrix、WireVariantID cross-language byte-equivalence、bundle v3 independent verifier。

**GLOSSARY.ja / 各 rule の .ja**: 未同期（English-primary。翻訳同期は follow-up）。

### Codex spec-review fold（2026-07-14、同日）

Phase-0 転記に Codex spec review（10 issue）を実施し全 fold:
- #1 catalog 未定義 → `schemas/scope-catalog.json`（named scope + profile enum、SEMANTIC_EXECUTION
  含む、TLOG_TRUSTED_TIME / freshness は p0-2-gated）+ `claims.catalog.enumerated` /
  `claims.contract.distinct-from-profile` / `claims.profile.{evidence-archive,provenance-release,
  external-effect}` 追加。vector の claimContractId 誤用（profile id）を claim-contract id に修正。
- #2 `SOURCE_CREDENTIAL_ATTESTATION (n/n)` → `claims.source-credential.n-of-n` 分離、
  `claims.source-set-binding.atomic` の uses を completeness（all-consumed）から declared-set/root
  binding（`commitment.source-root.tree`）へ。
- #3 lifecycle 矛盾 → `confidence.cryptosuite-lifecycle` を LINEAR_ATTESTATION 評価時に条件付け。
- #4 durability / `Decision:` prefix を statement に明文化。
- #5 EvidenceViewID 循環 → schema で id を manifest の外へ、spine を origin→head・末尾==head に規定、
  digest projection は P0-4 gate と明記。
- #6 view-level terminal verdict → `evidence.view.terminal-verdict`（contract-scoped、body-global
  Verified ではない）を定義し promotion から参照。
- #7 evidence-view.json teeth → scope enum / 非空 spine・vector / content-address・wireVariantId
  grammar pattern。one-result-per-scope と policyDecision↔profile 結合は semantic（vector で pin）と明記。
- #8 bundle-v3.json → inputSnapshotRefs（anchorStatus + timeBasis、値は p0-2-gated）+ commitment
  （SIGNATURE/CHECKPOINT）+ manifest refs を required 化。
- #9 resolver 矛盾 → `identity.variant.immutable-set` の uses から `resolver.immutability` を外し、
  `identity.resolution.exact-vs-legacy`（exact は (body, variant)、body-only は legacy projection）
  で reconcile。eviction を Unavailable + `EVIDENCE_EVICTED` reason に（`resolver.states` 整合）。
- #10 Option-D → `identity.proof-envelope.not-claimed`（wire-level proof separation を conformant と
  主張しない、future ProofEnvelopeID と共存可能）を testable rule 化。

catalog は 66 → 113 rule。lint / validate_vectors green。**残 semantic teeth**（one-result-per-scope、
policyDecision↔required-scope 結合、bundle snapshot 完全形）と **P0-2-gated**（trusted-time / freshness /
anchor 値）は上記 vector backlog に統合。

## 2026-07-15 — P0-2 / P0-3 / P0-4 転記（batch）

FABLE↔SOL debate の Agreed 決定（ユーザー承認済み、fork 裁定含む）を 1 batch で転記。
catalog は 113 → 177 rule。lint / validate_vectors green。実装（provin.oss / provin.auth）は後続 slice。

**Fork 裁定（ユーザー確定）**: P0-4 = **Fork W**（完全 W3C `eddsa-jcs-2022` + Multikey + proof-local
`@context` + KAT、external interop goal）。P0-3 = **Fork Y**（Owner に独立 `authentication` 鍵、
greenfield なので新規 Owner のみ）。ledger の "Fork C / joint recommendation" 文言はユーザー選択で上書き。

**P0-4（A3 common kernel — RFC 8785 canonicalization、Fork W）**:
- `rules/canon.yaml`: `canon.jcs.base` を actual RFC 8785 化（`jcs-rfc8785`）、`canon.number.safe-integer`
  gate 新設、`canon.jcs.int64-verbatim` を legacy verify 専用へ隔離、`canon.number.raw-token-guard`
  （unsafe integer を lossy parse 後の値から推測せず raw-token/lossless stage で reject、inv6）。
- `rules/identity.yaml`: `identity.wire-variant-id` を `wire:v1:jcs-rfc8785:sha256:<hex>` に freeze（inv8）。
- `rules/signer.yaml`: `signer.suite.eddsa-jcs-2022`（Fork W）/ `.exact-dispatch`（algorithm guessing 禁止、
  inv17）/ `.legacy-projection`（`LEGACY_PROVIN_EDDSA_JCS_INT64@1`、inv13）/ `.w3c-interop-gate`
  （public Fork W issuance を KAT + 外部 W3C verifier interop で release-gate、Codex fold）。
- `rules/confidence.yaml`: `confidence.legacy.sunset`（Deprecated 2026-07-14 / Sunset 2026-10-01 /
  remove 2027-04-01、inv14）/ `.anchored-eligibility`（proof.created 単独不可、anchor-before-Sunset、
  inv15/16。P0-2 `observation.record.commits` へ uses edge を追加）。
- `rules/commitment.yaml`: `commitment.source-root.canonicalizer-binding`（`source_root_canonical` を
  field 単独解釈せず enclosing contract + variant vector + snapshot へ binding、inv18/19）。
- `rules/claims.yaml`: `claims.suite.contract-id`（W3C / LEGACY 契約）/ `claims.headline.suite-contract`
  （Decision + cryptosuite + canonicalizer contract 表示、単一 `Verified[EDDSA]` へ圧縮しない、inv22）。
- `rules/evidence-view.yaml`: `evidence.manifest.independent-ids`（canonicalizer / cryptosuite / schema id を
  claim contract と独立に manifest へ commit、EvidenceViewID が dispatch 入力を分離 commit、inv7/9 — Codex fold）。
- schemas: `scope-catalog.json` に `suiteContractId` enum。`evidence-view.json` / `bundle-v3.json` の
  manifest に `canonicalizerId` / `cryptosuiteId` / `schemaVersion`（required、inv7 — Codex fold）。
  wireVariantId pattern を frozen 形へ。fixtures `claims-coverage-001/002/004` を manifest id 追加で更新。

**P0-2（C2.1 — anchored-order historical + freshness-bounded current）**:
- `rules/identity-lifecycle.yaml`（id `lifecycle.*`）: `target.did-document`（revoke は doc 内全 VM、
  inv11）/ `authorization.at-state`（KEY/CONTROLLER_AUTHORIZATION_AT_STATE を named state vector で評価
  — Codex fold）/ `event.source-of-truth`（event log = SoT、status = derived、inv13）/
  `reconcile.no-rewind`（inv14）/ `recovery.no-fabrication`（inv15）。
- `rules/observation-order.yaml`（id `observation.*`）: `order.authority`（inv5）/ `record.commits`
  （exact variant + lifecycle state vector + log 位置、`emission-log-v2.json`、inv6）/ `membership.proof`
  （Merkle inclusion か hash-chain replay、filelog を TLOG_INCLUSION と誤称しない、inv7）/
  `order.same-origin`（inv8）/ `order.cross-log-bridge`（inv9）/ `trusted-time.profile`（inv10）/
  `grandfather.exact-variant`（inv20）/ `legacy.body-only`（inv22）/ `legacy.no-pre-revocation-anchor`
  （既 revoke・anchor 無 legacy → historical INDETERMINATE + `legacy-no-pre-revocation-anchor`、inv21 —
  Codex fold）/ `production.closed-pilot`（inv25）。
- `rules/auth-liveness.yaml`（id `liveness.*`）: `controller-chain.current`（inv12）/
  `cache.bounded-freshness`（inv16）/ `profile.coupled-bounds`（inv17）/ `degraded.separate-contract`
  （inv18）/ `public-profile.fail-closed`（inv19）/ `offline.no-current-verified`（inv23）。
- `rules/claims.yaml`: `claims.lifecycle.scopes`（5 atomic scope 列挙、inv1）/ `claims.profile.authorization`
  （historical-acceptance@1 / current-authorization@1 = archetype とは別 family、headline 表示、
  atomic vector 再合成禁止、inv2/24）/ `.historical-acceptance`（inv3）/ `.current-authorization`（inv4）。
  `claims.profile.external-effect` を current-authorization scope 全体（key/controller-at-state +
  freshness）要求へ修正（freshness 単独では ACCEPT 不可、Codex fold）。
- schemas: `emission-log-v2.json`（observation record: exact variant `oneOf`、lifecycle state vector に
  `lifecycleSnapshotRef`、log 位置は decimal string / inv20）。`bundle-v3.json` lifecycle 拡張
  （`lifecycleEvidence` / `observationEvidence` / `trustProfileSnapshot`、`anchorStatus` / `timeBasis`
  enum を P0-2 確定値へ）。`scope-catalog.json` に lifecycle scope + `authorizationProfileId` enum。

**P0-3（A3.1 common mechanism + Fork Y）**:
- `rules/auth-grant.yaml`（id `auth.*`）: `contract.normative-sot`（inv1）/ `grant.exact-method`（inv7）/
  `grant.kid-match`（inv8）/ `method.relationship`（inv9）/ `method.string-reference-only`（inv10）/
  `transcript.bound-fields`（versioned schema、`login-transcript.json`、inv12）/ `.audience-required`（inv13）/
  `.domain-separation`（inv14）/ `token.issuance-vs-request`（inv15）/ `.signed-claims`（`token-claims.json`、
  inv16）/ `.lifetime-bound`（inv17）/ `.no-legacy-reprojection`（inv18）/ `forky.authentication-login`
  （Fork Y = public default、inv23）/ `forkx.closed-pilot-only`（inv21/22、subset + boot/reload 明示）/
  `legacy.did-login`（inv24）/ `headline.contract-id`（inv25）/ `migration.enable-gate`（Fork W/Y は Owner
  document migration 契約 ratify まで enable 禁止、Codex fold）。
- `rules/did-resolution-auth.yaml`（id `auth.resolve.*`）: `id-equality`（inv2）/ `double-binding`（inv3）/
  `result-shape`（inv4）/ `single-input-binding`（inv5）/ `failure-mapping`（inv6）/ `unknown-member`（inv11）/
  `resource-floor`（inv19）/ `origin-pin`（inv20）。
- `rules/claims.yaml`: `claims.login.contracts`（3 login contract、inv23/21/24）/ `.token-scopes`
  （issuance-with-max-age / current-at-request、inv15）。
- schemas: `login-transcript.json`（versioned、`transcriptVersion` / `domainSeparationTag` を const pin —
  Codex fold）、`token-claims.json`。`scope-catalog.json` に token scope + `authContractId` enum。

**Codex spec review（2026-07-15、file+pipe）**: 7 High を検出、全 fold（上記 "Codex fold" 印）。
1 dismiss（evidence-view の別 authz-decision field — `decisionProfileId` は versionedId で
`current-authorization@1` を既に受理、single-pin で合成禁止のため不要 = contract-based dismiss）。

**public surface 決定（ユーザー確認済み・確定）**:
- wire field 命名は **artifact の所属 ecosystem に従う** 原則で確定:
  - JWT/OAuth レイヤー（`login-transcript.json` / `token-claims.json`）= **snake_case**
    （`auth_contract_id` 等。JWT RFC 7519 / OAuth / OIDC 慣行、ledger prose と一致、rule statement も既に snake_case）。
  - dplaax 内部 evidence 構造（`evidence-view.json` / `bundle-v3.json` / `emission-log-v2.json` /
    `scope-catalog.json`）= **camelCase**（W3C VC data model 系の慣行）。
- frozen literal: `transcript_version="login-transcript-v1"`、`domain_separation_tag="dplaax-owner-login-v1"`
  （`provin-wire-variant-v1` 慣行に整合）。

**Vector backlog（impl/storage 依存、後続 slice）**: revoke 前後 / signer・observer backdating /
cross-origin bridge 有無 / parent revoke / cache freshness / status-event mismatch / grandfathering /
filelog replay↔Merkle parity（P0-2）。id/snapshot/relationship mismatch、multi-key order、duplicate VM、
cross-protocol replay、audience/issuer mismatch、legacy/new token matrix（P0-3）。RFC 8785 official /
W3C KAT / custom / legacy cutover matrix、WireVariantID cross-language byte-equivalence（P0-4）。

**Schema backlog（Codex 指摘、後続）**: standalone lifecycle-event / DIDDocSnapshot wire schema
（現状は content-address ref で参照）、Fork X PDP-containment manifest schema（delegation-authorizable set
列挙 = delegation.yaml scope grammar 依存）。

**GLOSSARY / 各 rule の .ja**: 未同期（English-primary、翻訳同期は follow-up）。

## 2026-07-15 — P0-5 / P0-7 転記（batch 2、P0 全 8 round 転記完了）

FABLE↔SOL debate の Agreed 決定 2 件を転記。catalog は 177 → 239 rule。lint / validate_vectors green。
これで P0-0〜P0-7 の全 architecture decision が rule catalog に SoT 化された。実装（provin.oss / provin.auth）は後続 slice。

**P0-5（B2 — durable quarantine + ReleaseAuthorization + external-effect state machine）**:

- `rules/external-effect.yaml`（id `effect.*`、28 rule 新設）: sink profile 分類（`external-effect-sink@1` /
  `archive-observation-sink@1`、evidence-only 証明不能な archive は external-effect 扱い、inv23）/
  required-scope 全 VERIFIED gate（inv1）/ full spine to origin 定義（inv2）/ bare verdict 禁止
  （Overall・body-level latest・adjacent、inv3）/ closed state machine
  `RECEIVED→QUARANTINED→EVIDENCE_VERIFIED→RELEASE_AUTHORIZED→DISPATCHING→EFFECT_*` + `DENIED`/`DENY_EXPIRED`
  （inv 状態機械）/ ReleaseAuthorization artifact + versioned wire artifact 経由の構造強制（inv4/26）/
  exact quarantine bytes 照合・再 fetch 禁止（inv5）/ valid_until + freshness 再評価（inv6）/
  atomic entry（inv7）/ structural pregate（inv8）/ verdict mapping（inv9）/ TTL→`DENY_EXPIRED`
  （evidence 不変、inv10）/ CAS/fencing single-flight（inv11）/ `EFFECT_CONFIRMED` のみ成功
  （inv12/20）/ `EFFECT_UNKNOWN` no-guess no-auto-retry（inv13）/ Writer idempotency capability 4 形
  （inv14）/ limited profile（inv15）/ delivery identity（inv16）/ local-state exactly-once 禁止
  （inv17、P1-D 独立 claim）/ receipt confirmed-only + limited claim（inv18/19）/
  ObservationRecord・DecisionRecord 分離（inv21/22）/ quarantine capacity・no-fallback（inv24/25）/
  writer 排他 cutover（inv27）/ `POSSIBLE_LOSS` 可視化（inv28）。
- `rules/claims.yaml` +2: `claims.effect.contracts`（contract 集合の enumerate、完了は
  `EFFECT_CONFIRMED@1` のみ）/ `claims.effect.legacy-receipt`（`LEGACY_SINK_RECEIPT@1` 投影、再昇格禁止）。
- `rules/audit.yaml` +1: `audit.release.synthesis`（per-scope vector からの synthesis + verdict digest commit）。
- schemas: `quarantine-entry.json`（payload blob と同一 atomic commit を明記）/
  `release-authorization.json`（normative commit list 全 field required）/ `observation-record.json`
  （coverage=NOT_EVALUATED const）/ `decision-record.json`（RELEASE 時 releaseAuthorizationId 必須の
  if/then）/ `effect-status.json`（closed enum + state 依存 required の if/then 3 本 + deliveryIdentity）。
- `scope-catalog.json` +2 def: `sinkProfileId`（legacy-adjacent-write@1 は migration posture のみ）/
  `effectContractId`（6 contract）。

**P0-7（B2 — Exact Artifact-Bound Release Security Gate）**:

- `rules/release-security.yaml`（id `release.*`、31 rule 新設）: subject = exact output digest（inv1）/
  同一 digest binding・cross-digest 再利用禁止（inv2）/ build-once（inv3）/ image digest pin +
  multi-arch index+platform 両記録（inv4）/ action SHA pin（inv5）/ source full-SHA・denylist 不可
  （inv6）/ tested=shipped toolchain（inv7）/ frozen lockfile graph（inv8）/ IMMUTABLE≠REPRODUCIBLE +
  build-input manifest（inv9/10）/ scan state 5 分類・error→CLEAN 投影禁止（inv11）/ bounded CLEAN
  （inv12/30）/ scan coverage 面 enumerate + trusted claim は builder も（inv13）/ scan artifact fields
  （inv14）/ DB freshness→DB_STALE（inv15）/ component_absent のみ非 waiver（inv16）/ reachability
  exact-binding + positive evidence なしは potentially_reachable（inv18/20）/ unreachable も dated waiver
  （inv17）/ Medium/Low も waiver 必須（inv22、self-review で追加）/ reachable High/Critical 0 非 waiver
  （inv21）/ waiver contract 全 field + auto-renew 禁止（inv23）/ waiver 早期失効（inv19）/
  scanner-outage waiver 同規律 + 同一 digest のみ clean 再利用（inv24）/ evidence PRESENT +
  ALLOW_WITH_WAIVER 分離（inv25）/ headline policy id + waiver count（inv26）/ trusted-builder 検証
  6 field pin（inv27）/ OCI/npm provenance 分離（inv28）/ SBOM subject-bound（inv29）/ 新 advisory で
  acceptance 再評価（inv30）/ docs pin claim 一致（inv31）/ baseline は TRUSTED_SUPPLY_CHAIN /
  REPRODUCIBLE_BUILD を名乗らない（inv32、D-4 maturity-ramp は notes に未裁定と明記）/
  versioned release profile（waiver cap / DB freshness / coverage、変更は version bump）。
- schemas: `release-evidence-manifest.json`（scanArtifact / sbomReference / provenanceReference $defs、
  oci-image-index→platformManifests 必須、TRUSTED_SUPPLY_CHAIN claim→provenance+sbom+workflowRef 必須、
  REPRODUCIBLE_BUILD claim→buildInputManifest 必須の if/then）/ `advisory-assessment.json`
  （4 分類 + reachabilityBinding）/ `release-waiver.json`（全 field required、autoRenew const false）。

**GLOSSARY**: P0-5 6 語（quarantine entry / ReleaseAuthorization / effect status /
ObservationRecord・DecisionRecord / delivery identity）+ P0-7 7 語（release subject / immutable artifact /
reproducible build / clean scan / component absent / unreachable・potentially reachable /
trusted build provenance）を追加。WireVariantID の stale な「P0-4 pending」注記を frozen 形へ修正。

**裁定状況**: D-3（optimistic profile）は debate 内で実質決着 — B2 に含めず、需要発生時のみ別 Ledger
（`effect.migration.exclusive-writers` の rollback 規律にも反映）。**D-4（maturity-ramp）のみ未裁定**、
期限は first public release 前（`release.claim.baseline-cap` の notes に明記）。

**Vector backlog（impl/storage 依存、後続 slice）**: broken ancestor/hole/revocation、source scope failure、
stale/expired authorization、crash/timeout/duplicate dispatch、multi-worker fencing、archive
observation/decision split、quota/no-fallback（P0-5）。tag-only/moving-ref/major-tag 拒否、scanner error
state 非投影、cross-digest evidence 拒否、waiver 失効/expiry、multi-arch 片面 scan block、SBOM
component-absent 偽装拒否、wrong-repo attestation 拒否（P0-7）。

**Schema backlog（後続）**: quarantine store の operational policy schema（quota/retention 数値は
deployment profile 側）、release profile の数値 catalog（waiver cap / DB freshness bound の versioned
値表）、Writer capability manifest（P1-D の conformance suite と対）、receipt credential の subject
wire fields（delivery identity / authorization digest / target acknowledgement の binding 形 —
`effect.receipt.confirmed-only` の rule はあるが PipelinePassCredential 側の required 形は wire-profile
起草待ち。Codex #6 指摘の残余）。

**Codex spec review（2026-07-15、file+pipe、2 回目 — 1 回目は途中 kill で stdout 空、stderr から
schema-binding 系の予兆 1 点を先行 fold）**: 10 issues（High 5 / Medium 5）検出、全 10 fold:
(1) DecisionRecord は decision=RELEASE のみ actionable(High)、(2) EFFECT_UNKNOWN の reconciliation
遷移を transition table として effect-status.json に normative 化(High)、(3) DENY_EXPIRED を
evidence-view.json policyDecision enum に追加 + bounded quarantine との関係を notes に明記(Med)、
(4) writer capability「or limited profile」明文化 + `writerCapabilityProfile` def 追加(Med)、
(5) 既存 effect-complete status の意味保存を statement に昇格(Med)、(6) ObservationRecord の
payload blob 同時 persist を明記 + receipt wire fields は backlog(Med、部分 fold)、
(7) `claims.effect.scope-mapping` 新設 — RECEIPT_EXTERNAL_EFFECT@1 scope は EFFECT_CONFIRMED@1
record からのみ評価(Med)、(8) potentially_reachable High/Critical を hard gate に折り込み
（fail-closed 解釈、inv20 の趣旨。**ユーザー確認推奨**: gate を厳しくする方向の解釈裁量）(High)、
(9) advisory-assessment に unreachable/component_absent の条件付き required（binding + evidence +
sbomRef）+ SBOM componentCoverage required 化(High)、(10) baseline-cap の claim 別 evidence 分離 +
manifest schema の per-claim 条件付き required（provenance minItems 1 / reproduction）(High)。
fold 後 240 rule、lint / validate_vectors / schema check green。dismiss 0。
