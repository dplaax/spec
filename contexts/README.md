# contexts/ — JSON-LD context 文書の SoT

dplaax protocol context の正規文書。**byte 単位で正規**であり、実装はここからの
byte-exact コピーを compile-time embed する（runtime fetch 禁止）。`@context` 配列は
署名スコープ内のバイト列として効くため、実装間の byte 差異は hash 分断
（partition trap）を引き起こす — vendoring 先は sha256 固定テストで drift を防ぐこと。

## 所有モデル（Model A、2026-06-11 確定）

二層構造:

1. **protocol context（本ディレクトリ）** — dplaax wire キー → IRI の写像。
   protocol が所有し、profile 間で同一。
2. **profile 拡張 context（各 profile が発行、正規は profile の SoT 側）** —
   profile 所有の custom subject field の term と、claim namespace prefix の接地
   （prefix → URL 写像、→ `credential.claim.grounding`）。protocol term の再定義は
   不可（`@protected` が機械的にも阻止する）。例: provin profile context の正規は
   provin.oss `packages/vc/contexts/provin-v1.jsonld`。

claim 値（`provin:filter` 等）は wire 上の文字列値であり context の対象外 —
意味の釘付けは profile の claim registry が担う（→ rules/credential.yaml の
`credential.claim.*`）。

## ファイル

| file | URI | sha256 |
|---|---|---|
| `v1.jsonld` | `https://poc.dplaax.io/vc/v1` | `4f79e1f18e257de0a822668b63b625831c37788e1e45441a01b48c53f4c5e6b2` |

- URI の `poc.` は tier marker — poc tier では byte レベルの進化を明示的に許容する。
  GA 時に `https://dplaax.io/vc/v1` へ昇格し、以降は不変（immutable）。
- `transformationClaim` は `@type: "@vocab"` で定義 — claim 値（compact IRI）が
  JSON-LD 展開で接地 URL 配下の語彙 IRI に解決され、(接地 URL, label) の同一性が
  JSON-LD/RDF 層でも機械的に成立する（→ `credential.claim.grounding`）。
- 文書を変更したら本表の sha256 を更新し、vendoring 先
  （provin.oss `packages/vc/contexts/`）へ byte-exact で同期する。
