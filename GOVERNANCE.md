# Governance

How decisions about this specification are made, by whom, and what happens
when that has to change. Complements [VERSIONING.md](VERSIONING.md) (what a
change breaks) and [CONTRIBUTING.md](CONTRIBUTING.md) (how to propose one).

## Roles

- **Maintainer** — currently one: [1o1 Co. Ltd.](https://1o1.co.jp/). The
  maintainer merges changes, cuts tags, and owns the `dplaax.dev` namespace
  publish root (`site/`).
- **Contributors** — anyone, through public Issues and pull requests. All
  discussion is public; there is no private decision channel.

## Change classes and required procedure

| Class | Examples | Procedure |
| --- | --- | --- |
| Editorial | prose clarification, typo, link | PR; maintainer merge |
| Additive | new rule (`status: todo`/`draft`), new vectors | Issue describing the norm, then a PR carrying the rule and its vectors; maintainer merge |
| Semantic | changing what an existing rule id asserts | Public proposal issue stating the compatibility impact per [VERSIONING.md](VERSIONING.md); explicit maintainer approval recorded on the issue |
| Namespace | anything under the published `site/` paths | Frozen once shipped — a semantic change requires a NEW path (`/v2`, a new grant name), never mutation of an existing one |

## Rule promotion: draft → stable

A rule is promoted from `draft` to `stable` when its conformance vectors are
passed by **two independent implementations**. Until a second implementation
exists, rules stay `draft` — deliberately: the promotion criterion doubles as
a standing invitation for that second implementation. (`todo → draft`
promotion freezes the rule id — see the README's id discipline.)

## Decision method

Single-maintainer discretion, exercised in public: proposals, objections, and
the decision itself are recorded on the issue that carries them. Before a
second maintainer from another organization lands, this document will be
revised to a consensus model with explicit escalation rules — single-company
authority is not the intended end state.

## Succession and forks

- If the maintainer is unresponsive for **six months** to a good-faith
  contact attempt (a public issue plus the contact routes published by the
  maintainer), any party may fork and continue under the Apache-2.0 terms.
  Nothing in this project impedes a fork.
- Already-issued credentials do not depend on this repository's fate for
  verification: the JSON-LD contexts are sha256-pinned and embedded in
  evidence bundles, so offline verification survives the namespace. The
  continuity plan for live resolution of `dplaax.dev` is tracked as its own
  workstream.

## IPR

Inbound = outbound: contributions are accepted under the repository's
Apache-2.0 license, which carries an express patent grant. A DCO sign-off
requirement may be added later; it is not required today.
