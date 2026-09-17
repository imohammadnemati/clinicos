CLINICOS_REMEDIATION_BASELINE.md
1. FINDING REGISTRY
 * F-001
   * Severity: P0
   * Domain: Identity / Tenant Isolation
   * Short title: Fallback to first clinic ID enables cross-tenant data leakage
   * Exact repository path: clinicos-main/utils/role_utils.py
   * Exact symbol/function/class: get_user_clinic_id
   * Observed behavior: If a user is not found in the Staff or Patient tables, the system defaults to querying the first clinic in the database (db.query(Clinic).first()) and returns its ID.
   * Evidence: "Fallback to first clinic" logic implemented inside get_user_clinic_id.
   * Target requirement violated: Tenant Isolation Invariant (Every authenticated request must have an explicit, trusted tenant context).
   * Security/safety/business impact: A new, unknown Telegram user interacting with the bot will be automatically bound to the first registered clinic in the database, polluting that clinic's data and exposing the patient to that clinic's staff.
   * Confidence: HIGH
   * Status: UNSAFE
 * F-002
   * Severity: P0
   * Domain: Medical Safety
   * Short title: Autonomous AI medical prescriptions in Facial Analysis
   * Exact repository path: clinicos-main/handlers/facial_analysis.py
   * Exact symbol/function/class: perform_facial_analysis
   * Observed behavior: The AI prompt explicitly asks the LLM to provide treatment recommendations including "estimated_units" (e.g., Botox units) and "estimated_volume". The result is stored in TreatmentRecommendation and delivered directly to the patient via a generated PDF.
   * Evidence: Prompt instructs: "Provide recommendations... include estimated units/volume if possible".
   * Target requirement violated: Medical Safety Boundaries (AI must not independently prescribe medication or determine treatment eligibility).
   * Security/safety/business impact: Direct patient harm and severe liability due to automated medical prescription without clinical review.
   * Confidence: HIGH
   * Status: UNSAFE
 * F-003
   * Severity: P0
   * Domain: AI Architecture
   * Short title: Active use of FreeLLMAPI instead of Google Gemini
   * Exact repository path: clinicos-main/patient_agent.py
   * Exact symbol/function/class: Module-level initialization
   * Observed behavior: The AI router is instantiated exclusively with FreeLLMAPIProvider. Gemini is not used for runtime execution.
   * Evidence: providers["freellmapi"] = FreeLLMAPIProvider() at the module level.
   * Target requirement violated: CHANGE-001 (Google Gemini is the only AI provider) and CHANGE-002 (FreeLLMAPI is removed).
   * Security/safety/business impact: Violates the foundational architecture mandate, sending potentially sensitive patient data to an unapproved proxy service.
   * Confidence: HIGH
   * Status: CONTRADICTORY
 * F-004
   * Severity: P1
   * Domain: Communication
   * Short title: Hardcoded Telegram API calls bypassing communication layer
   * Exact repository path: clinicos-main/lost_lead_recovery.py
   * Exact symbol/function/class: send_telegram_message
   * Observed behavior: Follow-up messages are dispatched via direct requests.post to the Telegram API.
   * Evidence: requests.post(f"[https://api.telegram.org/bot](https://api.telegram.org/bot){BOT_TOKEN}/sendMessage", ...)
   * Target requirement violated: INVARIANT-011 (Communication remains channel-agnostic).
   * Security/safety/business impact: Prevents multi-channel expansion (Web, SMS, Instagram) and bypasses policy validation and consent checks.
   * Confidence: HIGH
   * Status: CONTRADICTORY
 * F-005
   * Severity: P1
   * Domain: Reliability / Infrastructure
   * Short title: In-memory asynchronous scheduler prevents horizontal scaling
   * Exact repository path: clinicos-main/scheduler.py
   * Exact symbol/function/class: init_scheduler, nightly_jobs
   * Observed behavior: AsyncIOScheduler runs inside the main bot process, holding scheduled jobs in memory without durable storage or distributed locking.
   * Evidence: AsyncIOScheduler() instantiated without a persistent job store.
   * Target requirement violated: Stateless Application Runtime (Horizontal scaling must not cause duplicate executions).
   * Security/safety/business impact: Deploying multiple instances of the bot will cause duplicate nightly jobs, resulting in patients receiving duplicate follow-ups and reminders. Process restarts lose pending jobs.
   * Confidence: HIGH
   * Status: FRAGILE
 * F-006
   * Severity: P1
   * Domain: Knowledge / RAG
   * Short title: Knowledge retrieval relies on simple string matching
   * Exact repository path: clinicos-main/patient_agent.py
   * Exact symbol/function/class: generate_reply
   * Observed behavior: "RAG" is implemented by querying the KnowledgeItem table and checking if k.question_text in question. No embeddings or vector retrieval exist.
   * Evidence: if k.question_text and k.question_text in question: return k.answer_text
   * Target requirement violated: Knowledge System Responsibility (Semantic retrieval, embedding, and evidence assembly).
   * Security/safety/business impact: AI will fail to retrieve critical clinical or clinic knowledge unless exact keywords are used, leading to hallucination or skipped safety protocols.
   * Confidence: HIGH
   * Status: STUB
 * F-007
   * Severity: P1
   * Domain: Architecture / Client
   * Short title: Monolithic Telegram bot couples presentation to domain logic
   * Exact repository path: clinicos-main/bot.py
   * Exact symbol/function/class: Multiple handlers (e.g., appointment_confirm_callback)
   * Observed behavior: Telegram CallbackQueryHandler functions directly instantiate database models (Lead, AppointmentRequest, EscalationLog) and commit transactions.
   * Evidence: appointment_confirm_callback manually creates Lead and executes db.commit().
   * Target requirement violated: Core Platform First (Business logic must remain client-independent).
   * Security/safety/business impact: Developing Phase 2 (Mini App) and Phase 3 (Web/Mobile) is blocked because core domain logic is trapped inside Telegram message handlers.
   * Confidence: HIGH
   * Status: CONTRADICTORY
 * F-008
   * Severity: P1
   * Domain: Security / Authorization
   * Short title: Missing object-level authorization (IDOR risk)
   * Exact repository path: clinicos-main/bot.py
   * Exact symbol/function/class: remove_staff_callback
   * Observed behavior: Deletes a staff record based solely on staff_id from the callback data, without verifying if the executing user has administrative rights over that specific staff_id's clinic.
   * Evidence: staff_id = int(data.split('_')[2]); staff = db.query(Staff).filter_by(id=staff_id).first(); db.delete(staff)
   * Target requirement violated: Authorization (Server-side validation of object ownership).
   * Security/safety/business impact: A malicious user could craft a callback payload to delete staff from other clinics.
   * Confidence: HIGH
   * Status: UNSAFE
