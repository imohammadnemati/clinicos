# CLINICOS — TARGET ARCHITECTURE
## Document Status
- Document Type: Target Software Architecture Specification
- Product: Clinicos
- Version: 1.0
- Status: Target Architecture
- Purpose: Define the architectural destination of Clinicos
- Source of Truth: This document describes the desired architecture, not the current repository implementation.
---
# 1. ARCHITECTURAL OBJECTIVE
Clinicos must evolve into a modular, reliable, AI-native, multi-tenant platform for aesthetic and medical-aesthetic clinics.
The architecture must support:
- AI-powered conversations
- patient intelligence
- lead intelligence
- follow-up automation
- appointment management
- clinic knowledge
- medical safety
- facial analysis
- staff copilots
- analytics
- reporting
- notifications
- automation
- multiple communication channels
- multiple AI providers
- future multi-agent capabilities
The architecture must allow these capabilities to evolve independently without turning the entire codebase into one tightly coupled system.
---
# 2. CORE ARCHITECTURAL PRINCIPLES
## 2.1 Modularity
Each major business capability should have a clear boundary.
Examples:
- Identity
- Patients
- Conversations
- Leads
- Follow-ups
- Appointments
- Knowledge
- AI
- Medical Safety
- Facial Analysis
- Notifications
- Analytics
- Reporting
- Clinic Management
- Authentication
A change inside one domain should not unnecessarily break unrelated domains.
---
## 2.2 Separation of Concerns
The following concerns must remain separate:
- transport
- business logic
- data access
- AI orchestration
- external integrations
- background jobs
- domain rules
- security
- analytics
A Telegram handler should not contain complex lead-scoring logic.
A database model should not contain AI orchestration.
An AI provider implementation should not contain appointment business rules.
---
## 2.3 Domain-Driven Organization
The system should be organized around business domains rather than around technical files alone.
The architecture should make it obvious where functionality belongs.
Example:
```text
Patient Domain
Lead Domain
Appointment Domain
Knowledge Domain
AI Domain
Facial Analysis Domain
Notification Domain
Analytics Domain

⸻

3. HIGH-LEVEL SYSTEM

The target architecture can conceptually be represented as:

                    ┌─────────────────────┐
                    │   Client Channels   │
                    │                     │
                    │ Telegram            │
                    │ Instagram           │
                    │ Web                 │
                    │ Future Channels      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Communication Layer │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Identity Resolution │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conversation Layer  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐   ┌────────────┐   ┌─────────────┐
        │ Patient   │   │ Lead       │   │ Appointment │
        │Intelligence│  │Intelligence│   │   Engine    │
        └───────────┘   └────────────┘   └─────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ AI Orchestration    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐   ┌────────────┐   ┌─────────────┐
        │ Knowledge │   │ Safety     │   │ Vision /    │
        │ System    │   │ Layer      │   │ Facial AI   │
        └───────────┘   └────────────┘   └─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Automation / Events │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌───────────┐   ┌────────────┐   ┌─────────────┐
        │Notification│  │ Analytics  │   │ Reporting   │
        └───────────┘   └────────────┘   └─────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Persistent Storage  │
                    └─────────────────────┘

This diagram represents conceptual boundaries, not mandatory implementation technology.

⸻

4. ARCHITECTURAL LAYERS

The target system should conceptually contain the following layers.

Layer 1 — Channel / Interface

Responsible for:

* Telegram
* Instagram
* Web
* future channels
* API clients
* admin interfaces

This layer translates external requests into internal commands/events.

It should NOT contain core business logic.

⸻

Layer 2 — Application Layer

Responsible for orchestrating use cases.

Examples:

* Process patient message
* Create lead
* Qualify lead
* Schedule follow-up
* Request appointment
* Book appointment
* Generate facial analysis
* Generate weekly report
* Approve knowledge candidate

The application layer coordinates domains but should avoid becoming a giant “god service”.

⸻

Layer 3 — Domain Layer

Contains core business rules.

Examples:

* Lead scoring
* Patient lifecycle
* Follow-up rules
* Appointment rules
* Knowledge states
* Facial-analysis eligibility
* notification priorities

Domain rules should not depend directly on Telegram or a specific AI provider.

⸻

Layer 4 — Infrastructure Layer

Contains external implementations:

* PostgreSQL
* Redis
* Telegram API
* Instagram API
* AI providers
* object storage
* scheduling integrations
* email/SMS providers
* observability tools

Infrastructure should implement interfaces required by the application/domain layers.

⸻

5. DOMAIN MODULES

The target architecture should contain clear modules.

⸻

5.1 Clinic Management

Responsibilities:

* clinic
* branches
* services
* doctors
* staff
* working hours
* policies
* configuration
* tenant settings

⸻

5.2 Identity & Authentication

Responsibilities:

* users
* roles
* permissions
* authentication
* authorization
* session management
* channel identities
* identity resolution

Roles may include:

* owner
* doctor
* secretary
* patient
* admin/system roles

⸻

5.3 Patient Intelligence

Responsibilities:

* patient profiles
* patient lifecycle
* preferences
* language
* interaction history
* patient memory
* patient segmentation
* patient prioritization

⸻

5.4 Communication

Responsibilities:

* inbound messages
* outbound messages
* channel abstraction
* conversation state
* attachments
* media
* delivery status

The communication domain should not assume that Telegram is the only channel.

⸻

5.5 Lead Management

Responsibilities:

* lead creation
* qualification
* scoring
* status
* hot-lead detection
* assignment
* conversion
* lost lead
* recovery

⸻

5.6 Follow-up

Responsibilities:

* follow-up tasks
* scheduling
* triggers
* reminders
* completion
* cancellation
* recovery workflows

⸻

5.7 Appointment

Responsibilities:

* appointment requests
* availability
* booking
* rescheduling
* cancellation
* reminders
* doctor assignment
* service assignment
* appointment lifecycle

The appointment domain must use an authoritative availability source.

⸻

5.8 Knowledge

Responsibilities:

* clinic knowledge
* FAQs
* services
* prices
* policies
* knowledge candidates
* approval
* versioning
* deprecation
* retrieval

⸻

5.9 Medical Safety

Responsibilities:

* safety rules
* high-risk detection
* escalation
* emergency handling
* medical boundary enforcement

Medical Safety should be able to operate as a protective layer around AI behavior.

⸻

5.10 AI Platform

Responsibilities:

* model abstraction
* provider abstraction
* task routing
* prompt management
* context construction
* response validation
* fallback
* token/cost tracking
* AI observability

⸻

5.11 Facial Analysis

Responsibilities:

* image intake
* consent
* quality validation
* face detection
* landmarks
* measurements
* AI interpretation
* visualizations
* reports
* usage limits
* before/after

⸻

5.12 Notification

Responsibilities:

* notification creation
* prioritization
* delivery
* preferences
* escalation
* role-based routing

⸻

5.13 Analytics

Responsibilities:

* events
* metrics
* aggregations
* dashboards
* conversion analytics
* AI analytics
* operational analytics

⸻

5.14 Reporting

Responsibilities:

* weekly reports
* patient reports
* facial-analysis reports
* operational summaries
* AI performance summaries

⸻

5.15 Automation

Responsibilities:

* rules
* triggers
* conditions
* actions
* schedules
* event reactions

⸻

6. AI ARCHITECTURE

AI must be treated as a platform, not scattered throughout the codebase.

Conceptually:

Application
    │
    ▼
AI Orchestrator
    │
    ├── Task Classification
    ├── Context Builder
    ├── Knowledge Retrieval
    ├── Safety Layer
    ├── Model Router
    ├── Provider Adapter
    ├── Response Validation
    └── AI Observability
              │
              ▼
       Provider Abstraction
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
    Provider Provider Provider

⸻

7. FREE LLM API

FreeLLMAPI is the current reference AI gateway/provider for Clinicos.

The architecture must NOT assume that FreeLLMAPI will exist forever.

Therefore:

Clinicos AI Platform
        │
        ▼
Provider Interface
        │
        ├── FreeLLMAPI
        ├── Future Provider A
        ├── Future Provider B
        └── Future Provider C

The rest of Clinicos should not directly depend on FreeLLMAPI-specific implementation details.

Changing providers should not require rewriting business logic.

⸻

8. AI ORCHESTRATOR

The AI Orchestrator should determine:

* what task is being performed
* what context is required
* what knowledge is required
* whether AI is allowed to answer
* whether human escalation is required
* which model/provider should be used
* how the output should be validated

Example flow:

Patient Message
      │
      ▼
Intent Detection
      │
      ▼
Safety Check
      │
      ▼
Context Construction
      │
      ▼
Knowledge Retrieval
      │
      ▼
Task Selection
      │
      ▼
Model Selection
      │
      ▼
AI Generation
      │
      ▼
Response Validation
      │
      ▼
Business Rules
      │
      ▼
Response / Escalation

⸻

9. AI CONTEXT ARCHITECTURE

AI context must be assembled intentionally.

Possible context sources:

Current Message
Conversation History
Patient Memory
Clinic Knowledge
Operational State
Lead State
Appointment State
Relevant Previous Events
Safety Rules

Not every request should receive all available data.

Context should be:

* relevant
* minimal
* accurate
* tenant-isolated
* cost-aware

⸻

10. KNOWLEDGE RETRIEVAL

The knowledge system should eventually support retrieval.

Conceptually:

User Request
     │
     ▼
Intent / Topic
     │
     ▼
Knowledge Retrieval
     │
     ├── Approved Knowledge
     ├── Relevant Clinic Data
     └── Relevant Policies
     │
     ▼
Context Builder
     │
     ▼
AI

Approved knowledge should be prioritized over AI assumptions.

⸻

11. AI RESPONSE VALIDATION

AI output should not always be sent directly to users.

Depending on risk, responses may pass through:

* schema validation
* business-rule validation
* safety validation
* knowledge consistency checks
* appointment validation
* pricing validation

For critical actions, deterministic systems should be authoritative.

Example:

AI:
"I think tomorrow at 5 PM should be available."
NOT ACCEPTABLE.
Instead:
AI → Appointment System → Verified Availability → Response

⸻

12. DETERMINISTIC VS AI RESPONSIBILITIES

AI should handle tasks where reasoning or language understanding is useful.

Deterministic systems should remain authoritative for:

* prices
* appointment availability
* permissions
* patient identity
* usage limits
* financial calculations
* database state
* role access
* safety rules
* configuration

AI may interpret or recommend, but should not overwrite authoritative state without controlled application logic.

⸻

13. EVENT-DRIVEN ARCHITECTURE

Clinicos should gradually move toward meaningful domain events.

Examples:

patient.created
patient.updated
message.received
message.sent
lead.created
lead.updated
lead.became_hot
lead.converted
lead.lost
lead.recovered
appointment.requested
appointment.booked
appointment.cancelled
appointment.completed
followup.created
followup.required
followup.completed
human_takeover.started
human_takeover.completed
knowledge_candidate.created
knowledge.approved
knowledge.rejected
facial_analysis.started
facial_analysis.completed
facial_analysis.failed
patient.returned

Events may drive:

* notifications
* analytics
* automation
* reporting
* follow-up
* AI processing

⸻

14. EVENT DESIGN RULES

Events should:

* be immutable
* contain sufficient identifiers
* have timestamps
* identify tenant/clinic
* be traceable
* avoid unnecessary sensitive data
* be versionable when necessary

Consumers should be idempotent where appropriate.

⸻

15. AUTOMATION ARCHITECTURE

The automation engine should conceptually support:

EVENT
  +
CONDITIONS
  +
RULES
  ↓
ACTION

Example:

lead.became_hot
+
lead.score > threshold
+
clinic.open == true
↓
notify.secretary
+
create.followup
+
prioritize.conversation

Automation must remain configurable.

⸻

16. DATABASE ARCHITECTURE

PostgreSQL is the preferred primary relational database for the product.

It should store authoritative structured state.

Potential domains include:

* tenants
* clinics
* users
* roles
* patients
* identities
* conversations
* messages
* leads
* appointments
* followups
* knowledge
* facial analyses
* notifications
* events
* analytics metadata
* AI usage

The exact schema will be defined separately in:

CLINICOS_DATA_AND_DATABASE_SPEC.md

⸻

17. REDIS / FAST STATE

Redis may be used for:

* caching
* rate limiting
* temporary state
* locks
* queues where appropriate
* provider health
* short-lived sessions
* deduplication

Redis must not become the only source of truth for critical persistent business data.

⸻

18. OBJECT STORAGE

Large media should not necessarily be stored directly inside PostgreSQL.

Potential object-storage targets:

* patient images
* facial-analysis images
* generated reports
* attachments

Database records should store appropriate references and metadata.

Access must be secured.

⸻

19. MULTI-TENANCY ARCHITECTURE

Every tenant-sensitive operation must be associated with a clinic/tenant context.

Conceptually:

Request
  ↓
Authenticated Identity
  ↓
Tenant Context
  ↓
Authorization
  ↓
Business Logic
  ↓
Data Access

Tenant isolation must be enforced at multiple levels where appropriate.

A missing tenant context should be treated as a serious error.

⸻

20. AUTHORIZATION

Authorization should use:

* role-based access
* permission-based access
* tenant boundaries
* resource ownership where necessary

Examples:

A secretary should not automatically access:

* system-wide configuration
* another clinic’s patients
* restricted medical information
* owner-only analytics

Permissions should be explicit.

⸻

21. CHANNEL ABSTRACTION

Channels should implement a common internal interface.

Conceptually:

Channel Interface
send_message()
receive_message()
send_media()
receive_media()
get_user_identity()
handle_webhook()

Implementations may include:

Telegram
Instagram
Web
FutureChannel

The business logic should not depend on Telegram-specific objects.

⸻

22. CONVERSATION ARCHITECTURE

A conversation should be represented independently from the communication channel.

Conceptually:

Patient
   │
   ▼
Conversation
   │
   ├── Messages
   ├── Attachments
   ├── AI Responses
   ├── Human Responses
   ├── Events
   └── State

The system should support:

* active conversation
* human takeover
* AI mode
* waiting for patient
* waiting for staff
* resolved
* escalated

⸻

23. PATIENT MEMORY ARCHITECTURE

Patient memory should not simply equal conversation history.

Memory should contain selected durable information.

Potential categories:

* preferences
* interests
* language
* previous services
* communication preferences
* relevant notes
* confirmed facts

Memory entries should have:

* source
* timestamp
* confidence/state
* tenant
* optional expiration
* ability to correct/delete

⸻

24. FACIAL ANALYSIS ARCHITECTURE

Facial analysis should be separated into stages.

Image
  ↓
Consent
  ↓
Quality Validation
  ↓
Face Detection
  ↓
Landmarks
  ↓
Measurements
  ↓
AI Interpretation
  ↓
Safety Validation
  ↓
Visualization
  ↓
Report

The system must be able to identify which stage failed.

⸻

25. FACIAL MEASUREMENT VS AI INTERPRETATION

These must remain conceptually separate.

Measurement layer

Produces measurable outputs.

Interpretation layer

Explains what measurements may mean.

This separation allows:

* deterministic testing
* better auditing
* model replacement
* reduced hallucination
* reproducibility

⸻

26. ASYNCHRONOUS PROCESSING

Long-running operations should not block user interactions.

Potential asynchronous jobs:

* facial analysis
* PDF generation
* weekly reports
* analytics aggregation
* follow-up scheduling
* AI-heavy tasks
* image processing
* notification delivery

The system should use background workers/jobs where appropriate.

⸻

27. RETRY STRATEGY

External operations should support controlled retries.

Examples:

* AI provider failure
* Telegram failure
* database transient failure
* object storage failure

Retries must use:

* bounded attempts
* exponential backoff where appropriate
* idempotency
* dead-letter/failure handling when necessary

Never retry blindly forever.

⸻

28. AI PROVIDER FAILURE

Provider failure should not automatically become product failure.

The AI platform should support:

* timeout
* provider failure
* rate limit
* temporary unavailability
* malformed output

Possible response:

Primary Provider
      ↓
Failure
      ↓
Fallback Provider
      ↓
Failure
      ↓
Safe fallback / Human escalation

Fallback behavior must respect task safety and provider capability.

⸻

29. OBSERVABILITY

The architecture should support:

* structured logs
* metrics
* traces
* error tracking
* AI request tracking
* provider performance
* job monitoring
* event monitoring

Important identifiers should be traceable across layers.

Example:

request_id
tenant_id
patient_id
conversation_id
message_id
ai_request_id
event_id

Sensitive data should not be unnecessarily written to logs.

⸻

30. AI OBSERVABILITY

AI-specific telemetry should include where appropriate:

* provider
* model
* task
* latency
* token usage
* estimated cost
* success/failure
* fallback
* validation result
* escalation
* human correction

The system should make it possible to determine:

Which model/provider performs best for which task?

⸻

31. SECURITY ARCHITECTURE

Security must be implemented across:

* authentication
* authorization
* tenant isolation
* data access
* API security
* secrets management
* storage
* logging
* external integrations
* AI context
* media
* generated reports

Secrets must never be committed to source code or documentation.

⸻

32. SECRET MANAGEMENT

API keys and credentials must be provided through secure configuration.

Examples:

* environment variables
* managed secrets
* secret managers

Never put real credentials inside:

* source code
* README
* Markdown documentation
* Gemini Notebook sources
* prompts
* logs

⸻

33. DATA FLOW PRINCIPLE

Sensitive patient data should only flow to systems that require it.

The AI context builder should minimize unnecessary data exposure.

Example:

If a user asks:

“What is the clinic address?”

The AI does not need the patient’s entire medical history.

⸻

34. API ARCHITECTURE

The system should expose clear APIs between major modules.

Potential API categories:

/auth
/patients
/conversations
/messages
/leads
/followups
/appointments
/knowledge
/facial-analysis
/notifications
/analytics
/reports
/clinic
/ai

Exact API technology is a separate implementation decision.

⸻

35. COMMAND / QUERY SEPARATION

Where useful, the application should distinguish:

Commands

Actions that change state.

Examples:

* CreateLead
* BookAppointment
* ApproveKnowledge
* StartFacialAnalysis

Queries

Read-only operations.

Examples:

* GetPatient
* GetLead
* GetAvailableAppointments
* SearchKnowledge
* GetWeeklyAnalytics

This separation should improve clarity and testing.

⸻

36. IDEMPOTENCY

Critical operations should be idempotent where possible.

Examples:

* appointment booking
* message processing
* payment-related future operations
* notification delivery
* event processing
* facial-analysis job creation

A duplicate network request must not accidentally create duplicate business operations.

⸻

37. DATA CONSISTENCY

Critical state transitions should be atomic where necessary.

Examples:

Appointment booking should not result in:

appointment booked

without corresponding authoritative scheduling state.

Lead conversion should not partially update unrelated records.

Transactions should be used where appropriate.

⸻

38. VERSIONING

The architecture should support versioning for:

* APIs
* events
* knowledge
* prompts where necessary
* AI configurations
* report templates
* important domain structures

Changes should be backward-compatible when practical.

⸻

39. TESTABILITY

Each major domain should be testable independently.

Required categories may include:

Unit tests

* domain rules
* scoring
* validation
* safety rules

Integration tests

* database
* Redis
* AI providers
* external APIs

End-to-end tests

* patient conversation
* lead creation
* appointment flow
* facial-analysis flow
* human takeover

Security tests

* tenant isolation
* authorization
* secret exposure
* access control

⸻

40. AI TESTING

AI behavior should not be tested only by checking whether a response “sounds good.”

Tests should evaluate:

* correctness
* grounding
* safety
* hallucination
* consistency
* structured output
* escalation
* multilingual behavior
* cost
* latency

Important prompts/tasks should have regression tests.

⸻

41. MIGRATION STRATEGY

The existing repository must not be blindly rewritten.

The migration process should be:

Current Repository
       ↓
Current State Analysis
       ↓
Gap Analysis
       ↓
Architecture Mapping
       ↓
Prioritized Migration
       ↓
Incremental Refactoring
       ↓
Verification

Large rewrites should only be performed when justified.

⸻

42. LEGACY CODE

Existing code may contain:

* temporary implementations
* duplicated logic
* obsolete providers
* outdated assumptions
* incomplete features
* architectural shortcuts

Legacy code should not automatically define the target architecture.

Each major existing component should eventually be classified as:

* Keep
* Refactor
* Replace
* Remove
* Unknown / Requires Verification

⸻

43. SCALABILITY

The architecture should eventually support growth in:

* clinics
* patients
* conversations
* messages
* AI requests
* images
* reports
* analytics
* background jobs

Scaling should be possible without redesigning core domains.

⸻

44. PERFORMANCE

Performance priorities:

1. User-facing responsiveness
2. Reliable background processing
3. Efficient database queries
4. Efficient AI usage
5. Efficient retrieval
6. Efficient media processing

Long AI/image/report tasks should be asynchronous where appropriate.

⸻

45. COST ARCHITECTURE

Cost must be observable by:

* clinic
* task
* provider
* model
* time period

Potential cost sources:

* AI inference
* vision
* storage
* messaging APIs
* external APIs
* compute

The architecture should make cost optimization possible without changing product behavior.

⸻

46. DEPLOYMENT ARCHITECTURE

The exact hosting platform is not part of the product architecture.

Clinicos should remain portable across suitable infrastructure.

Potential components:

Application Server
Background Worker
PostgreSQL
Redis
Object Storage
AI Providers
External Channel APIs
Monitoring

Railway may be used as an implementation/deployment environment, but the architecture must not become dependent on Railway-specific behavior unless explicitly required.

⸻

47. DEVELOPMENT ENVIRONMENTS

The product should support:

* local development
* testing
* staging
* production

Configuration must be environment-specific.

Production secrets must never be copied into development documentation or test fixtures.

⸻

48. BACKGROUND JOB ARCHITECTURE

A job system should eventually handle:

* AI processing
* facial analysis
* report generation
* notifications
* follow-ups
* analytics
* weekly reports

Jobs should have:

* unique IDs
* status
* retries
* timestamps
* error information
* tenant context
* correlation IDs

⸻

49. FILE AND MEDIA ARCHITECTURE

Media processing should be isolated from normal text processing.

Potential media types:

* patient photos
* facial-analysis photos
* PDFs
* voice messages
* documents

Media should have:

* secure access
* metadata
* lifecycle
* ownership
* tenant association
* retention policy

⸻

50. REPORT GENERATION

Report generation should be modular.

Possible report types:

* facial analysis
* weekly clinic report
* patient summary
* AI performance
* analytics

Reports should be generated from structured data whenever possible rather than relying on uncontrolled AI-generated text.

⸻

51. ANALYTICS ARCHITECTURE

Operational events should feed analytics.

Conceptually:

Domain Events
      ↓
Event Processing
      ↓
Analytics Store / Aggregation
      ↓
Dashboards
Reports
AI Insights

Analytics must not alter authoritative operational state.

⸻

52. AI + BUSINESS LOGIC BOUNDARY

A major architectural rule:

AI should suggest, interpret, classify, summarize, and communicate. Deterministic application logic should enforce critical business rules.

Example:

AI may determine:

“This patient appears highly interested in Botox.”

Business logic determines:

lead score = 82

And the appointment system determines:

17:00 is actually available.

⸻

53. ANTI-GOD-SERVICE RULE

Clinicos must avoid a giant central service containing:

* all AI
* all database access
* all patient logic
* all appointment logic
* all lead logic
* all Telegram logic

A central orchestrator may coordinate workflows, but domain ownership must remain distributed across clear modules.

⸻

54. ANTI-GOD-DATABASE RULE

The database must not become the only place where business behavior is implicitly defined.

Important business rules should be explicit in application/domain logic.

Database constraints should still protect critical invariants.

⸻

55. ARCHITECTURAL GUARDRAILS

The following are considered architectural violations unless explicitly justified:

1. Business logic inside Telegram handlers.
2. Direct AI-provider calls scattered across the application.
3. Cross-domain database access without clear boundaries.
4. Clinic data without tenant context.
5. AI directly modifying critical state without validation.
6. Prices generated by AI instead of retrieved from authoritative data.
7. Appointment availability generated by AI.
8. Medical safety implemented only inside prompts.
9. Secrets inside source code.
10. Facial measurements generated solely by an LLM when deterministic measurement is available.
11. Critical state stored only in Redis.
12. Infinite retries.
13. Unbounded AI context.
14. Automatically storing hallucinated AI output as authoritative knowledge.
15. Telegram-specific objects leaking into domain logic.

⸻

56. ARCHITECTURAL DECISION PROCESS

When introducing a new component, ask:

1. Which domain owns it?
2. Is it deterministic or AI-driven?
3. What is its source of truth?
4. What data does it require?
5. What events does it produce?
6. What events does it consume?
7. What happens if it fails?
8. Does it need asynchronous processing?
9. Does it expose sensitive data?
10. Does it require tenant isolation?
11. How will it be tested?
12. How will it be observed?
13. Can it be replaced later?

⸻

57. TARGET ARCHITECTURE VS CURRENT CODE

This document is a target architecture.

The current codebase may not resemble it.

That is expected.

The engineering process must therefore continuously compare:

TARGET ARCHITECTURE
        ↓
CURRENT ARCHITECTURE
        ↓
ARCHITECTURAL GAP
        ↓
PRIORITY
        ↓
MIGRATION PLAN

Do not distort the target architecture merely to make it match legacy code.

⸻

58. ARCHITECTURAL EVOLUTION

Clinicos does not need to implement the entire target architecture immediately.

Architecture should evolve incrementally.

A sensible progression may be:

Stage 1

Stable modular monolith.

Stage 2

Strong domain boundaries.

Stage 3

Background jobs and event-driven workflows.

Stage 4

Advanced AI orchestration.

Stage 5

Multi-channel communication.

Stage 6

Advanced analytics and automation.

Stage 7

Selective extraction of independently scalable services if justified.

Microservices should NOT be introduced merely because they sound advanced.

A well-designed modular monolith is preferred until independent scaling or ownership genuinely requires service separation.

⸻

59. TARGET ARCHITECTURAL QUALITY

The final architecture should be:

* modular
* understandable
* testable
* observable
* secure
* tenant-safe
* AI-native
* provider-independent
* channel-independent
* scalable
* maintainable
* replaceable
* cost-aware
* medically cautious

⸻

60. FINAL ARCHITECTURAL PRINCIPLE

The most important architectural rule is:

Clinicos must be designed around its business domains and authoritative data, not around the limitations of its current AI provider, communication channel, hosting platform, or legacy code.

The system should be able to change:

* AI provider
* AI model
* communication channel
* hosting platform
* database implementation where practical
* facial-analysis implementation
* reporting engine

without requiring the entire product to be rebuilt.

⸻

END OF DOCUMENT