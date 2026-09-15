# CLINICOS — PRODUCT REQUIREMENTS

## Document Status

- Document Type: Product Requirements Specification
- Product: Clinicos
- Version: 1.0
- Status: Target Product Specification
- Purpose: Define what Clinicos must ultimately do and how it should behave
- Source of Truth: This document defines the desired product behavior, not the current implementation.
- Important: The current repository may be incomplete, outdated, temporary, or architecturally different from these requirements.

---

# 1. PRODUCT DEFINITION

Clinicos is an AI-native operating system for aesthetic, beauty, dermatology, cosmetic, and related medical/aesthetic clinics.

Clinicos is not merely:

- a Telegram chatbot
- an FAQ bot
- a CRM
- an appointment bot
- a lead tracker
- a facial-analysis tool

It is intended to become an intelligent digital operating layer for a clinic.

The system should connect:

- patients
- secretaries
- doctors
- clinic owners/managers
- clinic knowledge
- conversations
- leads
- appointments
- follow-ups
- AI
- facial analysis
- analytics
- notifications
- operational workflows

into one coherent system.

The product should continuously transform raw patient interactions into useful operational intelligence while maintaining safety, privacy, reliability, and human control.

---

# 2. PRODUCT PRINCIPLES

Clinicos must follow these principles:

1. AI-first
2. Human-controlled
3. Safety-first
4. Privacy-first
5. Evidence/knowledge-grounded
6. Explainable when making important classifications or recommendations
7. Modular
8. Multi-tenant
9. Scalable
10. Cost-aware
11. Channel-independent
12. Configurable by each clinic
13. Conversion-oriented without manipulation
14. Reliable before being clever
15. Never invent information

---

# 3. PRIMARY USERS

Clinicos must support at least these roles:

## 3.1 Patient

The patient should be able to:

- communicate with the clinic
- ask questions
- receive information
- learn about services
- ask about pricing
- request appointments
- reschedule appointments
- cancel appointments
- receive reminders
- receive follow-ups
- upload images when appropriate
- use facial analysis when eligible
- receive patient-friendly explanations
- request human assistance
- control communication preferences

---

## 3.2 Secretary

The secretary should be able to:

- see incoming conversations
- see patient profiles
- see patient history
- see lead status
- see lead priority
- see follow-up tasks
- see appointment requests
- manage appointments
- take over conversations
- correct AI responses
- review AI-generated information
- review knowledge candidates
- see important notifications
- see hot leads
- see patients requiring action
- use AI as a copilot rather than being replaced by it

---

## 3.3 Doctor

The doctor should be able to:

- access relevant patient information
- review conversation history
- review appointment information
- review facial-analysis results
- review AI-generated summaries
- provide/approve clinical or treatment-related information
- correct AI outputs
- control medical boundaries
- use an AI doctor/clinical copilot where appropriate
- review important escalations

The doctor-facing AI must never present itself as an autonomous medical authority.

---

## 3.4 Clinic Owner / Manager

The owner/manager should be able to:

- manage clinic configuration
- manage staff
- manage doctors
- manage services
- manage prices
- manage clinic knowledge
- manage working hours
- configure AI behavior
- configure lead thresholds
- configure follow-up rules
- configure notifications
- review analytics
- review conversion
- review staff performance
- review AI performance
- review operational problems
- review financial/commercial insights
- configure facial-analysis policies
- manage permissions

---

# 4. COMMUNICATION CHANNELS

## 4.1 Initial Channel

Telegram may be used as the initial communication channel.

However, Clinicos must NOT be architecturally defined as a Telegram-only product.

Telegram is a channel, not the product itself.

---

## 4.2 Future Channels

The product should be designed to eventually support:

- Instagram
- Website chat
- Web applications
- Other messaging channels
- Social-media channels
- Potential future voice channels

All channels should eventually feed into a unified communication layer.

---

# 5. UNIFIED PATIENT IDENTITY

