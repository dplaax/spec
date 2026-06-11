# dPLaaX — Concept

> This document is non-normative. The normative specification of dPLaaX is defined solely by rules/, schemas/, and vectors/ (→ [README.md](README.md)).
> This document addresses only *why* dPLaaX exists; it does not cover how it is implemented.

## What dPLaaX is

dPLaaX ("data PipeLine as a X" / "decentralized PipeLine as a X") is a protocol of boundary commitments. When data crosses the boundaries of organizations or systems, dPLaaX records at each boundary — in a tamper-evident form — who received what, what was done to it, and what was passed on, and makes that chain of records independently verifiable by third parties. The "X" is deliberately left open — Service, Substrate, Standard, and similar framings are all possible — to preserve flexibility in how the protocol is positioned.

"Data pipeline" is used here in a broad sense. It encompasses not only flows inside purpose-built pipeline products, but any phenomenon in which data crosses a boundary: supply-chain records, federated attribute information, audit logs, file handoffs, and more. The same protocol applies uniformly at every boundary, producing a consistent chain of records whether the boundaries fall within a single organization or span multiple organizations. dPLaaX defines the commitment protocol at each boundary; it does not define the transport layer that carries data.

With dPLaaX, a third party who has no prior contractual relationship with a data provider can still independently verify, for data that was conveyed under the protocol, the record of how that data was handled as it passed through a chain of boundaries.

What dPLaaX provides is authenticity and continuity of the record — nothing more. It does not guarantee the truth of the content: if the origin records an incorrect value, that value remains incorrect even when the provenance chain is complete. It does not, on its own, guarantee completeness: the existence of an unrecorded boundary cannot be proven from the records that remain. And "independently verifiable" is not unconditional — it rests on the verifier's choice of anchor of trust, namely how to trust the identity and authority of the recording parties. What dPLaaX changes is the basis for deciding where to place trust: that judgment can now rest on verified provenance rather than inference.

## The problem

When data crosses boundaries, its provenance erodes with each handoff.

The same value — say, "price: ¥150,000" — carries very different weight depending on whether it was recorded by a trusted origin at the source, or whether it is derived data that passed through multiple intermediaries. Yet the data's recipients — auditors, downstream systems, counterparties, and AI agents — have no structural means to distinguish between these cases.

### Audits are points; reality is a line

Real-world workflows are continuous and unbroken. Regulations and audits, however, sample that continuity by checking discrete points. Systems cannot retain a complete record of every flow, and the provenance between those points is forgotten.

The dominant approach today is to create "audit points" wherever regulations demand them. But points are only meaningful as cross-sections of a continuous line; creating points individually cannot reconstruct the line. Because data flows are continuous, provenance records should be continuous too.

dPLaaX's data-pipeline approach layers "provenance continuity" on top of "data continuity." The records dPLaaX produces are also points — one per boundary — but unlike isolated audit points created after the fact, each record is a cross-section that is connected to the records before and after it, forming a line. When a continuous provenance record exists, any provenance-related evidence that an audit demands can be derived as a cross-section at any point along that line. Mechanisms that preserve partial provenance chains exist, but the layer that treats the continuity of process boundaries as its primary concern — across all domains — remains vacant.

Lines are preferable to points for reasons beyond audit convenience. Creating plausible point artifacts — polished documents, internally consistent figures, records that look authentic — has always been cheap, and advances in generative technology are driving that cost further down. Fabricating a connected provenance line, by contrast, requires the signing keys of every boundary traversed and consistency with records already received downstream. That difficulty is independent of how convincing the artifact looks; the ability to produce indistinguishable points does not imply the ability to produce a verifiable line. dPLaaX therefore shifts the weight of trust from "does the artifact look genuine?" to "can the provenance line be verified?" This is not a claim that content cannot be falsified — a dishonest origin still holds its signing key and can sign an incorrect value (→ "What dPLaaX is"). The orders-of-magnitude difference in cost between fabricating an artifact and fabricating a verifiable provenance line is what makes lines more trustworthy than points.

