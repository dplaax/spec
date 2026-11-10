# formal — models of the protocol's properties

This directory holds formal models of properties the dPLaaX protocol is meant
to have, and the tooling that checks them. It is **non-normative**: the
normative content of this specification lives in `rules/`, `schemas/` and
`vectors/` only (see [CONTRIBUTING.md](../CONTRIBUTING.md)). A model here
binds each of its lemmas to rule ids; a lemma says nothing a rule does not
already say, it shows whether what the rules say holds against an attacker.

| model | tool | subject |
| --- | --- | --- |
| [`tamarin/chain.spthy`](tamarin/chain.spthy) | Tamarin 1.12.0 (with Maude 3.5.1) | the authentication of a provenance chain: signatures, links, compromised keys |

## Contract of `chain.spthy`

A model is only as good as the assumptions it is read under. These are the
ones `chain.spthy` makes; the model's header comment says the same.

- **Attacker.** The network is the attacker's (Dolev-Yao): every message is
  read, replayed, altered and composed at will.
- **Trusted.** The verifier, which is never taken over; hashing, which has
  no collisions; signatures, which cannot be forged without the key.
- **Open to compromise.** Any process's signing key, through the rule
  `CompromiseProcess`, which hands the key to the attacker and records
  `Compromised(P)`.
- **Persistence and time.** None. Clocks, `proof.created` and its ordering
  are outside the model.
- **Acceptance events.** `Accepted(b, P)`: the verifier accepted body `b` as
  signed by process `P`. `Linked(b2, a1, out1)`: the verifier accepted `b2`
  as the successor of the accepted credential at body address `a1` whose
  `outputHash` is `out1`.
- **Shape.** A credential's body is `<'cred', P, inp, out, prev>`: issuer,
  `inputHash`, `outputHash`, `previousCredential`. `prev` is `'origin'` for a
  chain origin and otherwise the predecessor's body address `h(b1)`, the hash
  of the proof-excluded body. The signature is outside the body, so a body
  signed again keeps its address.