2. P0 FORENSIC ANALYSIS
P0 Finding: F-001 (Tenant Isolation Fallback Leak)
Root Entry Point: clinicos-main/bot.py (e.g., main_menu_handler triggered by incoming Telegram message)
↓
Function: get_user_clinic_id(user_id) inside main_menu_handler
↓
Function: get_user_clinic_id in clinicos-main/utils/role_utils.py
↓
Problematic Operation: If Staff query fails and Patient query fails, executes clinic = db.query(Clinic).first(); return clinic.id
↓
Affected Resource: Lead, RawMessage, Session, Patient creation.
↓
Potential Impact: Any unauthenticated/new Telegram user messaging the bot will be automatically anchored to the first Clinic row in the database. Their messages will appear in that clinic's dashboard, and they will interact with that clinic's data, fundamentally breaking multi-tenancy.
P0 Finding: F-002 (Autonomous Medical Prescription)
Root Entry Point: clinicos-main/bot.py (facial_left_photo handler)
↓
Function: perform_facial_analysis in clinicos-main/handlers/facial_analysis.py
↓
Function: _router.generate(analysis_prompt)
↓
Problematic Operation: Prompt instructs LLM: "Provide recommendations (if any) for: 1. Botox... include estimated units/volume...". The resulting JSON is parsed, and TreatmentRecommendation is saved to the database.
↓
Affected Resource: TreatmentRecommendation table and generated PDF (services/pdf_generator.py).
↓
Potential Impact: The AI generates and provides direct medical prescriptions (dosage/units of Botox/filler) directly to the patient without human review, overriding the Medical Safety hierarchy.
P0 Finding: F-003 (Gemini-Only Invariant Violated)
Root Entry Point: clinicos-main/bot.py -> process_patient_message
↓
Function: clinicos-main/patient_agent.py module load
↓
Function: providers["freellmapi"] = FreeLLMAPIProvider()
↓
Problematic Operation: The ProviderManager is instantiated exclusively with the freellmapi provider.
↓
Affected Resource: _router.generate
↓
Potential Impact: All patient data and prompt context is routed to FreeLLMAPI, an unapproved third-party proxy, violating the explicit architecture change set that mandates Google Gemini as the sole provider.
3. TENANT ISOLATION FORENSIC AUDIT
 * Identity Resolution: Handled loosely in bot.py (get_or_create_patient_by_telegram).
 * Clinic Resolution: Determined by get_user_clinic_id. As noted in F-001, this relies on a dangerous fallback.
 * Database Query Enforcements:
   * bot.py show_leads: Uses filter_by(clinic_id=clinic_id). Centralized? No, caller-dependent.
   * bot.py show_appointments: Uses filter(Appointment.clinic_id == clinic_id). Caller-dependent.
   * lost_lead_recovery.py: Queries Lead.pipeline_stage == 'new' globally without looping through tenants securely. Iterates all leads indiscriminately.
   * facial_analysis.py: Assigns clinic_id=patient.clinic_id correctly based on the patient record.
 * Can a caller omit tenant scope? Yes. SQLAlchemy queries are raw and caller-dependent. There is no repository layer enforcing a global tenant filter.
 * Object Ownership Checks: Missing. remove_staff_callback does not check clinic_id.
 * Verdict: Tenant isolation is UNSAFE. It relies entirely on developer discipline in bot.py and is compromised by the role_utils.py fallback.
