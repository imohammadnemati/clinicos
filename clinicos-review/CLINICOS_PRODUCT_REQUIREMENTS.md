# CLINICOS PRODUCT REQUIREMENTS
**Document:** CLINICOS_PRODUCT_REQUIREMENTS.md  
**Version:** 2.0  
**Status:** Authoritative Product Requirements Specification  
**Effective:** Immediately  
**Language:** English  
**Parent Document:** CLINICOS_MASTER_VISION.md
---
# 1. Document Purpose
This document defines the product requirements for Clinicos.
It translates the Master Product Vision into concrete product capabilities, behaviors, workflows, roles, requirements, constraints, and acceptance criteria.
This document describes what Clinicos must provide as a product.
It does not prescribe every implementation detail.
Technical implementation must satisfy these requirements while remaining consistent with:
- `CLINICOS_MASTER_VISION.md`
- `CLINICOS_ARCHITECTURE_CHANGE_SET.md`
- `CLINICOS_TARGET_ARCHITECTURE.md`
- domain-specific specifications
- security and privacy requirements
- medical safety requirements
- platform governance requirements
---
# 2. Product Definition
Clinicos is an AI-native clinic operating platform.
The platform must unify:
- patient communication,
- patient identity,
- patient intelligence,
- conversations,
- lead management,
- follow-up,
- appointments,
- clinic knowledge,
- medical safety,
- AI assistance,
- facial analysis,
- notifications,
- automation,
- analytics,
- reporting,
- staff workflows,
- and clinic management.
Clinicos must be designed as a platform rather than a single-channel chatbot.
The first client is Telegram.
The product roadmap is:
```text
Phase 1
Telegram Bot
Phase 2
Telegram Bot
+
Telegram Mini App
Phase 3
Telegram Bot
+
Telegram Mini App
+
Web
+
Android
+
iOS

The Core Platform must remain independent of these clients.

⸻

3. Product Goals

Clinicos must achieve the following primary goals.

3.1 Unified Patient Interaction

Provide one coherent operational view of patient interactions.

3.2 Intelligent Communication

Use governed AI to understand and assist with patient communication.

3.3 Lead Capture and Conversion Support

Prevent leads from being lost and provide structured follow-up.

3.4 Operational Automation

Automate repetitive workflows while maintaining policy, consent, safety, and human control.

3.5 Staff Assistance

Reduce repetitive administrative work and improve staff visibility.

3.6 Patient Intelligence

Transform fragmented interactions into useful structured patient context.

3.7 Reliable Clinic Operations

Connect communication, appointments, follow-ups, and operational events.

3.8 Measurable Performance

Provide analytics and reporting for clinic operations.

3.9 Safe AI

Use AI within explicit safety, authorization, privacy, and operational boundaries.

3.10 Multi-Client Evolution

Allow the product to expand beyond Telegram without redesigning the core platform.

⸻

4. Product Principles

The following principles are mandatory.

4.1 Core Platform First

Business logic belongs in the Core Platform.

Clients are interfaces.

⸻

4.2 AI-Native

AI should be deeply integrated into workflows where it provides meaningful value.

⸻

4.3 Governed AI

AI must operate through explicit permissions, tools, policies, validation, and observability.

⸻

4.4 Gemini Only

Google Gemini is the only active AI provider.

FreeLLMAPI and other external AI providers are not part of the target runtime architecture.

⸻

4.5 No Multi-Provider Runtime Routing

Clinicos must not dynamically select between different AI providers.

Different Gemini models may be selected for different workloads.

This is model selection within one provider.

⸻

4.6 No AI Provider Fallback

Gemini failures must be handled through:

* retry,
* timeout,
* circuit breaker,
* queueing,
* graceful degradation,
* deterministic responses,
* or human handoff.

The platform must not silently switch to another AI provider.

⸻

4.7 Channel Agnostic

Business logic must not depend on Telegram.

Communication must be implemented through a channel abstraction.

⸻

4.8 Authoritative Operational Truth

AI must never invent live operational information.

⸻

4.9 Safety Before Commercial Optimization

Medical safety, privacy, consent, and authorization take priority over commercial objectives.

⸻

4.10 Human Control

Users and staff must be able to request or assume human handling when required.

⸻

5. Product Roles

Clinicos must support the following primary roles.

5.1 Patient

The patient interacts with the clinic and accesses permitted services.

5.2 Secretary / Staff

Staff manage daily clinic operations and patient communication.

5.3 Doctor

Doctors review relevant patient and clinical-operational information and handle appropriate escalations.

5.4 Owner / Manager

Owners and managers monitor and configure clinic operations.

5.5 System Administrator

Platform administrators manage system-level configuration and governance.

5.6 AI Agent

AI agents operate as controlled system actors with explicit permissions.

AI agents are not equivalent to human users.

⸻

6. Tenant Model

Clinicos must be multi-tenant.

Each clinic must be represented as an isolated tenant.

Tenant isolation must apply to:

* patients,
* staff,
* conversations,
* leads,
* appointments,
* knowledge,
* files,
* AI context,
* reports,
* analytics,
* notifications,
* configuration,
* audit logs,
* and integrations.

No user, AI agent, workflow, or integration may access another tenant’s data without explicit authorization.

⸻

7. Identity Requirements

PR-ID-001: Person Identity

The system must maintain a unified person identity.

PR-ID-002: Channel Identity

The system must support multiple identities associated with the same person.

Examples:

* Telegram identity
* Web identity
* Android identity
* iOS identity

PR-ID-003: Identity Resolution

The platform should support controlled identity resolution between channel identities.

Identity resolution must not rely solely on AI inference.

PR-ID-004: Identity Security

Identity operations must be authenticated and authorized.

PR-ID-005: Tenant Context

Every authenticated operation must have an explicit tenant context.

⸻

8. Authentication Requirements

Clinicos must provide secure authentication for supported users.

Authentication requirements include:

* secure credential handling,
* session management,
* token management,
* expiration,
* revocation,
* role-aware access,
* device/session visibility where appropriate,
* and auditability.

Client-specific authentication mechanisms may differ.

The underlying authorization model must remain centralized.

⸻

9. Authorization Requirements

Authorization must be enforced server-side.

Authorization must consider:

* actor,
* tenant,
* role,
* resource,
* action,
* workflow,
* and risk.

The client must never be treated as the final authorization authority.

⸻

10. Patient Management Requirements

Clinicos must provide a structured patient record.

The patient record should support:

* identity,
* contact information,
* language preference,
* communication preferences,
* channel identities,
* interaction history,
* lead status,
* appointment history,
* relevant follow-up state,
* permitted notes,
* tags,
* consent state,
* and other approved patient intelligence.

Sensitive data must have stricter access controls.

⸻

11. Patient Intelligence Requirements

PR-PI-001

The system must maintain structured patient context.

PR-PI-002

Patient context must distinguish authoritative facts from AI-generated interpretations.

PR-PI-003

AI-generated summaries must not silently replace source records.

PR-PI-004

Patient intelligence must be tenant-scoped.

PR-PI-005

Patient context provided to AI must be minimized to information relevant to the current task.

PR-PI-006

The system should identify useful interaction signals such as:

* interests,
* preferences,
* unresolved questions,
* lead state,
* requested services,
* and next actions.

⸻

12. Conversation Requirements

Clinicos must provide a unified conversation system.

The conversation system must support:

* inbound messages,
* outbound messages,
* conversation state,
* message history,
* attachments,
* metadata,
* intent,
* context,
* AI processing,
* staff takeover,
* and escalation.

The system should preserve conversation continuity.

⸻

13. Conversation Normalization

Messages from different channels must be normalized into a common internal representation.

The normalized representation should support:

* sender,
* recipient,
* timestamp,
* channel,
* content,
* media,
* message type,
* conversation,
* tenant,
* identity,
* and delivery metadata.

Channel-specific details must remain available where required.

⸻

14. Conversation Ownership

A conversation must support ownership states such as:

* AI-owned,
* staff-owned,
* shared,
* escalated,
* paused,
* closed.

When staff take ownership, AI automation must respect the ownership state.

⸻

15. Lead Management Requirements

Clinicos must provide structured lead management.

A lead should support:

* source,
* patient/person,
* intent,
* service interest,
* status,
* priority,
* score where applicable,
* last interaction,
* next action,
* assigned staff,
* follow-up state,
* appointment relationship,
* conversion state,
* and timestamps.

⸻

16. Lead Lifecycle

The lead lifecycle must support states such as:

NEW
QUALIFYING
QUALIFIED
ENGAGED
CONSIDERING
APPOINTMENT_REQUESTED
BOOKED
COMPLETED
CONVERTED
LOST
REACTIVATION

The exact implementation may evolve.

State transitions must be deterministic and auditable.

AI may recommend transitions but must not bypass business rules.

⸻

17. Lead Intelligence

AI may assist with:

* lead classification,
* intent detection,
* service interest extraction,
* urgency signals,
* conversation summaries,
* qualification,
* next-action recommendations,
* and follow-up recommendations.

AI-generated lead information must be distinguishable from authoritative lead state.

⸻

18. Follow-Up Requirements

Clinicos must provide a dedicated Follow-Up Engine.

The system must support:

* lead follow-up,
* patient follow-up,
* appointment reminders,
* appointment follow-up,
* no-show follow-up,
* post-service follow-up,
* human callback,
* reactivation,
* administrative follow-up,
* and approved campaigns.

⸻

19. Follow-Up Validation

Before a follow-up is executed, the system must revalidate relevant conditions.

These may include:

* patient existence,
* tenant,
* consent,
* communication preferences,
* safety state,
* human ownership,
* appointment state,
* timing,
* frequency limits,
* channel availability,
* workflow status,
* and cancellation.

A previously scheduled follow-up is not permanent authorization.

⸻

20. Follow-Up Deduplication

The system must prevent uncontrolled duplicate follow-ups.

Duplicate prevention must consider:

* workflow identity,
* patient,
* purpose,
* scheduled time,
* execution state,
* and idempotency keys where appropriate.

⸻

21. Appointment Requirements

Clinicos must support appointment-related workflows.

These may include:

* appointment requests,
* appointment confirmation,
* reminders,
* cancellation,
* rescheduling,
* attendance,
* no-show handling,
* and follow-up.

The Appointment Domain must remain authoritative for appointment state.

⸻

22. Appointment Truth

AI must not invent:

* available times,
* provider availability,
* clinic hours,
* appointment confirmation,
* appointment cancellation,
* or booking completion.

AI must retrieve these facts from authoritative systems.

⸻

23. Knowledge Requirements

Clinicos must provide a governed knowledge system.

Knowledge sources may include:

* clinic information,
* service descriptions,
* treatment information,
* preparation,
* aftercare,
* FAQs,
* clinic policies,
* educational material,
* and internal procedures.

Knowledge must support:

* versioning,
* tenant ownership,
* metadata,
* permissions,
* provenance,
* retrieval,
* freshness,
* and lifecycle management.

⸻

24. Knowledge Grounding

AI responses that rely on clinic-specific knowledge should use approved knowledge sources.

The system should be able to identify the source of important factual claims where appropriate.

AI should not fabricate clinic-specific information when the relevant source is unavailable.

⸻

25. Dynamic Operational Data

Dynamic operational facts must be retrieved from authoritative systems.

Examples include:

* current price,
* current discount,
* appointment availability,
* provider schedule,
* clinic hours,
* payment status,
* lead state,
* follow-up state,
* and booking status.

RAG must not be treated as the authoritative source for these facts.

⸻

26. AI Requirements

PR-AI-001

Clinicos must provide a centralized AI layer.

PR-AI-002

Gemini must be the only active external AI provider.

PR-AI-003

The platform must retain an internal AI abstraction.

PR-AI-004

Business domains must not directly depend on Gemini SDK implementation details.

PR-AI-005

Clients must not directly call Gemini for governed Clinicos workflows.

PR-AI-006

AI execution must be observable.

PR-AI-007

AI execution must be auditable where required.

PR-AI-008

AI must operate within authorization and safety boundaries.

⸻

27. Gemini Model Selection

Clinicos may use different Gemini models for different workloads.

Examples include:

* conversational reasoning,
* classification,
* extraction,
* summarization,
* multimodal processing,
* image analysis,
* report generation,
* and background tasks.

Model selection must be configuration-driven where practical.

The application must not scatter hardcoded model identifiers throughout business logic.

⸻

28. Gemini Failure Handling

When Gemini fails, Clinicos must support controlled degradation.

Possible strategies include:

* retry,
* timeout,
* exponential backoff,
* circuit breaker,
* queueing,
* safe deterministic response,
* deferred execution,
* and human handoff.

The system must not automatically invoke another AI provider.

⸻

29. AI Agent Requirements

Clinicos should support specialized AI agents.

Potential agents include:

* Conversation Agent,
* Lead Agent,
* Follow-Up Agent,
* Appointment Agent,
* Knowledge Agent,
* Staff Copilot,
* Patient Intelligence Agent,
* Reporting Agent,
* Safety Support Agent,
* Facial Analysis Agent,
* and Orchestrator Agent.

Each agent must have explicit:

* responsibility,
* permissions,
* tools,
* input,
* output,
* safety rules,
* and evaluation criteria.

⸻

30. AI Tool Requirements

AI tools must have:

* defined purpose,
* strict schemas,
* authorization requirements,
* tenant scope,
* risk classification,
* timeout,
* failure behavior,
* and audit requirements.

AI must not have unrestricted access to the database or infrastructure.

⸻

31. AI Context Requirements

AI context should contain only relevant information.

The system should prioritize:

1. Current request
2. User identity context
3. Relevant conversation context
4. Authoritative operational data
5. Relevant knowledge
6. Applicable policies

The system should avoid unnecessary context expansion.

⸻

32. AI Output Validation

AI-generated outputs must be validated before sensitive actions.

Validation may include:

* schema validation,
* factual validation,
* tool result validation,
* policy validation,
* safety validation,
* authorization validation,
* and content restrictions.

⸻

33. AI Hallucination Prevention

The platform must reduce hallucination risk through:

* retrieval,
* authoritative tools,
* structured outputs,
* constrained prompts,
* validation,
* explicit uncertainty handling,
* and human escalation.

AI must not fabricate:

* prices,
* appointment availability,
* provider schedules,
* policies,
* discounts,
* payment status,
* or medical facts unsupported by approved sources.

⸻

34. Medical Safety Requirements

Clinicos must include a dedicated medical safety layer.

The system must support:

* risk detection,
* escalation,
* safety-aware responses,
* human handoff,
* safety event tracking,
* and auditability.

Commercial optimization must never override medical safety.

⸻

35. Medical Communication Boundary

AI may provide approved educational or operational medical information within configured boundaries.

The system must not present unsupported medical claims as authoritative.

Where clinical assessment is required, the workflow should escalate appropriately.

⸻

36. Safety Escalation

A safety escalation may be triggered by:

* patient-reported concerning symptoms,
* adverse-event signals,
* urgent clinical concerns,
* high-risk requests,
* or configured safety rules.

Escalation must notify the appropriate human role according to clinic policy.

⸻

37. Facial Analysis Requirements

Clinicos may provide AI-assisted facial analysis.

The feature may support:

* image quality assessment,
* facial region detection,
* visual observations,
* structured aesthetic analysis,
* before-and-after comparison,
* and educational visualization.

The system must clearly distinguish visual analysis from medical diagnosis.

⸻

38. Facial Image Requirements

Facial images must be treated as sensitive data.

The system must support:

* explicit consent where required,
* access control,
* tenant isolation,
* secure storage,
* secure delivery,
* retention controls,
* and auditability.

⸻

39. Communication Requirements

Clinicos must provide a unified Communication Layer.

The Communication Layer must support an abstraction over:

* Telegram,
* Instagram,
* WhatsApp,
* SMS,
* email,
* web chat,
* mobile push,
* in-app communication,
* voice,
* and internal notifications.

Only supported channels should be enabled at any given product phase.

⸻

40. Communication Responsibilities

The Communication Layer is responsible for:

* message composition handling,
* channel selection,
* delivery,
* provider interaction,
* delivery tracking,
* retries,
* deduplication,
* provider errors,
* and communication observability.

It must not independently decide business intent.

⸻

41. Communication Intent

Communication requests must identify their business purpose.

Examples include:

* appointment confirmation,
* appointment reminder,
* follow-up,
* lead response,
* patient reactivation,
* administrative notice,
* safety escalation,
* human callback,
* marketing,
* authentication,
* and internal notification.

Intent does not equal authorization.

⸻

42. Communication Policy

Before sending a communication, the system should evaluate:

* recipient,
* tenant,
* intent,
* consent,
* channel,
* time,
* frequency,
* quiet hours,
* patient preferences,
* clinic policy,
* safety state,
* human ownership,
* and relevant workflow state.

⸻

43. Communication Lifecycle

The communication system should support states such as:

CREATED
PENDING_POLICY
APPROVED
SCHEDULED
READY
SENDING
SENT
DELIVERED
READ
FAILED
RETRY_SCHEDULED
CANCELLED
BLOCKED
EXPIRED
SUPPRESSED

The system must distinguish between:

* sent,
* delivered,
* and read.

⸻

44. Communication Reliability

The platform must support:

* idempotency,
* deduplication,
* retries,
* backoff,
* provider rate limits,
* circuit breakers,
* queueing,
* backpressure,
* and reconciliation.

Communication failure must not silently become workflow success.

⸻

45. Human Communication

Staff must be able to:

* send messages,
* edit AI drafts,
* approve AI messages,
* reject AI messages,
* take over conversations,
* pause automation,
* and resume automation where permitted.

Human actions must be auditable.

⸻

46. Notification Requirements

Clinicos must provide notifications for:

* appointments,
* follow-ups,
* operational events,
* safety escalations,
* staff tasks,
* authentication,
* administrative events,
* and approved marketing.

Notifications must respect communication policy.

⸻

47. Consent Requirements

The system must support consent at appropriate levels.

Consent may be:

* channel-specific,
* purpose-specific,
* tenant-specific,
* or workflow-specific.

Revocation must be respected.

Unknown consent must not be treated as positive marketing consent.

⸻

48. Quiet Hours

The system should support configurable quiet hours.

Quiet hours must be evaluated before non-urgent communications.

Safety-critical communication may follow separate escalation rules.

⸻

49. Communication Frequency Limits

The platform should enforce configurable communication frequency limits.

Limits may apply by:

* patient,
* channel,
* communication type,
* workflow,
* clinic,
* and time window.

⸻

50. Multilingual Requirements

The platform must support:

* Persian,
* English,
* Azerbaijani Turkish,
* Arabic,
* Turkish.

The system should support:

* language preference,
* language detection,
* multilingual templates,
* multilingual knowledge,
* multilingual AI,
* RTL,
* and code-switching.

⸻

51. Telegram Requirements

Phase 1 must provide a functional Telegram Bot.

The Telegram integration should support:

* inbound messages,
* outbound messages,
* text,
* media,
* patient identity mapping,
* conversation handling,
* AI responses,
* human takeover,
* notifications,
* and supported workflow interactions.

Telegram-specific behavior must remain isolated.

⸻

52. Telegram Mini App Requirements

Phase 2 must provide a Telegram Mini App.

The Mini App should support richer workflows such as:

* patient dashboard,
* appointment interaction,
* structured forms,
* service information,
* staff dashboard,
* lead management,
* analytics,
* and settings.

The Mini App must consume Core Platform APIs.

⸻

53. Web Requirements

Phase 3 must provide a web client.

The web client should support role-appropriate workflows for:

* patients,
* staff,
* doctors,
* and managers.

Business logic must remain server-side.

⸻

54. Android Requirements

Phase 3 may provide an Android application.

The Android application must use the same platform APIs and domain model.

It must not duplicate core business logic.

⸻

55. iOS Requirements

Phase 3 may provide an iOS application.

The iOS application must use the same platform APIs and domain model.

It must not duplicate core business logic.

⸻

56. Cross-Client Consistency

The same underlying patient, lead, appointment, conversation, and workflow state must remain consistent regardless of which client is used.

For example:

Telegram
   |
   v
Patient Conversation
   |
   v
Core Platform
   |
   +---- Web sees same state
   |
   +---- Mini App sees same state
   |
   +---- Android sees same state
   |
   +---- iOS sees same state

⸻

57. Clinic Management Requirements

Clinic management must support configuration of:

* clinic identity,
* business hours,
* services,
* providers,
* communication settings,
* staff,
* policies,
* templates,
* AI configuration,
* knowledge,
* and operational preferences.

Configuration must be tenant-scoped.

⸻

58. Staff Management

The system must support:

* staff accounts,
* roles,
* permissions,
* assignments,
* ownership,
* availability where relevant,
* and audit history.

⸻

59. Role-Based Access

Different roles must receive appropriate access.

Example:

Patient
  -> Own permitted information
Staff
  -> Operational patient information
Doctor
  -> Appropriate clinical and patient information
Manager
  -> Operational and management information
Administrator
  -> Platform-level administration

Exact permissions must be defined by the authorization system.

⸻

60. Analytics Requirements

Clinicos must collect structured operational events.

Analytics should support:

* lead funnel analysis,
* conversion,
* follow-up performance,
* appointment activity,
* communication performance,
* staff activity,
* AI performance,
* workflow performance,
* and patient engagement.

⸻

61. Reporting Requirements

Reports should support multiple roles.

Reports may include:

* daily operational summary,
* weekly clinic report,
* lead performance,
* follow-up effectiveness,
* appointment activity,
* communication statistics,
* AI performance,
* and safety activity.

AI-generated insights must be clearly distinguished from calculated metrics.

⸻

62. AI Evaluation Requirements

AI systems must be continuously evaluated.

Evaluation should include:

* accuracy,
* groundedness,
* instruction following,
* safety,
* multilingual quality,
* tool use,
* structured extraction,
* response quality,
* escalation correctness,
* and human correction rate.

⸻

63. AI Model Governance

AI configuration must be versioned.

The platform should track:

* Gemini model,
* model configuration,
* prompt version,
* agent version,
* tool configuration,
* evaluation version,
* and execution metadata.

⸻

64. Cost Management

The platform must monitor AI consumption.

Metrics should include where available:

* request volume,
* token usage,
* model usage,
* latency,
* error rate,
* and estimated cost.

The system should support configurable usage limits where appropriate.

⸻

65. Automation Requirements

Clinicos must support event-driven automation.

Examples include:

New Lead
    ->
Qualification
    ->
Follow-Up
Appointment Created
    ->
Reminder
Appointment Cancelled
    ->
Workflow Update
Patient Interaction
    ->
Patient Intelligence Update
Safety Event
    ->
Escalation

Automation must respect:

* authorization,
* consent,
* safety,
* tenant boundaries,
* and human ownership.

⸻

66. Event Requirements

Important domain events must be:

* structured,
* identifiable,
* timestamped,
* tenant-scoped,
* traceable,
* and observable.

Events must represent facts.

Commands must represent requested actions.

⸻

67. Idempotency

Critical operations should be idempotent where appropriate.

Examples:

* sending a notification,
* creating a follow-up,
* processing an external webhook,
* booking an appointment,
* updating a workflow,
* and applying an event.

Retries must not create uncontrolled duplicates.

⸻

68. Error Handling

The platform must provide predictable error handling.

Errors should be:

* classified,
* logged,
* observable,
* actionable,
* and safe for the user.

Sensitive internal details must not be exposed to patients.

⸻

69. Graceful Degradation

When an AI or external service is unavailable, Clinicos should continue operating where possible.

Examples:

* deterministic FAQ response,
* staff handoff,
* queued operation,
* delayed processing,
* or manual workflow.

Failure of an optional AI capability must not unnecessarily disable the entire clinic platform.

⸻

70. Security Requirements

The platform must provide:

* secure authentication,
* authorization,
* tenant isolation,
* encryption,
* secret management,
* audit logs,
* secure file handling,
* input validation,
* rate limiting,
* abuse protection,
* and secure integrations.

⸻

71. Prompt Injection Protection

External content must be treated as untrusted.

The platform must prevent patient or external content from overriding:

* system instructions,
* security rules,
* tool permissions,
* tenant boundaries,
* safety rules,
* or authorization.

⸻

72. Secret Protection

Secrets must never be:

* exposed to patients,
* included in AI prompts,
* logged in plaintext,
* embedded in client applications,
* or committed to source control.

Gemini credentials must remain server-side.

⸻

73. Privacy Requirements

The system must follow data minimization principles.

Only required information should be used for a workflow.

Sensitive patient information must have appropriate access controls and retention policies.

⸻

74. Audit Requirements

The platform must record important actions.

Audit events may include:

* login,
* permission changes,
* patient access,
* staff actions,
* AI tool calls,
* AI decisions where required,
* communication approvals,
* messages,
* appointment changes,
* consent changes,
* safety escalations,
* and configuration changes.

⸻

75. Observability Requirements

The system must provide:

* structured logs,
* metrics,
* tracing,
* correlation IDs,
* workflow IDs,
* AI execution IDs,
* communication IDs,
* and alerts.

Important workflows must be diagnosable from observable data.

⸻

76. Performance Requirements

The product should provide responsive user experiences.

Performance must be measured for:

* API requests,
* database operations,
* queue operations,
* AI calls,
* communication delivery,
* dashboards,
* and client interactions.

Performance targets should be defined per workflow during implementation.

⸻

77. Scalability Requirements

The architecture must support growth in:

* clinics,
* patients,
* conversations,
* messages,
* AI requests,
* appointments,
* files,
* and analytics events.

Scaling must not compromise tenant isolation or correctness.

⸻

78. Data Retention

Each data category must have an appropriate retention policy.

Retention should consider:

* operational requirements,
* privacy,
* security,
* legal requirements,
* storage cost,
* and patient expectations.

⸻

79. File Storage

The system must securely manage:

* patient images,
* documents,
* reports,
* attachments,
* and generated media.

File access must be authorized and tenant-scoped.

⸻

80. Search Requirements

Clinicos should provide search across appropriate entities.

Search may include:

* patients,
* conversations,
* leads,
* appointments,
* files,
* knowledge,
* and staff.

Search results must respect authorization and tenant isolation.

⸻

81. Dashboard Requirements

Dashboards should be role-specific.

Staff dashboards should prioritize:

* active conversations,
* unresolved tasks,
* leads,
* follow-ups,
* appointments,
* and escalations.

Management dashboards should prioritize:

* KPIs,
* trends,
* conversion,
* workload,
* communication,
* and operational performance.

⸻

82. Patient Dashboard Requirements

Where a structured client exists, patients should be able to access appropriate information such as:

* appointments,
* conversations,
* services,
* follow-up instructions,
* documents,
* and clinic information.

Patient access must remain limited to authorized information.

⸻

83. Staff Copilot Requirements

The Staff Copilot should assist with:

* conversation summaries,
* suggested replies,
* lead summaries,
* next actions,
* patient context,
* follow-up recommendations,
* and operational queries.

AI suggestions must remain distinguishable from confirmed facts.

⸻

84. Patient AI Assistant Requirements

The patient-facing AI assistant should:

* understand the patient request,
* retrieve relevant knowledge,
* retrieve authoritative operational data,
* provide appropriate responses,
* recognize when human intervention is needed,
* respect consent and privacy,
* and maintain conversation continuity.

⸻

85. AI Response Modes

Patient-facing AI may use:

DIRECT_RESPONSE
ASK_CLARIFICATION
RETRIEVE_INFORMATION
USE_TOOL
ESCALATE_TO_HUMAN
REFUSE
DEFER

The selected mode should depend on policy and task requirements.

⸻

86. Human Escalation Requirements

The system must support escalation when:

* the patient explicitly requests staff,
* the request exceeds AI permissions,
* the request is medically sensitive,
* confidence is insufficient,
* safety risk is detected,
* or clinic policy requires human review.

⸻

87. Ethical Communication Requirements

Clinicos must not intentionally generate:

* fabricated urgency,
* fabricated scarcity,
* false testimonials,
* deceptive medical claims,
* guilt-based persuasion,
* fear-based commercial pressure,
* or misleading pricing claims.

⸻

88. Pricing Requirements

AI must not invent pricing.

If pricing is available through an authoritative source, AI may communicate it.

If current pricing is unavailable, the system should provide an appropriate response such as:

* requesting staff assistance,
* providing general non-price information,
* or directing the patient to an authoritative pricing source.

⸻

89. Discount Requirements

AI must not invent discounts.

Discount information must come from an authoritative clinic configuration or approved campaign system.

Expired discounts must not be presented as active.

⸻

90. Appointment Booking Requirements

Where appointment booking is supported, the workflow must:

1. Identify the patient.
2. Determine the requested service.
3. Retrieve authoritative availability.
4. Present available options.
5. Obtain required confirmation.
6. Create the appointment through the authoritative system.
7. Confirm the actual result.
8. Record the event.
9. Trigger appropriate downstream workflows.

The AI must not claim booking success until the authoritative system confirms success.

⸻

91. Appointment Cancellation Requirements

Cancellation must be performed through the authoritative appointment system.

The communication layer must not independently mark an appointment as cancelled.

⸻

92. Appointment Rescheduling Requirements

Rescheduling must follow the same authoritative workflow.

The system must distinguish between:

* requested rescheduling,
* pending rescheduling,
* and confirmed rescheduling.

⸻

93. No-Show Requirements

The system should support no-show detection and follow-up.

No-show workflows must use authoritative appointment state.

⸻

94. Post-Service Follow-Up

Clinicos should support post-service workflows.

Examples include:

* routine check-in,
* aftercare reminder,
* satisfaction feedback,
* follow-up appointment suggestion,
* and safety screening.

Medical safety rules take priority.

⸻

95. Reactivation Requirements

Clinicos should support patient and lead reactivation.

Reactivation must consider:

* consent,
* communication preferences,
* previous activity,
* recent communications,
* clinic policy,
* and frequency limits.

⸻

96. Campaign Requirements

Marketing campaigns must support:

* explicit campaign definition,
* target audience,
* consent validation,
* frequency control,
* scheduling,
* message approval,
* delivery tracking,
* and performance measurement.

Campaigns must not bypass communication policies.

⸻

97. Communication Personalization

Personalization may use approved patient context.

The system should avoid exposing sensitive information unnecessarily.

AI-generated personalization must be validated before high-risk communication.

⸻

98. Localization Requirements

Localization must cover:

* UI,
* messages,
* templates,
* system notifications,
* knowledge,
* AI responses,
* dates,
* times,
* numbers,
* and RTL behavior.

⸻

99. Timezone Requirements

All scheduled workflows must operate using an explicit timezone.

Clinic timezone and patient timezone must be distinguishable where relevant.

Scheduling logic must not assume UTC-only user behavior.

⸻

100. Quiet Hours Requirements

The system must support clinic-configured and potentially patient-specific quiet hours.

Non-urgent communications should respect quiet hours.

Urgent safety communication may follow separate policy.

⸻

101. Notification Preference Requirements

Patients should be able to manage appropriate notification preferences.

Preferences may include:

* channel,
* communication category,
* language,
* frequency,
* and quiet hours.

Preferences must be applied consistently across workflows.

⸻

102. Communication Delivery Tracking

The platform should track:

* created,
* approved,
* scheduled,
* sent,
* delivered,
* read,
* failed,
* retried,
* cancelled,
* and suppressed.

Delivery status must originate from the communication infrastructure or provider evidence.

⸻

103. Provider Adapter Requirements

Each communication provider should be isolated behind an adapter.

Adapters should expose standardized internal behavior while hiding provider-specific details.

⸻

104. Integration Requirements

External integrations must use explicit interfaces.

Integrations should support:

* authentication,
* authorization,
* retries,
* timeouts,
* rate limits,
* webhooks,
* reconciliation,
* and observability.

⸻

105. Webhook Requirements

Incoming webhooks must be:

* authenticated,
* validated,
* tenant-safe,
* idempotent,
* logged,
* and observable.

Webhook ordering assumptions must be explicit.

⸻

106. API Requirements

The Core API must provide stable contracts.

APIs should support:

* authentication,
* identity,
* patients,
* conversations,
* leads,
* appointments,
* follow-ups,
* knowledge,
* AI,
* communication,
* notifications,
* analytics,
* reports,
* files,
* staff,
* and clinic configuration.

⸻

107. API Security

Every API endpoint must enforce:

* authentication,
* authorization,
* tenant scope,
* input validation,
* rate limiting where appropriate,
* and safe error handling.

⸻

108. API Versioning

Breaking API changes must be versioned or migrated through controlled compatibility strategies.

Clients must not silently break because of server-side changes.

⸻

109. Event API

Internal event contracts must be structured and versioned.

Events should contain sufficient metadata for:

* traceability,
* tenant identification,
* correlation,
* timestamping,
* and processing.

⸻

110. Product Notifications

The system should support internal notifications for staff.

Examples:

* new lead,
* urgent lead,
* safety escalation,
* appointment issue,
* failed workflow,
* human takeover request,
* and system alert.

⸻

111. Task Management

Clinicos should allow staff to manage operational tasks.

Tasks may be generated from:

* conversations,
* leads,
* appointments,
* follow-ups,
* safety events,
* or system events.

Tasks should have:

* owner,
* priority,
* due time,
* state,
* source,
* and audit history.

⸻

112. Staff Assignment

Workflows may be assigned to staff according to:

* role,
* clinic policy,
* workload,
* service,
* provider,
* or manual assignment.

AI may recommend assignment but must not bypass authorization.

⸻

113. Queue Requirements

Background workloads should use appropriate queues.

Potential queue categories include:

* AI tasks,
* notifications,
* follow-ups,
* analytics,
* reports,
* media processing,
* and integration events.

⸻

114. Retry Requirements

Retries must be bounded.

Retry logic should include:

* maximum attempts,
* exponential backoff,
* jitter where appropriate,
* failure classification,
* and dead-letter handling.

⸻

115. Circuit Breaker Requirements

External dependencies should support circuit-breaking where repeated failures could cause cascading failures.

This applies especially to:

* Gemini,
* communication providers,
* external scheduling,
* and other remote systems.

⸻

116. Backpressure

The system must protect itself from overload.

Possible mechanisms include:

* queue limits,
* concurrency limits,
* rate limiting,
* request rejection,
* deferred execution,
* and workload prioritization.

⸻

117. Priority

Workflows may have priority levels.

Safety-critical tasks must receive higher priority than routine commercial tasks.

⸻

118. Disaster Recovery

Clinicos must support recovery from:

* database failure,
* infrastructure failure,
* provider outage,
* message delivery outage,
* queue failure,
* configuration corruption,
* and deployment failure.

Backup and recovery requirements must be defined in the disaster recovery specification.

⸻

119. Backup Requirements

Critical data must be backed up according to defined retention and recovery objectives.

Backups must be protected from unauthorized access.

⸻

120. Recovery Requirements

Recovery procedures must be documented and tested.

The system should define:

* recovery objectives,
* backup frequency,
* restoration procedures,
* verification,
* and rollback strategy.

⸻

121. Deployment Requirements

Deployment must support:

* environment separation,
* secrets management,
* migrations,
* health checks,
* rollback,
* logging,
* monitoring,
* and reproducibility.

⸻

122. Environment Separation

At minimum, the architecture should distinguish between:

* development,
* testing,
* staging where appropriate,
* and production.

Production data must not be casually used in development environments.

⸻

123. Configuration Management

Configuration must be:

* versioned where appropriate,
* validated,
* environment-aware,
* tenant-aware,
* and auditable.

Secrets must not be stored as normal configuration values.

⸻

124. Feature Flags

Feature flags may be used for controlled rollout.

Feature flags must not be used to bypass:

* authorization,
* medical safety,
* privacy,
* consent,
* or tenant isolation.

⸻

125. Product Rollout

Major features should be introduced progressively where practical.

Possible rollout stages:

Development
   ->
Internal Validation
   ->
Limited Pilot
   ->
Controlled Production
   ->
General Availability

⸻

126. Beta Features

Experimental features must be clearly isolated from stable workflows.

AI experiments must not silently affect critical production behavior without appropriate controls.

⸻

127. Analytics Data Quality

Analytics must distinguish:

* raw events,
* calculated metrics,
* inferred signals,
* and AI-generated interpretations.

Metrics must have defined calculation rules.

⸻

128. KPI Requirements

Clinicos should provide KPIs across:

Patient Engagement

* active patients,
* response rate,
* interaction frequency.

Leads

* new leads,
* qualification,
* conversion,
* loss,
* reactivation.

Appointments

* requests,
* bookings,
* cancellations,
* no-shows,
* completion.

Follow-Up

* scheduled,
* sent,
* delivered,
* responded,
* converted,
* suppressed.

AI

* requests,
* success rate,
* latency,
* escalation,
* correction rate,
* safety events.

Operations

* staff workload,
* unresolved tasks,
* workflow failures,
* communication performance.

⸻

129. AI Success Metrics

AI success must not be measured only by response volume.

Useful metrics include:

* task completion,
* factual correctness,
* groundedness,
* human correction,
* escalation correctness,
* tool accuracy,
* workflow completion,
* and patient/staff outcome signals.

⸻

130. Product Success Criteria

Clinicos should be considered successful when it demonstrably improves clinic operations through:

* reduced repetitive staff work,
* fewer missed follow-ups,
* better lead visibility,
* better response consistency,
* improved operational visibility,
* safer communication,
* and reliable AI assistance.

Specific quantitative targets should be defined during implementation and validated empirically.

⸻

131. User Experience Requirements

The interface should:

* minimize unnecessary steps,
* provide clear next actions,
* show relevant context,
* avoid confusing AI behavior,
* make human escalation accessible,
* and communicate system state clearly.

⸻

132. AI Transparency

Where relevant, the system should indicate when content is:

* AI-generated,
* staff-generated,
* template-generated,
* or system-generated.

Users should not be intentionally misled about the source of communication where disclosure is required by policy or product design.

⸻

133. Uncertainty Handling

When AI lacks sufficient information, the system should:

* ask for clarification,
* retrieve additional information,
* use a tool,
* provide a bounded answer,
* or escalate.

The system should prefer uncertainty over fabrication.

⸻

134. Refusal Requirements

AI must refuse or redirect requests that exceed its permissions or safety boundaries.

Refusal should be:

* concise,
* respectful,
* useful where possible,
* and followed by an appropriate alternative.

⸻

135. Abuse Prevention

Clinicos must protect against:

* spam,
* automated abuse,
* message flooding,
* tool abuse,
* prompt injection,
* excessive AI usage,
* and malicious automation.

⸻

136. Rate Limiting

Rate limits should exist where necessary for:

* authentication,
* APIs,
* AI requests,
* messaging,
* public endpoints,
* and external integrations.

⸻

137. Data Provenance

Important information should have identifiable provenance where appropriate.

Possible provenance sources include:

* patient input,
* staff input,
* appointment system,
* clinic configuration,
* knowledge source,
* external integration,
* AI inference.

⸻

138. AI-Generated Data

AI-generated information should include appropriate metadata where useful:

* model,
* prompt version,
* agent,
* timestamp,
* source context,
* confidence or evaluation metadata where available.

AI-generated information should not silently appear as confirmed clinical fact.

⸻

139. Knowledge Freshness

Knowledge sources should have freshness metadata.

Stale knowledge should be identified and handled appropriately.

Operational information must still come from authoritative live systems.

⸻

140. Knowledge Approval

Clinic-specific knowledge may require approval before becoming available to patient-facing AI.

Knowledge changes should be versioned.

⸻

141. Prompt Governance

Prompts must be treated as controlled configuration.

Prompt changes should be:

* versioned,
* reviewable,
* testable,
* attributable,
* and reversible.

⸻

142. Model Governance

Gemini model changes should be:

* versioned,
* evaluated,
* monitored,
* and rolled out in a controlled manner.

A model change should not silently invalidate safety-critical behavior.

⸻

143. AI Regression Testing

AI workflows must be tested against regression datasets.

Regression tests should cover:

* normal requests,
* ambiguous requests,
* adversarial requests,
* safety cases,
* multilingual cases,
* tool use,
* and operational truth.

⸻

144. Security Regression Testing

Security regression tests should cover:

* cross-tenant access,
* privilege escalation,
* prompt injection,
* secret leakage,
* unauthorized tool use,
* and insecure file access.

⸻

145. Client Compatibility

The backend must remain compatible with supported clients.

Breaking changes must use controlled versioning.

⸻

146. Mobile Compatibility

Future mobile clients must use the same:

* identity,
* API,
* authorization,
* domain model,
* and event architecture.

⸻

147. Accessibility

Client interfaces should support appropriate accessibility practices.

Accessibility should be considered from the beginning rather than treated as a final polish step.

⸻

148. Internationalization

All user-facing text should be externalizable for localization.

Business logic must not depend on a specific language.

⸻

149. Date and Time Localization

The platform must support localized:

* date formats,
* time formats,
* timezone handling,
* and calendar representations where required.

⸻

150. Error Message Localization

Patient-facing errors should be localized.

Internal diagnostic information must remain protected.

⸻

151. Patient Data Export

Where supported by product and policy, patients or authorized staff should be able to request appropriate data exports.

Exports must be:

* authorized,
* scoped,
* auditable,
* and secure.

⸻

152. Patient Data Deletion

Where applicable, the platform should support controlled deletion or anonymization workflows.

Deletion must account for:

* legal requirements,
* audit obligations,
* dependencies,
* and data retention policies.

⸻

153. Consent History

Consent changes should be auditable.

The system should record:

* consent type,
* channel,
* timestamp,
* source,
* state,
* and revocation where applicable.

⸻

154. Communication History

The platform should retain appropriate communication metadata.

This may include:

* sender,
* recipient,
* channel,
* purpose,
* timestamp,
* delivery state,
* and relevant workflow.

⸻

155. Appointment History

Appointment changes should be traceable.

The system should distinguish:

* requested,
* confirmed,
* changed,
* cancelled,
* completed,
* and no-show.

⸻

156. Lead History

Lead state changes should be traceable.

Important transitions should record:

* previous state,
* new state,
* source,
* actor,
* timestamp,
* and reason where available.

⸻

157. Follow-Up History

Follow-up lifecycle should be observable.

The system should distinguish:

* scheduled,
* ready,
* executed,
* sent,
* delivered,
* responded,
* skipped,
* cancelled,
* failed,
* and suppressed.

⸻

158. AI Action History

AI actions that cause external effects should be auditable.

Examples:

* sending a message,
* creating a follow-up,
* updating a lead,
* creating a task,
* invoking a tool,
* or triggering an escalation.

⸻

159. Human Action History

Human actions should be auditable where appropriate.

Examples:

* staff takeover,
* approval,
* rejection,
* editing,
* assignment,
* appointment changes,
* configuration changes.

⸻

160. System Action History

Automated system actions should be traceable.

The system should distinguish:

* human action,
* AI action,
* scheduled automation,
* system event,
* and external integration.

⸻

161. Product Boundary: AI Versus Domain

The AI layer provides intelligence.

The domain layer provides authoritative state.

The distinction must remain explicit.

AI:
Interpret
Recommend
Generate
Summarize
Classify
Assist
Domain:
Own
Validate
Persist
Authorize
Execute
Audit

⸻

162. Product Boundary: Communication Versus Follow-Up

The Follow-Up Engine decides:

Should a follow-up exist?

The Communication Layer decides:

How should an approved communication be delivered?

Neither system should silently absorb the other’s responsibilities.

⸻

163. Product Boundary: Knowledge Versus Operational Truth

Knowledge provides:

Approved information.

Operational systems provide:

Current state.

The AI layer may combine both.

It must not confuse them.

⸻

164. Product Boundary: Client Versus Platform

Clients provide:

Interaction and presentation.

The platform provides:

Business logic, data, policies, AI governance, and operational state.

⸻

165. Product Boundary: AI Provider Versus AI Layer

Gemini provides:

Model inference.

Clinicos AI Layer provides:

Governance, orchestration, context, tools, validation, observability, and business integration.

⸻

166. Phase 1 Minimum Product

The Phase 1 MVP should include a complete functional foundation for:

* clinic identity,
* patient identity,
* Telegram communication,
* conversations,
* AI-assisted responses,
* knowledge retrieval,
* lead management,
* follow-up,
* appointment-related workflows,
* human takeover,
* notifications,
* safety escalation,
* analytics,
* and auditability.

The exact implementation sequence may vary.

⸻

167. Phase 1 Non-Requirements

Phase 1 does not require:

* Web client,
* Android client,
* iOS client,
* every possible communication channel,
* multi-provider AI routing,
* multi-provider AI fallback,
* speculative infrastructure,
* or every advanced analytics capability.

⸻

168. Phase 2 Minimum Product

Phase 2 should add the Telegram Mini App while preserving the same Core Platform.

Priority areas:

* structured patient experience,
* staff dashboards,
* appointment workflows,
* lead management,
* settings,
* and analytics.

⸻

169. Phase 3 Minimum Product

Phase 3 should expand the experience layer to:

* Web,
* Android,
* iOS.

The backend domain model should remain stable.

⸻

170. Migration Requirements

When moving from historical implementation to the target architecture, migration must identify:

* obsolete provider code,
* legacy routing,
* outdated APIs,
* stale environment variables,
* obsolete configuration,
* conflicting domain boundaries,
* and deprecated workflows.

Migration must be controlled rather than performed through undocumented rewrites.

⸻

171. Legacy Provider Removal

Historical AI providers that conflict with the target architecture should be removed or isolated from active runtime paths.

The target system must not retain hidden fallback paths to legacy providers.

⸻

172. Repository Alignment

The repository should eventually reflect the target architecture.

This includes:

* code structure,
* configuration,
* environment variables,
* adapters,
* services,
* tests,
* documentation,
* and deployment configuration.

⸻

173. Documentation as Product Infrastructure

Documentation is part of the product engineering system.

Major architectural changes must update affected specifications.

Contradictory documentation must be resolved rather than ignored.

⸻

174. Product Requirement Traceability

Important requirements should be traceable to:

* implementation,
* tests,
* documentation,
* and operational monitoring.

This allows the team to determine whether a requirement is actually implemented.

⸻

175. Definition of Done

A product capability should not be considered complete until:

1. Functional behavior exists.
2. Domain ownership is defined.
3. Authorization is enforced.
4. Tenant isolation is verified.
5. Failure handling exists.
6. Relevant tests exist.
7. Observability exists.
8. Audit behavior is defined where required.
9. AI behavior is evaluated where applicable.
10. Safety requirements are satisfied.
11. Documentation is updated.
12. Client behavior is compatible with the Core Platform model.

⸻

176. Architecture Compatibility Requirement

Every new feature must answer:

Does this feature preserve Core Platform independence from clients?

If not, the design must be reconsidered.

⸻

177. AI Compatibility Requirement

Every AI feature must answer:

Can this workflow operate safely through the governed AI layer using Gemini without creating hidden provider dependencies?

If not, the design must be reconsidered.

⸻

178. Operational Truth Requirement

Every feature involving live operational information must answer:

What is the authoritative source of truth?

If no authoritative source exists, the system must not fabricate the answer.

⸻

179. Human Control Requirement

Every automation feature must answer:

How can a human intervene?

If no appropriate intervention mechanism exists for a workflow that can affect patients, communication, safety, or clinic operations, the design must be reconsidered.

⸻

180. Privacy Requirement

Every feature involving patient information must answer:

What is the minimum data required?

Only necessary data should be exposed to the workflow or AI.

⸻

181. Safety Requirement

Every medical or health-related feature must answer:

What happens when the system detects uncertainty or risk?

There must be an explicit safety behavior.

⸻

182. Observability Requirement

Every critical workflow must answer:

How will the team know that this workflow succeeded or failed?

The answer must include observable signals.

⸻

183. Recovery Requirement

Every critical workflow must answer:

What happens after a timeout, retry, duplicate request, or provider failure?

The behavior must be deterministic and safe.

⸻

184. Cross-Client Requirement

Every new feature must be evaluated for:

* Telegram compatibility,
* Mini App compatibility,
* Web compatibility,
* mobile compatibility,
* and future channel compatibility.

Not every feature must launch on every client simultaneously.

However, the domain design must not become client-dependent.

⸻

185. Product Roadmap Principle

The roadmap should prioritize complete operational loops over isolated feature count.

A smaller number of reliable end-to-end workflows is preferable to many disconnected features.

⸻

186. End-to-End Product Workflow

A canonical patient workflow is:

Patient Sends Message
        |
        v
Telegram Adapter
        |
        v
Identity Resolution
        |
        v
Conversation
        |
        v
Intent Understanding
        |
        v
Patient Context
        |
        v
Policy + Safety
        |
        v
Knowledge / Operational Tools
        |
        v
Gemini Assistance
        |
        v
Output Validation
        |
        v
Response
        |
        v
Lead / Appointment / Follow-Up Action
        |
        v
Communication
        |
        v
Event
        |
        v
Analytics + Audit

⸻

187. Canonical Lead Workflow

Inbound Patient
      |
      v
Lead Detection
      |
      v
Lead Creation
      |
      v
Qualification
      |
      v
Service Interest
      |
      v
Appointment Opportunity
      |
      v
Follow-Up
      |
      v
Appointment
      |
      v
Completion
      |
      v
Conversion / Retention

Every transition must be governed by platform rules.

⸻

188. Canonical Follow-Up Workflow

Trigger
   |
   v
Determine Follow-Up
   |
   v
Check Patient State
   |
   v
Check Consent
   |
   v
Check Safety
   |
   v
Check Human Ownership
   |
   v
Check Frequency
   |
   v
Check Timing
   |
   v
Generate / Select Content
   |
   v
Validate
   |
   v
Send
   |
   v
Observe
   |
   v
Reconcile

⸻

189. Canonical AI Workflow

User Request
   |
   v
Authentication / Identity
   |
   v
Tenant Resolution
   |
   v
Intent Classification
   |
   v
Permission Check
   |
   v
Safety Check
   |
   v
Context Construction
   |
   v
Agent Selection
   |
   v
Gemini Model Selection
   |
   v
Knowledge / Tool Access
   |
   v
Gemini Execution
   |
   v
Output Validation
   |
   v
Domain Action or Response
   |
   v
Audit + Evaluation

⸻

190. Canonical Communication Workflow

Business Intent
   |
   v
Communication Request
   |
   v
Policy Validation
   |
   v
Consent Validation
   |
   v
Safety Validation
   |
   v
Content Validation
   |
   v
Channel Selection
   |
   v
Provider Adapter
   |
   v
Delivery
   |
   v
Delivery Event
   |
   v
Reconciliation
   |
   v
Analytics + Audit

⸻

191. Product-Level Safety Hierarchy

When requirements conflict, the system should prioritize:

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
User Preferences
      >
Patient Convenience
      >
Communication Reliability
      >
Commercial Optimization

⸻

192. Product-Level Decision Rules

When uncertainty exists:

* prefer authoritative data over AI memory,
* prefer clarification over fabrication,
* prefer human escalation over unsafe automation,
* prefer explicit consent over assumption,
* prefer deterministic rules over uncontrolled AI behavior,
* prefer safe degradation over silent failure,
* and prefer traceability over invisible automation.

⸻

193. Final Product Requirements Summary

Clinicos must provide a unified operating platform with:

Identity

Unified person and channel identity.

Patient Intelligence

Structured and contextual patient information.

Conversation

Persistent, normalized, intelligent conversations.

Lead Management

Structured lead lifecycle and qualification.

Follow-Up

Policy-aware automated follow-up.

Appointments

Authoritative appointment workflows.

Knowledge

Governed clinic and medical knowledge.

Medical Safety

Safety detection and escalation.

AI

Governed Gemini-powered intelligence.

Agents

Specialized AI agents with bounded tools.

Communication

Channel-agnostic communication infrastructure.

Notifications

Reliable operational and patient notifications.

Facial Analysis

Controlled image-based analysis capabilities.

Analytics

Operational intelligence and KPIs.

Reporting

Role-specific reports.

Automation

Event-driven operational workflows.

Clinic Management

Configuration and staff administration.

Security

Tenant isolation, authorization, privacy, and auditability.

Reliability

Retries, idempotency, observability, and recovery.

Clients

Telegram -> Mini App -> Web / Android / iOS.

⸻

194. Final Non-Negotiable Requirements

The following requirements are mandatory:

1. Clinicos must be a Core Platform, not a Telegram-specific application.
2. Telegram is the Phase 1 client.
3. Telegram Mini App is the Phase 2 client.
4. Web, Android, and iOS are Phase 3 clients.
5. Core business logic must remain client-independent.
6. Gemini is the only active AI provider.
7. FreeLLMAPI must not be part of the target runtime architecture.
8. Multi-provider AI routing must not be implemented.
9. AI provider fallback must not be implemented.
10. The internal AI abstraction must remain.
11. Gemini-specific code must remain isolated.
12. Clients must not directly call Gemini for governed workflows.
13. AI must not be the source of operational truth.
14. Dynamic facts must come from authoritative systems.
15. Communication must remain channel-agnostic.
16. Tenant isolation must be enforced centrally.
17. Authorization must be enforced server-side.
18. Consent must be enforced before applicable communication.
19. Medical safety must take precedence over commercial goals.
20. Human takeover must be supported.
21. Follow-ups must be revalidated before execution.
22. Communication must be idempotent where appropriate.
23. Important workflows must be observable.
24. Important actions must be auditable.
25. Sensitive patient data must be minimized and protected.
26. AI outputs must be validated before sensitive actions.
27. External integrations must be isolated behind defined boundaries.
28. Product logic must not be duplicated across clients.
29. Historical implementation must not override the target architecture.
30. Future extensibility must not justify unnecessary Phase 1 complexity.

⸻

195. Final Product Contract

The product contract for Clinicos is:

Clinicos is a clinic operating platform.
The Core Platform owns business state.
Clients provide user experiences.
Communication provides delivery infrastructure.
AI provides governed intelligence.
Gemini provides model inference.
Knowledge provides approved information.
Authoritative systems provide live operational truth.
Policies determine what is allowed.
Safety determines what is acceptable.
Human staff retain control where required.
Analytics measure outcomes.
Audit records important actions.
The architecture remains client-independent.
The platform evolves from Telegram to a multi-client system
without redesigning its core domain model.

⸻

196. Final Statement

Clinicos must not be built as a collection of disconnected AI features.

It must be built as one coherent operating system for clinics.

Every major capability must connect to the shared platform model:

Identity
   ->
Patient
   ->
Conversation
   ->
Intent
   ->
Lead / Appointment / Clinical Context
   ->
Policy
   ->
AI / Knowledge / Tools
   ->
Validated Action
   ->
Communication
   ->
Follow-Up
   ->
Outcome
   ->
Analytics
   ->
Improvement

The first implementation channel is Telegram.

The long-term product is much larger than Telegram.

The current AI engine is Gemini.

The long-term architecture is larger than any single AI provider.

The Core Platform is the foundation.

All future clients and channels must build on that foundation.

The ultimate product requirement is therefore:

Build Clinicos as a reliable, secure, AI-native, multi-tenant clinic operating platform whose intelligence is powered by governed Gemini integration and whose core business capabilities remain independent of both the AI provider and the client interface.
