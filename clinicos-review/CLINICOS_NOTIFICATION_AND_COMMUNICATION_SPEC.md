# CLINICOS_NOTIFICATION_AND_COMMUNICATION_SPEC.md
## 1. Document Purpose
This document defines the target architecture, domain boundaries, communication model, notification system, channel abstraction, delivery lifecycle, message composition, personalization, consent enforcement, reliability, security, privacy, observability, AI integration, human interaction, localization, and testing requirements for notifications and communication in Clinicos.
The Notification and Communication domain is responsible for reliably delivering approved communication through supported channels.
It is not responsible for deciding whether a business workflow should exist.
The system must separate:
1. Business intent.
2. Communication policy.
3. Message generation.
4. Message validation.
5. Channel selection.
6. Message delivery.
7. Delivery confirmation.
8. Failure handling.
9. Auditability.
Clinicos must never treat message generation and message delivery as the same responsibility.
---
# 2. Core Principle
The Communication Layer delivers messages.
It does not independently decide:
- whether a follow-up should happen
- whether a patient should be contacted
- whether a reminder is medically appropriate
- whether marketing consent exists
- whether a patient should be reactivated
- whether an appointment should be cancelled
- whether a clinical escalation is required
Those decisions belong to the appropriate upstream domain.
The Communication Layer receives an authorized communication request and attempts to deliver it through an appropriate channel.
---
# 3. Communication Safety Hierarchy
Communication behavior must follow this hierarchy:
1. Medical Safety
2. Privacy and Confidentiality
3. Consent
4. Authorization
5. Operational Correctness
6. User Preferences
7. Patient Convenience
8. Communication Reliability
9. Commercial Optimization
Commercial goals must never override safety, privacy, consent, or authorization.
---
# 4. Scope
This specification covers:
- communication channels
- channel abstraction
- notifications
- outbound messages
- inbound messages
- message templates
- message composition
- AI-generated messages
- staff-authored messages
- transactional notifications
- appointment notifications
- follow-up notifications
- marketing communication
- consent
- preferences
- quiet hours
- delivery states
- retries
- provider failover
- rate limiting
- message deduplication
- idempotency
- delivery tracking
- webhook handling
- channel capabilities
- localization
- multilingual communication
- media delivery
- attachments
- message security
- communication audit
- observability
- analytics
- human takeover
- communication suppression
- emergency communication
- provider integrations
---
# 5. Non-Goals
The Communication Layer does not own:
- lead scoring
- appointment availability
- medical diagnosis
- medical treatment recommendations
- follow-up policy
- patient segmentation
- clinical triage
- clinic business rules
- LLM provider selection
- knowledge retrieval
- facial analysis
These belong to other Clinicos domains.
---
# 6. Architectural Position
The Communication Layer sits downstream from business workflows.
A simplified architecture is:
```text
Business Domain
      |
      v
Policy / Workflow Engine
      |
      v
Communication Request
      |
      v
Message Composition
      |
      v
Policy Validation
      |
      v
Channel Selection
      |
      v
Communication Orchestrator
      |
      +----> Telegram Adapter
      +----> Instagram Adapter
      +----> WhatsApp Adapter
      +----> SMS Adapter
      +----> Email Adapter
      +----> Web Adapter
      +----> Mobile Adapter
      +----> Internal Notification Adapter
      |
      v
Provider
      |
      v
Delivery Events
      |
      v
Communication State
      |
      v
Analytics / Audit

⸻

7. Communication Sources

Communication requests may originate from:

* Appointment and Scheduling
* Follow-Up Engine
* Lead Management
* Patient Intelligence
* Medical Safety
* Clinic Management
* Secretary Copilot
* AI Agents
* Staff
* System events
* External integrations

The source must be identifiable.

⸻

8. Communication Intent

Every outbound communication should have an explicit intent.

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
PAYMENT_NOTICE
SAFETY_ESCALATION
HUMAN_CALLBACK
MARKETING
SYSTEM_NOTIFICATION
INTERNAL_STAFF_NOTIFICATION

The exact enumeration may evolve.

⸻

9. Intent Is Not Authorization

Having a valid intent does not automatically authorize delivery.

For example:

intent = MARKETING

does not mean:

marketing_consent = true

Consent and policy must be evaluated separately.

⸻

10. Communication Request

A communication request should conceptually contain:

communication_id
tenant_id
recipient_id
intent
priority
channel_preference
content_reference
locale
scheduled_at
expiration_at
source
idempotency_key
policy_context
metadata

Exact API and schema details may evolve.

⸻

11. Recipient

A recipient may be:

* patient
* lead
* staff member
* doctor
* manager
* clinic owner
* system operator

Recipient identity must resolve through the canonical identity system.

⸻

12. Recipient Identity

A recipient may have multiple communication endpoints.

Example:

Patient
 |
 +-- Telegram account
 +-- WhatsApp number
 +-- Phone number
 +-- Email
 +-- Web account

Communication endpoints must not automatically be treated as separate people.

⸻

13. Communication Endpoint

An endpoint represents a destination on a specific channel.

Conceptual model:

endpoint_id
recipient_id
channel
address
status
verified
preferred
capabilities
last_seen_at
metadata

⸻

14. Endpoint Verification

Where applicable, communication endpoints should be verified.

Examples:

* verified phone number
* verified email
* authenticated Telegram identity
* authenticated web account

Unverified endpoints must have restricted capabilities.

⸻

15. Channel Abstraction

The Communication Layer must expose a channel-independent interface.

Example:

send_message()
send_media()
send_template()
send_interactive_message()

Channel adapters translate these operations into provider-specific APIs.

⸻

16. Supported Channels

Target channels include:

TELEGRAM
INSTAGRAM
WHATSAPP
SMS
EMAIL
WEB_CHAT
MOBILE_PUSH
IN_APP
VOICE
INTERNAL

Not every channel must be available in every deployment.

⸻

17. Telegram

Telegram is an initial communication channel for Clinicos.

The Telegram adapter may support:

* text
* images
* documents
* buttons
* inline actions
* menus
* media groups
* message editing where supported
* message deletion where supported

The business layer must remain independent of Telegram-specific implementation.

⸻

18. Instagram

Future Instagram integration may support:

* direct messages
* supported interactive elements
* media
* automated responses

Availability depends on official platform capabilities and clinic authorization.

⸻

19. WhatsApp

WhatsApp integration may support:

* text
* approved templates
* media
* interactive messages
* transactional notifications

The implementation must respect the provider’s policy and message-template requirements.

⸻

20. SMS

SMS may be used for:

* appointment reminders
* verification
* urgent operational notifications
* selected transactional communication

SMS should generally not be used for long-form clinical information.

⸻

21. Email

Email may support:

* transactional notifications
* appointment information
* reports
* documents
* receipts
* selected marketing communication

Sensitive information must be minimized.

⸻

22. Web Chat

Web chat may support:

* real-time conversation
* notifications
* structured actions
* appointment operations
* file and media exchange

Authentication must be explicit.

⸻

23. Mobile Push

Push notifications may be used for:

* appointment reminders
* staff alerts
* workflow notifications
* system events

Push payloads must avoid exposing sensitive medical information on lock screens unless explicitly configured.

⸻

24. In-App Notifications

In-app notifications may contain more context because the user is inside an authenticated application.

Authorization must still be enforced.

⸻

25. Voice

Voice communication may be supported through external providers.

Voice automation must be governed by explicit consent, policy, and safety rules.

⸻

26. Internal Notifications

Internal notifications may target:

* secretary
* doctor
* manager
* owner
* support staff

Examples:

NEW_LEAD
URGENT_PATIENT_REVIEW
MISSED_CALL
BOOKING_CONFLICT
SAFETY_ESCALATION
SYSTEM_FAILURE

⸻

27. Channel Capabilities

Each channel adapter must declare capabilities.

Example:

{
  "text": true,
  "image": true,
  "document": true,
  "buttons": true,
  "rich_cards": false,
  "message_edit": true,
  "message_delete": true
}

The communication orchestrator must not assume that all channels support the same features.

⸻

28. Capability Negotiation

Message composition should adapt to channel capabilities.

Example:

Preferred:
Rich interactive card
Telegram:
Interactive buttons
SMS:
Plain text fallback

The semantic content must remain consistent.

⸻

29. Channel Fallback

A communication request may define fallback channels.

Example:

Telegram
    |
    v
WhatsApp
    |
    v
SMS

Fallback must only occur when:

* policy permits it
* consent permits it
* the alternative endpoint is valid
* the message intent is compatible with the fallback channel

⸻

30. No Unauthorized Fallback

A failed Telegram delivery must not automatically result in SMS marketing unless SMS marketing consent exists.

Channel fallback is not a consent bypass.

⸻

31. Preferred Channel

Patients may define preferred communication channels.

Preference hierarchy may be:

Explicit current request
>
Explicit channel preference
>
Verified preferred endpoint
>
Clinic default

⸻

32. Channel Preference vs Consent

Preference and consent are different.

Example:

Preferred channel = WhatsApp
Marketing consent = false

means:

The patient prefers WhatsApp for allowed communication, not that marketing through WhatsApp is authorized.

⸻

33. Communication Categories

Communication should be classified into categories such as:

TRANSACTIONAL
OPERATIONAL
CLINICAL_SAFETY
MARKETING
INTERNAL
AUTHENTICATION

Different categories have different policy requirements.

⸻

34. Transactional Communication

Transactional communication is directly related to an action or service requested by the patient.

Examples:

* appointment confirmation
* appointment cancellation
* password reset
* requested document

⸻

35. Operational Communication

Operational messages may include:

* clinic closure
* provider schedule change
* appointment location change
* system-generated administrative notice

⸻

36. Clinical Safety Communication

Clinical safety communication is initiated by a safety workflow.

It must follow Medical Safety policies.

Examples:

* urgent escalation
* adverse-event review request
* clinician callback request

⸻

37. Marketing Communication

Marketing communication includes:

* promotions
* campaigns
* reactivation offers
* promotional announcements
* cross-selling
* upselling

Marketing communication requires appropriate consent and policy compliance.

⸻

38. Authentication Communication

Authentication communication may include:

* OTP
* verification
* password reset
* security alerts

These messages should be treated separately from marketing.

⸻

39. Communication Policy

Every communication request must pass through policy evaluation.

Policy may consider:

* recipient
* intent
* consent
* channel
* time
* frequency
* quiet hours
* clinic policy
* patient preference
* safety state
* human ownership
* prior communication
* legal restrictions

⸻

40. Communication Policy Engine

The Communication Policy Engine should answer:

Can this message be sent?
Through which channels?
At what time?
With what content?
With what frequency?
Does approval require a human?

⸻

41. Follow-Up Integration

The Follow-Up Engine decides whether a follow-up should exist.

The Communication Layer decides how an approved follow-up is delivered.

Architecture:

Follow-Up Engine
      |
      v
Communication Request
      |
      v
Communication Policy
      |
      v
Message Composition
      |
      v
Channel Delivery

⸻

42. Appointment Integration

Appointment and Scheduling emits appointment events.

The Communication Layer may receive requests such as:

appointment_confirmation
appointment_reminder
appointment_changed
appointment_cancelled

The Follow-Up Engine remains responsible for reminder scheduling.

⸻

43. Medical Safety Integration

Medical Safety may create high-priority communication requests.

Examples:

SAFETY_ESCALATION
HUMAN_REVIEW
URGENT_CALLBACK

These messages must follow safety-specific policies.

⸻

44. Medical Safety Priority

Safety communication may override normal communication preferences when policy and law permit.

However, the system must not use “safety” as a generic reason to send unrelated marketing or commercial messages.

⸻

45. Human Takeover

Human ownership may suppress automated communication.

Example:

Patient is actively handled by secretary.

Automated follow-up may be paused according to workflow policy.

⸻

46. Human-Sent Messages

Staff messages should use the same communication infrastructure where possible.

This provides:

* consistent delivery tracking
* auditability
* channel abstraction
* rate limiting
* analytics

⸻

47. AI-Generated Messages

AI may generate communication content when authorized.

AI-generated messages must pass validation before delivery.

Validation may include:

* policy
* safety
* privacy
* hallucination
* tone
* language
* prohibited content
* dynamic data grounding

⸻

48. AI Must Not Invent Operational Facts

AI must not invent:

* appointment times
* provider availability
* prices
* clinic hours
* discounts
* policies
* payment status
* delivery status

Dynamic facts must come from authoritative tools.

⸻

49. Message Composition Pipeline

Recommended pipeline:

Communication Intent
       |
       v
Load Structured Data
       |
       v
Select Template / Generate Content
       |
       v
Personalization
       |
       v
Localization
       |
       v
Safety Validation
       |
       v
Privacy Validation
       |
       v
Policy Validation
       |
       v
Channel Rendering
       |
       v
Final Validation
       |
       v
Delivery

⸻

50. Templates

Templates should be preferred for deterministic transactional messages.

Examples:

Appointment confirmation
Appointment reminder
Password reset
Verification
Clinic closure

Templates reduce hallucination risk.

⸻

51. AI Template Personalization

AI may personalize approved templates within strict boundaries.

Example:

Template:
"Your appointment is scheduled for {{appointment_time}}."
AI:
May adapt tone and language.
AI:
Must not change appointment_time.

⸻

52. Structured Variables

Dynamic values should be represented as structured variables.

Example:

{
  "patient_name": "Sara",
  "appointment_date": "2026-09-25",
  "appointment_time": "17:30",
  "provider_name": "Dr. Example"
}

These values must come from authoritative systems.

⸻

53. Immutable Message Snapshot

Once a message is approved for delivery, the system should preserve the final message representation or a secure reconstructable snapshot.

This supports auditability.

⸻

54. Message Entity

Conceptual message entity:

message_id
tenant_id
recipient_id
conversation_id
intent
category
channel
endpoint_id
content
content_type
status
priority
scheduled_at
sent_at
delivered_at
failed_at
provider_message_id
created_at
updated_at

⸻

55. Message Status Lifecycle

Recommended states:

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

⸻

56. Message State Semantics

CREATED

Message request exists.

PENDING_POLICY

Policy validation is in progress.

APPROVED

Message is allowed to proceed.

SCHEDULED

Message has a future delivery time.

READY

Message can be sent.

SENDING

Provider delivery attempt is in progress.

SENT

Provider accepted the message.

DELIVERED

Provider confirmed delivery where supported.

READ

Recipient read the message where supported.

FAILED

Delivery failed.

RETRY_SCHEDULED

A retry is planned.

CANCELLED

Delivery was intentionally cancelled.

BLOCKED

Policy or safety prevented delivery.

EXPIRED

The message was no longer valid when execution was attempted.

SUPPRESSED

Delivery was prevented by a suppression rule.

⸻

57. Sent vs Delivered

These are different states.

SENT

means the provider accepted the request.

DELIVERED

means the provider reported successful delivery.

The system must not claim delivery when only provider acceptance is known.

⸻

58. Delivered vs Read

Read receipts are channel-dependent.

The system must never claim that a patient read a message unless the channel explicitly reports it.

⸻

59. Delivery Provider

A channel may have one or more providers.

Example:

SMS
 |
 +-- Provider A
 +-- Provider B

Provider abstraction must allow replacement.

⸻

60. Provider Routing

Provider routing may consider:

* availability
* cost
* latency
* rate limits
* reliability
* geographic restrictions
* message type
* channel requirements

Routing must not violate policy.

⸻

61. Provider Failover

Provider failure may trigger failover when:

* the message remains valid
* the alternate provider supports the content
* the alternate provider is authorized
* retry policy allows it

⸻

62. Provider Failover and Duplication

Failover must consider whether the first provider may already have accepted the message.

The system must use idempotency or provider reconciliation to reduce duplicate delivery.

⸻

63. Idempotency

Every send operation should have an idempotency key where supported.

Example:

communication_id + attempt_scope

Repeated processing must not intentionally create duplicate messages.

⸻

64. Duplicate Message Prevention

Duplicates may occur due to:

* queue retries
* worker restart
* webhook replay
* provider timeout
* network failures
* user retries

The system must use deterministic deduplication.

⸻

65. Message Deduplication

Communication deduplication should consider:

* communication intent
* recipient
* channel
* content fingerprint
* time window
* workflow instance
* idempotency key

Exact rules must be configurable.

⸻

66. Frequency Limits

Communication policies may limit:

* messages per hour
* messages per day
* messages per week
* marketing messages per campaign
* reminders per appointment

⸻

67. Communication Fatigue

The system should track communication load.

Examples:

messages_last_24h
messages_last_7d
marketing_messages_last_30d

Excessive communication should trigger suppression or policy review.

⸻

68. Quiet Hours

Quiet hours should be configurable per clinic and optionally per patient.

Example:

22:00–08:00

Non-urgent communication should normally be delayed.

⸻

69. Quiet Hours and Urgency

Urgent safety communication may use a different policy.

The system must distinguish:

URGENT_SAFETY

from:

MARKETING

⸻

70. Scheduling Communication

Messages may be scheduled for future delivery.

Scheduled messages must be revalidated before execution.

A scheduled message is not permanent authorization.

⸻

71. Pre-Send Revalidation

Immediately before sending, the system should revalidate:

* recipient status
* consent
* communication policy
* safety state
* human ownership
* cancellation state
* appointment state if relevant
* message expiration
* channel availability

⸻

72. Cancelled Appointment Reminder

If an appointment is cancelled, its future reminder must not be sent.

This requires reconciliation between Scheduling and Follow-Up.

⸻

73. Rescheduled Appointment Reminder

If an appointment is rescheduled, old reminders must be reconciled and new reminders generated as appropriate.

⸻

74. Stale Messages

Messages may become invalid before delivery.

Examples:

Appointment cancelled
Offer expired
Provider changed
Patient opted out
Safety state changed

The system must suppress stale messages.

⸻

75. Expiration

Communication requests may have an expiration time.

Example:

expiration_at = appointment_start_at

A reminder should not be delivered after the appointment has already started.

⸻

76. Cancellation

Scheduled communication should support cancellation.

Cancellation sources include:

* workflow cancellation
* appointment cancellation
* patient opt-out
* human takeover
* policy change
* safety escalation
* campaign cancellation

⸻

77. Consent

Consent must be explicit where required.

Consent types may include:

TRANSACTIONAL
MARKETING
VOICE
SMS
EMAIL
WHATSAPP
DATA_PROCESSING
MEDIA

Exact categories may evolve.

⸻

78. Consent Is Channel-Specific Where Required

A patient may consent to marketing through:

Email

without consenting to:

SMS

The system must not assume universal consent.

⸻

79. Consent Revocation

Consent revocation must take effect promptly.

Future unauthorized communications must be blocked.

⸻

80. Unknown Consent

Unknown consent must not be treated as positive marketing consent.

⸻

81. Transactional vs Marketing

The system must not label promotional content as transactional merely to bypass consent requirements.

Example:

"Your appointment is tomorrow."

may be transactional.

"Your appointment is tomorrow. Book another treatment now with 30% off."

contains marketing content and must be evaluated accordingly.

⸻

82. Mixed-Intent Messages

Messages containing both transactional and marketing content should be classified according to the stricter applicable policy.

The preferred design is to separate transactional and promotional messages.

⸻

83. Opt-Out

Patients must be able to opt out of applicable communication categories.

Examples:

STOP
Unsubscribe
Disable marketing

The exact mechanism depends on channel.

⸻

84. Opt-Out Processing

Opt-out events must be:

* authenticated where possible
* recorded
* auditable
* propagated to communication preferences
* applied to future communication

⸻

85. Emergency Opt-Out Exception

The system must define whether certain legally or clinically necessary communications may continue after opt-out.

Such behavior must be governed by explicit policy.

⸻

86. Preference Center

Future Clinicos UX should provide a communication preference center.

Patients may configure:

Preferred channels
Language
Quiet hours
Marketing preference
Reminder preference
Notification categories

⸻

87. Communication Preference Storage

Preferences should be structured.

Example:

{
  "language": "fa",
  "preferred_channels": ["telegram"],
  "marketing": false,
  "quiet_hours": {
    "start": "22:00",
    "end": "08:00"
  }
}

⸻

88. Preference Precedence

Recommended precedence:

Safety / Legal Requirement
>
Explicit Current User Request
>
Consent
>
Patient Preference
>
Clinic Policy
>
System Default

Actual policy may vary for specific categories.

⸻

89. Localization

Communication should support:

fa
en
az
ar
tr

⸻

90. Language Selection

Language should be determined using:

Current explicit request
>
Patient language preference
>
Conversation language
>
Clinic default

⸻

91. Translation

Transactional messages should preferably use professionally reviewed templates for high-risk communication.

AI translation may be used for lower-risk communication subject to validation.

⸻

92. Medical Communication Translation

Medical safety messages require stricter translation validation.

The system must not introduce clinical meaning changes during translation.

⸻

93. Code-Switching

Patient messages may contain multiple languages.

The system should preserve structured data and meaning when responding.

⸻

94. Formatting

Channel-specific rendering may include:

* bold
* lists
* buttons
* links
* images
* documents
* tables where supported

Formatting must not alter the underlying meaning.

⸻

95. Plain Text Fallback

Every important communication should have a plain-text fallback when possible.

This is essential for channels with limited formatting.

⸻

96. Rich Media

Communication may contain:

* images
* videos
* documents
* audio
* PDFs

Media must be validated before delivery.

⸻

97. Media Security

Uploaded or generated media should be:

* access-controlled
* scanned where applicable
* securely stored
* served through controlled URLs
* protected against unauthorized access

⸻

98. Temporary Media URLs

Sensitive media should preferably use short-lived signed URLs rather than permanent public URLs.

⸻

99. Medical Images

Medical or facial-analysis images must receive stricter privacy treatment.

They must not be sent to unrelated recipients or channels.

⸻

100. Facial Analysis Communication

If facial analysis produces a report, the Communication Layer may deliver it only after:

* analysis completion
* policy validation
* privacy validation
* recipient authorization

⸻

101. Document Delivery

Documents may include:

* reports
* appointment receipts
* invoices
* consent forms
* educational documents

Document access must be authorized.

⸻

102. File Expiration

Temporary files should expire according to policy.

⸻

103. Links

Links included in messages should be:

* HTTPS
* trusted
* scoped
* validated
* appropriate for the recipient

⸻

104. Deep Links

Secure deep links may support actions such as:

Confirm appointment
Reschedule appointment
Cancel appointment
View report
Contact clinic

Actions must still be authorized server-side.

⸻

105. Link Security

Possession of a link must not automatically grant unrestricted access to patient data.

⸻

106. Message Priority

Recommended priority levels:

CRITICAL
HIGH
NORMAL
LOW

Examples:

CRITICAL:
Safety escalation
HIGH:
Appointment cancellation by clinic
NORMAL:
Appointment reminder
LOW:
Marketing campaign

⸻

107. Queue Architecture

Communication delivery should use queues where appropriate.

Example:

Communication Request
        |
        v
Priority Queue
        |
        v
Worker
        |
        v
Channel Adapter

⸻

108. Priority Isolation

Low-priority marketing traffic must not block urgent safety or operational communication.

⸻

109. Rate Limiting

Rate limits may apply at:

* tenant
* recipient
* channel
* provider
* campaign
* IP
* endpoint

⸻

110. Backpressure

The communication system must protect providers from overload.

If queues grow excessively:

* low-priority traffic may be delayed
* campaigns may be paused
* retries may be slowed
* urgent messages retain priority

⸻

111. Retry Strategy

Retries should use bounded exponential backoff with jitter where appropriate.

Example:

Attempt 1
Attempt 2
Attempt 3
Attempt 4

Maximum attempts must be configured.

⸻

112. Retryable Errors

Potentially retryable:

timeout
temporary network failure
provider 5xx
rate limit
temporary provider outage

⸻

113. Non-Retryable Errors

Examples:

invalid recipient
invalid credentials
permission denied
unsupported content
invalid template
recipient blocked
consent denied

⸻

114. Rate-Limit Handling

When a provider returns a rate-limit response, the system should respect the provider’s retry guidance where available.

⸻

115. Circuit Breaker

A channel provider with repeated failures should be temporarily isolated.

⸻

116. Dead Letter Queue

Messages that repeatedly fail should enter a dead-letter or failure-review queue.

Staff/system operators should be able to inspect them.

⸻

117. Delivery Reconciliation

Provider callbacks should reconcile:

SENT
DELIVERED
READ
FAILED

states.

Webhook events must be idempotent.

⸻

118. Webhook Security

Provider webhooks must be:

* authenticated
* signature-verified where supported
* replay-protected where possible
* rate-limited
* logged
* scoped to the correct tenant

⸻

119. Webhook Ordering

Provider events may arrive out of order.

The system must handle:

DELIVERED
then
SENT

without corrupting state.

State transitions should use event timestamps and valid transition rules.

⸻

120. Provider Message IDs

Every provider message should store the provider’s external message ID where available.

This enables reconciliation.

⸻

121. Communication Event Model

Recommended events:

communication.created
communication.approved
communication.scheduled
communication.ready
communication.sending
communication.sent
communication.delivered
communication.read
communication.failed
communication.retry_scheduled
communication.cancelled
communication.blocked
communication.suppressed
communication.expired

⸻

122. Event vs Command

A command:

send_message

requests an action.

An event:

communication.sent

describes an action that happened.

These concepts must remain separate.

⸻

123. Outbox Pattern

Communication events should use an outbox or equivalent reliable publication mechanism.

⸻

124. Exactly-Once Illusion

Distributed systems generally cannot guarantee simple exactly-once delivery.

Clinicos should use:

at-least-once processing
+
idempotency
+
deduplication
+
provider reconciliation

⸻

125. Delivery Semantics

The system should clearly distinguish:

request accepted
provider accepted
delivered
read

These are not equivalent.

⸻

126. User-Facing Delivery Claims

The AI must not say:

“Your message was delivered.”

unless delivery has been confirmed.

Similarly:

“Your message was read.”

requires an actual read event.

⸻

127. Communication Failure UX

When delivery fails, the system should provide a useful fallback.

Example:

I could not deliver the message through Telegram. Would you like me to try another available channel?

Only offer channels that are actually available and authorized.

⸻

128. Staff Notification on Failure

Critical communication failures may trigger internal staff alerts.

Example:

Safety message failed to deliver.

⸻

129. Safety Message Escalation

If a critical safety message fails repeatedly, the system should escalate to an alternative authorized communication path or human staff according to policy.

⸻

130. No Infinite Retry

No message should retry indefinitely.

Every retry path must have a maximum boundary.

⸻

131. Communication Loop Prevention

The system must prevent loops such as:

Bot message
 -> Bot receives event
 -> Bot responds
 -> Bot receives event
 -> ...

⸻

132. Self-Message Detection

Channel adapters should identify messages originating from the clinic/system where possible.

⸻

133. Automated Conversation Loop

AI agents must not automatically respond to their own generated content.

⸻

134. Campaign Isolation

Marketing campaigns should be isolated from transactional messaging queues.

Campaign failure must not block operational communication.

⸻

135. Campaign Cancellation

Marketing campaigns must support global cancellation.

Already-sent messages remain historical facts.

Queued future messages should be suppressed.

⸻

136. Campaign Consent Revalidation

Marketing consent must be rechecked before campaign message delivery.

Consent at campaign creation time is not necessarily sufficient for future delivery.

⸻

137. Campaign Frequency

Campaign systems must respect:

* frequency caps
* quiet hours
* channel preferences
* recent contact limits
* suppression lists

⸻

138. Patient Suppression

Patients may be suppressed from specific communication categories.

Examples:

ALL_MARKETING
PROMOTIONAL_SMS
AUTOMATED_FOLLOWUP

⸻

139. Global Suppression

Clinic administrators may temporarily suppress:

* marketing
* automated messages
* a specific channel
* a specific campaign

⸻

140. Channel Outage

If a channel is unavailable:

* queue messages where appropriate
* fail over where allowed
* notify staff for critical communication
* prevent false delivery claims

⸻

141. Provider Outage

Provider outages should trigger:

* health monitoring
* circuit breaker
* controlled failover
* alerting
* recovery testing

⸻

142. Channel Health

The system should track:

provider_up
provider_latency
provider_error_rate
delivery_rate
failure_rate
queue_depth

⸻

143. Communication Analytics

Metrics may include:

messages_sent
messages_delivered
messages_read
delivery_rate
failure_rate
retry_rate
average_latency
channel_distribution
opt_out_rate

⸻

144. Campaign Analytics

Marketing analytics may include:

delivered
opened
clicked
replied
converted
unsubscribed

These metrics must be based on actual channel events.

⸻

145. Appointment Communication Analytics

Metrics may include:

reminder_delivery_rate
confirmation_rate
cancellation_after_reminder
reschedule_after_reminder
no_show_after_reminder

⸻

146. AI Communication Analytics

Metrics may include:

AI_generated_message_rate
human_edit_rate
human_rejection_rate
policy_block_rate
hallucination_rate
language_error_rate

⸻

147. Human Edit Rate

If staff frequently modify AI-generated messages, this may indicate quality or policy issues.

⸻

148. AI Message Evaluation

AI-generated communication should be evaluated for:

* factual correctness
* policy compliance
* safety
* tone
* language
* personalization
* privacy
* hallucination

⸻

149. AI Approval Modes

Possible modes:

AUTO
STAFF_APPROVAL
STAFF_ONLY
DISABLED

⸻

150. High-Risk Communication

High-risk messages should require stricter approval.

Examples:

* medical safety
* sensitive clinical information
* legal notices
* high-impact patient instructions

⸻

151. Medical Content Boundary

The Communication Layer should not independently generate medical advice.

If medical content is required, it should come from:

* authorized clinical workflow
* approved knowledge
* clinician-authored content
* Medical Safety domain

⸻

152. Medical Message Validation

Medical communication should be validated for:

* factual grounding
* safety
* appropriate uncertainty
* escalation instructions
* language correctness

⸻

153. Emergency Communication

Emergency communication should be generated or selected through a dedicated safety workflow.

The communication layer focuses on delivery reliability.

⸻

154. Confidentiality

Messages containing sensitive information must be delivered only to authorized recipients.

⸻

155. Data Minimization in Notifications

Notification previews should contain minimal sensitive information.

Example:

Bad:

Your biopsy for suspected melanoma is scheduled tomorrow.

Better:

You have an appointment tomorrow. Open Clinicos for details.

The exact content depends on policy and user settings.

⸻

156. Lock-Screen Privacy

Push notifications should avoid exposing sensitive medical information on lock screens by default.

⸻

157. Email Privacy

Sensitive medical details should be minimized in email subject lines.

⸻

158. SMS Privacy

Sensitive information should generally not be included in SMS unless explicitly authorized and appropriate.

⸻

159. Patient Identity Verification

Before disclosing sensitive appointment or medical information, the system must verify that the recipient is authorized.

⸻

160. Wrong-Recipient Protection

The system should detect suspicious endpoint changes and avoid immediately sending sensitive information to newly changed destinations where additional verification is required.

⸻

161. Communication Access Logs

Sensitive communication access should be logged.

⸻

162. Tenant Isolation

Communication queries must always be scoped by tenant.

A message belonging to Clinic A must never be visible to Clinic B.

⸻

163. Staff Access

Staff should only access communications permitted by their role.

⸻

164. Internal vs Patient Communication

Internal staff messages must be clearly separated from patient-facing communication.

Internal notes must never accidentally be sent to patients.

⸻

165. AI Prompt Isolation

Patient-specific data passed to an AI model should be limited to what is necessary for the message.

⸻

166. Prompt Injection Defense

Patient-authored content must never override:

* system policies
* consent rules
* channel restrictions
* safety rules
* authorization

⸻

167. Secret Protection

API keys, provider credentials, tokens, and secrets must never be included in message content, logs, prompts, or user-visible errors.

⸻

168. Error Messages

Errors shown to users must not expose:

* provider credentials
* internal URLs
* stack traces
* database details
* internal identifiers

⸻

169. Communication Audit

The system should preserve an auditable trail of:

who requested
what was requested
why
which policy allowed it
which channel was selected
what content was sent
when
delivery result
provider response

Sensitive content should be stored according to retention policy.

⸻

170. Content Retention

Message content retention should be configurable.

Possible strategies:

FULL_CONTENT
REDACTED_CONTENT
CONTENT_HASH
METADATA_ONLY

The selected strategy depends on compliance and product requirements.

⸻

171. Audit vs Privacy

Auditability must not become an excuse to retain unnecessary sensitive data.

Store the minimum data necessary.

⸻

172. Message Encryption

Sensitive communication data should be protected at rest and in transit.

⸻

173. Transport Security

External provider communication must use secure transport.

⸻

174. Credential Rotation

Provider credentials must support rotation without requiring major application changes.

⸻

175. Secret Management

Secrets should be stored in secure secret-management infrastructure.

They must not be hardcoded in source code.

⸻

176. Provider Abstraction

Each channel/provider integration should implement a common interface.

Conceptually:

class CommunicationProvider:
    async def send_text(...):
        ...
    async def send_media(...):
        ...
    async def get_delivery_status(...):
        ...
    async def health_check(...):
        ...

The exact implementation may differ.

⸻

177. Adapter Isolation

Provider-specific code must remain inside adapters.

Business logic must not contain provider-specific assumptions.

⸻

178. Provider Replacement

The system should allow replacing a communication provider without rewriting business workflows.

⸻

179. Channel Configuration

Clinic administrators may configure:

* enabled channels
* preferred providers
* sender identity
* fallback behavior
* rate limits
* quiet hours
* templates
* consent requirements

⸻

180. Sender Identity

Each channel may have a sender identity.

Examples:

Telegram Bot
WhatsApp Business Number
SMS Sender
Email Address
Web Application

Sender identity must be tenant-scoped.

⸻

181. Sender Authorization

A tenant must only be able to send through sender identities it is authorized to use.

⸻

182. Communication Templates

Templates should be versioned.

A template may contain:

template_id
version
intent
language
channel
content
variables
status
created_by
approved_by

⸻

183. Template Approval

High-risk templates may require staff approval before activation.

⸻

184. Template Version Stability

A scheduled message should use the intended template version or a clearly defined current version policy.

Changing a template must not silently mutate already-approved messages.

⸻

185. Template Testing

Templates should be tested for:

* missing variables
* incorrect formatting
* unsupported channel features
* translation issues
* excessive length

⸻

186. Channel Length Limits

Adapters must enforce channel-specific message limits.

Long messages may be split where appropriate.

⸻

187. Message Splitting

When splitting is necessary:

* preserve ordering
* avoid splitting sensitive values incorrectly
* preserve context
* avoid excessive fragmentation

⸻

188. Markdown and HTML Safety

User-generated or AI-generated formatting must be sanitized according to channel requirements.

⸻

189. Link Preview Control

For sensitive messages, link previews may need to be disabled.

⸻

190. Media Fallback

If a channel cannot deliver media, the system may provide:

* secure link
* alternative format
* plain-text explanation

only when policy permits.

⸻

191. Voice Message

Voice messages should include metadata:

duration
language
source
transcription_available

⸻

192. Voice Safety

AI-generated voice communication requires additional review for:

* identity representation
* accidental impersonation
* medical misinformation
* consent

⸻

193. Voice Transcription

Inbound voice messages may be transcribed for AI processing.

The transcription pipeline must preserve privacy and language context.

⸻

194. Inbound Communication

The Communication Layer also handles inbound messages.

Inbound messages may include:

* text
* images
* voice
* documents
* button actions
* reactions
* delivery responses

⸻

195. Inbound Normalization

Channel-specific inbound events should be normalized into a common structure.

Example:

InboundMessage
    message_id
    tenant_id
    channel
    sender_endpoint
    recipient_endpoint
    content
    content_type
    timestamp
    provider_message_id
    metadata

⸻

196. Inbound Routing

After normalization:

Inbound Message
      |
      v
Identity Resolution
      |
      v
Conversation Routing
      |
      v
Relevant Domain / Agent

⸻

197. Inbound Authorization

Incoming button actions and links must be authorized.

A button labeled “Cancel appointment” must not bypass server-side permission checks.

⸻

198. Inbound Spam

The system should detect:

* spam
* abuse
* repeated automated messages
* suspicious link attacks
* malicious payloads

⸻

199. Abuse Protection

Communication endpoints should support:

* rate limiting
* temporary blocking
* abuse scoring
* manual review

⸻

200. Conversation Continuity

Messages should be linked to conversations where applicable.

The communication system should preserve enough metadata to reconstruct communication history without becoming the owner of conversation business logic.

⸻

201. Communication History

Authorized users may view communication history.

The history should distinguish:

Inbound
Outbound
AI-generated
Staff-generated
System-generated

⸻

202. AI vs Human Attribution

Every outbound message should indicate internally whether it was:

AI
HUMAN
SYSTEM
HYBRID

⸻

203. Hybrid Messages

A staff member may edit AI-generated content before sending.

The message should be attributable as:

AI_ASSISTED_HUMAN_APPROVED

⸻

204. Human Approval

When required:

AI drafts
   |
   v
Staff reviews
   |
   +-- Approve
   +-- Edit
   +-- Reject

⸻

205. Rejection Analytics

Rejected AI messages should be logged for model-quality evaluation.

⸻

206. Staff Drafting

Staff should be able to:

* draft
* preview
* edit
* schedule
* send
* cancel

according to permissions.

⸻

207. Staff Signature

Clinic policies may require sender attribution.

Example:

Best regards,
Clinic Team

or:

Sara, Clinic Secretary

⸻

208. Brand Consistency

Communication should support clinic-level:

* name
* logo
* tone
* signature
* contact information
* language

⸻

209. Brand Safety

AI-generated communication must remain within configured clinic tone and brand constraints.

Brand preferences must never override medical safety.

⸻

210. Tone

Supported tones may include:

Professional
Warm
Concise
Friendly
Clinical
Formal

Tone should be configurable per communication category.

⸻

211. No Manipulative Communication

Clinicos must not generate messages using:

* guilt
* fear
* fake urgency
* fabricated scarcity
* fabricated social proof
* deceptive claims
* emotional pressure

⸻

212. Marketing Ethics

Marketing communication must be:

* truthful
* transparent
* consent-aware
* non-deceptive
* easy to opt out from

⸻

213. Price Communication

Prices must come from authoritative clinic configuration.

AI must not invent or infer current prices.

⸻

214. Discount Communication

Discounts must come from active authorized campaigns.

The AI must not fabricate discounts.

⸻

215. Availability Communication

Statements such as:

"Only two appointments left."

must be generated only from authoritative real-time data and only when such messaging is ethically and operationally permitted.

⸻

216. Scarcity Protection

Artificial scarcity must never be generated.

⸻

217. Notification Scheduling

Scheduled notifications should contain:

scheduled_at
timezone
expiration_at

⸻

218. Schedule Revalidation

Before scheduled delivery, the system should re-evaluate relevant dynamic conditions.

⸻

219. Example: Appointment Reminder

At scheduling time:

Appointment:
September 25, 17:00

At send time:

Appointment still active?
Confirmation still needed?
Patient still eligible for reminder?
Quiet hours?
Consent?
Human takeover?

Only then should the reminder be delivered.

⸻

220. Example: Marketing Campaign

At campaign creation:

Patient eligible

At delivery time:

Consent still valid?
Suppression active?
Frequency limit?
Channel still valid?
Campaign still active?

Only then should the message be sent.

⸻

221. Communication Expiration

Messages should expire when their underlying business context expires.

Examples:

Appointment reminder -> appointment start
Temporary offer -> campaign expiration
Verification code -> OTP expiration

⸻

222. Notification Batching

Low-priority notifications may be batched.

Examples:

3 internal low-priority alerts

may become:

You have 3 new clinic notifications.

Critical notifications must not be hidden inside a batch.

⸻

223. Digest Notifications

Staff may receive daily or weekly digests.

Digest generation must use actual system data.

⸻

224. Digest Safety

Critical events must not be delayed solely because a digest exists.

⸻

225. Staff Notification Prioritization

Staff notifications should prioritize:

1. Medical safety
2. Patient escalation
3. Appointment failures
4. High-value operational issues
5. Routine activity
6. Analytics

⸻

226. Patient Notification Prioritization

Patient communication should prioritize:

1. Safety
2. Appointment-critical information
3. Requested actions
4. Operational information
5. Routine follow-up
6. Marketing

⸻

227. Communication Kill Switch

Clinicos should support:

DISABLE_ALL_AUTOMATED_COMMUNICATION

while preserving authorized manual communication.

⸻

228. Channel Kill Switch

Individual channels should be disableable.

Example:

Telegram = disabled
SMS = enabled
Email = enabled

⸻

229. Tenant-Level Kill Switch

Each clinic should be able to pause automated communication for its own tenant.

⸻

230. System-Level Kill Switch

Platform administrators may disable a communication provider or communication category globally.

⸻

231. Disaster Recovery

Communication infrastructure must support recovery from:

* worker crashes
* queue failures
* provider outages
* database failures
* webhook loss
* duplicate events

⸻

232. Message Recovery

After worker restart, pending messages must be recoverable without duplication.

⸻

233. Queue Recovery

Queue processing should be durable.

Messages must not disappear silently after worker failure.

⸻

234. Provider Recovery

After provider recovery, queued messages must respect:

* expiration
* consent
* policy
* priority
* rate limits

⸻

235. Monitoring

Monitoring should cover:

queue_depth
send_latency
delivery_rate
failure_rate
retry_rate
provider_health
webhook_lag
blocked_messages
suppressed_messages

⸻

236. Alerting

Alerts should exist for:

* critical delivery failure
* provider outage
* abnormal failure rate
* queue buildup
* webhook outage
* repeated safety communication failures
* unusual spam behavior

⸻

237. Correlation IDs

Every communication workflow should carry:

request_id
correlation_id
tenant_id
communication_id

⸻

238. Distributed Tracing

A communication workflow may span:

Follow-Up Engine
    ->
Communication Service
    ->
Queue
    ->
Worker
    ->
Provider
    ->
Webhook

Tracing should connect these operations.

⸻

239. Security Testing

Test:

* tenant isolation
* endpoint authorization
* token replay
* webhook forgery
* unauthorized message sending
* sensitive-data leakage
* prompt injection
* malicious media
* malicious links

⸻

240. Consent Testing

Test:

marketing consent = true
marketing consent = false
marketing consent = unknown
consent revoked
channel-specific consent

⸻

241. Quiet-Hour Testing

Test:

* normal message during quiet hours
* urgent message during quiet hours
* scheduled message entering quiet hours
* quiet hours crossing midnight

⸻

242. Frequency Testing

Test:

* hourly limit
* daily limit
* campaign limit
* repeated automated messages
* multiple workflows targeting same patient

⸻

243. Deduplication Testing

Simulate:

same request
same event
same webhook
same worker retry
same provider response

Expected:

No unintended duplicate patient communication.

⸻

244. Provider Failure Testing

Simulate:

timeout
429
500
503
invalid response
network failure

Verify correct retry and failover behavior.

⸻

245. Delivery State Testing

Verify:

SENT
DELIVERED
READ
FAILED

remain semantically distinct.

⸻

246. Localization Testing

Test all supported languages:

Persian
English
Azerbaijani Turkish
Arabic
Turkish

including:

* RTL
* mixed-language text
* dates
* times
* numerals
* template variables

⸻

247. RTL Testing

Persian and Arabic communication must render correctly.

Mixed RTL/LTR content must be tested.

⸻

248. Media Testing

Test:

* image
* PDF
* document
* audio
* unsupported file
* oversized file
* expired URL

⸻

249. AI Communication Testing

Test:

* hallucinated appointment
* hallucinated price
* hallucinated discount
* hallucinated provider
* hallucinated delivery
* incorrect translation
* inappropriate tone
* privacy leakage
* policy bypass

⸻

250. Human Takeover Testing

Test:

AI automation active
       |
       v
Human takeover
       |
       v
Automated communication suppressed

⸻

251. Safety Testing

Test that:

Medical Safety BLOCK

prevents inappropriate automated communication.

⸻

252. Appointment Reconciliation Testing

Test:

Appointment booked
Reminder scheduled
Appointment cancelled
Reminder cancelled

and:

Appointment rescheduled
Old reminder cancelled
New reminder scheduled

⸻

253. End-to-End Communication Test

Example:

Patient books appointment
        |
        v
Appointment created
        |
        v
Follow-Up Engine schedules reminder
        |
        v
Communication request created
        |
        v
Policy validation
        |
        v
Channel selected
        |
        v
Message delivered
        |
        v
Delivery event received
        |
        v
Analytics updated

⸻

254. Performance Testing

Test:

* high-volume campaign
* appointment reminder burst
* provider outage recovery
* queue backlog
* multi-tenant load

⸻

255. Isolation Testing

One tenant’s communication spike must not prevent another tenant’s critical messages from being delivered.

⸻

256. Multi-Tenant Queue Strategy

Queues may be partitioned or fairly scheduled to prevent noisy-neighbor problems.

⸻

257. Fairness

Communication infrastructure should provide reasonable fairness across tenants.

Critical messages retain higher priority.

⸻

258. Cost Control

Provider routing may optimize cost.

However, cost optimization must not reduce:

* safety
* reliability
* consent compliance
* message correctness

⸻

259. Communication Cost Analytics

Track:

cost_per_message
cost_per_channel
cost_per_provider
cost_per_tenant
cost_per_campaign

where provider pricing data is available.

⸻

260. No Cost-Based Safety Degradation

The system must not route critical safety communication through an unreliable provider merely because it is cheaper.

⸻

261. Provider Selection

Provider selection may consider:

reliability
latency
cost
capacity
channel support
geographic support

with safety and correctness taking precedence.

⸻

262. Communication Service API

Conceptual API:

POST /communications
GET /communications/{id}
POST /communications/{id}/cancel
POST /communications/{id}/retry
GET /communications/{id}/status

Exact endpoints may evolve.

⸻

263. Send API

Conceptual request:

{
  "recipient_id": "patient_123",
  "intent": "APPOINTMENT_REMINDER",
  "channel": "telegram",
  "content": {
    "template_id": "appointment_reminder",
    "variables": {
      "appointment_time": "17:30"
    }
  },
  "idempotency_key": "appointment-123-reminder-24h"
}

⸻

264. API Validation

The API must validate:

* tenant
* recipient
* intent
* channel
* authorization
* consent
* content
* idempotency
* policy
* expiration

⸻

265. Communication Tool Boundary

AI agents should use controlled tools such as:

send_patient_message
send_staff_notification
get_delivery_status
cancel_scheduled_message

The AI must not access raw provider credentials.

⸻

266. AI Communication Authorization

AI communication permissions should be explicit.

Possible permissions:

CAN_SEND_TRANSACTIONAL
CAN_SEND_FOLLOWUP
CAN_SEND_MARKETING
CAN_SEND_SAFETY
CAN_SEND_INTERNAL

⸻

267. High-Risk AI Permissions

Marketing and safety communication should have separate permissions.

⸻

268. AI Prompt Context

AI message generation should receive only necessary context.

Example:

patient preferred language
appointment details
approved template
clinic tone
communication intent

Avoid unnecessary medical history.

⸻

269. Prompt Injection Defense

External content included in prompts must be clearly separated from system instructions.

⸻

270. Content Validation

Before delivery, validate:

* required variables
* prohibited phrases
* policy constraints
* safety constraints
* privacy constraints
* message length
* channel compatibility

⸻

271. Dynamic Data Validation

Dynamic variables must be validated against authoritative data before delivery.

⸻

272. Price Validation

If a message contains a price, the price must be sourced from the authoritative pricing system.

⸻

273. Appointment Validation

If a message contains appointment information, it must be sourced from the Appointment and Scheduling domain.

⸻

274. Provider Validation

If a message names a provider, the provider identity must come from authoritative clinic data.

⸻

275. Clinic Hours Validation

If a message contains clinic hours, they must come from current clinic configuration.

⸻

276. Communication Content Hash

The system may compute a content hash for:

* deduplication
* audit
* integrity verification

⸻

277. Message Immutability After Send

Once sent, the historical message representation should not be silently altered.

Corrections should be represented as new messages.

⸻

278. Message Editing

If a channel supports editing, edits must still be audited.

⸻

279. Deleted Messages

If a message is deleted on a provider platform, the internal audit should retain the fact that it existed and was deleted, subject to retention policy.

⸻

280. Communication History Integrity

Historical communication events should remain reconstructable even when provider APIs are no longer available.

⸻

281. Patient Conversation History

Conversation history should remain owned by the Conversation domain.

The Communication Layer stores delivery metadata and message transport state.

⸻

282. Separation of Concerns

The target boundary is:

Conversation:
"What is being discussed?"
Follow-Up:
"Should we contact the patient later?"
Communication:
"How do we deliver the approved communication?"
Channel Adapter:
"How does this provider accept the message?"

⸻

283. Operational Truth Boundary

The Communication Layer must retrieve dynamic truth from authoritative systems.

Examples:

Appointment -> Appointment Domain
Price -> Clinic/Pricing Domain
Patient identity -> Identity Domain
Medical safety -> Medical Safety Domain
Follow-up timing -> Follow-Up Engine

⸻

284. No Business Logic Duplication

Channel adapters must not implement:

appointment rules
marketing consent rules
follow-up timing
medical triage
lead scoring

⸻

285. Channel Adapter Simplicity

Adapters should focus on:

authentication
serialization
provider API calls
provider response parsing
webhook normalization
channel-specific constraints

⸻

286. Communication Orchestrator

The Communication Orchestrator coordinates:

Policy
Template
Localization
Channel
Provider
Retry
Delivery State

⸻

287. Communication Worker

Workers execute delivery jobs.

Workers must be:

* stateless where possible
* horizontally scalable
* idempotent
* observable

⸻

288. Worker Concurrency

Worker concurrency must respect provider limits.

⸻

289. Queue Ordering

Within a priority class, FIFO may be used where appropriate.

Critical safety messages should not be delayed by bulk traffic.

⸻

290. Transactional Outbox

Business domains should create communication requests through reliable transactional patterns.

Example:

Appointment Transaction
        |
        +-- Appointment Update
        |
        +-- Communication Event
        |
        v
Commit

⸻

291. Communication Event Processing

Events may be processed asynchronously.

Consumers must be idempotent.

⸻

292. Event Versioning

Communication events should have schema versions.

Example:

communication.sent.v1

⸻

293. Backward Compatibility

Event consumers should tolerate compatible schema evolution.

⸻

294. Dead-Letter Handling

Malformed or repeatedly failing communication events should enter a dead-letter workflow.

⸻

295. Human Review Queue

Some failed or blocked communications should enter a human review queue.

Examples:

unknown recipient
safety message failure
provider conflict
consent ambiguity
external synchronization conflict

⸻

296. Communication Dashboard

Staff dashboard may provide:

* communication history
* delivery status
* failed messages
* pending messages
* blocked messages
* retry controls
* channel health
* campaign overview
* patient preferences

⸻

297. Staff Retry

Staff may retry a failed message only if:

* the message remains valid
* consent remains valid
* policy permits
* recipient is valid

⸻

298. Staff Override

Staff may override selected communication blocks only with explicit permissions.

Every override must be audited.

⸻

299. Safety Override

Medical Safety may block automated communication.

Communication staff should not bypass this through ordinary retry actions.

⸻

300. Communication Governance

The system should maintain governance around:

* templates
* channels
* providers
* consent
* AI permissions
* retention
* audit
* safety

⸻

301. Versioned Communication Policies

Communication policies should be versioned.

Examples:

quiet_hours_policy_v3
marketing_policy_v5
reminder_policy_v2

⸻

302. Policy Evaluation Trace

For important communications, the system should record why a message was:

approved
blocked
suppressed
delayed

⸻

303. Example Approval Trace

Intent:
APPOINTMENT_REMINDER
Consent:
Not required
Patient:
Active
Appointment:
Confirmed
Quiet Hours:
No
Human Takeover:
No
Policy:
Allowed
Result:
APPROVED

⸻

304. Example Suppression Trace

Intent:
MARKETING
Consent:
Revoked
Result:
SUPPRESSED

⸻

305. Example Safety Block

Intent:
AUTOMATED_FOLLOWUP
Medical Safety:
HUMAN_REVIEW_REQUIRED
Result:
BLOCKED

⸻

306. Communication Reliability Contract

For every communication request, Clinicos must be able to answer:

Was it requested?
Was it approved?
Was it scheduled?
Was it attempted?
Was it accepted by the provider?
Was it delivered?
Was it read?
Did it fail?
Why?
Was it retried?
Was it suppressed?

⸻

307. Communication State Machine

Canonical lifecycle:

CREATED
   |
   v
PENDING_POLICY
   |
   +----> BLOCKED
   |
   v
APPROVED
   |
   +----> SCHEDULED
   |          |
   |          v
   |        READY
   |          |
   |          v
   +------> SENDING
              |
        +-----+------+
        |            |
        v            v
      SENT          FAILED
        |             |
        v             v
   DELIVERED    RETRY_SCHEDULED
        |
        v
      READ

⸻

308. Communication Invariants

The following invariants must always hold:

1. Communication must belong to exactly one tenant.
2. Every communication must have an explicit intent.
3. Authorization must be enforced server-side.
4. Consent must be evaluated where required.
5. AI must not bypass communication policy.
6. AI must not invent operational facts.
7. Scheduled communication must be revalidated before delivery.
8. Critical safety communication must have priority.
9. Marketing must never bypass consent.
10. Channel fallback must not bypass consent.
11. Delivery status must reflect actual provider evidence.
12. Sent, delivered, and read must remain distinct.
13. Messages must be idempotent.
14. Retries must be bounded.
15. Communication loops must be prevented.
16. Tenant isolation must always be enforced.
17. Sensitive information must be minimized.
18. Human takeover must suppress conflicting automation where configured.
19. Appointment communication must reconcile with appointment state.
20. Follow-up timing must remain owned by the Follow-Up Engine.
21. Channel adapters must not contain business-domain logic.
22. Provider credentials must never be exposed to AI.
23. Historical communication events must remain auditable.
24. Unknown delivery state must never be guessed.
25. Safety must override commercial optimization.

⸻

309. Canonical Notification Flow

BUSINESS EVENT
      |
      v
WORKFLOW / FOLLOW-UP ENGINE
      |
      v
COMMUNICATION REQUEST
      |
      v
POLICY VALIDATION
      |
      v
CONTENT SELECTION / GENERATION
      |
      v
SAFETY VALIDATION
      |
      v
PRIVACY VALIDATION
      |
      v
CONSENT VALIDATION
      |
      v
LOCALIZATION
      |
      v
CHANNEL SELECTION
      |
      v
FINAL PRE-SEND VALIDATION
      |
      v
QUEUE
      |
      v
COMMUNICATION WORKER
      |
      v
CHANNEL ADAPTER
      |
      v
PROVIDER
      |
      v
DELIVERY EVENT
      |
      v
COMMUNICATION STATE
      |
      v
ANALYTICS / AUDIT

⸻

310. Canonical Inbound Communication Flow

EXTERNAL CHANNEL
      |
      v
CHANNEL ADAPTER
      |
      v
WEBHOOK / POLLING
      |
      v
NORMALIZATION
      |
      v
AUTHENTICATION / VALIDATION
      |
      v
IDENTITY RESOLUTION
      |
      v
CONVERSATION ROUTING
      |
      v
DOMAIN / AI AGENT
      |
      v
ACTION OR RESPONSE

⸻

311. Canonical AI Message Flow

BUSINESS INTENT
      |
      v
STRUCTURED CONTEXT
      |
      v
APPROVED TEMPLATE OR AI GENERATION
      |
      v
CONTENT VALIDATION
      |
      v
POLICY VALIDATION
      |
      v
CHANNEL RENDERING
      |
      v
FINAL VALIDATION
      |
      v
SEND

⸻

312. Canonical Appointment Reminder Flow

Appointment Created
      |
      v
Follow-Up Engine
      |
      v
Reminder Scheduled
      |
      v
Appointment Changed?
      |
      +---- YES ---> Reconcile Reminder
      |
      +---- NO ----> Continue
                         |
                         v
                  Pre-Send Validation
                         |
                         v
                  Communication Layer
                         |
                         v
                       Send

⸻

313. Canonical Marketing Flow

Campaign
   |
   v
Eligible Audience
   |
   v
Consent Check
   |
   v
Frequency Check
   |
   v
Suppression Check
   |
   v
Channel Selection
   |
   v
Content Validation
   |
   v
Pre-Send Revalidation
   |
   v
Send

⸻

314. Canonical Safety Communication Flow

Medical Safety Event
      |
      v
Safety Policy
      |
      v
Communication Request
      |
      v
High Priority Queue
      |
      v
Approved Safety Content
      |
      v
Authorized Channel
      |
      v
Delivery
      |
      +---- Failure ----> Escalation

⸻

315. Canonical Failure Flow

Delivery Failure
      |
      v
Classify Error
      |
      +---- Non-Retryable ----> FAILED
      |
      +---- Retryable --------> RETRY
                                   |
                                   v
                              Revalidate
                                   |
                                   v
                                 Send
                                   |
                              +----+----+
                              |         |
                              v         v
                           SUCCESS    FAILURE
                                        |
                                        v
                                  Dead Letter /
                                  Human Review

⸻

316. Final Responsibility Matrix

Conversation AI
    -> Understands inbound intent.
Appointment Domain
    -> Owns appointment truth.
Follow-Up Engine
    -> Owns follow-up timing and workflow.
Medical Safety
    -> Owns safety decisions.
Consent / Privacy
    -> Owns communication authorization constraints.
Communication Layer
    -> Owns message delivery.
Channel Adapter
    -> Owns provider-specific transport.
Analytics
    -> Owns measurement and reporting.
Clinic Management
    -> Owns clinic-level communication configuration.

⸻

317. Final Architecture

                         CLINICOS
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
     Business Domains   Medical Safety    Clinic Config
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    Follow-Up / Workflow
                            |
                            v
                  Communication Request
                            |
                            v
                  Communication Policy
                            |
                            v
                    Message Composer
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          Template         AI          Staff
              |             |             |
              +-------------+-------------+
                            |
                            v
                   Content Validation
                            |
                            v
                   Channel Selection
                            |
                            v
                 Communication Queue
                            |
                            v
                Communication Workers
                            |
          +---------+-------+-------+---------+
          |         |       |       |         |
          v         v       v       v         v
       Telegram  WhatsApp  SMS    Email     Web
          |         |       |       |         |
          +---------+-------+-------+---------+
                            |
                            v
                    Provider Responses
                            |
                            v
                    Delivery Reconciliation
                            |
              +-------------+-------------+
              |                           |
              v                           v
           Analytics                    Audit

⸻

318. Final Design Philosophy

Clinicos must not treat communication as simply:

send(text)

Communication is a governed operational process:

Why should we communicate?
        |
        v
Are we allowed to?
        |
        v
What should be communicated?
        |
        v
Is the content correct?
        |
        v
Which channel is appropriate?
        |
        v
Is the message still valid?
        |
        v
Can it be delivered?
        |
        v
Was it actually delivered?
        |
        v
What happened afterward?

⸻

319. Final Safety Rule

The Communication Layer must prefer:

correct + authorized + verified

over:

fast + confident + unverified

A delayed message is often preferable to a wrong message.

A blocked message is preferable to an unauthorized message.

A human escalation is preferable to an unsafe automated message.

⸻

320. Final Operational Contract

The Communication Layer must guarantee:

No unauthorized communication.
No consent bypass.
No fabricated delivery status.
No fabricated operational facts.
No uncontrolled duplicate messages.
No infinite retries.
No silent communication loss.
No cross-tenant communication.
No AI access to raw provider credentials.
No unsafe medical messaging.
No marketing disguised as transactional communication.
No channel fallback that bypasses policy.
No automated communication that silently overrides human ownership.

⸻

321. Final Architecture Principle

The final Clinicos communication architecture is:

BUSINESS DOMAIN
      |
      v
DECIDE THAT COMMUNICATION IS NEEDED
      |
      v
FOLLOW-UP / WORKFLOW POLICY
      |
      v
COMMUNICATION POLICY
      |
      v
COMPOSE
      |
      v
VALIDATE
      |
      v
SELECT CHANNEL
      |
      v
DELIVER
      |
      v
RECONCILE
      |
      v
OBSERVE
      |
      v
AUDIT

The governing principle is:

Business domains decide WHY.
Policy decides WHETHER.
Content systems decide WHAT.
Communication decides HOW.
Channel adapters decide WHERE.
Providers report WHAT HAPPENED.
Audit records THE FACT.

This separation must remain intact as Clinicos evolves from a Telegram-first clinic assistant into a multi-channel AI-native clinic operating system.
