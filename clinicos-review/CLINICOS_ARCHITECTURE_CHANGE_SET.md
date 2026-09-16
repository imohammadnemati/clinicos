# Clinicos Architecture Change Set
## 1. Document Purpose
This document defines the authoritative architectural changes that supersede any conflicting provider, deployment, client, channel, or roadmap assumptions contained in earlier Clinicos specification documents.
The purpose of this document is to establish a controlled change set before the existing Clinicos specification suite is updated.
This document does not replace the existing Clinicos specifications.
Instead, it defines which architectural decisions have changed, which previous assumptions are no longer valid, and how all affected specifications must be updated.
---
# 2. Status
**Document Type:** Architecture Change Set  
**Status:** Authoritative  
**Scope:** Entire Clinicos platform  
**Applies To:** Product, architecture, AI, backend, frontend, infrastructure, security, testing, governance, documentation, and deployment  
**Priority:** Higher than conflicting assumptions in earlier specification documents  
**Version:** 1.0  
**Effective:** Immediately for all future architecture and implementation decisions
---
# 3. Architectural Authority
The following hierarchy defines architectural authority within the Clinicos documentation system.
When two documents contain conflicting architectural assumptions, the higher-level decision must take precedence.
The authority order is:
1. Current explicit product decisions
2. This Architecture Change Set
3. Clinicos Master Vision
4. Target Architecture
5. Product Requirements
6. Domain-specific specifications
7. Implementation details
8. Historical project documentation
9. Historical code assumptions
Historical implementation decisions must never override current architectural decisions.
---
# 4. Core Change Summary
Clinicos is undergoing two major structural changes.
## 4.1 AI Provider Strategy Change
Clinicos will use Google Gemini as the only AI provider during the current architecture lifecycle.
The target AI architecture must not depend on:
- FreeLLMAPI
- OpenRouter
- DeepSeek
- Qwen
- OpenAI
- Anthropic
- Groq
- Together AI
- Any other external AI provider
Google Gemini is the sole AI provider implementation.
However, Clinicos must preserve an internal AI abstraction layer so that the rest of the platform does not become tightly coupled to Gemini-specific implementation details.
The intended architecture is:
```text
Clinicos Core Platform
        |
        v
Clinicos AI Layer
        |
        v
Gemini AI Adapter
        |
        v
Google Gemini API

The architecture must not implement active multi-provider routing or provider fallback.

⸻

5. Client Roadmap Change

Clinicos will be developed through three client phases.

Phase 1

The only end-user interface is:

Telegram Bot

Phase 1 must prioritize the complete core business and AI capabilities required for the initial product.

No separate web application, Android application, iOS application, or Telegram Mini App is required for Phase 1.

⸻

Phase 2

Phase 2 adds:

Telegram Bot
Telegram Mini App

The Telegram Mini App must consume the same Clinicos backend and core platform services.

The Mini App must not duplicate core business logic.

⸻

Phase 3

Phase 3 adds:

Telegram Bot
Telegram Mini App
Web App
Android App
iOS App

All clients must consume the same platform-level APIs and domain services.

The architecture must avoid creating separate business logic implementations for individual clients.

⸻

6. Change Set Identifiers

The following changes are formally established.

ID	Change
CHANGE-001	Google Gemini is the only AI provider
CHANGE-002	FreeLLMAPI is removed from the target architecture
CHANGE-003	Multi-provider AI routing is removed from the target architecture
CHANGE-004	AI provider fallback is removed from the target architecture
CHANGE-005	Internal AI abstraction remains mandatory
CHANGE-006	Phase 1 is Telegram Bot only
CHANGE-007	Phase 2 adds Telegram Mini App
CHANGE-008	Phase 3 adds Web, Android, and iOS
CHANGE-009	Core Platform must remain client-independent
CHANGE-010	Communication Layer remains channel-agnostic
CHANGE-011	Business logic must not be implemented inside clients
CHANGE-012	Gemini-specific implementation must be isolated behind the AI layer
CHANGE-013	Provider-specific credentials must remain isolated
CHANGE-014	Dynamic operational truth must remain outside the LLM
CHANGE-015	AI provider replacement must remain technically possible
CHANGE-016	Client expansion must not require domain redesign
CHANGE-017	Existing specifications must be audited for conflicting assumptions
CHANGE-018	Historical provider architecture must not be treated as target architecture
CHANGE-019	Current implementation state must be distinguished from target architecture
CHANGE-020	Documentation must explicitly distinguish current state, target state, and future extensibility

⸻

7. CHANGE-001 — Google Gemini as the Sole AI Provider

Google Gemini is the only AI provider supported by the target Clinicos architecture.

All AI requests that leave the Clinicos platform must ultimately be routed to Google Gemini.

The target architecture must not contain active integrations with alternative LLM providers.

The following provider names must not appear as active target providers:

* FreeLLMAPI
* OpenRouter
* DeepSeek
* Qwen
* OpenAI
* Anthropic
* Groq
* Together AI
* Cohere
* Any equivalent third-party model provider

References to these providers may exist only in historical documentation or migration notes when necessary to explain legacy architecture.

⸻

8. CHANGE-002 — FreeLLMAPI Removal

FreeLLMAPI is no longer part of the target Clinicos architecture.

Any previous specification that describes FreeLLMAPI as:

* the primary AI gateway
* the primary model provider
* a routing provider
* a fallback provider
* an AI availability dependency
* a model-selection dependency

must be updated.

The final target architecture must not require FreeLLMAPI for normal operation.

⸻

9. CHANGE-003 — Removal of Multi-Provider Routing

Clinicos will not implement active multi-provider AI routing.

The following architecture is deprecated:

Provider A
Provider B
Provider C
Provider D
        |
        v
Provider Router

The target architecture is:

Clinicos AI Layer
        |
        v
Gemini Adapter
        |
        v
Google Gemini

There must be no provider scoring system whose purpose is to dynamically select between multiple LLM providers.

⸻

10. CHANGE-004 — Removal of AI Provider Fallback

Clinicos will not automatically switch to another AI provider when Gemini fails.

Examples of behavior that must not exist:

Gemini fails
    ->
DeepSeek

or:

Gemini fails
    ->
OpenRouter

or:

Gemini fails
    ->
FreeLLMAPI

Gemini failure must instead be handled through reliability mechanisms such as:

* retry policies
* exponential backoff
* timeout handling
* circuit breaking
* request prioritization
* graceful degradation
* deterministic templates
* human handoff
* queued processing
* temporary unavailability states

Provider substitution is not an operational fallback mechanism in the current architecture.

⸻

11. CHANGE-005 — AI Abstraction Must Remain

Removing multi-provider support does not mean removing the internal AI abstraction layer.

Clinicos must maintain a clean internal boundary between business logic and Gemini-specific API implementation.

Recommended structure:

AI Domain
    |
    +-- AI Orchestrator
    |
    +-- AI Gateway
            |
            +-- Gemini Adapter
                    |
                    +-- Google Gemini API

The rest of the platform must depend on Clinicos AI interfaces rather than directly importing Gemini SDK calls.

⸻

12. AI Abstraction Principles

The internal AI abstraction should define concepts such as:

* model request
* model response
* structured generation
* text generation
* multimodal generation
* token or usage metadata
* safety metadata
* latency metadata
* request correlation
* model configuration
* timeout
* retry behavior
* error classification

The abstraction must not expose unnecessary Gemini-specific concepts to unrelated business domains.

⸻

13. Gemini Adapter Boundary

The Gemini adapter is responsible for translating Clinicos AI requests into Gemini API requests.

It may contain:

* Gemini SDK usage
* Gemini authentication
* Gemini model identifiers
* Gemini-specific request formatting
* Gemini-specific response parsing
* Gemini-specific safety configuration
* Gemini-specific error mapping
* Gemini-specific usage metadata extraction

These details must remain inside the AI integration boundary.

⸻

14. Gemini Credential Isolation

Gemini API credentials must never be:

* hardcoded
* stored in source code
* stored in prompts
* exposed to clients
* returned through APIs
* stored in frontend code
* embedded in Telegram messages
* included in logs
* included in analytics payloads
* included in generated documentation

Credentials must be provided through secure server-side configuration.

⸻

15. AI Provider Independence Without Multi-Provider Runtime

The architecture must preserve replaceability without implementing multiple providers.

This means:

Current runtime:
Clinicos AI Layer
        |
        v
Gemini Adapter
        |
        v
Gemini

is valid.

The following is not required:

Gemini Adapter
OpenAI Adapter
DeepSeek Adapter
Qwen Adapter
Anthropic Adapter

The architecture should make future replacement technically possible without requiring such providers to exist today.

⸻

16. AI Model Selection

Clinicos may use different Gemini models for different workloads if required.

Model selection may be based on:

* task type
* latency requirements
* context requirements
* multimodal requirements
* reasoning requirements
* cost requirements
* quality requirements
* safety requirements

However, all models must belong to the Google Gemini ecosystem.

Model selection must not become provider selection.

⸻

17. AI Workload Routing

Clinicos may internally route different tasks to different Gemini models.

For example:

Simple classification
    ->
Gemini model optimized for latency
Complex reasoning
    ->
Gemini model optimized for reasoning
Image analysis
    ->
Gemini multimodal model
Long-context knowledge task
    ->
Gemini model optimized for context

This is model routing within one provider ecosystem.

It is not multi-provider routing.

⸻

18. AI Failure Handling

Gemini failures must be classified.

Possible categories include:

* authentication failure
* invalid request
* quota exhaustion
* rate limiting
* timeout
* network failure
* provider service failure
* malformed response
* safety block
* structured output failure
* internal validation failure

Each class must have deterministic handling.

⸻

19. AI Graceful Degradation

When AI is unavailable, Clinicos should degrade safely rather than inventing an answer.

Possible degradation strategies include:

* deterministic FAQ responses
* approved templates
* staff notification
* delayed processing
* queued response
* human takeover
* explicit temporary unavailability response
* safe refusal when appropriate

The system must never fabricate an AI result because Gemini is unavailable.

⸻

20. AI Cost Governance

Gemini usage must be observable and controllable.

Clinicos should track:

* request count
* model
* input usage
* output usage
* estimated cost where available
* latency
* success rate
* failure rate
* task type
* tenant
* feature
* agent
* environment

Cost optimization must not compromise medical safety or required response quality.

⸻

21. AI Observability

Every AI request should have a traceable internal identity.

Recommended metadata:

request_id
correlation_id
tenant_id
agent_id
task_type
model
environment
timestamp
latency
status
usage_metadata
failure_class

Sensitive content must be minimized in telemetry.

⸻

22. AI Safety Boundary

Gemini is a generation engine.

It is not the authoritative source of:

* appointment availability
* provider availability
* clinic hours
* current prices
* payment status
* booking status
* patient consent
* medical records
* medication status
* laboratory results
* treatment history
* clinic policy
* legal authorization

These facts must come from authoritative Clinicos domains or approved external systems.

⸻

23. Dynamic Truth Rule

AI-generated content must never be treated as operational truth merely because Gemini generated it.

The system must use authoritative sources for dynamic facts.

Correct architecture:

Authoritative System
        |
        v
Structured Data
        |
        v
AI Context
        |
        v
Gemini
        |
        v
Validated Response

Incorrect architecture:

Gemini
    |
    v
Assumed Operational Truth

⸻

24. Client Architecture Change

The client architecture is changing to a staged model.

The core platform must be built independently from the user interface.

The target architecture is:

                    Clinicos Core Platform
                             |
             +---------------+---------------+
             |               |               |
        Telegram Bot   Telegram Mini App   Other Clients
                                             |
                                   +---------+---------+
                                   |         |         |
                                  Web     Android     iOS

Not every client exists in every phase.

⸻

25. Phase 1 Definition

Phase 1 consists of:

Clinicos Core Platform
        |
        v
Telegram Bot

The Telegram Bot is the only external end-user client.

Phase 1 must focus on validating:

* patient interaction
* AI conversation
* lead management
* follow-up
* appointment workflows
* clinic operations
* staff workflows
* notifications
* knowledge access
* medical safety
* analytics
* AI evaluation
* core business workflows

⸻

26. Phase 1 Client Boundary

Telegram Bot must be treated as a client/channel.

It must not become the location of core business logic.

The bot may contain:

* Telegram update handling
* Telegram command parsing
* Telegram message formatting
* Telegram keyboard generation
* Telegram-specific interaction handling
* Telegram identity mapping
* Telegram media handling

The bot must not own:

* patient domain logic
* lead scoring logic
* appointment business rules
* follow-up policy
* medical safety decisions
* AI governance
* analytics calculations
* clinic policy
* authorization rules

⸻

27. Phase 2 Definition

Phase 2 adds:

Telegram Mini App

The architecture becomes:

Clinicos Core Platform
        |
        +-- Telegram Bot
        |
        +-- Telegram Mini App

Both clients must consume the same backend services.

⸻

28. Telegram Mini App Boundary

The Telegram Mini App is a presentation and interaction client.

It may provide richer interfaces such as:

* patient dashboards
* appointment views
* forms
* profile management
* lead-related interfaces
* clinic staff interfaces
* visual analytics
* image upload
* facial analysis workflows
* knowledge browsing
* structured workflows

Core business rules must remain server-side.

⸻

29. Phase 3 Definition

Phase 3 introduces:

* Web App
* Android App
* iOS App

The final client architecture becomes:

                    Clinicos Core Platform
                             |
       +---------------------+---------------------+
       |                     |                     |
 Telegram Clients       Web Application      Native Mobile
       |                                          |
  +----+----+                                +----+----+
  |         |                                |         |
 Bot     Mini App                          Android    iOS

⸻

30. Client-Neutral Backend

The Clinicos backend must expose client-neutral APIs.

APIs should represent domain capabilities rather than UI-specific behavior.

Preferred:

POST /appointments
GET /patients/{id}
POST /follow-ups
GET /leads
POST /conversations

Avoid:

POST /telegram/create-appointment
POST /ios/create-appointment
POST /android/create-appointment

unless a channel-specific endpoint is genuinely required by transport semantics.

⸻

31. Business Logic Location

Business logic must live in:

* domain services
* application services
* policy engines
* workflow engines
* authorization services
* backend modules

Business logic must not be duplicated across:

* Telegram Bot
* Telegram Mini App
* Web App
* Android App
* iOS App

⸻

32. Client Responsibilities

Clients should primarily handle:

* presentation
* user interaction
* local UI state
* input collection
* client-side validation for usability
* rendering
* navigation
* media capture
* authentication transport
* platform-specific capabilities

Server-side validation remains authoritative.

⸻

33. Server Authority

The server remains authoritative for:

* authentication
* authorization
* tenant isolation
* patient identity
* patient records
* appointments
* leads
* follow-ups
* clinic configuration
* consent
* medical safety
* AI decisions
* AI policy
* analytics
* audit
* billing state
* operational truth

⸻

34. Communication Layer Remains Channel-Agnostic

The Communication Layer must remain independent of the client roadmap.

Phase 1 may primarily use Telegram.

However, Communication Layer abstractions must not assume that Telegram is the only possible channel.

The architecture must support future channel adapters without redesigning business domains.

⸻

35. Channel Adapter Model

The target communication architecture remains:

Business Domain
       |
       v
Communication Request
       |
       v
Communication Policy
       |
       v
Communication Orchestrator
       |
       v
Channel Adapter
       |
       v
External Provider

Phase 1:

Telegram Adapter

Later:

Telegram Adapter
Instagram Adapter
WhatsApp Adapter
SMS Adapter
Email Adapter
Web Adapter
Push Adapter

Only channels actually implemented in a given phase are active.

⸻

36. Telegram as Phase 1 Channel

Telegram is the initial communication and interaction channel.

The initial implementation should prioritize:

* inbound messages
* outbound messages
* commands
* buttons
* inline interactions
* media
* documents
* voice messages where supported
* staff communication
* patient communication
* follow-up communication
* appointment communication

⸻

37. Telegram Does Not Define the Domain Model

Clinicos must not model its core domain around Telegram-specific concepts.

For example, a patient should not fundamentally be modeled as:

TelegramUser

Instead:

Patient
    |
    +-- ChannelIdentity
            |
            +-- TelegramIdentity

This allows additional channels later.

⸻

38. Unified Identity Model

A single person may interact through multiple channels.

The identity architecture must therefore support:

Person
 |
 +-- Telegram Identity
 +-- Web Identity
 +-- Android Identity
 +-- iOS Identity
 +-- Other Channel Identity

Channel identity must not automatically equal the clinical identity.

Identity linking must be controlled and auditable.

⸻

39. Conversation Architecture

Conversation logic must be channel-independent.

The system should normalize channel-specific input into a common internal representation.

Example:

Telegram Message
        |
        v
Telegram Adapter
        |
        v
Normalized Inbound Message
        |
        v
Conversation Domain
        |
        v
AI / Workflow / Human

⸻

40. AI and Client Separation

AI logic must not be embedded directly into client applications.

Incorrect:

Telegram Bot
    |
    +-- Gemini API

Correct:

Telegram Bot
    |
    v
Clinicos Backend
    |
    v
AI Layer
    |
    v
Gemini

The same rule applies to:

* Telegram Mini App
* Web App
* Android
* iOS

No client receives the Gemini API credential.

⸻

41. Direct Client-to-Gemini Requests

Direct client-to-Gemini communication is prohibited for Clinicos business workflows.

Clients must not directly invoke Gemini for:

* patient reasoning
* appointment decisions
* lead scoring
* follow-up decisions
* medical safety
* clinic knowledge
* staff workflows
* business workflows

All such requests must pass through the Clinicos AI layer.

⸻

42. Frontend AI Usage

Future clients may use local or UI-level AI features only if explicitly approved by the architecture.

Such features must not bypass Clinicos governance.

Any AI feature that affects:

* patient data
* medical interpretation
* clinic operations
* business decisions
* communication
* authorization

must use the governed Clinicos AI architecture.

⸻

43. Phase-Based Feature Strategy

The product roadmap must distinguish between:

1. Core platform capabilities
2. Phase 1 Telegram experience
3. Phase 2 Mini App experience
4. Phase 3 Web experience
5. Phase 3 mobile experiences

A capability should be implemented once in the core platform whenever possible.

The client layer should expose that capability through appropriate UX.

⸻

44. Core Platform Before Client Expansion

The architecture should prioritize building stable core services before duplicating functionality across clients.

Core domains should remain reusable across all phases.

Examples include:

* Identity
* Tenant Management
* Patient Intelligence
* Conversation
* Lead Management
* Follow-Up
* Appointments
* Knowledge
* Medical Safety
* AI
* Notifications
* Analytics
* Clinic Management
* Authentication
* Audit
* Observability

⸻

45. Client Expansion Rule

Adding a new client must not require rewriting core domain services.

The expected process is:

Existing Core API
        |
        v
New Client Adapter / UI

not:

New Client
        |
        v
New Business Logic
        |
        v
New Database Logic

⸻

46. API-First Client Architecture

The backend should expose stable APIs that can serve multiple clients.

The API layer should provide:

* authentication
* authorization
* resource access
* domain commands
* domain queries
* event-driven workflows where appropriate
* media upload
* AI task invocation through governed services

⸻

47. Client Authentication

Authentication mechanisms may differ by client.

Examples:

Telegram:
Telegram identity verification
Web:
Web authentication flow
Android:
Mobile authentication flow
iOS:
Mobile authentication flow

However, all clients must map into a unified Clinicos identity and authorization model.

⸻

48. Authorization Must Remain Centralized

Clients must never be trusted as the final authorization authority.

For example, hiding a UI button does not constitute authorization.

The backend must verify:

* user identity
* tenant membership
* role
* permissions
* resource ownership
* contextual authorization
* medical access restrictions

⸻

49. Tenant Isolation Across Clients

Tenant isolation must remain enforced server-side regardless of client.

The following clients must all respect identical tenant boundaries:

* Telegram Bot
* Telegram Mini App
* Web
* Android
* iOS

A client-specific implementation must never create a weaker tenant isolation boundary.

⸻

50. Medical Safety Across Clients

Medical safety policies are centralized.

A Telegram interaction and a future mobile interaction must not receive different safety decisions merely because they originated from different clients.

The Medical Safety domain remains authoritative.

⸻

51. Consent Across Clients

Consent must be represented centrally.

A consent decision made through one channel must be interpreted according to Clinicos consent rules.

Channel-specific consent must remain distinguishable.

For example:

Marketing Consent
    |
    +-- Telegram
    +-- SMS
    +-- Email

A Telegram consent must not automatically authorize unrelated channels.

⸻

52. Notification Architecture Across Phases

Notification business logic must remain independent of client presentation.

For example:

Appointment Reminder
        |
        v
Communication Policy
        |
        v
Available Channel

Phase 1 may deliver through Telegram.

Later phases may add:

* in-app notifications
* push notifications
* email
* SMS
* additional channels

without changing appointment domain logic.

⸻

53. Follow-Up Architecture Across Phases

Follow-Up Engine remains independent of clients.

A follow-up should be represented as a domain-level intention.

The system decides:

* whether a follow-up should occur
* when it should occur
* why it should occur
* whether consent allows it
* whether safety allows it
* which channel is appropriate

The client/channel layer then delivers it.

⸻

54. Appointment Architecture Across Phases

Appointment truth remains server-side.

Clients may:

* display appointments
* request appointment creation
* request rescheduling
* request cancellation

But the authoritative appointment domain determines whether the requested operation is valid.

⸻

55. Facial Analysis Architecture

Facial analysis must remain a backend capability.

Clients may provide:

* image capture
* image upload
* camera access
* upload progress
* visualization

But the analysis pipeline remains governed by the Clinicos backend and AI architecture.

The client must not contain authoritative medical or analytical logic.

⸻

56. Knowledge and RAG Architecture

Knowledge retrieval remains server-side.

Clients may submit queries.

The flow remains:

Client
   |
   v
Conversation / AI Layer
   |
   v
Knowledge Retrieval
   |
   v
Relevant Evidence
   |
   v
Gemini
   |
   v
Validated Response

The client must not independently construct authoritative clinical knowledge.

⸻

57. AI Agent Architecture

AI agents remain server-side.

Agents may include:

* Patient Intelligence Agent
* Conversation Agent
* Lead Agent
* Follow-Up Agent
* Knowledge Agent
* Secretary Copilot
* Reporting Agent
* Facial Analysis Agent
* Orchestrator

Agents must not be duplicated separately for Telegram, Web, Android, or iOS.

⸻

58. AI Agent Channel Independence

Agents should operate on normalized internal inputs.

Example:

Telegram
Web
Android
iOS
    |
    v
Normalized Interaction
    |
    v
Agent Orchestrator

This prevents channel-specific agent behavior from becoming part of the core architecture.

⸻

59. Agent Output Governance

Agent outputs must pass through the appropriate policy boundaries before causing external effects.

For example:

AI Agent
   |
   v
Policy Validation
   |
   v
Domain Action

AI agents must not directly mutate critical state without governed application-layer controls.

⸻

60. Historical Provider References

Historical documentation may contain references to:

* FreeLLMAPI
* DeepSeek
* Qwen
* OpenRouter
* OpenAI
* other providers

Such references may remain only when they are explicitly labeled as historical or deprecated.

They must not be presented as current target architecture.

Recommended terminology:

Historical Implementation

or:

Legacy Provider

or:

Deprecated Architecture

⸻

61. Current State vs Target State

Every specification that discusses implementation must clearly distinguish:

Current State
Target State
Future Extension
Historical State

This is especially important for AI providers and client architecture.

⸻

62. Repository Reality

The current repository may contain code that conflicts with the target architecture.

Such conflicts must not automatically cause the target architecture to change.

Instead:

Target Architecture
        |
        v
Implementation Gap
        |
        v
Migration Plan

The repository should eventually be migrated toward the approved target architecture.

⸻

63. Migration Principle

Migration should be performed deliberately.

The implementation team must not perform ad hoc changes merely to make the current repository appear consistent.

Every significant migration should identify:

* existing behavior
* target behavior
* affected modules
* data implications
* API implications
* security implications
* testing requirements
* rollback strategy

⸻

64. Provider Migration Strategy

If the current repository contains FreeLLMAPI or other providers, migration should follow:

Identify Provider Dependencies
        |
        v
Create / Confirm AI Abstraction
        |
        v
Implement Gemini Adapter
        |
        v
Move AI Workloads to Gemini
        |
        v
Remove Runtime Provider Routing
        |
        v
Remove Legacy Provider Dependencies
        |
        v
Run Full Test Suite
        |
        v
Verify Production Behavior

⸻

65. Provider Migration Safety

Legacy providers must not be deleted before the Gemini implementation has been validated.

The migration must verify:

* authentication
* request formatting
* response parsing
* structured output
* multimodal functionality
* timeout handling
* retry behavior
* rate-limit handling
* safety behavior
* usage tracking
* observability
* cost tracking
* failure classification

⸻

66. Provider Configuration

The final runtime configuration should be Gemini-centric.

Example conceptual configuration:

GEMINI_API_KEY
GEMINI_MODEL_DEFAULT
GEMINI_MODEL_FAST
GEMINI_MODEL_REASONING
GEMINI_MODEL_MULTIMODAL
GEMINI_TIMEOUT
GEMINI_MAX_RETRIES

Exact configuration names may differ in implementation.

No provider scoring configuration should remain.

⸻

67. Removal of Provider Scoring

Any Redis or database mechanism previously used for provider scoring must be treated as legacy if its sole purpose was multi-provider selection.

Examples include:

provider_score
provider_priority
provider_quota_score
provider_cooldown
provider_selection

Such mechanisms should not exist in the final Gemini-only architecture unless they serve a different, explicitly documented purpose.

⸻

68. Gemini Model Governance

The system may maintain internal model policies.

Example:

Task Type
    |
    v
Approved Gemini Model
    |
    v
AI Policy

The system should prevent arbitrary model selection by agents.

Model selection must remain governed.

⸻

69. AI Request Policy

Every AI request should be associated with:

* tenant
* actor
* feature
* task type
* agent
* model
* safety class
* data classification
* purpose

This supports:

* governance
* cost control
* observability
* auditing
* evaluation

⸻

70. AI Data Minimization

Only the minimum necessary data should be sent to Gemini.

The AI layer should support:

* context filtering
* field minimization
* sensitive data controls
* redaction where appropriate
* tenant isolation
* prompt construction policies

⸻

71. Prompt Architecture

Prompts must remain under Clinicos control.

Business rules must not be encoded solely in prompts.

Critical constraints must be enforced through deterministic application logic.

Correct:

Prompt
+
Policy Engine
+
Validation
+
Authoritative Data

Not:

Prompt Only

⸻

72. AI Output Validation

Gemini output must be validated before being used for:

* structured business actions
* communication
* patient-facing medical information
* staff recommendations
* workflow decisions

Validation may include:

* schema validation
* business-rule validation
* safety validation
* authorization validation
* source validation
* content validation

⸻

73. Client Roadmap Governance

The following roadmap is authoritative:

Phase 1
Telegram Bot
Phase 2
Telegram Bot
Telegram Mini App
Phase 3
Telegram Bot
Telegram Mini App
Web App
Android App
iOS App

Any specification describing a different initial client roadmap must be updated.

⸻

74. Phase 1 Completion Criteria

Phase 1 should not be considered complete merely because the Telegram Bot can send and receive messages.

Phase 1 completion should consider:

* core identity
* clinic tenancy
* patient workflows
* conversation
* AI
* lead management
* follow-up
* appointment workflows
* communication
* knowledge
* medical safety
* clinic management
* analytics
* observability
* security
* testing
* deployment
* reliability

The exact feature acceptance criteria are defined by the relevant domain specifications.

⸻

75. Phase 2 Completion Criteria

Phase 2 should demonstrate that the same core platform can serve both:

Telegram Bot
Telegram Mini App

without duplicating domain logic.

The Mini App should consume stable backend capabilities.

⸻

76. Phase 3 Completion Criteria

Phase 3 should demonstrate that the same core platform can serve:

Telegram Bot
Telegram Mini App
Web
Android
iOS

using a consistent domain and authorization model.

⸻

77. Client Feature Parity

Feature parity does not mean identical UI.

Different clients may provide different interaction patterns.

For example:

Telegram:
Conversational interaction
Mini App:
Structured workflow
Web:
Dashboard-oriented workflow
Mobile:
Native workflow

The underlying business rules must remain consistent.

⸻

78. Client-Specific Optimization

Each client may optimize:

* navigation
* interaction patterns
* rendering
* performance
* accessibility
* platform conventions
* notifications
* media capture

Client optimization must not modify authoritative business behavior.

⸻

79. API Versioning

As new clients are introduced, APIs must support controlled evolution.

Breaking API changes must be managed through:

* versioning
* compatibility windows
* migration plans
* deprecation policies

A new client must not force uncontrolled breaking changes for existing clients.

⸻

80. Backward Compatibility

Adding Phase 2 or Phase 3 clients must not break Phase 1 Telegram workflows without an intentional migration.

Telegram Bot must remain supported as a first-class client unless an explicit product decision changes the roadmap.

⸻

81. Channel Compatibility

The communication system must support channel capability discovery.

Different channels may have different capabilities:

* text
* media
* buttons
* documents
* voice
* interactive forms
* deep links
* rich UI

Business logic must not depend on one channel capability unless that capability is explicitly required.

⸻

82. Telegram-Specific Features

Telegram-specific functionality is allowed.

Examples:

* inline keyboards
* callback queries
* Telegram Mini App launch links
* Telegram user identity
* Telegram media
* Telegram bot commands

Such features must remain inside the Telegram integration boundary.

⸻

83. Mini App-Specific Features

Mini App-specific functionality is allowed.

Examples:

* Telegram WebApp APIs
* Mini App authentication integration
* Telegram-specific UI flows
* Telegram-specific navigation

These must not become core domain dependencies.

⸻

84. Web-Specific Features

Future Web App functionality may include:

* browser navigation
* desktop dashboards
* responsive UI
* browser notifications
* file upload
* richer reporting interfaces

These remain client concerns.

⸻

85. Mobile-Specific Features

Android and iOS may later support:

* native push notifications
* camera integration
* photo upload
* local caching
* biometric authentication
* native navigation
* offline-friendly UX where appropriate

Such features must integrate with the same backend authorization and domain services.

⸻

86. Offline Behavior

Future clients may implement offline UX.

However, offline state must never be treated as authoritative for critical clinical or operational data.

When synchronization occurs, the backend remains authoritative.

⸻

87. Synchronization

Future multi-client operation requires controlled synchronization.

The platform should define:

* timestamps
* versioning
* conflict handling
* idempotency
* event ordering
* synchronization state

This is particularly important when a user interacts through multiple clients.

⸻

88. Multi-Client Session Model

A single user may have simultaneous sessions.

Example:

Telegram
    +
Web
    +
Mobile

The platform must support consistent authorization and state handling.

Client sessions must not create separate patient identities without explicit identity-linking logic.

⸻

89. Notification Preference Model

Notification preferences must be centralized.

Users may have:

Preferred Language
Preferred Channel
Quiet Hours
Notification Types
Marketing Consent
Transactional Preferences

Channel-specific capabilities must still be respected.

⸻

90. AI Evaluation Across Clients

AI evaluation must distinguish between:

* AI model behavior
* prompt behavior
* agent behavior
* channel presentation
* client UX

A poor Telegram rendering issue must not be interpreted as an AI reasoning failure.

⸻

91. AI Quality Invariance

The core AI reasoning layer should remain client-independent.

Equivalent inputs should receive equivalent policy treatment regardless of whether the input originated from:

* Telegram
* Mini App
* Web
* Android
* iOS

Presentation may differ.

Policy must not.

⸻

92. Analytics Across Clients

Analytics should identify the client or channel where useful.

Recommended dimensions:

client_type
channel
platform
feature
tenant
role
workflow

Examples:

telegram_bot
telegram_mini_app
web
android
ios

This allows client-specific analytics without duplicating business metrics.

⸻

93. Observability Across Clients

Every request should support correlation across:

Client
    |
    v
API
    |
    v
Domain
    |
    v
AI
    |
    v
Communication
    |
    v
External Provider

Correlation identifiers should be preserved where technically possible.

⸻

94. Security Across Clients

Security controls must not vary arbitrarily by client.

All clients must enforce:

* authentication
* authorization
* tenant isolation
* secure transport
* input validation
* rate limiting
* auditability
* session management
* sensitive data protection

⸻

95. Client Trust Model

Clients are untrusted execution environments.

The backend must assume that:

* client code can be modified
* requests can be replayed
* hidden fields can be altered
* UI restrictions can be bypassed
* client state can be manipulated

Therefore, all security-critical checks must occur server-side.

⸻

96. AI Security Model

Gemini must never receive unrestricted authority over Clinicos systems.

The AI layer must operate through controlled tools and permissions.

AI should not have unrestricted access to:

* database
* secrets
* infrastructure
* arbitrary network services
* tenant data
* administrative operations

Tool access must be explicitly granted.

⸻

97. AI Tool Boundary

When an AI agent needs an external action, the preferred flow is:

Gemini
   |
   v
Structured Intent
   |
   v
Tool Permission Check
   |
   v
Application Service
   |
   v
Domain Validation
   |
   v
Action

Gemini output alone must never constitute authorization.

⸻

98. Human Override

Human staff must be able to intervene in appropriate workflows.

Human takeover must remain available regardless of client.

Examples include:

* conversation takeover
* follow-up cancellation
* message editing
* AI response rejection
* safety escalation
* appointment intervention

⸻

99. Kill Switches

Critical AI and communication capabilities must support operational shutdown.

Examples:

Disable AI
Disable outbound communication
Disable marketing
Disable a specific workflow
Disable a specific client
Disable a specific feature

Shutdown controls must not require removing the entire platform.

⸻

100. Disaster Recovery

AI provider failure must not be confused with total Clinicos platform failure.

If Gemini becomes unavailable:

Clinicos Core Platform
        |
        +-- remains operational
        |
        +-- deterministic workflows remain available
        |
        +-- non-AI features remain available
        |
        +-- AI-dependent workflows degrade safely

⸻

101. Business Continuity

The platform should continue essential deterministic operations even when AI is unavailable.

Examples:

* appointment management
* patient lookup
* clinic configuration
* staff access
* deterministic notifications
* existing records
* reporting based on stored data

AI-dependent operations may enter degraded states.

⸻

102. Data Architecture Impact

The AI provider change should not require storing provider-specific business state.

AI usage records should use provider-neutral internal concepts such as:

ai_request
ai_response
ai_usage
ai_task
ai_evaluation

Provider-specific metadata may exist inside integration-specific fields where necessary.

⸻

103. Database Provider Fields

If the existing database contains provider-specific routing fields, they must be reviewed.

Fields that exist solely to support multi-provider routing should be considered legacy.

Examples:

provider_score
provider_rank
provider_failover_count
provider_cooldown
provider_selection_reason

Such fields should not be retained in the target data model unless they have a new explicit purpose.

⸻

104. AI Auditability

The platform must preserve enough information to understand:

* which AI task ran
* which Gemini model was used
* which version of the AI policy was active
* which agent initiated the request
* what authoritative context was supplied
* what validation occurred
* whether a human approved the output
* what downstream action occurred

Sensitive content should be minimized according to privacy requirements.

⸻

105. Documentation Update Requirement

Every specification must be reviewed for:

* AI provider assumptions
* provider routing assumptions
* fallback assumptions
* client roadmap assumptions
* Telegram-only assumptions
* direct client-to-AI assumptions
* channel coupling
* duplicated business logic
* provider-specific configuration
* provider-specific database design

⸻

106. Required Documentation Terminology

Use:

Gemini
Google Gemini
Gemini Adapter
Clinicos AI Layer
AI Gateway
AI Abstraction
Telegram Bot
Telegram Mini App
Web App
Android App
iOS App
Core Platform
Communication Layer
Channel Adapter

Avoid describing alternative providers as active architecture.

⸻

107. Deprecated Terminology

The following terminology should be removed from current target architecture descriptions:

FreeLLMAPI Provider
FreeLLMAPI Gateway
Multi-provider LLM Router
LLM Provider Score
Provider Quota Router
Provider Failover
DeepSeek Primary Provider
OpenRouter Fallback
Qwen Fallback
OpenAI Fallback

Unless explicitly labeled as historical or deprecated.

⸻

108. Architecture Consistency Rule

No specification may independently redefine the AI provider strategy.

The AI strategy is defined centrally by this document and the updated AI Engineering and Target Architecture documents.

No domain document may reintroduce multi-provider runtime architecture.

⸻

109. Architecture Consistency for Clients

No domain document may assume:

Telegram = Clinicos

Instead:

Telegram = Initial Client / Channel
Clinicos = Core Platform

⸻

110. Domain Independence

The following domains must remain independent of client technology:

* Patient Intelligence
* Lead Management
* Follow-Up
* Appointments
* Knowledge
* Medical Safety
* AI
* Analytics
* Clinic Management
* Notifications
* Identity

⸻

111. Communication Independence

Communication must remain independent of business-domain implementation details.

Business domains express intent.

Communication determines delivery.

Channel adapters handle transport.

⸻

112. Architecture Flow

The preferred overall architecture is:

                       Clinicos Clients
                             |
        +--------------------+--------------------+
        |                    |                    |
   Telegram Bot        Telegram Mini App     Web / Mobile
        |                    |                    |
        +--------------------+--------------------+
                             |
                             v
                    API / Application Layer
                             |
                             v
                     Clinicos Core Domains
                             |
       +---------------------+---------------------+
       |                     |                     |
   AI Layer            Communication Layer     Domain Services
       |                     |                     |
       v                     v                     v
Gemini Adapter         Channel Adapters      Core Systems
       |
       v
Google Gemini

⸻

113. Request Flow

A typical AI-powered interaction should follow:

Client
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
Conversation / Domain Layer
    |
    v
AI Orchestrator
    |
    v
AI Policy
    |
    v
Gemini Adapter
    |
    v
Google Gemini
    |
    v
Output Validation
    |
    v
Domain / Communication Action
    |
    v
Audit + Observability
    |
    v
Client

⸻

114. Communication Flow

A typical outbound communication should follow:

Domain Event / Workflow
        |
        v
Communication Intent
        |
        v
Policy Validation
        |
        v
Message Composition
        |
        v
Safety / Consent Validation
        |
        v
Channel Selection
        |
        v
Channel Adapter
        |
        v
Telegram / Future Channel
        |
        v
Delivery Event
        |
        v
Audit / Analytics

⸻

115. Phase 1 End-to-End Architecture

Phase 1:

Patient / Staff
      |
      v
Telegram Bot
      |
      v
Clinicos API
      |
      +----------------------+
      |                      |
      v                      v
Core Domains             AI Layer
                              |
                              v
                         Gemini Adapter
                              |
                              v
                         Google Gemini

⸻

116. Phase 2 End-to-End Architecture

Phase 2:

                  +-- Telegram Bot
                  |
User ------------>+-- Telegram Mini App
                  |
                  v
            Clinicos Core API
                  |
       +----------+----------+
       |                     |
       v                     v
 Core Domains            AI Layer
                             |
                             v
                        Gemini Adapter
                             |
                             v
                        Google Gemini

⸻

117. Phase 3 End-to-End Architecture

Phase 3:

                         +-- Telegram Bot
                         |
                         +-- Telegram Mini App
                         |
User --------------------+-- Web App
                         |
                         +-- Android App
                         |
                         +-- iOS App
                                  |
                                  v
                           Clinicos Core API
                                  |
                +-----------------+-----------------+
                |                 |                 |
                v                 v                 v
           Core Domains       AI Layer       Communication
                                  |                 |
                                  v                 v
                           Gemini Adapter      Channel Adapters
                                  |
                                  v
                           Google Gemini

⸻

118. Architectural Invariants

The following statements are mandatory invariants.

INVARIANT-001

Google Gemini is the only active AI provider.

INVARIANT-002

No multi-provider AI runtime is required.

INVARIANT-003

No automatic provider fallback exists.

INVARIANT-004

The AI abstraction layer remains.

INVARIANT-005

Gemini credentials remain server-side.

INVARIANT-006

Clients never directly control Gemini.

INVARIANT-007

Phase 1 is Telegram Bot only.

INVARIANT-008

Phase 2 adds Telegram Mini App.

INVARIANT-009

Phase 3 adds Web, Android, and iOS.

INVARIANT-010

Core business logic is client-independent.

INVARIANT-011

Communication remains channel-agnostic.

INVARIANT-012

Telegram-specific logic remains inside Telegram integration boundaries.

INVARIANT-013

AI cannot become the source of operational truth.

INVARIANT-014

AI output does not equal authorization.

INVARIANT-015

Critical business rules remain deterministic.

INVARIANT-016

Tenant isolation is server-side.

INVARIANT-017

Medical safety is centralized.

INVARIANT-018

Consent is centralized.

INVARIANT-019

Historical provider architecture must not override current architecture.

INVARIANT-020

Adding a client must not require duplicating domain logic.

⸻

119. Migration Checklist — AI

Before considering the AI migration complete:

* [ ]	Gemini adapter exists
* [ ]	AI abstraction exists
* [ ]	Gemini authentication is server-side
* [ ]	All active AI workloads use Gemini
* [ ]	FreeLLMAPI runtime dependency removed
* [ ]	OpenRouter runtime dependency removed
* [ ]	DeepSeek runtime dependency removed
* [ ]	Qwen runtime dependency removed
* [ ]	OpenAI runtime dependency removed
* [ ]	Multi-provider router removed
* [ ]	Provider scoring removed
* [ ]	Provider fallback removed
* [ ]	Gemini failures have deterministic handling
* [ ]	AI usage is observable
* [ ]	AI cost is observable
* [ ]	AI requests are auditable
* [ ]	AI output validation exists
* [ ]	Safety policies remain active
* [ ]	AI credentials are not exposed to clients
* [ ]	Tests cover Gemini failures
* [ ]	Production configuration uses Gemini only

⸻

120. Migration Checklist — Phase 1

Before Phase 1 completion:

* [ ]	Telegram Bot integration works
* [ ]	Telegram identity mapping works
* [ ]	Inbound messages are normalized
* [ ]	Outbound communication is governed
* [ ]	AI requests pass through the backend
* [ ]	Gemini is used through the AI layer
* [ ]	Business logic is server-side
* [ ]	Patient workflows work
* [ ]	Lead workflows work
* [ ]	Follow-up workflows work
* [ ]	Appointment workflows work
* [ ]	Medical safety is enforced
* [ ]	Consent is enforced
* [ ]	Audit logs exist
* [ ]	Observability exists
* [ ]	Tenant isolation is verified
* [ ]	Security tests pass
* [ ]	Reliability tests pass

⸻

121. Migration Checklist — Phase 2

Before Phase 2 completion:

* [ ]	Telegram Mini App exists
* [ ]	Mini App authentication is secure
* [ ]	Mini App uses core APIs
* [ ]	No duplicated domain logic exists
* [ ]	Telegram Bot remains operational
* [ ]	Shared identity model works
* [ ]	Shared authorization works
* [ ]	Shared tenant isolation works
* [ ]	Shared analytics works
* [ ]	Shared audit model works
* [ ]	Shared AI architecture works

⸻

122. Migration Checklist — Phase 3

Before Phase 3 completion:

* [ ]	Web App exists
* [ ]	Android App exists
* [ ]	iOS App exists
* [ ]	All clients use core APIs
* [ ]	Authorization is centralized
* [ ]	Tenant isolation is consistent
* [ ]	Patient identity is unified
* [ ]	AI access remains centralized
* [ ]	Communication remains governed
* [ ]	Analytics identifies client type
* [ ]	Audit records identify client context
* [ ]	Cross-client synchronization is defined
* [ ]	API versioning is operational
* [ ]	Security controls are consistent

⸻

123. Documentation Audit Checklist

Every Clinicos specification must be checked for:

* [ ]	FreeLLMAPI references
* [ ]	DeepSeek references
* [ ]	Qwen references
* [ ]	OpenRouter references
* [ ]	OpenAI references
* [ ]	Anthropic references
* [ ]	Multi-provider routing
* [ ]	Provider scoring
* [ ]	Provider fallback
* [ ]	Provider-specific business logic
* [ ]	Telegram-only domain assumptions
* [ ]	Direct client-to-Gemini access
* [ ]	Client-side business logic
* [ ]	Duplicated domain logic
* [ ]	Incorrect phase roadmap
* [ ]	Channel-specific domain coupling
* [ ]	Missing client abstraction
* [ ]	Missing AI abstraction
* [ ]	Incorrect operational truth assumptions

⸻

124. Specification Update Rules

When updating existing specifications:

1. Preserve valid domain requirements.
2. Remove contradictory provider assumptions.
3. Remove contradictory client roadmap assumptions.
4. Preserve internal AI abstraction.
5. Preserve channel abstraction.
6. Preserve safety and privacy requirements.
7. Preserve tenant isolation.
8. Preserve auditability.
9. Preserve observability.
10. Preserve future extensibility.
11. Clearly distinguish current implementation from target architecture.
12. Do not introduce new providers unless the architecture is explicitly changed again.
13. Do not introduce new clients before their defined roadmap phase.
14. Do not move business logic into clients.

⸻

125. Specification Impact Classification

Each existing specification should be classified as:

HIGH IMPACT

Requires substantial rewriting because it directly defines:

* AI architecture
* provider architecture
* client architecture
* product roadmap
* communication architecture
* deployment assumptions

MEDIUM IMPACT

Requires targeted review because it may contain:

* provider references
* client assumptions
* AI configuration
* infrastructure assumptions

LOW IMPACT

Requires verification but should largely remain unchanged if no conflicting assumptions exist.

⸻

126. High-Impact Documents

The following documents require substantial review:

CLINICOS_MASTER_VISION.md
CLINICOS_PRODUCT_REQUIREMENTS.md
CLINICOS_TARGET_ARCHITECTURE.md
CLINICOS_AI_ENGINEERING_SPEC.md
CLINICOS_API_AND_INTEGRATION_SPEC.md
CLINICOS_AI_AGENT_ARCHITECTURE_SPEC.md
CLINICOS_KNOWLEDGE_AND_RAG_SPEC.md
CLINICOS_CONVERSATIONAL_AI_SPEC.md
CLINICOS_FOLLOW_UP_ENGINE_SPEC.md
CLINICOS_NOTIFICATION_AND_COMMUNICATION_SPEC.md
CLINICOS_PRODUCT_UX_SPEC.md
CLINICOS_AI_EVALUATION_AND_MODEL_GOVERNANCE_SPEC.md
CLINICOS_CLINIC_OPERATING_MODEL.md
CLINICOS_PLATFORM_GOVERNANCE_SPEC.md
CLINICOS_DEPLOYMENT_AND_INFRASTRUCTURE_SPEC.md

⸻

127. Medium-Impact Documents

The following documents require targeted review:

CLINICOS_DATA_AND_DATABASE_SPEC.md
CLINICOS_SECURITY_AND_PRIVACY_SPEC.md
CLINICOS_TESTING_AND_QUALITY_SPEC.md
CLINICOS_AUTOMATION_AND_EVENT_ENGINE_SPEC.md
CLINICOS_FACIAL_ANALYSIS_SPEC.md
CLINICOS_MEDICAL_SAFETY_SPEC.md
CLINICOS_PATIENT_INTELLIGENCE_SPEC.md
CLINICOS_CLINIC_MANAGEMENT_SPEC.md
CLINICOS_ANALYTICS_AND_REPORTING_SPEC.md
CLINICOS_OBSERVABILITY_AND_RELIABILITY_SPEC.md
CLINICOS_DISASTER_RECOVERY_AND_BUSINESS_CONTINUITY_SPEC.md

These documents must be changed only where contradictions exist.

⸻

128. Low-Impact Documents

Any remaining specification that contains neither:

* AI provider assumptions
* multi-provider architecture
* client roadmap assumptions
* Telegram-specific domain coupling

may remain unchanged after verification.

However, it must still be checked against this change set.

⸻

129. No Unnecessary Rewriting

A specification must not be rewritten merely because the architecture changed elsewhere.

Only affected sections should be updated when possible.

This reduces documentation drift and preserves established domain requirements.

⸻

130. Cross-Document Consistency

After all updates, the specification suite must contain one consistent architecture.

The following statements must be true across all documents:

Gemini is the only active AI provider.
Telegram Bot is the Phase 1 client.
Telegram Mini App is introduced in Phase 2.
Web, Android, and iOS are introduced in Phase 3.
Core business logic is client-independent.
Communication remains channel-agnostic.
AI remains behind an internal abstraction.
Dynamic operational truth comes from authoritative systems.
AI output does not equal authorization.
Medical safety remains centralized.

⸻

131. Forbidden Architectural Regressions

The following regressions are prohibited unless this change set is explicitly superseded.

Regression 1

Reintroducing FreeLLMAPI as an active provider.

Regression 2

Reintroducing provider scoring.

Regression 3

Reintroducing multi-provider failover.

Regression 4

Allowing clients to call Gemini directly.

Regression 5

Making Telegram the core domain model.

Regression 6

Implementing separate business logic for Web, Android, or iOS.

Regression 7

Allowing AI to determine operational truth without authoritative data.

Regression 8

Allowing AI output to bypass authorization or policy validation.

Regression 9

Creating client-specific versions of the same domain workflow.

Regression 10

Introducing Phase 3 clients into Phase 1 as mandatory architecture.

⸻

132. Future Provider Expansion

Future support for another AI provider is not prohibited permanently.

However, it requires an explicit architecture change.

It must not be introduced implicitly through implementation.

If a future provider is added, the architecture must define:

* provider abstraction
* provider adapter
* security model
* routing policy
* failure policy
* cost governance
* evaluation framework
* data governance
* observability
* testing
* migration strategy

Until such a change is approved, Gemini remains the sole provider.

⸻

133. Future Channel Expansion

Future channels may be added without changing the core product architecture.

New channels should implement the Communication Layer contracts.

Examples may include:

* Instagram
* WhatsApp
* SMS
* Email
* Voice
* additional messaging platforms

Such additions must not require rewriting domain logic.

⸻

134. Future Client Expansion

Future clients beyond Phase 3 may be added if required.

Any new client must follow the same principles:

* client independence
* centralized authorization
* shared domain services
* shared AI layer
* shared communication layer
* shared identity
* shared analytics
* shared audit

⸻

135. Architectural Philosophy

Clinicos is not a Telegram Bot with additional features.

Clinicos is a clinic operating platform whose first interface is Telegram.

Clinicos is not a Gemini wrapper.

Clinicos is an AI-native clinic operating platform whose current AI implementation uses Gemini.

The distinction is fundamental.

⸻

136. Product Architecture Principle

The product should be designed around:

Core Platform First
Clients Second

not:

Client First
Backend Around Client

⸻

137. AI Architecture Principle

The AI architecture should be designed around:

Governed AI Layer
        |
        v
Gemini

not:

Business Logic
        |
        v
Direct LLM API Calls

⸻

138. Communication Architecture Principle

Communication should be designed around:

Business Intent
        |
        v
Policy
        |
        v
Communication
        |
        v
Channel

not:

Business Logic
        |
        v
Telegram API

⸻

139. Client Architecture Principle

Clients should be designed around:

Client
   |
   v
API
   |
   v
Core Platform

not:

Client
   |
   +-- duplicated domain logic
   +-- duplicated database logic
   +-- duplicated AI logic

⸻

140. Source of Truth Principle

The following systems remain authoritative:

Patient Data
    -> Patient Domain
Appointments
    -> Appointment Domain
Consent
    -> Consent / Privacy Domain
Medical Safety
    -> Medical Safety Domain
Clinic Configuration
    -> Clinic Management Domain
Communication Delivery
    -> Communication Layer
AI Execution
    -> AI Layer
Analytics
    -> Analytics Domain

Gemini is not the source of truth for these domains.

⸻

141. AI Role

Gemini should be treated as a controlled intelligence capability.

It may:

* understand
* classify
* summarize
* reason
* generate
* extract
* transform
* analyze images where approved
* assist staff
* assist patients
* assist workflows

It must operate within Clinicos policy and domain boundaries.

⸻

142. Deterministic Core

Clinicos must preserve deterministic systems for:

* authentication
* authorization
* consent
* scheduling
* appointment state
* payment state
* tenant isolation
* safety gates
* communication policy
* audit
* data validation
* workflow state

AI augments these systems rather than replacing them.

⸻

143. Final Architecture Contract

The current Clinicos architecture is formally defined as:

                    CLINICOS
                       |
             +---------+---------+
             |                   |
        Core Platform        Client Layer
             |                   |
             |          +--------+--------+
             |          |        |        |
             |       Telegram  Mini App  Web/Mobile
             |
       +-----+---------------------------+
       |         |         |             |
     Domains    AI    Communication   Platform
                 |          |
                 v          v
             Gemini      Channels

The active AI provider is:

Google Gemini

The initial client is:

Telegram Bot

The second-phase client is:

Telegram Mini App

The third-phase clients are:

Web
Android
iOS

⸻

144. Final AI Contract

Clinicos must satisfy all of the following:

AI Abstraction exists
        +
Gemini Adapter exists
        +
Google Gemini is the sole active provider
        +
No provider scoring
        +
No provider failover
        +
No FreeLLMAPI runtime dependency
        +
No direct client-to-Gemini access
        +
AI output validation
        +
AI safety governance
        +
AI observability
        +
AI cost governance

⸻

145. Final Client Contract

Clinicos must satisfy:

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

All clients must use:

Shared Core Platform
Shared APIs
Shared Domain Logic
Shared Authorization
Shared Identity
Shared AI Layer
Shared Communication Layer
Shared Audit
Shared Observability

⸻

146. Final Non-Negotiable Rules

1. Gemini is the only active AI provider.
2. FreeLLMAPI is not part of the target runtime architecture.
3. Multi-provider routing is not part of the target runtime architecture.
4. Automatic AI provider fallback is not part of the target runtime architecture.
5. The internal AI abstraction layer remains mandatory.
6. Gemini credentials remain server-side.
7. Clients must not directly call Gemini for governed Clinicos workflows.
8. Phase 1 is Telegram Bot only.
9. Phase 2 adds Telegram Mini App.
10. Phase 3 adds Web, Android, and iOS.
11. Core business logic remains client-independent.
12. Communication remains channel-agnostic.
13. Telegram-specific logic remains isolated to Telegram integration boundaries.
14. AI agents remain server-side.
15. Medical safety remains centralized.
16. Consent remains centralized.
17. Tenant isolation remains server-side.
18. Dynamic operational truth comes from authoritative systems.
19. AI output does not equal authorization.
20. Historical implementation details must not override target architecture.
21. Adding a client must not require duplicating domain logic.
22. Adding a new provider requires an explicit architecture change.
23. Adding a new channel must use the Communication Layer abstraction.
24. All affected specifications must be audited for consistency.
25. The final specification suite must describe one coherent architecture.

⸻

147. Final Validation Checklist

Before considering the architecture migration complete, verify:

AI

* [ ]	Gemini is the only active AI provider
* [ ]	Gemini Adapter exists
* [ ]	AI abstraction exists
* [ ]	No FreeLLMAPI dependency remains
* [ ]	No OpenRouter dependency remains
* [ ]	No DeepSeek dependency remains
* [ ]	No Qwen dependency remains
* [ ]	No OpenAI dependency remains
* [ ]	No multi-provider router remains
* [ ]	No provider scoring remains
* [ ]	No provider fallback remains
* [ ]	Gemini credentials are server-side
* [ ]	AI requests are observable
* [ ]	AI outputs are validated
* [ ]	AI costs are measurable
* [ ]	AI failures degrade safely

Client Roadmap

* [ ]	Phase 1 is Telegram Bot only
* [ ]	Phase 2 adds Telegram Mini App
* [ ]	Phase 3 adds Web
* [ ]	Phase 3 adds Android
* [ ]	Phase 3 adds iOS
* [ ]	Core platform remains client-independent
* [ ]	Business logic is not duplicated
* [ ]	Authorization is centralized
* [ ]	Identity is centralized
* [ ]	Tenant isolation is centralized

Communication

* [ ]	Communication Layer remains channel-agnostic
* [ ]	Telegram is implemented as a channel adapter
* [ ]	Business domains do not directly depend on Telegram transport
* [ ]	Future channels can be added without domain redesign

Safety

* [ ]	Medical safety remains centralized
* [ ]	Consent remains centralized
* [ ]	AI cannot bypass safety gates
* [ ]	AI cannot bypass authorization
* [ ]	AI cannot invent operational truth
* [ ]	Sensitive data handling remains governed

Documentation

* [ ]	All high-impact specifications are updated
* [ ]	All medium-impact specifications are reviewed
* [ ]	Historical provider references are labeled
* [ ]	Phase roadmap is consistent across documents
* [ ]	No specification contradicts this change set
* [ ]	Target architecture and implementation state are clearly distinguished

⸻

148. Final Decision Record

The following decisions are considered approved architectural decisions for the current Clinicos roadmap:

Decision A — AI Provider

Clinicos will use Google Gemini as its sole active AI provider.

Decision B — AI Architecture

Clinicos will retain an internal AI abstraction and Gemini adapter.

Decision C — Provider Strategy

Clinicos will not implement active multi-provider routing or automatic provider failover.

Decision D — Initial Client

Clinicos Phase 1 will use Telegram Bot as the only end-user client.

Decision E — Second Client Phase

Clinicos Phase 2 will introduce Telegram Mini App.

Decision F — Multi-Platform Phase

Clinicos Phase 3 will introduce Web, Android, and iOS clients.

Decision G — Core Platform

Clinicos Core Platform will remain independent from individual clients.

Decision H — Communication

Clinicos Communication Layer will remain channel-agnostic.

Decision I — Business Logic

Business logic will remain in the backend and domain/application layers rather than in clients.

Decision J — Future Extensibility

The architecture will preserve future provider and client extensibility without implementing those alternatives prematurely.

⸻

149. Closing Architecture Statement

Clinicos is an AI-native clinic operating platform.

Its current intelligence layer is powered exclusively by Google Gemini.

Its initial user interface is Telegram Bot.

Its roadmap expands first to Telegram Mini App and later to Web, Android, and iOS.

The platform core must remain independent from both the AI provider implementation and the client presentation layer.

The architecture therefore follows this fundamental structure:

                     CLINICOS CORE
                          |
        +-----------------+-----------------+
        |                 |                 |
   Domain Services    AI Layer      Communication Layer
                          |                 |
                          v                 v
                    Gemini Adapter     Channel Adapters
                          |                 |
                          v                 v
                       Gemini          Telegram / Future

The objective is not to build a Telegram application around Gemini.

The objective is to build a durable clinic operating platform in which Telegram is the first interface and Gemini is the current intelligence provider.

This distinction must remain preserved throughout implementation, documentation, testing, deployment, and future expansion.
