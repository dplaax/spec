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
   provin-line/profile.spec `contexts/v1.jsonld`。（同 repo が存在するまでは
   provin.oss `vc/contexts/provin-v1.jsonld` が正規だった — 書かれていない spec
   の代わりに実装が立っていた状態。文書は不変で、所有者だけが変わった。）

claim 値（`provin:filter` 等）は wire 上の文字列値であり context の対象外 —
意味の釘付けは profile の claim registry が担う（→ rules/credential.yaml の
`credential.claim.*`）。

## ファイル

| file | URI | sha256 |
|---|---|---|
| `v1.jsonld` | `https://dplaax.dev/vc/v1` | `9716bca789bdb1042451746800cc463a616a57817008001a3a895e88c0aff25f` |

- URI `https://dplaax.dev/vc/v1` は v0 wire 語彙として凍結され、以降は不変（immutable）。
  `@context` 配列は署名スコープに bytes で乗るため、付け替えは実装間の hash 分断
  ＝次 MAJOR 相当の破壊であり、互換変更ではない。
- `transformationClaim` は `@type: "@vocab"` で定義 — claim 値（compact IRI）が
  JSON-LD 展開で接地 URL 配下の語彙 IRI に解決され、(接地 URL, label) の同一性が
  JSON-LD/RDF 層でも機械的に成立する（→ `credential.claim.grounding`）。
- 文書を変更したら本表の sha256 を更新し、vendoring 先
  （provin.oss `vc/contexts/`）へ byte-exact で同期する。
