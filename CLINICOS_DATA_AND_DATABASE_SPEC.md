# Clinicos — Data & Database Specification
**Document:** `CLINICOS_DATA_AND_DATABASE_SPEC.md`  
**Status:** Target / Authoritative Data Model  
**Version:** 1.0  
**Project:** Clinicos  
**Purpose:** Define the target data architecture, database model, data ownership, relationships, invariants, lifecycle rules, privacy requirements, and persistence strategy for Clinicos.
---
# 1. Document Purpose
This document defines the **target data and database architecture** of Clinicos.
It describes what the Clinicos platform SHOULD store, how information SHOULD be related, which system is authoritative for each type of data, and which invariants MUST be preserved.
This document is a **target-state specification**.
It does NOT assume that the current repository already implements this model.
The current repository MUST be inspected separately and compared against this specification.
The AI coding assistant MUST NOT interpret the current database schema as the desired architecture merely because it already exists.
The target data model is determined by:
1. Product Requirements
2. Target Architecture
3. This Data & Database Specification
4. Master Vision
5. Current Repository
6. Historical implementation documents
Current implementation may differ substantially from this model.
---
# 2. Core Data Principles
Clinicos MUST follow these principles.
## 2.1 Data must have a clear owner
Every important piece of information MUST have a defined source of truth.
Examples:
- Patient identity → Patient domain
- Appointment status → Appointment domain
- Lead status → Lead domain
- Clinic service price → Clinic/Service domain
- Approved medical guidance → Knowledge/Safety domain
- AI execution metadata → AI domain
- Facial measurements → Facial Analysis domain
No domain should silently become the authoritative source for another domain.
---
# 3. PostgreSQL as the Authoritative Database
PostgreSQL SHOULD be the primary authoritative persistent database.
It is responsible for durable business state.
Examples:
- clinics
- users
- patients
- conversations
- messages
- leads
- appointments
- services
- knowledge
- facial analyses
- AI execution records
- notifications
- audit logs
- domain events
Redis MAY be used for:
- caching
- temporary state
- rate limiting
- distributed locks
- queues
- short-lived session state
- provider cooldowns
- performance optimization
Redis MUST NOT become the authoritative source for critical business data.
If Redis is lost, Clinicos MUST remain capable of reconstructing authoritative business state from PostgreSQL and durable storage.
---
# 4. Multi-Tenancy
Clinicos MUST be designed as a multi-tenant system.
A tenant represents a clinic or clinic organization.
The system MUST guarantee strict data isolation between tenants.
A tenant MUST NEVER be able to access:
- another tenant's patients
- another tenant's conversations
- another tenant's leads
- another tenant's appointments
- another tenant's knowledge
- another tenant's facial analyses
- another tenant's analytics
- another tenant's AI data
- another tenant's staff information
- another tenant's files
---
# 5. Tenant Hierarchy
The conceptual hierarchy is:
```text
Tenant / Clinic
    │
    ├── Branches
    │
    ├── Users / Staff
    │
    ├── Doctors
    │
    ├── Patients
    │
    ├── Services
    │
    ├── Schedules
    │
    ├── Conversations
    │
    ├── Leads
    │
    ├── Follow-ups
    │
    ├── Appointments
    │
    ├── Knowledge
    │
    ├── Facial Analyses
    │
    ├── Notifications
    │
    ├── AI Execution Records
    │
    ├── Analytics
    │
    └── Audit Logs

Every tenant-owned entity MUST be associated with a tenant.

⸻

6. Tenant Isolation Rule

Every tenant-owned table SHOULD contain a tenant_id directly unless there is a strong architectural reason not to.

The system MUST NOT rely only on indirect relationships such as:

message → conversation → patient → tenant

for authorization-critical tenant filtering.

Direct tenant scoping improves:

* authorization
* query safety
* indexing
* auditing
* performance
* accidental cross-tenant data prevention

⸻

7. Core Entities

The target data model consists of the following major domains.

Tenant
Branch
User
Role
Permission
Doctor
Patient
ChannelIdentity
Conversation
Message
Attachment
Lead
LeadEvent
LeadScore
FollowUp
FollowUpExecution
Service
ServiceVariant
Price
DoctorService
Schedule
Availability
Appointment
KnowledgeItem
KnowledgeVersion
KnowledgeSource
KnowledgeCandidate
SafetyRule
Escalation
FacialAnalysis
FacialImage
FacialLandmark
FacialMetric
FacialObservation
TreatmentRecommendation
FacialBeforeAfter
FacialAnalysisUsage
AIRequest
AIResponse
AIProviderExecution
AIUsage
Notification
DomainEvent
Job
AnalyticsSnapshot
Report
AuditLog

The exact physical schema MAY differ if the architectural behavior remains equivalent.

⸻

8. Tenant / Clinic

A Tenant represents an independent clinic organization.

Conceptual fields:

id
name
slug
status
default_language
timezone
country
currency
branding_configuration
operational_configuration
created_at
updated_at

The tenant configuration MAY include:

* supported languages
* AI tone
* lead thresholds
* follow-up policies
* notification rules
* working hours
* facial-analysis policy
* escalation policy
* enabled channels
* enabled modules

Configuration SHOULD be structured and versionable when necessary.

⸻

9. Branch

A tenant MAY have multiple branches.

Conceptual fields:

id
tenant_id
name
address
phone
location
timezone
status
configuration
created_at
updated_at

Branch-specific information MUST NOT overwrite tenant-wide information unless explicitly intended.

Appointments, doctors, schedules, and services MAY be branch-specific.

⸻

10. Users and Staff

A User represents an authenticated person interacting with Clinicos as staff or an administrative user.

Possible roles include:

OWNER
DOCTOR
SECRETARY
MANAGER
ADMIN
PATIENT

The exact role model MAY use RBAC tables instead of a single role field.

Authorization MUST NOT rely solely on frontend role information.

Permissions MUST be validated server-side.

⸻

11. Roles and Permissions

The system SHOULD support:

roles
permissions
role_permissions
user_roles

Permissions SHOULD be granular.

Examples:

patient.read
patient.write
lead.read
lead.write
appointment.read
appointment.write
knowledge.read
knowledge.write
knowledge.approve
facial_analysis.read
facial_analysis.execute
analytics.read
billing.read
billing.write
staff.read
staff.write
settings.read
settings.write

Sensitive operations SHOULD require elevated permissions.

⸻

12. Doctor

Doctors MAY be represented as a specialized staff entity or as a user-linked professional profile.

Conceptual data:

id
tenant_id
user_id
branch_id
display_name
specialties
license_information_reference
bio
status
configuration
created_at
updated_at

Sensitive professional credentials MUST NOT be stored unnecessarily.

⸻

13. Patient

Patient is a central entity.

Conceptual fields:

id
tenant_id
external_reference
display_name
phone
email
preferred_language
timezone
date_of_birth
gender
status
consent_status
marketing_consent
medical_data_consent
created_at
updated_at
last_interaction_at

Not all fields are mandatory.

The system MUST collect only information necessary for legitimate product functionality.

Sensitive medical information MUST be treated separately from ordinary CRM information when appropriate.

⸻

14. Patient Identity Resolution

A patient MAY interact through multiple channels.

Therefore:

Patient
    │
    ├── Telegram Identity
    ├── Instagram Identity
    ├── Website Identity
    ├── WhatsApp Identity
    └── Other Channel Identity

Channel identities SHOULD be stored separately.

Conceptual entity:

ChannelIdentity
id
tenant_id
patient_id
channel
external_user_id
username
metadata
verified
created_at
updated_at

The same external identifier MUST NOT be assumed globally unique across all channels.

Uniqueness MUST normally be scoped by:

tenant + channel + external_user_id

⸻

15. Identity Resolution Safety

Clinicos MUST NOT automatically merge two patients merely because:

* names match
* usernames look similar
* phone numbers partially match
* profile information looks similar

Identity merging SHOULD require strong evidence.

When confidence is insufficient, the system SHOULD preserve separate identities.

Potential identity matches MAY be stored as candidates for human confirmation.

⸻

16. Conversations

A Conversation represents a communication thread between a patient and Clinicos.

Conceptual fields:

id
tenant_id
patient_id
channel
channel_conversation_id
status
started_at
last_message_at
assigned_user_id
metadata
created_at
updated_at

Conversation state is operational state.

It MUST NOT be confused with long-term patient memory.

⸻

17. Messages

A Message represents an individual communication event.

Conceptual fields:

id
tenant_id
conversation_id
patient_id
sender_type
sender_id
message_type
content
language
external_message_id
reply_to_message_id
timestamp
metadata
created_at

Possible message types:

text
image
video
audio
voice
document
location
system
event

External message IDs SHOULD be used for idempotency.

⸻

18. Attachments

Attachments SHOULD be stored as metadata references rather than binary blobs inside ordinary business tables.

Conceptual:

Attachment
id
tenant_id
owner_type
owner_id
storage_provider
storage_key
mime_type
size
checksum
encryption_status
created_at
expires_at

The database SHOULD store references.

Actual media SHOULD be stored in appropriate object/file storage.

⸻

19. Lead

A Lead represents a commercial/conversion opportunity.

Conceptual fields:

id
tenant_id
patient_id
source
status
temperature
score
score_explanation
interested_service_id
assigned_user_id
first_seen_at
last_activity_at
converted_at
lost_at
created_at
updated_at

Possible statuses:

NEW
ACTIVE
QUALIFIED
CONVERTED
LOST
INACTIVE
RETURNING

Possible temperature:

COLD
WARM
HOT

The exact taxonomy MAY evolve.

⸻

20. Lead Score

Lead score MUST be explainable.

The system SHOULD be able to answer:

Why is this patient currently considered a hot lead?

Potential signals:

* explicit interest
* requested price
* asked about availability
* requested appointment
* repeated engagement
* service preference
* response speed
* previous appointment
* previous treatment
* follow-up response
* recent activity

The system MUST NOT store an opaque score without sufficient explanation.

⸻

21. Lead Events

Important lead changes SHOULD be event-based.

Examples:

lead.created
lead.qualified
lead.became_hot
lead.became_cold
lead.converted
lead.lost
lead.recovered
lead.assigned
lead.score_changed

Each event SHOULD preserve:

event_type
previous_state
new_state
reason
source
timestamp
actor

⸻

22. Follow-Up

Follow-ups represent actions that Clinicos intends to perform later.

Conceptual:

id
tenant_id
patient_id
lead_id
conversation_id
type
status
scheduled_at
reason
priority
assigned_agent
attempt_count
completed_at
cancelled_at
created_at
updated_at

Possible statuses:

PENDING
SCHEDULED
IN_PROGRESS
COMPLETED
SKIPPED
CANCELLED
FAILED

Follow-up timing SHOULD be configurable.

The system MUST respect:

* opt-out
* working hours
* safety restrictions
* clinic policies
* channel limitations

⸻

23. Services

A Service represents something the clinic offers.

Examples:

* facial rejuvenation
* hair treatment
* mesotherapy
* PRP
* filler
* laser
* consultation

Conceptual:

id
tenant_id
branch_id
name
description
category
duration
status
metadata
created_at
updated_at

⸻

24. Pricing

Price MUST have an authoritative source.

AI MUST NEVER invent a price.

Possible structure:

Service
    │
    └── PriceVersion

Conceptual:

id
tenant_id
service_id
amount
currency
valid_from
valid_until
status
source
created_at

Historical prices SHOULD remain auditable.

If no valid current price exists, the AI SHOULD state that the price requires confirmation.

⸻

25. Doctors and Services

A doctor MAY offer multiple services.

A service MAY be offered by multiple doctors.

Therefore a many-to-many relationship MAY be required:

doctor_services

Potential fields:

doctor_id
service_id
branch_id
status
configuration

⸻

26. Schedule and Availability

Appointment availability MUST be based on authoritative scheduling data.

Potential entities:

Schedule
AvailabilityRule
AvailabilityException
Appointment

Examples of exceptions:

* vacation
* holiday
* blocked time
* emergency closure
* special working day

Clinicos MUST NOT tell a patient that a time slot is available unless availability has been verified against the authoritative scheduling state.

⸻

27. Appointment

Conceptual:

id
tenant_id
branch_id
patient_id
doctor_id
service_id
status
scheduled_start
scheduled_end
source
notes
confirmation_status
created_at
updated_at
cancelled_at
completed_at

Possible states:

REQUESTED
PENDING_CONFIRMATION
CONFIRMED
RESCHEDULED
CANCELLED
NO_SHOW
COMPLETED

The exact state machine MUST prevent invalid transitions.

⸻

28. Knowledge Base

The Knowledge Base is one of the most important data domains.

It contains clinic-approved information used by AI.

Examples:

* services
* prices
* working hours
* doctors
* policies
* preparation instructions
* aftercare
* FAQs
* promotions
* approved medical information
* clinic rules
* operational procedures

⸻

29. Knowledge Item

Conceptual:

id
tenant_id
category
title
content
status
authority_level
source_type
created_by
approved_by
created_at
updated_at

Possible statuses:

DRAFT
PENDING_REVIEW
APPROVED
REJECTED
ARCHIVED

AI MUST NOT automatically convert an unverified conversation statement into authoritative clinic knowledge.

⸻

30. Knowledge Versioning

Important knowledge SHOULD be versioned.

Conceptually:

KnowledgeItem
    │
    ├── Version 1
    ├── Version 2
    ├── Version 3
    └── Current Version

Versioning is particularly important for:

* prices
* medical guidance
* clinic policies
* promotions
* working hours
* service descriptions

Historical versions SHOULD remain auditable.

⸻

31. Knowledge Candidates

Clinicos MAY identify recurring unanswered questions or potentially useful information.

These SHOULD enter a candidate workflow:

Conversation
      ↓
Candidate Extraction
      ↓
Candidate
      ↓
Classification
      ↓
Human Review
      ↓
Approval
      ↓
Knowledge Item

AI MUST NOT create an infinite self-training loop where its own hallucinated output becomes future authoritative knowledge.

⸻

32. Safety Rules

Safety-sensitive information SHOULD have explicit structured representation.

Examples:

contraindications
red_flags
escalation_rules
medical_disclaimers
restricted_topics

Medical safety rules MUST have higher authority than generic AI generation.

⸻

33. Escalation

Escalation records MAY be used when AI determines that human intervention is required.

Conceptual:

id
tenant_id
patient_id
conversation_id
reason
severity
status
assigned_to
created_at
resolved_at

Possible severity:

LOW
MEDIUM
HIGH
CRITICAL

⸻

34. Facial Analysis

Facial analysis is a dedicated domain.

It MUST NOT be reduced to a single JSON field inside the patient record.

Conceptual:

Patient
   │
   └── FacialAnalysis
          │
          ├── Images
          ├── Landmarks
          ├── Metrics
          ├── Observations
          ├── Recommendations
          ├── Before/After
          └── Usage

⸻

35. Facial Analysis Record

Conceptual:

FacialAnalysis
id
tenant_id
patient_id
status
consent_status
image_quality_status
analysis_version
vision_model_reference
created_at
completed_at
failed_at

Possible states:

CREATED
WAITING_FOR_IMAGE
QUALITY_RETRY
PROCESSING
COMPLETED
FAILED
CANCELLED

⸻

36. Facial Images

Images MUST be stored separately.

Conceptual:

FacialImage
id
tenant_id
facial_analysis_id
attachment_id
image_type
quality_score
face_detected
created_at

Potential image types:

ORIGINAL
CROPPED
PROCESSED
ANNOTATED
BEFORE
AFTER
SIMULATION

⸻

37. Facial Landmarks

Facial landmarks SHOULD be stored separately from general analysis metadata.

Conceptual:

FacialLandmark
id
tenant_id
facial_analysis_id
landmark_set
index
x
y
z
confidence

The implementation MAY use MediaPipe or another vision technology.

The database SHOULD NOT be tightly coupled to one vendor-specific representation if avoidable.

⸻

38. Facial Metrics

Metrics represent measurable properties.

Examples:

symmetry
distances
angles
proportions
ratios
regional measurements

Conceptual:

FacialMetric
id
tenant_id
facial_analysis_id
metric_name
metric_value
unit
reference_range
confidence
calculation_version

Measurements and interpretations MUST remain separate.

⸻

39. Facial Observations

An observation is an interpretation of available measurements/image evidence.

Conceptual:

FacialObservation
id
tenant_id
facial_analysis_id
region
observation
confidence
source
created_at

Observations MUST NOT be presented as medical diagnoses unless clinically validated and explicitly supported.

⸻

40. Treatment Recommendations

Treatment recommendations MUST be represented separately.

Conceptual:

TreatmentRecommendation
id
tenant_id
facial_analysis_id
service_id
priority
reason
confidence
disclaimer
created_at

Recommendations MUST be:

* non-diagnostic
* appropriately qualified
* traceable to analysis evidence
* configurable
* subject to clinic policy

The AI MUST NOT claim certainty when the underlying analysis does not support certainty.

⸻

41. Before/After

Before/after comparisons SHOULD be separate records.

Conceptual:

FacialBeforeAfter
id
tenant_id
patient_id
before_analysis_id
after_analysis_id
comparison_data
created_at

The system MUST distinguish:

* real before/after photographs
* generated visualizations
* simulations
* predicted outcomes

Generated or simulated results MUST NEVER be presented as actual treatment outcomes.

⸻

42. Aging Simulation

If aging simulation is implemented, it MUST be explicitly labeled as simulation.

It MUST NOT be stored or presented as a factual prediction.

Example:

simulation_type = AGING_SIMULATION

with appropriate disclaimer metadata.

⸻

43. Facial Analysis Usage

Usage restrictions MUST be represented as policy/state, not hidden in arbitrary code.

For example, the product MAY define:

standard patient → one free lifetime analysis
authorized staff/doctor/admin → configurable access

This MUST remain configurable.

The database SHOULD support:

FacialAnalysisUsage

with:

tenant_id
patient_id
analysis_count
last_analysis_at
policy_version

The exact enforcement logic belongs to the application/service layer.

⸻

44. AI Execution Data

Clinicos needs observability over AI operations.

AI execution data SHOULD be persisted separately from patient-facing messages.

Core entities:

AIRequest
AIResponse
AIProviderExecution
AIUsage

⸻

45. AI Request

Conceptual:

id
tenant_id
conversation_id
patient_id
agent_type
task_type
request_status
model_reference
created_at
completed_at

Examples of task types:

PATIENT_REPLY
LEAD_CLASSIFICATION
FOLLOWUP_DECISION
KNOWLEDGE_RETRIEVAL
KNOWLEDGE_EXTRACTION
FACIAL_INTERPRETATION
REPORT_GENERATION
TRANSLATION
SUMMARY

⸻

46. AI Provider Execution

The AI layer MUST remain provider-agnostic.

FreeLLMAPI MAY be the current reference gateway/provider.

The data model MUST NOT hard-code the entire architecture around FreeLLMAPI.

Conceptual:

provider
model
request_id
latency_ms
input_tokens
output_tokens
total_tokens
status
error_type
retry_count
created_at

The system SHOULD be capable of recording future providers/models without changing core business entities.

⸻

47. AI Usage and Cost

The system SHOULD track:

* token usage
* latency
* provider
* model
* request type
* success/failure
* estimated cost where available
* retries
* fallback usage

This enables:

* cost optimization
* provider comparison
* reliability monitoring
* model evaluation
* performance analysis

Secrets and API keys MUST NEVER be stored in these records.

⸻

48. AI Memory

Clinicos SHOULD separate different forms of memory.

Conversation Context
Patient Memory
Clinic Knowledge
Operational State
Analytics

They MUST NOT be mixed into one uncontrolled memory blob.

AI-generated memories SHOULD preserve provenance.

For example:

source
source_message_id
confidence
created_by
created_at

A model’s own unsupported statement MUST NOT automatically become a patient fact.

⸻

49. Notifications

Notifications SHOULD be stored separately.

Conceptual:

Notification
id
tenant_id
recipient_user_id
type
priority
title
body
related_entity_type
related_entity_id
status
created_at
read_at

Examples:

HOT_LEAD
URGENT_ESCALATION
APPOINTMENT_REQUEST
MISSED_FOLLOWUP
LOST_LEAD
PATIENT_RETURNED
FACIAL_ANALYSIS_COMPLETE
HUMAN_TAKEOVER
SYSTEM_FAILURE

⸻

50. Domain Events

Clinicos SHOULD evolve toward an event-driven architecture.

Important events MAY include:

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
followup.created
followup.completed
appointment.requested
appointment.confirmed
appointment.cancelled
appointment.completed
knowledge_candidate.created
knowledge.approved
knowledge.updated
facial_analysis.started
facial_analysis.completed
facial_analysis.failed
human_takeover.started
human_takeover.completed

Events SHOULD contain enough metadata to support auditing and downstream processing.

⸻

51. Event Idempotency

Every externally triggered event SHOULD support idempotency.

For example:

external_event_id

or:

idempotency_key

must prevent duplicate processing.

A duplicated webhook or Telegram update MUST NOT create duplicate:

* messages
* appointments
* leads
* payments
* follow-ups
* facial analyses

⸻

52. Jobs

Long-running or asynchronous operations SHOULD use durable jobs.

Examples:

* follow-up execution
* report generation
* facial processing
* AI requests
* notification delivery
* analytics aggregation
* knowledge processing

A job SHOULD track:

id
tenant_id
type
status
attempt_count
scheduled_at
started_at
completed_at
last_error
created_at

⸻

53. State Machines

Important entities MUST have explicit state transitions.

For example:

Lead:
NEW
 ↓
ACTIVE
 ↓
QUALIFIED
 ↓
CONVERTED

or:

NEW → LOST
NEW → INACTIVE
ACTIVE → LOST
LOST → RETURNING
RETURNING → ACTIVE

Invalid transitions MUST be rejected.

State transitions SHOULD be auditable.

⸻

54. Appointment State Machine

Example:

REQUESTED
    ↓
PENDING_CONFIRMATION
    ↓
CONFIRMED
    ↓
COMPLETED

Alternative transitions:

REQUESTED → CANCELLED
PENDING_CONFIRMATION → CANCELLED
CONFIRMED → RESCHEDULED
CONFIRMED → CANCELLED
CONFIRMED → NO_SHOW
RESCHEDULED → CONFIRMED

The actual state machine MAY be expanded but MUST remain explicit.

⸻

55. Soft Delete

Critical business data SHOULD generally not be physically deleted immediately.

Where appropriate:

deleted_at
deleted_by
deletion_reason

MAY be used.

However, soft deletion MUST NOT conflict with privacy deletion requirements.

If a user requests legally required deletion, the system MUST support actual deletion or irreversible anonymization where required.

⸻

56. Timestamps

All important entities SHOULD include:

created_at
updated_at

Stateful entities SHOULD additionally include relevant lifecycle timestamps.

Examples:

completed_at
cancelled_at
deleted_at
last_activity_at

⸻

57. Timezones

Time MUST be stored consistently.

Recommended approach:

* persist timestamps in UTC
* convert to tenant/branch/user timezone at presentation time

Clinic timezone MUST be explicit.

Appointment scheduling MUST use the relevant clinic/branch timezone.

Never assume server timezone equals clinic timezone.

⸻

58. IDs

Entities SHOULD use stable non-sequential identifiers where appropriate.

UUID/UUIDv7 or an equivalent modern identifier strategy SHOULD be considered.

IDs MUST remain immutable.

External IDs MUST NOT replace internal primary keys.

⸻

59. Uniqueness Constraints

Important uniqueness constraints MUST be enforced at the database level where possible.

Examples:

tenant.slug
tenant + channel + external_user_id
tenant + external_message_id
tenant + idempotency_key

Application-level checks alone are insufficient for concurrency-sensitive uniqueness.

⸻

60. Indexing

Indexes SHOULD be designed around actual query patterns.

Likely indexes include:

tenant_id
patient_id
conversation_id
lead status
lead temperature
appointment scheduled_start
appointment status
followup scheduled_at
message timestamp
knowledge status
facial_analysis patient_id
AI request created_at
notification recipient + status
domain_event type + created_at

Indexes MUST be evaluated against real workloads.

Over-indexing SHOULD be avoided.

⸻

61. Composite Indexes

Multi-tenant queries SHOULD generally use composite indexes such as:

(tenant_id, patient_id)
(tenant_id, status)
(tenant_id, created_at)
(tenant_id, scheduled_at)

Exact indexes MUST be derived from actual access patterns.

⸻

62. JSON / JSONB

JSONB MAY be used for:

* flexible metadata
* provider-specific response metadata
* experimental configuration
* external payloads
* non-critical extensible fields

JSONB MUST NOT be used as an excuse to avoid proper relational modeling.

Important queryable business fields SHOULD have proper columns.

For example:

Bad:

patient.metadata = {
  "lead_status": "hot"
}

Preferred:

patient
lead
lead.status

⸻

63. Normalization

Core transactional data SHOULD generally be normalized.

Denormalization MAY be introduced for:

* performance
* analytics
* search
* materialized views
* read models

Any denormalized representation MUST have a clearly defined source of truth.

⸻

64. Analytics Data

Analytics SHOULD be separated conceptually from transactional state.

Possible architecture:

Transactional PostgreSQL
        ↓
Events
        ↓
Aggregation
        ↓
Analytics Tables / Views

Analytics MUST NOT become the authoritative source for transactional decisions.

⸻

65. Reporting

Reports MAY be generated from:

* transactional data
* domain events
* analytics snapshots

Weekly reports SHOULD preserve the reporting period.

Example:

period_start
period_end
tenant_id
generated_at
data_version

Reports SHOULD be reproducible where possible.

⸻

66. Audit Logs

Sensitive actions MUST be auditable.

Conceptual:

AuditLog
id
tenant_id
actor_type
actor_id
action
entity_type
entity_id
before_data
after_data
ip_reference
user_agent_reference
created_at

Potential audited operations:

* permission changes
* knowledge approval
* price changes
* appointment modifications
* patient deletion
* staff changes
* AI policy changes
* facial-analysis access
* sensitive-data access

Sensitive audit information MUST itself be protected.

⸻

67. Data Provenance

Important AI-derived information SHOULD preserve provenance.

For example:

source_type
source_id
source_message_id
source_document_id
source_model
source_version
confidence
created_at

This is especially important for:

* patient memory
* lead scoring
* knowledge candidates
* facial observations
* treatment recommendations
* AI summaries

⸻

68. Source of Truth Matrix

The following conceptual ownership MUST be preserved:

Data	Source of Truth
Clinic identity	Tenant
Branch	Branch
Staff identity	User
Permissions	RBAC
Patient identity	Patient
Channel identity	ChannelIdentity
Conversation	Conversation
Message	Message
Lead state	Lead
Lead history	LeadEvent
Follow-up	FollowUp
Service	Service
Price	PriceVersion
Doctor availability	Schedule / Availability
Appointment	Appointment
Clinic-approved knowledge	Knowledge
Safety rules	Safety
Facial measurements	FacialMetric
Facial landmarks	FacialLandmark
AI execution	AIRequest / AIProviderExecution
Notification	Notification
System events	DomainEvent
Audit history	AuditLog
Analytics	Analytics layer

⸻

69. Data Integrity Invariants

The following invariants MUST be preserved.

69.1 Tenant isolation

No cross-tenant relation may expose data.

69.2 Appointment integrity

An appointment MUST reference valid tenant-owned:

* patient
* doctor
* service
* branch

where applicable.

69.3 Lead integrity

A lead MUST belong to a valid patient and tenant.

69.4 Message integrity

A message MUST belong to a valid conversation.

69.5 Conversation integrity

A conversation MUST belong to a tenant.

69.6 Facial analysis integrity

A facial analysis MUST belong to the same tenant as its patient.

69.7 Knowledge integrity

Approved knowledge MUST have a valid approval history where required.

69.8 AI provenance

AI-generated structured information SHOULD retain enough provenance to understand where it came from.

⸻

70. Cross-Tenant Relationship Rule

The database MUST prevent relationships such as:

tenant A patient
      ↓
tenant B appointment

Application validation alone is insufficient when practical database constraints can prevent such states.

Queries MUST always be tenant-aware.

⸻

71. Privacy

Clinicos may process sensitive personal and potentially medical information.

Therefore:

* collect only necessary data
* restrict access
* encrypt sensitive information where appropriate
* avoid unnecessary duplication
* implement retention policies
* implement deletion/anonymization
* audit sensitive access
* do not expose patient data to unauthorized staff
* do not use patient data for unrelated purposes without appropriate authorization

⸻

72. Media Privacy

Facial images are particularly sensitive.

The system SHOULD support:

* secure storage
* access control
* encryption
* expiration policies
* deletion
* consent tracking
* audit logging

Facial images MUST NOT be publicly accessible through predictable URLs.

⸻

73. Data Retention

Different data categories MAY require different retention periods.

Examples:

temporary AI context → short retention
raw uploaded images → configurable retention
audit logs → longer retention
appointments → business-defined retention
analytics → longer-term aggregated retention

Retention policies MUST be configurable where business/legal requirements vary.

⸻

74. Deletion and Anonymization

The system SHOULD support:

patient deletion
patient anonymization
conversation deletion
media deletion
AI-data deletion

Deletion MUST consider relational dependencies.

The system MUST NOT accidentally leave sensitive media accessible after deleting its database record.

⸻

75. Backups

Production PostgreSQL MUST have:

* automated backups
* tested restoration
* retention policy
* monitoring
* secure backup storage

A backup strategy is incomplete if restoration has never been tested.

⸻

76. Migration Strategy

Database migrations MUST be:

* version-controlled
* deterministic
* reversible where practical
* tested
* compatible with deployment strategy

Destructive migrations MUST be handled carefully.

Large production migrations SHOULD use phased migration strategies when necessary.

⸻

77. Zero-Downtime Considerations

For production changes:

Prefer:

add new field
↓
deploy compatible application
↓
backfill data
↓
switch reads/writes
↓
remove legacy field later

instead of:

drop old field immediately
↓
deploy code

⸻

78. Concurrency

Database operations MUST account for concurrent requests.

Critical operations such as:

* appointment booking
* lead transitions
* usage limits
* provider quota
* notification delivery
* job claiming

MUST be protected against race conditions.

⸻

79. Facial Analysis Usage Concurrency

If a patient is allowed one analysis, two simultaneous requests MUST NOT both pass the limit because they raced each other.

Usage enforcement MUST be atomic.

The system SHOULD use:

* database constraints
* transactions
* locks
* idempotency

as appropriate.

⸻

80. Appointment Concurrency

Two patients MUST NOT be able to book the same exclusive doctor/time slot due to race conditions.

The authoritative availability system MUST enforce this at the transactional level.

⸻

81. Idempotency

External integrations SHOULD be idempotent.

Examples:

Telegram update
Webhook
Payment callback
Appointment confirmation
AI job
Notification job

Repeated delivery MUST NOT produce unintended duplicate business records.

⸻

82. Error Persistence

Important failures SHOULD be persisted in structured form.

Examples:

AI provider failure
facial processing failure
notification failure
appointment integration failure
knowledge processing failure

Errors SHOULD include:

error_code
error_type
safe_message
provider_reference
retryable
created_at

Secrets MUST NOT appear in error logs.

⸻

83. Secrets

The database MUST NEVER be used as a casual storage location for:

* API keys
* passwords
* access tokens
* private keys
* provider secrets

Secrets MUST be managed through an appropriate secret-management mechanism.

This specification intentionally contains no real credentials.

⸻

84. AI Provider Abstraction

The database model MUST remain compatible with:

FreeLLMAPI
future providers
future models
future routing strategies

Provider-specific fields SHOULD be stored in provider execution metadata rather than contaminating core patient/lead/appointment entities.

⸻

85. Model Versioning

AI outputs that materially affect the system SHOULD record:

provider
model
model_version
prompt_version
agent_version
analysis_version

This allows future debugging and evaluation.

⸻

86. Prompt and Policy Versioning

Important AI behavior SHOULD be traceable to:

prompt version
policy version
knowledge version
agent version

This is essential for reproducing unexpected behavior.

⸻

87. AI Output Is Not Automatically Truth

The database MUST distinguish:

verified fact
AI inference
AI hypothesis
unverified candidate
human-approved knowledge

AI-generated content MUST NOT automatically become authoritative business data.

⸻

88. Patient Memory Safety

A patient’s long-term memory SHOULD be built from verified or sufficiently reliable information.

Examples of acceptable memory candidates:

preferred language
known service interest
communication preference
confirmed appointment preference
explicitly stated non-sensitive preference

Uncertain information SHOULD remain uncertain.

⸻

89. Lead Intelligence Data

Lead intelligence SHOULD preserve both:

current score/state

and:

historical evidence

This allows the system to explain:

Why did this lead become hot?

rather than simply returning:

score = 87

⸻

90. Knowledge Intelligence Data

Knowledge intelligence SHOULD preserve:

question
frequency
source conversations
candidate answer
review status
approved answer

This enables FAQ intelligence without allowing AI hallucinations to become permanent knowledge.

⸻

91. Medical Safety Data

Medical safety data SHOULD be isolated from generic marketing content.

For example:

marketing message

must not override:

medical safety rule

Safety rules SHOULD have higher precedence in decision-making.

⸻

92. Conversion Intelligence

Conversion analytics SHOULD be based on measurable events.

Examples:

message
lead qualification
service interest
price inquiry
appointment request
appointment confirmation
appointment completion
conversion
lost lead
recovery

AI MUST NOT claim conversion improvement without measurable evidence.

⸻

93. A/B Testing Data

Future A/B testing SHOULD store:

experiment
variant
patient/lead assignment
exposure
outcome
conversion

Assignments MUST be deterministic enough to avoid uncontrolled switching between variants.

⸻

94. Notification Data

Notification records SHOULD be independent from the event that triggered them.

For example:

lead.became_hot
        ↓
notification.created
        ↓
notification.delivered

This allows delivery failures to be retried without replaying the original business event.

⸻

95. Event vs State

Clinicos MUST distinguish:

State

What is true now.

Example:

lead.temperature = HOT

Event

What happened.

Example:

lead.became_hot

Both may be required.

Current state supports fast queries.

Events support history, auditing, analytics, and automation.

⸻

96. Current State vs Historical State

Critical entities SHOULD preserve history when business decisions depend on it.

Examples:

* lead score changes
* appointment status changes
* price changes
* knowledge changes
* AI model changes
* facial-analysis versions

The system SHOULD NOT overwrite history when historical context is required.

⸻

97. Data Classification

Data SHOULD be classified conceptually as:

PUBLIC
INTERNAL
CONFIDENTIAL
SENSITIVE
HIGHLY_SENSITIVE

Examples:

Clinic public address → PUBLIC
Internal workflow → INTERNAL
Lead information → CONFIDENTIAL
Patient personal data → SENSITIVE
Facial images / medical information → HIGHLY_SENSITIVE

Access controls SHOULD reflect classification.

⸻

98. Database Transactions

Transactions MUST be used whenever multiple writes represent one logical business operation.

Examples:

Create appointment
+ update slot
+ emit event

or:

Complete facial analysis
+ store metrics
+ store observations
+ update usage
+ emit completion event

These operations SHOULD not leave partially committed business state.

⸻

99. Outbox Pattern

For important domain events, an outbox pattern SHOULD be considered.

Example:

Database Transaction
       │
       ├── Business State
       │
       └── Outbox Event
                ↓
             Worker
                ↓
        External Event Bus

This prevents the failure mode where database state commits but event publishing fails.

⸻

100. Repository Reality

The current repository MUST NOT be assumed to match this specification.

Before changing the database, the AI coding assistant MUST:

1. inspect current schema
2. inspect models
3. inspect migrations
4. inspect database access layer
5. inspect queries
6. inspect foreign keys
7. inspect indexes
8. inspect current data assumptions
9. identify legacy structures
10. compare current state with this target specification

Only then should migration planning begin.

⸻

101. Gap Analysis

The AI assistant SHOULD classify differences as:

MATCH
PARTIAL
MISSING
CONFLICT
LEGACY
UNKNOWN

Example:

Target: multi-tenant patient table
Current: patient table without tenant_id
Classification:
CONFLICT / HIGH RISK

The assistant MUST NOT silently redesign the system while claiming that it is only implementing a small feature.

⸻

102. Migration Planning

When the current schema differs from the target:

The assistant MUST explain:

Current state
Target state
Gap
Impact
Migration strategy
Risk
Rollback strategy
Verification

Large schema changes SHOULD be divided into controlled migrations.

⸻

103. Backward Compatibility

When possible, schema changes SHOULD maintain temporary compatibility with existing application code.

The assistant SHOULD avoid:

schema breaking change
+
large unrelated refactor
+
new feature

in a single uncontrolled change.

⸻

104. Testing Database Changes

Database changes MUST be tested at multiple levels.

At minimum:

migration test
model/constraint test
repository test
integration test
tenant-isolation test
transaction/concurrency test where relevant

Critical flows SHOULD be tested against a real PostgreSQL environment.

SQLite-only testing MUST NOT be presented as proof of PostgreSQL correctness when PostgreSQL-specific behavior matters.

⸻

105. PostgreSQL Verification

Because PostgreSQL is the target authoritative database, important PostgreSQL behavior MUST eventually be tested against actual PostgreSQL.

Especially:

* foreign keys
* unique constraints
* transactions
* indexes
* JSONB behavior
* locking
* concurrency
* migrations
* isolation
* row-level security if used

⸻

106. Row-Level Security

PostgreSQL Row-Level Security MAY be considered for additional tenant isolation.

If implemented, RLS policies MUST be thoroughly tested.

RLS MUST NOT be treated as a replacement for application authorization.

Defense in depth is preferred.

⸻

107. Search and Retrieval

Knowledge retrieval SHOULD be designed independently from transactional storage.

Possible future technologies:

* PostgreSQL full-text search
* pgvector
* external vector database

The choice MUST depend on actual requirements.

Vector storage MUST NOT replace authoritative structured data.

⸻

108. Vector Data

If embeddings are introduced:

source_id
tenant_id
embedding
content_hash
embedding_model
created_at

MUST be associated with the original source.

A vector result MUST always be traceable back to authoritative source content.

⸻

109. No Orphaned AI Data

AI records SHOULD remain traceable.

For example:

AIRequest
    ↓
AIProviderExecution
    ↓
AIResponse
    ↓
Business action / Message / Decision

If an AI response causes a lead score change, the relationship SHOULD be traceable where appropriate.

⸻

110. No Orphaned Media

Deleting a facial analysis MUST NOT accidentally leave its sensitive image publicly accessible.

Media lifecycle MUST be coordinated with database lifecycle.

⸻

111. Data Quality

The system SHOULD continuously validate:

* required fields
* valid foreign keys
* valid state transitions
* tenant ownership
* timestamps
* supported languages
* supported statuses
* duplicate external events
* invalid prices
* invalid appointment ranges

⸻

112. Language Data

Clinicos targets multilingual operation.

The system SHOULD support at least:

Persian
English
Azerbaijani Turkish
Arabic
Turkish

Language preferences SHOULD be stored as structured values.

Do not infer language solely from the last message when a confirmed user preference exists.

⸻

113. Localization

Localized content SHOULD be modeled carefully.

For clinic knowledge, where multilingual content is required, the architecture MAY use:

KnowledgeItem
    └── KnowledgeTranslation

rather than storing uncontrolled language fields.

The system MUST preserve the authoritative source language/content.

⸻

114. Patient Preferences

Patient preferences SHOULD be distinguishable from inferred preferences.

Example:

EXPLICIT:
Patient explicitly requested Persian.
INFERRED:
System estimates that Persian is preferred.

The latter MUST remain lower-confidence unless confirmed.

⸻

115. Data Ownership Rules

The following rules are mandatory:

1. Patient data belongs to the patient domain.
2. Lead state belongs to the lead domain.
3. Appointment state belongs to the appointment domain.
4. Service pricing belongs to pricing/service domain.
5. Clinic-approved knowledge belongs to knowledge domain.
6. Facial measurements belong to facial analysis domain.
7. AI execution metadata belongs to AI domain.
8. Analytics are derived data.
9. Events describe changes but do not replace current state.
10. Redis does not replace PostgreSQL as source of truth.

⸻

116. Security by Design

Database design MUST assume that:

* bugs happen
* developers make mistakes
* AI assistants hallucinate
* integrations retry
* requests arrive concurrently
* malicious input exists
* tenants must remain isolated

Therefore critical invariants SHOULD be enforced as close to the database as practical.

⸻

117. Performance Philosophy

Optimize only based on evidence.

Preferred order:

Correctness
↓
Integrity
↓
Security
↓
Observability
↓
Performance
↓
Optimization

Do not sacrifice data correctness for premature performance optimization.

⸻

118. Scalability

The target architecture SHOULD support growth from:

1 clinic

to:

many clinics

without requiring a complete database redesign.

Multi-tenancy MUST therefore be designed from the beginning.

⸻

119. Observability

Database-related monitoring SHOULD include:

* query latency
* connection pool health
* transaction failures
* deadlocks
* lock contention
* migration status
* backup status
* storage growth
* slow queries

⸻

120. Database Connection Management

The application MUST use controlled database connection pooling.

It MUST NOT create unbounded connections per request.

Connection settings SHOULD be environment-configurable.

⸻

121. Data Access Layer

Business logic SHOULD NOT scatter raw SQL throughout the codebase.

A clear persistence/data-access boundary SHOULD exist.

However, the assistant MUST follow the existing architecture when making incremental changes rather than introducing a massive abstraction layer without need.

⸻

122. Repository Pattern

Repositories or equivalent abstractions MAY be used for:

* patient access
* lead access
* appointment access
* knowledge access
* facial analysis access

The architectural choice SHOULD depend on actual project complexity.

Do not introduce patterns purely for aesthetic reasons.

⸻

123. Data Contracts

Important domain objects SHOULD have explicit schemas/contracts.

Examples:

Patient
Lead
Appointment
KnowledgeItem
FacialAnalysis
AIRequest
Notification

Contracts reduce accidental shape changes between modules.

⸻

124. Database as Contract

Database constraints are part of the system contract.

The application MUST NOT assume that database integrity can always be trusted if constraints are absent.

Critical constraints SHOULD be encoded at the database level whenever feasible.

⸻

125. Anti-Patterns

The following are prohibited or strongly discouraged:

125.1 Giant patient JSON blob

Do not store the entire patient state inside one JSON column.

125.2 AI as source of truth

Do not let generated text become authoritative business data automatically.

125.3 Redis as database

Do not rely on Redis for durable critical state.

125.4 Tenant filtering only in frontend

Tenant isolation MUST be enforced server-side.

125.5 No history

Do not overwrite critical state when historical auditing is required.

125.6 Hidden state machines

Do not encode business state transitions only as arbitrary if/else statements.

125.7 Untraceable AI output

Do not persist important AI decisions without provenance where traceability is required.

125.8 Public media URLs

Do not expose sensitive patient/facial images through unrestricted public URLs.

125.9 Hard-coded business rules

Do not hard-code policies that clinics may reasonably need to configure.

⸻

126. Definition of Done — Data Layer

A data-domain implementation is considered complete only when:

* schema is defined
* relationships are defined
* tenant isolation is enforced
* constraints are defined
* indexes are appropriate
* migrations exist
* rollback strategy is understood
* repository/data-access layer is updated
* tests exist
* concurrency risks are addressed
* auditability is addressed
* privacy implications are addressed
* actual PostgreSQL verification is performed when relevant

⸻

127. Required Verification

Before declaring database work complete, the AI assistant MUST verify:

Schema

* tables
* columns
* types
* constraints
* foreign keys
* indexes

Data integrity

* tenant isolation
* uniqueness
* state transitions
* orphan prevention

Runtime

* transactions
* concurrency
* retries
* idempotency

Security

* authorization
* sensitive data access
* media access

Operations

* migrations
* backup compatibility
* rollback
* monitoring

⸻

128. Honest Reporting

The AI assistant MUST distinguish:

Implemented
Verified
Partially verified
Not verified
Blocked

Example:

PostgreSQL migration created.
PostgreSQL integration test: NOT VERIFIED.
Reason: no PostgreSQL environment available.

The assistant MUST NEVER claim successful PostgreSQL verification if only SQLite or mocks were tested.

⸻

129. Target Data Architecture Summary

The intended data architecture is:

                    ┌──────────────────┐
                    │      Tenant      │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
     Users                Patients             Branches
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
             ▼                ▼                 ▼
        Identities       Conversations       Leads
             │                │                 │
             │                ▼                 ▼
             │             Messages          Followups
             │
             │
             └──────────────────────────────────────┐
                                                    │
                                                    ▼
                                              Appointments
                                                    │
                                                    ▼
                                                Services
                                                    │
                                                    ▼
                                                Doctors
      Knowledge ────────┐
      Safety ────────────┤
                         ▼
                    AI / Agents
                         │
             ┌───────────┼────────────┐
             ▼           ▼            ▼
         AI Requests   AI Usage   AI Decisions
      Patients
          │
          ▼
    Facial Analysis
          │
     ┌────┼──────────────┐
     ▼    ▼              ▼
 Images  Metrics     Observations
                         │
                         ▼
                  Recommendations
      Everything produces auditable events:
      Domain State
           ↓
      Domain Event
           ↓
      Automation
           ↓
      Notification / AI / Analytics / Reporting

⸻

130. Final Architectural Rules

The following rules are mandatory for Clinicos data architecture:

1. PostgreSQL is the authoritative transactional database.
2. Redis is not the source of truth.
3. Every tenant-owned entity MUST be tenant-scoped.
4. Cross-tenant access MUST be impossible through normal application paths.
5. Patient identity MUST be separated from channel identity.
6. Conversations MUST be separated from long-term patient memory.
7. Lead state MUST be separated from lead history.
8. Appointment availability MUST come from authoritative scheduling data.
9. AI MUST NOT invent prices or availability.
10. Knowledge MUST distinguish candidate information from approved information.
11. AI-generated knowledge MUST NOT automatically become authoritative.
12. Facial measurements MUST be separated from AI interpretation.
13. Facial images MUST receive stronger privacy protection.
14. AI execution MUST remain provider-agnostic.
15. FreeLLMAPI MAY be the current reference provider but MUST NOT become an architectural lock-in.
16. AI decisions SHOULD preserve provenance.
17. Critical state transitions MUST be explicit.
18. Critical operations MUST be transactionally safe.
19. External events MUST be idempotent.
20. Important changes SHOULD be auditable.
21. Historical state MUST be preserved where business decisions require it.
22. Sensitive data MUST be minimized and protected.
23. Database constraints SHOULD enforce critical invariants.
24. Analytics MUST NOT replace transactional truth.
25. Current repository structure MUST NOT override this target specification.
26. Migration from current → target MUST be deliberate and verified.
27. SQLite-only tests MUST NOT be presented as full PostgreSQL verification.
28. No credentials, API keys, or secrets belong in this specification or database design.
29. The database MUST support future channels beyond Telegram.
30. The database MUST support future multi-agent architecture without coupling core entities to a specific agent implementation.
31. Business policies SHOULD be configurable rather than hard-coded when appropriate.
32. Correctness, security, privacy, and reliability take priority over premature optimization.

⸻

131. Final Objective

The goal is not merely to create a database that can store the current Clinicos code.

The goal is to create a durable data foundation for the long-term Clinicos product.

Clinicos should be able to evolve from:

Telegram AI bot

into:

Multi-channel
AI-native
Multi-tenant
Clinic Operating System

without repeatedly redesigning its fundamental data architecture.

The data layer must therefore support:

Patient Intelligence
Lead Intelligence
Follow-up Automation
Appointments
Clinic Knowledge
Medical Safety
AI Agents
Facial Analysis
Notifications
Analytics
Reporting
A/B Testing
Conversion Intelligence
Human Takeover
Future Voice
Future Channels

while maintaining:

Security
Privacy
Tenant Isolation
Data Integrity
Auditability
Observability
Scalability
Provider Independence

This specification defines the target data architecture.

The current repository is an implementation starting point.

The engineering task is to progressively and safely move the implementation toward this target.