Clinicos should eventually provide a unified identity system.

A patient may interact through:

- Telegram
- Instagram
- website
- other supported channels

The system should attempt to recognize when multiple interactions belong to the same person.

Identity resolution must be:

- privacy-aware
- conservative
- explainable where appropriate
- resistant to accidental identity merging

The system must never confidently merge two people merely because their names or other weak identifiers match.

---

# 6. PATIENT INTELLIGENCE

Clinicos must maintain an intelligent patient profile.

The profile may include:

- identity information
- preferred language
- communication preferences
- conversation history
- interested services
- previously discussed services
- lead status
- lead score
- appointment status
- previous appointments
- follow-up status
- questions
- objections
- preferences
- relevant notes
- interaction history
- patient lifecycle stage

The system should distinguish between:

### Explicit information

Information directly provided or confirmed by the patient.

### Derived information

Information inferred from behavior or conversation.

### AI hypotheses

Possible interpretations that have not been confirmed.

Important patient facts must not be silently converted from inference into fact.

---

# 7. PATIENT LIFECYCLE

Clinicos should understand the patient journey.

Possible lifecycle states include:

- New
- Cold Lead
- Warm Lead
- Hot Lead
- Appointment Requested
- Appointment Booked
- Appointment Completed
- Converted
- Returning Patient
- Inactive
- Lost Lead
- Recovered Lead
- VIP / High-Value Patient

The exact lifecycle model must remain configurable.

---

# 8. LEAD INTELLIGENCE

Clinicos must provide an intelligent lead system.

The system should identify:

- cold leads
- warm leads
- hot leads
- converted leads
- lost leads
- inactive leads
- returning leads
- high-value leads

Lead classification should consider signals such as:

- service interest
- purchase intent
- appointment intent
- urgency
- questions about price
- questions about availability
- repeated engagement
- previous interactions
- responsiveness
- objections
- requested timing
- behavior patterns

Lead scoring must be:

- configurable
- explainable
- based on observable evidence
- resistant to arbitrary AI guesses

---

# 9. HOT LEAD DETECTION

Clinicos should automatically detect potentially hot leads.

Examples of strong signals:

- explicit desire to book
- asking for available appointment times
- asking how to pay
- asking where the clinic is before booking
- asking for immediate availability
- expressing strong interest in a specific treatment
- returning after previous interaction
- repeatedly engaging with treatment information

When a lead becomes hot, the system may:

- notify the secretary
- notify the appropriate staff member
- prioritize the conversation
- recommend an action
- create a follow-up task
- escalate to human takeover

The system must explain why a lead was classified as hot.

---

# 10. LEAD TRACKER

Clinicos should provide a lead-tracking system.

The lead tracker should show:

- patient
- source/channel
- interested service
- lead status
- lead score
- last interaction
- next action
- follow-up status
- appointment status
- conversion status
- assigned staff member
- important notes

The system should make it easy for staff to answer:

> Who needs attention right now?

---

# 11. FOLLOW-UP ENGINE

Clinicos must include an intelligent follow-up engine.

The engine should:

- detect when follow-up is appropriate
- schedule follow-ups
- recommend timing
- consider patient behavior
- consider clinic working hours
- consider previous messages
- avoid excessive messaging
- respect opt-outs
- avoid spam
- stop or modify follow-ups when the patient responds

Possible follow-up scenarios:

- patient asked a question but disappeared
- patient showed strong treatment interest
- patient requested information
- patient started booking but did not finish
- patient received pricing information but did not respond
- appointment was cancelled
- appointment was missed
- patient became inactive
- previous treatment was completed
- patient may be due for a return visit

---

# 12. LOST LEAD RECOVERY

Clinicos should identify lost or inactive opportunities.

The system should determine:

- why the lead may have been lost
- whether recovery is appropriate
- what message might be useful
- when to contact them
- whether human intervention is preferable