4. MEDICAL SAFETY FORENSIC AUDIT
 * Flow Trace:
   Telegram Photo Upload
   → facial_analysis.py:handle_photo
   → utils.image_quality.check_image_quality
   → facial_analysis.py:perform_facial_analysis
   → utils.facial_metrics.compute_facial_metrics (Geometric calculation)
   → Prompt generation requesting Botox/Filler units
   → FreeLLMAPIProvider (AI involvement)
   → JSON parsing
   → DB TreatmentRecommendation creation
   → pdf_generator.py:generate_facial_report
   → Sent to patient via update.message.reply_document.
 * Determinations:
   * Describes observed features: YES (computed via metrics).
   * Provides educational information: NO.
   * Suggests possible treatment categories: YES.
   * Recommends a specific treatment: YES.
   * Recommends dosage/units/volume: YES (Prompt explicitly asks for it).
   * Presents treatment as medically necessary: YES (Priority scores assigned).
   * Communicates directly to the patient: YES (Delivered as PDF).
   * Requires physician review: NO (No human-in-the-loop gate before sending).
 * Enforcement Boundary: NONE. There is no gate blocking the generated PDF from reaching the patient.
 * Verdict: UNSAFE.
5. GEMINI-ONLY RUNTIME AUDIT
Execution Path:
Telegram Message → bot.py:process_patient_message → patient_agent.py:generate_reply → _router.generate → ProviderRouter.generate → FreeLLMAPIProvider.generate → external HTTP call.
| Provider | File | Imported | Instantiated | Runtime Reachable | Configured | Target Status | Evidence |
|---|---|---|---|---|---|---|---|
| Gemini | gemini_provider.py | NO | NO | NO | YES (config.py) | REQUIRED | Exists in providers/ but not imported in __init__.py. |
| FreeLLMAPI | freellmapi_provider.py | YES | YES | YES | YES (config.py) | CONTRADICTORY | Exported in __init__.py, instantiated in patient_agent.py. |
| DeepSeek | deepseek_provider.py | NO | NO | NO | NO | DEAD | File exists, completely unreferenced. |
| OpenAI | openai_provider.py | NO | NO | NO | NO | DEAD | File exists, completely unreferenced. |
| OpenRouter | openrouter_provider.py | NO | NO | NO | NO | DEAD | File exists, completely unreferenced. |
| Mistral | mistral_provider.py | NO | NO | NO | NO | DEAD | File exists, completely unreferenced. |
| Cohere | cohere_provider.pu | NO | NO | NO | NO | DEAD | Typo in extension (.pu), unreferenced. |
6. PROVIDER ROUTING AUDIT
 * Trace:
   patient_agent.py initializes ProviderManager(providers={"freellmapi": FreeLLMAPIProvider()}, ...)
   ProviderRouter is injected with this manager.
   ProviderRouter.generate iterates _get_sorted_providers() (which only yields freellmapi) and executes.
 * Does multi-provider runtime routing actually occur? NO. Although the complex routing infrastructure (state_store.py, cost_manager.py, scoring_engine.py, cooldown_manager.py) is fully active and records successes/failures to Redis, it operates on a list of exactly ONE provider (freellmapi).
 * Verdict: LEGACY / DEAD. The routing mechanism is active overhead executing a single-provider loop.
