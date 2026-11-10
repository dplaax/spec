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
- この文書は変えない。新しい語は branch の context（下記）か次の base の版に置く。
  実装は byte-exact に vendor し（provin.oss `vc/contexts/`）、上の sha256 で固定する。
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
  `<stamp>` は UTC の時刻（`YYYYMMDDHHmm`）で、snapshot を足す pull request の中で決め
  （merge や deploy の時刻ではない）、その branch の既存のどの snapshot より後にする。
  より新しい snapshot を越えて rebase した snapshot は stamp を付け直す。stamp の無い
  path は配信せず、最新を指す別名も作らない。
- **凍結.** snapshot は `develop` への merge（ほかの者が vendor し始める最初の時点）から、
  `v1.jsonld` と同じく凍結する。変えるときは新しい stamp の snapshot を出す。sha256 は
  `contexts/branches/SHA256SUMS` に 1 snapshot 1 行で固定する（path は `/vc/branches/`
  からの相対で `.jsonld` を付けない）。deploy は配信する bytes をこの pin で照らし、
  一度上げた snapshot は消さない。
- **branch の中は足すだけ.** 後の snapshot は前の snapshot のすべての語を同じ定義のまま
  保ち、語を足すだけ。前の snapshot が定義するどの語も、最新の下で同じ意味になる。意味の
  変わる語は別の名前の branch に置く。
- **base の上で 1 つの名前に 1 つの定義.** branch の語は base の語を定義し直さない。同じ
  base の複数の branch が定義する名前は、どの branch でも同じ定義にする。そうすれば branch
  を並べて使え、まとめて取り込める。文書は base の context、次に branch の context を並べる
  （key binding の `@context` は
  `[credentials v2, dplaax v1, …/vc/branches/v1/keybinding/<stamp>]`）。
- **次の base へ.** branch の規則が確かめられたら（規則の `stable` への昇格が目安）、
  最新の snapshot を同じ IRI のまま次の base（`/vc/v2`）にまとめる。規則が確かめられない
  branch はまとめない。出した snapshot は配信を続け、実装は埋め込んだ写しを保つので、
  それを指す credential の意味は変わらない。
- **実装.** credential を JSON-LD として展開する実装（たとえば eddsa-rdfc-2022 の検証者）は、
  埋め込んだ snapshot だけを読み（byte-exact、`SHA256SUMS` で固定）、context を取りに
  行かない（`signer.suite.rdfc-expansion-guard`）。埋め込んでいない snapshot を指す
  credential は、そこでは展開できない。JCS の proof（eddsa-jcs-2022）の検証者は context の
  文書を読まないので、規則によっては branch の snapshot を URI の形で受けてよい。
- **検査.** `tools/lint.py` が、path と stamp、pin、足すだけの順、1 つの名前に 1 つの定義、
  そして変更の元の ref（`DPLAAX_BASE_REF`、CI が渡す）に対して出した snapshot が変わって
  いないことを確かめる。

| snapshot | sha256 |
|---|---|
| `https://dplaax.dev/vc/branches/v1/keybinding/202611101543` | `cc07379a021cad29b2e8f5c137a2d6c185e283cc523c7d59ef360b58f6594916` |

key binding の branch は `KeyBindingCredential` と、その subject の `kind`、`roles`
（`@set`。役割が 1 つでも配列のまま）、`audience`（`@id`。relying party の DID）、
`keyClass`、`key`、`keyId`、`publicKeyJwk`（`@json`。JWK をそのまま保つ）を定義する。
`kind`・`roles`・`keyClass`・`keyId` の値は文字列のまま（IRI として読まない）。前の 3 つの
語彙は profile のもの、key id は名前だから。語は base と同じく
`https://dplaax.dev/vocab#` の下の完全な IRI。
