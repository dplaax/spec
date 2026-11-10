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
| [`tamarin/delegation.spthy`](tamarin/delegation.spthy) | Tamarin 1.12.0 (with Maude 3.5.1) | delegation from an Owner to its Pipelines and Processes: who can delegate, over what, and what a delegation is used for |

## Result states

A lemma is in one of five states: **proved**; **refuted as expected** (a
negative control); **refuted, a design gap**; **unresolved** (the search did
not finish, timed out, or the model is ill-formed); **not started**. An
unresolved lemma does not count as proved. It is recorded here and the model
is still merged; by the next release it is proved, weakened, or dropped. A
refutation that is not expected fails CI.

Each model keeps the record of what each of its builds is expected to give
beside it, in `<model>.expected.tsv`; `check.sh` compares against it, and a
lemma absent from the file is expected to be proved. A build is the default
model or a negative control, a preprocessor flag that drops or relaxes one
check, or breaks one of the model's assumptions.

The exists-trace lemmas of each model are there so that its all-traces lemmas
are not vacuous: a safety property holds trivially of a model in which nothing
is ever accepted, and an exception nobody can reach is no exception.

## `chain.spthy`

### Contract

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
- **Not modelled.** Delegation (`delegation.spthy`), time and ordering, the
  source commitment, DID resolution (public keys reach the verifier
  directly), key rotation, the wire variant id, and the data behind the
  hashes (`inp` and `out` are the attacker's to choose). The issuer of a
  successor does not check its predecessor's signature: the weakest
  assumption, since verification is the verifier's duty.

### Lemmas, rules and implementation

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

`link_integrity` on its own establishes nothing against an attacker;
re-pointing is ruled out by `no_repointing`, which rests on
`signer_authenticity` and on that check.

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

### Results

Expectations: [`tamarin/chain.expected.tsv`](tamarin/chain.expected.tsv).

| build | lemma | state |
| --- | --- | --- |
| default | all eight | proved |
| `SkipLinkCheck` (the verifier reads neither `previousCredential` nor `inputHash` against the credential it extends) | `no_repointing`, `link_integrity` | refuted as expected |
| `SkipLinkCheck` | the other six | proved |

Unresolved: none.

## `delegation.spthy`

### Contract

The model's header comment says the same.

- **Attacker.** The network is the attacker's (Dolev-Yao).
- **Trusted.** The verifier and the consumer, which are never taken over;
  signatures, which cannot be forged without the key.
- **Open to compromise.** Any identity's key, an Owner's, a Pipeline's or a
  Process's, through the rule `CompromiseIdentity`, which records
  `Compromised(D)`.
- **An Owner's key and the separation assumption.** Every signature an
  Owner's key makes says, in the bytes it signs, what it is for. The model
  has the key also sign authentication challenges the attacker chooses, as
  `<'authentication', m>` (`OwnerAuthenticates`): the case the proof-purpose
  check of `delegation.proof` guards against. Without the assumption no
  verifier check helps: `UntaggedOwnerSignature`, a key that also signs
  attacker-chosen bytes with no purpose in them, refutes both authority
  lemmas. In provin.oss an Owner's keys make two other kinds of signature,
  each separated by what it signs rather than by the purpose check: the
  `#auth` key signs wireauth's canonical view, a format of its own, and the
  `#signing` key makes assertion proofs over the Owner's own DID document,
  separated from a delegation by the credential's type. An Owner delegates
  whichever of its own Pipelines and Processes the attacker asks for: what is
  modelled is who can produce a delegation, not when an Owner chooses to.
- **Persistence and time.** None. `validFrom`, `proof.created`, revocation
  and the registry's liveness checks are outside the model.
- **Acceptance events.** `Authorized(X, O)`: the verifier accepted a
  delegation of `X`, whose Owner is `O`. `Registered(T, O)`: the consumer put
  `T` on record under `O` on the strength of an accepted delegation.
- **Shape.** Identities follow the did:dplaax structural hierarchy: an Owner
  `$O`, a Pipeline `<'pipeline', $O, $p>`, a Process
  `<'process', $O, $p, $q>`, so an identity's Owner is read from its DID. A
  delegation's body is `<'delegation', I, X, B>`: issuer, subject,
  `delegatedBy`. Its proof signs the body together with the proof's purpose,
  `<purpose, body>`, as a Data Integrity proof covers its own options.
- **Not modelled.** DID resolution (public keys reach the verifier
  directly), key rotation, the scope tokens of `delegation.scope` (the
  catalog fixes their shape, not their use, and the provin profile refuses a
  scoped delegation), the provenance chain (`chain.spthy`), and the
  registry's other checks (its own registry, liveness, duplicates).

### Lemmas, rules and implementation

| lemma | kind | property | rule ids / implementation |
| --- | --- | --- | --- |
| `executable_pipeline` | exists-trace | a Pipeline's delegation is accepted with no key compromised (reachability) | — |
| `executable_process` | exists-trace | a Process's delegation is accepted with no key compromised | — |
| `executable_registration` | exists-trace | a delegation puts its subject on record with no key compromised | — |
| `authority_from_own_owner` | all-traces | a delegation of `X` accepted under `X`'s Owner `O` was signed by `O`, or `O`'s key was compromised first: no other Owner and no Pipeline, even one whose key is compromised (the chain of authority does not extend), and no signature `O` made for another purpose yields one | `delegation.binding` (the issuer is the subject's Owner, and an Owner: `SkipSubjectOwnerCheck`, `AcceptControllerIssuer`), `delegation.proof` (the purpose: `AnyProofPurpose`; the verification method names the issuer: `AnyVerificationMethod`); provin.oss `delegation.Verify` |
| `owner_compromise_exception` | exists-trace | with `O`'s key, a delegation `O` never signed is accepted: the exception in `authority_from_own_owner` is live | — |
| `registered_only_as_delegated` | all-traces | `T` is on record under `O` only if `O` signed a delegation of `T`, or `O`'s key was compromised first: a delegation is used only for the subject it names, under that subject's Owner | `delegation.use.subject-bound` (the target: `SkipTargetBinding`), and the rules of `authority_from_own_owner`; provin.oss `didregistry` (the delegation names exactly the target it registers) |
| `no_owner_subject` | all-traces | only a Pipeline or a Process of the Owner is accepted as a subject: structural, the verifier's patterns | `delegation.binding`; provin.oss `delegation.Verify` (`IsPipeline`, `IsProcess`) |

`authority_from_own_owner` and `registered_only_as_delegated` are what the
negative controls test; each control drops or relaxes one check, or breaks
the separation assumption, and refutes the lemmas that rest on it. Some of
what the rules ask is carried by the model's shape and tested by no control:
`delegatedBy` restating the issuer (`delegation.shape`) is a pattern of the
verifier, and no lemma depends on it, since the signature is the issuer's
already; the credential's type is the `'delegation'` tag; the scope tokens of
`delegation.scope` are not modelled. `no_owner_subject`, like chain's
`link_integrity`, holds by the verifier's patterns and on its own establishes
nothing against an attacker.

### In the code

`Authorized(X, O)` is provin.oss's `delegation.Verify` returning nil for a
credential whose `credentialSubject.id` is `X`, with `O` the Owner DID of `X`,
which `Verify` requires to equal the issuer. The model's verifier takes the
issuer's key from `!OwnerPk`, a key registered for an Owner DID, which stands
for `dplaax.RequireOwner`, for `Verify`'s check that the proof's
verification method names the issuer, and for the resolution of the issuer's
document with the key in its assertion relationship. `Verify`'s checks of
the proof's type and cryptosuite, of the credential's type tokens and of
`delegatedBy` are carried by the model's shape (see above), and its refusal
of a scoped delegation is outside the model. `Registered(T, O)` is the registry's
`issue` going past its binding of the delegation's subject to `T` and past
`Verify`. `!Valid` hands the verifier's result to the consumer.

### Results

Expectations: [`tamarin/delegation.expected.tsv`](tamarin/delegation.expected.tsv).

| build | lemma | state |
| --- | --- | --- |
| default | all seven | proved |
| `SkipSubjectOwnerCheck` (any Owner is taken as issuer, not the subject's) | `authority_from_own_owner`, `registered_only_as_delegated` | refuted as expected |
| `AcceptControllerIssuer` (a Process's Pipeline, its controller in the registry, may delegate it) | `authority_from_own_owner`, `registered_only_as_delegated` | refuted as expected |
| `AnyProofPurpose` (the proof's purpose is not checked) | `authority_from_own_owner`, `registered_only_as_delegated` | refuted as expected |
| `AnyVerificationMethod` (the proof is checked under the key of whatever identity its verification method names) | `authority_from_own_owner`, `registered_only_as_delegated` | refuted as expected |
| `UntaggedOwnerSignature` (the Owner's key also signs attacker-chosen bytes with no purpose in them: the separation assumption broken) | `authority_from_own_owner`, `registered_only_as_delegated` | refuted as expected |
| `SkipTargetBinding` (the consumer takes any accepted delegation as authority for any target) | `registered_only_as_delegated` | refuted as expected |
| each control | the other lemmas | proved |

Unresolved: none.

Each control adds a rule beside the default verifier or consumer rule, or
beside the Owner's signing rules. An added verifier or consumer rule contains
the default rule as its special case and keeps every other check, so the two
together are exactly the verifier or consumer with that one check dropped or
relaxed; a refutation under the control then shows the lemma rests on that
check.

## Running the checks

```sh
formal/tamarin/check.sh --all-builds                     # every build of every model, as CI runs it
formal/tamarin/check.sh --all-builds delegation          # every build of one model
formal/tamarin/check.sh                                  # every model, its default build
formal/tamarin/check.sh chain                            # one model, its default build (also: chain default)
formal/tamarin/check.sh chain SkipLinkCheck              # one model, a negative control
TIMEOUT=120 formal/tamarin/check.sh chain                # seconds per lemma (600 by default)
```

`check.sh [--all-builds] [MODEL [FLAG]]` runs `tamarin-prover` on each lemma
of `MODEL.spthy` in a process of its own, with `-D=FLAG` when a flag other
than `default` is given, reads the prover's summary (its exit code is 0 for a
refuted lemma too), classes the result, and exits 0 only when every lemma has
the result `MODEL.expected.tsv` names. A lemma that runs out of time is
unresolved, not refuted. `--all-builds` runs the default build and every
build the expectations name; a build whose results are not the expected ones
does not stop the others, and the last line lists every such build.

Before any lemma is proved, the model and its expectations are checked
against each other, so that neither can drift from the other unnoticed:

- each `#ifdef` names one flag (`tamarin-prover` would read `#ifdef A & B`
  as a condition, not as the build `A`);
- no lemma is inside an `#ifdef` (it would vanish from the other builds);
- every expected result is `verified`, `falsified` or `unresolved`;
- every lemma the expectations name is a lemma of the model;
- the model's `#ifdef` flags are exactly the builds the expectations name
  other than `default`, which may hold lines of its own for a design gap.

A `FLAG` the expectations do not name as a build is refused:
`tamarin-prover` ignores a flag the model does not use, so a misspelled
negative control would otherwise pass as the default model.

Tools: Tamarin 1.12.0 and Maude 3.5.1, the versions CI pins by SHA-256
(`.github/workflows/formal.yml`). On macOS:
`brew install tamarin-prover/tap/tamarin-prover` (Maude comes with it).

## Review

A pull request that changes a model, or the code a model's contract describes
(provin.oss `vc.VerifyChain`, `vc.ValidateChainLinks`, `delegation.Verify`,
the registry's use of a delegation), is reviewed for whether the contract
above still holds of the code. CI runs the models only when `formal/` or the
workflow changes; the review carries the rest.

Where a model and a rule disagree, neither wins by default: the disagreement
is judged, the rule, the model or the code is found to be the one in error,
and the outcome is recorded in the rule or in the decision record.

## Relation to provin.4s-intent

provin.4s-intent keeps its own Tamarin model of the pre-execution decision
(`verification/tamarin/intent.spthy`), which abstracts stage records in the
same shape as the credentials here. That model is to cite this one, once this
one is merged; the dependency runs one way, from 4s-intent to dPLaaX and
provin, never back.
