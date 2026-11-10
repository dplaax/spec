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
| [`tamarin/keybinding.spthy`](tamarin/keybinding.spthy) | Tamarin 1.12.0 (with Maude 3.5.1) | key bindings and their revocation lists: whose binding a relying party takes, for whom, and whether a revocation can be undone |

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

## `keybinding.spthy`

### Contract

The model's header comment says the same.

- **Attacker.** The network is the attacker's (Dolev-Yao).
- **Trusted.** The relying party's verifier, which is never taken over;
  signatures, which cannot be forged without the key.
- **Open to compromise.** An issuer's issuance key, through the rule
  `CompromiseIssuer`, which records `Compromised(I)`. An issuer's other key,
  one it signs other credentials with, signs whatever the attacker asks
  (`OtherKeySigns`).
- **Issuers' lists.** An issuer issues lists of any `validFrom` and either
  mark: its state may be restored to an older one, so nothing rests on its
  lists only moving forward. What is shown is that the list the relying
  party holds guards its marks.
- **The relying party.** It trusts an issuer when it holds a trust anchor
  for it (`!Anchor(V, I, pk)`, the issuer's issuance key), and holds one
  list per id, which a later list replaces. The list it holds is a state,
  `Held(~sid, ...)`, made when the first list under the id is held and
  carried through every later step under the same `~sid`, so that one state
  exists at a time. It looks a list up by its id, as
  `keybinding.status.entry` states.
- **Shape.** A binding's body is `<'binding', I, S, k, A, L>`: issuer,
  subject, bound key, audience, list. A list's id is a DID URL of its
  issuer, `<I, f>` for `I#f`. A list is abstracted to the one entry a
  binding has in it: `<'list', I, L, vf, mark>`, with `vf` a natural number
  so that lists are ordered and `mark` `'active'` or `'revoked'`. Its content
  hash is `h(body)`.
- **Persistence.** The held list is never lost: from the first list under an
  id on, the relying party holds one, and nothing in the model drops it.
  Keeping it so across a restart is the relying party's to do, outside the
  model.
- **Time.** None. A binding's period and its bound (`keybinding.validity`),
  a list's period and freshness (`keybinding.status-list.period`,
  `keybinding.status-list.fresh`) and the clock skew are outside the model,
  and so are DID resolution (public keys reach the verifier directly), key
  rotation, the issuer's scope, and how a list's bits are compressed.
  Receiving the held list again changes nothing and is not modelled.
- **Events.** `Accepted(V, I, S, k, A, L)`: `V` accepted `I`'s binding of `k`
  to `S` for `A` under `L`. `JudgedUnder(V, I, L, J)`: it was judged under
  the list `V` holds under `L`, held in `J`'s name. `AcceptedUnder(sid, m)`:
  it was accepted under the held state `sid`, whose mark was `m`.
  `Holds(V, L, I, vf, m)`: `V` took a list of `I` as the one it holds under
  `L`. `St(sid, V, L, J, vf, mark)`: each state of that list.

### Lemmas, rules and implementation