- **Not modelled.** Delegation (Owner, Pipeline), time and ordering, the
  source commitment, DID resolution (public keys reach the verifier
  directly), key rotation, the wire variant id, and the data behind the
  hashes (`inp` and `out` are the attacker's to choose). The issuer of a
  successor does not check its predecessor's signature: the weakest
  assumption, since verification is the verifier's duty.

## Lemmas, rules and implementation

| lemma | kind | property | rule ids / implementation |
| --- | --- | --- | --- |
| `executable_chain` | exists-trace | an origin and a successor are accepted with no key compromised (reachability) | — |
| `executable_fan_out` | exists-trace | two successors of one predecessor are both accepted | `chain.trigger.fan-out` |
| `executable_after_reissue` | exists-trace | a chain still proceeds after a re-signing event (that the address is the body's and not the proof's holds by construction, `h(b)`) | `identity.body-address` |
| `signer_authenticity` | all-traces | a credential accepted as `P`'s was issued by `P`, or `P`'s key was compromised first | `signer.proof.structure`; provin.oss `vc.Verifier.Verify` (signer-authenticity axis) |
| `forgery_after_compromise` | exists-trace | with `P`'s key, the attacker has a credential accepted as `P`'s that `P` never issued: the exception in `signer_authenticity` is live | — |
| `forged_predecessor_extended` | exists-trace | a forged origin under a leaked key is accepted and an uncompromised process's successor is linked to it: the reach of the exception | — |
| `no_repointing` | all-traces | a successor linked as an uncompromised `P2`'s names the predecessor's address as `previousCredential`, its `outputHash` as `inputHash`, and was issued so by `P2`; needs the signature check and the link check together | `chain.data-flow.continuity`, `credential.subject.input-hash`, `credential.subject.output-hash`, `credential.subject.previous-credential`, `credential.prev.content-hash`; provin.oss `vc.ValidateChainLinks` within `vc.VerifyChain` |
| `link_integrity` | all-traces | the verifier's link check is present: structural, the pattern of `VerifyNext`, proved without attacker reasoning; the `SkipLinkCheck` control removes it | provin.oss `vc.ValidateChainLinks` |

The exists-trace lemmas are there so that the all-traces lemmas are not
vacuous: a safety property holds trivially of a model in which nothing is ever
accepted, and an exception nobody can reach is no exception. `link_integrity`
on its own establishes nothing against an attacker; re-pointing is ruled out
by `no_repointing`, which rests on `signer_authenticity` and on that check.

### In the code

provin.oss's `vc.VerifyChain` returns a graded verdict, not accept or
reject. `Accepted(b, P)` is a credential whose per-credential verification
reports the signer-authenticity axis verified, with `P` the issuer the proof's
verification method resolves to; `Linked(b2, a1, out1)` is a chain whose
`firstBrokenLink` is nil at `b2`, with `a1` the predecessor's content address
and `out1` its `outputHash`. The model's `!Chain` keeps every credential the
verifier ever accepted, so a successor may be linked to any of them; the code
links only within the chain it is handed. That is an over-approximation of
the code, sound for the properties here.

## Results

A lemma is in one of five states: **proved**; **refuted as expected** (a
negative control); **refuted, a design gap**; **unresolved** (the search did
not finish, timed out, or the model is ill-formed); **not started**. An
unresolved lemma does not count as proved. It is recorded here and the model
is still merged; by the next release it is proved, weakened, or dropped. A
refutation that is not expected fails CI.

Each model keeps the record of what each of its builds is expected to give
beside it, in `<model>.expected.tsv` (here
[`tamarin/chain.expected.tsv`](tamarin/chain.expected.tsv)); `check.sh`
compares against it, and a lemma absent from the file is expected to be
proved.

| build | lemma | state |
| --- | --- | --- |
| default | all eight | proved |
| `SkipLinkCheck` (the verifier reads neither `previousCredential` nor `inputHash` against the credential it extends) | `no_repointing`, `link_integrity` | refuted as expected |
| `SkipLinkCheck` | the other six | proved |

Unresolved: none.

## Running the checks

```sh
formal/tamarin/check.sh                       # every model, its default build
formal/tamarin/check.sh chain                 # one model, its default build
formal/tamarin/check.sh chain SkipLinkCheck   # one model, a negative control
TIMEOUT=120 formal/tamarin/check.sh chain     # seconds per lemma (600 by default)
```

`check.sh [MODEL [FLAG]]` runs `tamarin-prover` on each lemma of
`MODEL.spthy` in a process of its own, with `-D=FLAG` when a flag is given,
reads the prover's summary (its exit code is 0 for a refuted lemma too),
classes the result, and exits 0 only when every lemma has the result
`MODEL.expected.tsv` names. A lemma that runs out of time is unresolved, not
refuted. A `FLAG` that `MODEL.expected.tsv` does not name as a build is
refused: `tamarin-prover` ignores a flag the model does not use, so a
misspelled negative control would otherwise pass as the default model.

Tools: Tamarin 1.12.0 and Maude 3.5.1, the versions CI pins by SHA-256
(`.github/workflows/formal.yml`). On macOS:
`brew install tamarin-prover/tap/tamarin-prover` (Maude comes with it).

## Review

A pull request that changes a model, or the code a model's contract describes
(provin.oss `vc.VerifyChain`, `vc.ValidateChainLinks`), is reviewed for
whether the contract above still holds of the code. CI runs the models only
when `formal/` or the workflow changes; the review carries the rest.

Where a model and a rule disagree, neither wins by default: the disagreement
is judged, the rule, the model or the code is found to be the one in error,
and the outcome is recorded in the rule or in the decision record.

## Relation to provin.4s-intent

provin.4s-intent keeps its own Tamarin model of the pre-execution decision
(`verification/tamarin/intent.spthy`), which abstracts stage records in the
same shape as the credentials here. That model is to cite this one, once this
one is merged; the dependency runs one way, from 4s-intent to dPLaaX and
provin, never back.