Recovery messages must not be manipulative or spammy.

---

# 13. APPOINTMENT ENGINE

Clinicos should eventually provide an appointment management engine.

It should support:

- appointment requests
- availability checking
- booking
- rescheduling
- cancellation
- reminders
- appointment status
- appointment history
- staff assignment
- doctor assignment
- service assignment

Critical rule:

> Clinicos must never claim that a time slot is available unless availability has actually been verified through the authoritative scheduling system.

The AI must never invent appointment availability.

---

# 14. APPOINTMENT INTELLIGENCE

The system should understand appointment-related intent.

Examples:

- "Can I come tomorrow?"
- "Do you have an appointment today?"
- "I want to book Botox."
- "Can I move my appointment?"
- "I can't come."
- "What time is the doctor available?"

The AI should convert these into structured operational actions whenever possible.

---

# 15. FAQ INTELLIGENCE

Clinicos must not be limited to manually written FAQs.

The system should analyze conversations and identify:

- frequently asked questions
- unanswered questions
- poorly answered questions
- recurring objections
- emerging questions
- outdated answers
- missing knowledge
- service-specific questions
- pricing questions
- operational questions

The system may propose new FAQ entries.

However:

> AI-generated knowledge must not automatically become authoritative clinic knowledge without an appropriate validation process.

---

# 16. CLINIC KNOWLEDGE BASE

Clinicos must maintain a structured clinic knowledge base.

Possible knowledge categories:

### Clinic information

- name
- address
- phone
- working hours
- holidays
- branches
- contact information

### Doctors

- name
- specialty
- biography
- working hours
- services provided
- approved information

### Services

- service name
- description
- indications
- preparation
- aftercare
- expected experience
- limitations
- approved pricing
- packages
- related services

### Policies

- cancellation policy
- payment policy
- booking policy
- refund policy
- privacy policy
- communication policy

### FAQs

- approved questions
- approved answers

### Promotions

- active offers
- eligibility
- expiration
- conditions

### Medical safety information

- approved warnings
- contraindication-related information
- escalation rules
- emergency guidance

---

# 17. KNOWLEDGE GOVERNANCE

Clinicos must distinguish between:

- authoritative knowledge
- candidate knowledge
- outdated knowledge
- user-generated information
- AI inference

Knowledge should have lifecycle states such as:

- Candidate
- Under Review
- Approved
- Rejected
- Deprecated

The AI must prioritize approved authoritative knowledge.

---

# 18. SECRETARY COPILOT

Clinicos should provide a Secretary Copilot.

It should assist with:

- conversation summaries
- suggested replies
- lead classification
- follow-up recommendations
- appointment handling
- patient summaries
- FAQ retrieval
- knowledge retrieval
- objection handling
- conversation handoff
- task generation

The secretary remains in control.

---

# 19. DOCTOR COPILOT

Clinicos should eventually provide a Doctor Copilot.

Potential functions:

- patient summary
- conversation summary
- treatment discussion summary
- relevant history extraction
- facial-analysis review
- patient question summarization
- non-diagnostic decision support
- preparation of patient-friendly explanations

The Doctor Copilot must clearly distinguish:

- known facts
- retrieved knowledge
- AI interpretation
- uncertainty

---

# 20. HUMAN TAKEOVER

Clinicos must support human takeover.

A human should be able to take control of a conversation at any time.

Triggers may include:

- patient request
- medical uncertainty
- complaint
- sensitive issue
- high-value patient
- high-risk topic
- AI uncertainty
- repeated misunderstanding
- explicit staff intervention

When takeover occurs:

- AI should stop or reduce autonomous responses according to configuration
- staff should see relevant context
- the system should record the takeover event

---

# 21. MEDICAL SAFETY LAYER

Medical safety is a core requirement.

Clinicos must NOT:

