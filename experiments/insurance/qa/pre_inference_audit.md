# Final pre-inference audit

**Status: PASS**

A separate AI reviewer independently checked the authored gold labels and request choices before inference. This was not human or external insurance/legal expert review.

Read-only semantic review of all 60 cases, all 12 documents, all 300 offered evidence sets and actual model request records. No model predictions were read, no evaluated-model inference was performed, and the benchmark was not modified by this reviewer.

## Result

- 60/60 decision golds confirmed
- 60/60 evidence golds sufficient
- 300 offered evidence options reviewed; one complete direct support option per case
- No unresolved blocking findings
- No answer-label, rationale or filename leakage in the actual model requests

The frozen offered-choice task has a supported decision gold and one complete, direct supporting evidence option per case under the stated evidence-chain standard. This is a benchmark quality gate, not a performance result or validation of real insurance law.

## Frozen inputs

Benchmark version: 1.0.0
Benchmark SHA-256: `8a0b1a6c4227b90b20c92de012c5d02a037e4ae4a79dac614b150345ed45c1bc`
Requests SHA-256: `03066c91f05878efcb7f3c358e91e0cfa9087091b205728c2788e61b0b8e1eba`

## Evidence standard and necessity

Use only the scenario and selected clauses for the complete direct proof. Do not import a needed policy rule from an unselected clause. For a conflict, cite the opposed rules and the fact that the documented priority/supersession scheme does not resolve them. For offen, cite a rule or status tying the claim to missing information, rather than treating absence as false. Refuting one conjunct is sufficient to refute a conjunction.

Gold sets were reduced wherever a clearly dispensable clause produced another sufficient offered option. Cases 028 and 051 retain conservative explicit two-clause chains; shorter natural-language explanations are possible, but none is offered as a competing set. Case 028 also has the unoffered complete V1+V4 route. Passing uniqueness means uniqueness among the five offered options, not uniqueness among all imaginable explanations.

## Main fixes verified

- F1 and O2 now explicitly state exactly-if conditions, eliminating the unsupported converse in positive labels.
- Case 019 now tests actual disease characteristics rather than the false assertion that a diagnosis has already proved them.
- Case 038 now tests actual causal facts rather than proof-required exception applicability.
- Case 031 now expressly asks about F2 with outdoor location and unknown security.
- Case 056 now includes H3 as well as H5.
- Random distractors that contained independent complete proof routes were removed, and every regenerated option was reread.

## Required distinctions

- Missing necessary facts remain open; positively failed conditions are false
- The three unresolved conflicts are fall_025, fall_045 and fall_049
- Effective priority, nonbinding documents and unrelated objects do not create unresolved conflicts
- Date/version cases fall_006, fall_028 and fall_033 require no arithmetic

## All 60 case verdicts

### fall_001 · PASS
Decision: nein. Unique offered evidence: b1 (L5).
L5 expressly distinguishes intentional use from intentional damage; the scenario establishes negligent damage.

### fall_002 · PASS
Decision: ja. Unique offered evidence: b1 (F3).
F3 itself waives the fixed-object connection in an exclusive locked cellar and specifies the remaining separate-lock requirement, both satisfied here.

### fall_003 · PASS
Decision: ja. Unique offered evidence: b5 (H2).
H2 directly includes portable computers as professional equipment; the scenario establishes the laptop and professional use.

### fall_004 · PASS
Decision: nein. Unique offered evidence: b3 (K5).
K5 expressly makes the information card non-binding and denies it priority. The asserted resolution is false, rather than itself an unresolved conflict.

### fall_005 · PASS
Decision: nein. Unique offered evidence: b5 (U7).
U7 expressly prohibits inferring the opposite contractual content from missing documents. No alternative option contains the competing electronics-status clause U3.

### fall_006 · PASS
Decision: ja. Unique offered evidence: b5 (V1+V4).
V4 provides the effective Delta inclusion; V1 makes the operative individual amendment prevail over general terms. The August loss is after the July effectivity date.

