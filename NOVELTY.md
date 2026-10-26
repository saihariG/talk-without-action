# Novelty check

## Berger et al. 2025, the sprint's citation
The sprint page's Q2.3 cites "Berger et al. 2025" as its only legal resource. It's linked to: Lee F. Berger, Michael L. Weiner & Weisiyu Jiang, "Coordination by Code: Rethinking Antitrust Liability in the Age of AI Pricing", *Antitrust Magazine* 40(1), Fall 2025, published Nov 25, 2025 (americanbar.org). Full text read on 2026-10-23.

What it is: a legal commentary on Section 1 liability when competitors use a **shared** AI pricing tool. It covers:
- *RealPage* (DOJ case and private MDL, hub-and-spoke) and *Gibson v. Cendyn* (dismissed, affirmed by the 9th Cir. on Aug 15, 2025);
- California AB 325, which amends the Cartwright Act;
- five hypothetical airline scenarios that differ in data pooling, mutual awareness, and agreed prompts.

Its plus factors are "prior collusion, evidence of intent to coordinate, the structure of the market, and whether the information shared is current, specific, bi- or multi-lateral, and competitively sensitive", following *Container Corp.*

**Overlap with this project: none on method or result.**
- It has no experiments, no LLM agents talking to each other, and no detectors.
- It doesn't evaluate LLM judges or price screens, and doesn't separate talk from causal effect.
- Its question is whether shared-tool use is an agreement. This project asks whether the evidence detectors use tracks causal coordination.

It is the doctrine side of the gap the sprint names ("The ML literature is re-deriving this without engaging older literature from other fields", from the sprint page). The paper cites it for framing. The primary law is in LEGAL_SOURCES.md.

## Nearest empirical work
- **Colosseum** (Nakamura, Kumar, Das, Abdelnabi, Mahmud et al., arXiv 2602.15198, v2 May 27 2026). This is the closest one. It audits collusion in *cooperative* multi-agent tasks (DCOPs) with both an LLM-as-a-judge on conversations and regret-based action metrics. It reports "collusion on paper": "agents plan to collude in text but often pick non-collusive actions". It also says that "action- and conversation-level collusion evidence can diverge".
  - **Difference:** their divergence is observed. Agents chose not to act on their talk, in cooperative settings, not markets. This project uses an intervention in a market: the message→ask path is cut by construction (D), so ground truth is causal, not judged. It then measures how standard antitrust-style detectors (price screen, the published reasoning judge, a message judge, action dependence) score it against a fixed rule.
  - **Cited in the paper.** The project builds on their result and adds the causal control, in the Agrawal market.
- **NARCBench** (Rose, Cullen et al., arXiv 2604.01151). Activation-probe collusion detection in committee, transfer and steganography tasks. It reports LLM-judge false positives on control runs (a naive Sonnet-5 judge "marked everything as suspicious"). There are no markets, no talk-without-action control, and no antitrust framing. Cited as evidence that text judges over-flag.
- **On the Fragility of AI Agent Collusion** (Keppo, Li, Tsoukalas, Yuan, arXiv 2603.20281). Theory plus experiments on heterogeneity in LLM pricing collusion. There's no detector evaluation and no work on communication as evidence. Cited for background only.
- **Agrawal et al.** (arXiv 2507.01413) is the base. Their judge scores reasoning only, never messages. Their runs and judge are re-used verbatim.

No paper was found with a talk-without-action (message-blind action) control in an LLM market, or one that tests plus-factor-style detectors against causal ground truth. The paper makes no claim to be first.
