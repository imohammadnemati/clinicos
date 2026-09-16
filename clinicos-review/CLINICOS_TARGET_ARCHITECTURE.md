# CLINICOS TARGET ARCHITECTURE
**Document:** CLINICOS_TARGET_ARCHITECTURE.md  
**Version:** 2.0  
**Status:** Authoritative Target Architecture Specification  
**Effective:** Immediately  
**Language:** English  
**Parent Documents:**
- CLINICOS_MASTER_VISION.md
- CLINICOS_PRODUCT_REQUIREMENTS.md
- CLINICOS_ARCHITECTURE_CHANGE_SET.md
---
# 1. Purpose
This document defines the target technical architecture of Clinicos.
It describes how the Clinicos platform is structured, how its domains interact, how AI is integrated, how clients communicate with the platform, how external systems are isolated, and how the architecture evolves across product phases.
This document defines the intended destination architecture.
The current repository implementation may differ substantially from this architecture.
Historical implementation decisions, temporary workarounds, provider integrations, legacy modules, or existing repository structures must not override this specification.
---
# 2. Architectural Status
This architecture is authoritative for the target Clinicos platform.
If an existing implementation conflicts with this document, the implementation must be evaluated against the target architecture rather than treated as the architectural source of truth.
Architecture changes must be documented explicitly.
No implementation should silently redefine the target architecture.
---
# 3. Core Architectural Decision
Clinicos is an AI-native clinic operating platform.
It is not:
- a Telegram bot with additional features;
- a collection of independent AI utilities;
- a Gemini wrapper;
- an LLM chatbot;
- a CRM with an AI feature;
- a single-channel automation system.
Clinicos is a multi-client clinic operating platform whose first client is Telegram.
The platform must therefore be designed around the following principle:
```text
CORE PLATFORM FIRST
CLIENTS SECOND

⸻

4. Target Platform Model

The target system is structured as:

                    CLIENTS
                       |
        +--------------+--------------+
        |              |              |
     Telegram       Mini App      Web / Mobile
        |              |              |
        +--------------+--------------+
                       |
                    API Layer
                       |
              Application Layer
                       |
                 Core Platform
                       |
       +---------------+----------------+
       |               |                |
    Domains         Workflows        Policies
       |               |                |
       +---------------+----------------+
                       |
                AI Governance Layer
                       |
                 Gemini Adapter
                       |
                 Google Gemini API
                       |
             External Integrations

The Core Platform is the center of the architecture.

Clients are replaceable presentation and interaction surfaces.

⸻

5. Architectural Principles

5.1 Core Platform First

Business logic must live inside the platform.

Clients must not contain authoritative business logic.

⸻

5.2 Client Independence

The Core Platform must remain functional regardless of whether the request originates from:

* Telegram;
* Telegram Mini App;
* Web;
* Android;
* iOS;
* future channels.

⸻

5.3 Channel Independence

Communication logic must not be tightly coupled to Telegram.

Telegram is the first communication channel, not the permanent architectural boundary.

⸻

5.4 Gemini-Only AI Provider

Google Gemini is the only active AI provider.

The architecture must not implement:

* FreeLLMAPI;
* OpenRouter;
* OpenAI as a runtime provider;
* Qwen as a runtime provider;
* DeepSeek as a runtime provider;
* multi-provider routing;
* provider scoring;
* provider fallback;
* cross-provider failover.

⸻

5.5 AI Abstraction Remains Mandatory

Although Gemini is the only active provider, Clinicos must maintain an internal AI abstraction.

The application must not directly depend on Gemini SDK behavior throughout the codebase.

The preferred structure is:

Clinicos Application
        |
   AI Interface
        |
   Gemini Adapter
        |
 Gemini SDK / API

This preserves architectural replaceability without implementing multi-provider runtime behavior.

⸻

5.6 No Direct Client-to-Gemini Access

Clients must never directly call Gemini for governed Clinicos workflows.

The following is prohibited:

Telegram Client -> Gemini
Web Client -> Gemini
Mobile Client -> Gemini
Mini App -> Gemini

The correct architecture is:

Client
   |
Clinicos API
   |
Core Platform
   |
AI Governance Layer
   |
Gemini Adapter
   |
Gemini

⸻

6. Architectural Layers

Clinicos is organized into the following logical layers.

1. Client Layer
2. API / Interface Layer
3. Application Layer
4. Domain Layer
5. Policy and Governance Layer
6. AI Layer
7. Infrastructure Layer
8. Integration Layer
9. Data Layer
10. Observability Layer

These layers may map to different physical modules or services depending on deployment strategy.

Logical separation is mandatory even if early deployment uses a modular monolith.

⸻

7. Client Layer

The Client Layer contains user-facing interfaces.

Planned clients:

Phase 1:
Telegram Bot
Phase 2:
Telegram Bot
Telegram Mini App
Phase 3:
Telegram Bot
Telegram Mini App
Web
Android
iOS

Future clients may be added without redesigning the Core Platform.

⸻

8. Phase 1 Client Architecture

Phase 1 uses Telegram as the primary external interface.

Telegram User
      |
Telegram Bot
      |
Telegram Adapter
      |
Clinicos API
      |
Core Platform

Telegram-specific concerns must remain inside the Telegram boundary.

Examples include:

* Telegram update parsing;
* Telegram user identifiers;
* Telegram message identifiers;
* Telegram media identifiers;
* Telegram reply mechanisms;
* Telegram webhook or polling behavior;
* Telegram-specific formatting.

These concerns must not leak into core business domains.

⸻

9. Phase 2 Client Architecture

Phase 2 adds Telegram Mini App functionality.

The Mini App must communicate with Clinicos through the platform API.

Telegram Mini App
        |
     API Layer
        |
   Core Platform

The Mini App must not directly access:

* database credentials;
* Redis credentials;
* Gemini credentials;
* internal service credentials;
* provider credentials.

⸻

10. Phase 3 Client Architecture

Phase 3 introduces:

* Web;
* Android;
* iOS.

All clients consume the same Core Platform APIs.

Telegram --------\
Mini App ---------\
Web ---------------\
Android ------------> Clinicos API -> Core Platform
iOS ----------------/

Client-specific UX is allowed.

Client-specific business logic is not.

⸻

11. Unified Identity Architecture

Clinicos must separate a person’s identity from their channel identities.

Conceptually:

Person
  |
  +-- Telegram Identity
  |
  +-- Web Identity
  |
  +-- Android Identity
  |
  +-- iOS Identity

A person may have multiple channel identities.

The system must maintain a canonical internal identity.

⸻

12. Identity Model

The conceptual identity hierarchy is:

Person
    |
    +-- PersonProfile
    |
    +-- ChannelIdentity
            |
            +-- Telegram
            +-- Web
            +-- Android
            +-- iOS

Channel identity must not become the primary domain identity.

Telegram user IDs must not be used as universal patient IDs.

⸻

13. Tenant Architecture

Clinicos is multi-tenant at the logical architecture level.

The primary isolation boundary is:

Clinic / Tenant

Every tenant-owned resource must be associated with the correct tenant.

Tenant isolation must apply to:

* patients;
* staff;
* conversations;
* leads;
* appointments;
* follow-ups;
* knowledge;
* reports;
* analytics;
* AI context;
* files;
* audit logs;
* notifications;
* configurations.

Cross-tenant data access must be impossible through ordinary application paths.

⸻

14. Core Platform

The Core Platform contains the authoritative business capabilities of Clinicos.

Major domains include:

Identity
Clinic Management
Patient Intelligence
Conversation
Lead Management
Follow-Up
Appointments
Knowledge
Medical Safety
Communication
Notifications
AI
Facial Analysis
Analytics
Reporting
Automation
Audit
Observability

The exact implementation may evolve.

The domain boundaries must remain explicit.

⸻

15. Domain Ownership Principle

Each important business concept must have a clear source of truth.

Examples:

Appointment availability
    -> Appointment / Scheduling domain
Patient identity
    -> Identity domain
Consent
    -> Consent / Privacy domain
Medical safety state
    -> Medical Safety domain
Lead state
    -> Lead Management domain
Follow-up schedule
    -> Follow-Up Engine
Communication delivery state
    -> Communication Layer
Clinic configuration
    -> Clinic Management
AI execution metadata
    -> AI Layer
Analytics
    -> Analytics / Reporting

No domain may silently become the source of truth for another domain’s responsibilities.

⸻

16. Application Layer

The Application Layer coordinates business use cases.

It translates external requests into domain operations.

Examples:

CreateLead
ScheduleFollowUp
BookAppointment
CancelAppointment
SendPatientMessage
GeneratePatientSummary
RunFacialAnalysis
CreateSafetyEscalation
GenerateWeeklyReport

Application services must orchestrate domains rather than embed large amounts of domain logic.

⸻

17. Domain Layer

The Domain Layer owns business rules.

Examples:

Lead qualification rules
Follow-up lifecycle rules
Appointment rules
Consent rules
Safety rules
Patient state rules
Clinic policy rules
Communication rules

Domain logic must not depend directly on:

* Telegram SDKs;
* Gemini SDKs;
* HTTP transport;
* database implementation details;
* UI components.

⸻

18. Policy Layer

Policy determines whether an action is permitted.

This layer is especially important for:

* communication;
* follow-up;
* AI actions;
* medical safety;
* privacy;
* authorization;
* automation.

The architectural distinction is:

Business Intent
      |
Policy
      |
Allowed / Blocked / Requires Human
      |
Execution

AI must not bypass policy.

⸻

19. Communication Architecture

Communication is separated from business workflows.

The architecture is:

Business Domain
      |
Business Intent
      |
Communication Policy
      |
Message Composition
      |
Validation
      |
Channel Selection
      |
Communication Orchestrator
      |
Channel Adapter
      |
Provider

The Communication Layer is responsible for delivery.

It does not independently invent business workflows.

⸻

20. Communication Channel Abstraction

The communication system must support channel adapters.

Initial channel:

Telegram

Planned channels:

Telegram
Instagram
WhatsApp
SMS
Email
Web Chat
Mobile Push
In-App
Voice
Internal Staff Notifications

The presence of a channel in this list does not mean it must be implemented immediately.

⸻

21. Telegram Adapter

Telegram-specific implementation must be isolated.

Conceptually:

Communication Layer
        |
Telegram Adapter
        |
Telegram API

The Core Platform should not depend on Telegram-specific message structures.

⸻

22. Appointment Architecture

Appointments must have authoritative records.

AI must never invent:

* appointment availability;
* provider availability;
* clinic hours;
* appointment status;
* appointment confirmation;
* pricing;
* discounts.

The correct flow is:

User Request
    |
Appointment Domain
    |
Authoritative Availability
    |
Business Validation
    |
Appointment Action
    |
Communication

⸻

23. Dynamic Operational Truth

Dynamic operational facts must come from authoritative systems.

Examples:

* available appointment slots;
* current appointment status;
* actual clinic hours;
* actual provider availability;
* current structured prices;
* current discounts;
* payment status;
* delivery status.

RAG and AI memory must not be treated as authoritative sources for these facts.

⸻

24. AI Architecture

The AI architecture is:

AI-enabled Domain
       |
AI Orchestrator
       |
AI Governance
       |
AI Interface
       |
Gemini Adapter
       |
Google Gemini

Gemini is the only runtime AI provider.

⸻

25. Gemini Adapter

All Gemini-specific behavior must be isolated behind an adapter.

The adapter is responsible for:

* authentication;
* Gemini API requests;
* model selection within Gemini;
* request formatting;
* response parsing;
* provider-specific error handling;
* token or usage metadata;
* provider-specific configuration.

The rest of the application should depend on the internal AI interface rather than Gemini SDK types.

⸻

26. Gemini Model Selection

Clinicos may use multiple Gemini models for different workloads.

This is considered model specialization within a single provider.

For example:

Fast conversational task
        |
Suitable Gemini model
Complex reasoning task
        |
Suitable Gemini model
Vision task
        |
Suitable Gemini vision-capable Gemini model
Structured generation
        |
Suitable Gemini model

This is not multi-provider routing.

⸻

27. AI Provider Boundary

The AI boundary must be explicit.

The application must not contain provider-specific conditionals such as:

if provider == "openai"
if provider == "deepseek"
if provider == "qwen"
if provider == "openrouter"
if provider == "freellmapi"

The target architecture has one active provider:

Gemini

⸻

28. AI Failure Handling

Gemini failures must be handled without switching to another AI provider.

Supported mechanisms include:

* bounded retry;
* exponential backoff;
* timeout;
* circuit breaker;
* queueing;
* rate-limit handling;
* graceful degradation;
* deterministic templates;
* cached safe responses where appropriate;
* human handoff;
* task postponement.

The system must never interpret provider failure as permission to call another provider.

⸻

29. Graceful AI Degradation

When AI is unavailable, Clinicos should continue functioning where possible.

Examples:

Appointment confirmation
    -> deterministic template
Appointment cancellation
    -> deterministic workflow
Simple administrative response
    -> deterministic template
Human handoff
    -> staff workflow
AI-only complex analysis
    -> queue / retry / human escalation

The platform must degrade safely rather than silently fabricate an AI-generated result.

⸻

30. AI Orchestrator

The AI Orchestrator coordinates governed AI execution.

Responsibilities include:

* selecting the appropriate AI capability;
* preparing context;
* enforcing AI permissions;
* selecting an appropriate Gemini model;
* invoking tools;
* validating outputs;
* recording execution metadata;
* handling failures;
* enforcing safety constraints.

The orchestrator must not become a general-purpose uncontrolled autonomous agent.

⸻

31. AI Agents

Clinicos may contain specialized AI agents.

Examples:

Conversation Agent
Patient Intelligence Agent
Lead Agent
Follow-Up Agent
Knowledge Agent
Secretary Copilot
Reporting Agent
Facial Analysis Agent

Agents must operate within explicit permissions.

⸻

32. Agent Permission Model

Each agent must define:

Allowed Inputs
Allowed Tools
Allowed Actions
Forbidden Actions
Required Policies
Required Human Approval
Output Constraints
Audit Requirements

An AI agent must not receive unrestricted access to the entire platform.

⸻

33. Tool-Using AI

AI agents may use tools when required.

Examples:

get_patient_context()
get_appointment()
check_availability()
get_lead()
get_followup_state()
search_knowledge()
create_followup()
request_human_handoff()

Tools must enforce authorization independently.

AI instructions alone are not authorization.

⸻

34. AI Cannot Bypass Domain Authorization

The following is prohibited:

AI -> Database directly
AI -> unrestricted API
AI -> arbitrary appointment modification
AI -> arbitrary patient record access
AI -> unrestricted communication

The correct pattern is:

AI
 |
Governed Tool
 |
Authorization
 |
Policy
 |
Domain Operation

⸻

35. AI Context Architecture

AI context must be assembled from authoritative sources.

Conceptually:

User Message
    |
Conversation Context
    |
Patient Context
    |
Clinic Context
    |
Relevant Knowledge
    |
Current Operational Data
    |
Safety State
    |
Consent State
    |
AI Context Builder
    |
Gemini

Only context required for the task should be provided.

⸻

36. Context Minimization

AI requests must use data minimization.

The system should avoid sending unrelated:

* patient records;
* staff records;
* conversations;
* medical images;
* clinic data;
* financial information.

Context must be task-specific.

⸻

37. Prompt Injection Defense

External content must be treated as untrusted.

Potentially untrusted content includes:

* patient messages;
* forwarded messages;
* uploaded documents;
* knowledge documents;
* web content;
* imported text;
* user-provided instructions.

Untrusted content must not redefine:

* system instructions;
* authorization;
* safety policy;
* tool permissions;
* tenant boundaries;
* privacy constraints.

⸻

38. AI Output Validation

AI output must be validated before execution.

Validation may include:

Schema validation
Safety validation
Authorization validation
Business-rule validation
Fact validation
Language validation
Content policy validation
Action validation

For structured actions, schema validity alone is not sufficient.

⸻

39. AI Hallucination Prevention

Clinicos must not rely on model confidence as proof of truth.

For important operational facts:

AI claim
    |
Authoritative source lookup
    |
Validation
    |
Final response

For example:

AI: "You have an appointment tomorrow at 5 PM."
Not sufficient.
System:
Appointment database -> verifies appointment
Then:
Communication -> sends verified information.

⸻

40. Medical Safety Architecture

Medical Safety is a first-class domain.

The safety hierarchy is:

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
Commercial Optimization

Commercial goals must never override safety.

⸻

41. Medical Safety Boundary

AI must not independently establish medical truth where authoritative clinical judgment is required.

The system must distinguish between:

Educational Information
Clinical Decision Support
Medical Safety Escalation
Diagnosis
Treatment Decision
Emergency Communication

High-risk situations must trigger appropriate human or clinical escalation.

⸻

42. Facial Analysis Architecture

Facial analysis is an independent governed capability.

Conceptually:

Image Upload
     |
Image Validation
     |
Consent / Privacy Check
     |
Facial Analysis Pipeline
     |
AI / Vision Processing
     |
Structured Findings
     |
Safety / Quality Validation
     |
User-facing Result

The system must clearly distinguish:

Observed image characteristics

from:

Medical diagnosis

⸻

43. Patient Intelligence

Patient Intelligence aggregates authorized information into useful operational context.

Possible inputs:

Identity
Conversation
Lead history
Appointment history
Follow-up history
Preferences
Consent
Interaction history
Relevant knowledge
Safety state

Patient Intelligence must not become an unrestricted data lake accessible to every AI component.

⸻

44. Conversation Architecture

The Conversation domain owns conversational state.

It is responsible for:

* inbound messages;
* conversation sessions;
* normalized user input;
* intent;
* conversation context;
* AI response orchestration;
* human takeover;
* conversation state.

Communication owns transport and delivery metadata.

Conversation owns conversational meaning.

⸻

45. Conversation vs Communication

These responsibilities must remain separate.

Conversation:
"What does the user mean?"
Communication:
"How was the message delivered?"

For example:

Conversation:
User requests appointment.
Appointment:
Checks availability.
Communication:
Sends appointment confirmation through Telegram.

⸻

46. Lead Management

Lead Management owns the lead lifecycle.

Examples:

New
Qualified
Contacted
Interested
Booked
Converted
Lost
Reactivated

AI may assist lead qualification and prioritization.

AI does not override lead-domain state transitions.

⸻

47. Follow-Up Engine

The Follow-Up Engine owns future communication intentions.

Conceptually:

Trigger
   |
Follow-Up Policy
   |
Validation
   |
Schedule
   |
Pre-send Revalidation
   |
Communication

A scheduled follow-up is not permanent authorization.

Consent, safety, ownership, frequency, and operational conditions must be revalidated before execution.

⸻

48. Notification Architecture

Notifications are delivered through the Communication Layer.

Notification generation must remain separate from transport.

Notification Intent
      |
Policy
      |
Message
      |
Communication Layer
      |
Channel Adapter

⸻

49. Knowledge Architecture

The Knowledge domain manages structured and unstructured clinic knowledge.

Possible sources include:

* clinic FAQs;
* approved service descriptions;
* approved educational material;
* internal procedures;
* policies;
* staff documentation.

Knowledge retrieval may support AI.

Knowledge retrieval must not override authoritative operational systems.

⸻

50. RAG Boundary

RAG is appropriate for:

* approved informational content;
* clinic documentation;
* educational knowledge;
* policies;
* FAQs.

RAG is not authoritative for:

* live appointment availability;
* current appointment status;
* current provider availability;
* current payment state;
* current delivery state;
* dynamic transactional facts.

⸻

51. Automation Architecture

Automation is event-driven.

Conceptually:

Domain Event
    |
Event Bus / Event Dispatcher
    |
Automation Rules
    |
Policy Validation
    |
Action

Automation must be idempotent.

⸻

52. Event Architecture

Events represent facts that have already occurred.

Examples:

patient.created
lead.created
lead.updated
appointment.created
appointment.confirmed
appointment.cancelled
appointment.completed
followup.created
followup.sent
message.received
message.delivered
safety.escalated

Events must not be confused with commands.

⸻

53. Commands vs Events

Command:

"Create an appointment."

Event:

"Appointment was created."

Commands request actions.

Events record facts.

⸻

54. Outbox Pattern

Important domain events should use an outbox pattern where appropriate.

Conceptually:

Transaction
    |
Database Change
    |
Outbox Event
    |
Event Dispatcher
    |
Consumers

This reduces the risk of losing events between database commits and event publication.

⸻

55. Idempotency

Important operations must support idempotency.

Examples:

* message sending;
* appointment creation;
* follow-up creation;
* webhook processing;
* event consumption;
* automation execution;
* report generation.

Repeated delivery must not create unintended duplicate business effects.

⸻

56. Data Architecture

The database is a system of record for platform state.

The database must enforce:

* tenant ownership;
* referential integrity;
* uniqueness;
* required fields;
* lifecycle constraints where appropriate;
* auditability;
* transactional consistency.

⸻

57. Database Independence

Business logic must not become inseparable from a specific database implementation.

PostgreSQL is the expected primary relational database technology unless explicitly changed by an authoritative architecture decision.

Application architecture should still preserve appropriate persistence boundaries.

⸻

58. Redis

Redis may be used for:

* caching;
* distributed locks;
* rate limiting;
* queues where appropriate;
* temporary state;
* idempotency keys;
* short-lived coordination.

Redis must not become the authoritative long-term source of critical business truth.

⸻

59. File and Media Storage

Files and media must be handled through controlled storage abstractions.

Examples:

Medical images
Patient documents
Generated reports
Clinic assets
Knowledge files
Communication media

Sensitive files require:

* authorization;
* tenant isolation;
* controlled access;
* appropriate retention;
* secure URLs or equivalent access controls;
* auditability.

⸻

60. API Layer

The API Layer exposes platform capabilities to clients and integrations.

It should support:

Authentication
Authorization
Request validation
Rate limiting
Tenant resolution
Request normalization
Response formatting
Error handling
Observability

⸻

61. API Design Principle

APIs should represent platform capabilities rather than client-specific implementation details.

Bad:

/telegram/create-followup

Preferred:

/followups

Telegram-specific behavior belongs in the Telegram adapter.

⸻

62. Client-Specific Endpoints

Client-specific endpoints may exist when genuinely necessary.

However, they must still delegate to shared application and domain logic.

A Telegram-specific endpoint must not create an alternative business implementation.

⸻

63. Authentication

Authentication identifies the caller.

Authorization determines what the caller may do.

These concepts must remain separate.

⸻

64. Authorization

Authorization must be enforced server-side.

Roles may include:

Patient
Secretary
Doctor
Owner
Manager
Administrator

Permissions must be granular enough to protect sensitive operations.

⸻

65. Staff Architecture

Staff users operate within a tenant.

Staff permissions should be based on:

Role
Permission
Tenant
Resource Ownership
Action Sensitivity
Clinical Context

AI must respect the same authorization boundaries.

⸻

66. Audit Architecture

Important actions must generate audit records.

Examples:

* patient access;
* record modification;
* appointment modification;
* consent change;
* communication;
* AI action;
* staff override;
* safety escalation;
* permission change;
* configuration change.

Audit records must be tamper-resistant and tenant-aware.

⸻

67. Observability Architecture

The platform must provide:

Logs
Metrics
Traces
Audit Events
AI Execution Records
Communication Delivery Records
Error Records

Important requests should have correlation identifiers.

⸻

68. AI Observability

AI execution should record appropriate metadata such as:

Request ID
Tenant
Agent
Task
Gemini Model
Latency
Token / usage metadata where available
Tool Calls
Validation Result
Outcome
Error Category
Human Intervention

Sensitive prompt and response content must be handled according to privacy policy.

⸻

69. Communication Observability

Communication should record:

Communication ID
Tenant
Recipient
Intent
Channel
Provider Message ID
Created At
Scheduled At
Sent At
Delivered At
Read At where available
Failure Reason
Retry Count
Final State

Transport status must not be confused with business success.

⸻

70. Reliability Architecture

Reliability mechanisms include:

Timeouts
Retries
Backoff
Circuit Breakers
Queues
Dead Letter Handling
Idempotency
Deduplication
Rate Limiting
Backpressure
Health Checks
Graceful Degradation
Recovery Procedures

Retries must always be bounded.

⸻

71. No Infinite Retry

No operation may retry indefinitely.

Every retryable operation must define:

Maximum Attempts
Backoff Strategy
Retryable Errors
Non-Retryable Errors
Final Failure State
Recovery Path

⸻

72. Provider Rate Limits

Gemini API limits must be handled explicitly.

The AI Layer must implement appropriate:

* request throttling;
* concurrency controls;
* retry behavior;
* queueing;
* backpressure;
* usage monitoring.

Provider limits must not be solved through provider switching.

⸻

73. Security Architecture

Security must be layered.

Required controls include:

Authentication
Authorization
Tenant Isolation
Encryption
Secret Management
Input Validation
Output Validation
Rate Limiting
Audit Logging
Secure File Access
Webhook Verification
Prompt Injection Defense
Abuse Protection

⸻

74. Secret Management

Secrets must never be embedded in:

* source code;
* client applications;
* prompts;
* logs;
* Git repositories;
* documentation.

Examples:

Gemini API key
Telegram bot token
Database credentials
Redis credentials
Storage credentials

Secrets must be injected through secure configuration mechanisms.

⸻

75. Gemini Credential Boundary

Only trusted server-side infrastructure may access Gemini credentials.

The following is prohibited:

Mobile Client -> Gemini API Key
Web Browser -> Gemini API Key
Mini App -> Gemini API Key
Telegram User -> Gemini API Key

⸻

76. Privacy Architecture

Privacy must be enforced through:

Data Minimization
Purpose Limitation
Access Control
Tenant Isolation
Retention Policies
Consent Management
Secure Storage
Secure Transmission
Auditability
Controlled AI Context

⸻

77. Consent Architecture

Consent must be explicit and contextual.

Relevant consent may include:

Communication Consent
Marketing Consent
Data Processing Consent
Medical Image Consent
AI Processing Consent
Channel Consent

Unknown consent must not be interpreted as positive marketing permission.

⸻

78. Consent Revocation

Consent changes must be respected by future operations.

Scheduled workflows must re-check relevant consent before execution.

Historical records may remain auditable according to retention requirements.

⸻

79. Human-in-the-Loop Architecture

Human staff must be able to take control of appropriate workflows.

Examples:

AI conversation -> human takeover
AI lead qualification -> staff review
AI medical safety escalation -> clinical review
AI follow-up -> staff approval
AI-generated report -> staff review

Human ownership must prevent conflicting AI automation where appropriate.

⸻

80. Human Takeover

When a conversation is assigned to a human:

AI automation
     |
     X
Human Owner
     |
Communication

AI must not silently continue autonomous communication that conflicts with human ownership.

⸻

81. AI Approval Modes

AI-powered operations may support:

AUTO
STAFF_APPROVAL
STAFF_ONLY
DISABLED

The approval mode is determined by risk and clinic policy.

⸻

82. High-Risk AI Actions

Higher-risk actions require stronger controls.

Examples:

* medical safety communication;
* treatment-related recommendations;
* sensitive patient record modification;
* external communication with clinical implications;
* irreversible business actions.

These actions may require human approval or deterministic workflows.

⸻

83. Business Workflow Architecture

Canonical workflow pattern:

Trigger
   |
Understand
   |
Check State
   |
Check Authorization
   |
Check Consent
   |
Check Safety
   |
Apply Business Policy
   |
Execute Domain Operation
   |
Communicate
   |
Observe
   |
Audit

AI may assist at specific stages but does not replace governance.

⸻

84. Lead-to-Conversion Workflow

Conceptually:

Inbound Message
      |
Conversation
      |
Intent Detection
      |
Lead Creation / Update
      |
Qualification
      |
Human / AI Assistance
      |
Follow-Up Policy
      |
Communication
      |
Appointment
      |
Conversion

Each domain owns its state.

⸻

85. Appointment Workflow

Conceptually:

Patient Request
      |
Conversation
      |
Appointment Intent
      |
Availability Tool
      |
Appointment Policy
      |
Appointment Creation
      |
Confirmation
      |
Follow-Up / Reminder
      |
Appointment Completion

AI cannot invent availability.

⸻

86. Safety Escalation Workflow

Conceptually:

Patient Message
      |
Conversation AI
      |
Safety Detection
      |
Medical Safety Domain
      |
Risk Classification
      |
Human / Clinical Escalation
      |
Controlled Communication
      |
Audit

Safety decisions must not depend solely on commercial automation.

⸻

87. Reporting Architecture

Reporting should use authoritative platform data.

Examples:

Weekly Clinic Report
Lead Conversion Report
Appointment Report
Follow-Up Performance
Communication Report
AI Performance Report
Operational Report

AI may summarize reports.

AI must not fabricate the underlying metrics.

⸻

88. Analytics Architecture

Analytics should distinguish:

Raw Operational Data
Derived Metrics
AI-generated Interpretation
Human Interpretation

AI-generated interpretation must not overwrite authoritative measurements.

⸻

89. AI Evaluation

AI performance must be measurable.

Potential dimensions:

Accuracy
Safety
Groundedness
Tool Correctness
Instruction Following
Latency
Cost
Failure Rate
Human Override Rate
Escalation Rate
User Feedback

Evaluation results must remain distinguishable from production business truth.

⸻

90. Model Governance

Because Gemini is the only active provider, model governance focuses on:

* Gemini model selection;
* model version tracking;
* capability mapping;
* prompt versioning;
* tool versioning;
* evaluation;
* regression testing;
* cost monitoring;
* latency monitoring;
* safety evaluation.

⸻

91. Gemini Model Versioning

Every AI execution should be traceable to the Gemini model configuration used.

Model configuration should be centrally managed.

Application code should avoid scattering model names throughout business logic.

⸻

92. Prompt Versioning

Production prompts must be versioned.

Each AI execution should be attributable to:

Prompt Version
Agent Version
Tool Version
Model
Policy Version

This enables reproducibility and regression analysis.

⸻

93. Knowledge Versioning

Knowledge used by AI should be traceable where appropriate.

Important metadata may include:

Knowledge Source
Document Version
Chunk Version
Retrieval Timestamp
Knowledge Scope
Tenant

⸻

94. Workflow Versioning

Long-running workflows should preserve the relevant workflow version.

A scheduled workflow must not silently change behavior because of an unrelated code or policy deployment unless explicitly designed to do so.

⸻

95. Configuration Architecture

Configuration should be separated into:

Platform Configuration
Tenant Configuration
Feature Configuration
AI Configuration
Communication Configuration
Security Configuration
Operational Configuration

Secrets must remain separate from ordinary configuration.

⸻

96. Feature Flags

Feature flags may be used for:

* staged rollout;
* beta capabilities;
* channel activation;
* AI capabilities;
* experimental workflows;
* clinic-specific features.

Feature flags must not be used to hide architectural violations.

⸻

97. Integration Architecture

External integrations must be isolated behind adapters.

Examples:

Telegram Adapter
Gemini Adapter
Payment Adapter
Calendar Adapter
Storage Adapter
Email Adapter
SMS Adapter

External provider-specific details must not leak into core domains.

⸻

98. Integration Failure

External integration failure must not corrupt domain state.

The system should distinguish:

Business Operation Success

from:

External Delivery Success

For example:

Appointment created successfully
+
Telegram confirmation failed

The appointment remains created.

The communication failure is handled separately.

⸻

99. Webhook Architecture

Inbound webhooks must be:

* authenticated or verified;
* validated;
* idempotent;
* observable;
* tenant-aware where applicable.

Repeated webhook delivery must not cause repeated business effects.

⸻

100. Background Jobs

Long-running or asynchronous operations should use background workers where appropriate.

Examples:

AI processing
Report generation
Follow-up scheduling
Message delivery
Media processing
Analytics aggregation
Knowledge indexing
Webhook processing

⸻

101. Queue Architecture

Queues should be used where asynchronous processing improves reliability.

Important queues may include:

AI Tasks
Communication Tasks
Follow-Up Tasks
Media Tasks
Report Tasks
Event Processing

Queue consumers must support idempotency.

⸻

102. Priority Architecture

Not all jobs have equal priority.

Priority may depend on:

Medical Safety
User Interaction
Appointment Operations
Human Staff Requests
Transactional Communication
Routine Automation
Analytics
Background Maintenance

Safety-related operations must not be starved by commercial workloads.

⸻

103. Backpressure

The system must apply backpressure when:

* Gemini is rate limited;
* communication providers are unavailable;
* queues grow excessively;
* database capacity is constrained;
* workers are overloaded.

Backpressure is preferable to uncontrolled concurrency.

⸻

104. Circuit Breakers

Circuit breakers should protect the platform from repeatedly calling failing external systems.

Potential protected integrations include:

Gemini
Telegram
Storage
External APIs

Circuit breakers must support recovery and observability.

⸻

105. Caching

Caching may improve performance.

However:

Cached data != authoritative truth

Dynamic operational information must be refreshed according to its consistency requirements.

⸻

106. Cache Safety

Sensitive tenant data must never be cached without appropriate isolation.

Cache keys must include sufficient tenant and resource context.

Cross-tenant cache collisions must be impossible.

⸻

107. Database Transaction Boundaries

Operations affecting multiple related records should use appropriate transactional boundaries.

Examples:

Appointment creation
Consent update
Lead state transition
Follow-up scheduling
Configuration changes

Distributed operations must use appropriate consistency patterns rather than assuming a global transaction.

⸻

108. Data Lifecycle

Data must have defined lifecycle policies.

Examples:

Creation
Active Use
Archival
Retention
Deletion
Anonymization where appropriate

Sensitive data must not be retained indefinitely without justification.

⸻

109. Deletion Architecture

Deletion requests must respect:

* legal requirements;
* audit requirements;
* retention rules;
* tenant policy;
* data dependencies;
* backup lifecycle.

Deletion must not create inconsistent references.

⸻

110. Disaster Recovery

The platform must define:

Backup Strategy
Recovery Objectives
Database Recovery
File Recovery
Configuration Recovery
Secret Recovery
Queue Recovery
Event Recovery
Operational Runbooks

⸻

111. Business Continuity

If Gemini becomes unavailable, the clinic should retain access to core deterministic operations where possible.

Examples:

View appointments
Manage patient records
Review leads
Perform staff actions
Send deterministic transactional messages
Review reports

AI-dependent operations may be delayed or escalated.

⸻

112. Deployment Architecture

The target architecture must support cloud deployment.

A modular monolith is acceptable during early development if logical boundaries are preserved.

The system does not require premature microservices.

⸻

113. Modular Monolith Principle

Early Clinicos deployment may be:

Single Application
    |
    +-- Identity Module
    +-- Patient Module
    +-- Conversation Module
    +-- Lead Module
    +-- Follow-Up Module
    +-- Appointment Module
    +-- Knowledge Module
    +-- Safety Module
    +-- Communication Module
    +-- AI Module
    +-- Analytics Module

Modules must communicate through defined interfaces.

⸻

114. Future Service Extraction

A module may later become an independent service if justified by:

* scale;
* reliability;
* deployment independence;
* team ownership;
* security boundary;
* performance requirements.

Service extraction must preserve domain ownership.

⸻

115. Microservice Restraint

Microservices are not a goal by themselves.

Clinicos should prefer:

Clear Boundaries
+
Strong Contracts
+
Simple Deployment

over unnecessary distributed complexity.

⸻

116. Infrastructure Components

A representative deployment may contain:

Application Server
PostgreSQL
Redis
Object Storage
Background Worker
Scheduler
Monitoring
Log Aggregation
Secret Management

Exact infrastructure vendors are implementation decisions unless explicitly fixed elsewhere.

⸻

117. Environment Architecture

At minimum:

Development
Staging
Production

Environments must be isolated.

Production credentials must never be used in development.

⸻

118. Configuration by Environment

Environment-specific configuration must not be hardcoded.

Examples:

Database URL
Redis URL
Gemini credential
Telegram credential
Storage configuration
Logging configuration
Feature flags

⸻

119. Production Safety

Production deployment should include:

* health checks;
* startup validation;
* migration control;
* rollback capability;
* monitoring;
* alerting;
* secret validation;
* dependency checks.

⸻

120. Migration Architecture

Database migrations must be:

* versioned;
* reviewable;
* reversible where practical;
* tested;
* production-aware.

Schema changes must not silently invalidate existing domain data.

⸻

121. API Versioning

Public APIs should support controlled evolution.

Breaking changes require explicit versioning or migration strategies.

Internal APIs may evolve more quickly but must preserve module contracts.

⸻

122. Error Architecture

Errors should be classified.

Examples:

Validation Error
Authorization Error
Not Found
Conflict
Business Rule Violation
External Integration Error
AI Error
Rate Limit
Timeout
System Error

Errors must not expose secrets or sensitive internals.

⸻

123. User-Facing Error Handling

Users should receive clear, safe messages.

The platform should not expose:

* stack traces;
* API keys;
* internal prompts;
* database details;
* infrastructure credentials;
* internal service topology.

⸻

124. AI Error Handling

AI errors should be mapped into controlled application outcomes.

Examples:

Gemini timeout
    -> retry / queue / human fallback
Gemini rate limit
    -> backoff / queue
Invalid structured output
    -> validation failure / retry / human review
Unsafe output
    -> block / escalate
Missing authoritative data
    -> do not fabricate

⸻

125. Observability Correlation

A cross-domain request should be traceable.

Example:

Request ID
    |
Conversation ID
    |
Patient ID
    |
AI Execution ID
    |
Tool Call ID
    |
Appointment Operation ID
    |
Communication ID
    |
Provider Message ID

This enables complete debugging without mixing domain ownership.

⸻

126. Logging

Logs should contain sufficient operational context without unnecessary sensitive data.

Structured logging is preferred.

Logs should support:

Search
Filtering
Correlation
Alerting
Incident Investigation

⸻

127. Metrics

Important metrics may include:

API latency
Error rate
Queue depth
Gemini latency
Gemini error rate
Gemini usage
Communication delivery rate
Follow-up completion
Appointment conversion
Lead conversion
Human takeover
Safety escalations
Database latency
Worker utilization

⸻

128. Alerting

Alerts should focus on actionable conditions.

Examples:

Gemini outage
High AI error rate
Telegram delivery degradation
Queue backlog
Database failure
High safety escalation failure
Communication failure spike
Cross-tenant access anomaly

⸻

129. Testing Architecture

Testing must occur at multiple levels.

Unit Tests
Domain Tests
Integration Tests
API Tests
AI Tests
Security Tests
Workflow Tests
End-to-End Tests
Load Tests
Failure Tests
Recovery Tests

⸻

130. Domain Testing

Business rules must be testable without external providers.

Examples:

Consent rules
Follow-up rules
Appointment rules
Lead state transitions
Authorization
Tenant isolation
Safety policies

⸻

131. AI Testing

AI testing must include:

Prompt Regression
Structured Output Validation
Groundedness
Tool Selection
Tool Argument Validation
Safety
Prompt Injection
Multilingual Behavior
Failure Handling
Model Regression

⸻

132. Gemini Testing

Gemini integration tests should verify:

* authentication;
* model configuration;
* timeout handling;
* retry behavior;
* structured outputs;
* error mapping;
* usage tracking;
* rate-limit handling.

Tests must not introduce alternate runtime providers.

⸻

133. Communication Testing

Communication tests should cover:

Consent
Opt-out
Quiet Hours
Frequency Limits
Duplicate Prevention
Channel Selection
Provider Errors
Retries
Delivery State
Webhook Reconciliation
Human Takeover

⸻

134. Tenant Isolation Testing

Security tests must attempt to verify that:

Tenant A cannot access Tenant B data.

This must be tested across:

* APIs;
* database queries;
* caches;
* files;
* AI context;
* search;
* analytics;
* background jobs;
* events;
* communications.

⸻

135. End-to-End Testing

Representative workflows should be tested end-to-end.

Example:

Telegram Message
    |
Conversation
    |
Lead
    |
Follow-Up
    |
Appointment
    |
Communication
    |
Delivery
    |
Analytics

⸻

136. AI End-to-End Testing

AI workflows should verify:

User Input
    |
Context Assembly
    |
Policy
    |
Gemini
    |
Tool Use
    |
Validation
    |
Domain Action
    |
Communication
    |
Audit

⸻

137. Security Testing

Security testing should include:

* authentication bypass;
* authorization bypass;
* tenant isolation;
* prompt injection;
* malicious file input;
* webhook spoofing;
* credential leakage;
* rate-limit abuse;
* data exposure;
* insecure direct object references.

⸻

138. Performance Testing

Performance testing should cover:

Concurrent Users
Concurrent Telegram Messages
AI Request Bursts
Communication Bursts
Appointment Traffic
Large Knowledge Searches
Media Processing
Reporting
Queue Backlogs

⸻

139. Scalability

The architecture should scale by improving:

Application Capacity
Worker Capacity
Queue Capacity
Database Capacity
Cache Capacity
Storage Capacity
External API Capacity

Scaling should not require rewriting business domains.

⸻

140. Horizontal Scaling

Stateless application components should be horizontally scalable where practical.

Shared state should be stored in appropriate centralized infrastructure.

⸻

141. Session Architecture

Application instances should not rely on local memory for durable session state.

Session state should use appropriate persistence or distributed mechanisms.

⸻

142. Background Worker Scaling

Workers should be independently scalable.

Examples:

AI Workers
Communication Workers
Automation Workers
Media Workers
Reporting Workers

Priority and backpressure must remain enforced.

⸻

143. Scheduler Architecture

Scheduled tasks must be resilient to:

* duplicate execution;
* process restart;
* clock changes;
* timezone differences;
* delayed execution;
* missed execution.

Schedulers must use durable state where required.

⸻

144. Time and Timezone

All time-sensitive operations must use explicit timezone semantics.

Tenant and user timezone preferences should be represented explicitly where relevant.

Scheduling must not assume server-local time.

⸻

145. Localization Architecture

The platform must support:

Persian
English
Azerbaijani
Arabic
Turkish

Language support must be centralized.

⸻

146. RTL Architecture

Right-to-left languages must be supported at presentation and communication layers.

The Core Platform must store language-neutral structured state.

⸻

147. Multilingual AI

Gemini may operate across supported languages.

The system should preserve:

* user language preference;
* clinic language preference;
* conversation language;
* explicit user switching;
* code-switching behavior where appropriate.

⸻

148. Brand and Tone

Clinic-specific communication style may be configurable.

However, tone customization must not override:

* safety;
* privacy;
* consent;
* factual correctness;
* legal constraints;
* human ownership.

⸻

149. Ethical Communication

Clinicos must prohibit communication patterns involving:

* deception;
* fabricated scarcity;
* fabricated social proof;
* false urgency;
* fear-based manipulation;
* guilt-based manipulation;
* misleading medical claims.

Commercial optimization must remain subordinate to safety and consent.

⸻

150. Operational Truth Boundary

The following architecture rule is mandatory:

LLM Memory
    !=
System of Record

Gemini may reason over data.

Gemini does not own platform truth.

⸻

151. Source-of-Truth Matrix

Domain	Authoritative Source
Identity	Identity Domain
Tenant	Clinic / Tenant Domain
Patient Record	Patient Domain
Conversation State	Conversation Domain
Lead State	Lead Management
Appointment	Appointment Domain
Availability	Scheduling / Authoritative Availability
Follow-Up	Follow-Up Engine
Consent	Consent / Privacy Domain
Safety State	Medical Safety
Knowledge	Knowledge Domain
Communication Delivery	Communication Layer
AI Execution	AI Layer
Facial Analysis Result	Facial Analysis Domain
Analytics	Analytics Domain
Audit	Audit System

⸻

152. Architectural Dependency Direction

Dependencies should generally flow inward.

Preferred:

Client
  |
API
  |
Application
  |
Domain
  |
Infrastructure

Infrastructure implementations should not redefine domain behavior.

⸻

153. AI Dependency Direction

Preferred:

Domain/Application
      |
AI Interface
      |
AI Governance
      |
Gemini Adapter
      |
Gemini

Not:

Domain
  |
Gemini SDK

⸻

154. Communication Dependency Direction

Preferred:

Domain
  |
Communication Intent
  |
Communication Layer
  |
Channel Adapter
  |
Provider

Not:

Domain
  |
Telegram SDK

⸻

155. Repository Architecture

The repository should reflect logical architecture.

A representative structure may be:

app/
  api/
  application/
  domain/
    identity/
    clinic/
    patients/
    conversations/
    leads/
    followups/
    appointments/
    knowledge/
    safety/
    communication/
    notifications/
    analytics/
    reporting/
    facial_analysis/
  ai/
    interfaces/
    orchestrator/
    agents/
    tools/
    gemini/
  infrastructure/
    database/
    redis/
    storage/
    queues/
    scheduling/
  integrations/
    telegram/
    ...
  observability/
  security/

The exact repository structure may differ.

The architectural boundaries must remain recognizable.

⸻

156. Telegram Boundary

Telegram implementation should be contained within:

integrations/telegram/

or an equivalent isolated boundary.

Telegram-specific concepts must not propagate into domain models.

⸻

157. Gemini Boundary

Gemini implementation should be contained within:

ai/gemini/

or an equivalent isolated boundary.

Gemini-specific SDK objects must not become general application data types.

⸻

158. Adapter Principle

Adapters translate external representations into internal representations.

Example:

Telegram Update
    |
Telegram Adapter
    |
Normalized Message

and:

AI Request
    |
Gemini Adapter
    |
Gemini API Request

⸻

159. Anti-Corruption Boundary

External systems must not redefine Clinicos domain models.

External identifiers may be stored as integration metadata.

They must not become the primary business identity unless explicitly required.

⸻

160. API Contract Principle

API contracts should expose stable domain capabilities.

They should avoid exposing:

* database schemas;
* Gemini request structures;
* Telegram update payloads;
* provider-specific implementation details.

⸻

161. Data Transfer Objects

DTOs should be used at appropriate boundaries.

Examples:

TelegramMessageDTO
CreateLeadRequest
AppointmentResponse
AIExecutionRequest
CommunicationRequest

DTOs should not be mistaken for domain entities.

⸻

162. Domain Events

Domain events should describe meaningful business facts.

Examples:

LeadQualified
AppointmentBooked
AppointmentCompleted
FollowUpScheduled
PatientConsentRevoked
SafetyEscalated

⸻

163. Integration Events

External events should be normalized before entering the Core Platform.

Example:

Telegram Update
    |
Telegram Integration
    |
Normalized Message Received
    |
Conversation Domain

⸻

164. AI Events

AI-specific events may include:

ai.execution.started
ai.execution.completed
ai.execution.failed
ai.tool.called
ai.validation.failed
ai.human_review_required

These events are observability and governance mechanisms.

⸻

165. Communication Events

Communication events may include:

communication.created
communication.approved
communication.scheduled
communication.sending
communication.sent
communication.delivered
communication.read
communication.failed
communication.cancelled
communication.blocked
communication.suppressed

⸻

166. Event Ordering

Consumers must not assume perfect event ordering.

Events may be:

* delayed;
* duplicated;
* retried;
* received out of order.

Consumers must reconcile state using timestamps, versions, or authoritative records where necessary.

⸻

167. Event Retention

Event retention should be determined by:

* operational requirements;
* analytics;
* audit requirements;
* privacy;
* storage cost.

Sensitive events require appropriate retention policies.

⸻

168. Architecture for Human Staff

Staff interfaces should consume the same Core Platform APIs.

Staff UI
    |
API
    |
Core Platform

Staff interfaces must not contain alternative business logic.

⸻

169. Secretary Copilot

Secretary Copilot is an AI-assisted capability.

It may help with:

* conversation summaries;
* lead summaries;
* suggested responses;
* follow-up suggestions;
* appointment context;
* administrative tasks.

It must respect staff permissions and clinic policies.

⸻

170. Doctor Workflow

Doctor-facing capabilities must prioritize:

* patient context;
* appointment context;
* clinical safety;
* relevant history;
* structured summaries.

AI suggestions must remain distinguishable from authoritative clinical records.

⸻

171. Owner / Manager Workflow

Owner and manager capabilities may include:

* clinic analytics;
* staff management;
* configuration;
* lead performance;
* appointment metrics;
* communication metrics;
* AI usage;
* operational reports.

Tenant isolation remains mandatory.

⸻

172. Patient Workflow

Patient-facing capabilities may include:

* conversation;
* appointment operations;
* follow-up;
* service information;
* consent;
* reports;
* facial analysis where enabled;
* communication preferences.

Patients must only access their authorized data.

⸻

173. Clinic Configuration

Clinic configuration may include:

Business Hours
Services
Providers
Communication Preferences
Follow-Up Policies
Branding
Languages
AI Approval Modes
Notification Policies

Configuration must not override platform-level safety constraints.

⸻

174. Policy Precedence

Where policies conflict, precedence must be explicit.

Recommended hierarchy:

Platform Safety
    >
Medical Safety
    >
Privacy
    >
Consent
    >
Authorization
    >
Regulatory / Legal Constraints
    >
Clinic Policy
    >
User Preference
    >
Commercial Optimization

⸻

175. No Silent Policy Override

No AI agent, automation, client, or integration may silently override policy.

Overrides must be:

* explicitly authorized;
* auditable;
* bounded;
* attributable.

⸻

176. Kill Switches

The platform should support emergency disabling of:

AI
Specific AI Agent
Specific Automation
Specific Communication Channel
Marketing Communication
Follow-Up Engine
Specific Clinic
Specific Feature

Kill switches must be observable and auditable.

⸻

177. Emergency Degradation

If a critical dependency fails, the system should move into a controlled degraded mode.

Example:

Gemini unavailable
    |
AI disabled
    |
Deterministic workflows remain active
    |
Human workflows remain active

⸻

178. Operational Runbooks

Important failure scenarios must have documented procedures.

Examples:

Gemini outage
Telegram outage
Database outage
Redis outage
Queue backlog
Storage outage
Data recovery
Security incident
Cross-tenant incident

⸻

179. Security Incident Architecture

Security incidents must support:

Detection
Containment
Investigation
Audit
Recovery
Post-Incident Review

Sensitive incidents must have appropriate escalation paths.

⸻

180. Data Breach Isolation

Tenant isolation mechanisms must allow investigation of:

Which tenant
Which resources
Which users
Which requests
Which AI executions
Which communications

were affected by an incident.

⸻

181. Cost Architecture

AI usage must be measurable.

The system should track appropriate Gemini usage metrics.

Cost optimization must not compromise:

* safety;
* correctness;
* privacy;
* required capability.

⸻

182. AI Cost Controls

Possible controls include:

Model Selection
Context Minimization
Caching
Prompt Optimization
Batching where appropriate
Usage Limits
Tenant Quotas
Task Classification

No alternate provider is used for cost optimization.

⸻

183. AI Latency Controls

Latency-sensitive workflows may use faster Gemini models where appropriate.

Latency optimization must preserve task quality and safety.

⸻

184. AI Capability Registry

The platform should maintain a conceptual registry mapping tasks to appropriate Gemini capabilities.

Example:

Task
  |
Required Capability
  |
Allowed Gemini Models
  |
Output Contract
  |
Safety Level
  |
Approval Mode

⸻

185. AI Task Classification

Before invoking Gemini, tasks may be classified into categories such as:

Conversation
Extraction
Classification
Summarization
Reasoning
Vision
Structured Generation
Report Generation

Task classification must not be used to bypass safety policy.

⸻

186. Structured AI Outputs

Where AI output drives system behavior, structured outputs should be preferred.

Example:

{
  "intent": "appointment_request",
  "confidence": 0.94,
  "required_action": "check_availability"
}

The exact schema depends on the use case.

The output must still be validated.

⸻

187. AI Confidence

Model-reported confidence must not be treated as authorization or truth.

Confidence may be used as one signal among others.

⸻

188. AI Action Boundary

AI should generally propose or invoke governed actions rather than directly manipulating infrastructure.

Preferred:

AI -> Tool -> Policy -> Domain

⸻

189. Autonomous Behavior Limits

AI autonomy must be explicitly bounded.

Every autonomous workflow should define:

Trigger
Scope
Allowed Actions
Forbidden Actions
Maximum Iterations
Time Limit
Cost Limit where appropriate
Safety Conditions
Human Escalation
Stop Conditions

⸻

190. Agent Loop Protection

Agents must not enter infinite loops.

Controls should include:

* maximum iterations;
* maximum tool calls;
* execution timeout;
* budget limits;
* repeated-action detection;
* state validation.

⸻

191. Automation Loop Protection

Event-driven automation must prevent:

Event A
 -> Automation
 -> Event B
 -> Automation
 -> Event A

from creating uncontrolled loops.

⸻

192. Communication Loop Protection

The system must prevent AI from responding indefinitely to its own generated messages.

Inbound and outbound messages must be distinguishable.

⸻

193. Human Message Attribution

Communication records must distinguish:

AI Generated
Human Generated
System Generated
Hybrid / Human Edited AI

This is important for auditability.

⸻

194. AI-to-Human Handoff

AI should escalate when:

* user requests a human;
* policy requires a human;
* medical safety requires a human;
* AI cannot safely complete the task;
* repeated failures occur;
* authorization is unclear;
* user intent is ambiguous in a high-risk context.

⸻

195. Human-to-AI Resume

AI automation may resume only when the relevant human ownership state permits it.

Resume events should be auditable.

⸻

196. Product Expansion Principle

New clients and channels must be additive.

The architecture should evolve:

Phase 1
Telegram
   |
Core Platform
Phase 2
Telegram + Mini App
   |
Core Platform
Phase 3
Telegram + Mini App + Web + Android + iOS
   |
Core Platform

The Core Platform should not be rewritten for each client.

⸻

197. Channel Expansion Principle

Adding a channel should primarily require:

Channel Adapter
+
Authentication / Identity Mapping
+
Capability Mapping
+
UI / Transport Implementation

It should not require rewriting:

* Lead Management;
* Follow-Up;
* Appointment;
* Patient Intelligence;
* Medical Safety;
* AI Orchestration.

⸻

198. Client Expansion Principle

Adding Web, Android, or iOS should not create separate patient, appointment, or lead databases.

All clients access shared platform state.

⸻

199. Multi-Channel Conversation

A future user may communicate through multiple channels.

The architecture should support:

Person
 |
Conversation Identity
 |
Multiple Channel Identities

The platform should preserve continuity where identity resolution and authorization permit it.

⸻

200. Cross-Channel Communication

Cross-channel fallback must never happen automatically merely because one channel fails.

The platform must verify:

Channel Consent
Authorization
Channel Availability
User Preference
Policy
Safety

before using another channel.

⸻

201. Mobile Architecture

Native or cross-platform mobile applications should act as clients.

They must communicate through authenticated APIs.

They must not replicate the Core Platform.

⸻

202. Web Architecture

The Web client should consume shared APIs.

Web-specific concerns may include:

* UI;
* routing;
* client state;
* accessibility;
* browser capabilities.

Business truth remains server-side.

⸻

203. Mini App Architecture

The Telegram Mini App should be considered a client application embedded within Telegram.

It must not become the Core Platform.

⸻

204. Client Security

Clients must never be trusted with:

* server secrets;
* unrestricted database access;
* unrestricted AI access;
* cross-tenant authority.

All sensitive operations must be authorized server-side.

⸻

205. API Rate Limiting

Rate limiting must exist at multiple boundaries where appropriate:

Client
User
Tenant
Endpoint
AI Task
Communication
Webhook

Rate limiting must be observable.

⸻

206. Abuse Prevention

The platform should detect and limit:

* spam;
* automated abuse;
* prompt flooding;
* AI resource exhaustion;
* communication flooding;
* malicious uploads;
* repeated invalid authentication attempts.

⸻

207. File Upload Security

Uploaded files must be:

* validated;
* size-limited;
* type-checked;
* safely stored;
* access-controlled;
* scanned where appropriate;
* isolated from executable paths.

⸻

208. Medical Image Security

Medical or aesthetic images require additional protection.

The system must ensure:

Explicit Access
Tenant Isolation
Consent Where Required
Secure Storage
Controlled Processing
Auditability
Retention Rules

⸻

209. Search Architecture

Search should respect:

Tenant
Role
Permission
Resource Ownership
Data Sensitivity

AI-assisted search must not bypass these filters.

⸻

210. Analytics Isolation

Analytics queries must enforce tenant boundaries.

Aggregated analytics must not accidentally expose identifiable data across tenants.

⸻

211. Reporting Isolation

Reports must be generated from authorized tenant data only.

Generated AI summaries must inherit the same data boundary.

⸻

212. Data Export

Authorized users may export appropriate tenant data.

Exports must:

* be authorized;
* be audited;
* respect privacy;
* use secure delivery;
* avoid unnecessary data exposure.

⸻

213. Backup Isolation

Backups must be protected with appropriate access controls.

Restoration procedures must preserve tenant boundaries.

⸻

214. Backup Testing

Backups must be periodically tested for restorability.

A backup that cannot be restored must not be treated as a reliable backup.

⸻

215. Recovery Point

Recovery objectives should be defined for important data classes.

Critical operational data should have stronger recovery requirements than temporary caches.

⸻

216. Recovery Ordering

A recovery sequence should prioritize:

Database
Core Application
Identity / Authorization
Queues
Communication
AI
Analytics

Exact ordering may depend on incident type.

⸻

217. AI During Recovery

AI should remain disabled or degraded until its dependencies and safety boundaries are verified.

AI should not become the first dependency required to restore core operations.

⸻

218. Communication During Recovery

Communication recovery must avoid duplicate messages.

Pending communication records must be reconciled before replay.

⸻

219. Event Replay

Event replay must be designed carefully.

Replay operations must respect:

Idempotency
Current State
Event Version
Tenant
Business Rules

⸻

220. Schema Evolution

Domain schemas must evolve through controlled migrations.

Event schemas should be versioned where necessary.

AI output schemas should also be versioned.

⸻

221. Backward Compatibility

Compatibility should be maintained where practical for:

* APIs;
* events;
* stored workflows;
* client versions;
* integrations.

Breaking changes require migration plans.

⸻

222. Architecture Documentation

Architecture decisions must be documented.

Important changes should include:

Decision
Reason
Impact
Affected Documents
Migration
Compatibility
Rollback

⸻

223. Architecture Decision Records

Significant architectural decisions should be captured as ADRs.

Examples:

Why Gemini-only
Why modular monolith
Why Telegram-first
Why channel abstraction
Why AI abstraction remains
Why domain-owned source of truth

⸻

224. Documentation Priority

The following hierarchy applies:

Architecture Change Set
    >
Master Vision
    >
Product Requirements
    >
Target Architecture
    >
Domain Specifications
    >
Implementation

If lower-level implementation conflicts with an authoritative architectural requirement, the implementation must be reviewed.

⸻

225. Historical Architecture

Historical implementation documents may contain useful migration information.

They must not be treated as the target architecture.

In particular, historical multi-provider AI designs are obsolete for the target architecture.

⸻

226. Explicitly Removed Architecture

The following are removed from the target architecture:

FreeLLMAPI
OpenRouter runtime routing
DeepSeek runtime provider
Qwen runtime provider
OpenAI runtime provider
Provider scoring
Provider score adjustment
Provider cooldown routing
AI provider fallback
Multi-provider failover

These concepts must not be reintroduced without an explicit architecture change.

⸻

227. Retained Architectural Abstraction

The following remains mandatory:

Internal AI Interface
Gemini Adapter
AI Orchestrator
AI Governance
Task-level Gemini model selection

The abstraction exists for maintainability and controlled evolution, not for active multi-provider routing.

⸻

228. Gemini Failure Boundary

Gemini failure is handled inside the AI reliability boundary.

Correct:

Gemini
  |
Failure
  |
AI Reliability
  |
Retry / Backoff / Queue / Degrade / Human

Incorrect:

Gemini
  |
Failure
  |
OpenRouter
  |
DeepSeek
  |
Qwen

⸻

229. AI Provider Replacement

The architecture should remain technically capable of replacing the Gemini adapter in the future.

However, no alternative provider is part of the current target runtime.

This distinction is important:

Replaceable Architecture
!=
Multi-Provider Runtime

⸻

230. Platform vs Provider

Clinicos owns:

Business Logic
Data
Policies
Agents
Tools
Workflows
Safety
Communication
Analytics
User Experience

Gemini provides:

AI Model Capability

Clinicos must remain the product.

⸻

231. Platform vs Client

Clinicos Core owns:

Business Truth
Authorization
Policies
AI Governance
Safety
Data
Workflows

Clients own:

Presentation
Interaction
Local UI State
Client-Specific UX

⸻

232. Platform vs Communication

Business domains decide:

WHY communicate

Communication Layer decides:

HOW to deliver

Channel adapters decide:

WHERE to deliver

Providers report:

WHAT happened

Audit records:

WHAT FACTUALLY OCCURRED

⸻

233. Platform vs AI

Business domains decide:

WHAT business operation exists

AI may assist with:

UNDERSTANDING
REASONING
GENERATION
CLASSIFICATION
SUMMARIZATION

Policy decides:

WHETHER the AI-proposed operation is permitted

Domain services execute:

THE ACTUAL BUSINESS OPERATION

⸻

234. Canonical Architecture

The final conceptual architecture is:

                        USERS
                          |
        +-----------------+------------------+
        |                 |                  |
     Telegram          Mini App         Web / Mobile
        |                 |                  |
        +-----------------+------------------+
                          |
                      API Layer
                          |
                  Authentication
                          |
                   Authorization
                          |
                Application Layer
                          |
        +-----------------+------------------+
        |                 |                  |
      Domains           Policies          Workflows
        |                 |                  |
        +-----------------+------------------+
                          |
                    AI Governance
                          |
                    AI Interface
                          |
                   Gemini Adapter
                          |
                   Google Gemini
                          |
        +-----------------+------------------+
        |                 |                  |
    PostgreSQL          Redis            Storage
        |                 |                  |
        +-----------------+------------------+
                          |
                 Event / Job System
                          |
        +-----------------+------------------+
        |                 |                  |
 Communication        Analytics         Observability
        |
 Channel Adapters
        |
 Telegram / Future Channels

⸻

235. Canonical Request Flow

A typical AI-assisted request follows:

1. User interacts with a client.
2. Client sends request to Clinicos API.
3. Authentication identifies the caller.
4. Authorization validates access.
5. Request is normalized.
6. Application service identifies the use case.
7. Relevant domain state is loaded.
8. Policies are evaluated.
9. AI is invoked only if appropriate.
10. AI context is constructed from authorized data.
11. Gemini executes the AI task.
12. Output is validated.
13. Tools may be invoked through governed interfaces.
14. Domain operations execute.
15. Communication is generated if required.
16. Communication policy is evaluated.
17. Message is delivered through the appropriate channel.
18. Events and audit records are produced.
19. Metrics and traces are recorded.

⸻

236. Canonical Non-AI Request Flow

Not every operation requires AI.

Example:

User
  |
Client
  |
API
  |
Authorization
  |
Application Service
  |
Appointment Domain
  |
Database
  |
Communication
  |
Channel Adapter

The system must not invoke Gemini unnecessarily.

⸻

237. Canonical AI Request Flow

User
  |
Client
  |
API
  |
Authorization
  |
Application Service
  |
AI Orchestrator
  |
Policy
  |
Context Builder
  |
Gemini Adapter
  |
Gemini
  |
Output Validation
  |
Tool / Domain Action
  |
Communication

⸻

238. Canonical Safety Flow

User Input
    |
Conversation
    |
Safety Detection
    |
Medical Safety
    |
Risk Assessment
    |
Policy
    |
Human / Clinical Escalation
    |
Controlled Communication
    |
Audit

⸻

239. Canonical Follow-Up Flow

Trigger
    |
Follow-Up Engine
    |
Policy
    |
Consent
    |
Safety
    |
Human Ownership
    |
Schedule
    |
Pre-Send Revalidation
    |
Message Generation
    |
Communication
    |
Delivery
    |
Observation

⸻

240. Canonical Multi-Channel Flow

Person
   |
Unified Identity
   |
Channel Identity
   |
Client / Channel
   |
Core Platform
   |
Business Domain
   |
Communication Layer
   |
Approved Channel

⸻

241. Architecture Non-Negotiables

The following rules are mandatory.

1. Gemini is the only active AI provider.
2. FreeLLMAPI is not part of the target architecture.
3. Multi-provider runtime routing is prohibited.
4. AI provider fallback is prohibited.
5. Internal AI abstraction remains mandatory.
6. Gemini-specific code must be isolated behind the AI boundary.
7. Clients must not call Gemini directly.
8. Telegram is the first client/channel, not the permanent platform boundary.
9. Telegram-specific logic must remain isolated.
10. Core business logic must remain client-independent.
11. Communication must remain channel-agnostic.
12. Dynamic operational truth must come from authoritative systems.
13. AI must not fabricate operational facts.
14. AI must not bypass authorization.
15. AI must not bypass consent.
16. AI must not bypass medical safety.
17. Tenant isolation must apply across all domains and infrastructure.
18. Human takeover must be supported where required.
19. Important operations must be observable and auditable.
20. Retries must be bounded.
21. Asynchronous processing must be idempotent.
22. Communication must prevent uncontrolled duplication.
23. Safety must take priority over commercial optimization.
24. Adding a new client must not require redesigning the Core Platform.
25. Adding a new channel must not require redesigning business domains.
26. Historical implementation must not override target architecture.
27. Architecture changes must be explicitly documented.

⸻

242. Migration Principle

Migration from the current repository to this architecture should be incremental.

The system should not be rewritten blindly.

Migration should proceed by:

Understand Current State
        |
Map Current Components
        |
Identify Conflicts
        |
Define Target Boundaries
        |
Introduce Interfaces
        |
Migrate Dependencies
        |
Remove Legacy Paths
        |
Test
        |
Deploy Incrementally

⸻

243. Legacy Isolation

Legacy code may temporarily remain if required for migration.

However:

Legacy Code
    !=
Target Architecture

Legacy provider routing or obsolete AI integrations must not become new dependencies.

⸻

244. Migration Priority

Migration priority should generally follow:

1. Security
2. Tenant Isolation
3. AI Provider Boundary
4. Core Domain Boundaries
5. Communication Boundary
6. Client Independence
7. Data Consistency
8. Observability
9. Reliability
10. Optimization

⸻

245. Architecture Validation

Before considering a major module complete, verify:

Does it have a clear owner?
Does it have a defined source of truth?
Does it respect tenant isolation?
Does it respect authorization?
Does it respect consent?
Does it respect medical safety?
Does it avoid direct provider coupling?
Does it avoid client-specific business logic?
Does it have observability?
Does it support failure handling?
Does it have tests?

⸻

246. Final Architecture Statement

Clinicos is a clinic operating platform with an AI-native architecture.

Its architecture is centered on a client-independent Core Platform.

Telegram is the initial client and communication channel.

Telegram Mini App is the second-stage client.

Web, Android, and iOS are later clients.

Google Gemini is the only active AI provider.

Gemini is accessed through a governed internal AI layer and isolated adapter.

The Core Platform owns business truth.

Domains own their respective state.

Policies determine whether actions are permitted.

AI assists with understanding, reasoning, generation, classification, and other bounded capabilities.

AI does not own business truth and does not bypass authorization, consent, safety, or domain rules.

Communication is separated from business workflows.

Channels are adapters rather than business domains.

Dynamic operational facts come from authoritative systems.

The platform is designed to evolve from a Telegram-first product into a multi-client clinic operating system without requiring a redesign of its core architecture.

The final architectural philosophy is:

CORE PLATFORM FIRST
CLIENTS SECOND
BUSINESS INTENT
        |
      POLICY
        |
     EXECUTION
        |
 COMMUNICATION
        |
     CHANNEL
GOVERNED AI
        |
   GEMINI ONLY
AUTHORITATIVE SYSTEMS
        |
    BUSINESS TRUTH
AI
        |
  REASONING + ASSISTANCE
SAFETY
        |
      FIRST
TENANT ISOLATION
        |
      ALWAYS

This architecture defines the target technical foundation of Clinicos.

Available next action: [Create a downloadable DOCX file here in this chat containing the editable prose above](chatgpt://followup-prompt?start_index=79695&end_index=79780)
