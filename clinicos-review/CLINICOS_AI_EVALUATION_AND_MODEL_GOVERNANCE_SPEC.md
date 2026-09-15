# CLINICOS — AI EVALUATION AND MODEL GOVERNANCE SPECIFICATION
**Document:** `CLINICOS_AI_EVALUATION_AND_MODEL_GOVERNANCE_SPEC.md`  
**Status:** Target / Authoritative AI Governance Specification  
**Version:** 1.0  
**Priority:** Critical  
**Audience:** AI Engineering, ML Engineering, Backend Engineering, Product, Clinical Safety, Security, QA, Operations, and Clinic Administrators
---
# 1. Purpose
This document defines the target evaluation, validation, monitoring, governance, and lifecycle management model for artificial intelligence systems used by Clinicos.
Clinicos may use:
- foundation models
- large language models
- multimodal models
- embedding models
- reranking models
- speech models
- image analysis models
- specialized classifiers
- AI agents
- agentic workflows
- model-based decision support systems
- third-party AI providers
AI capabilities must not be treated as inherently trustworthy.
Every AI capability must have measurable quality, safety, reliability, cost, and operational characteristics.
This document defines how Clinicos determines:
- whether a model is suitable for a task
- whether an AI capability is safe enough for deployment
- whether a model is improving
- whether a model is degrading
- when a model should be replaced
- when a model should be restricted
- when a model must be removed from production
- how AI changes are evaluated
- how AI incidents are handled
- how model versions are governed
- how evaluation datasets are created and maintained
- how production feedback becomes evaluation data
- how human review is incorporated
- how AI performance is measured over time
---
# 2. Governance Philosophy
Clinicos must not optimize AI systems for a single metric.
A model that is:
```text
cheap

but unsafe is unacceptable.

A model that is:

accurate

but too slow for interactive communication may be operationally unsuitable.

A model that is:

high quality

but repeatedly hallucinates appointment availability is unacceptable for operational use.

A model that:

generates persuasive responses

but violates clinic policy is unacceptable.

Therefore:

AI Quality
=
Capability
+
Safety
+
Reliability
+
Operational Correctness
+
Policy Compliance
+
Cost Efficiency
+
Latency
+
Observability

No single dimension should define model fitness.

⸻

3. Core Governance Principle

Clinicos must distinguish between:

1. Model capability
2. Model quality
3. Model safety
4. Model reliability
5. Model suitability for a specific task
6. Model suitability for a specific risk level
7. Model suitability for a specific language
8. Model suitability for a specific clinic workflow

A model may be excellent for one task and unsuitable for another.

For example:

Model A
Excellent at:
- summarization
- translation
Poor at:
- structured extraction
- medical safety
Model B
Excellent at:
- structured classification
Poor at:
- long-form patient communication

Model governance must therefore be task-specific.

⸻

4. Model Governance Scope

This specification applies to:

* LLMs
* multimodal LLMs
* vision models
* speech-to-text models
* text-to-speech models
* embedding models
* rerankers
* classifiers
* OCR systems
* facial analysis models
* AI agents
* model ensembles
* provider routing systems
* model fallback systems
* AI-powered workflows
* AI-generated content
* AI-assisted operational decisions

⸻

5. AI System Layers

Clinicos should evaluate AI at multiple layers.

Layer 1
Foundation Model
Layer 2
Provider / API
Layer 3
Model Gateway
Layer 4
Prompt / Instruction Layer
Layer 5
Tool-Calling Layer
Layer 6
Agent Layer
Layer 7
Workflow Layer
Layer 8
Product Feature
Layer 9
Clinic Operation

A model can pass evaluation while the overall AI system still fails.

Therefore:

Model Evaluation
≠
System Evaluation

Both are required.

⸻

6. Model Registry

Clinicos should maintain a model registry.

Each registered model should contain:

* model ID
* provider
* provider model name
* version
* capability class
* supported modalities
* supported languages
* context limits
* structured output support
* tool-calling support
* known limitations
* safety classification
* cost profile
* latency profile
* availability status
* evaluation status
* approval status
* deployment status
* retirement status

⸻

7. Model Identity

Every model invocation must be traceable to an immutable model identity.

A model identity should include:

provider
model
version
configuration
deployment revision

A generic identifier may be:

model_id

but the system must preserve enough metadata to reproduce which model configuration generated an output.

⸻

8. Model Versioning

Model versions must be explicit.

Examples:

provider/model-v1
provider/model-v2
provider/model-v3

If a provider silently changes the underlying model while retaining the same public name, Clinicos should treat the change as a potentially new evaluation target when detectable.

⸻

9. Model Status Lifecycle

A model should move through:

Discovered
    ↓
Registered
    ↓
Candidate
    ↓
Evaluated
    ↓
Approved
    ↓
Canary
    ↓
Production
    ↓
Restricted
    ↓
Deprecated
    ↓
Retired

A model must not enter production solely because it is available through an API.

⸻

10. Model Discovery

New models may be discovered through:

* provider announcements
* internal experiments
* benchmark results
* engineering research
* cost optimization efforts
* latency optimization efforts
* user feedback
* production incidents
* new product requirements

Discovery does not imply approval.

⸻

11. Candidate Models

A candidate model may be used for:

* offline evaluation
* sandbox testing
* controlled experiments
* benchmark comparison

Candidate models must not receive unrestricted production traffic.

⸻

12. Model Approval

Production approval should require evidence that the model meets the requirements for its intended task.

Approval should consider:

* quality
* safety
* reliability
* latency
* cost
* language performance
* structured output reliability
* tool-calling reliability
* policy compliance
* privacy characteristics
* operational fit

⸻

13. Task-Specific Model Fitness

Model approval should be task-specific.

Examples:

Model X approved for:
- FAQ response drafting
- summarization
Model X not approved for:
- appointment booking decisions
- clinical decision support

Approval must not automatically apply to every AI feature.

⸻

14. Risk Classification

AI capabilities should be classified by risk.

Recommended levels:

R0 — Informational
R1 — Administrative
R2 — Operational
R3 — Sensitive
R4 — Clinical / High Risk

Examples:

R0

* translation
* summarization
* formatting

R1

* FAQ drafting
* lead classification

R2

* appointment workflow assistance
* follow-up recommendations

R3

* sensitive patient communication
* image-related patient data processing

R4

* clinical decision support
* medically significant interpretation

Risk level determines evaluation depth and deployment controls.

⸻

15. Evaluation Tiers

Clinicos should use multiple evaluation tiers.

Tier 0
Static validation
Tier 1
Offline benchmark
Tier 2
Adversarial evaluation
Tier 3
Human evaluation
Tier 4
Shadow production
Tier 5
Canary production
Tier 6
Full production monitoring

Higher-risk systems require more tiers.

⸻

16. Static Validation

Static validation should verify:

* schema compatibility
* required output fields
* tool definitions
* prompt integrity
* policy configuration
* model availability
* authentication
* timeout configuration
* fallback configuration

Static validation does not prove AI quality.

⸻

17. Offline Evaluation

Offline evaluation uses predefined test cases.

Examples:

Input
Expected behavior
Expected constraints
Expected structured output
Expected safety behavior

Offline evaluation must be repeatable.

⸻

18. Evaluation Dataset

Clinicos should maintain controlled evaluation datasets.

Datasets may include:

* synthetic cases
* manually authored cases
* anonymized production cases
* adversarial cases
* regression cases
* multilingual cases
* edge cases
* safety cases
* tool-use cases
* workflow cases

⸻

19. Dataset Separation

Evaluation data should be separated into:

Training / Development Data
Validation Data
Test Data
Production Monitoring Data

The final test set should not be continuously tuned against.

⸻

20. Golden Dataset

Clinicos should maintain a curated golden dataset.

A golden dataset contains high-value cases with trusted expected outcomes.

It should include:

* normal cases
* difficult cases
* high-risk cases
* known historical failures
* multilingual cases
* regression cases

⸻

21. Golden Dataset Governance

Golden datasets must be:

* versioned
* reviewed
* access-controlled
* traceable
* periodically refreshed

Changes to the golden dataset must be auditable.

⸻

22. Evaluation Case Structure

An evaluation case may contain:

case_id
task
risk_level
language
input
context
expected_behavior
expected_output
required_constraints
forbidden_behavior
tools_allowed
evaluation_method
severity
source
dataset_version

⸻

23. Expected Behavior vs Exact Output

AI evaluation should generally avoid requiring one exact textual answer.

For many tasks, multiple outputs may be valid.

Therefore evaluation should distinguish:

Exact Match

from:

Behavioral Correctness

For example:

Question:
"What are your clinic hours?"
Valid answer:
Any answer that accurately reflects the authoritative clinic schedule.

⸻

24. Deterministic Evaluation

Deterministic evaluation should be used where possible.

Examples:

* JSON schema validation
* required field validation
* tool-call validation
* state transition validation
* appointment slot validity
* permission validation
* policy rule validation

⸻

25. Semantic Evaluation

Semantic evaluation may assess:

* correctness
* relevance
* completeness
* coherence
* instruction following
* factual consistency

Semantic evaluation should not replace deterministic checks when deterministic checks are possible.

⸻

26. LLM-as-Judge

LLM-based evaluation may be used as one evaluation signal.

However:

LLM-as-Judge
≠
Ground Truth

LLM judges may introduce:

* bias
* model preference
* scoring instability
* correlated errors
* sensitivity to wording

Therefore LLM judges must themselves be validated.

⸻

27. Human Evaluation

Human review is required for selected evaluation categories.

Human evaluation may assess:

* safety
* clinical appropriateness
* communication quality
* policy adherence
* multilingual quality
* harmful ambiguity
* patient experience

⸻

28. Expert Review

High-risk medical evaluations should use appropriately qualified human reviewers.

A general language evaluator must not be assumed to be sufficient for clinical safety evaluation.

⸻

29. Human Evaluation Protocol

Human reviewers should receive:

* standardized instructions
* evaluation criteria
* blinded model identity where practical
* representative cases
* severity definitions
* escalation rules

Reviewer disagreements should be measurable.

⸻

30. Inter-Rater Agreement

Where multiple reviewers evaluate the same cases, Clinicos should measure agreement.

Possible measures include:

* percent agreement
* Cohen’s kappa
* Fleiss’ kappa
* weighted agreement metrics

The appropriate metric depends on the evaluation task.

⸻

31. Evaluation Dimensions

Core evaluation dimensions should include:

1. Task correctness
2. Factuality
3. Instruction following
4. Safety
5. Policy compliance
6. Structured output validity
7. Tool-use correctness
8. Context utilization
9. Hallucination rate
10. Refusal quality
11. Language quality
12. Latency
13. Cost
14. Reliability
15. Consistency

⸻

32. Task Correctness

Task correctness measures whether the AI accomplished the intended task.

Examples:

* correct intent classification
* correct lead extraction
* correct summary
* correct response generation
* correct tool selection

⸻

33. Factuality

Factuality measures whether claims are supported by authoritative information.

For operational tasks:

Authoritative System
>
Knowledge Base
>
AI Inference

The model should not invent facts.

⸻

34. Hallucination

A hallucination occurs when the AI presents unsupported information as fact.

Clinicos should track hallucinations by:

* type
* severity
* domain
* model
* workflow
* language
* tenant
* impact

⸻

35. Hallucination Severity

Recommended severity:

H0 — No hallucination
H1 — Harmless / cosmetic
H2 — Operationally misleading
H3 — Material operational harm
H4 — Safety / clinical harm

⸻

36. Safety Evaluation

Safety evaluation should test whether the model:

* follows safety policies
* refuses unsafe requests
* escalates appropriately
* avoids dangerous instructions
* respects clinical boundaries
* protects sensitive information
* handles uncertainty appropriately

⸻

37. Refusal Quality

A refusal should be evaluated for:

* correctness
* clarity
* relevance
* politeness
* useful redirection
* absence of fabricated reasoning

A refusal that simply says:

"I cannot help."

may be safe but operationally poor if a useful safe alternative exists.

⸻

38. Uncertainty Handling

AI should express uncertainty when evidence is insufficient.

Bad:

"The doctor is available at 4 PM."

when availability has not been checked.

Better:

"I need to check the current appointment schedule."

The system should reward correct uncertainty.

⸻

39. Abstention

Models should be allowed to abstain when confidence or evidence is insufficient.

Possible output:

ABSTAIN

or:

ESCALATE_TO_HUMAN

Abstention should be evaluated as a valid behavior where appropriate.

⸻

40. Overconfidence

Clinicos should explicitly measure overconfidence.

A model that is frequently wrong while expressing high confidence is more dangerous than a model that appropriately escalates uncertainty.

⸻

41. Calibration

Where confidence scores are available, Clinicos should evaluate calibration.

Conceptually:

Predicted Confidence
        ↓
Observed Correctness

High-confidence predictions should have correspondingly high empirical correctness.

⸻

42. Language Evaluation

Clinicos should evaluate supported languages independently.

Target languages include:

* Persian
* English
* Azerbaijani Turkish
* Arabic
* Turkish

Performance in English must not be assumed to represent performance in other languages.

⸻

43. Persian Evaluation

Persian evaluation should consider:

* Persian script
* colloquial Persian
* formal Persian
* mixed Persian-English messages
* Persian numerals
* dates
* local terminology
* medical terminology
* transliteration
* common typing errors

⸻

44. Multilingual Code-Switching

The system should be evaluated on messages such as:

"I want to book PRP برای هفته بعد."

Mixed-language input should not cause loss of operational meaning.

⸻

45. Medical Terminology Evaluation

Medical terminology should be evaluated separately from general language quality.

Examples:

* procedure names
* anatomy
* medication names
* symptoms
* contraindications
* common abbreviations

Medical terminology errors should receive appropriate severity.

⸻

46. Structured Output Evaluation

Structured AI outputs should be validated against schemas.

Example:

{
  "intent": "appointment_request",
  "service": "hair_prp",
  "confidence": 0.94
}

Validation should check:

* required fields
* types
* enums
* ranges
* relationships
* semantic constraints

⸻

47. Invalid Structured Output

Invalid outputs should never be trusted merely because the textual response looks plausible.

Invalid output should trigger:

Retry
Repair
Fallback
Human Review

depending on the task.

⸻

48. Tool-Calling Evaluation

Tool-using models should be evaluated for:

* correct tool selection
* correct arguments
* correct sequence
* refusal to call unauthorized tools
* correct interpretation of tool results
* handling of tool failures
* avoiding unnecessary calls

⸻

49. Tool Argument Validation

AI-generated tool arguments must be validated before execution.

Example:

AI:
book_appointment(
    patient_id="...",
    slot="..."
)

The system must validate:

* authorization
* patient identity
* slot validity
* clinic policy
* appointment state

⸻

50. Tool Result Grounding

After a tool call, the model should use the actual result.

It must not substitute a previous assumption for the returned data.

⸻

51. Agent Evaluation

Agents should be evaluated as systems, not only as prompts.

Evaluation should include:

* planning
* tool selection
* state handling
* memory usage
* policy compliance
* recovery
* escalation
* loop prevention
* completion accuracy

⸻

52. Agent Loop Safety

Agents must not enter infinite loops.

Evaluation should test:

Tool Failure
   ↓
Retry
   ↓
Retry
   ↓
Retry

and verify that retry limits eventually trigger fallback or escalation.

⸻

53. Agent Goal Drift

Evaluation should test whether agents remain aligned with the original task.

For example:

Goal:
Book an appointment.
Agent must not:
Modify unrelated patient data.

⸻

54. Prompt Injection Evaluation

Evaluation datasets should include adversarial messages attempting to:

* override system instructions
* reveal secrets
* access unauthorized data
* manipulate tools
* bypass policies
* impersonate staff
* modify workflows

⸻

55. Data Exfiltration Evaluation

The system should test whether AI can be induced to reveal:

* API keys
* secrets
* internal prompts
* hidden policies
* other patients’ data
* internal database information
* staff-only information

⸻

56. Cross-Tenant Safety Evaluation

Tests must verify that a model cannot retrieve or reveal information from another tenant.

Example:

Tenant A
   ↓
Patient Request
   ↓
Attempt to retrieve Tenant B data

Expected result:

Denied

⸻

57. Privacy Evaluation

AI systems should be evaluated for:

* unnecessary data exposure
* sensitive data retention
* prompt logging
* provider data handling
* accidental disclosure
* cross-user leakage

⸻

58. Prompt and Context Evaluation

AI quality depends on context construction.

Evaluation should compare:

Model Only

against:

Model + Correct Context

and:

Model + Incorrect Context

The system must detect whether context improves or harms results.

⸻

59. Retrieval-Augmented Evaluation

For RAG-based features, evaluate:

1. retrieval recall
2. retrieval precision
3. source authority
4. grounding
5. answer correctness
6. citation correctness where applicable
7. stale knowledge handling

⸻

60. Knowledge Freshness Evaluation

Dynamic information must be tested for freshness.

Example:

Old policy
+
New policy

The system should use the active authoritative policy.

⸻

61. Operational Grounding Evaluation

Test cases should verify that AI uses authoritative systems for:

* appointments
* availability
* current clinic policies
* configured services
* structured pricing
* staff availability

⸻

62. Medical Safety Evaluation

Medical AI capabilities require specialized evaluation.

Tests should include:

* common clinical scenarios
* ambiguous symptoms
* red-flag symptoms
* contraindications
* medication questions
* emergency situations
* uncertainty
* inappropriate self-treatment requests
* requests for diagnosis

⸻

63. Clinical Boundary Testing

The system should test whether AI improperly:

* diagnoses
* prescribes
* changes medications
* declares eligibility
* provides definitive treatment decisions
* minimizes serious symptoms

⸻

64. Emergency Escalation Evaluation

For potentially urgent messages, evaluate whether the system:

1. recognizes the safety signal
2. avoids false reassurance
3. avoids unsafe delay
4. follows configured escalation policy
5. communicates appropriately

⸻

65. Image Model Evaluation

Image-capable AI should be evaluated for:

* image quality sensitivity
* blur
* lighting
* occlusion
* angle
* resolution
* skin tone variation
* demographic robustness
* artifact sensitivity
* false confidence

⸻

66. Facial Analysis Evaluation

Facial analysis must distinguish between:

Observable Image Characteristics

and:

Clinical Diagnosis

Evaluation must prevent unsupported medical conclusions.

⸻

67. Image Quality Thresholds

Image analysis should define minimum acceptable conditions.

Possible dimensions:

* resolution
* sharpness
* illumination
* face visibility
* orientation
* obstruction

If requirements are not met:

ABSTAIN

should be preferred over fabricated analysis.

⸻

68. Bias and Fairness Evaluation

Models should be evaluated for systematic performance differences across relevant groups where appropriate and lawful.

Potential dimensions may include:

* language
* skin tone
* age range
* sex where relevant to the task
* communication style
* channel

Fairness evaluation must be task-specific.

⸻

69. Bias Response

If meaningful performance disparities are detected:

1. identify cause
2. quantify impact
3. restrict affected capability if necessary
4. improve data or prompting
5. re-evaluate
6. document decision

⸻

70. Regression Testing

Every significant AI change should trigger regression evaluation.

Changes include:

* model version
* provider
* prompt
* system instructions
* tools
* retrieval logic
* context construction
* workflow
* policy
* output schema
* routing logic

⸻

71. Regression Suite

The regression suite should include:

* historical failures
* high-risk cases
* common cases
* multilingual cases
* edge cases
* production incidents
* tool-use cases
* policy cases

⸻

72. Regression Gate

A change should not be promoted if it causes unacceptable regression.

Example:

New Model
↓
Overall score improves
BUT
Safety score decreases materially

The model must not automatically pass.

⸻

73. Critical Metric Protection

Certain metrics should act as hard gates.

Examples:

Critical Safety Violations = 0
Unauthorized Data Disclosure = 0
Unauthorized Tool Execution = 0
Invalid Critical State Transition = 0

Thresholds may vary by task, but critical failures require explicit governance.

⸻

74. Benchmarking

Models should be benchmarked against:

* current production model
* candidate models
* deterministic baseline where available
* previous approved version

⸻

75. Baseline

Every AI capability should have a defined baseline.

A baseline may be:

Current Production Model

or:

Deterministic Rule System

or:

Human Performance

depending on the task.

⸻

76. Human Baseline

For selected tasks, human performance should be measured.

This provides context for AI performance.

Example:

Human agreement: 96%
Model agreement: 91%

This may indicate that the model is not yet suitable for the task.

⸻

77. Evaluation Metrics by Task

Different tasks require different metrics.

Classification

* accuracy
* precision
* recall
* F1
* confusion matrix

Extraction

* field accuracy
* precision
* recall
* completeness

Retrieval

* recall@k
* precision@k
* MRR
* nDCG

Generation

* factuality
* relevance
* completeness
* safety
* human preference

Tool Use

* tool accuracy
* argument validity
* task completion
* unauthorized call rate

⸻

78. Cost Metrics

AI evaluation should include:

* input token cost
* output token cost
* total request cost
* average cost per workflow
* cost per successful outcome
* cost per patient interaction

⸻

79. Latency Metrics

Measure:

* time to first token
* total response time
* tool latency
* retrieval latency
* workflow latency
* provider latency

Interactive workflows should have explicit latency budgets.

⸻

80. Reliability Metrics

Measure:

* success rate
* timeout rate
* provider error rate
* malformed output rate
* tool failure rate
* retry rate
* fallback rate

⸻

81. Availability

Model availability should be measured independently from model quality.

A high-quality model that is unavailable is not operationally reliable.

⸻

82. Provider Reliability

Providers should be evaluated for:

* uptime
* latency
* rate limits
* error rates
* model stability
* pricing stability
* API compatibility

⸻

83. Provider Independence

Clinicos should avoid architectural dependency on one AI provider.

The model gateway should allow:

Provider A
Provider B
Provider C
Provider D

without requiring major product redesign.

⸻

84. Model Routing Evaluation

Routing decisions should be evaluated.

Example:

Task
 ↓
Model Router
 ↓
Selected Model

The router should be measured for:

* correct model selection
* cost efficiency
* quality
* latency
* fallback effectiveness

⸻

85. Dynamic Model Routing

Routing may consider:

* task type
* language
* risk level
* complexity
* latency budget
* cost budget
* provider health
* model quality

⸻

86. Routing Safety

A router must never choose a lower-quality model for a high-risk task solely because it is cheaper.

Risk requirements must act as constraints.

⸻

87. Shadow Evaluation

A candidate model may run in shadow mode.

Example:

Production Request
       ↓
Production Model → Real Response
       ↓
Candidate Model → Evaluation Only

The candidate result must not affect the patient.

⸻

88. Shadow Data Handling

Shadow evaluation must respect:

* privacy
* consent
* data minimization
* provider policies
* retention rules

Production data must not automatically be sent to every candidate provider.

⸻

89. Canary Deployment

A candidate model may receive a small percentage of eligible traffic.

Canary evaluation should monitor:

* safety
* quality
* errors
* latency
* cost
* escalation
* user outcomes

⸻

90. Canary Eligibility

Canary traffic should be restricted by:

* tenant
* workflow
* language
* risk level
* user cohort
* percentage

High-risk workflows may require stronger restrictions.

⸻

91. Canary Stop Conditions

A canary should automatically stop or rollback if:

* critical safety violations increase
* error rates exceed threshold
* latency exceeds threshold
* hallucination increases materially
* unauthorized actions occur
* cost increases beyond limits

⸻

92. Production Monitoring

Production AI systems require continuous monitoring.

Monitoring should include:

Quality
Safety
Reliability
Latency
Cost
Drift
User Feedback
Human Corrections

⸻

93. AI Observability Record

Each AI invocation should be traceable through:

request_id
tenant_id
workflow_id
agent_id
task
model_id
model_version
prompt_version
policy_version
knowledge_version
tool_calls
latency
token_usage
cost
result_status
evaluation_signals

Sensitive content should be minimized or protected.

⸻

94. Prompt Versioning

Prompts are production software artifacts.

Every important prompt should have:

* prompt ID
* version
* owner
* purpose
* risk level
* change history
* evaluation status

⸻

95. Prompt Change Governance

A prompt change may alter model behavior substantially.

Therefore prompt changes should trigger evaluation when they affect:

* task behavior
* safety
* tools
* policy
* output format
* context

⸻

96. System Instruction Governance

System-level instructions should be:

* versioned
* access-controlled
* tested
* auditable

Unauthorized prompt modification must be prevented.

⸻

97. Tool Configuration Governance

Changes to tools may be equivalent to model changes.

For example:

Before:
AI can read appointment availability.
After:
AI can create appointments.

This is a major capability change and requires re-evaluation.

⸻

98. Knowledge Version Governance

Changes to retrieved knowledge can change AI behavior.

Therefore:

Model Version
+
Prompt Version
+
Knowledge Version
+
Tool Version

should be traceable for important AI outputs.

⸻

99. Evaluation Reproducibility

Evaluation runs should record:

* dataset version
* model version
* prompt version
* system configuration
* temperature or sampling configuration
* tool configuration
* knowledge version
* evaluator version

⸻

100. Randomness

Where models are stochastic, evaluation should account for variability.

Possible approaches:

* fixed seeds where supported
* repeated runs
* distribution-based metrics
* confidence intervals

A single run should not always be treated as definitive.

⸻

101. Statistical Significance

When comparing models, meaningful differences should be distinguished from random variation.

Where appropriate, use:

* confidence intervals
* bootstrap methods
* paired comparisons
* significance tests

⸻

102. Evaluation Repetition

High-risk capabilities should be evaluated across multiple runs when stochasticity can materially affect outcomes.

⸻

103. Evaluation Drift

The evaluation system itself can become stale.

Clinicos should monitor:

* outdated test cases
* changing patient behavior
* new languages
* new procedures
* new workflows
* new attack patterns
* new model capabilities

⸻

104. Production Drift

Production behavior may change over time.

Possible drift signals:

* intent distribution changes
* language distribution changes
* increasing escalation
* increasing correction rate
* new failure categories
* new hallucination patterns

⸻

105. Data Drift

Monitor changes in:

* input length
* language
* vocabulary
* service types
* channel distribution
* patient behavior
* image characteristics

⸻

106. Concept Drift

Concept drift occurs when the meaning or relationship between inputs and desired outputs changes.

Examples:

* clinic policy changes
* new services
* new appointment rules
* new communication practices

The evaluation set must evolve accordingly.

⸻

107. Human Correction as Signal

Human corrections are valuable evaluation data.

Examples:

AI:
"Appointment confirmed."
Human:
"Appointment was only requested."

This should become a potential regression case.

⸻

108. User Feedback

User feedback may provide signals such as:

* thumbs up
* thumbs down
* correction
* escalation
* complaint
* abandonment

Feedback should be interpreted carefully.

A positive response does not necessarily prove factual correctness.

⸻

109. Outcome-Based Evaluation

Where possible, evaluate real outcomes.

Examples:

* appointment successfully booked
* follow-up completed
* lead converted
* patient required correction
* human takeover occurred
* task resolved

Outcome metrics should complement text-quality metrics.

⸻

110. AI Success Definition

AI success should be defined at the task level.

Example:

Task:
Book appointment
Success:
Valid appointment created
+
Correct patient
+
Correct service
+
Valid slot
+
Required confirmation
+
No policy violation

A fluent response alone is not success.

⸻

111. End-to-End Evaluation

End-to-end evaluation should test:

Input
 ↓
AI
 ↓
Tools
 ↓
Workflow
 ↓
Database
 ↓
Notification
 ↓
User Outcome

This is required for important workflows.

⸻

112. Failure Taxonomy

AI failures should be classified.

Recommended categories:

F01 — Factual Error
F02 — Hallucination
F03 — Safety Violation
F04 — Policy Violation
F05 — Wrong Intent
F06 — Wrong Entity
F07 — Wrong Tool
F08 — Invalid Tool Arguments
F09 — Structured Output Failure
F10 — Retrieval Failure
F11 — Context Failure
F12 — Language Failure
F13 — Prompt Injection Success
F14 — Privacy Failure
F15 — Latency Failure
F16 — Provider Failure
F17 — Workflow Failure
F18 — Cost Failure
F19 — Human Escalation Failure
F20 — Other

⸻

113. Failure Severity

Recommended severity:

S0 — Cosmetic
S1 — Minor
S2 — Operationally Significant
S3 — Serious
S4 — Critical / Safety

⸻

114. Critical AI Incident

A critical incident may include:

* patient safety risk
* medical misinformation causing potential harm
* unauthorized patient data disclosure
* cross-tenant data exposure
* unauthorized clinical action
* unauthorized external side effect
* widespread incorrect communication

Critical incidents require immediate containment.

⸻

115. Incident Response

AI incident response should follow:

Detect
 ↓
Contain
 ↓
Assess
 ↓
Mitigate
 ↓
Investigate
 ↓
Correct
 ↓
Re-evaluate
 ↓
Recover
 ↓
Document

⸻

116. AI Kill Switch

Clinicos must support emergency disabling of:

* model
* provider
* agent
* workflow
* tool
* outbound automation
* AI category
* tenant AI features

⸻

117. Automatic Rollback

Where technically safe, the system should support automatic rollback based on predefined conditions.

Examples:

Critical safety violation
Provider instability
Mass malformed output
Unexpected cost spike

⸻

118. Model Deprecation

Models should be deprecated when:

* provider announces retirement
* quality becomes insufficient
* cost becomes uncompetitive
* latency becomes unacceptable
* safety issues emerge
* better approved alternatives exist
* required capabilities are missing

⸻

119. Model Retirement

Retired models must not receive production traffic.

Historical records must continue to reference the retired model identity.

⸻

120. Model Replacement

Replacing a model requires evaluation of:

Old Model
vs
New Model

across relevant tasks.

Replacement must not rely solely on provider benchmarks.

⸻

121. Benchmark Independence

External benchmarks may inform decisions but must not be the sole basis for production approval.

Clinicos-specific evaluation is mandatory.

⸻

122. Model Card

Every production model should have an internal model card containing:

* intended use
* prohibited use
* provider
* version
* capabilities
* limitations
* languages
* risk classification
* evaluation results
* known failure modes
* cost profile
* latency profile
* approval status

⸻

123. AI Capability Card

Each product AI capability should also have a capability card.

Example:

Capability:
Lead Qualification
Risk:
R1
Allowed Models:
Model A
Model B
Required Tools:
Patient Lookup
Human Review:
Only on low confidence
Critical Failures:
Incorrect patient association

⸻

124. Approval Authority

Approval authority should depend on risk.

Example:

R0:
AI Engineering
R1:
AI Engineering + Product
R2:
AI Engineering + Product + Operations
R3:
AI Engineering + Security + Operations
R4:
AI Engineering + Clinical Safety + Security + Product

Exact governance may evolve.

⸻

125. Change Classification

AI changes should be classified as:

Minor
Moderate
Major
Critical

⸻

126. Minor Changes

Examples:

* wording adjustment
* non-functional logging
* metadata change

May require limited evaluation.

⸻

127. Moderate Changes

Examples:

* prompt modification
* retrieval change
* model routing change
* output schema modification

Require regression evaluation.

⸻

128. Major Changes

Examples:

* model replacement
* new tool access
* new agent capability
* workflow behavior change
* new patient-facing automation

Require broader evaluation and controlled deployment.

⸻

129. Critical Changes

Examples:

* clinical AI capability
* autonomous high-impact action
* sensitive data access
* major safety policy change

Require formal review and approval.

⸻

130. AI Release Pipeline

Recommended pipeline:

Development
    ↓
Static Validation
    ↓
Offline Evaluation
    ↓
Safety Evaluation
    ↓
Human Evaluation
    ↓
Regression Gate
    ↓
Shadow
    ↓
Canary
    ↓
Production
    ↓
Continuous Monitoring

⸻

131. Evaluation Gate

A release should pass all applicable gates.

Example:

Schema Gate
Safety Gate
Quality Gate
Regression Gate
Latency Gate
Cost Gate
Security Gate
Operational Gate

⸻

132. Hard vs Soft Gates

Hard gates must block release.

Examples:

Critical safety failure
Unauthorized data access
Invalid critical tool execution

Soft gates may trigger review.

Examples:

Small latency regression
Small cost increase
Minor language quality decrease

⸻

133. Model Scorecard

Each candidate model should receive a scorecard.

Example:

Task Quality        92
Safety              99
Reliability         97
Tool Accuracy       95
Persian Quality     90
Latency             85
Cost Efficiency     88
Overall             Approved

The exact scoring methodology must be defined per capability.

⸻

134. Weighted Scoring

Weighted scoring may be used for model selection.

Example:

Overall Score =
Quality × 0.30
+
Safety × 0.30
+
Reliability × 0.15
+
Tool Accuracy × 0.10
+
Latency × 0.05
+
Cost × 0.10

Weights are task-specific.

For high-risk tasks, safety should dominate.

⸻

135. Constraint-Based Selection

For high-risk capabilities, weighted scoring alone is insufficient.

Example:

If Safety < threshold:
    Reject
Else:
    Compare Quality / Cost / Latency

⸻

136. Pareto Evaluation

Models may be compared across:

Quality
Safety
Latency
Cost

A model is preferable when it improves one or more dimensions without unacceptable regression in others.

⸻

137. Model Selection Objective

The goal is not:

Choose the highest benchmark score.

The goal is:

Choose the safest and most effective model
for the specific Clinicos task
under operational constraints.

⸻

138. Cost Governance

Every production AI capability should have:

* expected cost
* maximum cost
* budget owner
* usage limits
* alert thresholds

⸻

139. Cost Anomaly Detection

Detect:

* sudden token spikes
* unusually long prompts
* repeated retries
* agent loops
* unexpected model routing
* abusive usage

⸻

140. Token Budget

AI workflows may define:

maximum input tokens
maximum output tokens
maximum tool calls
maximum retries
maximum total cost

⸻

141. Latency Budget

Each interactive AI workflow should define an acceptable latency budget.

If exceeded:

Fallback
Degrade
Stream
Escalate

depending on workflow.

⸻

142. Quality-Cost Tradeoff

Cost optimization must preserve minimum quality and safety thresholds.

Example:

Do not replace a model with a cheaper model
if the cheaper model violates the task's quality gate.

⸻

143. Provider Quotas

Providers may impose:

* rate limits
* daily quotas
* monthly quotas
* concurrency limits

The gateway should monitor these.

⸻

144. Provider Failure Routing

When a provider fails:

Primary Provider
      ↓
Health Check
      ↓
Fallback Provider
      ↓
Alternative Model
      ↓
Deterministic Fallback
      ↓
Human Escalation

⸻

145. Fallback Evaluation

Fallback paths must be evaluated independently.

A fallback that works technically but produces unsafe outputs is not a valid fallback.

⸻

146. Degraded Mode

Clinicos should support degraded operation.

Example:

AI unavailable
↓
Use deterministic FAQ
↓
Capture appointment request
↓
Create human task

The clinic should remain operational where possible.

⸻

147. AI Dependency Risk

Critical workflows should avoid depending exclusively on AI.

Examples:

Appointment system

must remain functional without AI.

AI should assist the workflow rather than become the sole source of truth.

⸻

148. Human Override

Humans must be able to override AI recommendations where authorized.

Overrides should be recorded.

⸻

149. Override Analysis

Clinicos should measure:

* override frequency
* override reason
* model
* workflow
* language
* staff role

High override rates may indicate model or workflow problems.

⸻

150. Human Correction Taxonomy

Corrections may include:

Wrong Fact
Wrong Intent
Wrong Tone
Wrong Patient
Wrong Appointment
Missing Information
Unsafe Recommendation
Wrong Language
Policy Violation
Other

⸻

151. Continuous Learning Loop

Production feedback should feed an improvement loop:

Production
 ↓
Observe
 ↓
Detect Failure
 ↓
Classify
 ↓
Add Evaluation Case
 ↓
Improve
 ↓
Evaluate
 ↓
Deploy
 ↓
Monitor

⸻

152. No Uncontrolled Online Learning

Production data must not automatically modify model behavior without governance.

Clinicos should not implement uncontrolled:

Production Output
 ↓
Automatic Training
 ↓
Immediate Production Deployment

⸻

153. Dataset Promotion

A production case should become part of an evaluation dataset only after appropriate review.

Sensitive information must be handled according to privacy requirements.

⸻

154. Synthetic Data

Synthetic cases may be used for:

* edge cases
* rare scenarios
* adversarial testing
* privacy-preserving development

Synthetic data must not be assumed to perfectly represent real patients.

⸻

155. Production Sampling

Clinicos may sample production interactions for quality evaluation.

Sampling must respect:

* privacy
* consent
* retention
* access control
* applicable regulations

⸻

156. Evaluation Privacy

Evaluation datasets should avoid unnecessary personally identifiable information.

Where possible:

Raw Patient Data
      ↓
De-identification
      ↓
Evaluation Dataset

⸻

157. Sensitive Evaluation Cases

High-risk evaluation data should have restricted access.

Access should be:

* role-based
* logged
* minimized
* time-limited where appropriate

⸻

158. Evaluation Environment

Evaluation should occur in controlled environments.

Possible environments:

Local
Development
Staging
Evaluation
Shadow
Canary
Production

Production experiments must be explicitly controlled.

⸻

159. Evaluation Isolation

Evaluation workloads must not accidentally:

* modify production state
* send patient messages
* create appointments
* trigger workflows
* charge patients
* alter clinic policies

⸻

160. Side-Effect Protection

Evaluation tools should default to:

Read Only

unless explicitly configured otherwise.

⸻

161. Evaluation Sandbox

A sandbox should support:

* fake patients
* fake appointments
* fake schedules
* fake messages
* fake tools
* deterministic fixtures

⸻

162. Evaluation Replay

Historical interactions may be replayed in a sandbox.

Replay should preserve relevant context while preventing real-world side effects.

⸻

163. Model Evaluation API

The platform should expose evaluation capabilities through APIs.

Potential operations:

create_evaluation_run
start_evaluation_run
get_evaluation_run
compare_models
get_scorecard
approve_model
reject_model
create_regression_case

⸻

164. Evaluation Run

An evaluation run should contain:

* run ID
* model
* model version
* dataset
* dataset version
* prompt version
* evaluator version
* configuration
* start time
* end time
* results
* failures
* approval status

⸻

165. Evaluation Result

Each case should record:

case_id
model_id
output
expected_behavior
score
failure_type
severity
evaluator
timestamp

⸻

166. Evaluation Artifact

Important evaluation artifacts should be retained:

* prompts
* outputs
* scores
* logs
* model metadata
* dataset version
* evaluator version
* configuration

⸻

167. Evaluation Dashboard

The evaluation dashboard should show:

* model comparison
* quality trends
* safety trends
* regression
* cost
* latency
* language performance
* workflow performance
* failure categories

⸻

168. Trend Analysis

Track performance over time.

Example:

Model Quality
↑
Hallucination
↓
Human Correction
↓
Cost
→

A single evaluation run should not be the only decision signal.

⸻

169. Model Performance by Language

Performance should be segmented by:

Persian
English
Azerbaijani Turkish
Arabic
Turkish

A high global score can hide poor performance in one language.

⸻

170. Model Performance by Workflow

Measure separately for:

* lead qualification
* FAQ
* appointment assistance
* follow-up
* summarization
* patient communication
* image analysis
* clinical safety workflows

⸻

171. Model Performance by Risk Level

Report:

R0 performance
R1 performance
R2 performance
R3 performance
R4 performance

Higher-risk tasks should have stricter thresholds.

⸻

172. Model Performance by Tenant

Where privacy and statistical validity allow, identify tenant-specific degradation.

One clinic’s workflow may expose failures not seen elsewhere.

⸻

173. Small-Sample Caution

Low sample sizes must not be treated as strong evidence.

Reports should expose:

Sample Size
Confidence

where appropriate.

⸻

174. Evaluation Confidence

Model decisions should communicate confidence in the evaluation itself.

Example:

High confidence:
10,000 representative cases
Low confidence:
42 synthetic cases

⸻

175. Benchmark Leakage

Evaluation datasets must be protected from accidental contamination.

A model should not pass because the exact test cases were included in training or prompt examples.

⸻

176. Prompt Benchmark Leakage

Few-shot examples should not accidentally contain final benchmark cases.

⸻

177. Evaluator Drift

If evaluator models change, historical scores may no longer be directly comparable.

Evaluator versions must therefore be recorded.

⸻

178. Judge Calibration

LLM judges should be calibrated against human-reviewed cases.

The judge should be periodically checked for:

* systematic bias
* model favoritism
* language bias
* verbosity bias
* refusal bias

⸻

179. Human Preference vs Correctness

Human preference should not override factual correctness.

A persuasive but incorrect answer should not win against a correct but less polished answer.

⸻

180. Fluency Trap

Clinicos must explicitly guard against:

Fluent ≠ Correct
Confident ≠ Correct
Long ≠ Better
Human-like ≠ Safe

⸻

181. Evaluation Anti-Patterns

Clinicos must avoid:

Anti-Pattern 1

Using one benchmark to approve every AI capability.

Anti-Pattern 2

Evaluating only English.

Anti-Pattern 3

Evaluating only average scores.

Anti-Pattern 4

Ignoring rare catastrophic failures.

Anti-Pattern 5

Using LLM-as-judge as absolute truth.

Anti-Pattern 6

Testing only successful scenarios.

Anti-Pattern 7

Ignoring tool-call failures.

Anti-Pattern 8

Ignoring latency and cost.

Anti-Pattern 9

Testing a model without its production context.

Anti-Pattern 10

Deploying a new model without regression testing.

Anti-Pattern 11

Training directly on unreviewed production outputs.

Anti-Pattern 12

Treating provider benchmark claims as Clinicos evidence.

Anti-Pattern 13

Allowing high-risk model routing based only on cost.

Anti-Pattern 14

Allowing silent model changes.

Anti-Pattern 15

Failing to preserve historical model identity.

⸻

182. AI Governance Decision Matrix

A simplified decision model:

                    Low Risk      Medium Risk      High Risk
----------------------------------------------------------------
Offline Eval          Required       Required        Required
Safety Eval           Basic          Strong          Extensive
Human Review          Optional       Recommended    Required
Shadow                Optional       Recommended    Required
Canary                Recommended    Required        Controlled
Kill Switch           Required       Required        Required
Audit                 Required       Required        Required
Clinical Review       No             Sometimes       Required

⸻

183. Production Readiness Checklist

Before production approval:

[ ] Model registered
[ ] Model identity recorded
[ ] Intended task defined
[ ] Risk level defined
[ ] Allowed use defined
[ ] Prohibited use defined
[ ] Dataset evaluated
[ ] Regression suite passed
[ ] Safety evaluation passed
[ ] Tool evaluation passed if applicable
[ ] Multilingual evaluation passed
[ ] Latency acceptable
[ ] Cost acceptable
[ ] Privacy reviewed
[ ] Security reviewed
[ ] Human escalation configured
[ ] Fallback configured
[ ] Kill switch configured
[ ] Monitoring configured
[ ] Owner assigned
[ ] Approval recorded

⸻

184. Model Promotion Checklist

A candidate model may be promoted when:

Quality ≥ Task Threshold
Safety ≥ Safety Threshold
Reliability ≥ Reliability Threshold
Latency ≤ Latency Budget
Cost ≤ Cost Budget
No Critical Failure
Regression Gate Passed
Operational Gate Passed

⸻

185. Model Rejection Checklist

A model should be rejected when:

Critical safety failure
OR
Unauthorized data access
OR
Unacceptable task accuracy
OR
Unacceptable policy violations
OR
Unacceptable reliability
OR
Unacceptable operational cost
OR
Unacceptable latency

⸻

186. Model Restriction

A model may be restricted rather than fully rejected.

Examples:

Approved for:
R0 / R1
Not approved for:
R2 / R3 / R4

or:

Approved for:
English
Restricted for:
Persian

⸻

187. Capability-Level Approval

Approval should be granted at the capability level.

Example:

Model:
X
Capability:
FAQ Response
Status:
Approved
Capability:
Appointment Booking
Status:
Restricted

⸻

188. Tenant-Level Governance

Different clinics may have different:

* policies
* languages
* workflows
* risk tolerances
* enabled features

However, tenant-specific configuration must not weaken platform-level safety requirements.

⸻

189. Clinic-Specific Evaluation

Where clinic workflows are highly customized, tenant-specific evaluation cases may be required.

Examples:

* custom cancellation policy
* custom services
* custom appointment rules
* custom communication style

⸻

190. Governance Hierarchy

The AI governance hierarchy should be:

Platform Safety
        ↓
Security / Privacy
        ↓
Clinical Safety
        ↓
Legal / Compliance
        ↓
Clinic Policy
        ↓
Workflow Policy
        ↓
AI Capability Policy
        ↓
Model Preference

Lower layers must not override higher layers.

⸻

191. AI Governance Board

As Clinicos scales, a formal governance group may review high-impact AI changes.

Potential members:

* AI engineering
* product
* security
* clinical safety
* QA
* operations
* legal/compliance where applicable

⸻

192. Governance Review Triggers

Formal review may be triggered by:

* new high-risk capability
* major model replacement
* safety incident
* privacy incident
* major provider change
* new clinical workflow
* major autonomous action
* significant performance regression

⸻

193. Documentation Requirements

Each production AI capability should document:

* purpose
* owner
* model
* prompt
* tools
* data sources
* risk level
* evaluation
* known limitations
* fallback
* monitoring
* approval
* rollback procedure

⸻

194. Model Decision Record

Important model decisions should produce a decision record.

Example:

Decision:
Replace Model A with Model B
Reason:
Model B improves Persian intent classification by 8%
while maintaining safety thresholds.
Risks:
Higher latency
Mitigation:
Use Model B only for complex Persian classification.

⸻

195. Architecture Independence

AI governance must remain independent of any specific provider.

The specification must remain valid if Clinicos changes:

Provider
Model
Gateway
Hosting
Inference architecture

⸻

196. Future Model Types

The governance system should be extensible to:

* multimodal models
* reasoning models
* small local models
* specialized medical models
* embedding models
* vision models
* speech models
* agent models
* ensemble systems

⸻

197. Local Model Governance

If Clinicos later deploys local or self-hosted models, they must follow the same evaluation principles.

Self-hosting does not automatically imply safety.

⸻

198. Open-Source Model Governance

Open-source models require evaluation of:

* model provenance
* license
* training characteristics where known
* vulnerabilities
* update history
* inference behavior
* security

⸻

199. Third-Party Provider Governance

Third-party providers should be evaluated for:

* data handling
* retention
* security
* reliability
* pricing
* API stability
* model changes
* regional availability

⸻

200. Provider Model Change

If a provider changes a model materially:

Detect
 ↓
Mark Model Revision
 ↓
Run Regression
 ↓
Safety Evaluation
 ↓
Decide

Silent acceptance should be avoided.

⸻

201. AI Supply Chain

Clinicos should maintain visibility into:

Provider
 ↓
Model
 ↓
Gateway
 ↓
Prompt
 ↓
Tools
 ↓
Knowledge
 ↓
Workflow
 ↓
Product

A change anywhere in this chain may affect behavior.

⸻

202. AI Configuration Fingerprint

For critical workflows, Clinicos should generate a configuration fingerprint based on:

* model
* model version
* prompt
* tools
* knowledge version
* policy version
* routing configuration

This allows historical outputs to be traced to a specific AI configuration.

⸻

203. Reproducibility Limitations

Exact reproduction may not always be possible because:

* providers may update models
* inference may be stochastic
* external knowledge may change
* tools may return different data

The system should therefore preserve enough metadata to maximize reproducibility.

⸻

204. Evaluation Storage

Evaluation results should be stored independently from transient application logs.

They should support:

* historical comparison
* audit
* reporting
* regression analysis

⸻

205. Evaluation Retention

Evaluation artifacts should have defined retention policies.

High-value safety cases should be retained according to governance requirements.

⸻

206. Evaluation Security

Evaluation systems must protect:

* patient data
* model outputs
* prompts
* internal instructions
* benchmark datasets
* provider credentials

⸻

207. AI Governance Metrics

Organization-level governance metrics should include:

* critical AI incidents
* safety violations
* hallucination rate
* human correction rate
* unauthorized action rate
* model regression rate
* evaluation coverage
* multilingual coverage
* mean time to detect
* mean time to contain
* mean time to recover

⸻

208. Evaluation Coverage

Clinicos should track what percentage of AI behavior is covered by evaluation.

Possible dimensions:

Task Coverage
Language Coverage
Risk Coverage
Workflow Coverage
Tool Coverage
Failure Coverage

⸻

209. Unknown Failure Rate

Clinicos should monitor failures that do not fit existing categories.

A high unknown-failure rate indicates that the failure taxonomy is incomplete.

⸻

210. Safety Margin

Production thresholds should include safety margin.

A model that barely passes should not necessarily be treated as robust.

Example:

Required Safety Score: 95
Observed: 95.1

This may warrant additional evaluation before approval.

⸻

211. Robustness Testing

Models should be tested against variations such as:

* spelling errors
* slang
* incomplete messages
* contradictory information
* long messages
* short messages
* multilingual input
* adversarial input
* noisy images

⸻

212. Stress Testing

AI systems should be tested under:

* high request volume
* provider throttling
* long prompts
* repeated tool failures
* queue backlog
* concurrent requests

⸻

213. Resilience Testing

Failure scenarios should include:

Provider Down
Model Timeout
Tool Down
Database Delay
Queue Delay
Network Failure
Invalid Response
Rate Limit

⸻

214. Chaos Evaluation

Selected AI infrastructure may undergo controlled failure testing.

Examples:

Disable provider
Delay tool
Return malformed output
Duplicate event
Drop event

The system should recover safely.

⸻

215. AI Security Evaluation

Security testing should include:

* prompt injection
* jailbreak attempts
* tool abuse
* data exfiltration
* privilege escalation
* cross-tenant access
* malicious file input
* malicious image input

⸻

216. File and Image Safety

AI systems receiving files or images should be evaluated for:

* malicious payloads
* unsupported formats
* oversized files
* corrupted files
* prompt injection embedded in documents
* sensitive information extraction

⸻

217. AI Output Sanitization

AI output must be treated as untrusted data until validated.

This is especially important for:

* HTML
* Markdown
* SQL
* tool arguments
* URLs
* executable instructions

⸻

218. AI-Generated Code

If AI is used to generate code for Clinicos:

* generated code must undergo normal software review
* security testing remains mandatory
* AI approval does not equal code approval

AI coding assistance must not bypass engineering quality gates.

⸻

219. AI-Generated Configuration

AI-generated:

* workflows
* policies
* templates
* prompts
* routing rules

must undergo validation before activation.

⸻

220. AI-Generated Clinical Content

AI-generated clinical content must follow clinical review requirements appropriate to the use case.

It must not be treated as authoritative merely because it was generated by a specialized model.

⸻

221. AI Governance for Autonomous Actions

Autonomous actions should have explicit authorization boundaries.

Examples:

Send informational message
→ May be automated
Book appointment
→ Requires validated operational conditions
Modify clinical record
→ Requires authorized human workflow
Change medication
→ Human clinical control required

⸻

222. Action Risk Matrix

Each action should define:

Risk
Authorization
Required Confidence
Human Approval
Audit Requirement
Rollback / Compensation

⸻

223. Confidence Thresholds

Confidence thresholds may be used, but confidence alone must not determine safety.

A model can be confidently wrong.

Therefore:

Confidence
+
Evidence
+
Policy
+
Risk

must be considered together.

⸻

224. Evidence Requirement

High-impact AI actions should require evidence.

Evidence may include:

* authoritative database result
* approved knowledge source
* validated tool output
* human approval

⸻

225. Evidence Freshness

Evidence should have a freshness requirement.

For dynamic facts:

Current data

must be preferred over cached historical information when appropriate.

⸻

226. AI Decision Trace

For high-impact decisions, the system should preserve:

* inputs
* relevant context
* model
* version
* tools
* evidence
* policy
* decision
* action
* human approval if applicable

⸻

227. Explainability

Clinicos should distinguish:

Explanation

from:

Internal Chain of Thought

The system should not require exposing hidden model reasoning.

Instead, it should provide structured evidence and decision metadata where appropriate.

⸻

228. Safe Explanation

A safe explanation may state:

"Appointment availability was confirmed using the scheduling system."

rather than exposing internal reasoning.

⸻

229. Patient-Facing AI Disclosure

Where required or appropriate, patients may be informed that AI assistance is being used.

Disclosure policy should consider:

* jurisdiction
* clinic policy
* interaction type
* risk
* applicable regulations

⸻

230. AI Identity

Patient-facing systems should not falsely represent AI as a human.

Where an AI agent communicates autonomously, the product should follow applicable disclosure requirements.

⸻

231. Human Escalation Transparency

When escalation occurs, the system should communicate appropriate expectations.

Example:

"I will pass this to the clinic team for review."

The system should not falsely imply that a doctor has already reviewed the message.

⸻

232. Continuous Improvement Governance

Every improvement cycle should answer:

What failed?
Why did it fail?
How often?
How severe?
What changed?
Did the change improve the problem?
Did it create new problems?

⸻

233. Before / After Evaluation

Every major AI improvement should compare:

Before
vs
After

across relevant metrics.

⸻

234. Improvement Acceptance

A change should be accepted only when:

Target Metric Improves
AND
No Critical Regression
AND
Safety Maintained
AND
Operational Constraints Maintained

⸻

235. No Single-Metric Optimization

Clinicos must avoid optimizing exclusively for:

* response rate
* conversion
* speed
* cost
* user satisfaction
* benchmark score

A system can improve one metric while becoming unsafe.

⸻

236. Business Metric Guardrails

Business metrics may be monitored, but they must not override safety.

For example:

Conversion ↑
Safety ↓

must be treated as a failed optimization.

⸻

237. Patient Experience Metrics

Measure:

* satisfaction
* abandonment
* response quality
* escalation experience
* communication clarity
* repeated questions

Patient experience is important but does not replace correctness.

⸻

238. Operational Efficiency Metrics

Measure:

* staff time saved
* task completion time
* response time
* follow-up completion
* appointment utilization
* manual workload

⸻

239. AI ROI

AI ROI should consider:

Value Generated
-
AI Cost
-
Operational Cost
-
Correction Cost
-
Incident Cost

A cheap AI system that creates expensive errors is not cost-effective.

⸻

240. Correction Cost

Correction cost may include:

* staff review
* repeated communication
* patient support
* operational remediation
* incident handling

⸻

241. AI Debt

Clinicos should track AI debt.

AI debt includes:

* outdated prompts
* stale evaluation sets
* undocumented models
* untested workflows
* excessive provider dependency
* unreviewed production failures

⸻

242. AI Technical Debt Review

Periodic AI governance reviews should identify:

What AI components are becoming unsafe or obsolete?

⸻

243. Governance Review Frequency

The frequency of formal review should depend on risk.

High-risk systems should be reviewed more frequently than low-risk informational systems.

⸻

244. Model Review Triggers

Re-evaluation should occur when:

* model changes
* prompt changes
* tools change
* knowledge changes materially
* policy changes
* workflow changes
* incident occurs
* drift is detected
* provider changes behavior

⸻

245. Automatic Re-Evaluation

The platform should support automatic re-evaluation after configured changes.

Example:

Prompt Version Updated
        ↓
Regression Suite
        ↓
Safety Suite
        ↓
Approval Gate

⸻

246. Governance Audit Trail

Governance actions must be auditable.

Examples:

* model approved
* model rejected
* model restricted
* model retired
* threshold changed
* evaluator changed
* dataset changed
* capability enabled

⸻

247. Governance Roles

Possible roles:

AI Engineer
AI Reviewer
Clinical Reviewer
Security Reviewer
Product Owner
Operations Owner
Governance Administrator

Permissions must be separated.

⸻

248. Separation of Duties

For high-risk capabilities, the same person should not necessarily:

Create
Evaluate
Approve
Deploy

all without independent review.

⸻

249. Emergency Governance

During a critical incident, authorized operators must be able to disable unsafe AI capabilities immediately.

Formal documentation can follow after containment.

⸻

250. Post-Incident Re-Evaluation

After a serious AI incident:

Incident
 ↓
Containment
 ↓
Root Cause
 ↓
Regression Case
 ↓
Fix
 ↓
Re-Evaluation
 ↓
Controlled Redeployment

⸻

251. Regression Case From Incident

Every meaningful AI failure should be considered for conversion into a permanent regression test.

This prevents repeated failures.

⸻

252. Historical Failure Library

Clinicos should maintain a library of known AI failures.

Categories may include:

* hallucination
* safety
* privacy
* tool use
* language
* workflow
* provider
* prompt injection

⸻

253. Failure Reproduction

Where possible, failures should be reproducible in a controlled environment.

The system should preserve sufficient metadata for reproduction.

⸻

254. AI Governance Maturity

A mature Clinicos AI system should progress through:

Level 1
Basic Evaluation
Level 2
Regression Testing
Level 3
Continuous Monitoring
Level 4
Controlled Deployment
Level 5
Risk-Based Governance
Level 6
Outcome-Based Optimization

⸻

255. Minimum Viable Governance

Even the earliest production AI capability must have:

Model Identity
Task Definition
Risk Classification
Basic Evaluation
Safety Tests
Fallback
Logging
Owner
Kill Switch

⸻

256. Advanced Governance

A mature system should additionally have:

Continuous Evaluation
Drift Detection
Automated Regression
Canary Deployment
Model Routing
Outcome Evaluation
Automated Incident Detection
Governance Dashboard

⸻

257. Reference AI Evaluation Architecture

                         ┌─────────────────────┐
                         │   Model Registry    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Evaluation Manager  │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │ Golden Dataset │   │ Regression Set │   │ Safety Dataset │
     └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                         ┌─────────────────────┐
                         │ Evaluation Engine   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │ Deterministic  │   │ LLM Judge      │   │ Human Review   │
     │ Evaluators     │   │ Evaluators     │   │                │
     └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                         ┌─────────────────────┐
                         │ Evaluation Results  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Governance Gates    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                Reject           Canary          Approve
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Production Monitor  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Feedback / Incidents│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Evaluation Dataset  │
                         └─────────────────────┘

⸻

258. Reference Model Promotion Flow

Candidate Model
      ↓
Register
      ↓
Static Validation
      ↓
Offline Benchmark
      ↓
Safety Evaluation
      ↓
Regression Evaluation
      ↓
Human Evaluation
      ↓
Governance Review
      ↓
Shadow
      ↓
Canary
      ↓
Production
      ↓
Continuous Monitoring

⸻

259. Reference Incident Flow

Production Failure
       ↓
Detect
       ↓
Classify Severity
       ↓
Contain
       ↓
Disable Model / Workflow if Required
       ↓
Assess Patient Impact
       ↓
Investigate
       ↓
Fix
       ↓
Create Regression Case
       ↓
Re-Evaluate
       ↓
Canary
       ↓
Restore Production
       ↓
Document

⸻

260. Reference Continuous Evaluation Loop

Production
   ↓
Signals
   ↓
Feedback
   ↓
Failure Classification
   ↓
Evaluation Case
   ↓
Regression Suite
   ↓
Model / Prompt / Workflow Change
   ↓
Evaluation
   ↓
Controlled Deployment
   ↓
Production Monitoring
   ↓
Repeat

⸻

261. Core AI Governance Invariants

The following invariants are mandatory:

1. Every production AI capability must have an identifiable model configuration.
2. Every AI capability must have an explicit purpose.
3. Every AI capability must have a risk classification.
4. High-risk capabilities require stronger evaluation and human governance.
5. Critical safety failures must block deployment.
6. AI must not be approved solely on provider benchmarks.
7. AI must not be evaluated only in English.
8. Model changes require appropriate regression testing.
9. Prompt changes that materially affect behavior require evaluation.
10. Tool changes that expand capability require evaluation.
11. AI confidence must not be treated as proof of correctness.
12. Missing authoritative information must not be fabricated.
13. High-impact actions require evidence and authorization.
14. Human override must remain possible.
15. Production AI must be observable.
16. AI incidents must be auditable.
17. Critical AI capabilities must have kill switches.
18. Historical model identity must remain traceable.
19. Evaluation datasets must be versioned.
20. Evaluation results must be reproducible to the extent technically possible.
21. Production failures should feed regression testing after appropriate review.
22. Uncontrolled online learning is prohibited.
23. Safety takes precedence over cost and conversion.
24. Provider independence must be preserved.
25. Model approval must be capability-specific.
26. Fallback systems must themselves be evaluated.
27. AI output must be treated as untrusted until validated.
28. AI must not silently bypass workflow policy.
29. AI governance decisions must be auditable.
30. The goal of governance is safe, reliable, measurable AI rather than maximum automation.

⸻

262. Definition of Done

The Clinicos AI Evaluation and Model Governance system is considered implemented when:

Model Management

* model registry exists
* model versions are tracked
* model lifecycle is implemented
* model ownership is defined
* model retirement is supported

Evaluation

* evaluation datasets exist
* golden dataset exists
* regression suite exists
* safety suite exists
* multilingual evaluation exists
* tool-use evaluation exists
* end-to-end evaluation exists

Governance

* risk classification exists
* approval workflow exists
* model scorecards exist
* capability-level approval exists
* governance audit trail exists

Deployment

* shadow mode exists
* canary mode exists
* rollback exists
* kill switches exist
* fallback exists

Monitoring

* quality monitoring exists
* safety monitoring exists
* latency monitoring exists
* cost monitoring exists
* reliability monitoring exists
* drift monitoring exists

Human Oversight

* human review exists
* human override exists
* clinical review exists for applicable capabilities
* escalation exists

Security

* prompt injection testing exists
* privacy evaluation exists
* cross-tenant evaluation exists
* tool authorization testing exists
* sensitive evaluation data is protected

Continuous Improvement

* production feedback can become evaluation cases
* incidents create regression cases
* model replacement can be benchmarked
* evaluation history is preserved

⸻

263. Final Governance Philosophy

Clinicos should never ask only:

"Is this model good?"

The correct questions are:

Is it good for this task?
Is it safe for this task?
Is it reliable enough?
Is it good in the languages we support?
Does it follow clinic policy?
Does it use authoritative information?
Can we detect when it fails?
Can a human intervene?
Can we stop it immediately?
Can we reproduce what happened?
Can we prove that a new version is better?
Can we detect when it becomes worse?
Can we replace it without rebuilding Clinicos?

The target AI governance loop is:

DISCOVER
   ↓
REGISTER
   ↓
CLASSIFY
   ↓
EVALUATE
   ↓
VALIDATE
   ↓
APPROVE
   ↓
SHADOW
   ↓
CANARY
   ↓
DEPLOY
   ↓
MONITOR
   ↓
LEARN
   ↓
RE-EVALUATE
   ↓
IMPROVE
   ↓
REPLACE OR RETIRE

The central principle is:

No AI capability should become trusted merely because it works. It becomes trusted because it has been evaluated, constrained, observed, and continuously governed.

Clinicos should treat AI models as replaceable components inside a governed operational system.

The product must remain safe if:

a model fails,
a provider fails,
a prompt fails,
a tool fails,
a workflow fails,
a model becomes obsolete,
or an AI output is wrong.

The ultimate objective is not to build the most autonomous AI system.

The objective is to build an AI system that is:

measurably useful, operationally reliable, clinically responsible, secure, observable, replaceable, and continuously improvable.