- fabricate diagnoses
- fabricate medical facts
- fabricate contraindications
- fabricate treatment outcomes
- fabricate clinical history
- fabricate doctor instructions
- fabricate prices
- fabricate appointment availability
- present uncertain information as certain

The system should recognize high-risk topics and escalate when necessary.

Examples:

- emergency symptoms
- severe adverse reactions
- medication emergencies
- severe allergic reactions
- dangerous post-procedure symptoms
- significant bleeding
- acute neurological symptoms
- chest pain
- breathing difficulty
- other potentially urgent situations

The AI should provide appropriate safety-oriented guidance and recommend human/medical evaluation when required.

---

# 22. AI PERSONALITY

The default AI personality should be:

- professional
- friendly
- concise
- empathetic
- respectful
- trustworthy
- non-manipulative
- medically cautious
- patient-centered

The AI should not:

- pressure patients
- create artificial urgency
- manipulate emotions
- exaggerate benefits
- guarantee outcomes
- shame patients
- fabricate scarcity

---

# 23. MULTILINGUAL SUPPORT

Clinicos should support:

- Persian
- English
- Azerbaijani Turkish
- Arabic
- Turkish

The system should be able to:

- detect language
- maintain language preference
- respond in the appropriate language
- preserve medical terminology appropriately
- preserve clinic-specific terminology
- generate reports in supported languages

Language support should be extensible.

---

# 24. AI / LLM ABSTRACTION

Clinicos must not hard-code the entire product around one AI model.

The product should have an AI abstraction layer.

This layer should allow:

- model/provider replacement
- task-specific model selection
- future routing
- cost optimization
- fallback
- monitoring
- token/cost tracking

The project currently uses **FreeLLMAPI as a reference AI gateway/provider**.

FreeLLMAPI should be treated as an integration/gateway layer, not as an irreversible architectural dependency.

The underlying model may change in the future without redesigning the entire product.

---

# 25. AI TASK ROUTING

Different tasks may eventually use different AI models.

Potential task categories:

- conversation
- classification
- summarization
- extraction
- translation
- vision
- medical safety
- analytics
- report generation

Routing should consider:

- quality
- latency
- cost
- availability
- task requirements
- safety

---

# 26. MULTI-AGENT CAPABILITY

Clinicos may evolve into a multi-agent system.

Potential agents:

- Patient Agent
- Lead Agent
- Follow-up Agent
- Appointment Agent
- Knowledge Agent
- Secretary Agent
- Medical Safety Agent
- Analytics Agent
- Facial Analysis Agent
- Reporting Agent

A central orchestration layer may coordinate these agents.

Agents must not create contradictory independent versions of patient truth.

Shared state and authoritative data must remain centralized.

---

# 27. AI MEMORY AND CONTEXT

Clinicos should separate different types of context.

### Conversation context

What is happening in the current conversation.

### Patient memory

Longer-term patient-specific information.

### Clinic knowledge

Authoritative information about the clinic.

### Operational state

Appointments, tasks, lead status, follow-ups, etc.

### Analytics

Aggregated behavioral and operational information.

These contexts must not be mixed carelessly.

---

# 28. KNOWLEDGE LEARNING PIPELINE

Clinicos should eventually learn from conversations in a controlled manner.

Desired pipeline:

1. Detect candidate information
2. Extract candidate
3. Classify candidate
4. Check source
5. Validate
6. Human review when required
7. Store approved knowledge
8. Make retrievable
9. Monitor usage
10. Deprecate when outdated

The system must avoid:

> AI hallucination → stored as knowledge → future AI retrieval → amplified hallucination

This feedback loop must be explicitly prevented.

---

# 29. FACIAL ANALYSIS SYSTEM

Facial analysis is a strategic Clinicos capability.

The system should support:

1. Image upload
2. User consent
3. Image-quality assessment
4. Face detection
5. Facial landmark detection
6. Facial measurements
7. Metric generation
8. AI interpretation
9. Patient-friendly explanation
10. Treatment-oriented suggestions
11. Optional visualization
12. Optional PDF report
13. Before/after comparison
14. Usage tracking
15. Safety disclaimers

