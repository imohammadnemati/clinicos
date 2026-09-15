# CLINICOS — PRODUCT UX SPECIFICATION
**Document:** `CLINICOS_PRODUCT_UX_SPEC.md`  
**Product:** Clinicos  
**Status:** Target Product UX / Authoritative UX Specification  
**Priority:** Critical  
**Scope:** Product Experience, User Experience, Information Architecture, Role-Based UX, Patient Experience, Staff Experience, Doctor Experience, Owner Experience, AI Interaction, Conversation UX, Workflow UX, Accessibility, Localization, Responsive Design, Notifications, Human Handoff, Error Handling, Trust and Safety  
**Audience:** Product Designers, UX Engineers, Frontend Engineers, Backend Engineers, AI Engineers, Product Managers, QA Engineers, Clinical Reviewers
---
# 1. PURPOSE
This document defines the target user experience architecture for Clinicos.
Clinicos is an AI-native operating system for aesthetic and cosmetic clinics.
The UX must make complex AI capabilities feel simple, predictable, trustworthy, and operationally useful.
The product must not expose unnecessary technical complexity to clinic staff.
Users should interact with clinic workflows rather than infrastructure.
The UX must support:
- Patients
- Secretaries
- Doctors
- Clinic owners
- Clinic managers
- AI agents
- Human reviewers
- Administrators
The experience must work across multiple communication channels while maintaining a unified patient and clinic context.
---
# 2. CORE UX PRINCIPLE
Clinicos should feel like:
```text
A smart clinic operating system

not:

A collection of AI tools

The user should not need to understand:

* Which LLM is being used
* Which provider generated a response
* Which agent executed a task
* Which queue processed an event
* Which model analyzed an image
* Which internal workflow triggered an action

Unless this information is explicitly useful for an authorized user.

⸻

3. PRIMARY UX OBJECTIVE

The primary UX objective is:

Reduce clinic operational workload while improving patient experience and conversion quality.

The product should minimize:

* Repetitive work
* Context switching
* Manual follow-up
* Message searching
* Appointment coordination
* Lead tracking
* Information duplication
* AI supervision overhead

⸻

4. SECONDARY UX OBJECTIVES

Clinicos should also:

* Improve response speed
* Improve consistency
* Improve patient communication
* Improve follow-up completion
* Improve lead visibility
* Improve appointment management
* Improve staff coordination
* Improve patient retention
* Improve clinic analytics
* Improve clinical communication
* Improve AI transparency

⸻

5. UX PRINCIPLES

Clinicos UX must follow these principles.

5.1 Simplicity

The interface should expose only the information needed for the current task.

5.2 Progressive Disclosure

Advanced information should be available when needed without overwhelming the primary workflow.

5.3 Context Preservation

Users should not repeatedly re-enter information that Clinicos already knows.

5.4 Action Orientation

Important screens should answer:

What happened?
Why does it matter?
What should I do next?

5.5 Trust

AI-generated information must never appear more certain than it actually is.

5.6 Human Control

Humans must be able to review, override, pause, or stop AI-driven workflows where appropriate.

5.7 Consistency

The same concept must look and behave consistently across the product.

5.8 Safety

Medical and privacy-sensitive actions must prioritize safety over convenience.

5.9 Accessibility

The system must remain usable by users with different abilities and levels of technical experience.

5.10 Localization

Localization must affect language, formatting, cultural conventions, time, date, number, currency, and communication style.

⸻

6. UX ARCHITECTURE

The target product experience can be represented as:

                    CLINICOS
                       |
        +--------------+--------------+
        |              |              |
     PATIENT         STAFF          DOCTOR
        |              |              |
        |        +-----+------+       |
        |        |            |       |
        |     SECRETARY      OWNER    |
        |        |            |       |
        +--------+------------+-------+
                         |
                    AI PLATFORM
                         |
        +----------------+----------------+
        |                |                |
   Conversations      Workflows        Insights
        |                |                |
      Leads         Appointments      Analytics
      Follow-up     Notifications     Reports
      Support       Automation        AI

⸻

7. USER ROLES

Clinicos must support role-specific experiences.

Primary roles:

patient
secretary
doctor
owner
manager
platform_admin

Additional specialized roles may be introduced later.

⸻

8. PATIENT UX

The patient experience should prioritize:

* Simplicity
* Speed
* Trust
* Clarity
* Privacy
* Human access
* Low cognitive load

The patient should not need to understand Clinicos.

They should simply communicate with the clinic.

⸻

9. SECRETARY UX

The secretary experience should prioritize:

* Inbox management
* Lead management
* Appointment management
* Follow-up management
* Patient context
* AI assistance
* Human takeover
* Task prioritization

The secretary should be able to understand the operational state of the clinic quickly.

⸻

10. DOCTOR UX

The doctor experience should prioritize:

* Clinical context
* Patient summary
* Relevant conversation history
* AI-generated summaries
* Facial analysis results
* Treatment-related context
* Human verification
* Clinical review
* Minimal administrative burden

Doctors should not be forced through workflows designed for secretaries.

⸻

11. OWNER UX

The owner or manager experience should prioritize:

* Clinic performance
* Lead conversion
* Revenue-related metrics
* Staff workload
* Appointment performance
* Follow-up performance
* AI performance
* Operational bottlenecks
* Alerts
* Reports

Owner UX should focus on decisions rather than raw operational details.

⸻

12. PLATFORM ADMIN UX

Platform administrators may need:

* Tenant management
* System health
* AI provider status
* Model configuration
* Policy management
* Security monitoring
* Audit logs
* Usage monitoring
* Feature flags
* System-level analytics

Platform administrators must not automatically gain access to patient data without appropriate authorization.

⸻

13. ROLE-BASED NAVIGATION

Navigation should be role-aware.

A secretary should not see the same primary navigation as a doctor.

Example secretary navigation:

Inbox
Leads
Patients
Appointments
Follow-ups
Tasks
Knowledge
Reports

Example doctor navigation:

Today
Patients
Appointments
Clinical Review
AI Insights
Facial Analysis
Reports

Example owner navigation:

Dashboard
Leads
Appointments
Patients
Team
Analytics
Reports
Automation
Settings

⸻

14. INFORMATION ARCHITECTURE

The core information architecture should revolve around:

Clinic
 ├── Patients
 ├── Conversations
 ├── Leads
 ├── Appointments
 ├── Follow-ups
 ├── Tasks
 ├── Services
 ├── Knowledge
 ├── Automations
 ├── Analytics
 ├── Reports
 └── Settings

⸻

15. PATIENT-CENTERED MODEL

The patient should be treated as a central entity.

A patient may have:

Identity
Consent
Profile
Conversations
Leads
Appointments
Follow-ups
Images
Facial Analyses
AI Interactions
Notes
Preferences
Activity

The UX should allow authorized users to navigate between these contexts without losing the patient identity.

⸻

16. PATIENT 360 VIEW

The Patient 360 view should provide a unified overview.

Possible structure:

Patient Header
    |
    +-- Basic Information
    +-- Current Status
    +-- Next Appointment
    +-- Active Lead
    +-- Follow-up Status
    +-- Recent Conversation
    +-- Clinical Context
    +-- Facial Analysis
    +-- Activity Timeline

⸻

17. PATIENT HEADER

The patient header should show only high-value information.

Potential fields:

Name
Primary Contact
Patient Status
Lead Status
Next Appointment
Assigned Staff
Important Flags
Consent Status

Sensitive information must only be displayed to authorized roles.

⸻

18. PATIENT TIMELINE

The patient timeline should unify important events.

Examples:

Patient created
Message received
Lead created
Lead qualified
Appointment booked
Appointment rescheduled
AI analysis completed
Follow-up sent
Patient replied
Appointment completed

The timeline should distinguish:

human action
AI action
system action
patient action

⸻

19. TIMELINE UX

Timeline entries should be:

* Chronological
* Filterable
* Searchable where appropriate
* Role-aware
* Auditable

Users should be able to open an event for more detail.

⸻

20. CONVERSATION UX

Conversation is one of the primary interaction surfaces of Clinicos.

The conversation interface should support:

* Incoming messages
* Outgoing messages
* AI-generated drafts
* AI-sent messages
* Human messages
* Attachments
* Images
* Voice messages
* Structured actions
* Lead context
* Appointment context
* Follow-up context
* Human takeover

⸻

21. UNIFIED CONVERSATION MODEL

Different channels should map to a common conversation model.

Potential channels:

Telegram
Instagram
Web
WhatsApp
SMS
Future channels

The UX should avoid forcing staff to learn a different workflow for every channel.

⸻

22. CHANNEL INDICATORS

The system may display the channel used for a conversation.

Example:

Telegram
Instagram
Web

Channel indicators should be visually subtle.

The conversation content remains the primary focus.

⸻

23. AI MESSAGE DRAFT

When AI proposes a response but does not automatically send it, the UI should clearly identify it as a draft.

Example:

AI Draft
"I can help you with available appointment times.
Would you prefer morning or afternoon?"

Actions:

Send
Edit
Regenerate
Reject
Take Over

⸻

24. AI-SENT MESSAGE

If AI is authorized to send a message automatically, the internal staff interface should make this visible.

Example:

AI sent

This improves operational transparency.

The patient-facing experience should follow the clinic’s configured communication policy.

⸻

25. AI TRANSPARENCY

Staff should be able to determine:

* Whether AI generated a response
* Whether a human edited it
* Whether a human approved it
* Whether an automation sent it
* Whether the message triggered a workflow

The UI should not expose unnecessary technical model details by default.

⸻

26. HUMAN TAKEOVER

Human takeover must be a first-class UX feature.

Example:

[Take over conversation]

When activated:

AI automation paused

The interface should clearly indicate the state.

⸻

27. AI PAUSE STATES

Possible conversation states:

AI_ACTIVE
AI_DRAFTING
HUMAN_REVIEW
HUMAN_ACTIVE
AI_PAUSED
CLOSED

⸻

28. RESUMING AI

When human control ends, the user should be able to resume AI.

Example:

Resume AI assistance

The system should not silently resume AI after a human takeover unless explicitly configured and permitted.

⸻

29. LEAD UX

Lead management should focus on:

Who is this?
What do they want?
How valuable is the opportunity?
What happened?
What should happen next?

⸻

30. LEAD CARD

A lead card may show:

Patient
Intent
Service
Lead Score
Lead Status
Last Contact
Next Follow-up
Assigned Staff
Response Status

⸻

31. LEAD STATUS

Example states:

new
contacted
qualified
hot
warm
cold
appointment_pending
booked
converted
lost

The exact lifecycle should be configurable.

⸻

32. LEAD SCORE

Lead score should be visually understandable.

Example:

High intent

rather than exposing an unexplained numeric score as the primary UI.

The numeric score may be available in detail views.

⸻

33. LEAD EXPLANATION

If AI contributes to lead scoring, staff should be able to see an explanation.

Example:

Why this lead is high priority:
- Asked about treatment pricing
- Requested available appointment times
- Replied within 10 minutes

The explanation must reflect actual evidence.

⸻

34. FOLLOW-UP UX

Follow-up should be represented as an operational task rather than an abstract AI feature.

Example:

Follow up with Sara
Reason:
No response after consultation inquiry
Due:
Today, 16:00
Suggested action:
Send follow-up message

⸻

35. FOLLOW-UP PRIORITY

Follow-ups may be prioritized by:

Urgency
Lead value
Patient preference
Appointment proximity
Workflow policy
Risk

⸻

36. FOLLOW-UP ACTIONS

Staff may:

Send
Edit
Reschedule
Skip
Cancel
Mark complete
Assign
Take over

⸻

37. APPOINTMENT UX

Appointment UX must be operationally authoritative.

The UI must not display availability based on AI memory.

Availability must come from the authoritative appointment or scheduling system.

⸻

38. APPOINTMENT CREATION

The appointment workflow should minimize steps.

Potential flow:

Select Patient
    ↓
Select Service
    ↓
Select Provider
    ↓
Select Available Time
    ↓
Confirm

⸻

39. APPOINTMENT CONFIRMATION

After confirmation:

Appointment confirmed

The system may trigger:

Confirmation message
Reminder workflow
Calendar event
Staff notification

⸻

40. APPOINTMENT RESCHEDULING

Rescheduling should preserve history.

The system should show:

Previous time
New time
Reason if provided
Who changed it
When it changed

⸻

41. APPOINTMENT REMINDERS

The system should support configurable reminder policies.

Example:

24 hours before
2 hours before

The actual schedule should be configurable by clinic policy.

⸻

42. NO-SHOW UX

After a no-show event, the system may surface:

No-show detected

Possible actions:

Contact patient
Reschedule
Create follow-up
Mark resolved

⸻

43. DASHBOARD UX

The dashboard should be role-specific.

A dashboard should not simply display every metric.

It should answer:

What requires my attention?

⸻

44. SECRETARY DASHBOARD

Potential sections:

Today's Tasks
Unread Conversations
Hot Leads
Upcoming Appointments
Overdue Follow-ups
AI Escalations
Operational Alerts

⸻

45. DOCTOR DASHBOARD

Potential sections:

Today's Appointments
Patients Requiring Review
Clinical AI Alerts
Facial Analysis Reviews
Patient Notes
Follow-up Cases

⸻

46. OWNER DASHBOARD

Potential sections:

Today's Activity
Lead Funnel
Conversion Rate
Appointment Performance
Follow-up Performance
Staff Workload
Revenue Indicators
Patient Retention
AI Performance

⸻

47. DASHBOARD PRIORITIZATION

Dashboard items should be ordered by operational importance.

Recommended priority:

Critical
High
Actionable
Informational
Historical

⸻

48. TASK CENTER

Clinicos should provide a unified task center.

Tasks may originate from:

Lead
Follow-up
Appointment
AI escalation
Patient request
Human review
Workflow
System alert

⸻

49. TASK CARD

A task should contain:

Task title
Patient
Reason
Priority
Due time
Assigned user
Source
Recommended action
Status

⸻

50. AI ACTIONS

AI-generated recommended actions should be visually distinguished from mandatory actions.

Example:

Recommended by AI

versus:

Required by clinic policy

⸻

51. AI RECOMMENDATION UX

AI recommendations should provide:

Recommendation
Reason
Evidence
Confidence where meaningful
Available actions

Avoid presenting opaque recommendations without context.

⸻

52. AI SUMMARY UX

AI summaries should be concise by default.

Example:

Patient Summary
Interested in hair treatment.
Asked about price and availability.
Requested an appointment next week.
No appointment booked yet.

The user should be able to expand for more detail.

⸻

53. AI SUMMARY SOURCE

Important AI summaries should allow users to inspect supporting source information where appropriate.

Possible source types:

Conversation
Appointment
Patient record
Uploaded image
Clinic knowledge

⸻

54. KNOWLEDGE UX

Clinic knowledge should be accessible through:

Knowledge
FAQs
Services
Policies
Templates
Clinical information
Operational rules

⸻

55. KNOWLEDGE EDITING

Authorized staff should be able to:

Create
Edit
Publish
Archive
Review
Version

Knowledge changes should be auditable.

⸻

56. KNOWLEDGE STATUS

Possible states:

draft
review
published
archived

⸻

57. SERVICE UX

Each clinic service should have structured information.

Potential fields:

Service Name
Description
Category
Duration
Provider
Price
Preparation
Aftercare
Eligibility
FAQ
Booking Rules

Dynamic operational fields must come from authoritative clinic configuration.

⸻

58. PRICE DISPLAY

Prices must not be invented by AI.

If price is available:

Show authoritative clinic price.

If price is unavailable:

Tell the user that the clinic needs to confirm it.

Never fabricate a price.

⸻

59. AI AND OPERATIONAL TRUTH

AI may explain operational information.

AI must not become the source of operational truth.

Examples of authoritative information:

Appointment availability
Current clinic price
Provider schedule
Clinic opening hours
Appointment status
Payment status

⸻

60. FACIAL ANALYSIS UX

Facial Analysis should be presented as a guided workflow.

Recommended flow:

Introduction
    ↓
Consent
    ↓
Capture / Upload
    ↓
Image Quality Check
    ↓
Analysis
    ↓
Results
    ↓
Optional Clinical Review

⸻

61. FACIAL ANALYSIS INTRODUCTION

The patient should understand:

* What the analysis does
* What it does not do
* Why an image is required
* How the image is handled
* Whether results are AI-generated
* Whether a clinician reviews the result

⸻

62. IMAGE CAPTURE UX

The capture interface should provide simple guidance.

Examples:

Use even lighting.
Keep your face centered.
Remove sunglasses.
Keep your face relaxed.
Avoid beauty filters.

The system should avoid overwhelming the user.

⸻

63. IMAGE QUALITY FEEDBACK

Quality errors should be actionable.

Bad:

Image rejected.

Better:

Your face is too dark to analyze reliably.
Please move to brighter, even lighting and try again.

⸻

64. FACIAL ANALYSIS RESULTS

Results should distinguish:

Visible observations
AI interpretation
Recommendations
Clinical review

These should never be visually conflated.

⸻

65. RESULT CONFIDENCE

The system may display qualitative confidence:

High confidence
Moderate confidence
Limited confidence
Unable to determine

Patient-facing confidence language must be carefully designed.

⸻

66. FACIAL ANALYSIS DISCLAIMERS

Disclaimers should be contextual rather than excessively intrusive.

Example:

This analysis is AI-assisted and is not a medical diagnosis.
A qualified clinician should make clinical decisions.

⸻

67. BEFORE-AND-AFTER UX

Before-and-after comparison should support:

Before
After
Date
Capture conditions
Analysis version

The UI should warn when comparison conditions are significantly different.

⸻

68. REPORT UX

Reports should have role-specific versions.

Patient report:

Simple
Readable
Educational
Non-diagnostic

Clinician report:

Detailed
Structured
Evidence-oriented
Auditable

Owner report:

Operational
Aggregated
Performance-oriented

⸻

69. NOTIFICATION UX

Notifications should be:

* Relevant
* Actionable
* Prioritized
* Non-spammy
* Respectful of preferences

⸻

70. NOTIFICATION PRIORITY

Possible levels:

critical
high
normal
low

⸻

71. NOTIFICATION GROUPING

Related notifications should be grouped.

Example:

3 follow-ups require attention

instead of:

Notification 1
Notification 2
Notification 3

⸻

72. QUIET HOURS

Patient and staff notification preferences should support quiet hours where applicable.

Critical safety or operational notifications may follow different policies.

⸻

73. CHANNEL PREFERENCE

The system should respect configured channel preferences.

Potential channels:

Telegram
Instagram
SMS
Email
Push
In-app

⸻

74. COMMUNICATION CONSENT

The system must distinguish:

communication consent
marketing consent
facial analysis consent
data processing consent

These must not be treated as interchangeable.

⸻

75. ACCESSIBILITY

The product should follow modern accessibility principles.

The system should support:

* Keyboard navigation
* Screen readers
* Sufficient contrast
* Clear focus states
* Semantic structure
* Accessible labels
* Alternative text where appropriate
* Reduced motion preferences
* Resizable text
* Touch-friendly controls

⸻

76. RESPONSIVE UX

The web interface must support:

Mobile
Tablet
Desktop
Large desktop

The primary workflow should remain usable on small screens.

⸻

77. MOBILE-FIRST PRINCIPLE

Patient-facing and urgent staff workflows should prioritize mobile usability.

Important actions should remain accessible without requiring desktop-only interactions.

⸻

78. INFORMATION DENSITY

Different roles require different information density.

Secretary:

High operational density

Doctor:

High clinical relevance

Owner:

High analytical density

Patient:

Low cognitive density

⸻

79. SEARCH UX

Global search should support authorized users in finding:

Patients
Leads
Appointments
Conversations
Tasks
Reports
Knowledge

Search results must respect permissions.

⸻

80. FILTERING

Major list views should support filters.

Examples:

Status
Date
Assigned user
Priority
Channel
Service
Provider
Lead score
Appointment state

⸻

81. SORTING

Lists should support useful sorting.

Examples:

Newest
Oldest
Highest priority
Soonest due
Recently updated

⸻

82. EMPTY STATES

Empty states should explain what the user can do next.

Bad:

No data.

Better:

No follow-ups are due today.
When a follow-up becomes due, it will appear here.

⸻

83. LOADING STATES

Loading states should communicate progress when operations take time.

Examples:

Analyzing image...
Loading patient context...
Checking appointment availability...
Generating draft...

Avoid indefinite spinners without context.

⸻

84. LONG-RUNNING OPERATIONS

For operations such as:

Facial analysis
Large report generation
Bulk imports
Large exports

the system should use asynchronous progress states.

Example:

Processing
25%

where meaningful progress can be measured.

⸻

85. ERROR UX

Errors must be:

* Understandable
* Actionable
* Non-technical where possible
* Honest
* Recoverable

Bad:

ProviderRouterException: 503

Better:

The analysis could not be completed right now.
Please try again.

Internal logs may retain technical details.

⸻

86. ERROR CLASSIFICATION

Errors should be categorized internally:

validation_error
permission_error
authentication_error
rate_limit_error
network_error
provider_error
data_error
safety_error
consent_error
timeout
system_error

⸻

87. RETRY UX

The UI should offer retry when retry is safe.

Example:

Try again

The system should avoid creating duplicate operations when a user retries.

⸻

88. UNSAFE ACTION UX

When an action is blocked by safety policy, the UI should explain the reason at an appropriate level.

Example:

This request requires review by a qualified clinician.

Do not expose internal safety mechanisms unnecessarily.

⸻

89. HUMAN ESCALATION UX

When AI cannot safely proceed:

Human review required

The system should create a clear task.

The task should include:

Reason
Patient
Conversation
Relevant evidence
Suggested next step
Urgency

⸻

90. ESCALATION PRIORITY

Potential priorities:

critical
urgent
high
normal
low

⸻

91. AI CONFIDENCE UX

Confidence should only be shown when it is meaningful and correctly interpreted.

Avoid:

AI confidence: 97%

when users may interpret this as medical certainty.

Prefer contextual language where appropriate:

High model confidence, but clinical review is still required.

⸻

92. TRUST INDICATORS

The system may use trust indicators such as:

Verified clinic information
AI-generated
Human reviewed
System confirmed
Pending confirmation

These labels must be consistent throughout the product.

⸻

93. AUDIT UX

Authorized users should be able to inspect important actions.

Example:

Appointment changed by Secretary
AI draft edited by Doctor
Automation sent reminder
Lead score updated
Facial analysis completed

⸻

94. ACTIVITY HISTORY

Activity history should include:

Who
What
When
Source
Result

For AI actions:

AI agent
Workflow
Model execution reference

may be recorded internally.

⸻

95. SETTINGS UX

Settings should be organized by responsibility.

Example:

Clinic
Team
Services
Appointments
Notifications
AI
Automations
Channels
Knowledge
Privacy
Security
Billing
Integrations

⸻

96. AUTOMATION BUILDER UX

Authorized users may eventually configure workflows visually.

Conceptual builder:

Trigger
   ↓
Condition
   ↓
Action
   ↓
Wait
   ↓
Condition
   ↓
Action

Example:

Lead becomes hot
      ↓
Wait 10 minutes
      ↓
Check whether patient replied
      ↓
If no reply
      ↓
Send follow-up

⸻

97. AUTOMATION SAFETY

The workflow builder must prevent invalid workflows.

Examples:

* Infinite loops
* Missing terminal state
* Invalid permissions
* Unsafe actions
* Unavailable tools
* Invalid time conditions
* Conflicting actions

⸻

98. AUTOMATION PREVIEW

Before activation, users should be able to inspect:

Trigger
Conditions
Actions
Delays
Branches
Potential notifications
Potential AI calls

⸻

99. AUTOMATION DRY RUN

Where possible, workflows should support dry-run mode.

Dry-run should show:

What would have happened

without executing external side effects.

⸻

100. WORKFLOW VERSIONING

Published workflows must be versioned.

Example:

Lead Follow-up v1
Lead Follow-up v2

Existing workflow instances should continue according to their assigned version unless explicitly migrated.

⸻

101. WORKFLOW PAUSING

Authorized users should be able to pause an automation.

Pause should not silently delete existing workflow state.

The UI should show:

Automation paused

⸻

102. WORKFLOW ACTIVATION

Activation should require validation.

The system should check:

* Permissions
* Required configuration
* Trigger validity
* Action availability
* Safety policies
* Channel availability
* Knowledge dependencies

⸻

103. WORKFLOW HISTORY

Users should be able to inspect:

Runs
Successes
Failures
Skipped runs
Cancelled runs
Human escalations

⸻

104. WORKFLOW DEBUGGING

Authorized technical users should be able to inspect:

Trigger event
Conditions evaluated
Actions executed
Errors
Retries
Timing
Workflow version

⸻

105. PATIENT-FACING UX

Patient-facing UX must avoid internal terminology.

Do not expose:

workflow instance
agent orchestration
event router
provider score
RAG
tool call
LLM

Use natural language.

⸻

106. STAFF-FACING UX

Staff-facing UX may expose operational concepts.

Examples:

AI Draft
Automation
Follow-up
Human Review
AI Escalation

⸻

107. OWNER-FACING UX

Owner-facing UX should expose business outcomes.

Examples:

Lead conversion improved
Response time decreased
Follow-ups completed
Appointments booked

⸻

108. CLINICAL UX BOUNDARY

Clinicos must clearly separate:

Administrative workflow

from:

Clinical decision support

Clinical decisions must remain under appropriate human responsibility unless a separately validated workflow explicitly permits otherwise.

⸻

109. MEDICAL SAFETY UX

When a user asks for potentially dangerous or clinically sensitive guidance, the product must follow the Medical Safety Specification.

The UX must support:

Refusal
Safe alternative
Human escalation
Urgent escalation

when required.

⸻

110. EMERGENCY UX

If a conversation contains potential emergency indicators, the UX must prioritize immediate human attention.

The system should not bury urgent alerts under ordinary lead or marketing tasks.

⸻

111. PRIVACY UX

Users should understand when personal data is being collected or analyzed.

Sensitive workflows should provide appropriate notices.

Examples:

Facial image analysis
Medical information
Contact information
Communication history

⸻

112. DATA RETENTION UX

Where appropriate, authorized users should be able to understand retention policies.

Patients should have appropriate privacy controls according to applicable policy and law.

⸻

113. DELETE UX

Deletion actions should be explicit.

For sensitive data:

Delete

should not be a one-click accidental operation.

Critical destructive actions should require confirmation.

⸻

114. CONFIRMATION DIALOGS

Confirmation should be used for:

* Deleting sensitive data
* Cancelling appointments
* Publishing major automation changes
* Sending potentially consequential communications
* Revoking consent
* Destructive configuration changes

Do not overuse confirmations for routine actions.

⸻

115. UNDO

Where safe and technically possible, provide undo.

Examples:

Archive lead
Undo

However, irreversible external actions such as already-sent messages cannot always be undone.

⸻

116. TOASTS AND FEEDBACK

Transient feedback should be concise.

Example:

Follow-up scheduled.

Errors should remain visible long enough for users to understand them.

⸻

117. BULK ACTIONS

Authorized staff should be able to perform bulk actions where operationally useful.

Examples:

Assign leads
Schedule follow-ups
Archive conversations
Export reports

Bulk actions require strong confirmation and permission checks.

⸻

118. BULK AI ACTIONS

Bulk AI actions require additional safeguards.

Examples:

Generate follow-ups for 100 leads

should provide:

Number of affected patients
Estimated messages
Estimated AI usage
Potential external side effects

before execution.

⸻

119. COST-AWARE UX

Where AI operations consume meaningful resources, authorized users may see estimated usage.

Example:

This operation will analyze 250 images.

Exact financial information should only be shown if reliable cost data exists.

⸻

120. AI MODEL VISIBILITY

The default UX should not require users to choose an AI model.

Model selection is an infrastructure concern.

Advanced administrators may be allowed to configure model policies.

⸻

121. MULTILINGUAL UX

Clinicos should support multilingual experiences.

Target languages include:

Persian
English
Azerbaijani Turkish
Arabic
Turkish

The localization system must be extensible.

⸻

122. LANGUAGE PREFERENCE

Language may be configured at:

Patient level
User level
Clinic level
Conversation level

The most specific valid preference should normally take precedence.

⸻

123. LANGUAGE DETECTION

AI may detect language automatically.

However, explicit user preference should override automatic detection.

⸻

124. RTL SUPPORT

Persian and Arabic interfaces must support right-to-left layouts.

The system must support mixed-direction content correctly.

Examples:

Persian UI
English medical terms
Numbers
Dates
Phone numbers
URLs

must remain readable.

⸻

125. DATE AND TIME

Date and time display should respect the configured locale and timezone.

The system must distinguish:

storage timezone
clinic timezone
user timezone
patient timezone

⸻

126. CALENDAR SYSTEMS

The UI may support multiple calendar representations where required.

For example:

Gregorian
Persian

Calendar conversion must be deterministic and tested.

⸻

127. NUMBER FORMATTING

Numbers should respect locale.

Examples include:

Decimal separators
Thousands separators
Currency
Phone numbers
Dates

⸻

128. CURRENCY

Currency display must come from clinic configuration.

The UI must not infer currency from language alone.

⸻

129. CULTURAL LOCALIZATION

Localization must not be limited to translation.

It should consider:

* Communication tone
* Date conventions
* Time conventions
* Honorifics
* Name ordering
* Local communication expectations

⸻

130. NOTIFICATION LANGUAGE

Patient notifications should use the patient’s preferred language when available.

Fallback order should be configurable.

⸻

131. MESSAGE TEMPLATES

Templates should support:

Static content
Variables
Conditional sections
Localization
Clinic branding
Approval state
Versioning

⸻

132. TEMPLATE VARIABLES

Example:

{{patient.first_name}}
{{appointment.date}}
{{appointment.time}}
{{clinic.name}}
{{service.name}}

Variables must be validated before sending.

⸻

133. MISSING VARIABLES

If required data is missing, the message should not be sent with broken placeholders.

Bad:

Hello {{patient.first_name}}

The system must either:

* Resolve the variable
* Use a safe fallback
* Block the message

⸻

134. BRANDING

Clinic branding may include:

Clinic name
Logo
Color system
Typography
Contact information

Branding must not compromise accessibility or readability.

⸻

135. DESIGN SYSTEM

Clinicos should maintain a centralized design system.

The design system should define:

Colors
Typography
Spacing
Buttons
Inputs
Cards
Tables
Dialogs
Navigation
Status indicators
Icons
Forms
Charts
Notifications

⸻

136. DESIGN TOKENS

Design tokens should be used instead of hard-coded UI values.

Example categories:

color.*
spacing.*
radius.*
typography.*
shadow.*
breakpoint.*
motion.*

⸻

137. STATUS SYSTEM

Status colors and labels must be standardized.

Examples:

success
warning
error
info
neutral
pending

Color must never be the only signal.

⸻

138. ICONOGRAPHY

Icons should support comprehension but not replace essential text.

Critical actions should have accessible labels.

⸻

139. MOTION

Motion should be purposeful.

Use animation for:

* State transitions
* Loading
* Confirmation
* Navigation context

Avoid unnecessary motion.

Respect reduced-motion preferences.

⸻

140. FORMS

Forms should:

* Minimize required fields
* Validate early
* Preserve user input
* Explain errors
* Support keyboard navigation
* Avoid unnecessary steps

⸻

141. FORM VALIDATION

Validation should distinguish:

Missing
Invalid
Unavailable
Conflicting
Unauthorized

⸻

142. AUTOSAVE

Autosave may be used for long forms where safe.

The UI should communicate save state.

Example:

Saved
Saving...
Unsaved changes

⸻

143. DRAFT STATES

Important content should support drafts.

Examples:

Knowledge article
Automation
Message template
Report
Clinic configuration

⸻

144. UNSAVED CHANGES

When leaving a screen with unsaved changes, the UI should warn the user.

⸻

145. TABLE UX

Tables should support:

* Sorting
* Filtering
* Pagination
* Search
* Column customization where useful
* Responsive behavior

⸻

146. MOBILE TABLES

On mobile, tables should transform into cards or horizontally scroll only when necessary.

Critical information must remain visible.

⸻

147. ANALYTICS UX

Analytics should prioritize trends and decisions.

Avoid displaying large numbers of meaningless charts.

Each chart should answer a question.

Example:

Are leads converting faster this month?

⸻

148. CHART ACCESSIBILITY

Charts should have:

* Labels
* Text summaries
* Accessible descriptions
* Tooltips
* Non-color-dependent interpretation

⸻

149. REPORT UX

Reports should support:

View
Filter
Export
Share
Schedule
Archive

Permissions must apply to all report actions.

⸻

150. EXPORT UX

Exports should clearly indicate:

Data scope
Date range
Filters
Format
Requester

Sensitive exports may require additional confirmation.

⸻

151. SEARCH RESULT TRUST

Search results must distinguish between:

Exact match
Relevant match
AI-assisted match

AI-assisted search must not silently fabricate records.

⸻

152. AI SEARCH

If AI search is used, it should retrieve from authoritative data sources.

The AI layer should not invent records that do not exist.

⸻

153. PATIENT MATCHING

When identifying a patient from a conversation, the system should use reliable identity signals.

Ambiguous matches should require confirmation.

Never silently merge two patients based solely on weak similarity.

⸻

154. DUPLICATE PATIENT UX

When potential duplicates are detected:

Possible duplicate patient

The user should be able to:

Review
Merge
Keep separate
Dismiss

⸻

155. MERGE SAFETY

Patient merging is a high-impact action.

The UI should show:

Records being merged
Conflicting fields
Data that will be retained
Data that may be discarded

⸻

156. PERMISSION UX

The interface should hide actions users cannot perform where appropriate.

If an action is visible but unavailable, explain why.

⸻

157. ROLE PERMISSIONS

Permissions should be capability-based rather than relying only on broad role names.

Example:

patient.read
patient.edit
patient.delete
appointment.create
appointment.cancel
automation.publish
ai.review
facial_analysis.view

⸻

158. TENANT ISOLATION UX

Users must never see data belonging to another clinic.

Tenant context should be implicit but enforced at every backend layer.

⸻

159. CLINIC SWITCHING

Users with access to multiple clinics may have a clinic selector.

The current clinic context must always be visible.

⸻

160. CROSS-CLINIC DATA

Cross-clinic views should only exist when explicitly authorized.

Patient data must not leak between tenants.

⸻

161. ONBOARDING

New clinic onboarding should be progressive.

Recommended flow:

Create clinic
    ↓
Configure identity
    ↓
Add staff
    ↓
Add services
    ↓
Configure appointments
    ↓
Connect channels
    ↓
Add knowledge
    ↓
Configure AI
    ↓
Activate automations

⸻

162. ONBOARDING PRINCIPLE

Do not require the clinic to configure everything before seeing value.

The user should reach a meaningful first success quickly.

⸻

163. FIRST VALUE

Potential first-value moment:

Connect a communication channel
    ↓
Receive first patient message
    ↓
Clinicos identifies the conversation
    ↓
Creates or matches patient
    ↓
Creates lead
    ↓
Provides AI assistance

⸻

164. SETUP CHECKLIST

The dashboard may display:

Clinic profile
Staff
Services
Appointments
Communication channel
Knowledge
AI settings
Automation

with progress indicators.

⸻

165. AI ONBOARDING

AI onboarding should explain:

What AI can do
What AI cannot do
When humans are involved
How clinic knowledge is used
How data is handled

⸻

166. AUTOMATION ONBOARDING

Automation onboarding should provide safe templates.

Examples:

New Lead Follow-up
Appointment Reminder
No-show Follow-up
Post-Visit Follow-up

Templates should be reviewed and configurable before activation.

⸻

167. EMPTY CLINIC EXPERIENCE

A new clinic should not appear broken because it has no data.

Instead show:

Your clinic is ready.
Complete setup to start receiving and managing patient conversations.

⸻

168. HELP SYSTEM

Clinicos should provide contextual help.

Help may appear as:

Tooltips
Inline explanations
Guides
Documentation
Examples

⸻

169. AI ASSISTED HELP

AI may answer product usage questions.

It must use current product documentation and configuration where necessary.

It must not invent unavailable features.

⸻

170. USER FEEDBACK

Users should be able to report:

Bug
Wrong AI response
Wrong patient match
Incorrect automation
Poor analysis
Feature request

⸻

171. AI FEEDBACK

For AI-generated outputs, provide lightweight feedback mechanisms.

Examples:

Helpful
Not helpful
Wrong
Needs review

This feedback should feed evaluation systems where appropriate.

⸻

172. FACIAL ANALYSIS FEEDBACK

Users may report:

Analysis inaccurate
Image quality problem
Finding incorrect
Result unclear

Feedback should be linked to:

image_id
analysis_id
model_version
tenant_id

⸻

173. CONVERSATION FEEDBACK

Staff may mark AI messages:

Correct
Incorrect
Unsafe
Too verbose
Wrong tone
Missing context

⸻

174. AI FAILURE RECOVERY

When AI fails:

Retry
Fallback
Human handoff

should be considered based on policy.

The user should not be left with a broken workflow.

⸻

175. PROVIDER FAILURE UX

The product should hide infrastructure-specific failures from normal users.

For example, do not expose:

OpenRouter 503
Gemini timeout
Provider quota exceeded

Instead:

AI assistance is temporarily unavailable.
You can continue manually.

⸻

176. OFFLINE AND DEGRADED MODE

Where possible, Clinicos should support graceful degradation.

Examples:

AI unavailable

should not necessarily mean:

Clinic operations unavailable

Core operational features should continue where possible.

⸻

177. DEGRADED MODE INDICATOR

Authorized staff may see:

AI assistance temporarily unavailable

without blocking unrelated functionality.

⸻

178. PERFORMANCE UX

User-facing operations should feel responsive.

Target latency classes should be defined separately for:

Instant interactions
Normal requests
AI generation
Image analysis
Reports
Bulk operations

⸻

179. PERCEIVED PERFORMANCE

For long-running AI operations:

* Show immediate acknowledgement
* Show progress where meaningful
* Allow safe navigation away
* Notify when complete
* Preserve operation state

⸻

180. REAL-TIME UPDATES

Where appropriate, use real-time updates for:

New messages
Appointment changes
Task assignment
AI completion
Analysis completion
Workflow status

⸻

181. EVENTUAL CONSISTENCY UX

If data may take time to synchronize, the UI should communicate temporary states.

Example:

Syncing...

rather than showing incorrect final state.

⸻

182. CONFLICT UX

If two users modify the same entity:

This record was updated by another user.

The UI should allow the user to review and resolve conflicts where appropriate.

⸻

183. HUMAN VS AI VISUAL DISTINCTION

The system should use consistent visual semantics for:

Human
AI
System
Patient

The distinction must not rely only on color.

⸻

184. AI ACTION HISTORY

For important AI actions, staff should be able to inspect:

Action
Time
Patient
Workflow
Result
Human override

⸻

185. AI EXPLANATIONS

AI explanations should be concise and evidence-based.

Avoid exposing hidden chain-of-thought.

The product may expose:

Reason
Evidence
Relevant records
Decision factors

without exposing private internal reasoning.

⸻

186. PROMPT VISIBILITY

Normal users should not see system prompts.

Authorized technical administrators may have access to appropriate configuration metadata.

Secrets must never be displayed.

⸻

187. AI POLICY UX

Clinic administrators may configure policies such as:

AI auto-send enabled
AI draft-only
Human approval required
High-risk escalation

⸻

188. SAFE DEFAULTS

New clinics should start with conservative defaults.

Examples:

AI draft mode
Human approval for sensitive workflows
Limited automation
Explicit consent

Automation can be expanded after configuration.

⸻

189. AUTO-SEND POLICY

Auto-send should be configurable by:

Channel
Message type
Workflow
Patient segment
Risk level
Clinic policy

⸻

190. MARKETING VS OPERATIONAL MESSAGES

The UI must distinguish:

Operational message
Transactional message
Marketing message
Clinical communication

Different policies may apply.

⸻

191. SPAM PROTECTION UX

The system should prevent excessive messaging.

Potential controls:

Frequency caps
Quiet hours
Cooldowns
Opt-out
Duplicate prevention

⸻

192. PATIENT OPT-OUT

Patients should have clear ways to opt out where applicable.

The system must respect opt-out state.

⸻

193. MESSAGE PREVIEW

Before sending automated messages, authorized users should be able to preview the rendered message.

Preview must resolve variables.

⸻

194. MESSAGE PERSONALIZATION

Personalization should remain appropriate.

Avoid excessive or creepy personalization.

Use only information relevant to the communication.

⸻

195. CONVERSATIONAL TONE

Clinic tone should be configurable.

Examples:

Professional
Warm
Concise
Premium
Friendly

Tone configuration must not override safety requirements.

⸻

196. AI LANGUAGE QUALITY

AI output should be reviewed for:

* Language
* Tone
* Grammar
* Cultural appropriateness
* Medical safety
* Clinic policy compliance

⸻

197. USER EDUCATION

Clinicos should educate users about AI capabilities gradually.

Avoid overwhelming onboarding with technical details.

⸻

198. PRODUCT TRUST

Trust is built through:

Transparency
Consistency
Human control
Correctness
Auditability
Privacy
Predictability

⸻

199. UX ANTI-PATTERNS

The following are prohibited or strongly discouraged.

199.1 AI Everywhere

Do not insert AI into every screen merely because it is available.

199.2 AI as Authority

Do not present AI output as automatically correct.

199.3 Hidden Automation

Do not silently automate consequential actions.

199.4 Data Dump Dashboards

Do not overwhelm users with metrics.

199.5 Technical Errors

Do not expose infrastructure errors to normal users.

199.6 Fake Certainty

Do not hide uncertainty.

199.7 Excessive Notifications

Do not turn Clinicos into a notification generator.

199.8 Overconfiguration

Do not force clinics to configure dozens of settings before obtaining value.

199.9 Fragmented Patient Context

Do not force users to search multiple places for basic patient context.

199.10 Channel-Specific Workflows

Do not create completely separate operational workflows for every communication channel.

⸻

200. PRIMARY USER JOURNEYS

Clinicos should define and optimize the following journeys.

⸻

201. JOURNEY: NEW PATIENT MESSAGE

Patient sends message
        ↓
Message received
        ↓
Patient identified or created
        ↓
Conversation created
        ↓
Intent detected
        ↓
Lead created or updated
        ↓
AI assistance
        ↓
Response
        ↓
Follow-up if needed

⸻

202. JOURNEY: LEAD TO APPOINTMENT

New lead
    ↓
Qualification
    ↓
Intent identified
    ↓
Service identified
    ↓
Availability checked
    ↓
Appointment proposed
    ↓
Patient selects time
    ↓
Appointment confirmed
    ↓
Reminder

⸻

203. JOURNEY: MISSED APPOINTMENT

Appointment marked no-show
        ↓
No-show workflow
        ↓
Patient contacted
        ↓
Patient response
        |
        +---- Reschedule
        |
        +---- Decline
        |
        +---- Human review

⸻

204. JOURNEY: FACIAL ANALYSIS

Patient requests analysis
        ↓
Consent
        ↓
Image upload
        ↓
Quality check
        |
        +---- Fail → Retake
        |
        +---- Pass
                 ↓
              Analysis
                 ↓
          Safety evaluation
                 ↓
              Results
                 ↓
        Optional clinician review

⸻

205. JOURNEY: HUMAN ESCALATION

Conversation
    ↓
AI detects escalation condition
    ↓
AI stops autonomous action
    ↓
Human task created
    ↓
Staff notified
    ↓
Human reviews context
    ↓
Human responds
    ↓
AI remains paused or resumes according to policy

⸻

206. JOURNEY: CLINIC ONBOARDING

Create account
    ↓
Create clinic
    ↓
Configure profile
    ↓
Add services
    ↓
Add staff
    ↓
Connect channel
    ↓
Configure knowledge
    ↓
Review AI settings
    ↓
Activate safe automations
    ↓
Receive first conversation

⸻

207. UX STATE MODEL

Major entities should expose understandable states.

Example conversation:

NEW
ACTIVE
AI_ASSISTED
HUMAN_ACTIVE
WAITING
ESCALATED
CLOSED

⸻

208. STATE VISIBILITY

Current state should always be visible when it affects user action.

⸻

209. STATE TRANSITIONS

Important transitions should be logged.

Example:

AI_ASSISTED
    ↓
HUMAN_ACTIVE

with:

actor
timestamp
reason

⸻

210. USER ACTION PRIORITY

Primary actions should be visually dominant.

Example:

Confirm Appointment

should be more prominent than:

View Technical Details

⸻

211. SECONDARY ACTIONS

Secondary actions should not compete with the primary workflow.

Examples:

View history
More options
Technical details
Export

⸻

212. DESTRUCTIVE ACTIONS

Destructive actions must be visually differentiated and require appropriate confirmation.

⸻

213. UX FOR EXPERT USERS

Expert users may need shortcuts and advanced controls.

Examples:

Keyboard shortcuts
Advanced filters
Bulk actions
Automation debugging
Technical audit

These should not burden novice users.

⸻

214. PROGRESSIVE DISCLOSURE

Advanced information should appear only when needed.

Example:

Default:

AI generated a response.

Expanded:

Source:
Conversation history
Clinic knowledge
Workflow policy

⸻

215. CONTEXTUAL ACTIONS

Actions should appear near the object they affect.

Example:

Patient page:

Book appointment
Send message
Create follow-up
Start analysis

⸻

216. GLOBAL ACTIONS

Global actions may include:

Search
Create patient
Create appointment
Open inbox

⸻

217. KEYBOARD SUPPORT

Desktop workflows should support keyboard shortcuts for frequent actions.

Potential shortcuts:

Open search
Next conversation
Assign task
Reply
Take over

Exact shortcuts should be defined by the frontend design system.

⸻

218. TOUCH SUPPORT

Mobile interactions should support:

* Large tap targets
* Swipe where appropriate
* Bottom-sheet patterns
* Mobile-friendly forms
* Sticky primary actions

⸻

219. RESPONSIVE CONVERSATION VIEW

On desktop:

Conversation | Patient Context

On mobile:

Conversation
      ↓
Patient Context

Context panels should become accessible without permanently consuming screen space.

⸻

220. RESPONSIVE PATIENT VIEW

Desktop may support:

Patient profile | Timeline | Context panel

Mobile should prioritize:

Patient header
Next action
Timeline
Context

⸻

221. RESPONSIVE DASHBOARD

Dashboards should not simply shrink desktop layouts.

They should be redesigned around mobile priorities.

⸻

222. NOTIFICATION CENTER

The notification center should group notifications by:

Urgency
Type
Patient
Time

⸻

223. NOTIFICATION ACTIONS

Notifications should support direct actions where safe.

Example:

Hot lead detected
[Open Lead]

⸻

224. DEEP LINKS

Notifications should open the exact relevant context.

Example:

New human review required

should open:

Patient → Conversation → Review state

rather than a generic dashboard.

⸻

225. SESSION MANAGEMENT

The UX should support:

Login
Logout
Session expiration
Re-authentication
Multi-device sessions

Sensitive actions may require re-authentication.

⸻

226. AUTHENTICATION UX

Authentication should minimize friction while preserving security.

⸻

227. SECURITY WARNINGS

Security-related UX should be clear and actionable.

Avoid alarming users without reason.

⸻

228. PERMISSION DENIED

Example:

You do not have permission to view this patient.

Where possible, explain who can perform the action.

⸻

229. SESSION EXPIRATION

When a session expires:

Your session has expired.
Please sign in again.

The system should preserve safe unsaved work where possible.

⸻

230. DATA PRIVACY BY DESIGN

UX should minimize unnecessary exposure of sensitive patient information.

Examples:

* Hide sensitive data by default where appropriate
* Avoid showing full patient lists unnecessarily
* Mask sensitive values where appropriate
* Require authorization for exports
* Avoid unnecessary data duplication

⸻

231. SCREENSHOT SAFETY

The system should consider privacy risks when displaying sensitive data on screens.

Patient data should not be unnecessarily exposed in notifications or previews.

⸻

232. CLINIC BRANDING SAFETY

Clinic branding must not make safety warnings or important system states invisible.

⸻

233. AI BRANDING

AI functionality should have consistent labeling.

Examples:

AI Draft
AI Suggestion
AI Analysis
AI Summary

⸻

234. HUMAN REVIEW LABEL

Human-reviewed outputs may be labeled:

Reviewed by staff

or:

Clinician reviewed

only when the review actually occurred.

⸻

235. NO FALSE TRUST SIGNALS

Never display:

Verified
Clinically approved
Doctor reviewed

unless the underlying condition is actually true.

⸻

236. REPORT SHARING

Reports may be shared only through authorized mechanisms.

Sharing should respect:

Patient consent
Clinic policy
Role permissions
Data classification

⸻

237. PUBLIC LINKS

Public patient data links should be avoided by default.

If implemented, they must use:

* Expiring tokens
* Limited scope
* Revocation
* Access logging

⸻

238. PATIENT SELF-SERVICE

Future patient self-service may include:

Appointments
Messages
Forms
Reports
Facial analysis
Consent
Preferences

Each feature must respect authorization.

⸻

239. PATIENT HOME

A potential patient home could show:

Next appointment
Recent conversation
Pending actions
Available clinic services
Reports

⸻

240. PATIENT ACTIONS

Patient-facing actions should be simple:

Book
Reschedule
Cancel
Ask
Upload
Confirm
Review

⸻

241. PATIENT EDUCATION

Educational content should be separated from personalized clinical advice.

⸻

242. AI EDUCATION

When AI provides educational information, the UX should distinguish general education from patient-specific medical decisions.

⸻

243. CLINIC KNOWLEDGE IN UX

When AI answers questions using clinic knowledge, the interface may show:

Based on clinic information

where useful.

⸻

244. STALE KNOWLEDGE

If knowledge may be outdated, the system should not present it as current without validation.

⸻

245. DYNAMIC INFORMATION

Dynamic information must be fetched from authoritative systems.

Examples:

Current availability
Current pricing
Current appointment state
Current clinic hours

⸻

246. AI FALLBACK UX

When authoritative information is unavailable:

I need to confirm this with the clinic.

The system should create an appropriate follow-up or human task.

⸻

247. HUMAN APPROVAL UX

Approval requests should clearly state:

What will happen
Who will receive it
What information is involved
Why approval is needed

⸻

248. APPROVAL ACTIONS

Examples:

Approve
Reject
Edit
Request changes
Assign

⸻

249. APPROVAL EXPIRATION

Approval requests may expire.

The UI should indicate:

Approval expired

and explain what happens next.

⸻

250. AUDITABLE APPROVAL

Every approval should record:

Approver
Time
Action
Version
Object

⸻

251. WORKFLOW HUMAN GATES

High-impact workflows may require explicit human approval before external side effects.

Examples:

Large bulk communication
Sensitive clinical message
High-risk patient communication
Mass automation activation

⸻

252. AI SAFETY GATES

AI outputs may pass through safety gates before reaching users or external systems.

Conceptually:

AI Output
   ↓
Policy Check
   ↓
Safety Check
   ↓
Permission Check
   ↓
Human Approval if required
   ↓
External Action

⸻

253. ACCESSIBILITY FOR AI

AI-generated content must remain accessible.

Examples:

* Screen-reader compatible text
* Clear labels
* No meaning encoded only by color
* Expandable content
* Proper heading hierarchy

⸻

254. INTERNATIONALIZATION ARCHITECTURE

All user-visible strings must be externalized.

Do not hard-code user-facing text in application logic.

⸻

255. TRANSLATION KEYS

Example:

conversation.ai_draft.title
appointment.confirmed.title
facial_analysis.quality.low_light

⸻

256. FALLBACK LANGUAGE

If a translation is unavailable, the system should use a configured fallback language.

It must never display raw translation keys to patients.

⸻

257. TEXT EXPANSION

Layouts must tolerate longer translations.

Do not rely on fixed-width text containers for important UI labels.

⸻

258. RTL/LTR MIXED CONTENT

The UI must correctly handle:

Arabic
Persian
English
Numbers
URLs
Email addresses

within the same screen.

⸻

259. TIMEZONE UX

Appointment times must clearly indicate the relevant clinic timezone when ambiguity exists.

⸻

260. PATIENT TIMEZONE

If patient timezone differs from clinic timezone, appointment communication should avoid ambiguity.

⸻

261. BUSINESS HOURS

The UI should reflect clinic working hours when known.

It must not infer working hours from historical patterns.

⸻

262. CLOSED CLINIC UX

When the clinic is closed:

The clinic is currently closed.

The system may still accept messages and schedule follow-up according to policy.

⸻

263. AFTER-HOURS AI

After-hours AI behavior must be configurable.

Possible modes:

AI only
Draft only
Human escalation
Emergency-aware
Closed response

⸻

264. HUMAN AVAILABILITY

If staff availability is known, the UX may show:

A staff member is available

or:

A staff member will respond during clinic hours

Only when this information is authoritative.

⸻

265. PATIENT WAITING STATE

The patient should receive clear feedback when waiting for human review.

Example:

Your message has been received.
A member of the clinic team will review it.

⸻

266. NO FALSE HUMAN CLAIMS

AI must never falsely claim:

A doctor is reviewing this

unless a real human review task exists.

⸻

267. NO FALSE AVAILABILITY

The system must not claim:

A doctor is available

unless the scheduling or staff availability system confirms it.

⸻

268. NO FALSE APPOINTMENT

The system must not claim an appointment is booked unless the appointment system confirms creation.

⸻

269. CONFIRMATION PATTERN

For critical operations, the UI should use a two-step truth model:

Request
   ↓
System confirmation
   ↓
User-visible confirmed state

⸻

270. OPTIMISTIC UI

Optimistic UI may be used for low-risk operations.

For high-impact operations:

Appointment booking
Payment
Deletion
Consent
External communication

the final state should depend on authoritative confirmation.

⸻

271. EXTERNAL SIDE EFFECTS

The UX must clearly indicate when an action creates an external side effect.

Examples:

Message will be sent
Appointment will be cancelled
Patient will receive notification

⸻

272. BULK SIDE EFFECT WARNING

Bulk actions should summarize consequences.

Example:

You are about to send messages to 87 patients.

⸻

273. SAFE CONFIRMATION LANGUAGE

Confirmation dialogs should explain consequences rather than merely ask:

Are you sure?

Better:

Cancel this appointment?
The patient will be notified according to clinic policy.

⸻

274. PRODUCT FEEDBACK LOOP

UX feedback should connect to product analytics.

Track:

Feature usage
Drop-off
Error rate
Task completion
Time to completion
AI acceptance
AI rejection
Human takeover
Workflow abandonment

⸻

275. UX METRICS

Important UX metrics include:

Task completion rate
Time to first response
Time to appointment
Lead handling time
Follow-up completion rate
AI draft acceptance rate
AI edit rate
Human takeover rate
Error recovery rate
Patient drop-off

⸻

276. AI UX METRICS

Track:

AI suggestion acceptance
AI suggestion rejection
AI edit distance
AI escalation rate
AI failure rate
AI hallucination reports
AI safety blocks

⸻

277. FACIAL ANALYSIS UX METRICS

Track:

Image upload success
Quality failure rate
Retake rate
Analysis completion
Analysis failure
Human review rate
User satisfaction

⸻

278. ONBOARDING METRICS

Track:

Setup completion
Time to first value
Channel connection
First conversation
First appointment
First automation

⸻

279. PERFORMANCE METRICS

Track:

Page load
Interaction latency
API latency
AI latency
Image analysis latency
Workflow latency
Notification latency

⸻

280. ERROR METRICS

Track:

UI errors
API errors
AI errors
Workflow errors
Permission failures
Integration failures

⸻

281. UX EXPERIMENTATION

The product may support controlled experiments.

Examples:

Message wording
Onboarding flow
CTA placement
AI draft presentation
Follow-up timing

Experiments must not compromise safety or privacy.

⸻

282. FEATURE FLAGS

UX features should support feature flags where appropriate.

Example:

facial_analysis_v2
new_inbox_ui
ai_draft_v3

⸻

283. CANARY RELEASES

Major UX changes should support controlled rollout.

Possible rollout:

Internal
Small tenant group
Larger tenant group
All tenants

⸻

284. UX ROLLBACK

Major changes should be reversible.

Rollback should not corrupt user data or workflow state.

⸻

285. DESIGN-ENGINEERING CONTRACT

Design specifications must identify:

Component
State
Interaction
Validation
Error
Loading
Empty
Permission
Accessibility
Responsive behavior

⸻

286. COMPONENT STATES

Every major component should define:

Default
Hover
Focus
Active
Disabled
Loading
Success
Error
Empty

⸻

287. DESIGN HANDOFF

Design handoff should include:

Component specification
Responsive behavior
Interaction behavior
Accessibility requirements
Content rules
State rules

⸻

288. FRONTEND ARCHITECTURE ALIGNMENT

The frontend should consume domain APIs rather than embedding business rules in UI components.

The UI should not independently calculate authoritative business state.

⸻

289. BACKEND AUTHORITY

Backend services remain authoritative for:

Permissions
Patient identity
Appointments
Lead state
Workflow state
Consent
Security
Operational data

⸻

290. AI AUTHORITY BOUNDARY

AI should not be treated as authoritative for:

Identity
Appointment availability
Appointment confirmation
Current price
Permission
Consent
Security state

⸻

291. UX AND EVENT ENGINE

The UX should reflect event-driven state changes.

Examples:

Lead created

should update relevant UI surfaces.

Appointment confirmed

should update:

Patient
Conversation
Appointment
Task
Notification

where applicable.

⸻

292. REAL-TIME CONSISTENCY

The product should converge toward a consistent state across screens.

⸻

293. STALE DATA INDICATORS

If data may be stale, the UI should indicate this when it materially affects decisions.

Example:

Last updated 2 minutes ago

⸻

294. REFRESH

Users should be able to refresh important views where appropriate.

Automatic refresh is preferred where safe and useful.

⸻

295. ERROR BOUNDARIES

Frontend sections should fail gracefully.

An error in:

AI Insights

should not break:

Appointments

⸻

296. RESILIENCE UX

When a subsystem is unavailable:

Unavailable component

should provide an alternative path where possible.

⸻

297. PATIENT SAFETY OVER CONVERSION

If a conflict exists between:

conversion optimization

and:

patient safety

patient safety wins.

⸻

298. PRIVACY OVER CONVENIENCE

If a conflict exists between:

convenience

and:

privacy

the product should follow configured privacy requirements.

⸻

299. HUMAN OVERRIDE

Authorized humans must be able to override AI recommendations where policy permits.

Human overrides must be logged.

⸻

300. AI CANNOT OVERRIDE HUMANS

AI must not silently reverse an authorized human decision.

⸻

301. PATIENT EXPERIENCE PRIORITY

The patient experience should optimize for:

Clarity
Trust
Speed
Respect
Safety
Privacy

⸻

302. STAFF EXPERIENCE PRIORITY

Staff experience should optimize for:

Efficiency
Context
Prioritization
Control
Visibility
Automation

⸻

303. DOCTOR EXPERIENCE PRIORITY

Doctor experience should optimize for:

Clinical relevance
Safety
Context
Reviewability
Minimal administrative burden

⸻

304. OWNER EXPERIENCE PRIORITY

Owner experience should optimize for:

Visibility
Performance
Growth
Operational control
Decision support

⸻

305. UX GOVERNANCE

Product UX decisions should be documented.

Major changes should specify:

Problem
User
Current behavior
New behavior
Expected outcome
Safety impact
Data impact

⸻

306. UX VERSIONING

Major UX architecture changes should be versioned.

Example:

UX v1
UX v2

Component-level changes should remain backward compatible where necessary.

⸻

307. UX TESTING

UX testing should include:

Usability testing
Accessibility testing
Responsive testing
Localization testing
Workflow testing
AI interaction testing
Error-state testing
Security-state testing

⸻

308. USER JOURNEY TESTING

Critical journeys must be tested end-to-end.

Minimum journeys:

New patient message
Lead qualification
Appointment booking
Appointment reminder
No-show recovery
Human takeover
Facial analysis
AI escalation
Clinic onboarding

⸻

309. ACCESSIBILITY TESTING

Test:

Keyboard
Screen reader
Contrast
Focus
Touch
Text scaling
RTL
Reduced motion

⸻

310. LOCALIZATION TESTING

Test all supported languages for:

Layout
Text direction
Date
Time
Numbers
Currency
Long strings
Mixed RTL/LTR

⸻

311. AI UX TESTING

Test:

Correct output
Wrong output
Uncertain output
Unsafe output
Provider failure
Timeout
Human escalation
Fallback

⸻

312. FACIAL ANALYSIS UX TESTING

Test:

Good image
Poor lighting
Blur
Occlusion
Multiple faces
Wrong orientation
Low resolution
Consent missing
Consent revoked
Analysis failure

⸻

313. AUTOMATION UX TESTING

Test:

Trigger
Condition
Action
Delay
Retry
Cancellation
Human approval
Failure
Replay

⸻

314. SECURITY UX TESTING

Test:

Unauthorized access
Expired session
Cross-tenant access
Permission changes
Sensitive export
Consent revocation

⸻

315. USER ACCEPTANCE TESTING

Representative users should test:

Patient
Secretary
Doctor
Owner

before major releases.

⸻

316. UX DEFINITION OF DONE

A UX feature is not complete until:

* Primary journey is defined
* Empty state is defined
* Loading state is defined
* Error state is defined
* Permission state is defined
* Responsive behavior is defined
* Accessibility behavior is defined
* Localization behavior is defined
* AI behavior is defined if applicable
* Audit behavior is defined if applicable
* Safety behavior is defined where relevant
* Analytics events are defined

⸻

317. PRODUCT UX INVARIANTS

The following invariants must always hold.

Invariant 1

The UI must never claim an operation succeeded unless the authoritative system confirms success.

Invariant 2

The UI must never present AI output as guaranteed medical truth.

Invariant 3

Patients must never see another tenant’s data.

Invariant 4

AI must not silently resume after an explicit human takeover unless policy explicitly allows it.

Invariant 5

Dynamic operational information must come from authoritative sources.

Invariant 6

Sensitive actions must respect permissions.

Invariant 7

Consent-dependent processing must respect consent state.

Invariant 8

The system must not expose internal secrets.

Invariant 9

The interface must remain usable when AI is unavailable.

Invariant 10

Human safety decisions override conversion optimization.

⸻

318. UX QUALITY BAR

A high-quality Clinicos UX should feel:

Simple
Fast
Calm
Trustworthy
Professional
Modern
Human
Context-aware
AI-assisted
Never AI-dependent

⸻

319. FINAL PRODUCT PHILOSOPHY

Clinicos should not make clinic staff work harder to use AI.

Instead:

AI should reduce complexity.

The ideal experience is:

Patient communicates naturally
        ↓
Clinicos understands context
        ↓
Clinicos organizes the work
        ↓
AI assists where useful
        ↓
Automation handles repetitive operations
        ↓
Humans control consequential decisions
        ↓
Clinic operates more efficiently

The user should experience the result, not the machinery.

⸻

320. FINAL UX PRINCIPLE

The ultimate UX goal of Clinicos is:

Make the right action obvious,
make the safe action easy,
make repetitive work automatic,
make AI understandable,
and always keep humans in control of consequential decisions.

This principle should guide all future Clinicos product and interface decisions.