| lemma | kind | property | rule ids / implementation |
| --- | --- | --- | --- |
| `executable_binding` | exists-trace | a binding is accepted with no key compromised (reachability) | — |
| `executable_replace` | exists-trace | a later list replaces the held one with no key compromised | — |
| `key_from_trusted_issuer` | all-traces | a binding accepted is of an issuer the relying party's trust anchor names, and that issuer bound the key to the subject, or its issuance key was compromised first | `keybinding.issuer` (the anchor: `SkipAnchorCheck`; the issuance key: `AnyIssuerKey`); provin.oss `keybinding.Verifier.VerifyBinding` |
| `issuer_compromise_exception` | exists-trace | with an issuer's issuance key, a binding it never made is accepted: the exception is live | — |
| `bound_to_audience` | all-traces | a binding accepted was bound for this relying party, or the issuer's key was compromised first | `keybinding.audience` (`SkipAudienceCheck`; `AnyIssuerKey` too, a forged binding names any audience); provin.oss `VerifyBinding` |
| `executable_revocation` | exists-trace | the relying party holds a list that marks the entry, with no key compromised | — |
| `list_authentic` | all-traces | a list the relying party holds was issued, as it is held, by its issuer, or that issuer's issuance key was compromised first | `keybinding.issuer` (a list's key: `AnyListKey`); provin.oss `VerifyStatusList` |
| `list_of_its_issuer` | all-traces | a binding is judged only under a list held in its own issuer's name, whoever else's key is compromised | `keybinding.status-list.id` (`AnyListIssuer`), `keybinding.status.entry` (the binding names a list of its issuer: `AnyEntryList`); provin.oss `VerifyStatusList` (the id as a DID URL of the issuer), `VerifyBinding` (the list held is the binding's) |
| `revocation_not_cleared` | all-traces | once the list held under an id marks the entry, every later state of it does, by a later list or an earlier one | `keybinding.status-list.monotonic` (`AcceptClearedMark`); provin.oss `VerifyStatusList` |
| `accept_needs_active` | all-traces | a binding is accepted only under a held list that leaves its entry active | `keybinding.status.entry` (`AcceptAnyMark`); provin.oss `VerifyBinding` |
| `same_validfrom_same_content` | all-traces | a list replaces the held one only when it is later; one of the same `validFrom` is the held one only with the same content hash | `keybinding.status-list.monotonic`, `keybinding.status-list.content-hash` (`SameValidFromAnyContent`); provin.oss `VerifyStatusList` |

`list_authentic` and `list_of_its_issuer` together say that a binding is
judged only under a list its own issuer issued: the first by the list's
signature, the second by its id. `revocation_not_cleared` and
`accept_needs_active` together say that no binding under a list id is
accepted once the relying party has held a list under it that marks the
entry: acceptance is a step of the held state, and every state after one
that marks the entry marks it. The single lemma that says so directly did
not finish in several minutes of search, so it is stated as the two.

`revocation_not_cleared` is proved by induction over the states of the held
list; the one state at a time (`Held` under one `~sid`) is what makes the
induction go through, and Tamarin's `S` heuristic proves it in seconds
(`[heuristic=S]`). `same_validfrom_same_content` and `accept_needs_active`
hold by the relying party's patterns, like chain's `link_integrity`: they are
what the rules state for one step, and each is refuted by the control that
drops that step's check. The content hash being a function of the content is
carried by `h(body)`; that the hash ignores the compression of the bits is a
property of `keybinding.status-list.content-hash`, pinned by its vectors,
not modelled.

### In the code

`Accepted(V, I, S, k, A, L)` is provin.oss's `keybinding.Verifier.VerifyBinding`
returning a binding, with `V` the Verifier's audience and the anchor's issuer
`I`. `!Anchor(V, I, pk)` stands for the `keybinding.Anchor` of `I`: its
issuance keys, of which `VerifyBinding` and `VerifyStatusList` accept only a
signature under one, by the anchor's issuer. `HoldList` and the replacing
rules are `VerifyStatusList` with no held list and with one: the list's id
read as a DID URL of the issuer, a list of another `validFrom` than the held
one taken only when later (`ErrStatusListRewound` otherwise), the same
`validFrom` and content hash returning the held list, and a later list that
unmarks an entry refused (`ErrStatusListRevocationCleared`). `Accept`'s use
of the held list is `VerifyBinding`'s check that the list held is the
binding's and does not mark the binding's index (`ErrRevoked`). In the code
the list held is also tied to the binding's issuer by its own issuer, the
anchor's, so the code does not rest on the id alone as the model's relying
party does.

provin.oss's `Verifier` holds no state: `Held` is its caller's. The caller
passes the list it holds to `VerifyStatusList` and `VerifyBinding`, keeps
what `VerifyStatusList` returns as the list held, one per issuer and list
id, never drops it, and restores it after a restart with
`RestoreStatusList`. The model rests on the caller doing so. The time checks
of both functions, `RestoreStatusList` itself, and a held list whose key has
left the anchor (key rotation) are outside the model.

### Results

Expectations: [`tamarin/keybinding.expected.tsv`](tamarin/keybinding.expected.tsv).

| build | lemma | state |
| --- | --- | --- |
| default | all eleven | proved |
| `SkipAnchorCheck` (a binding and a first list are taken under any issuer's issuance key, anchored or not) | `key_from_trusted_issuer` | refuted as expected |
| `AnyIssuerKey` (a binding is taken under any key of the anchored issuer) | `key_from_trusted_issuer`, `bound_to_audience` | refuted as expected |
| `SkipAudienceCheck` (a binding for any relying party is taken) | `bound_to_audience` | refuted as expected |
| `AnyEntryList` (a binding may name a list of another issuer) | `list_of_its_issuer` | refuted as expected |
| `AnyListIssuer` (a list is held under an id that is not a DID URL of its issuer) | `list_of_its_issuer` | refuted as expected |
| `AnyListKey` (a first list is taken under any key of the anchored issuer) | `list_authentic` | refuted as expected |
| `AcceptAnyMark` (a binding is accepted whatever the held list marks) | `accept_needs_active` | refuted as expected |
| `AcceptClearedMark` (a later list may leave active an entry the held list marks) | `revocation_not_cleared` | refuted as expected |
| `SameValidFromAnyContent` (a list of the held one's `validFrom` replaces it whatever its content hash; a revoked entry still stays revoked) | `same_validfrom_same_content` | refuted as expected |
| each control | the other lemmas | proved |

Unresolved: none. Every lemma takes under 15 seconds per build on a laptop.

Each control adds a rule beside a default rule of the relying party and
keeps every other check, so that the added rule together with the default
one is the relying party with that one check dropped or relaxed; a
refutation under the control then shows the lemma rests on that check.

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
the registry's use of a delegation, `keybinding.Verifier`'s `VerifyBinding`
and `VerifyStatusList`), is reviewed for whether the contract
above still holds of the code. CI runs the models only when `formal/` or the
workflow changes; the review carries the rest.

Where a model and a rule disagree, neither wins by default: the disagreement
is judged, the rule, the model or the code is found to be the one in error,
and the outcome is recorded in the rule or in the decision record.

## Relation to provin.4s-intent

provin.4s-intent, a product built on provin, can cite the models here. The
dependency runs one way, from 4s-intent to dPLaaX and provin, never back.