---

# 30. FACIAL ANALYSIS — MEDIAPIPE

MediaPipe may be used as the facial landmark/measurement foundation.

Potential outputs:

- facial landmarks
- symmetry measurements
- proportions
- distances
- angles
- regional measurements
- other measurable facial features

Measurements should be separated from AI interpretation.

---

# 31. FACIAL ANALYSIS — AI INTERPRETATION

AI may interpret facial-analysis measurements.

The AI should explain:

- what was measured
- what the measurement may indicate
- limitations
- possible aesthetic considerations
- possible treatment categories

The system must NOT present facial analysis as a definitive medical diagnosis.

---

# 32. FACIAL ANALYSIS — IMAGE QUALITY

Before analysis, Clinicos should evaluate image quality.

Potential checks:

- face visibility
- lighting
- blur
- angle
- distance
- occlusion
- image resolution
- multiple faces

If quality is insufficient:

- explain the problem
- ask the patient to retake the image
- provide simple instructions

The system should not perform unreliable analysis merely to produce an answer.

---

# 33. FACIAL ANALYSIS — USAGE POLICY

The intended default policy is:

### Standard patient

One free facial analysis per lifetime unless clinic policy/configuration changes this.

### Doctor / Admin / Authorized staff

Unlimited or configurable access according to clinic policy.

The system must track usage.

Usage rules must be configurable.

---

# 34. FACIAL ANALYSIS — PDF REPORT

Clinicos should eventually generate a professional facial-analysis report.

The report may contain:

- patient information
- analysis date
- image
- summary
- measurements
- observations
- visualizations
- treatment-oriented suggestions
- limitations
- medical/aesthetic disclaimer
- clinic branding

Reports should support RTL languages where appropriate.

---

# 35. FACIAL VISUALIZATION

The system should optionally visualize:

- facial landmarks
- measurement lines
- angles
- regions
- symmetry
- comparison areas

Visualizations must be understandable to the patient.

---

# 36. BEFORE / AFTER

Clinicos should support before/after facial analysis.

The system should allow:

- storing analysis results
- linking images
- comparing measurements
- comparing visualizations
- showing changes over time

Comparisons must not falsely imply causality.

---

# 37. AGING SIMULATION

Clinicos may eventually support aging simulation.

Any simulation must be explicitly labeled as:

- simulated
- approximate
- non-predictive

It must never be presented as a factual prediction of the patient's future appearance.

---

# 38. VISION AI

Vision-capable AI should be abstracted from the rest of the product.

The vision system may be used for:

- image understanding
- image-quality interpretation
- facial-analysis interpretation
- visual comparison
- patient-friendly explanation

Vision AI must not bypass deterministic safety/measurement layers.

---

# 39. PRICING INTELLIGENCE

Clinicos should intelligently handle pricing.

It should be able to:

- retrieve current approved prices
- explain pricing factors
- identify price-sensitive leads
- recommend appropriate next actions
- explain packages
- compare approved packages
- detect pricing questions

The system must NEVER invent a price.

If the price is unavailable or uncertain, the system should say so and route appropriately.

---

# 40. CONVERSION INTELLIGENCE

Clinicos should understand the complete conversion funnel:

Interaction
→ Interest
→ Qualified Lead
→ Hot Lead
→ Appointment Request
→ Appointment
→ Attendance
→ Treatment
→ Conversion
→ Returning Patient

The system should identify:

- drop-off points
- conversion bottlenecks
- common objections
- successful patterns
- high-performing services
- high-performing follow-ups

---

# 41. A/B TESTING

Clinicos should eventually support controlled experimentation.

Possible experiments:

- message wording
- CTA wording
- follow-up timing
- educational content
- offers
- recovery messages
- conversation strategies

