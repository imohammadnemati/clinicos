# CLINICOS API AND INTEGRATION SPEC
**Document:** CLINICOS_API_AND_INTEGRATION_SPEC.md  
**Version:** 2.0  
**Status:** Authoritative API and Integration Specification  
**Effective:** Immediately  
**Language:** English  
**Parent Documents:**
- CLINICOS_MASTER_VISION.md
- CLINICOS_PRODUCT_REQUIREMENTS.md
- CLINICOS_TARGET_ARCHITECTURE.md
- CLINICOS_AI_ENGINEERING_SPEC.md
- CLINICOS_SECURITY_AND_PRIVACY_SPEC.md
- CLINICOS_DATA_AND_DATABASE_SPEC.md
- CLINICOS_PLATFORM_GOVERNANCE_SPEC.md
---
# 1. Purpose
This document defines the target API, integration, communication, authentication, authorization, external-system, AI, event, webhook, and client-integration architecture of Clinicos.
It defines how Clinicos Core Platform communicates with:
- Telegram
- Telegram Mini App
- Web applications
- Android applications
- iOS applications
- Google Gemini
- external healthcare and operational systems
- payment systems
- notification providers
- future channel adapters
- internal services
- event infrastructure
- administrative tools
This document is an architectural specification.
It is not a direct description of the current repository implementation.
---
# 2. Architectural Authority
The target architecture defined here takes precedence over historical implementation decisions.
Historical integrations, providers, APIs, database structures, and communication mechanisms must not be treated as authoritative unless they are explicitly compatible with this specification.
If an existing implementation conflicts with this document, the implementation is considered legacy and must be migrated or replaced.
---
# 3. Core Architecture
Clinicos follows the following high-level architecture:
```text
Clients
    |
    v
API / Application Boundary
    |
    v
Clinicos Core Platform
    |
    +--------------------+
    |                    |
    v                    v
AI Layer             Domain Services
    |                    |
    v                    +--------------------+
Gemini Adapter           |                    |
    |                    v                    v
    v                Data Layer          Event Layer
Google Gemini

Communication channels remain separate from business-domain logic.

⸻

4. Core Architectural Principles

Clinicos APIs MUST follow these principles:

1. Clients communicate with Clinicos Core Platform through governed APIs.
2. Clients MUST NOT contain business-critical domain logic.
3. Clients MUST NOT directly call Gemini for governed workflows.
4. Clients MUST NOT directly access the database.
5. Clients MUST NOT directly access internal services.
6. Business domains remain the source of business truth.
7. The API layer exposes governed application capabilities.
8. Authorization MUST be enforced server-side.
9. Tenant isolation MUST be enforced server-side.
10. Medical safety policies MUST be enforced server-side.
11. Consent policies MUST be enforced server-side.
12. Dynamic operational facts MUST come from authoritative systems.
13. AI output MUST pass validation before causing side effects.
14. External providers MUST be isolated behind integration adapters.
15. Provider-specific behavior MUST NOT leak into domain logic.
16. API contracts MUST be versioned.
17. Side-effecting operations MUST be idempotent where applicable.
18. Webhooks MUST be authenticated and verified.
19. Integration failures MUST be observable.
20. API behavior MUST be auditable for sensitive operations.

⸻

5. API Architecture

Clinicos uses an application API boundary between clients and the Core Platform.

Conceptually:

Telegram Bot
Telegram Mini App
Web
Android
iOS
        |
        v
API Gateway / Application API
        |
        v
Authentication
        |
        v
Authorization
        |
        v
Application Services
        |
        v
Domain Services
        |
        v
Data / Event / Integration Layers

The exact transport technology may evolve.

The architectural contract must remain stable.

⸻

6. API Transport

The primary client-facing API SHOULD use HTTPS.

REST-style APIs SHOULD be the default for:

* authentication
* patient operations
* conversations
* leads
* appointments
* follow-ups
* notifications
* clinic management
* analytics
* reports
* settings
* AI operations

Other transports may be used where technically justified.

Examples include:

* WebSocket
* Server-Sent Events
* webhook callbacks
* asynchronous event delivery
* internal message queues

Transport choice MUST NOT move business logic into the transport layer.

⸻

7. HTTPS Requirement

All external API traffic MUST use HTTPS.

Plain HTTP MUST NOT be used for production authenticated traffic.

Sensitive information MUST NOT be transmitted over unencrypted transport.

⸻

8. API Base Structure

The API SHOULD follow a versioned structure such as:

/api/v1/

Future incompatible contracts SHOULD use:

/api/v2/

Versioning MUST be explicit.

Breaking changes MUST NOT silently modify the behavior of an existing API version.

⸻

9. API Versioning

API versions represent compatibility contracts.

A version MAY remain operational even after a newer version is introduced.

Deprecation MUST include:

* deprecation notice
* migration documentation
* affected clients
* sunset timeline
* compatibility expectations
* monitoring

⸻

10. Backward Compatibility

Non-breaking changes SHOULD be preferred.

Examples of generally compatible changes:

* adding optional response fields
* adding optional request fields
* adding new endpoints
* adding new event types

Potentially breaking changes include:

* changing field meaning
* removing fields
* changing authentication requirements
* changing validation semantics
* changing enum meanings
* changing authorization behavior
* changing error semantics

⸻

11. Resource-Oriented API

API resources SHOULD correspond to meaningful platform entities.

Examples:

/persons
/patients
/channel-identities
/conversations
/messages
/leads
/follow-ups
/appointments
/clinics
/staff
/knowledge
/notifications
/reports
/analytics
/ai

The exact endpoint structure may evolve.

Domain ownership must remain clear.

⸻

12. Domain Ownership

Each major resource MUST have one authoritative domain owner.

Examples:

Resource	Owner
Patient	Patient Intelligence / Identity Domain
Person	Identity Domain
Channel Identity	Identity / Communication Domain
Conversation	Conversation Domain
Lead	Lead Management Domain
Follow-Up	Follow-Up Engine
Appointment	Appointment Domain
Medical Safety State	Medical Safety Domain
Knowledge Document	Knowledge Domain
Notification	Communication Layer
Clinic Configuration	Clinic Management
Analytics	Analytics Domain

No API endpoint should create competing sources of truth.

⸻

13. Identity Model

Clinicos MUST distinguish between:

Person
    |
    +-- Channel Identity
    |      +-- Telegram
    |      +-- Web
    |      +-- Android
    |      +-- iOS
    |
    +-- Clinic Membership
    |
    +-- Authentication Identity

A channel identity MUST NOT automatically become a complete clinical identity without appropriate identity resolution.

⸻

14. Authentication

Clinicos MUST provide authenticated API access for protected operations.

Authentication mechanisms MAY differ by client.

Examples:

* Telegram identity verification
* session-based authentication
* access tokens
* refresh tokens
* OAuth/OIDC
* device-bound authentication
* administrative authentication

The exact mechanism is implementation-dependent.

The security model is not.

⸻

15. Authentication and Authorization Separation

Authentication answers:

Who is this?

Authorization answers:

What is this identity allowed to do?

These MUST remain separate concepts.

A successfully authenticated user MUST NOT automatically receive broad permissions.

⸻

16. Role Model

The platform supports major roles including:

* patient
* secretary
* doctor
* owner
* manager
* administrator

Additional roles MAY be introduced.

Permissions SHOULD be capability-based rather than relying only on role names.

⸻

17. Authorization

Authorization MUST be evaluated server-side.

The API MUST NOT trust:

* client-supplied role
* client-supplied clinic ID
* client-supplied permissions
* client-supplied patient ownership
* client-supplied staff privileges

Sensitive authorization decisions MUST be derived from trusted server-side state.

⸻

18. Tenant Isolation

Every tenant-scoped request MUST resolve a trusted tenant context.

The API MUST enforce:

Authenticated Identity
        |
        v
Tenant Membership
        |
        v
Resource Authorization

A client MUST NOT select an arbitrary tenant identifier and gain access to it.

⸻

19. Cross-Tenant Access

Cross-tenant access MUST be denied by default.

Administrative cross-tenant operations, if ever required, MUST use explicitly privileged server-side workflows.

Such operations MUST be auditable.

⸻

20. Clinic Context

For clinic-scoped operations, the API SHOULD establish:

request_id
actor_id
tenant_id
clinic_id
authorization_context
locale
timezone

The context MUST be derived from trusted sources where possible.

⸻

21. Request Identification

Every request SHOULD have a unique request identifier.

Example:

X-Request-ID

If the client provides one, the server MUST validate and safely normalize it.

The platform SHOULD generate one when absent.

⸻

22. Correlation IDs

Long-running workflows SHOULD use correlation identifiers.

A correlation ID SHOULD connect:

API Request
    |
    v
Application Operation
    |
    v
AI Task
    |
    v
Tool Calls
    |
    v
Events
    |
    v
External Integrations

This enables distributed tracing and audit reconstruction.

⸻

23. Idempotency

Side-effecting API operations SHOULD support idempotency.

Examples:

POST /appointments
POST /follow-ups
POST /notifications
POST /payments
POST /messages

A client MAY provide:

Idempotency-Key

The server MUST ensure that repeated requests do not unintentionally duplicate side effects.

⸻

24. Idempotency Scope

Idempotency keys MUST be scoped appropriately.

At minimum, the system SHOULD consider:

* tenant
* authenticated actor
* endpoint
* operation
* idempotency key

The implementation MUST prevent cross-tenant collisions.

⸻

25. Request Validation

Every API request MUST be validated.

Validation SHOULD include:

* schema validation
* type validation
* required fields
* length limits
* enum validation
* authorization
* tenant ownership
* business rules
* safety rules

Input validation MUST occur before domain side effects.

⸻

26. Output Validation

API responses MUST conform to their declared contract.

Responses SHOULD NOT expose:

* internal stack traces
* secrets
* provider credentials
* raw database errors
* unnecessary internal identifiers
* sensitive internal prompts

⸻

27. Error Model

The API SHOULD provide structured errors.

Example:

{
  "error": {
    "code": "APPOINTMENT_NOT_AVAILABLE",
    "message": "The requested appointment slot is not available.",
    "request_id": "req_123"
  }
}

Error codes SHOULD be stable.

Human-readable messages MAY evolve.

⸻

28. Error Categories

Common error categories include:

AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
VALIDATION_ERROR
NOT_FOUND
CONFLICT
RATE_LIMITED
SAFETY_BLOCKED
CONSENT_REQUIRED
TENANT_ACCESS_DENIED
DEPENDENCY_FAILURE
AI_UNAVAILABLE
INTEGRATION_FAILURE
INTERNAL_ERROR

⸻

29. Error Information Disclosure

Errors MUST NOT disclose unnecessary sensitive information.

For example, an unauthorized request MUST NOT reveal whether another tenant contains a specific patient.

⸻

30. Rate Limiting

Public and authenticated APIs SHOULD implement rate limits.

Limits MAY vary by:

* identity
* tenant
* endpoint
* operation
* client
* IP
* risk category

High-risk operations SHOULD have stricter limits.

⸻

31. Abuse Prevention

The API MUST defend against:

* brute force attempts
* automated abuse
* request flooding
* message spam
* AI abuse
* resource exhaustion
* repeated expensive requests
* enumeration attacks

⸻

32. Pagination

Collection endpoints SHOULD support pagination.

Example:

?page=2&page_size=50

Cursor-based pagination SHOULD be preferred for large or frequently changing datasets.

⸻

33. Filtering

Filtering MUST be explicitly defined.

Examples:

status
created_at
updated_at
clinic_id
assigned_staff_id
language
channel

User-provided filtering MUST NOT bypass authorization.

⸻

34. Sorting

Sorting SHOULD be restricted to supported fields.

Clients MUST NOT provide arbitrary database expressions.

⸻

35. Search

Search APIs MUST enforce authorization and tenant isolation.

Search results MUST NOT expose records outside the actor’s permitted scope.

⸻

36. Sensitive Search

Patient and medical information searches SHOULD have stronger controls and auditability.

⸻

37. Patient APIs

Patient APIs MAY support:

* patient profile
* contact information
* preferences
* communication preferences
* language
* clinic relationship
* relevant history
* consent records
* operational status

Medical information MUST follow the Medical Safety and Security specifications.

⸻

38. Patient Creation

Patient creation MUST distinguish:

* person creation
* patient relationship
* channel identity
* clinic membership

Duplicate prevention SHOULD be supported.

⸻

39. Patient Identity Resolution

Identity resolution MAY use:

* verified phone number
* verified channel identity
* authenticated account
* staff-assisted matching
* explicit patient confirmation

AI MUST NOT autonomously merge uncertain identities.

⸻

40. Conversation APIs

Conversation APIs SHOULD support:

* conversation retrieval
* message retrieval
* inbound message ingestion
* outbound message creation
* conversation state
* assignment
* human takeover
* AI state
* metadata

Conversation ownership remains with the Conversation domain.

⸻

41. Message Ownership

Communication delivery metadata belongs to the Communication Layer.

Conversation content and conversation state belong to the Conversation Domain.

These responsibilities MUST remain separated.

⸻

42. Lead APIs

Lead APIs MAY support:

* lead creation
* lead status
* lead scoring
* source
* assignment
* qualification
* conversion state
* follow-up state
* notes
* activity history

AI-generated lead assessments MUST be treated as derived intelligence, not immutable truth.

⸻

43. Follow-Up APIs

Follow-Up APIs SHOULD support:

* create follow-up
* validate follow-up
* schedule
* pause
* resume
* cancel
* execute
* retry
* human takeover
* status inspection

The Follow-Up Engine owns follow-up lifecycle.

⸻

44. Appointment APIs

Appointment APIs MUST use authoritative appointment data.

They MAY support:

* appointment creation
* appointment lookup
* confirmation
* rescheduling
* cancellation
* reminders
* availability lookup
* provider assignment

AI MUST NOT invent appointment availability.

⸻

45. Appointment Availability

Availability MUST come from an authoritative scheduling source.

If availability cannot be verified, the API MUST NOT represent an unavailable or unknown slot as available.

⸻

46. Clinic Management APIs

Clinic management APIs MAY support:

* clinic profile
* working hours
* services
* staff
* rooms
* operational policies
* communication preferences
* AI configuration
* localization
* notification settings

Sensitive administrative operations require appropriate authorization.

⸻

47. Staff APIs

Staff APIs MAY support:

* staff profile
* role
* permissions
* assignment
* workload
* availability
* clinic membership
* activity

Staff access MUST be tenant-scoped.

⸻

48. Knowledge APIs

Knowledge APIs MAY support:

* document registration
* document versioning
* indexing
* retrieval
* metadata
* source status
* approval status
* publication state

Knowledge APIs MUST NOT become a substitute for operational truth.

⸻

49. Knowledge Source Authority

Knowledge systems are authoritative for approved knowledge content only.

They are not authoritative for:

* live appointment availability
* current inventory
* current patient status
* current payment status
* real-time staff availability
* dynamic operational state

⸻

50. AI API Boundary

Clinicos exposes AI capabilities through an internal governed AI layer.

Conceptually:

Client
   |
   v
Clinicos API
   |
   v
Application Service
   |
   v
AI Orchestration Layer
   |
   v
AI Task
   |
   v
Gemini Adapter
   |
   v
Google Gemini

⸻

51. Gemini-Only Architecture

Google Gemini is the only active AI provider in the target architecture.

The following are NOT active runtime providers:

* FreeLLMAPI
* OpenRouter
* DeepSeek
* Qwen
* OpenAI
* other external LLM providers

⸻

52. No Multi-Provider Routing

Clinicos MUST NOT implement runtime routing between different AI providers.

There MUST NOT be:

Gemini -> OpenAI
Gemini -> DeepSeek
Gemini -> Qwen
Gemini -> OpenRouter

as provider fallback paths.

⸻

53. Gemini Model Routing

Multiple Gemini models MAY be used.

This is considered model selection within a single provider.

For example:

Gemini Model A -> lightweight classification
Gemini Model B -> conversational reasoning
Gemini Model C -> advanced multimodal task

This does not constitute multi-provider routing.

⸻

54. AI Provider Abstraction

An internal AI abstraction MUST remain.

Example conceptual interface:

AIEngine
    |
    +-- generate()
    +-- generate_structured()
    +-- analyze_multimodal()
    +-- evaluate()
    +-- embed()

The implementation MAY contain a Gemini adapter.

⸻

55. Gemini Adapter

Provider-specific logic MUST be isolated inside the Gemini adapter.

The adapter owns:

* Gemini SDK integration
* authentication
* model identifiers
* provider request formatting
* provider response parsing
* provider error mapping
* provider-specific configuration
* provider-specific telemetry

Domain logic MUST NOT depend directly on Gemini SDK types.

⸻

56. Direct Gemini Access Prohibited

The following components MUST NOT directly call Gemini:

* Telegram bot handlers
* web clients
* mobile clients
* frontend JavaScript
* domain entities
* database layer
* arbitrary background jobs

All governed AI calls MUST pass through the AI layer.

⸻

57. AI Failure Handling

Gemini failures MUST be handled through:

* retry
* exponential backoff
* timeout
* circuit breaker
* queueing
* graceful degradation
* deterministic templates
* human escalation

Provider substitution MUST NOT be used.

⸻

58. Graceful AI Degradation

If Gemini is temporarily unavailable, Clinicos MAY fall back to deterministic functionality.

Examples:

AI appointment explanation
        ->
deterministic appointment information
AI-generated reminder
        ->
approved template
AI conversational response
        ->
human handoff

This is functional degradation, not provider fallback.

⸻

59. AI Request Authorization

Every AI operation MUST define:

* actor
* tenant
* purpose
* task type
* allowed data
* allowed tools
* risk level
* output contract
* side-effect permissions

⸻

60. AI Data Access

AI requests MUST receive only the context required for the task.

The API MUST NOT blindly send the entire patient record to Gemini.

⸻

61. AI Privacy Boundary

Sensitive data MUST be minimized before leaving the Core Platform.

Where appropriate, the AI layer SHOULD perform:

* redaction
* minimization
* normalization
* pseudonymization
* field filtering

⸻

62. AI Tool Calls

AI tool calls MUST pass through governed application tools.

Examples:

get_patient_context
get_appointment
get_availability
create_follow_up
send_message
create_task
search_knowledge

AI MUST NOT directly execute:

SQL
shell commands
filesystem operations
arbitrary HTTP requests

⸻

63. AI Write Operations

AI-generated write operations MUST have explicit permission.

Examples:

send message
create follow-up
modify appointment
create lead
update patient preference

Each operation MUST be authorized independently.

⸻

64. High-Risk AI Actions

High-risk actions SHOULD require stronger validation or human approval.

Examples:

* medical advice
* safety escalation
* appointment cancellation
* financial operations
* sensitive data changes
* bulk communication
* marketing campaigns
* irreversible actions

⸻

65. AI Output Validation

AI output MUST pass:

1. schema validation
2. semantic validation
3. business-rule validation
4. safety validation
5. authorization validation
6. factual validation where required

Only validated output may trigger side effects.

⸻

66. Dynamic Truth

Dynamic operational information MUST come from authoritative APIs or domain services.

Examples include:

* appointment availability
* appointment status
* clinic hours
* provider availability
* payment status
* current pricing
* current discounts
* current service availability

Gemini MUST NOT be treated as the source of these facts.

⸻

67. AI Hallucination Prevention

The API architecture MUST reduce hallucination risk by separating:

AI Reasoning

from:

Authoritative Operational Truth

⸻

68. Communication API Boundary

Communication APIs MUST separate:

Business Intent
        |
        v
Communication Policy
        |
        v
Message Composition
        |
        v
Channel Selection
        |
        v
Delivery

⸻

69. Communication Request

A communication request SHOULD contain:

tenant_id
recipient
intent
priority
channel_constraints
content
locale
schedule
policy_context
idempotency_key
correlation_id

⸻

70. Communication Intent

Examples:

APPOINTMENT_CONFIRMATION
APPOINTMENT_REMINDER
APPOINTMENT_RESCHEDULE
APPOINTMENT_CANCELLATION
FOLLOW_UP
LEAD_RESPONSE
LEAD_REACTIVATION
PATIENT_REACTIVATION
ADMINISTRATIVE_NOTICE
HUMAN_CALLBACK
MARKETING
SAFETY_ESCALATION
INTERNAL_STAFF_NOTIFICATION

Intent does not itself grant authorization.

⸻

71. Communication Authorization

Before sending, the system MUST evaluate:

* recipient
* tenant
* consent
* purpose
* channel permission
* quiet hours
* frequency limits
* safety state
* human ownership
* clinic policy
* communication history

⸻

72. Telegram Integration

Telegram is the initial external communication channel.

The architecture MUST isolate Telegram-specific implementation behind a Telegram adapter.

Conceptually:

Communication Layer
        |
        v
Telegram Adapter
        |
        v
Telegram Bot API

⸻

73. Telegram Bot Boundary

Telegram-specific concerns include:

* update parsing
* webhook or polling integration
* Telegram user IDs
* chat IDs
* message formatting
* media handling
* callback queries
* command handling
* Telegram-specific rate limits

These concerns MUST NOT leak into core domain models.

⸻

74. Telegram Identity

A Telegram identity SHOULD contain:

telegram_user_id
telegram_chat_id
username
display_name
verification_state

Only trusted fields should be used for identity resolution.

⸻

75. Telegram Authentication

Telegram identity MUST be mapped to a Clinicos identity through a controlled authentication process.

A Telegram username alone MUST NOT be treated as a secure identity proof.

⸻

76. Telegram Webhooks

If Telegram webhooks are used, incoming requests MUST be validated using appropriate Telegram security mechanisms.

Webhook processing MUST be idempotent.

⸻

77. Telegram Update Deduplication

Repeated Telegram updates MUST NOT create duplicate domain events or duplicate side effects.

The system SHOULD persist processed update identifiers where appropriate.

⸻

78. Telegram Commands

Telegram commands MAY provide shortcuts to application functionality.

Examples:

/start
/help
/appointments
/contact

Commands MUST invoke application services rather than embedding business logic inside bot handlers.

⸻

79. Telegram Mini App

The Telegram Mini App is a presentation layer.

It MUST communicate with Clinicos Core Platform through governed APIs.

It MUST NOT directly access:

* database
* Gemini
* internal service endpoints
* private infrastructure

⸻

80. Mini App Authentication

Mini App identity MUST be verified server-side.

Client-provided identity information MUST NOT be trusted without cryptographic verification.

⸻

81. Web Client

The future Web application follows:

Web Client
    |
    v
Clinicos API
    |
    v
Core Platform

The web client MUST remain independent of domain implementation details.

⸻

82. Android Client

The Android application follows the same architectural boundary:

Android
    |
    v
Clinicos API
    |
    v
Core Platform

Android-specific functionality MUST remain inside the Android client layer unless it is genuinely domain functionality.

⸻

83. iOS Client

The iOS application follows:

iOS
    |
    v
Clinicos API
    |
    v
Core Platform

The iOS client MUST NOT duplicate business-critical logic.

⸻

84. Client Expansion Principle

Adding:

* Mini App
* Web
* Android
* iOS

MUST NOT require redesigning core business domains.

The API layer is the stable integration boundary.

⸻

85. Client Capability Model

Different clients MAY support different capabilities.

For example:

Telegram Bot
    -> conversational interaction
Mini App
    -> structured workflows
Web
    -> advanced management
Mobile
    -> notifications and operational workflows

Capability differences MUST NOT change domain truth.

⸻

86. Client Feature Flags

Client-specific functionality MAY be controlled through feature flags.

Feature flags MUST be evaluated server-side for security-sensitive functionality.

⸻

87. External Integrations

External systems MUST be isolated behind integration adapters.

Examples:

Telegram Adapter
Gemini Adapter
Payment Adapter
SMS Adapter
Email Adapter
Calendar Adapter
Storage Adapter

⸻

88. Integration Adapter Contract

An integration adapter SHOULD define:

* request mapping
* response mapping
* authentication
* timeout
* retry behavior
* error mapping
* rate limiting
* observability
* provider identifiers

⸻

89. Provider Independence

The business domain MUST NOT depend on provider-specific identifiers or response formats.

For example:

Domain:
appointment_id
Provider:
external_appointment_id

The mapping belongs in the integration layer.

⸻

90. External Provider Failure

External provider failures MUST be mapped into stable internal error categories.

Example:

Provider timeout
    ->
DEPENDENCY_TIMEOUT

Provider-specific errors SHOULD NOT leak into clients unless necessary.

⸻

91. Integration Timeouts

Every external request MUST have a bounded timeout.

No external API call may wait indefinitely.

⸻

92. Retry Policy

Retries MUST be bounded.

Retries SHOULD use:

* exponential backoff
* jitter
* maximum attempt count
* retryable error classification

Non-retryable errors MUST NOT be repeatedly retried.

⸻

93. Circuit Breaker

High-value external dependencies SHOULD use circuit breakers.

Circuit breakers SHOULD prevent cascading failures.

⸻

94. Bulkheads

Independent integrations SHOULD use isolated resource pools where necessary.

A failure in one integration MUST NOT consume all platform resources.

⸻

95. External API Rate Limits

The integration layer MUST respect provider rate limits.

Rate-limit handling SHOULD include:

* queueing
* backoff
* prioritization
* batching where supported

⸻

96. Webhook Architecture

Inbound webhooks SHOULD follow:

External Provider
        |
        v
Webhook Endpoint
        |
        v
Authentication / Verification
        |
        v
Schema Validation
        |
        v
Deduplication
        |
        v
Normalization
        |
        v
Domain Event

⸻

97. Webhook Security

Webhooks MUST be protected against:

* forged requests
* replay attacks
* malformed payloads
* oversized payloads
* unauthorized sources

Where supported, signature verification MUST be used.

⸻

98. Webhook Idempotency

Webhook handlers MUST tolerate duplicate delivery.

Processing the same provider event multiple times MUST NOT produce duplicate business effects.

⸻

99. Webhook Ordering

Providers may deliver events out of order.

The system MUST NOT assume perfect ordering unless guaranteed by the provider.

Domain state reconciliation SHOULD handle ordering anomalies.

⸻

100. Webhook Replay Protection

Where provider event identifiers and timestamps are available, the system SHOULD detect suspicious replayed events.

⸻

101. Event-Driven Integration

Clinicos SHOULD use domain and integration events for asynchronous workflows.

Examples:

appointment.created
appointment.updated
appointment.cancelled
followup.created
followup.scheduled
communication.sent
communication.failed
lead.created
lead.converted
safety.escalated

⸻

102. Commands vs Events

A command requests an action.

An event records that something happened.

Example:

Command:
SendAppointmentReminder
Event:
AppointmentReminderSent

These concepts MUST remain separate.

⸻

103. Event Ownership

Every event MUST have an authoritative producer.

Consumers MUST NOT modify historical event meaning.

⸻

104. Event Schema

Events SHOULD contain:

event_id
event_type
event_version
occurred_at
tenant_id
actor_id
aggregate_type
aggregate_id
correlation_id
causation_id
payload

⸻

105. Event Versioning

Events MUST be versioned.

Breaking event changes require a new event version.

Consumers MUST be able to determine the event schema version.

⸻

106. Outbox Pattern

Side-effecting domain operations SHOULD use an outbox pattern where appropriate.

Conceptually:

Transaction
    |
    +-- Domain State Change
    |
    +-- Outbox Event

Both should commit atomically.

⸻

107. Event Delivery

Event consumers SHOULD assume at-least-once delivery.

Consumers MUST therefore implement idempotency.

⸻

108. Dead Letter Handling

Events that repeatedly fail SHOULD move to a dead-letter mechanism.

Dead-lettered events MUST be observable and recoverable.

⸻

109. Event Replay

The architecture SHOULD support controlled event replay where technically appropriate.

Replay MUST NOT unintentionally duplicate irreversible side effects.

⸻

110. Background Jobs

Long-running work SHOULD be asynchronous.

Examples:

* AI processing
* report generation
* bulk notifications
* indexing
* analytics aggregation
* external synchronization
* media processing

⸻

111. Job Idempotency

Background jobs MUST be idempotent where possible.

Job retries MUST NOT create uncontrolled duplicates.

⸻

112. Job Status

Long-running operations MAY expose:

PENDING
RUNNING
COMPLETED
FAILED
CANCELLED
EXPIRED

⸻

113. Asynchronous API Pattern

For long-running requests, the API MAY return:

{
  "operation_id": "op_123",
  "status": "PENDING"
}

The client MAY then query operation status.

⸻

114. Streaming

Streaming MAY be used for conversational AI or other interactive experiences.

Streaming MUST NOT bypass:

* authorization
* safety
* tenant isolation
* output validation
* audit requirements

⸻

115. Streaming Safety

AI streaming responses MUST NOT expose unsafe or unvalidated content merely because generation is incremental.

Sensitive workflows MAY require buffered validation before display.

⸻

116. File Uploads

File uploads SHOULD use controlled upload mechanisms.

The API MUST validate:

* file size
* file type
* MIME type
* authorization
* tenant ownership
* malware/security status where applicable

⸻

117. Medical Image Uploads

Medical or facial images require stronger privacy controls.

Access MUST be restricted to authorized workflows.

⸻

118. Signed URLs

Sensitive files SHOULD use short-lived signed URLs where appropriate.

Permanent public URLs MUST NOT be used for sensitive medical media.

⸻

119. Storage Integration

Storage providers MUST be isolated behind storage abstractions.

Domain logic MUST NOT depend directly on provider-specific SDKs.

⸻

120. Media Processing

Media processing MAY include:

* image validation
* resizing
* compression
* metadata removal
* facial analysis preparation
* report generation

Processing MUST preserve security and tenant isolation.

⸻

121. Facial Analysis Integration

Facial analysis MUST be accessed through the Clinicos Facial Analysis domain.

The API MUST NOT allow arbitrary AI image analysis without governed task context.

⸻

122. Facial Analysis Data

Facial analysis results MUST distinguish between:

raw image
derived measurements
AI interpretation
user-facing explanation

These should not be conflated.

⸻

123. Medical Safety Integration

Medical Safety is a higher-priority policy boundary.

API operations MUST respect medical safety state.

For example:

serious adverse event
        ->
pause routine commercial follow-up
        ->
route to appropriate safety workflow

⸻

124. Safety Escalation

Safety-related operations MAY require:

* urgent staff notification
* human review
* emergency guidance
* workflow suspension

The API MUST NOT allow ordinary commercial workflows to override safety states.

⸻

125. Consent Integration

Communication APIs MUST respect consent state.

Consent MUST be evaluated at execution time where relevant.

⸻

126. Consent Revocation

After consent revocation, future unauthorized communication MUST be blocked.

Already-completed communication MUST remain auditable according to retention policy.

⸻

127. Marketing Consent

Marketing consent MUST be distinct from transactional communication authorization.

A patient receiving an appointment reminder does not automatically grant marketing permission.

⸻

128. Privacy Preferences

The API MAY expose user communication preferences such as:

* preferred channel
* preferred language
* quiet hours
* notification categories
* marketing preferences

Preferences MUST be subordinate to safety, authorization, and legal requirements.

⸻

129. Localization

The platform supports:

fa
en
az
ar
tr

The API SHOULD use standardized locale codes.

⸻

130. Language Selection

Language preference SHOULD follow:

Explicit user preference
        >
Verified profile preference
        >
Conversation language
        >
Clinic default
        >
System default

⸻

131. RTL Support

Persian and Arabic experiences MUST support right-to-left presentation where appropriate.

API responses SHOULD remain language-neutral and structured.

⸻

132. Timezone Handling

Time-sensitive operations MUST use explicit timezone context.

Clinic timezone and user timezone MAY differ.

Scheduling MUST use authoritative timezone rules.

⸻

133. Date and Time Representation

APIs SHOULD use ISO 8601 timestamps.

Example:

2026-09-16T18:30:00+03:30

Ambiguous local timestamps MUST be avoided.

⸻

134. Appointment Time Zones

Appointment APIs MUST identify the timezone used for interpreting appointment times.

Clients MUST NOT silently convert appointment times without respecting the authoritative timezone.

⸻

135. Currency

Financial APIs SHOULD use:

* integer minor units where appropriate
* explicit currency codes
* server-side calculations

Clients MUST NOT be trusted for final financial calculations.

⸻

136. Pricing

Current pricing MUST come from authoritative clinic or commerce data.

Gemini MUST NOT invent current pricing.

⸻

137. Discounts

Discounts MUST come from authoritative campaign or clinic configuration.

AI-generated discount claims are prohibited unless backed by verified data.

⸻

138. Payment Integration

Payment providers MUST be isolated behind payment adapters.

The API MUST NOT trust client-reported payment success.

Payment status MUST come from authoritative provider verification or internal payment records.

⸻

139. Payment Webhooks

Payment webhooks MUST be authenticated and idempotent.

Financial state changes MUST be auditable.

⸻

140. Notification Integration

Notification delivery MUST use the Communication Layer.

Business domains SHOULD request communication rather than directly calling channel providers.

⸻

141. SMS Integration

Future SMS support SHOULD follow:

Communication Layer
        |
        v
SMS Adapter
        |
        v
SMS Provider

Provider-specific logic remains isolated.

⸻

142. Email Integration

Email follows the same abstraction.

Communication Layer
        |
        v
Email Adapter
        |
        v
Email Provider

⸻

143. WhatsApp Integration

If introduced, WhatsApp MUST be implemented as a channel adapter.

Core business logic MUST remain channel-independent.

⸻

144. Instagram Integration

If introduced, Instagram MUST be implemented as a channel adapter.

Instagram-specific APIs MUST NOT become core domain dependencies.

⸻

145. Channel-Neutral Communication

The same business intent SHOULD be deliverable through different channels when permitted.

Example:

FOLLOW_UP
    |
    +-- Telegram
    +-- WhatsApp
    +-- SMS
    +-- Email

Channel selection remains a communication concern.

⸻

146. Unauthorized Channel Fallback

If a preferred channel fails, the system MUST NOT automatically switch to another channel unless:

* the user has authorization for the fallback
* policy allows it
* the purpose allows it
* frequency limits allow it
* safety rules allow it

⸻

147. Human Handoff

The API MUST support human takeover.

Examples:

AI conversation
      ->
human takeover
      ->
AI paused
      ->
staff response

AI MUST respect human ownership state.

⸻

148. Human Ownership

When a staff member owns a conversation, automated workflows MUST NOT silently override that ownership.

⸻

149. Staff Approval

Certain AI-generated actions MAY require:

DRAFT
    ->
STAFF_APPROVAL
    ->
EXECUTE

⸻

150. Approval Expiration

Approval requests SHOULD expire when their underlying operational state becomes stale.

For example, an approved appointment message should be revalidated before sending if the appointment changed.

⸻

151. Stale Data Protection

The API MUST detect stale state where relevant.

Examples:

Appointment changed
Price changed
Consent revoked
Lead status changed
Human takeover occurred
Safety state changed

⸻

152. Pre-Execution Validation

Before important side effects, the system SHOULD revalidate:

* authorization
* tenant
* consent
* safety
* resource state
* operational truth
* idempotency
* policy

⸻

153. API Audit Logging

Sensitive operations MUST be auditable.

Examples:

* patient record changes
* consent changes
* appointment changes
* staff permission changes
* AI side effects
* bulk communication
* medical safety actions
* financial actions

⸻

154. Audit Record

Audit records SHOULD contain:

event_id
timestamp
tenant_id
actor_id
action
resource_type
resource_id
result
request_id
correlation_id
reason

⸻

155. Audit Integrity

Audit records SHOULD be append-only.

Application users MUST NOT be able to silently modify historical audit records.

⸻

156. Sensitive Data Logging

Logs MUST NOT contain unnecessary:

* passwords
* API keys
* access tokens
* medical records
* patient identifiers
* payment credentials
* private AI context

⸻

157. API Observability

APIs MUST expose sufficient telemetry for:

* latency
* throughput
* errors
* saturation
* rate limits
* dependency failures
* authentication failures
* authorization failures

⸻

158. Integration Observability

Every important external integration SHOULD expose:

* request count
* success count
* failure count
* latency
* timeout count
* retry count
* provider error categories
* circuit state

⸻

159. AI Observability

AI operations SHOULD track:

* task type
* model
* latency
* token usage where available
* estimated cost
* validation failures
* safety blocks
* retries
* success/failure
* human escalation

Sensitive prompt content SHOULD NOT be logged by default.

⸻

160. API Metrics

Important API metrics include:

request_latency
request_rate
error_rate
5xx_rate
4xx_rate
rate_limit_events
authentication_failures
authorization_failures
dependency_latency
dependency_failures

⸻

161. Distributed Tracing

The platform SHOULD support distributed tracing across:

API
Application Service
AI Layer
Database
Queue
External Integration
Webhook
Communication Layer

⸻

162. Health Endpoints

The platform SHOULD expose health information appropriate to its deployment model.

Example conceptual endpoints:

/health
/ready

Health responses MUST NOT expose secrets or sensitive infrastructure details.

⸻

163. Readiness

Readiness SHOULD reflect whether the service can safely accept traffic.

A temporary dependency issue MAY affect readiness depending on whether the dependency is critical.

⸻

164. Liveness

Liveness should indicate whether the process is functioning.

Liveness checks SHOULD NOT unnecessarily depend on external providers.

⸻

165. Graceful Shutdown

API services MUST support graceful shutdown where possible.

In-flight work SHOULD either complete safely or be recoverable.

⸻

166. Concurrency Control

The platform MUST prevent conflicting updates where necessary.

Examples:

Appointment double booking
Concurrent consent changes
Duplicate follow-up creation
Conflicting staff assignments

⸻

167. Optimistic Concurrency

Version numbers or equivalent mechanisms SHOULD be used for resources where concurrent updates are likely.

⸻

168. Conflict Responses

Concurrency conflicts SHOULD return structured conflict errors.

Example:

409 CONFLICT

The client can then refresh current state.

⸻

169. Transaction Boundaries

API handlers SHOULD NOT define arbitrary database transactions.

Transactions belong to application/domain operations where business invariants are understood.

⸻

170. Database Access

The API layer MUST NOT construct arbitrary SQL from client input.

Database access belongs to controlled repositories or domain infrastructure.

⸻

171. Secret Management

API and integration credentials MUST be stored using secure secret management.

Secrets MUST NOT be:

* committed to source control
* embedded in client applications
* returned through APIs
* logged
* placed in prompts

⸻

172. Gemini Credentials

Gemini credentials MUST remain server-side.

Clients MUST NOT receive Gemini API keys.

⸻

173. Telegram Credentials

Telegram bot credentials MUST remain server-side.

⸻

174. External Provider Credentials

All provider credentials MUST remain inside their respective integration boundary.

⸻

175. Configuration

Configuration SHOULD be separated from code.

Examples:

AI model configuration
API limits
feature flags
channel configuration
clinic policies
notification policies

Secrets remain separate from ordinary configuration.

⸻

176. Configuration Validation

Services SHOULD validate configuration at startup.

Invalid critical configuration SHOULD prevent unsafe startup.

⸻

177. Environment Separation

The platform SHOULD distinguish:

development
testing
staging
production

Credentials and infrastructure MUST remain environment-specific.

⸻

178. Production Safety

Production APIs MUST NOT expose development debugging functionality.

⸻

179. CORS

Browser-facing APIs MUST use explicit CORS configuration.

Wildcard CORS SHOULD NOT be used for authenticated production applications unless justified and safe.

⸻

180. CSRF

Browser authentication mechanisms MUST consider CSRF protection where applicable.

⸻

181. Token Security

Access tokens SHOULD:

* have limited lifetime
* be scoped
* be securely stored
* be revocable where required

⸻

182. Refresh Tokens

Refresh tokens SHOULD be protected with stronger security controls than ordinary access tokens.

⸻

183. Session Revocation

The platform SHOULD support session revocation for:

* logout
* account compromise
* staff deactivation
* permission changes
* security incidents

⸻

184. Device Management

Mobile clients MAY support device registration.

Device identifiers MUST NOT be treated as sufficient identity proof.

⸻

185. Administrative APIs

Administrative APIs MUST use stronger authorization.

Examples:

clinic configuration
staff permissions
AI configuration
billing configuration
bulk operations
data export
data deletion

⸻

186. Bulk Operations

Bulk operations MUST be:

* explicitly authorized
* rate-limited
* observable
* auditable
* cancellable where possible

⸻

187. Bulk AI Operations

Bulk AI operations SHOULD have explicit budgets and quotas.

Examples:

* bulk lead classification
* campaign drafting
* report generation
* knowledge processing

⸻

188. Bulk Communication

Bulk communication MUST pass:

* consent
* policy
* frequency
* tenant
* safety
* approval
* rate-limit checks

⸻

189. Data Export APIs

Data export MUST respect:

* tenant authorization
* patient rights
* privacy policy
* data minimization
* audit requirements

⸻

190. Data Deletion APIs

Deletion requests MUST follow defined retention and legal policies.

Deletion MUST NOT bypass required audit or legal retention obligations.

⸻

191. API Documentation

All public/internal application APIs SHOULD have machine-readable schemas.

OpenAPI is RECOMMENDED for HTTP APIs.

⸻

192. OpenAPI

The API specification SHOULD define:

* paths
* methods
* parameters
* request schemas
* response schemas
* error schemas
* authentication
* authorization requirements
* examples

⸻

193. Contract Testing

API contracts SHOULD have automated contract tests.

Clients and servers SHOULD be tested against the same contract where practical.

⸻

194. Integration Testing

Integration tests SHOULD cover:

* authentication
* authorization
* tenant isolation
* database
* queues
* Gemini
* Telegram
* webhooks
* communication
* appointment systems
* storage
* payment systems

⸻

195. Gemini Integration Tests

Gemini integration tests SHOULD verify:

* request formatting
* authentication
* model selection
* structured outputs
* timeout behavior
* retry behavior
* failure mapping
* safety handling
* output validation

⸻

196. No Fake AI Verification

Tests MUST distinguish between:

mocked Gemini behavior

and:

real Gemini integration

A mocked test MUST NOT be presented as proof of real provider compatibility.

⸻

197. External Integration Test Modes

Each integration SHOULD support:

mock
sandbox
staging
production

where the provider supports these environments.

⸻

198. Webhook Testing

Webhook tests SHOULD include:

* valid signatures
* invalid signatures
* duplicate events
* reordered events
* malformed payloads
* replay attempts
* provider outages

⸻

199. API Security Testing

Security testing SHOULD include:

* authentication bypass
* authorization bypass
* tenant escape
* IDOR
* injection
* rate-limit bypass
* token abuse
* webhook forgery
* replay attacks
* sensitive data leakage

⸻

200. API Performance

Performance testing SHOULD measure:

* median latency
* p95 latency
* p99 latency
* throughput
* concurrency
* dependency impact
* database impact

⸻

201. AI Latency

AI latency MUST be measured separately from general API latency.

For example:

API latency
    =
request processing
+
AI latency
+
database latency
+
external integration latency

⸻

202. Long AI Operations

Long AI operations SHOULD use asynchronous execution rather than blocking HTTP requests indefinitely.

⸻

203. API Timeouts

Every API endpoint MUST have bounded execution time.

Endpoints involving asynchronous work SHOULD return operation identifiers.

⸻

204. Queue-Based Processing

Queue-based processing SHOULD be used for:

* heavy AI tasks
* bulk operations
* reports
* notifications
* indexing
* media processing

⸻

205. Priority Queues

The system MAY prioritize:

1. medical safety
2. authentication/security
3. operationally critical communication
4. appointment operations
5. patient-facing workflows
6. background analytics
7. non-critical bulk processing

Commercial optimization MUST NOT override medical safety.

⸻

206. Backpressure

The system MUST apply backpressure when dependencies or workers become saturated.

⸻

207. Queue Poisoning

Repeatedly failing jobs MUST be isolated rather than continuously retrying forever.

⸻

208. Integration Failover

Failover means recovering functionality safely.

For Gemini, failover MUST NOT mean switching to another AI provider.

For communication channels, channel fallback MAY exist only when explicitly authorized.

⸻

209. Provider Replacement

The architecture MUST make provider replacement technically possible through adapters.

However, no second AI provider is part of the active target runtime.

⸻

210. Provider Lock-In Boundary

Provider-specific code SHOULD remain confined to:

integration/
adapters/
providers/

or equivalent architectural boundaries.

⸻

211. Domain Independence

Core domains MUST NOT import:

Gemini SDK
Telegram SDK
payment SDK
SMS SDK
email SDK

directly.

They should depend on internal interfaces.

⸻

212. Dependency Direction

Preferred dependency direction:

Client
  ->
API
  ->
Application
  ->
Domain
  ->
Interfaces
  ->
Infrastructure Adapters

Infrastructure dependencies MUST NOT flow upward into domain models.

⸻

213. Integration Dependency Graph

A healthy dependency graph resembles:

Presentation
     |
     v
API
     |
     v
Application Services
     |
     +------> Domain Services
     |
     +------> AI Interface
     |
     +------> Communication Interface
     |
     +------> Scheduling Interface
     |
     +------> Storage Interface
     |
     +------> Payment Interface
                    |
                    v
             External Adapters

⸻

214. API Gateway Responsibilities

If an API gateway is used, it MAY handle:

* TLS termination
* routing
* authentication integration
* rate limiting
* request IDs
* WAF functionality
* observability

It SHOULD NOT contain business logic.

⸻

215. Business Logic Boundary

Business logic belongs in application/domain services.

It MUST NOT be hidden inside:

* frontend code
* API gateway rules
* Telegram handlers
* Gemini prompts
* database triggers unless explicitly justified

⸻

216. API Composition

API endpoints MAY compose multiple domain services.

However, the endpoint itself SHOULD remain thin.

⸻

217. Transactional APIs

Operations requiring atomicity SHOULD execute through application services with explicit transactional boundaries.

⸻

218. Saga / Workflow Coordination

Long-running cross-domain workflows MAY use orchestration.

Example:

Lead Created
   ->
Qualification
   ->
Follow-Up
   ->
Appointment
   ->
Confirmation

Each step MUST remain independently observable.

⸻

219. Workflow Compensation

Where an operation cannot be rolled back, the system SHOULD use compensating actions.

Example:

notification sent
appointment update failed
        ->
do not resend blindly
        ->
reconcile state

⸻

220. Reconciliation

External systems MAY diverge from internal state.

Clinicos SHOULD provide reconciliation mechanisms.

Examples:

* appointment synchronization
* payment synchronization
* message delivery reconciliation
* webhook reconciliation

⸻

221. Source of Truth Hierarchy

For each fact, the system MUST define its authoritative source.

Example:

Appointment availability -> Scheduling System
Payment status -> Payment System
Patient identity -> Identity Domain
Consent -> Consent Domain
Clinic policy -> Clinic Management
Medical safety state -> Medical Safety Domain
AI interpretation -> AI Layer
Communication delivery -> Communication Layer

⸻

222. API Source-of-Truth Rule

An API endpoint MUST NOT return AI-generated operational facts when an authoritative source is available.

⸻

223. Caching

Caching MAY be used for performance.

Cached values MUST have appropriate:

* TTL
* invalidation
* scope
* tenant isolation
* freshness requirements

⸻

224. Sensitive Data Caching

Sensitive patient or medical information SHOULD have strict caching controls.

⸻

225. Operational Truth Caching

Dynamic operational data MUST NOT be served from stale cache beyond acceptable freshness.

⸻

226. API Response Caching

Public cache headers MUST NOT accidentally expose private tenant data.

⸻

227. Security Headers

Browser-facing APIs SHOULD use appropriate security headers.

⸻

228. Request Size Limits

The API MUST impose request size limits.

Limits SHOULD be stricter for:

* unauthenticated endpoints
* webhook endpoints
* file uploads
* AI inputs

⸻

229. AI Input Limits

AI endpoints MUST enforce bounded:

* prompt size
* context size
* attachment size
* tool-call count
* iteration count

⸻

230. AI Cost Protection

The API MUST protect against uncontrolled AI spending.

Controls MAY include:

* per-request budgets
* per-user quotas
* per-tenant quotas
* model-specific limits
* concurrency limits
* daily budgets
* monthly budgets

⸻

231. AI Abuse Prevention

Users MUST NOT be able to use Clinicos as an unrestricted general-purpose Gemini proxy.

AI access MUST be task-scoped.

⸻

232. AI Task Registry

Each governed AI endpoint SHOULD map to a known AI task.

Example:

CONVERSATION_RESPONSE
LEAD_CLASSIFICATION
FOLLOW_UP_DRAFT
KNOWLEDGE_ANSWER
REPORT_GENERATION
FACIAL_ANALYSIS
TRANSLATION

⸻

233. AI Endpoint Permissions

Each AI task SHOULD define:

allowed_roles
allowed_data
allowed_tools
risk_level
budget
model_policy
output_schema
approval_mode

⸻

234. Prompt Injection Protection

API-fed content may contain adversarial instructions.

The AI layer MUST distinguish:

system instructions
developer instructions
trusted application context
retrieved knowledge
user content
external content

User or external content MUST NOT automatically override higher-priority instructions.

⸻

235. Tool Authorization

Even if Gemini requests a tool through an API operation, the tool MUST independently verify authorization.

⸻

236. AI Auditability

Important AI actions SHOULD record:

* task type
* model
* request ID
* tenant
* actor
* tool calls
* output validation
* final action
* approval state

Sensitive raw content SHOULD be minimized.

⸻

237. API Governance

Every API endpoint SHOULD have an owner.

Endpoint ownership SHOULD identify:

* domain
* team
* security requirements
* data classification
* SLA
* lifecycle status

⸻

238. Endpoint Lifecycle

Endpoints SHOULD move through:

PROPOSED
DESIGNED
IMPLEMENTED
TESTED
RELEASED
DEPRECATED
REMOVED

⸻

239. Breaking Change Governance

Breaking API changes require:

* documented reason
* migration plan
* affected clients
* compatibility period
* testing
* release approval

⸻

240. Documentation Synchronization

API implementation MUST remain synchronized with:

* OpenAPI
* domain contracts
* integration contracts
* event schemas
* authentication rules
* security requirements

⸻

241. API Review Checklist

Every significant API change SHOULD verify:

[ ] Authentication
[ ] Authorization
[ ] Tenant isolation
[ ] Input validation
[ ] Output validation
[ ] Error model
[ ] Idempotency
[ ] Rate limiting
[ ] Auditability
[ ] Observability
[ ] Privacy
[ ] Security
[ ] Testing
[ ] Documentation

⸻

242. Integration Review Checklist

Every external integration SHOULD verify:

[ ] Adapter boundary
[ ] Authentication
[ ] Credential isolation
[ ] Timeout
[ ] Retry
[ ] Rate limiting
[ ] Error mapping
[ ] Idempotency
[ ] Webhook verification
[ ] Replay protection
[ ] Observability
[ ] Reconciliation
[ ] Failure behavior
[ ] Data minimization

⸻

243. Client Integration Checklist

Every client SHOULD verify:

[ ] API authentication
[ ] Secure token storage
[ ] Authorization handling
[ ] API version compatibility
[ ] Error handling
[ ] Rate-limit handling
[ ] Offline behavior where relevant
[ ] Retry safety
[ ] Localization
[ ] Accessibility
[ ] No direct database access
[ ] No direct Gemini access
[ ] No embedded business-critical logic

⸻

244. Canonical Request Flow

The canonical protected API flow is:

CLIENT REQUEST
      |
      v
TLS / Edge
      |
      v
Request ID
      |
      v
Authentication
      |
      v
Tenant Resolution
      |
      v
Authorization
      |
      v
Input Validation
      |
      v
Application Service
      |
      v
Domain Rules
      |
      v
Safety / Consent / Policy
      |
      v
Domain Operation
      |
      v
Database / Event / Integration
      |
      v
Output Validation
      |
      v
Audit / Telemetry
      |
      v
RESPONSE

⸻

245. Canonical AI Request Flow

CLIENT
   |
   v
API
   |
   v
AUTHORIZATION
   |
   v
AI TASK REGISTRY
   |
   v
CONTEXT BUILDER
   |
   v
GEMINI ADAPTER
   |
   v
GOOGLE GEMINI
   |
   v
STRUCTURED OUTPUT
   |
   v
VALIDATION
   |
   v
POLICY / SAFETY
   |
   v
OPTIONAL TOOL EXECUTION
   |
   v
AUDIT / OBSERVABILITY
   |
   v
RESPONSE

⸻

246. Canonical Communication Flow

Business Domain
      |
      v
Communication Request
      |
      v
Consent / Policy Validation
      |
      v
Message Composition
      |
      v
Channel Selection
      |
      v
Communication Orchestrator
      |
      v
Channel Adapter
      |
      v
External Provider
      |
      v
Delivery Event
      |
      v
Communication State
      |
      v
Audit / Analytics

⸻

247. Canonical Appointment Flow

Client
   |
   v
Appointment API
   |
   v
Authorization
   |
   v
Scheduling Domain
   |
   v
Authoritative Availability
   |
   v
Appointment Transaction
   |
   v
Appointment Event
   |
   v
Follow-Up Engine
   |
   v
Communication Layer
   |
   v
Channel Adapter

⸻

248. Canonical Follow-Up Flow

Trigger
   |
   v
Follow-Up Engine
   |
   v
Policy Evaluation
   |
   v
Consent Check
   |
   v
Safety Check
   |
   v
Human Ownership Check
   |
   v
Schedule
   |
   v
Pre-Send Revalidation
   |
   v
Communication Layer
   |
   v
Channel Adapter
   |
   v
Delivery

⸻

249. Canonical Telegram Flow

Telegram
    |
    v
Telegram Adapter
    |
    v
Update Verification
    |
    v
Normalization
    |
    v
Identity Resolution
    |
    v
Clinicos API / Application Service
    |
    v
Conversation Domain
    |
    v
AI Layer if required
    |
    v
Communication Layer
    |
    v
Telegram Adapter
    |
    v
Telegram

⸻

250. Canonical Mini App Flow

Telegram Mini App
        |
        v
Mini App Authentication
        |
        v
Clinicos API
        |
        v
Core Platform
        |
        +----> Domain Services
        |
        +----> AI Layer
        |
        +----> Communication Layer
        |
        +----> Data Layer

⸻

251. Canonical Web Flow

Web
 |
 v
API
 |
 v
Authentication
 |
 v
Authorization
 |
 v
Application Services
 |
 v
Core Platform

⸻

252. Canonical Mobile Flow

Android / iOS
      |
      v
Clinicos API
      |
      v
Core Platform

⸻

253. No Client-to-Database Access

No supported client may connect directly to:

* PostgreSQL
* Redis
* internal databases
* private queues
* internal service ports

All access MUST pass through governed application boundaries.

⸻

254. No Client-to-Gemini Access

Clients MUST NOT contain Gemini credentials or directly invoke Gemini for governed Clinicos workflows.

⸻

255. No Business Logic in Prompts

Critical business rules MUST NOT exist only inside prompts.

Prompts may guide reasoning.

Deterministic policies MUST enforce critical constraints.

⸻

256. No Business Logic in Clients

Critical rules MUST NOT exist only in:

* Telegram handlers
* Mini App JavaScript
* web frontend
* Android
* iOS

The server remains authoritative.

⸻

257. No Operational Truth in AI

AI MUST NOT become the source of truth for operational state.

⸻

258. No Provider Leakage

Provider-specific concepts MUST NOT leak into domain contracts.

⸻

259. No Silent Side Effects

AI-generated or API-triggered side effects MUST be explicit, authorized, observable, and auditable.

⸻

260. No Silent Cross-Channel Messaging

A failed channel MUST NOT silently cause communication through another channel without authorization and policy validation.

⸻

261. No Silent Cross-Tenant Operations

Tenant boundaries MUST be enforced for every resource and integration.

⸻

262. Security Priority

The API architecture follows:

Medical Safety
    >
Privacy / Confidentiality
    >
Consent
    >
Authorization
    >
Tenant Isolation
    >
Operational Correctness
    >
User Preferences
    >
Convenience
    >
Commercial Optimization

⸻

263. Reliability Priority

When reliability conflicts with unsafe or unauthorized behavior:

Safety and authorization win.

The platform MUST prefer a safe failure over an unsafe successful operation.

⸻

264. Failure Philosophy

Clinicos SHOULD fail:

* explicitly
* safely
* observably
* recoverably

It MUST NOT fail by:

* inventing data
* bypassing authorization
* duplicating side effects
* silently switching providers
* silently crossing tenants
* silently ignoring consent
* silently overriding human ownership

⸻

265. Current AI Provider Rule

The active AI provider is:

Google Gemini

No other AI provider is part of the active target runtime.

⸻

266. Current Client Roadmap

The API architecture supports:

Phase 1
Telegram Bot
Phase 2
Telegram Bot
Telegram Mini App
Phase 3
Telegram Bot
Telegram Mini App
Web
Android
iOS

The Core Platform remains independent of this rollout order.

⸻

267. Phase 1 API Priority

Phase 1 SHOULD prioritize:

* Telegram identity
* conversation APIs
* patient APIs
* lead APIs
* follow-up APIs
* appointment APIs
* communication APIs
* AI APIs
* clinic management basics
* authentication
* authorization
* observability

⸻

268. Phase 2 API Priority

Phase 2 SHOULD add:

* Mini App authentication
* structured patient workflows
* appointment UI APIs
* lead management UI APIs
* staff-facing operational APIs where applicable
* richer notification state

⸻

269. Phase 3 API Priority

Phase 3 SHOULD extend the same API contracts to:

* Web
* Android
* iOS

The domains MUST NOT be duplicated for each client.

⸻

270. API Scalability

The architecture SHOULD support horizontal scaling.

Stateful behavior SHOULD be externalized where appropriate.

⸻

271. Stateless API Services

API services SHOULD remain stateless where practical.

Session state, queues, caches, and persistent state belong in appropriate infrastructure.

⸻

272. Redis

If Redis is used, it MUST remain an infrastructure component.

Clients MUST NOT access Redis directly.

⸻

273. PostgreSQL

If PostgreSQL is used, it MUST remain behind the data access layer.

Clients MUST NOT access PostgreSQL directly.

⸻

274. Database Transactions

Critical domain invariants MUST be enforced through transactional application/domain operations.

⸻

275. Cache Invalidation

Cache invalidation MUST be explicit for mutable operational data.

⸻

276. Deployment Compatibility

API contracts MUST remain compatible across rolling deployments where possible.

⸻

277. Zero-Downtime Considerations

Deployments SHOULD support:

* backward-compatible migrations
* rolling updates
* graceful shutdown
* queue draining
* versioned events

⸻

278. Database Migration Safety

Database migrations MUST NOT silently break active API versions.

⸻

279. Integration Migration

When replacing an external provider adapter:

Domain Contract
      |
      v
Integration Interface
      |
      +-- Old Adapter
      |
      +-- New Adapter

The domain contract remains stable.

⸻

280. Gemini Model Migration

Changing Gemini models MUST occur behind the AI layer.

The API contract SHOULD remain stable unless task semantics intentionally change.

⸻

281. AI Model Configuration

Gemini model configuration SHOULD be centralized.

Examples:

task_type
model
temperature
max_output_tokens
timeout
budget
structured_output_schema

⸻

282. Model Rollout

New Gemini models SHOULD be introduced through:

* configuration
* evaluation
* shadow testing where appropriate
* controlled rollout
* monitoring
* rollback

⸻

283. AI Rollback

AI rollback means returning to a previously approved Gemini model/configuration.

It does NOT mean switching to another provider.

⸻

284. API Rollback

API releases SHOULD support rollback without corrupting persistent state.

⸻

285. Incident Response

API incidents SHOULD record:

* start time
* affected services
* affected tenants
* affected integrations
* symptoms
* root cause
* mitigation
* recovery
* follow-up actions

⸻

286. Integration Incident Response

External provider outages MUST be distinguishable from internal failures.

⸻

287. Kill Switches

The platform SHOULD support controlled kill switches for:

* AI
* specific AI tasks
* communication
* specific channels
* bulk messaging
* external integrations
* high-risk workflows

⸻

288. AI Kill Switch

If Gemini becomes unsafe, unavailable, or misconfigured, AI capabilities MAY be disabled while deterministic functionality remains available.

⸻

289. Communication Kill Switch

Communication may be globally or selectively paused during incidents.

⸻

290. Integration Kill Switch

Individual external providers MAY be disabled without disabling unrelated domains.

⸻

291. Tenant-Level Controls

Where appropriate, administrators MAY disable specific features for individual tenants.

Tenant-level controls MUST NOT bypass global safety requirements.

⸻

292. Feature Flag Safety

Feature flags MUST NOT be used to bypass:

* authorization
* tenant isolation
* consent
* medical safety
* security controls

⸻

293. Testing Matrix

The API platform SHOULD test:

Unit
Integration
Contract
End-to-End
Security
Load
Chaos
Failure Recovery
Webhook
AI
Communication
Multi-Tenant Isolation

⸻

294. Multi-Tenant Testing

Automated tests MUST verify that:

Tenant A cannot access Tenant B

through:

* direct IDs
* search
* pagination
* filters
* exports
* webhooks
* AI tools
* background jobs
* caches
* events

⸻

295. AI Tenant Isolation

AI context MUST be tenant-scoped.

Retrieval, tool access, and memory MUST NOT cross tenant boundaries.

⸻

296. Integration Tenant Isolation

External integration metadata MUST retain tenant context where necessary.

Provider callbacks MUST be mapped to the correct tenant using trusted identifiers.

⸻

297. Communication Tenant Isolation

A communication request MUST include sufficient tenant context to prevent cross-tenant delivery.

⸻

298. Appointment Tenant Isolation

Appointment operations MUST verify clinic and tenant ownership before access or mutation.

⸻

299. Patient Data Protection

Patient data MUST be protected throughout:

Client
   ->
API
   ->
Application
   ->
Domain
   ->
Storage
   ->
Integration

Every boundary MUST enforce appropriate access controls.

⸻

300. Data Minimization

Only necessary data SHOULD cross each architectural boundary.

Examples:

Client -> only required UI data
AI -> only required reasoning context
Provider -> only required integration data
Logs -> only required telemetry

⸻

301. Data Classification

API resources SHOULD be classified according to sensitivity.

Possible categories:

PUBLIC
INTERNAL
CONFIDENTIAL
SENSITIVE
HIGHLY_SENSITIVE

Medical and identity information generally require stronger protection.

⸻

302. Sensitive API Responses

Sensitive responses SHOULD avoid unnecessary duplication of medical or identity data.

⸻

303. Privacy by Design

Every new integration MUST answer:

1. What data is sent?
2. Why is it sent?
3. Who receives it?
4. How long is it retained?
5. How is it protected?
6. Can it be minimized?
7. Can it be avoided?

⸻

304. API Data Retention

API logs and integration records MUST follow defined retention policies.

⸻

305. External Data Retention

External provider data retention MUST follow applicable contractual and privacy requirements.

⸻

306. Audit Retention

Security and safety-relevant audit records SHOULD have longer retention than ordinary operational logs where required.

⸻

307. API Documentation Requirements

Every significant endpoint MUST document:

* purpose
* authentication
* authorization
* request
* response
* errors
* idempotency
* rate limits
* side effects
* audit requirements

⸻

308. Integration Documentation Requirements

Every integration MUST document:

* provider
* purpose
* credentials
* API endpoints
* request/response mapping
* timeout
* retry
* rate limits
* webhook behavior
* failure modes
* monitoring
* replacement strategy

⸻

309. API Naming

API names SHOULD use domain language rather than infrastructure terminology.

Prefer:

appointments
follow-ups
patients
conversations

over implementation-specific terms.

⸻

310. API Semantic Stability

The meaning of a resource MUST remain stable across clients.

Telegram, Web, Android, and iOS MUST interpret the same domain resource consistently.

⸻

311. API as Product Contract

The API is a product contract between:

Clinicos Core Platform

and:

Clients / Integrations

It is not merely a technical transport layer.

⸻

312. Integration as Boundary

External integrations are replaceable boundaries.

The business domain should remain functional even when an external provider changes.

⸻

313. Provider Failure Principle

A provider failure MUST NOT cause:

* fabricated success
* fabricated data
* unauthorized fallback
* silent data corruption
* duplicate side effects

⸻

314. Reconciliation Principle

When external and internal state disagree, the platform SHOULD reconcile against the authoritative source rather than guessing.

⸻

315. AI Truth Principle

Gemini provides intelligence.

Gemini does not own Clinicos operational truth.

⸻

316. Communication Truth Principle

Communication state must be based on actual delivery evidence.

The system MUST distinguish:

created
sent
delivered
read
failed

⸻

317. Appointment Truth Principle

Appointment truth must come from the Appointment/Scheduling domain.

⸻

318. Consent Truth Principle

Consent truth must come from the Consent/Privacy domain.

⸻

319. Safety Truth Principle

Medical safety state must come from the Medical Safety domain.

⸻

320. Identity Truth Principle

Identity resolution must come from trusted identity mechanisms and domain state.

⸻

321. Final Architectural Contract

Clinicos APIs MUST enforce the following:

Client
    ->
API
    ->
Core Platform

and:

Core Platform
    ->
Governed AI Layer
    ->
Gemini

and:

Core Platform
    ->
Communication Layer
    ->
Channel Adapter
    ->
External Channel

⸻

322. Final Non-Negotiable Rules

The following rules are mandatory:

1. Google Gemini is the only active AI provider.
2. FreeLLMAPI is not part of the target architecture.
3. OpenRouter is not part of the target architecture.
4. DeepSeek is not part of the target architecture.
5. Qwen is not part of the target architecture.
6. OpenAI is not part of the target AI runtime.
7. Multi-provider AI routing is prohibited.
8. AI provider fallback is prohibited.
9. Internal AI abstraction remains mandatory.
10. Gemini-specific code must remain isolated behind the AI adapter.
11. Clients must not call Gemini directly.
12. Clients must not access databases directly.
13. Clients must not access Redis directly.
14. Clients must not contain critical business logic.
15. Business domains remain authoritative for business truth.
16. Dynamic operational facts must come from authoritative systems.
17. AI output must be validated before side effects.
18. AI tools must be individually authorized.
19. Tenant isolation is mandatory.
20. Authorization is mandatory.
21. Consent must be enforced.
22. Medical safety overrides commercial optimization.
23. Communication must remain channel-agnostic.
24. Telegram-specific logic must remain inside the Telegram boundary.
25. Mini App, Web, Android, and iOS are clients, not separate business platforms.
26. External providers must be isolated behind adapters.
27. Webhooks must be authenticated and idempotent.
28. Side-effecting operations must support idempotency where applicable.
29. Retries must be bounded.
30. External failures must be observable.
31. Silent cross-channel fallback is prohibited without authorization.
32. Silent cross-tenant access is prohibited.
33. Human takeover must be respected.
34. Sensitive operations must be auditable.
35. API contracts must be versioned.
36. Breaking changes must be governed.
37. AI failures must degrade safely.
38. Provider replacement must be technically possible but is not part of the active AI runtime.
39. Core business logic must remain client-independent.
40. API boundaries must remain stable as clients expand.

⸻

323. Final Architecture

The final target architecture is:

                         CLINICOS CLIENTS
                              |
          +-------------------+-------------------+
          |                   |                   |
       Telegram           Mini App          Web / Mobile
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                    APPLICATION API LAYER
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
     Authentication      Authorization        Tenant Context
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                    CLINICOS CORE PLATFORM
                              |
       +----------------------+----------------------+
       |                      |                      |
       v                      v                      v
   DOMAIN SERVICES        EVENT ENGINE          COMMUNICATION
       |                      |                      |
       |                      |                      v
       |                      |                CHANNEL ADAPTERS
       |                      |                      |
       |                      |             +--------+--------+
       |                      |             |        |        |
       |                      |          Telegram  Future   Future
       |                      |
       +----------------------+
                              |
                              v
                         AI LAYER
                              |
                              v
                       GEMINI ADAPTER
                              |
                              v
                       GOOGLE GEMINI

⸻

324. Final Product Principle

Clinicos is not:

Telegram Bot + APIs

It is:

AI-Native Clinic Operating Platform

whose first interface is Telegram.

It is not:

Gemini Wrapper

It is:

Governed Clinic Operating Platform
with Gemini as its active AI intelligence provider.

The API layer exists to make the Core Platform:

* secure
* tenant-aware
* client-independent
* channel-independent
* AI-governed
* observable
* auditable
* extensible
* reliable
* replaceable at integration boundaries

The long-term architectural direction is:

CORE PLATFORM FIRST
        >
API CONTRACTS
        >
CLIENTS

and:

BUSINESS INTENT
        >
POLICY
        >
AI / CONTENT
        >
COMMUNICATION
        >
CHANNEL
        >
EXTERNAL PROVIDER

This hierarchy is the canonical API and integration contract for Clinicos.
