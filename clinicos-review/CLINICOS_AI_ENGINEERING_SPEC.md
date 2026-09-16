# CLINICOS AI ENGINEERING SPEC
**Document:** CLINICOS_AI_ENGINEERING_SPEC.md  
**Version:** 2.0  
**Status:** Authoritative AI Engineering Specification  
**Effective:** Immediately  
**Language:** English  
**Parent Documents:**
- CLINICOS_MASTER_VISION.md
- CLINICOS_PRODUCT_REQUIREMENTS.md
- CLINICOS_TARGET_ARCHITECTURE.md
- CLINICOS_ARCHITECTURE_CHANGE_SET.md
---
# 1. Purpose
This document defines the engineering architecture and implementation requirements for artificial intelligence within Clinicos.
It specifies:
- AI system boundaries;
- Gemini integration;
- internal AI abstraction;
- model selection;
- AI orchestration;
- agent execution;
- tool usage;
- context construction;
- structured outputs;
- validation;
- safety;
- reliability;
- observability;
- cost management;
- evaluation;
- privacy;
- security;
- failure handling;
- human oversight.
This document defines how AI is engineered inside Clinicos.
It does not redefine the broader Clinicos product architecture.
---
# 2. AI Architecture Status
This document is authoritative for AI engineering decisions.
The target AI architecture uses Google Gemini as the only active AI provider.
Historical AI provider implementations are not authoritative.
The following historical concepts must not be reintroduced into the target runtime architecture:
- FreeLLMAPI;
- OpenRouter;
- DeepSeek;
- Qwen;
- OpenAI runtime integration;
- provider scoring;
- provider ranking;
- provider cooldown routing;
- multi-provider routing;
- AI provider fallback;
- provider failover.
---
# 3. Core AI Decision
Clinicos uses:
```text
Clinicos AI Layer
        |
   Gemini Adapter
        |
   Google Gemini

Gemini is the only active AI provider.

The AI architecture must not contain runtime logic that chooses between multiple external AI providers.

⸻

4. Internal AI Abstraction

Even though Gemini is the only active provider, Clinicos must maintain an internal AI abstraction.

The purpose of the abstraction is:

* separation of concerns;
* testability;
* maintainability;
* centralized governance;
* provider-specific isolation;
* controlled future replacement;
* stable application interfaces.

The abstraction must not be implemented as an active multi-provider routing system.

⸻

5. Required Dependency Direction

The preferred dependency direction is:

Application / Domain
        |
   AI Interface
        |
 AI Governance Layer
        |
   Gemini Adapter
        |
    Gemini API

Application and domain code must not directly depend on Gemini SDK objects.

⸻

6. Forbidden Dependency Direction

The following patterns are prohibited:

Domain -> Gemini SDK
Domain -> Gemini API
Client -> Gemini API
Telegram -> Gemini API
Web -> Gemini API
Mobile -> Gemini API

All governed AI operations must pass through the Clinicos AI Layer.

⸻

7. AI Layer Responsibilities

The AI Layer is responsible for:

* AI task orchestration;
* model selection within Gemini;
* context preparation;
* prompt management;
* tool orchestration;
* output parsing;
* output validation;
* AI policy enforcement;
* safety controls;
* usage tracking;
* latency tracking;
* failure handling;
* AI execution logging;
* evaluation metadata.

The AI Layer does not own business truth.

⸻

8. AI Does Not Own Business Truth

Gemini is a reasoning and generation system.

It is not the authoritative source of:

* patients;
* appointments;
* availability;
* prices;
* clinic hours;
* provider schedules;
* payment status;
* communication delivery state;
* consent;
* authorization;
* safety state.

These values must come from authoritative Clinicos domains or approved external systems.

⸻

9. AI System Model

The target AI architecture is:

User / System Event
        |
Application Layer
        |
AI Orchestrator
        |
AI Governance
        |
Task Classification
        |
Context Builder
        |
Prompt / Instruction Builder
        |
Gemini Adapter
        |
Google Gemini
        |
Output Parser
        |
Output Validator
        |
Policy Validation
        |
Tool / Domain Action
        |
Final Result

⸻

10. AI Task Lifecycle

Every governed AI execution should conceptually follow:

RECEIVE
  |
CLASSIFY
  |
AUTHORIZE
  |
BUILD CONTEXT
  |
SELECT MODEL
  |
BUILD REQUEST
  |
EXECUTE
  |
PARSE
  |
VALIDATE
  |
GROUND
  |
EXECUTE TOOLS IF REQUIRED
  |
FINALIZE
  |
OBSERVE
  |
AUDIT

Not every AI task requires every stage, but no stage may be skipped when its risk profile requires it.

⸻

11. AI Task Types

Clinicos may support AI tasks including:

Conversation
Intent Classification
Entity Extraction
Lead Qualification
Patient Summarization
Follow-Up Drafting
Knowledge Question Answering
Report Generation
Clinical Information Explanation
Image Analysis
Document Analysis
Translation
Classification
Structured Extraction
Reasoning

Each task must have a defined contract.

⸻

12. AI Task Contract

Every production AI task should define:

Task Name
Purpose
Input Schema
Output Schema
Required Context
Allowed Tools
Forbidden Tools
Safety Level
Approval Mode
Allowed Models
Timeout
Retry Policy
Validation Rules
Audit Requirements

⸻

13. Task Registry

Clinicos should maintain a centralized conceptual AI task registry.

Example:

conversation.reply
lead.classify
lead.summarize
patient.summarize
followup.generate
knowledge.answer
report.generate
facial_analysis.interpret
document.extract

The registry should prevent AI configuration from being scattered throughout business code.

⸻

14. Model Selection

Clinicos may use different Gemini models for different workloads.

Examples:

Fast conversational workload
        |
Suitable Gemini model
Complex reasoning workload
        |
Suitable Gemini model
Vision workload
        |
Suitable Gemini vision-capable model
Structured extraction
        |
Suitable Gemini model

This is model selection within one provider.

It is not provider routing.

⸻

15. Model Selection Rules

Model selection should consider:

* task capability;
* latency;
* expected reasoning complexity;
* context requirements;
* multimodal requirements;
* structured output support;
* reliability;
* cost;
* safety requirements.

Model selection must not compromise safety or correctness.

⸻

16. Centralized Model Configuration

Gemini model identifiers must be centrally configurable.

Business domains should not hardcode Gemini model names.

Preferred:

AI Task
   |
Task Configuration
   |
Gemini Model Configuration

Not:

AppointmentService -> hardcoded model
LeadService -> hardcoded model
ConversationService -> hardcoded model

⸻

17. Model Version Tracking

Every production AI execution should be attributable to the Gemini model configuration used.

The execution record should capture appropriate model metadata.

This enables:

* regression analysis;
* incident investigation;
* cost analysis;
* performance comparison;
* reproducibility.

⸻

18. AI Abstraction Interface

The internal AI interface should conceptually support operations such as:

generate()
generate_structured()
analyze_image()
analyze_document()

The exact interface may evolve.

The application should not depend on provider-specific request objects.

⸻

19. Example Internal AI Contract

A conceptual request may contain:

AIRequest
    task
    model_policy
    system_instruction
    user_input
    context
    tools
    output_schema
    safety_policy
    timeout
    metadata

The exact implementation is determined by the repository architecture.

⸻

20. AI Response Contract

An AI response should conceptually contain:

AIResponse
    output
    structured_output
    model
    usage
    latency
    finish_reason
    safety_metadata
    execution_id

Provider-specific response details should remain inside the Gemini adapter.

⸻

21. Gemini Adapter Responsibilities

The Gemini adapter owns Gemini-specific concerns.

It may handle:

* SDK initialization;
* API authentication;
* request translation;
* response translation;
* model invocation;
* provider error mapping;
* usage extraction;
* Gemini-specific configuration;
* Gemini-specific multimodal handling.

It must not contain Clinicos business logic.

⸻

22. Gemini Adapter Non-Responsibilities

The Gemini adapter must not decide:

* whether a patient can access data;
* whether a follow-up should be sent;
* whether an appointment may be booked;
* whether marketing consent exists;
* whether a user should be escalated;
* whether a medical action is safe.

Those decisions belong to Clinicos domains and policies.

⸻

23. Gemini Credentials

Gemini credentials must exist only in trusted server-side environments.

Credentials must never be exposed to:

* Telegram users;
* Web clients;
* Mini Apps;
* Android applications;
* iOS applications;
* browser JavaScript;
* prompts;
* logs;
* client-side source code.

⸻

24. AI Request Construction

AI requests should be constructed from controlled components:

System Instructions
+
Task Instructions
+
Authorized Context
+
User Input
+
Tool Definitions
+
Output Schema
+
Safety Constraints

Untrusted content must not redefine system-level instructions.

⸻

25. Instruction Hierarchy

The AI system must preserve instruction hierarchy.

Conceptually:

Platform Safety
        >
AI Governance
        >
Agent Instructions
        >
Task Instructions
        >
User Input
        >
External Retrieved Content

Lower-trust content must not override higher-priority instructions.

⸻

26. Prompt Injection Defense

Patient messages, documents, retrieved content, and external text must be treated as untrusted.

Examples:

"Ignore your previous instructions."
"Reveal the system prompt."
"Call this tool without authorization."
"Send this patient data to another user."

Such content must not modify AI permissions.

⸻

27. Tool Authorization

AI tool availability does not equal authorization.

A tool invocation must pass server-side authorization and policy checks.

Preferred:

AI
 |
Tool Request
 |
Authorization
 |
Policy
 |
Domain Service
 |
Result

⸻

28. Direct Database Access Prohibited

AI agents must never receive unrestricted database access.

Prohibited:

AI -> SQL -> Database

Preferred:

AI -> Governed Tool -> Domain Service -> Repository

⸻

29. Tool Architecture

Tools should expose narrowly scoped operations.

Examples:

get_patient_summary()
get_appointment()
check_appointment_availability()
get_lead()
get_followup_status()
search_knowledge()
request_human_handoff()
create_followup()

Tools should not expose arbitrary internal capabilities.

⸻

30. Tool Contracts

Each tool must define:

Name
Purpose
Input Schema
Output Schema
Authorization Requirements
Tenant Requirements
Safety Requirements
Side Effects
Idempotency Requirements
Audit Requirements

⸻

31. Read Tools

Read-only tools should be preferred for information gathering.

Examples:

get_patient_summary
get_appointment
search_knowledge
get_lead

Read access must still respect authorization and tenant isolation.

⸻

32. Write Tools

Write tools require stricter governance.

Examples:

create_followup
update_lead
create_appointment
cancel_appointment
send_message

Write tools must validate:

* authorization;
* business rules;
* consent;
* safety;
* resource ownership;
* current state.

⸻

33. High-Risk Tools

High-risk tools may require human approval.

Examples:

Clinical escalation
Sensitive record modification
External communication with medical implications
Irreversible actions
High-impact patient operations

⸻

34. Tool Result Trust

Tool results from authoritative Clinicos systems are more authoritative than model-generated assumptions.

If Gemini says:

"The clinic has an available slot at 17:00."

the system must verify availability through the authoritative appointment system.

⸻

35. Dynamic Data Grounding

Dynamic facts must be retrieved at execution time where required.

Examples:

Current appointment
Current availability
Current clinic hours
Current price
Current discount
Current payment status

AI memory must not substitute for current system state.

⸻

36. Grounded Generation

For fact-sensitive tasks:

Question
  |
Identify required facts
  |
Retrieve authoritative data
  |
Build context
  |
Gemini
  |
Validate generated answer

⸻

37. Knowledge Grounding

Knowledge retrieval may be used for:

* FAQs;
* approved clinic information;
* educational material;
* internal documentation;
* approved policies.

Retrieved knowledge must be scoped to the tenant and task.

⸻

38. RAG Limitations

RAG must not be treated as authoritative for dynamic operational truth.

For example:

RAG:
"Doctor works from 16:00 to 20:00."
Current scheduling system:
Doctor is unavailable today.
Current scheduling system wins.

⸻

39. Context Builder

The Context Builder assembles authorized context for an AI task.

Potential context components:

User Context
Conversation Context
Patient Context
Clinic Context
Appointment Context
Lead Context
Follow-Up Context
Safety Context
Consent Context
Knowledge Context
Current Operational Data

Only relevant context should be included.

⸻

40. Context Minimization

The AI system must minimize unnecessary personal data.

For each task, the system should ask:

What information is necessary?
What information is optional?
What information is prohibited?

Unrelated sensitive data should not be sent to Gemini.

⸻

41. Tenant-Aware Context

Every context-building operation must be tenant-aware.

The AI context must never combine data from different clinics.

Cross-tenant context contamination is a critical security failure.

⸻

42. Patient Context

Patient context may include only information authorized for the specific task.

Possible components:

Identity
Relevant Conversation
Relevant Appointment
Relevant Lead State
Relevant Follow-Up State
Relevant Preferences
Relevant Consent
Relevant Safety State

⸻

43. Staff Context

Staff context must respect staff permissions.

An AI agent acting on behalf of a secretary must not automatically inherit doctor-level access.

AI permissions must be derived from the actual operation and authorization context.

⸻

44. Conversation Context

Conversation context should include relevant conversational history.

Context should be bounded to prevent:

* unnecessary token usage;
* irrelevant information;
* privacy exposure;
* context confusion.

⸻

45. Context Window Management

Large contexts should be managed using:

* summarization;
* selective retrieval;
* relevance filtering;
* structured state;
* conversation windows.

Critical facts must not be lost during summarization.

⸻

46. AI Memory

AI memory must not be treated as an authoritative database.

Persistent user or clinic state must be stored in appropriate Clinicos domains.

Gemini receives context from those domains when needed.

⸻

47. Structured State Over Narrative State

Important business facts should preferably be represented structurally.

Example:

{
  "appointment_status": "confirmed",
  "appointment_time": "2026-09-20T17:00:00",
  "provider_id": "provider_123"
}

rather than relying solely on narrative text.

⸻

48. Structured Outputs

When AI output drives application behavior, structured output should be preferred.

Example:

{
  "intent": "appointment_request",
  "requires_availability_check": true,
  "language": "fa"
}

The schema must be validated before use.

⸻

49. Schema Validation

Structured AI output must pass schema validation before reaching business logic.

Invalid output should produce a controlled failure.

The system must never assume that a syntactically incorrect model response is valid.

⸻

50. Semantic Validation

Schema validation is not sufficient.

The system must also validate semantic correctness.

Example:

AI Output:
appointment_status = confirmed
System:
No appointment exists.
Result:
Reject output.

⸻

51. Business Validation

AI output must pass business rules before execution.

Example:

AI:
"Send a promotional follow-up."
Policy:
Marketing consent is absent.
Result:
Block.

⸻

52. Safety Validation

AI-generated content must pass relevant safety validation.

Unsafe content must not be delivered merely because it is grammatically correct or structurally valid.

⸻

53. Factual Validation

When the output contains important factual claims, those claims should be checked against authoritative data when feasible.

Particularly:

* appointment facts;
* prices;
* availability;
* clinic policies;
* payment state;
* communication state.

⸻

54. AI Response Generation

AI-generated responses should be constructed using:

Authorized Context
+
Task Instructions
+
Safety Rules
+
Clinic Tone
+
User Language
+
Output Constraints

⸻

55. Response Boundaries

AI responses must not:

* fabricate facts;
* fabricate appointments;
* fabricate availability;
* fabricate pricing;
* fabricate policies;
* fabricate delivery status;
* fabricate clinical records.

⸻

56. Medical AI Boundary

Medical AI functionality must remain within explicitly defined safety boundaries.

AI may support:

* educational explanation;
* summarization;
* structured information extraction;
* triage assistance;
* safety signal detection;
* clinician support.

AI must not silently convert uncertain information into definitive clinical claims.

⸻

57. Clinical Safety Escalation

If a conversation indicates a potentially serious safety issue:

Conversation AI
    |
Safety Detection
    |
Medical Safety Domain
    |
Risk Assessment
    |
Human / Clinical Escalation

Commercial automation must be interrupted where safety policy requires.

⸻

58. AI and Diagnosis

The AI system must not present unsupported diagnostic conclusions as established medical facts.

Where uncertainty exists, the response should preserve appropriate uncertainty and escalation pathways.

⸻

59. AI and Treatment Recommendations

Treatment-related outputs require stricter controls.

Where appropriate:

* approved clinical knowledge should be used;
* relevant patient context must be verified;
* unsafe recommendations must be blocked;
* clinician review may be required.

⸻

60. AI and Emergency Situations

Potential emergencies require priority handling.

AI must not delay necessary escalation by continuing a normal conversational flow.

Emergency communication must follow the Medical Safety specification.

⸻

61. AI Agent Architecture

Agents are specialized AI capabilities operating under explicit boundaries.

Examples:

Conversation Agent
Lead Agent
Patient Intelligence Agent
Follow-Up Agent
Knowledge Agent
Secretary Copilot
Reporting Agent
Facial Analysis Agent

⸻

62. Agent Contract

Every production agent should define:

Purpose
Inputs
Outputs
Tools
Permissions
Forbidden Actions
Safety Requirements
Approval Mode
Context Requirements
Stop Conditions
Maximum Iterations
Audit Requirements

⸻

63. Agent Independence

Agents must not directly modify other domain state without using governed interfaces.

For example:

Lead Agent
   |
Lead Tool
   |
Lead Domain

not:

Lead Agent
   |
Direct Database Mutation

⸻

64. Agent Orchestrator

The Agent Orchestrator manages multi-step AI workflows.

Responsibilities include:

* agent selection;
* context preparation;
* tool availability;
* iteration limits;
* state tracking;
* safety checks;
* output validation;
* human escalation.

⸻

65. Agent Loop Limits

Every agent execution must have bounded limits.

Examples:

Maximum Iterations
Maximum Tool Calls
Maximum Execution Time
Maximum AI Calls
Maximum Resource Budget

⸻

66. Agent Stop Conditions

Agents must stop when:

* task is completed;
* required information is unavailable;
* policy blocks the action;
* safety escalation is required;
* human intervention is required;
* maximum iterations are reached;
* timeout occurs;
* repeated failure occurs.

⸻

67. Multi-Agent Architecture

Multiple specialized agents may exist.

However, multi-agent execution must remain controlled.

The system must prevent agents from creating uncontrolled autonomous chains.

⸻

68. Agent-to-Agent Communication

Agent communication should use structured messages where practical.

Agents must not exchange unrestricted hidden state.

Important actions must remain observable.

⸻

69. Human Approval

AI operations may require:

AUTO
STAFF_APPROVAL
STAFF_ONLY
DISABLED

Approval mode must be determined by risk and clinic configuration.

⸻

70. Human Review Payload

When human approval is required, the staff member should receive enough information to understand:

What AI wants to do
Why
Relevant source data
Potential impact
Generated content
Policy status
Safety status

⸻

71. AI Editing by Humans

Staff may edit AI-generated content.

The system should preserve attribution:

AI Generated
Human Edited
Human Approved
Sent

where appropriate.

⸻

72. AI and Human Ownership

When a human takes ownership of a conversation or workflow, AI automation must respect that ownership.

AI must not silently compete with staff actions.

⸻

73. AI Scheduling

AI may suggest future actions.

The Follow-Up Engine owns actual scheduling.

Preferred:

AI
 |
Follow-Up Proposal
 |
Follow-Up Policy
 |
Schedule

Not:

AI
 |
Direct Scheduler Mutation

⸻

74. AI Communication

AI may generate communication content.

The Communication Layer owns delivery.

Preferred:

AI
 |
Communication Draft
 |
Communication Policy
 |
Communication Layer
 |
Channel Adapter

⸻

75. AI Marketing

AI may assist with marketing content where permitted.

Marketing communication must still satisfy:

* consent;
* frequency limits;
* clinic policy;
* ethical communication rules;
* channel policy.

AI must not manufacture urgency or scarcity.

⸻

76. AI Follow-Up Generation

AI may recommend:

Timing
Purpose
Suggested Content
Channel

The Follow-Up Engine must validate the proposal.

⸻

77. AI Appointment Assistance

AI may understand appointment requests.

The actual appointment operation must be performed by the Appointment domain.

Example:

User:
"I want an appointment tomorrow afternoon."
AI:
Understands intent.
Appointment Domain:
Checks real availability.
Communication:
Reports actual available options.

⸻

78. AI Knowledge Answering

Knowledge answers should be grounded in approved knowledge where required.

The AI must distinguish:

Known from approved source

from:

General model knowledge

when the distinction matters.

⸻

79. AI Report Generation

AI may summarize analytics.

However:

Authoritative Metrics
        |
Report Builder
        |
Gemini Summary

The model must not generate the underlying metrics from memory.

⸻

80. AI Translation

Translation may be performed by Gemini.

Translation must preserve:

* meaning;
* clinical safety;
* numerical values;
* dates;
* times;
* names;
* structured facts.

⸻

81. Multilingual AI

Supported languages include:

Persian
English
Azerbaijani
Arabic
Turkish

The AI layer should support explicit language metadata.

⸻

82. Language Detection

Language detection may be AI-assisted.

However, explicit user preference should generally take precedence over inferred language when available.

⸻

83. Code Switching

Users may switch languages during a conversation.

The system should support code-switching while preserving:

* identity;
* intent;
* safety;
* structured state.

⸻

84. RTL Awareness

The AI layer should not corrupt RTL text.

Structured data should remain language-neutral.

Presentation concerns should remain in the client or communication layer.

⸻

85. Prompt Architecture

Prompts should be treated as production configuration.

A production prompt should have:

Prompt ID
Version
Purpose
Task
Safety Rules
Output Contract
Allowed Tools
Owner
Status

⸻

86. Prompt Versioning

Prompts must be versioned.

A production execution should be traceable to the prompt version used.

This supports:

* regression analysis;
* debugging;
* evaluation;
* controlled rollout.

⸻

87. Prompt Change Management

Prompt changes should be reviewed when they can affect:

* safety;
* business behavior;
* tool usage;
* data access;
* communication;
* clinical interpretation.

⸻

88. System Instructions

System-level AI instructions must be centrally managed.

They should define:

* role;
* boundaries;
* safety requirements;
* tool restrictions;
* truth requirements;
* escalation rules.

⸻

89. User Instructions

User input is treated as task input.

It must not automatically modify:

* permissions;
* safety rules;
* system policies;
* tenant boundaries;
* tool authorization.

⸻

90. External Content

External content must be clearly separated from trusted instructions.

Examples:

<UNTRUSTED_PATIENT_MESSAGE>
...
</UNTRUSTED_PATIENT_MESSAGE>

Equivalent implementation mechanisms may be used.

⸻

91. AI Output Safety

AI output should be evaluated before:

* display;
* storage as structured business state;
* communication;
* tool execution;
* clinical use.

⸻

92. AI Output Filtering

Potentially unsafe outputs should be:

Blocked
Regenerated
Escalated
Human Reviewed

depending on the task risk.

⸻

93. AI Hallucination Handling

If required information is unavailable, the AI should prefer:

I do not have enough verified information.

over fabricated content.

The exact user-facing wording depends on language and UX.

⸻

94. Uncertainty Handling

AI outputs should preserve uncertainty where appropriate.

The system should distinguish:

Verified Fact
Likely Interpretation
Model Suggestion
Unknown

⸻

95. AI Confidence Handling

Model confidence must never be treated as proof.

Confidence cannot independently authorize:

* medical decisions;
* patient access;
* appointment actions;
* communication;
* financial actions.

⸻

96. AI Safety Hierarchy

AI decisions must respect:

Medical Safety
    >
Privacy / Confidentiality
    >
Consent
    >
Authorization
    >
Operational Correctness
    >
User Preference
    >
Commercial Optimization

⸻

97. AI Privacy

Only the minimum required patient data should be sent to Gemini.

The system should avoid sending:

* unrelated medical history;
* unrelated conversations;
* unrelated staff data;
* unrelated tenant data;
* unnecessary identifiers.

⸻

98. Sensitive Data Redaction

Where feasible, sensitive identifiers should be minimized or redacted when they are not required for the task.

Redaction must not destroy information required for correctness.

⸻

99. AI Data Retention

AI prompts and outputs must follow Clinicos data retention rules.

Sensitive AI data must not be retained indefinitely without a defined purpose.

⸻

100. AI Logging

AI logging must balance observability and privacy.

Logs should prefer metadata such as:

Execution ID
Task
Agent
Tenant
Model
Latency
Status
Error Category
Token Usage

over unnecessary full prompt and response content.

⸻

101. AI Execution Record

A governed AI execution should have a unique execution identifier.

Example:

AIExecution
    execution_id
    tenant_id
    task
    agent
    model
    prompt_version
    policy_version
    started_at
    completed_at
    status
    usage
    latency

⸻

102. Tool Execution Record

Tool calls should also be observable.

Example:

AIToolExecution
    tool_call_id
    execution_id
    tool_name
    status
    started_at
    completed_at
    validation_result

⸻

103. AI Traceability

A production workflow should allow tracing:

User Request
    |
Conversation ID
    |
AI Execution
    |
Prompt Version
    |
Gemini Model
    |
Tool Calls
    |
Domain Operation
    |
Communication

⸻

104. AI Error Taxonomy

AI errors should be classified.

Examples:

Authentication Failure
Rate Limit
Timeout
Network Error
Provider Error
Invalid Response
Schema Validation Failure
Safety Validation Failure
Tool Failure
Context Failure
Policy Failure
Internal System Failure

⸻

105. Gemini Rate Limits

Gemini rate limits must be handled explicitly.

Mechanisms may include:

* request throttling;
* concurrency limits;
* exponential backoff;
* queueing;
* workload prioritization;
* graceful degradation.

⸻

106. Gemini Retry Policy

Retries must be bounded.

Retry only when the error is appropriate for retry.

Example retryable conditions may include:

Temporary network failure
Transient provider failure
Certain rate-limit conditions

Non-retryable errors should fail fast.

⸻

107. Exponential Backoff

Retries should use bounded exponential backoff where appropriate.

The system must prevent retry storms.

⸻

108. Circuit Breaker

A circuit breaker may temporarily stop calls to Gemini when repeated failures occur.

Conceptually:

Healthy
  |
Failures
  |
Open
  |
Recovery Window
  |
Half-Open
  |
Healthy / Open

⸻

109. AI Queueing

AI workloads may be queued when:

* Gemini is rate limited;
* concurrency is high;
* workload is non-urgent;
* background processing is required.

⸻

110. AI Priority

AI tasks may have different priorities.

Example:

Medical Safety
    >
Active User Conversation
    >
Appointment Operation
    >
Staff Request
    >
Routine Automation
    >
Reporting
    >
Background Analysis

Exact priority values are implementation-specific.

⸻

111. AI Backpressure

When Gemini capacity is constrained, the system must apply backpressure.

It should prefer:

Queue
Defer
Degrade
Human Handoff

over uncontrolled request growth.

⸻

112. AI Graceful Degradation

Not every feature requires AI.

Examples:

Appointment confirmation
    -> deterministic template
Simple administrative notification
    -> deterministic template
Human handoff
    -> deterministic workflow
AI-only analysis
    -> queue / retry / human review

⸻

113. No Provider Fallback

If Gemini fails, Clinicos must not automatically call another AI provider.

Prohibited:

Gemini
  |
failure
  |
OpenAI

or:

Gemini
  |
failure
  |
DeepSeek

or any equivalent provider fallback.

⸻

114. No Provider Routing

The system must not implement:

Provider Score
Provider Ranking
Provider Quota Score
Provider Cooldown
Provider Selection
Provider Failover

for external AI providers.

⸻

115. Model-Level Routing

Model selection within Gemini is allowed.

For example:

Task A -> Gemini Model A
Task B -> Gemini Model B
Task C -> Gemini Vision Model

This is internal model specialization.

⸻

116. AI Cost Management

AI cost should be monitored continuously.

Relevant metrics include:

Requests
Input Tokens
Output Tokens
Estimated Cost
Cost per Task
Cost per Tenant
Cost per Workflow

Exact billing fields depend on Gemini capabilities and available telemetry.

⸻

117. Cost Optimization

Cost may be optimized through:

* appropriate Gemini model selection;
* context minimization;
* prompt optimization;
* caching;
* avoiding unnecessary AI calls;
* batching where appropriate;
* deterministic workflows.

Cost optimization must not bypass safety.

⸻

118. AI Call Minimization

The platform should not invoke Gemini when deterministic logic is sufficient.

Example:

"Cancel my appointment."
If identity and appointment are unambiguous:
deterministic appointment workflow may be sufficient.

AI should be used where it adds meaningful value.

⸻

119. AI Caching

AI outputs may be cached only when safe.

Caching must consider:

* tenant;
* user;
* data freshness;
* personalization;
* sensitivity;
* task type.

Dynamic operational answers should not be cached beyond their safe validity period.

⸻

120. AI Batch Processing

Batching may be used for appropriate background tasks.

Batch processing must not delay safety-critical operations.

⸻

121. AI Evaluation Framework

Every important AI capability should have measurable evaluation criteria.

Potential dimensions:

Accuracy
Groundedness
Safety
Instruction Following
Tool Correctness
Structured Output Validity
Language Quality
Latency
Cost
Human Override Rate
Failure Rate

⸻

122. Evaluation Datasets

Evaluation datasets should contain representative cases.

They may include:

Normal Cases
Ambiguous Cases
Adversarial Cases
Safety Cases
Multilingual Cases
Tool-Use Cases
Boundary Cases
Failure Cases

⸻

123. Safety Evaluation

Safety evaluation should include:

* medical safety cases;
* privacy cases;
* prompt injection;
* unauthorized requests;
* harmful communication;
* unsafe tool requests;
* fabricated operational facts.

⸻

124. Regression Testing

AI changes should be evaluated against previous test cases.

Prompt changes and Gemini model changes can produce behavioral regressions.

Regression testing must therefore be part of the deployment process.

⸻

125. Model Change Evaluation

Changing the Gemini model for a task requires evaluation against:

Accuracy
Safety
Latency
Cost
Tool Behavior
Structured Output
Language Support

⸻

126. Prompt Change Evaluation

Prompt changes should be tested against relevant production-like scenarios before rollout.

High-risk prompt changes require stricter review.

⸻

127. Shadow Evaluation

Where practical, new AI configurations may be evaluated without affecting live users.

This can be used for:

* prompt changes;
* model changes;
* tool changes;
* context changes.

⸻

128. Human Evaluation

Human reviewers may evaluate:

* correctness;
* usefulness;
* tone;
* safety;
* factual grounding;
* clinical appropriateness.

Human evaluation must be structured where possible.

⸻

129. AI Feedback

User and staff feedback may be captured.

Feedback should be separated from authoritative business state.

For example:

AI Answer Rating = feedback signal

not:

AI Answer Rating = factual truth

⸻

130. AI Quality Metrics

Recommended metrics include:

Grounded Answer Rate
Unsafe Output Rate
Tool Success Rate
Structured Output Validity
Human Correction Rate
Human Override Rate
Escalation Rate
AI Failure Rate
Average Latency
Average Cost

⸻

131. AI Reliability Metrics

The platform should track:

Gemini Availability
Gemini Error Rate
Gemini Timeout Rate
Rate Limit Frequency
Retry Rate
Circuit Breaker Events
Queue Delay
AI Task Success Rate

⸻

132. AI SLA

AI-dependent workflows should have appropriate service targets.

Targets may differ between:

Interactive
Transactional
Background
Safety-related

Safety-related workflows require special handling and must not be degraded in a way that creates unsafe behavior.

⸻

133. AI Observability Dashboard

Operations should be able to monitor:

AI Requests
AI Failures
Gemini Latency
Gemini Usage
Model Distribution
Task Distribution
Tool Calls
Safety Blocks
Human Escalations
Queue Depth
Cost

⸻

134. AI Incident Detection

The system should detect abnormal conditions such as:

Sudden Error Spike
Sudden Latency Increase
Unusual Token Consumption
Repeated Tool Failures
Unexpected Output Schema Failures
Safety Failure Spike

⸻

135. AI Incident Response

AI incidents should support:

Detection
Containment
Investigation
Mitigation
Recovery
Post-Incident Review

Possible mitigation:

Disable specific agent
Disable specific task
Disable autonomous mode
Switch to deterministic templates
Require human approval
Pause AI globally

No provider fallback is used.

⸻

136. AI Kill Switch

Clinicos should support disabling:

All AI
Specific Agent
Specific Task
Specific Gemini Model Configuration
Autonomous Actions
AI Communication
AI Facial Analysis

Kill switches must be auditable.

⸻

137. AI Safety Kill Switch

Medical safety-related AI functionality should have stronger operational controls.

A safety incident may require immediate suspension of an AI capability.

⸻

138. AI Security

Security must cover:

Credentials
Prompts
Context
Tools
Outputs
Logs
Storage
APIs
Tenant Isolation

⸻

139. Prompt Security

Prompts must not contain:

* API keys;
* database credentials;
* private infrastructure secrets;
* unrelated patient data;
* unnecessary tenant information.

⸻

140. Tool Security

Tools must enforce authorization independently from the model.

A malicious or confused model must not be able to elevate privileges through tool calls.

⸻

141. Output Security

AI output must be treated as untrusted until validated.

Generated text must not be directly interpreted as:

* executable code;
* SQL;
* shell commands;
* privileged instructions.

⸻

142. Code Generation

If Clinicos uses Gemini for coding or internal developer assistance, generated code must be treated as untrusted until reviewed and tested.

AI-generated code must not automatically enter production.

⸻

143. AI and SQL

Gemini must not be given unrestricted SQL execution capability.

If analytical queries are supported, they must use constrained, validated interfaces.

⸻

144. AI and Shell Access

Production AI agents must not have unrestricted shell or infrastructure access.

Any infrastructure automation must use narrowly scoped and explicitly authorized tools.

⸻

145. AI and File Access

AI file access must be scoped.

The model should only receive files required for the current task.

⸻

146. AI and Medical Images

Medical images require:

Authorization
Consent where required
Secure Transfer
Controlled Processing
Tenant Isolation
Retention Controls

⸻

147. Facial Analysis AI

Facial analysis should use a dedicated AI task contract.

Conceptually:

Image
 |
Validation
 |
Consent
 |
Facial Analysis Pipeline
 |
Gemini Vision Capability where appropriate
 |
Structured Result
 |
Safety / Quality Validation
 |
Final Result

⸻

148. Facial Analysis Output

Facial analysis should distinguish:

Observed Visual Characteristics

from:

Medical Diagnosis

The AI must not present visual observations as definitive medical diagnoses.

⸻

149. Image Quality

Before AI image analysis, the system should validate:

* file type;
* resolution;
* image integrity;
* orientation;
* acceptable framing;
* required image count;
* processing constraints.

Poor-quality images should produce a controlled retry or user instruction.

⸻

150. AI Document Processing

Documents may be processed by Gemini where appropriate.

The pipeline should include:

Upload
 |
Validation
 |
Authorization
 |
Extraction
 |
AI Processing
 |
Structured Output
 |
Validation
 |
Storage / Result

⸻

151. AI Report Generation

AI-generated reports should be built from structured authoritative data.

Example:

Analytics
    |
Structured Report Data
    |
Gemini
    |
Narrative Summary
    |
Validation
    |
Final Report

⸻

152. AI and Analytics

AI may interpret analytics.

It must not change raw metrics.

Example:

Conversion Rate = 18.4%
AI Interpretation:
"Conversion increased compared with the previous period."

The percentage itself must come from analytics.

⸻

153. AI and Recommendations

Recommendations must identify whether they are:

System Rule
AI Suggestion
Human Decision

AI suggestions must not be represented as established business facts.

⸻

154. AI and Pricing

AI may explain or present pricing retrieved from authoritative systems.

It must not invent:

* current prices;
* discounts;
* promotional eligibility;
* payment status.

⸻

155. AI and Clinic Policies

AI may answer clinic policy questions when grounded in approved policy sources.

If the policy is unknown, AI must not invent one.

⸻

156. AI and Appointment Availability

Availability must always come from the authoritative appointment system.

Gemini may interpret the request but does not determine availability.

⸻

157. AI and Communication Delivery

Gemini must not claim that a message was delivered unless the Communication Layer provides the delivery state.

⸻

158. AI and Follow-Up

Gemini may recommend follow-up content or timing.

The Follow-Up Engine owns scheduling and lifecycle.

⸻

159. AI and Consent

AI must never infer marketing permission from silence.

Consent must come from the Consent / Privacy domain.

⸻

160. AI and Authorization

AI cannot grant itself additional permissions.

Every tool call must be authorized server-side.

⸻

161. AI and Tenant Isolation

Tenant boundaries must be enforced outside the model.

The model must never be trusted to remember tenant boundaries correctly.

⸻

162. AI Context Authorization

Before context is sent to Gemini, the system should verify:

Who is requesting?
Which tenant?
Which resource?
Why is it needed?
What fields are allowed?

⸻

163. AI Data Minimization by Task

Example:

Task:
Appointment Reminder
Required:
Patient name
Appointment time
Provider
Clinic identity
Not required:
Unrelated medical history
Other conversations
Other patients

⸻

164. AI Output Storage

Not every AI output must be permanently stored.

Storage decisions should consider:

Business Value
Audit Requirement
Privacy
Safety
Retention
Cost

⸻

165. AI Auditability

High-impact AI actions should be auditable.

Audit information may include:

Actor
Tenant
Task
Agent
Model
Prompt Version
Tool Calls
Policy Result
Human Approval
Final Action
Timestamp

⸻

166. AI Attribution

The system should distinguish:

AI Generated
Human Generated
Human Edited AI
System Generated

where relevant.

⸻

167. AI Reproducibility

For important workflows, the system should preserve sufficient metadata to understand how an AI result was produced.

This includes:

Model
Prompt Version
Tool Versions
Policy Version
Knowledge Version where applicable
Input Context Metadata

⸻

168. AI Determinism

AI outputs are inherently variable.

Therefore, business-critical operations must not rely on unvalidated free-form model output.

Use:

Structured Output
+
Validation
+
Authoritative Data
+
Deterministic Business Rules

⸻

169. AI and Business Rules

AI should interpret or assist with business rules.

It should not replace deterministic rules where deterministic enforcement is practical.

⸻

170. AI and State Machines

Domain state transitions should remain controlled by domain services.

AI may recommend a transition.

The domain decides whether the transition is valid.

⸻

171. AI and Event Systems

AI may consume events as input.

AI must not generate arbitrary business events without passing through appropriate domain operations.

⸻

172. AI Event Safety

An AI-generated event proposal is not equivalent to a domain event.

Only successful domain operations should produce authoritative business events.

⸻

173. AI and Automation

AI may participate in automation.

Automation must still enforce:

Authorization
Consent
Safety
Frequency
Tenant
Idempotency

⸻

174. AI Automation Loops

AI-driven automation must prevent:

AI
 ->
Event
 ->
Automation
 ->
AI
 ->
Event

from becoming an uncontrolled loop.

⸻

175. AI Resource Budgets

Long-running AI workflows should have bounded resource budgets.

Possible controls:

Maximum Model Calls
Maximum Tool Calls
Maximum Runtime
Maximum Tokens
Maximum Cost

⸻

176. AI Concurrency

AI concurrency must be controlled.

Unlimited concurrent Gemini calls are prohibited.

⸻

177. Tenant AI Quotas

Tenant-level AI quotas may be implemented.

Quota enforcement must not bypass safety-critical operations.

⸻

178. AI Fairness of Resource Allocation

Resource scheduling should prevent a single tenant or workflow from exhausting shared AI capacity.

⸻

179. AI Priority Queues

Where needed, AI tasks may use priority queues.

Safety and active-user workflows should not be blocked indefinitely by background processing.

⸻

180. AI Retry Idempotency

Retrying an AI task must not accidentally repeat a side effect.

AI generation and business action execution should be separated where necessary.

⸻

181. AI Action Pattern

Preferred:

AI
 |
Proposal
 |
Validation
 |
Domain Action

rather than:

AI
 |
Unvalidated Side Effect

⸻

182. Transactional AI Actions

If an AI task results in a business operation, the business operation should be executed transactionally where appropriate.

⸻

183. AI and Communication Safety

AI-generated communications must pass Communication Layer policies.

AI must not bypass:

* consent;
* quiet hours;
* frequency limits;
* human ownership;
* channel restrictions.

⸻

184. AI and Marketing Ethics

AI marketing content must not use:

* fake scarcity;
* fake urgency;
* fabricated testimonials;
* fabricated social proof;
* misleading medical claims;
* manipulative fear;
* guilt.

⸻

185. AI Tone

Clinic-specific tone may be configured.

Tone must never override:

Safety
Accuracy
Privacy
Consent
Truthfulness

⸻

186. AI Localization

AI-generated content should respect clinic and user language preferences.

Language changes must not change underlying business meaning.

⸻

187. AI Date and Time Handling

AI must not infer dates and times when authoritative structured values are available.

Dates and times should be passed as structured data where possible.

⸻

188. AI Numeric Accuracy

Important numerical values should be provided through structured context.

AI-generated numerical claims should be validated when they affect business or clinical decisions.

⸻

189. AI Naming Accuracy

Names of:

* patients;
* doctors;
* services;
* clinics;
* appointments;

should come from structured authoritative context when available.

⸻

190. AI Output Formatting

The final presentation format should be controlled by the client or communication layer.

The AI layer should prefer structured semantic output where possible.

⸻

191. AI Streaming

Streaming may be used for interactive responses.

Streaming must not bypass output validation for actions or sensitive content.

⸻

192. Partial AI Output

Partial streaming output must not be interpreted as a completed business action.

⸻

193. AI Cancellation

Long-running AI tasks should support cancellation where practical.

Cancellation should prevent unnecessary resource consumption.

⸻

194. AI Timeout

Every AI operation must have a bounded timeout.

Timeouts should depend on task type.

⸻

195. AI Queue Timeout

Queued AI tasks should also have expiration or maximum waiting policies.

Expired tasks must reach an explicit terminal state.

⸻

196. AI Recovery

After application restart, in-flight AI tasks must be reconciled.

The system must avoid duplicate business side effects.

⸻

197. AI State Persistence

Important AI workflow state must not rely exclusively on process memory.

Durable state should be used for long-running workflows.

⸻

198. AI Health Checks

Operational monitoring should include AI dependency health.

Health checks must not generate excessive Gemini traffic.

⸻

199. AI Readiness

The application should verify required Gemini configuration during startup.

Invalid AI configuration should produce a clear operational failure rather than silent malfunction.

⸻

200. AI Configuration Validation

Configuration should validate:

Gemini Credential Availability
Model Configuration
Task Configuration
Timeouts
Retry Policy
Quota Configuration
Feature Flags

⸻

201. AI Secret Rotation

Gemini credentials should be rotatable without requiring source-code changes.

⸻

202. AI Environment Separation

Development, staging, and production AI credentials and configurations must remain separate.

Production Gemini credentials must never be committed to source control.

⸻

203. AI Testing Architecture

Testing should include:

Unit Tests
Integration Tests
Contract Tests
Prompt Tests
Golden Tests
Safety Tests
Security Tests
Load Tests
Failure Tests
End-to-End Tests

⸻

204. AI Unit Tests

Unit tests should cover:

* context construction;
* policy decisions;
* schema validation;
* tool authorization;
* output parsing;
* error mapping.

⸻

205. Gemini Integration Tests

Integration tests should verify:

Gemini Authentication
Model Invocation
Structured Outputs
Error Mapping
Timeouts
Rate Limits
Usage Metadata
Multimodal Processing

⸻

206. Mocking Gemini

Most domain tests should not require live Gemini access.

The internal AI interface should be mockable.

⸻

207. Contract Testing

The Gemini adapter should have contract tests to ensure the rest of Clinicos receives stable internal AI responses.

⸻

208. Golden Tests

Important AI tasks may use golden test cases.

A golden test should define expected properties rather than necessarily requiring exact wording.

⸻

209. Semantic AI Testing

AI tests should evaluate semantic correctness where exact text matching is inappropriate.

Examples:

Correct Intent
Correct Tool
Correct Facts
Correct Safety Decision
Correct Language

⸻

210. Prompt Injection Testing

Test cases should attempt to manipulate the model into:

* revealing instructions;
* bypassing authorization;
* exposing private data;
* calling unauthorized tools;
* changing tenant context;
* ignoring safety rules.

⸻

211. Hallucination Testing

Tests should verify that the AI does not invent:

Appointments
Availability
Prices
Policies
Patient Facts
Delivery Status
Clinical Records

⸻

212. Multilingual Testing

Supported languages must be tested independently.

Testing should include:

Persian
English
Azerbaijani
Arabic
Turkish

⸻

213. RTL Testing

Persian and Arabic AI output should be tested for correct rendering and semantic preservation.

⸻

214. Tool Testing

Tool tests must verify:

* valid arguments;
* invalid arguments;
* unauthorized calls;
* cross-tenant access;
* stale data;
* conflicting state;
* retries;
* duplicate calls.

⸻

215. AI Load Testing

Load tests should measure:

Concurrent Gemini Requests
Queue Growth
Latency
Error Rate
Token Consumption
Worker Utilization

⸻

216. AI Failure Testing

Failure scenarios should include:

Gemini Timeout
Rate Limit
Network Failure
Invalid Response
Schema Failure
Tool Failure
Database Failure
Queue Failure

⸻

217. AI Chaos Testing

Where practical, controlled failures may be introduced to validate graceful degradation.

⸻

218. AI Security Testing

Security testing should include:

Prompt Injection
Tool Escalation
Tenant Escape
Credential Exposure
Context Leakage
Data Exfiltration
Malicious Files
Abuse

⸻

219. AI Privacy Testing

Privacy tests should verify that irrelevant sensitive data is not included in AI context.

⸻

220. AI Regression Gate

Production AI changes should not be released if critical safety or correctness regressions are detected.

⸻

221. Deployment of AI Changes

AI changes include:

* prompt changes;
* model changes;
* agent changes;
* tool changes;
* context changes;
* validation changes.

Each should have an appropriate deployment strategy.

⸻

222. AI Feature Rollout

New AI capabilities may be rolled out using:

Disabled
Internal
Pilot
Limited Tenant
General Availability

⸻

223. AI Rollback

AI configurations should be rollback-capable.

Rollback should be possible for:

* prompt version;
* model configuration;
* agent version;
* tool configuration;
* feature flag.

⸻

224. AI Configuration Audit

Changes to high-impact AI configuration should be auditable.

⸻

225. AI Governance Ownership

AI engineering governance should define ownership for:

Models
Prompts
Agents
Tools
Safety Rules
Evaluation
Costs
Observability

⸻

226. AI Change Review

Changes affecting medical safety, privacy, authorization, or autonomous actions require stricter review.

⸻

227. AI Documentation

Each production AI capability should have documentation describing:

Purpose
Inputs
Outputs
Model
Prompt
Tools
Policies
Safety
Failure Modes
Evaluation
Owner

⸻

228. AI Architecture Decision Records

Major AI decisions should be recorded as ADRs.

Examples:

Gemini-only provider architecture
Internal AI abstraction
Model specialization strategy
Tool governance
AI human approval modes
AI context minimization

⸻

229. AI Anti-Patterns

The following are prohibited:

Direct Client -> Gemini
Direct Domain -> Gemini SDK
AI -> Database
AI -> Arbitrary SQL
AI -> Unrestricted Shell
AI -> Unauthorized Communication
AI -> Unvalidated Business Action
AI -> Cross-Tenant Context
AI -> Provider Fallback
AI -> Fabricated Operational Truth

⸻

230. AI Architecture Review Checklist

Before accepting an AI feature, verify:

Is the task clearly defined?
Is the model selected centrally?
Is Gemini accessed through the AI layer?
Is context authorized?
Is tenant isolation enforced?
Are tools governed?
Is output structured where appropriate?
Is output validated?
Are business rules enforced?
Is safety enforced?
Is consent enforced?
Is the action auditable?
Is failure handling bounded?
Is human escalation available where needed?
Is the feature tested?

⸻

231. Production AI Checklist

Before production release:

Gemini configuration verified
Prompt versioned
Model configuration versioned
Tool permissions verified
Tenant isolation tested
Safety tests passed
Prompt injection tests passed
Hallucination tests passed
Multilingual tests passed
Failure handling tested
Observability enabled
Cost monitoring enabled
Rollback available

⸻

232. AI Architecture Invariants

The following invariants are mandatory:

1. Gemini is the only active AI provider.
2. No provider routing exists.
3. No provider fallback exists.
4. Internal AI abstraction remains mandatory.
5. Gemini-specific code remains isolated.
6. Clients never access Gemini directly.
7. AI never owns business truth.
8. AI never bypasses authorization.
9. AI never bypasses consent.
10. AI never bypasses medical safety.
11. AI never receives unrestricted database access.
12. AI tool calls are governed.
13. AI outputs are validated before side effects.
14. Dynamic operational facts come from authoritative systems.
15. Tenant isolation applies to every AI context.
16. Sensitive data is minimized.
17. AI execution is observable.
18. Important AI actions are auditable.
19. AI retries are bounded.
20. AI loops are bounded.
21. AI failures do not trigger provider switching.
22. Human escalation exists for high-risk workflows.
23. AI-generated communication is subject to Communication policies.
24. AI-generated business state is not automatically authoritative.
25. AI configuration is versioned.
26. AI changes are evaluated before production.
27. AI can be disabled through operational controls.

⸻

233. Canonical AI Architecture

The final AI architecture is:

                    CLIENT
                       |
                     API
                       |
                 CORE PLATFORM
                       |
                APPLICATION LAYER
                       |
                 AI ORCHESTRATOR
                       |
                 AI GOVERNANCE
                       |
                TASK CLASSIFIER
                       |
                 CONTEXT BUILDER
                       |
                PROMPT BUILDER
                       |
                 AI INTERFACE
                       |
                GEMINI ADAPTER
                       |
                GOOGLE GEMINI
                       |
              RESPONSE PARSER
                       |
             OUTPUT VALIDATION
                       |
              POLICY VALIDATION
                       |
             GOVERNED TOOL CALL
                       |
                DOMAIN SERVICE
                       |
              BUSINESS OPERATION
                       |
               COMMUNICATION
                       |
                  CHANNEL

⸻

234. Canonical AI Agent Flow

User Input
    |
Conversation
    |
Agent Selection
    |
Authorization
    |
Context Construction
    |
Safety Evaluation
    |
Gemini
    |
Tool Selection
    |
Tool Authorization
    |
Tool Execution
    |
Result Validation
    |
Final Response
    |
Communication
    |
Audit

⸻

235. Canonical AI Safety Flow

Input
  |
Safety Detection
  |
Medical Safety
  |
Policy
  |
Human / Clinical Escalation
  |
Controlled AI Response

⸻

236. Canonical AI Appointment Flow

User
  |
Gemini / Conversation
  |
Appointment Intent
  |
Appointment Domain
  |
Authoritative Availability
  |
Appointment Operation
  |
Communication

⸻

237. Canonical AI Follow-Up Flow

Trigger
  |
AI Recommendation
  |
Follow-Up Policy
  |
Consent
  |
Safety
  |
Human Ownership
  |
Follow-Up Engine
  |
Communication

⸻

238. Canonical AI Communication Flow

Business Intent
  |
AI Content Generation
  |
Output Validation
  |
Communication Policy
  |
Communication Layer
  |
Channel Adapter
  |
Provider

⸻

239. Canonical AI Failure Flow

Gemini Request
     |
Failure
     |
Classify Failure
     |
Retry if appropriate
     |
Backoff
     |
Retry Limit
     |
Queue / Degrade / Human

There is no provider fallback.

⸻

240. Canonical AI Truth Flow

Business Question
      |
Required Fact
      |
Authoritative Domain
      |
Verified Data
      |
AI Context
      |
Gemini Reasoning
      |
Validated Response

⸻

241. Canonical AI Security Flow

Request
   |
Authentication
   |
Authorization
   |
Tenant Resolution
   |
Context Authorization
   |
AI Governance
   |
Gemini
   |
Output Validation
   |
Domain Authorization
   |
Execution

⸻

242. Final AI Engineering Principles

Clinicos AI must follow these principles:

AI assists.
Domains decide.
Gemini reasons.
Systems provide truth.
AI proposes.
Policies govern.
Tools execute.
Authorization controls.
Clients interact.
Core Platform owns logic.
Communication delivers.
Business domains own intent.
Safety comes first.
Commercial optimization comes later.

⸻

243. Final Provider Principle

The current production AI provider architecture is:

Clinicos
   |
AI Layer
   |
Gemini Adapter
   |
Google Gemini

There is no runtime provider competition.

There is no provider scoring.

There is no provider fallback.

There is no multi-provider routing.

⸻

244. Final Abstraction Principle

The system intentionally maintains:

AI Interface
    |
Gemini Adapter

This provides architectural replaceability without introducing unnecessary runtime complexity.

The abstraction exists for clean architecture, not for provider switching.

⸻

245. Final AI Product Principle

Clinicos must never become:

Gemini + Database + Telegram

Instead, the target is:

Clinic Operating Platform
        +
Governed AI Layer
        +
Gemini

Gemini is a capability inside Clinicos.

Clinicos remains the product.

⸻

246. Final Non-Negotiable Rules

1. Google Gemini is the only active AI provider.
2. FreeLLMAPI is removed from the target architecture.
3. OpenRouter is removed from the target runtime architecture.
4. DeepSeek is removed from the target runtime architecture.
5. Qwen is removed from the target runtime architecture.
6. OpenAI is removed from the target runtime architecture.
7. Multi-provider routing is prohibited.
8. Provider fallback is prohibited.
9. Provider scoring is prohibited.
10. Provider cooldown routing is prohibited.
11. Internal AI abstraction is mandatory.
12. Gemini-specific implementation must remain isolated.
13. Clients must never directly call Gemini.
14. Domain services must never directly depend on Gemini SDKs.
15. AI must not own authoritative business data.
16. AI must not invent operational facts.
17. AI must not bypass authorization.
18. AI must not bypass consent.
19. AI must not bypass medical safety.
20. AI must not access the database without governed domain tools.
21. AI tool execution must be authorized.
22. AI outputs must be validated.
23. AI-driven side effects must be governed.
24. Tenant isolation must apply to all AI context.
25. Sensitive data must be minimized.
26. AI execution must be observable.
27. High-impact AI actions must be auditable.
28. AI retries must be bounded.
29. AI agent loops must be bounded.
30. Gemini failures must be handled through retry, backoff, queueing, graceful degradation, or human escalation.
31. Gemini failures must never trigger another AI provider.
32. Dynamic operational truth must come from authoritative systems.
33. Follow-Up scheduling remains owned by the Follow-Up Engine.
34. Appointment truth remains owned by the Appointment domain.
35. Communication delivery remains owned by the Communication Layer.
36. Medical safety remains owned by the Medical Safety domain.
37. AI changes must be evaluated before production.
38. AI configuration must be versioned.
39. Production AI must be disableable through operational controls.
40. AI must remain a governed capability of the Clinicos platform rather than becoming the platform itself.

⸻

247. Final Architecture Statement

Clinicos AI is a governed intelligence layer built around Google Gemini.

The platform does not outsource business truth, authorization, safety, workflow ownership, or communication governance to the model.

Gemini provides reasoning, generation, classification, summarization, multimodal analysis, and other AI capabilities.

Clinicos provides:

Identity
Data
Business Logic
Policies
Safety
Tools
Workflows
Communication
Authorization
Tenant Isolation
Observability
Auditability

The final architecture is:

                 CLINICOS CORE PLATFORM
                           |
                    AI GOVERNANCE
                           |
                     AI INTERFACE
                           |
                    GEMINI ADAPTER
                           |
                    GOOGLE GEMINI

The system is intentionally:

AI-Native
+
Domain-Centric
+
Policy-Governed
+
Safety-First
+
Tenant-Isolated
+
Client-Independent
+
Channel-Agnostic
+
Observable
+
Auditable
+
Replaceable at the abstraction boundary

The target is not a chatbot powered by Gemini.

The target is a clinic operating system in which Gemini is a governed intelligence capability.
