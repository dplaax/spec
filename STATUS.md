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
- vc_resolver 領域の rule file — drafts に下敷きあり、未 stub 化。
- 隣接クレデンシャル間の hash 連続性（outputHash と次の inputHash の一致）の規範化 —
  抽出時に言及はあったが出典の規範文が未特定。特定のうえ転記する。
- schema 参照の subject 内配置 — W3C VC Data Model の top-level credentialSchema 慣行からの
  意図的逸脱として rationale の明記が未了（`credential.schema-ref` の notes 参照）。
- cryptosuite lifecycle の補完候補（検証器ごとの allow-list / no-op identifier 禁止 /
  Deprecated の cutoff date 規則）— 旧 draft 由来、provin.oss に対応なし。取り込み判断未了。
- `registry.append-only` の出典は旧 draft のみ — provin.oss に対応実装が現れた時点で要突合。
- 監査用列挙 API（issuer / ingress set でのクエリ面）— サービス API 側、未設計。
  spec scope 外（wire profile / 実装 repo 側）の可能性が高い。
- JSON-LD context 文書の実体（`https://poc.dplaax.io/vc/v1`）— provin.oss
  `packages/vc/contexts/` も空。spec とどちらが先に持つか未決。
- `generate` のベース語彙昇格パス — `credential.transformation.base-vocabulary` の
  notes に移行済み（本台帳からは削除）。
- transformationType draft の「生成器は常時 FirstDrop」判断（draft 決定事項 3）—
  SourceCommitment 改組（上記 現状宣言 2026-06-11）により論拠の片方（位相反転で
  commitment が使えなくなる）が消滅し、**未決に戻した**。
  → 次項 transformationClaim 再構成で protocol 側は解消見込み（protocol は位相を
  claim に紐付けない。位相は trigger 規則が決める）。provin profile 側の表現は
  `docs/draft/dplaax-transformationType.md`（scope 側）の ⚠ 注記参照。
- **transformationType → transformationClaim 再構成（base 語彙の解体）** —
  方向確定（2026-06-11 設計会話）、影響実査・実施は未着手。
  **論拠（2 軸分離）**: 形状（prev × SourceCommitment）は改組後 wire パラメタで
  自明であり、フィールドの非冗長な仕事は「情報源についての主張 (claim)」のみ。
  型に位相を背負わせる `credential.transformation.aggregate-origin` は混同の名残。
  **方向**:
  (1) wire キー transformationType → transformationClaim 改名
  （Paper 01 §4.3 の語彙と乖離 — 乖離の記録必須）。
  (2) dplaax は claim の意味を固定しない。protocol に残すのは
  フィールドの存在 + 文法（`+` 結合 / `<namespace>:<label>` 形式、無印値全廃 =
  全 claim namespace 必須）+ **解釈デフォルト**:
  「検証器・監査者は、認識しない claim から閉世界推論を引き出してはならない
  (MUST NOT)。未知 claim = 開世界として扱う」。
  **閉世界/開世界の定義（CWA/OWA）**: source_root に含まれない =
  閉世界 claim では「寄与していない」と推論可（除外推論・クリアランスが可能、
  申告漏れは嘘であり ingress 突合で検出・帰責対象）。開世界 claim では「不明」
  （包含方向の束縛・改ざん検出は両者共通で保たれる。失われるのは除外推論のみ。
  申告漏れは嘘ですらない — 完全性を主張していないため）。
  未知 claim を閉として扱うと監査者が偽クリアランスを発行し得るため、
  開がデフォルト = 強い結論（除外）には claim の意味の積極的認識を要求する
  fail-closed 構造。
  (3) `credential.transformation.base-vocabulary` の 3 値釘付けを解体、
  `aggregate-origin` を protocol 規則から削除（provin profile 規則への降格判断含む）。
  (4) provin profile が 5 claim（filter / convert / aggregate / enrich / generate）の
  意味（閉/開、内容関係）を釘付け。generate のベース語彙昇格パスは消滅
  （`credential.transformation.base-vocabulary` notes の昇格記述も削除対象）。
  profile 内で意味と不整合な claim（畳み込みを convert と宣言等）は虚偽の主張として
  検出・帰責対象 — 嘘の検出可能性は profile 層で保たれる。
  **波及見込み（未実査）**: ppc draft（drafts/v1_00x）、provin.oss wire 定数 +
  TransformationType 型 + GLOSSARY、JSON-LD context、transformationType
  incubation draft の全面改訂、rules/credential.yaml の transformation 節改組。
  実施手順は SourceCommitment 改組と同じ: 台帳化（本項）→ grep 実査 → lock-step 実施。

## trust model（L1/L2/L3）の行き先

L2（audit reachability）は `rules/origin.yaml` の class 定義の前提。concept.md には技術記述を
置かない方針のため、規範部分は origin rules へ、非技術の動機部分のみ concept.md へ。
定義の転記元は dplaas.oss salvage（上記）。
