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
- この file は自身の URI `https://dplaax.dev/vc/v1` でも byte-exact で**配信**される:
  deploy の workflow（`.github/workflows/deploy.yml`）が deploy 時に `/vc/v1` へ
  写し、配信する bytes の sha256 が上の pin と違えば build を落とす。よって
  `contexts/v1.jsonld` は、この repo が配信する識別子、provin.oss の vendor の写し、
  これを埋め込むすべての実装という 3 つの利用者の唯一の元で、sha256 も 1 つ。

## branch の context（`/vc/branches/`）

branch の context は、protocol の context のある版（base）の上に、1 つの機能の語を
置く。base を凍結したまま、機能の語を定義して試せるようにするため。

- **path.** `contexts/branches/<base>/<feature>/<stamp>.jsonld` を
  `https://dplaax.dev/vc/branches/<base>/<feature>/<stamp>` で byte-exact に配信する。
  `<stamp>` は snapshot を凍結した UTC の時刻（`YYYYMMDDHHmm`）。stamp の無い path は配信しない。
- **凍結.** 各 snapshot は `v1.jsonld` と同じく、一度出したら凍結。変えるときは新しい
  stamp の snapshot を出す。sha256 は `contexts/branches/SHA256SUMS` に固定し、deploy の
  workflow が配信する bytes を照らす。
- **branch の中は足すだけ.** 後の snapshot は前の snapshot のすべての語を同じ定義のまま
  保ち、語を足すだけ。どの snapshot の下の文書も最新の下で同じ意味になる。意味の変わる
  語は別の名前の branch に置く。
- **base と並べる.** branch の語は base の語を定義し直さない。文書は base の context、
  次に branch の context を並べる（key binding の `@context` は
  `[credentials v2, dplaax v1, …/vc/branches/v1/keybinding/<stamp>]`）。
- **次の base へ.** branch の規則が確かめられたら（規則の `stable` への昇格が目安）、
  最新の snapshot を同じ IRI のまま次の base（`/vc/v2`）にまとめる。出した snapshot は
  配信を続け、実装は埋め込んだ写しを保つので、それを指す credential の意味は変わらない。
- **vendoring.** branch の語を処理する実装は、読む snapshot をそれぞれ byte-exact に
  埋め込み、`SHA256SUMS` で固定する。

| branch | snapshot | 最初の URI | sha256 |
|---|---|---|---|
| `v1/keybinding` | `202611101543` | `https://dplaax.dev/vc/branches/v1/keybinding/202611101543` | `cc07379a021cad29b2e8f5c137a2d6c185e283cc523c7d59ef360b58f6594916` |

key binding の branch は `KeyBindingCredential` と、その subject の `kind`、`roles`
（`@set`。役割が 1 つでも配列のまま）、`audience`（`@id`。relying party の DID）、
`keyClass`、`key`、`keyId`、`publicKeyJwk`（`@json`。JWK をそのまま保つ）を定義する。
`kind`・`roles`・`keyClass`・`keyId` の値は文字列のまま（IRI として読まない）。前の 3 つの
語彙は profile のもの、key id は名前だから。語は base と同じく
`https://dplaax.dev/vocab#` の下の完全な IRI。