7. TELEGRAM COUPLING AUDIT
| File | Symbol | Telegram Dependency | Business Responsibility | Target Violation | Refactor Priority |
|---|---|---|---|---|---|
| bot.py | appointment_confirm_callback | update.callback_query | Lead creation, DB commits | Business Logic | P1 |
| bot.py | add_staff_confirm | update.message.text | Staff creation, DB commits | Business Logic | P1 |
| lost_lead_recovery.py | send_telegram_message | requests.post | Follow-up delivery | Communication | P1 |
| facial_analysis.py | perform_facial_analysis | update.effective_user | Analysis DB records, File I/O | Business Logic | P2 |
| bot.py | human_handoff | context.bot.send_message | Escalation logic, DB commits | Business Logic | P2 |
8. COMMUNICATION LAYER AUDIT
 * Trace (Patient Message Reply): bot.py:main_menu_handler → patient_agent.py:process_patient_message → update.message.reply_text(answer).
 * Trace (Lost Lead Follow-up): scheduler.py:nightly_jobs → lost_lead_recovery.py:recover_lost_leads → send_telegram_message → requests.post.
 * Stages that exist: Channel Selection (Hardcoded), Telegram API.
 * Stages missing: Policy Validation, Message Composition, Delivery Tracking, Channel Abstraction.
 * Verdict: Bypasses Communication Layer target architecture. Direct HTTP and SDK calls are scattered.
9. FOLLOW-UP / SCHEDULING AUDIT
 * Trace: scheduler.py uses AsyncIOScheduler → executes nightly_jobs → calls recover_lost_leads.
 * Is state persisted? Lead recovery attempts are updated in the DB (lead.recovery_attempts), but the schedule itself is an in-memory cron job.
 * Is execution idempotent? No. If two instances of the bot run, both in-memory schedulers will execute recover_lost_leads simultaneously, pulling the same DB records and dispatching duplicate Telegram requests.
 * What happens after process restart? The cron schedule re-initializes. No pending/missed jobs are recovered.
 * Distributed lock / Outbox? Missing.
 * Verdict: FRAGILE. The implementation cannot safely scale beyond a single instance.
10. AGENT ARCHITECTURE AUDIT
 * Entry Point: patient_agent.py:process_patient_message.
 * Responsibilities Concentrated Here:
   * Identity Resolution: Calls get_or_create_patient.
   * Safety Validation: Hardcoded call to check_medical_risk(raw_text).
   * Business Hours Check: Calls can_auto_reply.
   * Raw Event Storage: Inserts RawMessage to DB.
   * Intent/Context Extraction: Sends FACTS_PROMPT to LLM to extract JSON.
   * State Update: Modifies ConversationState based on JSON.
   * Lead Scoring & Creation: Calculates score, creates Lead, creates AppointmentRequest.
   * Response Generation: Calls LLM again with REPLY_PROMPTS.
   * Outcome Tracking: Hashes response and updates OutcomePattern.
 * Verdict: CONTRADICTORY. Monolithic design violating the orchestrated, tool-based agent architecture defined in the spec.
11. KNOWLEDGE / RAG AUDIT
 * Implementation Found:
   In patient_agent.py:generate_reply:
   knowledge = db.query(KnowledgeItem).filter(...).all()
for k in knowledge:
    if k.question_text and k.question_text in question:
        return k.answer_text

 * Verdict: MISSING TARGET CAPABILITY. This is an exact-substring string match loop. There is no vector database, chunking, embeddings, or retrieval engine present.
12. DATA ARCHITECTURE AUDIT
 * Initialization: Base.metadata.create_all(bind=engine) in database.py. No Alembic or migration scripts exist.
 * Schema Structure: Good use of SQLAlchemy relationships and foreign keys in models.py.
 * Tenant Keys: tenant_id does not exist. Models use clinic_id as the tenant boundary.
 * JSON Fields: Used in Patient.summary_data and ConversationState.missing_information.
 * Structural Risks: Lack of a migration framework (Alembic) means any schema changes currently require dropping tables or manual SQL interventions. Missing database-level constraints for concurrency.
