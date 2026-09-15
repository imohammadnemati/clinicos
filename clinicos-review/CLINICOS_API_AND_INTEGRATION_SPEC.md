# Clinicos — API & Integration Specification
**Document:** `CLINICOS_API_AND_INTEGRATION_SPEC.md`  
**Status:** Target / Authoritative API & Integration Specification  
**Version:** 1.0  
**Project:** Clinicos
---
# 1. Purpose
This document defines the target API architecture and external integration strategy for Clinicos.
It specifies:
- API design principles
- internal service boundaries
- external integrations
- communication channels
- webhooks
- authentication
- authorization
- idempotency
- error handling
- AI provider integration
- Telegram integration
- future Instagram integration
- future web/WhatsApp/social integrations
- appointment integrations
- media/storage integrations
- notification integrations
- event-driven integrations
- integration testing
- observability
- retry and failure handling
This document describes the **target architecture**.
It does NOT assume that the current repository already implements these APIs or integrations.
The current repository MUST be inspected before implementation.
---
# 2. API Philosophy
Clinicos APIs MUST be:
- predictable
- secure
- tenant-aware
- versionable
- observable
- idempotent where required
- explicit about errors
- independent from specific AI providers
- independent from specific communication channels where practical
The API architecture MUST support the evolution of Clinicos from a Telegram-first system into a multi-channel clinic operating system.
---
# 3. Architectural Principle
The core business logic MUST NOT be tightly coupled to one communication channel.
Preferred architecture:
```text
                    External Channels
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       Telegram       Instagram        Web / Other
          │               │                │
          └───────────────┼────────────────┘
                          ▼
                 Channel Adapter Layer
                          │
                          ▼
                Unified Message Model
                          │
                          ▼
                 Conversation Domain
                          │
                          ▼
                  AI / Business Logic
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
            Leads     Follow-ups   Appointments
              │
              ▼
          Analytics

The business layer SHOULD work with normalized internal concepts rather than raw Telegram/Instagram-specific payloads.

⸻

4. API Layers

Clinicos SHOULD conceptually contain the following layers:

External API
      ↓
Authentication
      ↓
Authorization
      ↓
Tenant Context
      ↓
Request Validation
      ↓
Application / Use Case Layer
      ↓
Domain Layer
      ↓
Data Access
      ↓
Infrastructure

External integrations SHOULD NOT directly modify database records without passing through appropriate business logic.

⸻

5. API Types

Clinicos may expose several API categories:

1. Public API
2. Authenticated Application API
3. Internal Service API
4. Webhook API
5. Channel Integration API
6. AI Provider Integration API
7. Admin API
8. Background Job Interfaces

Each category MUST have appropriate authentication and authorization.

⸻

6. API Versioning

Public and externally consumed APIs SHOULD be versioned.

Preferred pattern:

/api/v1/...

Breaking changes SHOULD introduce a new version.

Non-breaking additions MAY remain within the current version.

⸻

7. Resource-Oriented API

APIs SHOULD generally be organized around domain resources.

Examples:

/api/v1/patients
/api/v1/leads
/api/v1/conversations
/api/v1/messages
/api/v1/appointments
/api/v1/services
/api/v1/knowledge
/api/v1/facial-analyses
/api/v1/notifications
/api/v1/analytics

The exact route naming MAY evolve according to framework conventions.

⸻

8. REST vs Other Protocols

REST/HTTP SHOULD be the default external API style unless a different protocol provides a clear advantage.

WebSockets or Server-Sent Events MAY be used for real-time dashboards.

GraphQL MAY be considered if the frontend requires complex data composition.

gRPC MAY be considered for internal high-performance service-to-service communication if Clinicos evolves into multiple independently deployed services.

Do not introduce multiple protocols without a real architectural need.

⸻

9. JSON

JSON SHOULD be the default API representation.

Responses SHOULD have predictable structures.

Example:

{
  "data": {},
  "meta": {}
}

Errors SHOULD use a consistent structure.

⸻

10. Error Format

Recommended error format:

{
  "error": {
    "code": "APPOINTMENT_SLOT_UNAVAILABLE",
    "message": "The requested appointment slot is no longer available.",
    "request_id": "..."
  }
}

Internal stack traces MUST NOT be returned to clients.

⸻

11. Error Codes

Error codes SHOULD be stable machine-readable identifiers.

Examples:

AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
TENANT_ACCESS_DENIED
RESOURCE_NOT_FOUND
VALIDATION_ERROR
RATE_LIMITED
IDEMPOTENCY_CONFLICT
APPOINTMENT_SLOT_UNAVAILABLE
AI_PROVIDER_UNAVAILABLE
AI_REQUEST_TIMEOUT
FACIAL_ANALYSIS_FAILED
MEDIA_INVALID
KNOWLEDGE_NOT_APPROVED
INTERNAL_ERROR

Clients SHOULD rely on error codes rather than parsing human-readable messages.

⸻

12. HTTP Status Codes

Use standard HTTP semantics.

Examples:

200 OK
201 Created
202 Accepted
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
429 Too Many Requests
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout

Do not use HTTP 200 for every failure.

⸻

13. Request IDs

Every request SHOULD have a unique request/correlation ID.

Example:

X-Request-ID

The request ID SHOULD appear in:

* API response
* structured logs
* traces
* relevant events
* background jobs

This enables end-to-end debugging.

⸻

14. Correlation IDs

Long-running workflows SHOULD preserve a correlation ID.

Example:

Patient Message
    ↓
AI Request
    ↓
Lead Update
    ↓
Follow-up
    ↓
Notification

All related operations SHOULD be traceable through a shared correlation ID.

⸻

15. Authentication

Authenticated APIs MUST verify identity before accessing protected resources.

Authentication may use:

* secure sessions
* access tokens
* OAuth
* channel-specific authentication
* signed integration credentials

The exact mechanism depends on the interface.

⸻

16. Authorization

Authentication alone is insufficient.

Every protected operation MUST verify:

User
+
Tenant Membership
+
Permission
+
Resource Ownership

where applicable.

⸻

17. Tenant Context

Tenant context MUST be derived from trusted authentication/integration context.

The API MUST NOT blindly trust:

{
  "tenant_id": "..."
}

from the client.

If a tenant ID is accepted as an input, it MUST be validated against the authenticated user’s authority.

⸻

18. Object-Level Authorization

Every resource lookup MUST verify tenant ownership and permission.

Unsafe:

GET /api/v1/patients/{patient_id}

with only:

patient_id exists

Safe conceptual flow:

authenticate
↓
resolve tenant
↓
load patient within tenant
↓
authorize access
↓
return data

⸻

19. Idempotency

Idempotency is mandatory for operations that may be retried.

Examples:

* appointment booking
* webhook processing
* external payment events
* message ingestion
* notification delivery
* facial analysis jobs
* asynchronous AI jobs

Clients MAY provide:

Idempotency-Key

The server SHOULD persist and enforce it for relevant operations.

⸻

20. Idempotent Webhooks

Webhook providers frequently retry events.

Therefore:

same webhook
+
same external event ID

MUST NOT create duplicate business state.

⸻

21. Pagination

Collection APIs SHOULD support pagination.

Example:

?page=1&limit=50

or cursor-based pagination.

Cursor pagination SHOULD be preferred for large or frequently changing datasets.

⸻

22. Filtering

APIs MAY support controlled filtering.

Example:

GET /leads?status=ACTIVE&temperature=HOT

Filtering parameters MUST be validated.

Do not allow arbitrary SQL-like query expressions from clients.

⸻

23. Sorting

Sorting MUST use an allowlist of supported fields.

Unsafe:

?sort=<arbitrary SQL>

Safe:

?sort=-created_at

where created_at is explicitly supported.

⸻

24. Field Selection

Field selection MAY be supported in the future.

If implemented, clients MUST NOT be able to bypass security restrictions by requesting hidden fields.

Sensitive fields must remain permission-protected.

⸻

25. Rate Limiting

Rate limits SHOULD exist for:

* authentication
* public APIs
* AI endpoints
* facial analysis
* message ingestion
* exports
* webhooks
* administrative operations

Limits SHOULD be tenant-aware where appropriate.

⸻

26. API Input Validation

Every request MUST validate:

* data type
* required fields
* field length
* enum values
* ranges
* relationships
* file sizes
* timestamps
* IDs

Validation MUST happen before business logic executes.

⸻

27. API Response Security

Responses MUST contain only fields the caller is authorized to see.

Do not return internal fields merely because they exist in a database model.

Examples of fields that may require restriction:

* internal notes
* staff performance data
* AI provider metadata
* internal IDs
* sensitive patient information
* security metadata

⸻

28. Mass Assignment Protection

APIs MUST NOT blindly map arbitrary request fields to database models.

Unsafe:

update_patient(**request.json)

if the client can modify:

tenant_id
role
permissions
created_at
security flags

Only explicitly allowed fields may be updated.

⸻

29. Channel Abstraction

Clinicos SHOULD normalize channel-specific messages into a common internal format.

Example:

{
  "channel": "telegram",
  "external_user_id": "...",
  "external_message_id": "...",
  "message_type": "text",
  "content": "...",
  "timestamp": "..."
}

The internal conversation system SHOULD NOT need to understand every raw Telegram-specific detail.

⸻

30. Unified Message Model

The internal message model SHOULD support:

channel
external_message_id
external_conversation_id
sender
recipient
message_type
content
language
attachments
timestamp
metadata

This enables future channels.

⸻

31. Channel Adapter Interface

Each channel adapter SHOULD conceptually expose operations such as:

receive_event()
normalize_event()
send_message()
send_media()
edit_message()
delete_message()
resolve_identity()
verify_webhook()

Not every channel must support every operation.

Capabilities SHOULD be explicit.

⸻

32. Telegram Integration

Telegram is the initial channel.

Telegram integration SHOULD be isolated inside a Telegram adapter/module.

The adapter SHOULD handle:

* updates
* message normalization
* identity resolution
* media downloads
* outgoing messages
* commands
* webhook/polling mechanics
* Telegram-specific errors

Core business logic SHOULD remain Telegram-independent.

⸻

33. Telegram Identity

Telegram identifiers SHOULD be stored as channel identities.

The system MUST NOT treat a Telegram user ID as a universal patient ID.

Conceptually:

Telegram User
      ↓
ChannelIdentity
      ↓
Patient

⸻

34. Telegram Message Idempotency

Telegram updates MUST be processed idempotently.

The system SHOULD track appropriate external update/message identifiers.

Repeated updates MUST NOT create duplicate messages.

⸻

35. Telegram Media

Telegram media SHOULD follow:

Telegram
   ↓
validate
   ↓
download securely
   ↓
store private media
   ↓
create attachment
   ↓
process

Temporary downloaded files SHOULD be deleted when no longer needed.

⸻

36. Telegram Webhook vs Polling

The integration MAY use:

* webhook
* polling

The choice is an infrastructure concern.

Business logic MUST remain independent of whether Telegram delivery uses polling or webhook mode.

⸻

37. Future Instagram Integration

Instagram SHOULD be implemented as another channel adapter.

Conceptually:

Instagram
   ↓
Instagram Adapter
   ↓
Unified Message Layer
   ↓
Conversation
   ↓
Patient Intelligence

The core architecture MUST NOT require Telegram-specific logic for Instagram.

⸻

38. Instagram Requirements

When supported, Instagram integration SHOULD handle:

* account connection
* authentication
* webhook verification
* incoming messages
* relevant comments/DM events where officially supported
* identity resolution
* outgoing replies where permitted
* media
* rate limits
* platform-specific restrictions

Instagram API capabilities MUST be verified against the current official platform capabilities before implementation.

Do not assume an API feature exists.

⸻

39. Future Channels

The architecture SHOULD allow:

Telegram
Instagram
WhatsApp
Website Chat
Mobile App
Other Social Channels

without redesigning the patient/conversation/lead domains.

⸻

40. Channel Capability Matrix

Each channel SHOULD declare capabilities.

Example:

Capability	Telegram	Instagram	Web
Text	Yes	Yes	Yes
Image	Yes	Yes	Yes
Voice	Yes	Depends	Depends
Edit Message	Yes	Depends	Depends
Delete Message	Depends	Depends	Yes
Rich Buttons	Yes	Depends	Yes
Webhook	Yes	Yes	N/A

The actual capability matrix MUST be verified before implementation.

⸻

41. External Provider Boundaries

External services MUST be treated as unreliable boundaries.

They may:

* timeout
* return invalid responses
* rate-limit
* change behavior
* become unavailable
* return malformed data
* return duplicate events

Integration code MUST handle these cases.

⸻

42. AI Integration

AI providers MUST be accessed through an abstraction layer.

Preferred:

Application
    ↓
AI Service
    ↓
Provider Router / Manager
    ↓
Provider Adapter
    ↓
FreeLLMAPI / Future Provider

Core business logic MUST NOT directly call provider SDKs.

⸻

43. AI Provider Interface

A provider abstraction SHOULD conceptually support:

generate()
generate_structured()
analyze_image()
embed()
health_check()

Capabilities MUST be explicit.

A provider that does not support vision MUST NOT be treated as if it does.

⸻

44. AI Request Contract

AI requests SHOULD contain:

task
tenant context
agent context
relevant user context
relevant knowledge
input
constraints
expected output schema

Do not send irrelevant data.

⸻

45. Structured AI Output

For important workflows, AI SHOULD return structured output.

Example:

{
  "intent": "PRICE_INQUIRY",
  "service": "facial_mesotherapy",
  "lead_temperature": "WARM",
  "needs_human": false,
  "confidence": 0.91
}

The application MUST validate AI output before using it.

⸻

46. AI Output Validation

Never trust model output blindly.

The application SHOULD validate:

* schema
* enum values
* required fields
* numeric ranges
* tenant references
* business rules

Example:

If AI returns:

appointment_status = CONFIRMED

the application MUST NOT automatically confirm the appointment unless the authoritative appointment system confirms it.

⸻

47. AI Provider Failure

Provider failures SHOULD be classified:

timeout
rate_limit
server_error
invalid_response
authentication_error
network_error
content_error
unsupported_capability

Retryability MUST be determined by error type.

⸻

48. AI Retry Policy

Retry only when appropriate.

Generally retryable:

timeout
temporary network failure
temporary provider failure
429
503

Potentially non-retryable:

invalid API key
invalid request
unsupported capability
policy rejection
invalid schema caused by application bug

⸻

49. AI Fallback

If multiple providers exist, fallback MAY be used.

However:

* safety policies must remain constant
* output must still be validated
* provider changes must be observable
* fallback must not create uncontrolled costs

FreeLLMAPI may be the current reference provider.

The architecture MUST allow future provider routing.

⸻

50. AI Cost Control

AI integrations SHOULD support:

* token limits
* context limits
* caching
* prompt minimization
* model selection
* provider routing
* rate limits
* usage tracking

Cost optimization MUST NOT weaken medical or security safeguards.

⸻

51. AI Timeout

Every AI request MUST have a bounded timeout.

No request should be allowed to hang indefinitely.

Timeouts SHOULD be configurable.

⸻

52. AI Cancellation

Long-running AI jobs SHOULD support cancellation where practical.

Cancelled requests MUST not continue consuming resources indefinitely.

⸻

53. AI Observability

Track:

provider
model
task
latency
input tokens
output tokens
status
error
retry count
fallback
request ID

Sensitive prompts and outputs SHOULD NOT be logged unnecessarily.

⸻

54. Knowledge Integration

AI retrieval SHOULD use the approved Knowledge Base.

Flow:

User message
    ↓
Intent
    ↓
Knowledge retrieval
    ↓
Approved knowledge
    ↓
AI generation
    ↓
Validation
    ↓
Response

Unapproved knowledge SHOULD NOT be presented as authoritative.

⸻

55. Appointment Integration

Appointment APIs MUST distinguish:

request
availability check
reservation
confirmation
cancellation
rescheduling
completion

These are different operations.

⸻

56. Appointment Availability

Availability MUST be obtained from the authoritative scheduling system.

Never infer:

19:00 is probably available

and tell the patient that it is confirmed.

⸻

57. Appointment Booking

Booking SHOULD be transactional and idempotent.

Conceptual:

Request
 ↓
Validate patient
 ↓
Validate doctor/service
 ↓
Check availability
 ↓
Reserve
 ↓
Confirm
 ↓
Emit event

If any critical step fails, the system MUST not falsely report success.

⸻

58. Appointment Rescheduling

Rescheduling SHOULD preserve history.

Do not simply overwrite the original appointment time without audit/history when business traceability is required.

⸻

59. Appointment Cancellation

Cancellation SHOULD:

* verify authorization
* update appointment state
* record reason where appropriate
* release availability
* emit event
* trigger relevant follow-up/notification logic

⸻

60. Storage Integration

File/object storage SHOULD be abstracted.

Potential storage providers MAY include:

* S3-compatible storage
* cloud object storage
* other secure storage systems

Core business logic SHOULD depend on a storage interface rather than a specific provider.

⸻

61. Storage Interface

Conceptual operations:

upload()
download()
delete()
generate_signed_url()
exists()
metadata()

Access MUST be authorization-aware.

⸻

62. Storage Security

Private patient media MUST:

* remain private
* use access control
* use short-lived signed URLs where applicable
* avoid predictable public paths
* have retention policies

⸻

63. Notification Integration

Notifications MAY use:

* Telegram
* email
* SMS
* push
* dashboard notifications
* future channels

Notification delivery SHOULD be abstracted from business logic.

⸻

64. Notification Flow

Preferred:

Business Event
     ↓
Notification Decision
     ↓
Notification Record
     ↓
Delivery Adapter
     ↓
External Channel

Business events should not directly call Telegram/email APIs everywhere in the codebase.

⸻

65. Notification Idempotency

Repeated events MUST NOT cause uncontrolled duplicate notifications.

Notifications SHOULD have idempotency keys where appropriate.

⸻

66. External Email/SMS Providers

If integrated, providers MUST be abstracted.

Example:

Notification Service
      ↓
Email Adapter
      ↓
Provider

The clinic/business layer should not depend on a specific vendor.

⸻

67. Webhooks

Webhook endpoints MUST:

1. authenticate/verify source
2. validate payload
3. enforce size limits
4. create/request idempotency
5. persist relevant event
6. acknowledge safely
7. process asynchronously when appropriate

⸻

68. Webhook Acknowledgement

Webhook handlers SHOULD acknowledge quickly when the provider expects fast responses.

Heavy processing SHOULD move to background jobs.

⸻

69. Webhook Replay Protection

Where providers provide timestamps/signatures, validate them.

Repeated webhook events MUST be detected.

⸻

70. Background Jobs

Background jobs SHOULD handle:

* AI processing
* follow-ups
* notifications
* media processing
* facial analysis
* report generation
* analytics
* knowledge processing

API requests SHOULD NOT perform long-running operations synchronously when doing so would cause poor reliability.

⸻

71. Job Idempotency

A job MAY be retried.

Therefore jobs MUST be designed so that retrying does not create duplicate business effects.

⸻

72. Job Failure Handling

Jobs SHOULD support:

pending
running
completed
failed
retrying
cancelled

Failed jobs SHOULD preserve enough information for debugging.

⸻

73. Dead Letter Handling

Repeatedly failing jobs SHOULD eventually move to a dead-letter or manual-review state.

The system SHOULD notify operators when critical jobs repeatedly fail.

⸻

74. Integration Circuit Breakers

For unstable external providers, circuit breakers MAY be used.

Example:

Provider healthy
      ↓
requests allowed
Repeated failures
      ↓
circuit open
cooldown
      ↓
health check
provider recovers
      ↓
requests resume

⸻

75. Integration Health Checks

External integrations SHOULD expose health status where practical.

Examples:

Telegram
AI provider
Database
Redis
Storage
Appointment provider
Notification provider

Health checks MUST NOT expose secrets.

⸻

76. Graceful Degradation

Clinicos SHOULD degrade safely.

Example:

If AI is unavailable:

AI unavailable
↓
do not hallucinate
↓
inform patient appropriately
↓
offer human takeover
↓
queue/retry where appropriate

If analytics is unavailable:

analytics unavailable
↓
core patient/appointment operations continue

⸻

77. Channel Failure

If Telegram is unavailable:

The underlying patient/lead data SHOULD remain intact.

The system should be able to recover when the channel returns.

⸻

78. Provider Failure

If FreeLLMAPI is unavailable:

The AI abstraction layer SHOULD allow future fallback providers if configured.

If no safe provider is available:

do not fabricate response

Human takeover or a safe fallback response SHOULD be used.

⸻

79. Integration Configuration

Integration configuration SHOULD be tenant-aware where appropriate.

Examples:

Telegram bot
Instagram account
notification preferences
AI configuration
working hours
appointment provider
storage provider

Secrets MUST remain in secret management rather than ordinary configuration tables.

⸻

80. OAuth Integrations

For OAuth-based integrations:

* state parameter must be validated
* authorization code must be protected
* redirect URI must be strict
* tokens must be securely stored
* scopes must be minimal
* refresh behavior must be handled
* disconnect/revoke must be supported

⸻

81. External IDs

External provider IDs SHOULD be stored separately from internal IDs.

Example:

internal_patient_id
telegram_user_id
instagram_user_id

Never assume external IDs are globally unique.

⸻

82. External Data Synchronization

When syncing data:

The system MUST distinguish:

authoritative local data
authoritative external data
derived synchronized data

Synchronization conflicts MUST have an explicit resolution strategy.

⸻

83. Integration Conflict Resolution

Example:

If clinic scheduling says:

19:00 unavailable

while an external cache says:

19:00 available

the authoritative source MUST win.

The system MUST NOT merge conflicting truth sources blindly.

⸻

84. Web API Security

All external API endpoints SHOULD use HTTPS in production.

Sensitive endpoints MUST NOT operate over unencrypted transport.

⸻

85. CORS

CORS SHOULD be restrictive.

Do not use:

Access-Control-Allow-Origin: *

for authenticated sensitive APIs unless there is a clear justified architecture.

⸻

86. API Keys

If Clinicos exposes API keys for integrations:

Keys SHOULD:

* be hashed or securely stored where practical
* have scopes
* have expiration
* support rotation
* be revocable
* be audited

⸻

87. API Key Scopes

Example:

patients:read
leads:read
appointments:read
appointments:write
analytics:read

Do not issue universal unrestricted API keys by default.

⸻

88. Public Endpoints

Public endpoints SHOULD be minimized.

If public access is necessary:

* rate limit
* validate inputs
* avoid sensitive data
* use anti-abuse controls
* monitor traffic

⸻

89. Integration Documentation

Every integration SHOULD document:

Purpose
Authentication
Required scopes
Endpoints
Payloads
Error behavior
Retry policy
Rate limits
Idempotency
Security
Monitoring
Disconnect process

⸻

90. Integration Lifecycle

Every integration SHOULD support:

Not connected
    ↓
Connecting
    ↓
Connected
    ↓
Degraded
    ↓
Disconnected
    ↓
Revoked

The exact states may vary.

⸻

91. Integration Disconnect

Disconnecting an integration SHOULD:

* revoke credentials where possible
* stop new event processing
* preserve historical business data where appropriate
* invalidate active tokens
* update integration status
* audit the operation

⸻

92. Integration Data Ownership

External systems MUST NOT silently become the source of truth for Clinicos data.

Every synchronized field MUST have an ownership rule.

Example:

Clinic service description
→ Clinicos authoritative
Telegram username
→ Telegram authoritative
Appointment slot
→ Scheduling source authoritative

⸻

93. Data Mapping

Each integration SHOULD define an explicit mapping:

External Object
      ↓
Normalizer
      ↓
Internal Domain Object

Do not scatter mapping logic across unrelated business modules.

⸻

94. Integration Adapters

Recommended conceptual structure:

integrations/
    telegram/
    instagram/
    whatsapp/
    ai/
    storage/
    notifications/
    appointments/

The exact repository structure MAY differ.

The architectural boundary matters more than the folder name.

⸻

95. Integration Testing

Every integration SHOULD have:

Unit tests

* payload parsing
* validation
* mapping
* error classification

Integration tests

* authentication
* real API behavior where feasible
* webhook handling
* retries
* rate limits

Failure tests

* timeout
* malformed response
* duplicate event
* provider outage
* invalid credential

⸻

96. Contract Testing

Where practical, external integrations SHOULD use contract tests.

This helps detect provider API changes before production failures.

⸻

97. Mocking

Mocks are useful for:

* unit tests
* deterministic failure scenarios
* local development

But mocks MUST NOT be treated as proof that a real external integration works.

Real integration verification is required where feasible.

⸻

98. Sandbox Environments

Use provider sandbox/test environments when available.

Production credentials MUST NOT be used for routine testing.

⸻

99. Integration Monitoring

Monitor:

* request count
* success rate
* failure rate
* latency
* rate limits
* retries
* authentication failures
* webhook failures
* provider availability

⸻

100. Integration Cost Monitoring

For paid integrations, monitor:

* requests
* tokens
* storage
* media processing
* SMS
* email
* provider fees

Cost spikes SHOULD trigger alerts where appropriate.

⸻

101. API Deprecation

Breaking API changes MUST have a deprecation strategy.

Prefer:

announce
↓
support old + new
↓
migrate clients
↓
measure usage
↓
remove old version

Do not remove external APIs without understanding who uses them.

⸻

102. Backward Compatibility

Integration changes SHOULD preserve compatibility when practical.

If breaking compatibility is unavoidable:

* version the API
* document migration
* provide transition period
* test both versions
* monitor adoption

⸻

103. API Documentation

Production APIs SHOULD have machine-readable documentation such as OpenAPI where appropriate.

Documentation SHOULD include:

* endpoints
* request schemas
* response schemas
* errors
* authentication
* permissions
* examples

⸻

104. API Contract Ownership

Each API contract SHOULD have a clear owner.

Changes SHOULD be reviewed against:

* product requirements
* security
* data model
* frontend/client needs
* integrations
* backward compatibility

⸻

105. API and Database Separation

API models MUST NOT automatically expose database models directly.

Prefer:

Database Model
      ↓
Domain Model
      ↓
API Response DTO

This prevents accidental exposure of internal fields.

⸻

106. Transaction Boundaries

API operations that perform multiple business changes MUST use appropriate transactions.

Example:

POST /appointments

may involve:

validate slot
reserve slot
create appointment
create event

The architecture MUST ensure consistent state.

⸻

107. Event-Driven Integration

Clinicos SHOULD increasingly use domain events.

Example:

lead.became_hot
      ↓
Automation Engine
      ├── notification
      ├── follow-up
      └── analytics

This reduces tight coupling.

⸻

108. Event Schema

Events SHOULD contain:

{
  "event_id": "...",
  "event_type": "lead.became_hot",
  "tenant_id": "...",
  "entity_type": "lead",
  "entity_id": "...",
  "occurred_at": "...",
  "correlation_id": "...",
  "actor": {},
  "payload": {}
}

Event payloads MUST NOT contain unnecessary sensitive information.

⸻

109. Event Versioning

Events SHOULD have versions.

Example:

lead.became_hot.v1
lead.became_hot.v2

or:

{
  "event_type": "lead.became_hot",
  "event_version": 1
}

Consumers MUST be able to handle expected versions.

⸻

110. Event Security

Events MUST respect tenant isolation.

Consumers MUST NOT process events for unauthorized tenants.

Sensitive event payloads SHOULD be minimized.

⸻

111. API Security Checklist

Before shipping an API:

* [ ]	Authentication
* [ ]	Authorization
* [ ]	Tenant isolation
* [ ]	Input validation
* [ ]	Output filtering
* [ ]	Rate limiting
* [ ]	Error handling
* [ ]	Logging
* [ ]	Request ID
* [ ]	Idempotency where required
* [ ]	Concurrency considerations
* [ ]	Security tests

⸻

112. Integration Security Checklist

Before shipping an integration:

* [ ]	Authentication verified
* [ ]	Credentials secured
* [ ]	Minimal scopes
* [ ]	Tenant mapping
* [ ]	External IDs mapped
* [ ]	Webhook verification
* [ ]	Replay protection
* [ ]	Idempotency
* [ ]	Retry strategy
* [ ]	Timeout
* [ ]	Rate limits
* [ ]	Failure handling
* [ ]	Monitoring
* [ ]	Disconnect/revocation

⸻

113. AI Integration Checklist

Before shipping an AI integration:

* [ ]	Provider abstraction
* [ ]	Secret management
* [ ]	Context minimization
* [ ]	Prompt injection protection
* [ ]	Structured output where appropriate
* [ ]	Output validation
* [ ]	Timeout
* [ ]	Retry policy
* [ ]	Fallback policy
* [ ]	Cost limits
* [ ]	Token tracking
* [ ]	Privacy review
* [ ]	Medical safety review
* [ ]	Observability

⸻

114. Channel Integration Checklist

Before shipping a new communication channel:

* [ ]	Adapter created
* [ ]	Identity mapping
* [ ]	Message normalization
* [ ]	Media handling
* [ ]	Webhook/event processing
* [ ]	Outgoing message capability
* [ ]	Error handling
* [ ]	Rate limits
* [ ]	Idempotency
* [ ]	Security
* [ ]	Tenant isolation
* [ ]	Monitoring

⸻

115. Current Repository Rule

The AI coding assistant MUST NOT assume that the current repository already follows this architecture.

Before modifying integrations:

1. inspect existing integration modules
2. identify current providers
3. inspect API routes
4. inspect webhook handlers
5. inspect database interactions
6. inspect environment variables
7. inspect authentication
8. inspect tests
9. compare current vs target
10. plan migration

⸻

116. Gap Classification

Differences SHOULD be classified:

MATCH
PARTIAL
MISSING
CONFLICT
LEGACY
UNKNOWN

No major integration refactor should happen without identifying its impact.

⸻

117. Implementation Strategy

For new integrations:

Define contract
↓
Define adapter
↓
Define authentication
↓
Define mapping
↓
Define error behavior
↓
Define idempotency
↓
Implement
↓
Unit test
↓
Integration test
↓
Failure test
↓
Security review
↓
Production verification

⸻

118. No Fake Integrations

The AI assistant MUST NOT claim:

Instagram connected

merely because:

* environment variables exist
* code was written
* mocks pass
* a button exists

A real integration is connected only when actual authentication and API communication have been verified.

⸻

119. No Fake Availability

The AI assistant MUST NOT claim:

appointment available

unless the authoritative scheduling system confirms it.

⸻

120. No Fake AI Success

The AI assistant MUST NOT claim:

AI provider working

based only on mocked responses.

Real provider verification is required for real integration claims.

⸻

121. No Secret Leakage

The AI assistant MUST never place:

* API keys
* tokens
* passwords
* private credentials

inside:

* source files
* documentation
* Markdown files
* test fixtures
* Notebook sources
* public GitHub repositories

⸻

122. Integration Failure Philosophy

When an external dependency fails:

Detect
↓
Classify
↓
Retry if safe
↓
Fallback if available
↓
Degrade safely
↓
Notify if necessary
↓
Record failure

Never hide an integration failure by returning fabricated success.

⸻

123. Target Integration Architecture

The target architecture is:

                         ┌─────────────────────┐
                         │ External Channels   │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
          Telegram              Instagram             Web
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Channel Adapters    │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Unified Message     │
                         │ / Identity Layer    │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Conversation       │
                         │ / Patient Domain    │
                         └──────────┬──────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Application / AI    │
                         │ Orchestration       │
                         └──────────┬──────────┘
                                    │
            ┌───────────────────────┼──────────────────────┐
            ▼                       ▼                      ▼
        Leads                 Appointments             Knowledge
            │                       │                      │
            └───────────────────────┼──────────────────────┘
                                    ▼
                           ┌─────────────────┐
                           │ Domain Events   │
                           └────────┬────────┘
                                    │
                  ┌─────────────────┼──────────────────┐
                  ▼                 ▼                  ▼
             Notifications      Analytics          Automation
AI Integration:
Application
     ↓
AI Service
     ↓
Provider Router
     ├── FreeLLMAPI
     ├── Future Provider A
     └── Future Provider B
Storage:
Application
     ↓
Storage Abstraction
     ↓
Private Object Storage
External Scheduling:
Application
     ↓
Appointment Abstraction
     ↓
Authoritative Scheduling System

⸻

124. Final Architectural Rules

The following rules are mandatory:

1. Core business logic MUST remain channel-independent.
2. External channels MUST use adapters.
3. Telegram MUST NOT become the architecture of the entire product.
4. Instagram MUST be treated as an additional channel, not a special business domain.
5. External provider failures MUST be expected.
6. External events MUST be idempotent.
7. APIs MUST be tenant-aware.
8. Authentication and authorization MUST remain separate concepts.
9. Authorization MUST be server-side.
10. Sensitive API responses MUST expose only authorized fields.
11. API contracts MUST be versionable.
12. Breaking changes MUST be controlled.
13. AI providers MUST remain abstracted.
14. FreeLLMAPI is a provider/gateway, not the core application architecture.
15. AI outputs MUST be validated.
16. AI MUST NOT invent business state.
17. AI MUST NOT invent appointment availability.
18. AI MUST NOT invent prices.
19. Long-running operations SHOULD use background jobs.
20. Webhooks MUST be verified and idempotent.
21. External IDs MUST remain separate from internal IDs.
22. Media storage MUST be private for sensitive files.
23. Secrets MUST never be committed or logged.
24. External integrations MUST be observable.
25. Real integrations MUST be tested against real providers when feasible.
26. Mocks MUST NOT be presented as real integration verification.
27. Integration failures MUST fail safely.
28. Current repository behavior MUST be inspected before refactoring.
29. Security and privacy requirements MUST override convenience.
30. The API architecture MUST support the long-term evolution of Clinicos into a multi-channel, AI-native, multi-tenant clinic operating system.

⸻

125. Final Objective

The API and integration architecture should allow Clinicos to evolve from:

Telegram-first AI assistant

into:

Multi-channel
AI-native
Multi-tenant
Clinic Operating System

without rewriting its core business domains every time a new:

* channel
* AI provider
* storage provider
* scheduling provider
* notification provider
* analytics system

is introduced.

The goal is:

Stable Core
+
Replaceable Integrations
+
Secure APIs
+
Observable External Boundaries
+
Provider Independence
+
Safe Failure

The current repository is an implementation starting point.

This specification defines the target API and integration architecture.

All future implementation MUST progressively move the system toward this architecture while preserving correctness, security, privacy, reliability, and product requirements.