### fall_007 · PASS
Decision: nein. Unique offered evidence: b3 (Z1).
Z1 expressly says later signature alone does not displace an earlier amendment.

### fall_008 · PASS
Decision: offen. Unique offered evidence: b5 (L6).
L6 supplies the loan definition and explains why ownership by a friend does not establish the missing agreed transfer for use.

### fall_009 · PASS
Decision: ja. Unique offered evidence: b1 (O2).
Revised O2 now explicitly states an if-and-only-if permission. Both intent and actual investigation impairment are established, so ja is unambiguous.

### fall_010 · PASS
Decision: nein. Unique offered evidence: b1 (F4).
F4 directly excludes the shared cellar from the particular cellar exception asserted. The alternative F2/F3 proof routes are not offered.

### fall_011 · PASS
Decision: nein. Unique offered evidence: b1 (N1).
N1 alone refutes the ownership component of the conjunction: neither an invoice nor a photo plus attributable statement is present. Refuting one conjunct is sufficient.

### fall_012 · PASS
Decision: nein. Unique offered evidence: b4 (V4).
V4 expressly limits the amendment to Delta and leaves the exclusion for other devices unchanged.

### fall_013 · PASS
Decision: nein. Unique offered evidence: b1 (F2).
F2 explicitly says a frame lock alone is insufficient. This is a known failed condition, not missing information.

### fall_014 · PASS
Decision: ja. Unique offered evidence: b4 (M1).
The scenario contains all content elements described in M1, and the claim is expressly limited to that M1 content description.

### fall_015 · PASS
Decision: ja. Unique offered evidence: b3 (N1).
N1 expressly permits the photo-plus-attributable-statement alternative without an invoice.

### fall_016 · PASS
Decision: nein. Unique offered evidence: b5 (V1).
V1 expressly says brochures do not alter the contract; a newer publication date does not give contractual priority.

### fall_017 · PASS
Decision: nein. Unique offered evidence: b2 (M3).
M3 explicitly says no diagnosis is required and its absence alone is not a formal defect. M1 alone states required elements without expressly denying other requirements.

### fall_018 · PASS
Decision: offen. Unique offered evidence: b5 (W1).
W1 identifies the required water origin and escape conditions. The scenario supplies neither, so the factual classification remains open. W7 is no longer a competing option.

### fall_019 · PASS
Decision: offen. Unique offered evidence: b1 (R4).
The revised claim asks whether the illness meets the actual R4 event characteristics, not whether those characteristics are already proved. Severity and unexpectedness are unknown; R6 is not offered as a competing evidence route.

### fall_020 · PASS
Decision: offen. Unique offered evidence: b3 (U5+U6).
U5 supplies the intent condition; U6 supplies the missing-culpability fact because the scenario only refers to U6. Neither missing intent nor missing negligence is treated as the opposite fact.

### fall_021 · PASS
Decision: ja. Unique offered evidence: b1 (R4+R5).
R4 supplies the covered-event rule and R5 establishes that the spouse is a risk person; both illness characteristics are stated as satisfied.

### fall_022 · PASS
Decision: nein. Unique offered evidence: b1 (H3).
H3 expressly excludes shared storage rooms from the insured location.

### fall_023 · PASS
Decision: nein. Unique offered evidence: b1 (R4+R5).
R4 limits the eligible sick people and R5 expressly excludes colleagues from risk persons. The relationship is known, so nein rather than offen.

### fall_024 · PASS
Decision: offen. Unique offered evidence: b3 (M5).
M5 limits the portal message to receipt. It neither confirms nor denies formal completeness; the actual certificate contents are not supplied. M1 is no longer a competing option.

### fall_025 · PASS
Decision: konflikt. Unique offered evidence: b4 (K1+K2+K3).
K2 and K3 conflict on business travel. K1 establishes equal rank, no replacement and no agreed preference. The scenario itself does not supply the absence of replacement/preference, so K1 remains needed for the complete conflict proof.

### fall_026 · PASS
Decision: offen. Unique offered evidence: b1 (K7).
K7 expressly says no document settles winter-sports activity coverage. Spatial coverage cannot fill that missing subject-matter rule.

