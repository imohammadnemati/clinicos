# CLINICOS MASTER VISION
## Master Product Vision & Target Architecture
**Project:** Clinicos  
**Document:** Master Vision  
**Status:** Strategic Source of Truth  
**Purpose:** Define what Clinicos is intended to become  
**Important:** This document defines the target product and engineering direction. It does NOT describe the current implementation state.
---
# 1. WHAT IS CLINICOS?
Clinicos is an AI-native operating system for aesthetic, beauty, dermatology, and cosmetic clinics.
Clinicos is not merely:
- a Telegram chatbot
- an Instagram bot
- an appointment booking system
- a CRM
- a facial-analysis application
- or a generic AI assistant
Clinicos is intended to combine all of these capabilities into one intelligent clinic platform.
The ultimate goal is to create a system that can understand:
- the clinic
- its doctors
- its staff
- its patients
- its leads
- its conversations
- its services
- its knowledge
- its appointments
- its business performance
- and the patient's journey
and use this information to help the clinic acquire, understand, convert, serve, retain, and follow up with patients.
---
# 2. THE CORE IDEA
The central idea behind Clinicos is:
> Turn the clinic's communication, patient data, knowledge, leads, appointments, follow-ups, and AI capabilities into one continuously improving intelligent system.
Clinicos should progressively become the clinic's:
- AI receptionist
- AI secretary
- AI sales assistant
- AI CRM
- AI patient intelligence system
- AI knowledge system
- AI follow-up engine
- AI analytics assistant
- AI clinic copilot
while keeping humans in control whenever human judgment is required.
---
# 3. PRODUCT PHILOSOPHY
Clinicos must be designed around the following principles.
## 3.1 AI-Native
AI is not an optional feature attached to the product.
AI is part of the core architecture.
---
## 3.2 Human-in-the-Loop
Clinicos must never attempt to replace doctors or appropriate human staff.
The system should know when to:
- answer automatically
- ask for more information
- recommend an appointment
- escalate to a human
- notify a secretary
- notify a doctor
- stop making assumptions
---
## 3.3 Patient-Centered
The system should understand the patient journey rather than treating every message as an isolated question.
A patient's:
- previous conversations
- interests
- questions
- concerns
- services of interest
- lead status
- appointment history
- follow-up history
- language
- preferences
- and relevant interactions
should contribute to the overall patient context.
---
## 3.4 Clinic-Specific Intelligence
Every clinic should have its own knowledge and behavior.
The AI must understand:
- clinic services
- prices
- doctors
- treatment protocols
- working hours
- policies
- frequently asked questions
- location
- contact information
- appointment rules
- promotions
- brand voice
Clinicos should not behave like one generic AI for every clinic.
---
## 3.5 Evidence Before Assumption
The AI must distinguish between:
- known facts
- retrieved clinic knowledge
- verified patient information
- inference
- uncertainty
- assumptions
It must never invent clinic policies, prices, medical facts, appointment availability, or patient information.
---
## 3.6 Continuous Improvement
Clinicos should learn from operational data without blindly learning false information.
The system should progressively improve:
- FAQ coverage
- lead classification
- follow-up timing
- response quality
- patient understanding
- clinic knowledge
- conversion intelligence
- workflow automation
---
# 4. TARGET USERS
Clinicos is intended to support four primary roles.
## 4.1 Patient
The patient interacts with the clinic through supported communication channels.
The patient should be able to:
- ask questions
- receive information
- understand services
- request appointments
- communicate concerns
- send images when appropriate
- receive facial-analysis results
- receive follow-ups
- interact in their preferred supported language
---
## 4.2 Secretary
The secretary should have an AI copilot that reduces repetitive work.
The system should help the secretary:
- understand incoming conversations
- identify hot leads
- prioritize follow-ups
- answer repetitive questions
- manage appointments
- review patient history
- receive AI-generated suggestions
- take over conversations
- review AI activity
- recover lost leads
---
## 4.3 Doctor
The doctor should have access to relevant patient intelligence.
The system should help doctors:
- understand patient context
- review relevant conversation history
- review facial-analysis information
- review treatment interests
- receive escalations
- inspect AI-generated summaries
- maintain control over medical decisions
---
## 4.4 Clinic Owner / Manager
The owner should be able to understand and improve clinic operations.
Clinicos should provide:
- lead analytics
- conversion analytics
- appointment analytics
- follow-up analytics
- staff activity insights
- AI performance insights
- weekly reports
- lost-lead insights
- service demand insights
- patient behavior insights
---
# 5. COMMUNICATION CHANNELS
The initial and currently important communication interface is Telegram.
However, the product vision is broader.
Clinicos should be architected so communication channels can evolve independently from the core intelligence layer.
Potential channel architecture includes:
```text
Instagram
Telegram
Website
Other messaging channels
Future communication interfaces
        ↓
Unified Communication Layer
        ↓
Clinicos Intelligence Layer

The system must avoid coupling core business logic directly to one communication platform.

⸻

6. INSTAGRAM / SOCIAL LEAD INTELLIGENCE

One of the major strategic goals of Clinicos is to handle social-media-originated leads.

Instagram is particularly important for aesthetic clinics because patients frequently discover clinics through:

* posts
* reels
* stories
* comments
* direct messages
* advertisements
* profile visits
* educational content

Clinicos should ultimately be capable of turning social interactions into structured leads.

The target system should be able to:

* ingest relevant Instagram interactions where official APIs and permissions allow
* identify potential leads
* understand intent
* classify lead temperature
* extract service interests
* identify questions
* identify objections
* track follow-up status
* connect the interaction to an existing patient
* recommend appropriate responses
* notify a human when needed

Important:

Platform limitations must never be bypassed through unsafe or unofficial methods.

The architecture should isolate social-channel integrations from the core intelligence system.

⸻

7. PATIENT INTELLIGENCE

Patient Intelligence is one of the core Clinicos systems.

The goal is to transform raw interactions into structured patient understanding.

The system should understand:

* identity
* language
* interests
* services of interest
* conversation history
* lead status
* appointment status
* previous appointments
* follow-up status
* questions
* objections
* preferences
* relevant behavioral signals

The patient should not be represented merely as a Telegram user ID.

Clinicos should maintain a persistent patient identity across interactions and channels whenever technically possible and legally appropriate.

⸻

8. IDENTITY RESOLUTION

Clinicos should support identity resolution.

The system should be able to determine when multiple interactions belong to the same patient.

Potential identifiers include:

* platform identity
* phone number
* clinic-specific patient identifier
* verified contact information
* patient aliases

Identity resolution must prioritize correctness and privacy.

Never merge two patients merely because they appear similar.

Ambiguous identity matches should require additional evidence or human confirmation.

⸻

9. LEAD INTELLIGENCE

Every relevant patient interaction can potentially represent a lead.

Clinicos should classify leads using signals such as:

* service interest
* purchase intent
* urgency
* questions about price
* questions about availability
* questions about treatment
* objections
* previous interactions
* appointment intent
* response behavior
* follow-up history

The system should distinguish between:

* cold lead
* warm lead
* hot lead
* converted lead
* lost lead
* inactive lead
* returning patient

Lead scoring must be explainable.

The system should be able to explain why a lead was classified as high priority.

⸻

10. HOT LEAD DETECTION

Clinicos should identify high-conversion-potential leads.

Examples of hot-lead signals include:

* explicit intent to book
* asking for available appointment times
* asking for exact pricing before booking
* asking about treatment availability
* requesting doctor information
* sending required information
* responding positively to a follow-up
* repeatedly engaging with treatment-related information

Hot leads should be surfaced to clinic staff.

The system should support configurable thresholds and clinic-specific behavior.

⸻

11. LEAD TRACKER

Clinicos should maintain a structured Lead Tracker.

Each lead should be associated with relevant information such as:

* patient
* source
* service
* intent
* temperature
* status
* assigned staff member
* last interaction
* next action
* follow-up status
* conversion status
* lost reason when known

The goal is to ensure that leads do not disappear inside chat histories.

⸻

12. FOLLOW-UP ENGINE

One of the most important Clinicos capabilities is automated intelligent follow-up.

The system should identify when a patient requires follow-up.

Examples:

* patient asked about a treatment but did not book
* patient requested a price and disappeared
* patient showed high purchase intent
* patient started an appointment flow but abandoned it
* patient received information but did not respond
* patient previously expressed interest
* patient may need post-appointment follow-up

Follow-up timing should not be purely fixed.

The system should eventually learn appropriate timing based on:

* patient behavior
* lead temperature
* service
* previous response patterns
* clinic configuration

Follow-ups must respect:

* clinic working hours
* patient experience
* opt-out preferences
* platform policies
* appropriate communication frequency

⸻

13. LOST LEAD RECOVERY

Clinicos should actively identify lost or abandoned opportunities.

The system should answer questions such as:

* Which leads stopped responding?
* Why did they stop?
* Which services generate the most lost leads?
* Which leads are worth recovering?
* When should they be contacted?
* What message should be sent?

Lost Lead Recovery should generate actionable recommendations rather than simply reporting statistics.

⸻

14. FAQ INTELLIGENCE

Clinicos should maintain an intelligent clinic FAQ system.

Instead of relying only on manually written FAQs, the system should analyze real patient conversations and identify:

* frequently asked questions
* unanswered questions
* ambiguous answers
* outdated information
* new recurring questions
* common objections
* service misunderstandings

The system should be capable of recommending new FAQ entries.

Potential workflow:

Patient conversations
        ↓
Question extraction
        ↓
Clustering
        ↓
Frequency analysis
        ↓
Knowledge candidate
        ↓
Human verification
        ↓
Clinic Knowledge Base

AI-generated knowledge should not automatically become authoritative clinic policy without appropriate validation.

⸻

15. CLINIC KNOWLEDGE BASE

Each clinic should have a dedicated knowledge layer.

Knowledge may include:

* services
* treatment descriptions
* pricing
* doctor profiles
* clinic policies
* working hours
* location
* preparation instructions
* aftercare information
* FAQs
* promotions
* contraindications approved by the clinic
* operational rules

The AI should retrieve clinic-specific knowledge before answering clinic-specific questions.

⸻

16. SECRETARY COPILOT

Secretary Copilot is a major product feature.

It should help the secretary perform repetitive and cognitively expensive tasks.

Potential capabilities:

* summarize patient conversation
* suggest response
* classify lead
* suggest next action
* identify missing information
* recommend follow-up
* identify urgent escalation
* retrieve clinic knowledge
* show patient history
* prepare appointment information
* detect hot leads
* recover lost leads
* draft personalized messages

The secretary must remain able to review and modify AI suggestions.

⸻

17. HUMAN TAKEOVER

Clinicos must support explicit human takeover.

When a human takes control:

* AI should stop responding automatically where appropriate
* conversation ownership should become clear
* staff should know the current state
* the AI should preserve context
* the system should record the handoff

Human takeover should be available for:

* medical questions requiring professional judgment
* complaints
* sensitive situations
* high-value patients
* uncertain AI responses
* explicit patient requests
* operational exceptions

⸻

18. APPOINTMENT ENGINE

Clinicos should provide intelligent appointment functionality.

Capabilities should include:

* appointment requests
* availability handling
* scheduling
* rescheduling
* cancellation
* reminders
* appointment status
* doctor/service association
* patient association
* staff visibility

The AI must never claim that an appointment is available unless availability is actually verified.

⸻

19. MEDICAL SAFETY LAYER

Clinicos operates in a healthcare-related domain.

A dedicated medical-safety layer is required.

The system must distinguish:

Administrative information
        ↓
General educational information
        ↓
Treatment-related information
        ↓
Potential medical advice
        ↓
High-risk medical situations

Higher-risk situations should trigger stronger safeguards and potentially human escalation.

Clinicos must not:

* fabricate diagnoses
* guarantee outcomes
* fabricate contraindications
* invent medication instructions
* replace professional medical evaluation
* present uncertain AI output as confirmed medical fact

⸻

20. MULTILINGUAL INTELLIGENCE

Clinicos should support multilingual conversations.

Current target languages include:

* Persian
* English
* Azerbaijani Turkish
* Arabic
* Turkish

Language detection should happen automatically where possible.

The system should preserve the patient’s preferred language throughout the conversation.

Translation must not destroy medical meaning or clinic-specific terminology.

⸻

21. AI / LLM ARCHITECTURE

Clinicos should use an abstraction layer between business logic and LLM providers.

The application should not directly couple every feature to one specific model.

Target architecture:

Clinicos AI Services
        ↓
LLM Abstraction Layer
        ↓
LLM Gateway / Provider
        ↓
Model(s)

⸻

22. FREELLMAPI

FreeLLMAPI is the current reference LLM gateway/provider architecture for Clinicos.

The intended role of FreeLLMAPI is to provide a unified interface between Clinicos and underlying AI models/providers.

Conceptually:

Clinicos
    ↓
FreeLLMAPI
    ↓
Underlying AI model/provider
    ↓
Response

The key architectural benefit is that Clinicos business logic should remain as independent as possible from the underlying model vendor.

FreeLLMAPI should therefore be treated as the current reference AI gateway.

However:

The architecture must remain modular enough that the LLM gateway can evolve in the future without rewriting the entire product.

⸻

23. AI PROVIDER ABSTRACTION

The system should support provider abstraction.

The application should be able to evolve between:

* FreeLLMAPI
* direct providers
* multiple model providers
* specialized vision providers
* specialized embedding providers
* future AI services

without coupling the entire codebase to one provider.

Provider-specific logic belongs in the provider/integration layer.

Business logic should depend on stable application-level interfaces.

⸻

24. MODEL ROUTING

Future Clinicos architecture may use intelligent model routing.

Different tasks may require different models.

Examples:

* simple FAQ → inexpensive/fast model
* complex reasoning → stronger model
* vision → vision-capable model
* summarization → efficient model
* classification → lightweight model
* medical-safety evaluation → dedicated safety workflow

Routing should optimize:

* quality
* latency
* reliability
* cost
* availability

Routing must never sacrifice safety merely to reduce cost.

⸻

25. MULTI-AGENT ARCHITECTURE

Clinicos may evolve into a multi-agent system.

Possible specialized agents include:

* Patient Agent
* Lead Agent
* Follow-up Agent
* Appointment Agent
* Knowledge Agent
* Secretary Agent
* Medical Safety Agent
* Analytics Agent
* Facial Analysis Agent
* Reporting Agent

Agents should not operate as uncontrolled independent chatbots.

They should communicate through defined interfaces and shared state.

A central orchestration layer should coordinate them.

⸻

26. AGENT ORCHESTRATION

Target architecture:

                    Clinicos Orchestrator
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
 Patient Agent         Lead Agent        Appointment Agent
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ↓
                    Shared Patient Context
                            ↓
                     Knowledge Layer
                            ↓
                      LLM Gateway

The exact agent architecture should evolve based on actual product complexity.

Do not introduce agents merely for architectural fashion.

⸻

27. AI MEMORY AND CONTEXT

Clinicos should distinguish between:

* conversation context
* patient memory
* clinic knowledge
* operational state
* analytics data

AI memory must be controlled.

The system should never blindly store every model-generated statement as permanent truth.

Important facts should have provenance and appropriate confidence.

⸻

28. KNOWLEDGE LEARNING

Clinicos should progressively improve its clinic-specific knowledge.

Potential pipeline:

Conversation
    ↓
Extract candidate knowledge
    ↓
Validate
    ↓
Classify
    ↓
Store
    ↓
Retrieve in future conversations

The system should avoid self-learning loops where hallucinated information becomes permanent knowledge.

⸻

29. FACIAL ANALYSIS

Facial analysis is a strategic Clinicos capability.

The goal is to allow a patient to provide a facial image and receive an AI-assisted analysis experience that can increase:

* patient engagement
* treatment understanding
* lead conversion
* personalization
* clinic value

The system should use computer vision infrastructure such as MediaPipe for facial landmark detection and measurement.

⸻

30. FACIAL ANALYSIS PIPELINE

Target workflow:

Patient
   ↓
Facial Analysis Request
   ↓
Instruction / Consent / Safety
   ↓
Image Upload
   ↓
Image Quality Check
   ↓
Quality Retry if Needed
   ↓
Face Detection
   ↓
Facial Landmarks
   ↓
Facial Metrics
   ↓
AI Interpretation
   ↓
Treatment-oriented Suggestions
   ↓
Patient-friendly Result
   ↓
Optional Visualization
   ↓
Optional PDF Report
   ↓
Lead / Follow-up Intelligence

⸻

31. IMAGE QUALITY SYSTEM

Before facial analysis, the system should verify image quality.

Potential checks include:

* face visibility
* lighting
* blur
* framing
* resolution
* face orientation
* obstruction
* number of faces

If quality is insufficient, the system should explain what is wrong and request another image.

The retry experience should be user-friendly.

⸻

32. FACIAL LANDMARKS AND METRICS

MediaPipe can be used to identify facial landmarks.

The system may derive structured metrics from landmarks.

Potential measurements include:

* facial proportions
* symmetry-related measurements
* distances
* ratios
* geometric relationships

Measurements must be treated as quantitative image-derived observations rather than definitive medical diagnoses.

⸻

33. FACIAL ANALYSIS INTERPRETATION

AI interpretation may translate measurements into understandable patient-facing observations.

The system should avoid:

* diagnosing disease from a photograph
* making definitive medical claims
* guaranteeing cosmetic outcomes
* pretending that an image alone provides complete clinical assessment

Results should clearly remain assistive/informational.

⸻

34. TREATMENT RECOMMENDATION

Facial analysis may generate treatment-oriented suggestions.

Recommendations must be:

* cautious
* explainable
* based on available information
* non-definitive
* appropriate for human review where needed

The system should ideally connect observations to relevant clinic services without pretending to perform a complete medical consultation.

⸻

35. FACIAL ANALYSIS USAGE POLICY

The intended product policy is:

Standard patient

One free facial analysis during their lifetime.

Doctor / Admin / authorized clinic roles

Unlimited or role-configured access according to clinic policy.

The exact limits must be configurable.

Usage must be tracked reliably.

The system should prevent accidental duplicate consumption.

⸻

36. FACIAL ANALYSIS REPORT

The system should be able to generate a patient-friendly PDF report.

Potential contents:

* analysis summary
* facial measurements
* observations
* visualizations
* treatment-oriented suggestions
* disclaimers
* clinic branding
* patient information where appropriate

PDF generation should support multilingual output, including RTL languages.

⸻

37. FACIAL ANALYSIS VISUALIZATION

Where technically and ethically appropriate, Clinicos should support visual presentation of analysis.

Potential features:

* landmark visualization
* measurement overlays
* facial regions
* before/after comparison
* structured result cards

Visualizations must accurately represent what was actually measured.

Never fabricate visual analysis.

⸻

38. BEFORE / AFTER SYSTEM

Clinicos should support before/after comparison for applicable treatments.

Potential functionality:

* store before image
* store after image
* associate images with patient/treatment
* compare relevant metrics
* display visual differences
* generate reports

Image comparison must respect patient privacy and consent.

⸻

39. AGING SIMULATION

A future capability may include aging simulation or textual age-related prediction.

This must be treated as an estimate/simulation rather than a factual prediction.

The system must clearly distinguish:

* simulation
* prediction
* measurement
* medical fact

⸻

40. VISION AI

Clinicos should be capable of incorporating vision-capable AI models where available.

Vision may be used for:

* facial image understanding
* image quality assistance
* visual interpretation
* document/image understanding
* future clinic workflows

Vision should remain behind an abstraction layer rather than becoming hard-coded into the patient agent.

⸻

41. PRICING INTELLIGENCE

Clinicos should eventually assist clinics with pricing-related interactions.

Potential capabilities:

* retrieve current clinic pricing
* answer pricing questions
* compare service packages
* explain what affects price
* identify price-sensitive leads
* suggest appropriate next actions

The system must never invent prices.

Prices must come from authoritative clinic configuration or verified knowledge.

⸻

42. CONVERSION INTELLIGENCE

Clinicos should optimize the complete journey:

Attention
 ↓
Interaction
 ↓
Question
 ↓
Interest
 ↓
Lead
 ↓
Qualified Lead
 ↓
Hot Lead
 ↓
Appointment
 ↓
Visit
 ↓
Treatment
 ↓
Follow-up
 ↓
Retention

The system should identify where patients drop out.

It should help the clinic improve conversion at each stage.

⸻

43. A/B TESTING

Clinicos should eventually support experimentation.

Possible experiments:

* response wording
* follow-up timing
* CTA
* educational message
* offer presentation
* lead recovery strategy
* appointment prompts

A/B testing should measure actual outcomes.

The system must avoid claiming that one strategy is better without sufficient data.

⸻

44. ANALYTICS

Clinicos should provide operational and AI analytics.

Important metrics may include:

* leads
* qualified leads
* hot leads
* appointments
* conversion rate
* response time
* follow-up completion
* lost leads
* recovered leads
* service demand
* AI response quality
* human takeover rate
* patient engagement
* facial-analysis usage
* facial-analysis-to-lead conversion

⸻

45. WEEKLY REPORT

Clinicos should provide an automated weekly report.

The report should summarize:

* lead volume
* lead quality
* hot leads
* appointments
* conversions
* lost leads
* recovered leads
* top patient questions
* unanswered questions
* service demand
* staff activity
* AI performance
* recommended actions

The goal is not just reporting.

The report should answer:

“What should the clinic do next week to improve?”

⸻

46. AI PERFORMANCE MONITORING

Clinicos should eventually monitor its own AI performance.

Possible metrics:

* successful responses
* failed responses
* escalation rate
* human correction rate
* hallucination reports
* unanswered questions
* response latency
* token usage
* cost
* lead conversion impact

AI performance should be evaluated using measurable outcomes rather than subjective claims.

⸻

47. COST OPTIMIZATION

AI infrastructure should be cost-aware.

The system should optimize:

* model selection
* prompt length
* context size
* caching
* retrieval
* repeated requests
* unnecessary model calls

However:

Cost optimization must never compromise patient safety or critical correctness.

⸻

48. VOICE NOTES — FUTURE CAPABILITY

Voice interaction is a future capability.

The system may eventually support:

* patient voice messages
* secretary voice messages
* voice transcription
* voice understanding
* voice-to-text workflow
* future voice responses

Potential technologies may include external STT services.

Voice must remain modular and must not complicate the core product architecture unnecessarily.

⸻

49. NOTIFICATION SYSTEM

Clinicos should eventually support intelligent notifications.

Examples:

* hot lead detected
* urgent escalation
* appointment request
* missed follow-up
* lost lead
* high-value patient
* facial analysis completed
* human takeover required
* system failure

Notifications should be configurable by role.

⸻

50. PATIENT PRIORITIZATION

Clinicos should be capable of prioritizing patients based on business and operational signals.

Potential categories:

* VIP
* hot lead
* urgent
* follow-up required
* inactive
* returning patient
* high-value patient

Prioritization must be explainable and configurable.

⸻

51. PRIVACY AND DATA PROTECTION

Clinicos handles sensitive patient-related information.

The architecture must prioritize:

* data minimization
* access control
* role-based permissions
* encryption where appropriate
* secure secrets management
* auditability
* safe logging
* patient privacy
* image privacy
* controlled data retention

Patient images must receive additional protection.

⸻

52. SECURITY

Security is a first-class requirement.

The system must protect:

* authentication tokens
* API keys
* database credentials
* patient information
* facial images
* clinic information
* staff information

Never expose secrets in:

* Git
* logs
* AI prompts
* Notebook sources
* public documentation
* error messages

⸻

53. SCALABILITY

Clinicos should eventually support multiple clinics.

The architecture should be multi-tenant.

A clinic’s:

* patients
* staff
* knowledge
* pricing
* services
* conversations
* analytics
* AI configuration

must remain isolated from other clinics.

No clinic should accidentally access another clinic’s data.

⸻

54. MULTI-TENANT AI

AI context must be clinic-specific.

For every AI request, the system should understand the appropriate:

* clinic
* patient
* role
* language
* conversation
* knowledge
* permissions

Cross-clinic knowledge leakage is unacceptable.

⸻

55. CONFIGURABILITY

Clinics should eventually be able to configure:

* services
* prices
* doctors
* working hours
* staff
* AI tone
* escalation rules
* follow-up rules
* lead thresholds
* language behavior
* facial-analysis settings
* notification rules

The system should avoid hard-coding clinic-specific behavior.

⸻

56. OBSERVABILITY

Clinicos should be observable in production.

Important signals:

* application errors
* API errors
* LLM errors
* latency
* database errors
* Redis errors
* queue/scheduler errors
* failed workflows
* Telegram errors
* image-processing errors
* PDF generation errors

Critical workflows should have traceable logs.

Logs must not expose sensitive patient data unnecessarily.

⸻

57. RELIABILITY

Clinicos should be designed for graceful failure.

If the LLM is unavailable:

* the system should fail safely
* it should not fabricate answers
* appropriate fallback behavior should occur
* critical actions should not be falsely confirmed

If the database is unavailable:

* the system must not pretend data was saved

If appointment availability cannot be verified:

* the system must not claim availability

If facial analysis fails:

* the patient should receive a clear explanation and appropriate retry/fallback behavior

⸻

58. ARCHITECTURAL MODULARITY

The system should be divided into logical modules.

Potential major domains:

Identity
Patient Intelligence
Conversation
Lead Management
Follow-up
Appointments
Knowledge
Medical Safety
AI / LLM
Facial Analysis
Notifications
Analytics
Reporting
Authentication
Clinic Management

Each domain should have clear responsibilities.

Avoid creating a single giant module containing unrelated business logic.

⸻

59. EVENT-DRIVEN EVOLUTION

As Clinicos grows, important events should be represented explicitly.

Examples:

lead.created
lead.updated
lead.became_hot
appointment.requested
appointment.booked
appointment.cancelled
followup.required
followup.completed
human_takeover.started
facial_analysis.started
facial_analysis.completed
patient.returned
knowledge_candidate.created

This can enable future automation without tightly coupling every module.

⸻

60. FUTURE AUTOMATION ENGINE

Clinicos should eventually support rule-based and AI-assisted automation.

Example:

IF
patient shows high intent
AND
appointment not booked
AND
follow-up allowed
THEN
create follow-up task
AND
notify secretary
AND
recommend personalized message

Automation must remain configurable and auditable.

⸻

61. PRODUCT EXPERIENCE

Clinicos should feel:

* intelligent
* fast
* professional
* trustworthy
* personalized
* simple
* human

AI should not make the product feel robotic.

The system should minimize unnecessary questions.

It should remember relevant context.

⸻

62. AI PERSONALITY

The exact communication style may vary by clinic.

However, default behavior should be:

* professional
* friendly
* concise when appropriate
* clear
* empathetic
* non-manipulative
* medically cautious

The system should never pressure patients into treatment.

⸻

63. LEAD CONVERSION WITHOUT MANIPULATION

Clinicos is intended to improve conversion.

However, conversion must not rely on:

* deception
* fabricated urgency
* fake scarcity
* false medical claims
* manipulation
* fear-based selling

The goal is:

Help the right patient make an informed decision and help the clinic avoid losing legitimate opportunities.

⸻

64. PROJECT DEVELOPMENT PHILOSOPHY

Clinicos should be developed toward the target architecture, not merely patched indefinitely around historical implementation decisions.

When the current code conflicts with the target architecture:

1. Identify the conflict.
2. Explain it.
3. Determine whether migration is necessary.
4. Preserve working functionality where possible.
5. Refactor incrementally.
6. Test after each significant change.

Do not blindly preserve bad historical architecture simply because it already exists.

⸻

65. AI CODING ASSISTANT ROLE

Any AI coding assistant working on Clinicos should act as:

* Senior Software Architect
* Senior Backend Engineer
* Senior AI Engineer
* Product Engineer
* Security Reviewer
* Database Reviewer
* Code Reviewer
* Testing Engineer
* Architecture Guardian

The AI assistant must not behave like a blind code generator.

⸻

66. REQUIRED AI DEVELOPMENT PROCESS

Before implementing a significant feature:

Understand the requirement
        ↓
Inspect current code
        ↓
Inspect related architecture
        ↓
Identify constraints
        ↓
Compare current state with target vision
        ↓
Design solution
        ↓
Explain trade-offs
        ↓
Implement
        ↓
Test
        ↓
Review
        ↓
Verify

⸻

67. NO HALLUCINATION POLICY

The AI assistant must never invent:

* files
* functions
* classes
* APIs
* database tables
* environment variables
* dependencies
* deployment states
* test results
* external service capabilities

If information is missing:

Say that it is missing.

If something has not been tested:

Say that it has not been tested.

If something is an assumption:

Label it as an assumption.

⸻

68. FACT / INFERENCE / HYPOTHESIS

When ambiguity exists, the AI should distinguish:

FACT

Verified from the repository, database, documentation, or actual test.

INFERENCE

Strongly implied but not directly verified.

HYPOTHESIS

Possible explanation that requires verification.

ASSUMPTION

Temporary assumption required to proceed.

This distinction is especially important for debugging and architecture decisions.

⸻

69. CHANGE MANAGEMENT

Every significant architecture change should document:

* Why the change is needed
* What problem it solves
* What alternatives were considered
* What files/modules are affected
* What risks exist
* How migration will occur
* How it will be tested

⸻

70. CURRENT IMPLEMENTATION VS TARGET VISION

This distinction is critical.

The current repository may contain:

* incomplete features
* temporary architecture
* legacy code
* technical debt
* experimental features
* abandoned providers
* partially implemented systems

None of these automatically define the final Clinicos product.

The target vision defined in this document represents the intended destination.

The actual repository represents the current starting point.

The engineering task is to intelligently bridge the two.

⸻

71. PRIORITY ORDER

When deciding what to build next, consider:

1. Patient safety
2. Data security
3. Core product correctness
4. Reliability
5. Patient experience
6. Clinic operational value
7. Lead conversion value
8. Scalability
9. Cost efficiency
10. Nice-to-have features

⸻

72. FINAL PRODUCT VISION

The ultimate Clinicos experience should look conceptually like this:

                    ┌─────────────────────────┐
                    │        CLINICOS         │
                    │  AI Clinic OS           │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
       Patient AI          Clinic Copilot       Management AI
             │                   │                   │
             ▼                   ▼                   ▼
      Patient Intelligence   Secretary AI       Analytics
      Lead Intelligence      Doctor Support     Weekly Reports
      Follow-up              Human Takeover     KPIs
      Appointments            Knowledge          Insights
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   CLINICOS AI LAYER    │
                    │                         │
                    │ LLM / Agents / Vision  │
                    │ Knowledge / Safety     │
                    │ Orchestration / Memory │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     FREE LLM API        │
                    │   Reference AI Gateway  │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               ▼                 ▼                 ▼
             LLMs             Vision            Future AI

⸻

73. THE FINAL GOAL

Clinicos should eventually become a system where a clinic does not merely “use an AI chatbot.”

Instead:

The clinic has an intelligent digital operating layer that understands its patients, conversations, leads, appointments, knowledge, staff workflows, and business performance.

The AI should continuously help the clinic:

Acquire patients
      ↓
Understand patients
      ↓
Qualify leads
      ↓
Convert leads
      ↓
Book appointments
      ↓
Support patients
      ↓
Assist staff
      ↓
Support doctors
      ↓
Follow up
      ↓
Recover lost opportunities
      ↓
Analyze performance
      ↓
Improve the clinic

That is the ultimate destination of Clinicos.

⸻

74. MASTER RULE

When developing Clinicos, always ask:

“Does this change move Clinicos closer to the intended product, or does it merely patch the current implementation?”

Prefer solutions that move the system toward the intended architecture while maintaining production stability.

The goal is not to preserve the past.

The goal is to build the best version of Clinicos.

⸻

END OF CLINICOS MASTER VISION