13. AUTHORIZATION / IDOR AUDIT
 * Trace (Privileged operation): bot.py:remove_staff_callback.
   Authentication (Telegram user exists) → Button clicked → ID parsed from callback payload → db.query(Staff).filter_by(id=staff_id).first() → db.delete().
 * Missing Ownership Checks: No validation to ensure the requesting user has OWNER role, nor that the Staff member being deleted belongs to the requester's clinic_id.
 * Verdict: UNSAFE. Severe BOLA/IDOR vulnerability.
14. TESTING AUDIT
 * Directories/Files: NONE found in the manifest.
 * Evidence: The repository lacks a tests/ directory or any .py files containing pytest or unittest fixtures.
 * Verdict: MISSING.
15. DEPLOYMENT / RELIABILITY AUDIT
 * Dockerfile: Standard Python 3.11 slim setup. Exposes 8080.
 * Procfile: worker: python bot.py.
 * Scheduler Process: Running entirely inside the main bot.py execution thread via app.post_init.
 * Risks: Running the Telegram polling mechanism, the ASGI/WSGI webhooks (if activated), and AsyncIOScheduler in a single container makes horizontal scaling dangerous and memory management unpredictable.
16. DEAD / LEGACY CODE CLASSIFICATION
 * llm/providers/deepseek_provider.py: DEAD. Unreferenced in codebase.
 * llm/providers/openai_provider.py: DEAD. Unreferenced in codebase.
 * llm/providers/mistral_provider.py: DEAD. Unreferenced in codebase.
 * llm/providers/openrouter_provider.py: DEAD. Unreferenced in codebase.
 * llm/providers/cohere_provider.pu: DEAD. Unreferenced, invalid extension.
 * llm/provider_router.py: LEGACY. Active but performs routing on a fixed list of 1 provider.
 * llm/scoring_engine.py: LEGACY. Maintains scores for models that are no longer used.
17. DOCUMENTATION VS CODE
| Target Requirement | Specification | Repository Evidence | Status | Evidence Path | Confidence |
|---|---|---|---|---|---|
| Gemini Only | Change Set | FreeLLMAPI used explicitly | CONTRADICTORY | patient_agent.py line 45 | HIGH |
| No Provider Routing | Change Set | ProviderRouter instantiated | LEGACY | patient_agent.py line 56 | HIGH |
| Tenant Isolation | Data & DB | clinic_id fallback to first() | UNSAFE | role_utils.py line 38 | HIGH |
| Medical Safety | Medical Safety | Recommends Botox units via LLM | UNSAFE | facial_analysis.py line 125 | HIGH |
| Client Independence | Target Arch | DB commits inside Telegram handlers | CONTRADICTORY | bot.py | HIGH |
| Channel Agnostic | Communication | Direct requests.post to Telegram | CONTRADICTORY | lost_lead_recovery.py | HIGH |
| RAG | Knowledge | Exact string match on question_text | MISSING | patient_agent.py line 117 | HIGH |
| Durable Scheduler | Automation | AsyncIOScheduler in-memory | FRAGILE | scheduler.py | HIGH |
| Automated Tests | Testing & Quality | No test files present | MISSING | Repository Manifest | HIGH |
18. REMEDIATION DEPENDENCY GRAPH
The remediation must be executed in order, securing the data perimeter before decoupling the architecture.
 * Tenant Isolation & Identity Security (Resolves F-001, F-008)
   ↓
 * Medical Safety & Prompt Governance (Resolves F-002)
   ↓
 * Gemini-Only Provider Alignment (Resolves F-003, cleans up Legacy LLM code)
   ↓
 * Core Service Boundaries & Telegram Decoupling (Resolves F-007, extracts logic from bot.py)
   ↓
 * Communication Layer Abstraction (Resolves F-004)
   ↓
 * Follow-Up / Durable Scheduling (Resolves F-005)
   ↓
 * Knowledge & RAG Implementation (Resolves F-006)
