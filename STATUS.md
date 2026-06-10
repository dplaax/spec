# STATUS — 起草の現状（一時文書）

> 本ファイルは作業台帳であり spec の一部ではない。spec 安定後に削除する。
> tools/lint.py の走査対象外（規範語の引用が許される唯一の markdown）。

## 現状宣言（2026-06-10）

- 構造を rule catalog 方式へ全面改組（rules/ + schemas/ + vectors/、規律は README.md 参照）。
- 旧 6 セクション skeleton（docs/）は削除。旧 Layer 構造での起草蓄積はブランチ
  `drafts/v1_001` / `drafts/v1_002` に保存されている。
- **未転記の規範内容の台帳は、各 rule stub の `source` field に移行した**。
  `status: todo` の entry を grep すれば未転記一覧になる。転記完了で `source` を削除する。
- transformationType の open-world 規則（2026-06-10 設計会話起点）は
  `credential.transformation.open-world-namespaced` / `.open-world-bare` として
  最初の `status: draft` rule に転記済み。
- 名称: 本 repo は dplaax のみを定義する。旧 protocol 名・旧実装名の語彙は spec 本文に持ち込まない。

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
- 監査用列挙 API（issuer / ingress set でのクエリ面）— サービス API 側、未設計。
  spec scope 外（wire profile / 実装 repo 側）の可能性が高い。
- JSON-LD context 文書の実体（`https://poc.dplaax.io/vc/v1`）— provin.oss
  `packages/vc/contexts/` も空。spec とどちらが先に持つか未決。
- **`generate` のベース語彙昇格パス**（2026-06-10 設計会話起点）: 生成的派生（出力の情報源が
  入力集合に閉じない = aggregate の閉じた畳み込みと意味論が異なる）は profile 非依存の
  普遍要件。wire profile 拡張（`provin:generate`、provin 側 backlog で管理）として先行させ、
  語彙が安定した時点で無印 `generate` のベース語彙入りを提案。昇格時はエイリアス対応表を
  rules に明記する。→ `credential.transformation.base-vocabulary` の転記時に notes へ引き継ぐ。

## trust model（L1/L2/L3）の行き先

L2（audit reachability）は `rules/origin.yaml` の class 定義の前提。concept.md には技術記述を
置かない方針のため、規範部分は origin rules へ、非技術の動機部分のみ concept.md へ。
定義の転記元は dplaas.oss salvage（上記）。