Experiments should measure actual outcomes.

The system must avoid declaring a strategy successful based on insufficient data.

---

# 42. ANALYTICS

Clinicos should provide analytics such as:

### Lead analytics

- new leads
- qualified leads
- hot leads
- converted leads
- lost leads
- recovered leads

### Appointment analytics

- requests
- bookings
- cancellations
- no-shows
- completed appointments

### Conversion analytics

- conversion rate
- service conversion
- lead-to-appointment conversion
- appointment-to-treatment conversion

### Operational analytics

- response time
- follow-up completion
- staff activity
- human takeover
- unresolved conversations

### Knowledge analytics

- top questions
- unanswered questions
- outdated knowledge
- knowledge gaps

### AI analytics

- AI responses
- failures
- escalations
- corrections
- hallucination reports
- latency
- token usage
- cost

### Facial analysis analytics

- number of analyses
- successful analyses
- failed analyses
- usage by role
- conversion after analysis

---

# 43. WEEKLY REPORT

Clinicos should generate a weekly clinic intelligence report.

The report should include:

- total leads
- hot leads
- appointments
- conversions
- lost leads
- recovered leads
- top questions
- unanswered questions
- service demand
- staff activity
- AI performance
- facial-analysis usage
- important operational problems
- recommended actions

Recommendations should be evidence-based.

---

# 44. AI PERFORMANCE MONITORING

Clinicos must monitor AI quality.

Metrics may include:

- successful responses
- failed responses
- escalations
- human corrections
- hallucination reports
- unanswered questions
- response latency
- token usage
- cost
- conversion impact
- user satisfaction where measurable

The system should detect degradation.

---

# 45. COST OPTIMIZATION

AI costs should be actively controlled.

Potential techniques:

- model selection
- routing
- prompt optimization
- context reduction
- caching
- retrieval optimization
- avoiding duplicate requests
- summarization
- task-specific models

Cost optimization must never override:

1. safety
2. correctness
3. reliability
4. required quality

---

# 46. VOICE FUTURE

Voice-note support is a future capability.

Potential functions:

- patient voice messages
- secretary voice messages
- speech-to-text
- AI analysis
- future voice responses

Voice should remain modular.

It must not become a hard dependency for the core product.

---

# 47. NOTIFICATION SYSTEM

Clinicos should provide intelligent notifications.

Potential notification events:

- hot lead
- urgent escalation
- appointment request
- appointment booking
- appointment cancellation
- missed follow-up
- lost lead
- recovered lead
- high-value patient
- facial analysis completed
- human takeover
- system failure
- AI failure

Notifications should be:

- role-based
- configurable
- prioritized
- non-spammy

---

# 48. PATIENT PRIORITIZATION

Clinicos should prioritize patients based on configurable signals.

Possible priorities:

- urgent
- hot lead
- VIP
- high-value
- follow-up required
- returning patient
- inactive
- normal

Prioritization should be explainable.

---

# 49. PRIVACY

Clinicos handles potentially sensitive patient information.

The product must support:

- data isolation
- access control
- least privilege
- secure storage
- secure communication
- auditability
- configurable retention
- deletion policies
- privacy-aware AI processing

Patient information must never leak across clinics.

---

# 50. MULTI-TENANCY

Clinicos must support multiple clinics.

Each clinic must have isolated:

- patients
- conversations
- staff
- doctors
- appointments
- services
- prices
- knowledge
- analytics
- facial analyses
- AI configuration
- reports

Cross-clinic data leakage is a critical security failure.

---

# 51. CONFIGURABILITY

Each clinic should be able to configure:

- clinic information
- services
- prices
- doctors
- staff
- working hours
- languages
- AI tone
- escalation rules
- lead thresholds
- follow-up rules
- notification rules
- facial-analysis settings
- patient usage limits
- appointment policies
- knowledge

The core software should not require code changes for normal clinic configuration.

---