(Note: Adding Tests is a prerequisite continuous step across all phases).
19. P0/P1 REMEDIATION BACKLOG
 * Finding ID: F-001 (Tenant Leakage Fallback)
   * Problem: Unauthenticated users fall back to the first clinic in the DB.
   * Proposed architectural change: Remove the db.query(Clinic).first() fallback. Require explicit clinic assignment (e.g., via invite link, dedicated bot token, or strict unassigned state).
   * Files likely affected: utils/role_utils.py, bot.py.
   * Files explicitly frozen: None for this specific fix.
 * Finding ID: F-002 (Autonomous Medical Prescription)
   * Problem: LLM instructs specific Botox/Filler unit dosages without human review.
   * Proposed architectural change: Remove dosing instructions from the analysis_prompt. Introduce a clinical review flag for aesthetic interpretations before PDF generation.
   * Files likely affected: handlers/facial_analysis.py.
 * Finding ID: F-003 (FreeLLMAPI Active Use)
   * Problem: System routes to FreeLLMAPI, violating Gemini-only architecture.
   * Proposed architectural change: Swap freellmapi_provider.py with gemini_provider.py in llm/providers/__init__.py and patient_agent.py. Remove routing overhead logic.
   * Files likely affected: patient_agent.py, llm/providers/__init__.py.
 * Finding ID: F-008 (Missing IDOR Protection)
   * Problem: Staff deletion relies only on staff_id.
   * Proposed architectural change: Inject clinic_id check into remove_staff_callback matching the executing user's authorized scope.
   * Files likely affected: bot.py.
20. FIRST IMPLEMENTATION PHASE
 * Objective: Secure the Tenant Boundary, enforce Medical Safety, and align the AI Provider to the Architectural Change Set (Gemini Only).
 * Prerequisites: None (this is the foundational fix phase).
 * Exact findings addressed: F-001, F-002, F-003, F-008.
 * Exact files expected to change:
   * clinicos-main/utils/role_utils.py
   * clinicos-main/bot.py
   * clinicos-main/handlers/facial_analysis.py
   * clinicos-main/patient_agent.py
   * clinicos-main/llm/providers/__init__.py
 * Files explicitly frozen: database.py, models.py (No schema changes in Phase 1 to limit risk).
 * Tests required:
   * Unit test verifying get_user_clinic_id returns None or raises an error when a user has no clinic (Tenant Isolation).
   * Unit test verifying remove_staff_callback rejects unauthorized deletion requests.
 * Acceptance criteria:
   * A new user messaging the bot is NOT assigned to Clinic.id = 1 by default.
   * Facial Analysis prompt no longer requests estimated_units or estimated_volume.
   * patient_agent.py initializes the AI layer using GeminiProvider exclusively. FreeLLMAPI is entirely removed from the runtime path.
 * Rollback considerations: Ensure config.py has a valid GEMINI_API_KEY mapping before deployment to prevent immediate AI failure.
21. FINAL SECTION
A. Confirmed P0 findings
 * Tenant Isolation Fallback Leak (get_user_clinic_id fallback).
 * Autonomous Medical Prescriptions in Facial Analysis.
 * Violation of Gemini-Only constraint (Active use of FreeLLMAPI).
B. Confirmed P1 findings
 * Missing Object-Level Authorization (IDOR) on Staff Deletion.
 * In-memory asynchronous scheduling preventing safe scaling.
 * Direct Telegram API calls bypassing a Channel-Agnostic Communication Layer.
 * Complete absence of Automated Testing.
 * Monolithic Telegram bot tightly coupling business logic to presentation.
C. Findings requiring further evidence
 * Webhook security/idempotency (Webhooks currently appear bypassed in favor of polling via Application.builder().run_polling(), but exact production deployment commands are unverified).
D. Legacy components confirmed
 * llm/provider_router.py, llm/scoring_engine.py, llm/cost_manager.py, llm/cooldown_manager.py.
 * All provider files in llm/providers/ except the active one.
E. Missing capabilities
 * Actual RAG / Vector Database implementations.
 * Channel-Agnostic Communication Layer.
 * Durable Background Task Queues.
 * Test Suite.
F. Architectural dependencies
 * Tenant isolation and authorization MUST be fixed before the bot is decoupled into discrete services, as the current coupling hides the lack of secure boundaries.
G. Recommended first implementation phase
 * Phase 1: Foundation & Safety. Focus purely on fixing the P0 Tenant Isolation leak, the P0 Medical Safety prompt, the P1 IDOR vulnerability, and swapping the runtime LLM strictly to Gemini. Do not attempt structural decoupling until the data perimeter and AI compliance are secured.