There are three layers of trust that this protocol takes on. The first is that each individual record is internally consistent — who signed it, and whether it has been tampered with. The second is that a record can be traced back to a declared account of what it was made from. dPLaaX covers these two layers. The third layer — whether the output was *correctly* derived from the declared inputs, in the sense of semantic correctness — is deliberately outside the protocol. Signatures prove identity, not truth, and whether a transformation is correct can only be judged by someone who understands what the transformation means. Not over-committing at the boundary is what preserves the reliability of the commitment that is made.

### Cross-organizational provenance

Even when records are preserved continuously, who can verify them is a separate question. Within a single organization, the anchor of trust is usually clear, and existing simple mechanisms often suffice. The unsolved problem is how to preserve boundary-by-boundary data provenance in a verifiable form across flows that span **multiple organizations with no shared anchor of trust**. Note that data does not always stay within a single organization. The value of applying the same protocol to intra-organizational records lies in ensuring that the line does not break when those records eventually cross a boundary.

### Rapid growth in provenance demand

Demand for provenance attestation is expanding rapidly across multiple domains: software supply chains, physical supply chains (product passports), content authenticity, security and compliance reporting, and AI training-data governance. In each of these domains, industry-scale standardization of provenance is underway.

These existing ecosystems are not mutually exclusive; they coexist as efforts targeting different **units of boundary** — build artifact, product lifecycle, content unit, and so on. Some have lineage or ancestry features, but each is scoped to its own unit and domain. The layer that dPLaaX addresses — treating the **continuity of process boundaries in data pipelines broadly construed as its primary subject, regardless of domain** — is still vacant. Interoperability with existing ecosystems is a premise, but how that is achieved is outside the scope of this document.

### AI as a data consumer

The provenance problem predates AI, but the spread of AI sharpens it. Because LLMs cannot internally verify the factual accuracy of their input data, providing them with data whose provenance has not been verified creates a structural risk of degraded judgment quality (Unverified In, Hallucination Out). The commitment protocol of dPLaaX treats both human and machine verifiers on equal footing, and directly supports use cases in which AI agents verify the provenance of reference data mechanically.

## Regulatory tailwinds

Regulations that require provenance attestation — or that are structurally well-suited to it — are spreading across multiple domains. For the provenance-related portions of the evidence those regulations demand, a continuous provenance record makes it unnecessary to instrument each regulation individually; the required evidence can be derived as a cross-section of the line.

| Domain | Regulation (examples) |
| --- | --- |
| Supply chain / product | ESPR / Digital Product Passport / EU Battery Regulation / EU Data Act / IRA-FEOC rules |
| Sustainability | CSRD (Scope 3, third-party assurance) / CBAM |
| Food / pharmaceuticals | DSCSA (unit-level prescription drug tracing) / FSMA 204 |
| Financial ICT / data protection | DORA (ICT risk, audit trail) / GDPR Art. 5(2) and Art. 30 (accountability, records of processing) |
| Digital identity | eIDAS 2.0 (EUDI Wallet, electronic attestation of attributes) |
| AI governance | EU AI Act (Arts. 10–12: data governance, documentation, logging) / California AB-2013 (training data disclosure) / California SB-942 (generated-content disclosure) |
| Defense / sensitive information | US DoD CMMC 2.0 / CUI requirements |

dPLaaX does not by itself achieve regulatory compliance. Each regulation imposes domain-specific recording, control, reporting, and legal interpretation requirements. What continuous provenance can provide is the foundation for the provenance-related portion of that evidence.

## References

The papers below document the path to this subject from the context of the AI era; they do not limit the scope of dPLaaX to AI applications.

- From "move fast" to "move with trust" / *Toward Trustworthy Data Pipelines in the AI Era: Provenance, Sovereignty, and Agent Access* — [doi.org/10.5281/zenodo.19554296](https://doi.org/10.5281/zenodo.19554296) (2026-04-13)
- Cryptographic provenance in data pipelines / *Cryptographic Provenance Attestation in Data Pipelines: Structural Guarantees for Data Trustworthiness via W3C VC/DID* — [doi.org/10.5281/zenodo.20042030](https://doi.org/10.5281/zenodo.20042030) (2026-05-05)
- Data sovereignty in the AI era / *Data Sovereignty in the AI Era: Federated Pipeline Networks (v2)* — [doi.org/10.5281/zenodo.20124910](https://doi.org/10.5281/zenodo.20124910) (2026-05-12)