# 52. AUTOMATION ENGINE

Clinicos should eventually include a configurable automation engine.

Automations may use:

- events
- rules
- conditions
- AI classifications
- time
- patient state
- lead state
- appointment state

Examples:

### Example 1

If a patient becomes hot:
→ notify secretary
→ create follow-up task
→ prioritize conversation

### Example 2

If a patient asks about pricing:
→ retrieve approved price
→ answer
→ update service interest
→ update lead score

### Example 3

If a patient requests appointment:
→ verify availability
→ create appointment request

### Example 4

If a patient becomes inactive after strong interest:
→ create recovery opportunity

---

# 53. EVENT-DRIVEN PRODUCT BEHAVIOR

The product should eventually expose meaningful domain events.

Examples:

- patient.created
- patient.updated
- lead.created
- lead.became_hot
- lead.converted
- lead.lost
- lead.recovered
- appointment.requested
- appointment.booked
- appointment.cancelled
- followup.required
- followup.completed
- human_takeover.started
- facial_analysis.started
- facial_analysis.completed
- patient.returned
- knowledge_candidate.created
- knowledge.updated

These events may trigger automation, notifications, analytics, and other workflows.

---

# 54. PRODUCT UX

The overall product experience should feel:

- intelligent
- fast
- professional
- simple
- trustworthy
- personalized
- human

The complexity of the underlying AI must not create unnecessary complexity for clinic staff.

---

# 55. ERROR HANDLING

When Clinicos cannot safely complete an action, it must:

1. recognize the limitation
2. avoid inventing an answer
3. explain the limitation appropriately
4. provide the safest next action
5. escalate when required
6. log the failure when appropriate

Example:

If the AI cannot verify appointment availability:

It must NOT say:

> "Tomorrow at 5 PM is available."

Instead it should say that availability needs to be checked through the clinic's scheduling system or route the request to staff.

---

# 56. UNCERTAINTY HANDLING

Clinicos should distinguish:

### FACT

Verified information.

### INFERENCE

Reasonable conclusion based on available information.

### HYPOTHESIS

Possible interpretation requiring confirmation.

### ASSUMPTION

Temporary assumption used because information is missing.

Important decisions should not silently convert an assumption into a fact.

---

# 57. HUMAN OVERSIGHT

AI should remain under human control.

Humans must be able to:

- correct
- override
- approve
- reject
- disable
- escalate
- review

AI decisions.

High-risk actions should have stronger human oversight.

---

# 58. AUDITABILITY

Important system actions should be traceable.

Examples:

- AI response
- human correction
- lead classification
- appointment action
- knowledge approval
- knowledge rejection
- facial analysis
- notification
- human takeover
- configuration changes

The system should be able to answer:

> Why did Clinicos do this?

when technically and legally appropriate.

---

# 59. RELIABILITY

Core operations should be reliable.

The product should tolerate:

- temporary AI failures
- network failures
- provider failures
- database failures
- external API failures
- timeout
- malformed AI output

Failures should degrade gracefully.

---

# 60. NO HALLUCINATION REQUIREMENT

Clinicos must follow a strict anti-hallucination philosophy.

The AI must not invent:

- prices
- appointment availability
- doctors
- services
- policies
- patient history
- medical facts
- clinic information
- treatment guarantees
- test results
- facial measurements
- system capabilities

When information is unavailable:

> The system should acknowledge uncertainty and use an appropriate fallback.

---

# 61. PATIENT EXPERIENCE REQUIREMENTS

The patient should experience Clinicos as:

- helpful
- fast
- respectful
- understandable
- personalized
- safe

The system should avoid:

- repetitive responses
- unnecessary questions
- robotic language
- excessive upselling
- spam
- contradictions
- unexplained AI behavior

---

# 62. BUSINESS VALUE

Clinicos should create measurable value for clinics.

Primary value areas:

1. More qualified leads
2. Faster response
3. Higher appointment conversion
4. Better follow-up
5. Fewer lost leads
6. Better patient retention
7. Better staff productivity
8. Better patient experience
9. Better clinic intelligence
10. Reduced repetitive work
11. Better use of patient data
12. Better AI-assisted operations

---

# 63. PRIORITY FRAMEWORK

When product requirements conflict, use this priority order:

### P0 — Critical

- Patient safety
- Security
- Privacy
- Data isolation
- Correctness
- Reliable core operations

### P1 — Core Product

- Patient intelligence
- Lead management
- Follow-up
- Appointment management
- Knowledge base
- Human takeover
- AI assistant
- Multilingual support

### P2 — Strategic

- Facial analysis
- Analytics
- Reporting
- Conversion intelligence
- AI performance monitoring
- Automation engine
- A/B testing

### P3 — Advanced / Future

- Multi-agent architecture
- Voice
- Advanced vision
- Aging simulation
- Advanced prediction
- Cross-channel identity intelligence
- Advanced optimization

---

# 64. ACCEPTANCE PHILOSOPHY

A feature should not be considered complete merely because:

- code exists
- an endpoint exists
- a UI exists
- an AI response is produced

A feature is complete only when:

1. expected behavior is defined
2. edge cases are considered
3. failure modes are handled
4. security is considered
5. data integrity is preserved
6. relevant tests exist
7. real behavior is verified
8. the feature integrates correctly with the rest of the product

---

# 65. CURRENT IMPLEMENTATION VS TARGET

This document describes the desired product.

The existing repository is only the current implementation state.

Therefore:

- Do not assume current code represents the final architecture.
- Do not preserve a bad architecture merely because it already exists.
- Do not remove desired capabilities because they are currently missing.
- Do not claim a capability exists because it appears in this document.
- Do not rewrite the product requirements to match the current repository.
- Compare current implementation against this document and identify gaps.

The correct process is:

CURRENT STATE
→ GAP ANALYSIS
→ TARGET DESIGN
→ IMPLEMENTATION PLAN
→ IMPLEMENTATION
→ TESTING
→ VERIFICATION

---

# 66. FINAL PRODUCT VISION

Clinicos should ultimately become an intelligent digital operating layer for aesthetic and medical-aesthetic clinics.

It should connect:

Patient
↕
Communication
↕
AI
↕
Patient Intelligence
↕
Lead Intelligence
↕
Follow-up
↕
Appointments
↕
Clinic Knowledge
↕
Medical Safety
↕
Facial Intelligence
↕
Staff Copilots
↕
Analytics
↕
Automation

while keeping humans in control.

The goal is not to build a chatbot.

The goal is to build a system that understands what is happening inside a clinic, helps staff act at the right time, reduces repetitive work, improves patient experience, increases legitimate conversion, and continuously turns clinic interactions into useful operational intelligence.

---

# 67. NON-NEGOTIABLE PRODUCT RULES

The following rules must always be respected:

1. Never invent information.
2. Never fabricate prices.
3. Never fabricate appointment availability.
4. Never fabricate medical facts.
5. Never fabricate patient history.
6. Never present AI inference as verified fact.
7. Never expose one clinic's data to another clinic.
8. Never allow AI to silently become the final authority for high-risk medical decisions.
9. Never allow AI-generated knowledge to automatically become authoritative without appropriate validation.
10. Never sacrifice safety for conversion.
11. Never sacrifice correctness for lower AI cost.
12. Never sacrifice privacy for convenience.
13. Never design the entire product around a single AI provider.
14. Never treat Telegram as the definition of the product.
15. Never treat the current repository as the definition of the desired product.
16. Always distinguish target product requirements from current implementation.
17. Always prefer verified data over AI-generated assumptions.
18. Always provide a human escalation path when appropriate.
19. Always preserve auditability for important actions.
20. Always design for future extensibility.

---

# END OF DOCUMENT