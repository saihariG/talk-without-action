# Legal sources

Court opinions are public domain. This is research framing, not legal advice, and the paper says it was written by non-lawyers.

## US

**Sherman Act §1, 15 U.S.C. §1.** "Every contract, combination in the form of trust or otherwise, or conspiracy, in restraint of trade or commerce among the several States, or with foreign nations, is declared to be illegal." Source: Cornell LII (`usc15_1.txt`).

**Price fixing is per se illegal, and the agreement itself is the offense.** *United States v. Socony-Vacuum Oil Co.*, 310 U.S. 150 (1940).
- At 223: "a combination formed for the purpose and with the effect of raising, depressing, fixing, pegging, or stabilizing the price of a commodity ... is illegal per se."
- At 224 n.59: "a conspiracy to fix prices violates § 1 of the Act though no overt act is shown, though it is not established that the conspirators had the means available for accomplishment of their objective".
- Pin pages from the Justia page markers. Text also in `socony.txt`.
- **Relevance.** Under §1, talk without action that amounts to an agreement is not legally innocent, even with no effect on prices. That's why the paper claims only that the detectors can't tell talk from *causal* coordination, not that D runs are lawful.

**Parallel conduct alone isn't agreement.**
- *Theatre Enterprises v. Paramount Film Distributing Corp.*, 346 U.S. 537, 541 (1954): "'conscious parallelism' has not yet read conspiracy out of the Sherman Act entirely."
- *Bell Atlantic Corp. v. Twombly*, 550 U.S. 544 (2007). Pin pages from the Library of Congress U.S. Reports PDF (`twombly_usrep.pdf`):
  - At 554: parallel conduct is "consistent with conspiracy, but just as much in line with a wide swath of rational and competitive business strategy".
  - At 557: "Without more, parallel conduct does not suggest conspiracy". Parallel conduct "needs some setting suggesting the agreement necessary to make out a §1 claim".
  - At 556 n.4, quoting 6 Areeda & Hovenkamp ¶1425: "parallel behavior that would probably not result from chance, coincidence, independent responses to common stimuli, or mere interdependence unaided by an advance understanding among the parties".

**The evidentiary standard: evidence must tend to exclude independent action.**
- *Monsanto Co. v. Spray-Rite Service Corp.*, 465 U.S. 752, 764 (1984): "There must be evidence that tends to exclude the possibility that the manufacturer and nonterminated distributors were acting independently." At 768, it requires evidence of "a conscious commitment to a common scheme designed to achieve an unlawful objective."
- *Matsushita Elec. Indus. Co. v. Zenith Radio Corp.*, 475 U.S. 574, 588 (1986), extends this to §1 generally. A plaintiff "must present evidence 'that tends to exclude the possibility' that the alleged conspirators acted independently."
- Pin pages from Justia page markers.
- **Relevance.** B (comms off) is a lab version of "independent responses to common stimuli". D2b flags 3 of 10 B runs, so a moderate J-R threshold doesn't meet this standard.

**Plus factors.** *In re Flat Glass Antitrust Litigation*, 385 F.3d 350 (3d Cir. 2004). Text from OpenJurist, cited by paragraph, ¶¶34-37. Reporter pages are not verified; secondary sources place the passage at 358-61.
- ¶35 lists three plus factors: "(1) evidence that the defendant had a motive to enter into a price fixing conspiracy; (2) evidence that the defendant acted contrary to its interests; and (3) 'evidence implying a traditional conspiracy.'"
- ¶36: the first two "largely restate the phenomenon of interdependence". Acting contrary to interest means "conduct that would be irrational assuming that the defendant operated in a competitive market".
- ¶37: "The most important evidence will generally be non-economic evidence 'that there was an actual, manifest agreement not to compete.'" That may include "proof that the defendants got together and exchanged assurances of common action".
- **Mapping to the detectors.** D1 (price > 90) is a version of plus factors 1-2, which the court says restate interdependence. D3 (J-M on messages) reads exactly the "exchanged assurances of common action" that ¶37 calls the most important evidence. D runs are full of such assurances, and the asks never saw them. So the plus factor courts weigh most fires on talk that, by construction, can't have caused the asks. That's the paper's main legal point.

