# STATUS — 起草の現状（一時文書）

> 本ファイルは作業台帳であり spec の一部ではない。spec 安定後に削除する。
> tools/lint.py の走査対象外（規範語の引用が許される唯一の markdown）。

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

- conformance vector の実体 — provin.oss のテストを seed にしつつ、実装の癖を encode せず
  spec 起点で書き直す（vectors/README.md の規律）。
- ~~vc_resolver 領域の rule file~~ — **2026-06-11 解決**: drafts/v1_002 vc_resolver 節
  から rules/resolver.yaml へ転記（6 rules: address.form / immutability / states /
  states.no-demotion / batch.shape / body.encoding）。
- ~~隣接クレデンシャル間の hash 連続性の規範化~~ — **2026-06-11 解決**: 出典は
  drafts/v1_001 conformance 節の L2 検証規則 "Input-output binding"。
  `chain.data-flow.continuity` として転記済み。
- schema 参照の subject 内配置 — W3C VC Data Model の top-level credentialSchema 慣行からの
  意図的逸脱として rationale の明記が未了（`credential.schema-ref` の notes 参照）。
- ~~cryptosuite lifecycle の補完候補 3 点~~ — **2026-06-11 解決**: no-op 禁止は
  provin.oss に実装済み（「対応なし」は stale だった）と判明、
  `signer.cryptosuite.no-op-rejected` として転記。allow-list（deployment 運用事項・
  出典未発見）と cutoff date（Sunset 遷移で表現可能・冗長）は不採用、
  理由は `confidence.cryptosuite-lifecycle` notes に記録。
- `registry.append-only` の出典は旧 draft のみ — provin.oss に対応実装が現れた時点で要突合。
- 監査用列挙 API（issuer / ingress set でのクエリ面）— サービス API 側、未設計。
  spec scope 外（wire profile / 実装 repo 側）の可能性が高い。
- ~~JSON-LD context 文書の実体~~ — **2026-06-11 解決**: 所有は二層（Model A）。
  protocol context の正規は本 repo `contexts/v1.jsonld`（byte 単位）、provin.oss は
  byte-exact vendoring + sha256 固定テスト。詳細は contexts/README.md と
  `credential.field.context`。
- ~~`generate` のベース語彙昇格パス~~ — base 語彙の解体（2026-06-11）により消滅。
- ~~profile 識別の MUST 化~~ — **2026-06-11 解決**: 識別マーカーの MUST ではなく
  **namespace 接地の MUST**（`credential.claim.grounding`）として再構成。claim の
  同一性 = (接地 URL, label)、裸 prefix の衝突を署名スコープ内で排除。provin profile
  context（接地担体）の正規は provin.oss 側。
  ⚠ **provin.io ドメインの所有確認が未了** — poc.provin.io/vc/v1 が署名バイトに
  入るため、外部 deployment 前に取得・確認必須。

## trust model（L1/L2/L3）の行き先

**2026-06-11 転記完了**（転記元: dplaas.oss `docs/concepts/provenance.md` §1）。
定義は GLOSSARY.md（trust layering entry）、L2 の位置づけと L3 の scope 外宣言は
`commitment.class.definition` notes、非技術の動機は concept.md（点の監査、線の現実 の
末尾段落）。L1 = confidence 3 軸、L2 = source commitment、L3 = 意味的監査（protocol 外）。
dplaas.oss の origin 規範記述本体は本 catalog の commitment.* rules に対応あり
（derived_from / source_root / source_root_canonical / 構築手順 / 外部参照の除外）。