### fall_027 · PASS
Decision: offen. Unique offered evidence: b3 (H6).
H6 makes actual use at the loss date decisive; that use is undocumented. Ownership and location do not establish private use.

### fall_028 · PASS
Decision: nein. Unique offered evidence: b3 (V4+V6).
V4 supplies the July commencement date and V6 expressly makes the June loss date control instead of the August report date, with no retroactivity. No other offered set contains V4; the complete time-and-scope proof is unique among the choices.

### fall_029 · PASS
Decision: nein. Unique offered evidence: b5 (Z5).
Z5 expressly says Gamma makes no rule about the main dwelling. Its garage inclusion therefore does not resolve the dwelling conflict.

### fall_030 · PASS
Decision: offen. Unique offered evidence: b3 (N1).
N1 requires unique attribution of the account statement. That factual attribute is unknown; it is not affirmatively absent. N5 is not offered as a competing clarification.

### fall_031 · PASS
Decision: offen. Unique offered evidence: b4 (F2).
The revised scenario specifies theft outside the dwelling and unknown actual security; the claim expressly asks whether F2 was fulfilled. F2 supplies the unknown requirements, while the receipt cannot establish them.

### fall_032 · PASS
Decision: ja. Unique offered evidence: b2 (O4).
O4 expressly authorizes necessary immediate loss-mitigation before consultation.

### fall_033 · PASS
Decision: offen. Unique offered evidence: b1 (V4+V6).
V4 establishes the actual device/event inclusion and its temporal change point. V6 makes the unknown loss date, rather than the known report date, decisive. No other option contains V4.

### fall_034 · PASS
Decision: nein. Unique offered evidence: b4 (Z6).
Z6 explicitly makes the unsigned draft non-binding and says it expands no protection.

### fall_035 · PASS
Decision: nein. Unique offered evidence: b1 (L3).
L3 itself excludes professional use from the borrowed-instrument exception, so the exception does not override L2 for the professional concert.

### fall_036 · PASS
Decision: nein. Unique offered evidence: b1 (O2).
O2 requires both conditions, and actual investigation impairment is expressly false. The refusal permission therefore fails despite proven intent.

### fall_037 · PASS
Decision: nein. Unique offered evidence: b1 (W2).
W2 expressly excludes rain, including entry through damage to the building. The independent W1 definition-based proof is no longer offered.

### fall_038 · PASS
Decision: offen. Unique offered evidence: b5 (W4).
The revised statement is about actual causation and absence of another cause. Those are unresolved, not established false. W4 specifies precisely these two factual conditions; W5 is not offered as a competing route.

### fall_039 · PASS
Decision: nein. Unique offered evidence: b2 (U5).
U5 expressly excludes negligence from the intent exclusion, and the scenario now positively establishes negligence.

### fall_040 · PASS
Decision: ja. Unique offered evidence: b1 (W3).
W3 directly includes frost rupture of fixed drinking-water pipes. W1 cannot substitute because rupture does not itself establish escaped-water damage.

### fall_041 · PASS
Decision: nein. Unique offered evidence: b3 (L3).
L3 directly excludes loss from the borrowed-musical-instrument exception.

### fall_042 · PASS
Decision: ja. Unique offered evidence: b3 (N1+N3).
The positive conjunction needs N1 for ownership via invoice and N3 for damage via a repair report; neither alone establishes the whole positive claim.

### fall_043 · PASS
Decision: nein. Unique offered evidence: b1 (N6).
N6 expressly says complete documentation is not acknowledgement of coverage.

### fall_044 · PASS
Decision: ja. Unique offered evidence: b1 (W4).
W4 grants the exception when both causal facts hold, and the scenario establishes both. W5 states necessary proof conditions but does not independently grant the exception.

### fall_045 · PASS
Decision: konflikt. Unique offered evidence: b4 (Z1+Z3+Z4).
Z3 and Z4 are opposite effective dwelling rules. Z1 establishes that later signature/date alone cannot resolve the same-rank conflict. Gamma has a separate garage scope.