**Proposals that aren't accepted, and invitations to collude.**
- *United States v. American Airlines, Inc.*, 743 F.2d 1114 (5th Cir. 1984). Text from OpenJurist, by paragraph.
  - Crandall's proposal to Braniff was declined. ¶51: "That he was not able to price fix and thus, has no liability under section 1, has no effect on whether his unsuccessful efforts to monopolize constitute attempted monopolization."
  - ¶53: "an agreement is not an absolute prerequisite for the offense of attempted joint monopolization".
  - So under §1, a one-sided proposal without acceptance is not an agreement.
- FTC, *Policy Statement Regarding the Scope of Unfair Methods of Competition Under Section 5 of the FTC Act* (Nov. 10, 2022), p. 12 & n.71 (`ftc_s5.pdf`).
  - It lists "invitations to collude" among past uses of Section 5. "Invitations to collude, even if unaccepted, represent both an incipient violation as well as a violation of the spirit of the antitrust laws".
  - It cites *In re Quality Trailer Products Corp.*, 115 F.T.C. 944 (1992), and *In re Valassis Communications*, Dkt. C-4160 (2006), both consent orders.
  - **Status caveat:** one search found no sign the statement was rescinded under the current Commission, but that isn't confirmed, so it is not cited as current policy.
- **Relevance.** D-run sellers trade explicit mutual assurances ("hold firm", "no solo undercutting"). Legally that looks more like accepted invitations than one-sided ones. Whether a message-writing call counts as the "firm" agreeing, when that firm's asks come from a separate call, is left open.

## EU

**Article 101(1) TFEU** (ex Art. 81 EC, ex Art. 85 EEC) prohibits "all agreements between undertakings, decisions by associations of undertakings and concerted practices which ... have as their object or effect the prevention, restriction or distortion of competition". Source: EUR-Lex CELEX 12008E101.

**A concerted practice needs concertation, then conduct, with causation between them. EU law presumes the causation.** Case C-8/08 *T-Mobile Netherlands*, ECLI:EU:C:2009:343 (EUR-Lex).
- ¶26 defines a concerted practice: coordination by which "practical cooperation between them is knowingly substituted for the risks of competition" (citing *Suiker Unie* ¶26 and *Ahlström* ¶63).
- ¶51: the concept "implies, in addition to the participating undertakings concerting with each other, subsequent conduct on the market and a relationship of cause and effect between the two". But "subject to proof to the contrary ... it must be presumed that the undertakings taking part in the concerted action and remaining active on the market take account of the information exchanged with their competitors in determining their conduct". A concerted practice is caught "even in the absence of anti-competitive effects on the market" (citing *Hüls* ¶¶161-163).
- ¶¶61-62: the presumption holds even for a single meeting, and firms "may justifiably be called upon to adduce evidence that that concerted action did not have any effect on their conduct".
- **Relevance.** This is the closest legal analogue to the design. EU law presumes the message→conduct link that D deliberately cuts. D runs are the situation where that presumption is false. They show that message-based detectors (D3) and the action-dependence slope (D4) can't supply the "proof to the contrary". D4's β is positive in all 6 D runs even though the link is absent by construction.

**Parallel conduct proves concertation only if concertation is the only plausible explanation.** Joined Cases C-89/85 etc., *Ahlström Osakeyhtiö v Commission* ("Wood Pulp II"), ECLI:EU:C:1993:120, ¶71: "parallel conduct cannot be regarded as furnishing proof of concertation unless concertation constitutes the only plausible explanation for such conduct." At ¶126 the Court finds it was not the only plausible explanation on those facts.

## Not used / not verified
- Berger et al. 2025 (the sprint's legal citation) is commentary, not a primary source. See NOVELTY.md.
- *U.S. v. Container Corp.*, 393 U.S. 333 (1969) is cited in Berger. Not checked against the opinion and not quoted.
- *Hüls* (C-199/92 P) and *Anic* are cited through *T-Mobile* ¶51 only and not quoted directly.