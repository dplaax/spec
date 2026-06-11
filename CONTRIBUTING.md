# Contributing to the dPLaaX Specification

dPLaaX spec へのコントリビューションと public review を歓迎する。
本書は提案の出し方と、この repo 特有の規律を説明する。

## Public review

- 規範内容（rule の statement・vector の期待値）への疑義・反例・曖昧さの指摘は
  **Issue** で受け付ける。最も価値が高いのは「この rule のこの解釈とこの解釈が
  両立してしまう」「この vector の期待値はこの実装では再現できない」という具体例。
- 設計判断への異論は、何が壊れるか（相互運用・監査可能性・判定可能性のどれが、
  どう）まで書かれていると検討が速い。

## 変更提案（Pull Request）

1. **規範は 3 artifact のみ** — `rules/`（挙動・判定）、`schemas/`（wire shape）、
   `vectors/`（期待入出力）。markdown は non-normative であり、規範の変更は
   必ず rule / schema / vector の変更として表現する（→ [README.md](README.md)）。
2. **rule の statement は 256 文字以内・RFC 2119 規範語を含む・他所で再表現しない**。
   notes は non-normative（規範語を含むと lint が落とす）。
3. **挙動規範の変更には vector を添える** — 新 rule は 1 本以上、意味変更は
   既存 vector の期待値変更として表現する（= 意味変更とみなされる。
   → [VERSIONING.md](VERSIONING.md)）。
4. **lint green を維持する**: `python3 tools/lint.py`
5. vector の期待値（hash・Merkle root 等）は spec の規則から導出し、可能なら
   独立実装で再計算して確認する。導出過程を PR 説明に書く。

## 互換性の単位

互換性は **rule の `id` と statement の意味**で測る。ファイル配置・行番号・
markdown は規範外。0.x では rule の削除・意味変更も minor で許容される —
詳細は [VERSIONING.md](VERSIONING.md)。

## ガバナンス

現状は maintainer 裁量で判断し、議論は Issue / PR 上で公開で行う。
コントリビュータの増加に応じて、意思決定プロセス（rule の昇格判断・
breaking 判断の合議体制）を段階的に明文化する予定。提案があれば Issue へ。

## License

コントリビューションは [Apache License 2.0](LICENSE) の下で提供されたものとみなす。