### fall_046 · PASS
Decision: ja. Unique offered evidence: b3 (K4).
K4 expressly states agreement on Portugal. The Canada and business-travel conflicts are irrelevant, and the independent worldwide K2 proof is no longer offered.

### fall_047 · PASS
Decision: offen. Unique offered evidence: b3 (U3).
U3 already states the absence of both binding activation evidence and a binding deactivation. U2 concerns the general location/offer file and U7 is a generic missing-document rule; neither alone establishes the electronics activation criterion and its status.

### fall_048 · PASS
Decision: ja. Unique offered evidence: b2 (F1+F2).
Revised F1 explicitly supplies an if-and-only-if inclusion, and F2 supplies the security rule satisfied by the fixed bracket plus separate lock. F2+F5 lacks the inclusion rule and cannot replace the complete positive proof.

### fall_049 · PASS
Decision: konflikt. Unique offered evidence: b5 (K1+K2+K3).
K2 and K3 conflict on Canada; K1 establishes equal rank with no replacement or agreed preference. Purpose is irrelevant to this exclusively spatial claim. A set containing K2/K3 but not K1 omits part of the unresolved-conflict proof.

### fall_050 · PASS
Decision: nein. Unique offered evidence: b2 (H2).
H2 directly excludes professional tools, regardless of their location inside the dwelling.

### fall_051 · PASS
Decision: nein. Unique offered evidence: b4 (O5+O6).
O5 provides the prior-approval requirement for nonurgent repair; O6 explicitly distinguishes inspection approval from repair approval. No other option contains O5, so this direct two-step proof is unique among the choices.

### fall_052 · PASS
Decision: ja. Unique offered evidence: b1 (R2).
R2 defines withdrawal as complete abandonment before the first booked segment. The scenario itself identifies the flight as that segment and abandonment on the preceding unbooked ride.

### fall_053 · PASS
Decision: ja. Unique offered evidence: b2 (L3).
L3 itself states the derogation from L2 and includes the private borrowed-instrument damage, with both professional-use and loss carve-outs absent.

### fall_054 · PASS
Decision: offen. Unique offered evidence: b4 (O2).
O2 specifies the two relevant conditions; both are unknown. Neither missing condition is treated as false. O1 is no longer offered as a competing incomplete-status explanation.

### fall_055 · PASS
Decision: offen. Unique offered evidence: b5 (U1+U2).
U1 supplies the binding-location rule and non-binding status of an offer; U2 supplies the actual missing certificate and missing accepted offer. No other option includes U2.

### fall_056 · PASS
Decision: nein. Unique offered evidence: b5 (H3+H5).
H3 defines the insured location as the named dwelling, which excludes the new unnamed dwelling. H5 then denies the borrowed-item inclusion at that place. Both clauses are now included in the gold.

### fall_057 · PASS
Decision: nein. Unique offered evidence: b1 (M4).
M4 makes an original conditional on a qualified express request; the scenario expressly states there was no request.

### fall_058 · PASS
Decision: nein. Unique offered evidence: b5 (M2).
M2 explicitly rejects a work-incapacity certificate without trip reference as a substitute for the requested travel-incapacity proof. M1 is not offered as an independent failure-of-requirements route.

### fall_059 · PASS
Decision: nein. Unique offered evidence: b4 (R2).
R2 itself excludes an interruption after journey commencement and defines withdrawal before the first booked segment; the first booked flight has already been taken.

### fall_060 · PASS
Decision: ja. Unique offered evidence: b2 (Z5).
Z5 expressly includes garage flood damage and replaces Beta there. The separate dwelling conflict does not affect the garage statement.

## Limitations

- Purposive synthetic challenge set, not a representative production sample.
- Five cases share each document and are not independent observations.
- Only three conflict cases; no precise per-class generalization is justified.
- Guided document comprehension and offered evidence-set selection; no free-form citation generation, retrieval, OCR, long PDFs or arithmetic test.
- Separate AI review does not replace human insurance/legal expert validation.
- Evidence uniqueness is operational and among the offered choices; this review is not a formal theorem prover.
