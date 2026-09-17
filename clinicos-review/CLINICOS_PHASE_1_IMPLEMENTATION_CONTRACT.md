CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT.md
1. SCOPE
Phase 1 addresses ONLY the following high-priority forensic findings:
 * F-001 — Tenant Isolation Fallback
 * F-002 — Medical Safety Boundary in Facial Analysis
 * F-003 — Gemini-Only Runtime
 * F-008 — Object-Level Authorization / IDOR
The following components and capabilities will NOT be implemented or redesigned in Phase 1:
 * Communication Layer abstraction
 * Durable Scheduler implementation (Celery/RQ)
 * Knowledge/RAG system implementation
 * Full Agent Orchestrator refactoring
 * Telegram decoupling from business domains
 * Web/Mobile client APIs
 * Database migration framework (Alembic setup)
 * Major database schema redesigns
==================================================
2. REPOSITORY INSPECTION
F-001 (Tenant Isolation Fallback):
 * utils/role_utils.py: get_user_clinic_id currently queries Staff, then Patient. If both fail, it executes clinic = db.query(Clinic).first() and returns clinic.id.
 * bot.py: get_or_create_patient_by_telegram uses the exact same fallback: clinic = db.query(Clinic).first().
 * Callers of get_user_clinic_id: language_callback, main_menu_handler, appointment_confirm_callback, add_staff_confirm, show_staff_list, show_remove_staff, remove_staff_callback inside bot.py.
 * All these callers blindly accept the returned clinic_id and use it to query or create resources.
F-002 (Medical Safety Boundary):
 * handlers/facial_analysis.py: perform_facial_analysis uses an LLM prompt that explicitly requests: "Provide recommendations... include estimated units/volume if possible".
 * Model: TreatmentRecommendation contains estimated_units and estimated_volume.
 * PDF Generation: services/pdf_generator.py safely checks if rec.get('estimated_units'): before appending it to the PDF string.
F-003 (Gemini-Only Runtime):
 * patient_agent.py: Instantiates ProviderManager(providers={"freellmapi": FreeLLMAPIProvider()}).
 * llm/providers/__init__.py: Only exports FreeLLMAPIProvider.
 * llm/providers/gemini_provider.py: Exists and is fully implemented, importing GEMINI_API_KEY from config.
 * Abstraction: ProviderRouter.generate handles execution dynamically over the registered providers.
F-008 (Object-Level Authorization / IDOR):
 * bot.py: remove_staff_callback extracts staff_id from the callback payload and directly deletes the Staff record.
 * bot.py: add_staff_confirm creates new staff using the executing user's clinic_id but lacks a strict check to verify if the executing user has the OWNER role.
==================================================
3. F-001 IMPLEMENTATION CONTRACT
1. What is the current identity resolution flow?
Users are looked up in the Staff table, then the PatientAlias/Patient tables.
2. What trusted tenant context currently exists?
A user's presence in the Staff or Patient table provides a deterministic clinic_id.
3. What happens when tenant context is missing?
The system currently assigns the user to the very first Clinic record found in the database.
4. Which callers depend on get_user_clinic_id returning a clinic?
Multiple bot.py handlers, including add_staff_confirm, remove_staff_callback, appointment_confirm_callback, and main_menu_handler.
5. What return type or exception behavior is safest?
get_user_clinic_id must return Optional[int] (i.e., None if no trusted context is found) instead of falling back to a default clinic. get_or_create_patient_by_telegram must similarly fail or return None if a clinic association cannot be securely determined.
6. Which downstream functions must handle an unassigned user?
All caller handlers in bot.py.
7. What patient-facing behavior should occur when tenant context is missing?
The bot must refuse tenant-bound operations and present a safe fallback message (e.g., "You are not associated with any clinic. Please contact your clinic administrator.")
8. Can an unknown user access any clinic data?
Currently, yes. Under this contract, NO.
9. Can an unknown user create tenant-owned records?
Currently, yes. Under this contract, NO.
10. What exact invariant will be enforced?
NO TRUSTED TENANT → NO TENANT-OWNED OPERATION.
==================================================
4. F-008 AUTHORIZATION CONTRACT
For remove_staff_callback (and by extension add_staff_confirm), the following authorization chain must be enforced:
Authentication (Telegram User ID)
→ Actor Identity (Resolved via Staff table)
→ Actor Role (Verified via get_user_role)
→ Actor Tenant (Verified via get_user_clinic_id)
→ Target Resource (Staff record to be deleted)
→ Target Resource Tenant (staff.clinic_id)
→ Ownership Match (Actor Tenant == Target Resource Tenant)
→ Authorization Decision (Actor Role == 'owner' AND Ownership Match == True)
→ Mutation (db.delete(staff))
Specifications:
 * Required role: owner.
 * Required clinic_id relationship: The executing owner's clinic_id must exactly match the target staff's clinic_id.
 * Exact rejection behavior: If unauthorized, the operation must return a standard localized error message (e.g., "Unauthorized action.") and abort the database transaction.
 * Fail closed: Yes. If any parameter is missing (staff_id, clinic_id, role), the operation is rejected.
 * Audit event: Missing in current implementation. Phase 1 will not implement a full Audit Log system but will add standard logger.warning events for unauthorized access attempts.
 * Centralized authorization helper: Phase 1 will implement the checks directly in the respective handlers to avoid expanding scope, as a centralized authorization layer does not yet exist.
==================================================
5. F-002 MEDICAL SAFETY CONTRACT
Boundary Definition:
The AI facial analysis must be strictly limited to visual/structural observation and educational interpretation. It MUST NOT provide dosage, units, volume, prescription-like instructions, or definitive treatment eligibility.
Phase 1 Contract:
 * Autonomous AI Output: The analysis_prompt in handlers/facial_analysis.py will be modified to remove the request for "estimated units/volume if possible". It will be explicitly instructed not to provide dosages or units.
 * Database Model: The estimated_units and estimated_volume fields in the TreatmentRecommendation model (models/facial_models.py) will remain FROZEN for Phase 1 to preserve backward compatibility and avoid database migrations. The application will simply stop populating them.
 * Patient-Facing Report: The services/pdf_generator.py already handles missing units/volume safely (if rec.get('estimated_units'):). No changes are required to the PDF generator.
 * Physician Review: Not implemented in the current repository. Phase 1 will not build a new UI for physician review, but will enforce the safety boundary at the prompt/AI generation level.
==================================================
6. F-003 GEMINI-ONLY IMPLEMENTATION CONTRACT
Target Architecture Check:
Clinicos Core Platform → Clinicos AI Layer → Gemini Adapter → Google Gemini API.
Current Abstraction:
The repository maintains an internal abstraction via BaseLLMProvider, ProviderManager, and ProviderRouter.
Phase 1 Architecture Contract:
 * Gemini Only: patient_agent.py will instantiate ProviderManager exclusively with the GeminiProvider.
 * FreeLLMAPI Unreachable: FreeLLMAPIProvider will be removed from the instantiation payload and will not be exported by llm/providers/__init__.py.
 * No Fallback/Routing: ProviderRouter will continue to exist to satisfy the application's API expectation (_router.generate), but it will iterate over a list containing exactly one provider (Gemini).
 * Abstraction Intact: ProviderManager and ProviderRouter will be FROZEN and retained to prevent deep refactoring of patient_agent.py and facial_analysis.py.
 * Isolation: Gemini-specific generation logic remains securely isolated within llm/providers/gemini_provider.py.
==================================================
7. GEMINI CONFIGURATION CONTRACT
Inspection:
config.py exports GEMINI_API_KEY and PROVIDER_MODELS.
Contract:
 * Required configuration: GEMINI_API_KEY must be present.
 * Optional configuration: GEMINI_MAX_TOKENS and GEMINI_MODEL (defaults provided in code).
 * Startup validation: The startup_diagnostics function in bot.py must validate the presence of GEMINI_API_KEY.
 * Failure behavior: If GEMINI_API_KEY is missing, startup_diagnostics must log a CRITICAL error and the bot should safely reject AI-dependent requests at runtime (returning safe fallback messages) rather than crashing the polling process.
 * Secret Logging: API keys MUST NOT be logged during diagnostics or error handling.
==================================================
8. CROSS-FINDING DEPENDENCIES
 * F-001 & F-008 (Tenant Isolation & Authorization): F-001 MUST be completed before F-008. remove_staff_callback depends on a trustworthy get_user_clinic_id to verify ownership. If F-001 is not fixed, the authorization check in F-008 could be spoofed by the fallback mechanism.
 * F-003 & F-002 (Gemini & Medical Safety): These are independent of the identity flows. Changing patient_agent.py to use Gemini (F-003) does not alter the medical safety prompt inside facial_analysis.py (F-002). They can be implemented sequentially.
==================================================
9. EXACT FILE CHANGE PLAN
| File | Expected Change | Reason | Finding | Risk | Required? |
|---|---|---|---|---|---|
| utils/role_utils.py | Remove db.query(Clinic).first() fallback. Return None if no record. | Prevent cross-tenant data leakage for unauthenticated users. | F-001 | MED | YES |
| bot.py | Add None handling for clinic_id. Enforce authorization in staff mutation callbacks. | Handle safe fallback for F-001; enforce IDOR protection. | F-001, F-008 | HIGH | YES |
| handlers/facial_analysis.py | Remove unit/volume requests from analysis_prompt. | Prevent AI from issuing autonomous medical prescriptions. | F-002 | LOW | YES |
| patient_agent.py | Swap FreeLLMAPIProvider instantiation with GeminiProvider. | Comply with Gemini-only target runtime. | F-003 | LOW | YES |
| llm/providers/__init__.py | Export GeminiProvider instead of FreeLLMAPIProvider. | Hide unapproved providers from the module interface. | F-003 | LOW | YES |
FILES FROZEN IN PHASE 1:
 * models.py: Frozen to prevent risky database schema migrations during the security/safety remediation.
 * database.py: Core DB connection logic is stable.
 * services/pdf_generator.py: Safely ignores missing data; no changes needed.
 * llm/provider_router.py & llm/provider_manager.py: Retained to preserve the internal AI abstraction interface and avoid cascading rewrites.
==================================================
10. TEST CONTRACT
Because the repository currently lacks a test infrastructure, Phase 1 establishes the minimum required test structure (tests/ directory with pytest configurations) without necessarily implementing the full suite, but defining the required assertions.
Tenant Isolation (F-001):
 * Assert that get_user_clinic_id returns None for a random Telegram ID.
 * Assert that get_or_create_patient_by_telegram raises an exception or returns None if a new user attempts creation without a valid clinic invite/context.
 * Assert that known Patient and Staff IDs resolve to their exact clinic_id.
Authorization (F-008):
 * Assert that a mock user with role owner can successfully execute the deletion logic for a Staff record where staff.clinic_id == owner.clinic_id.
 * Assert that a mock user with role owner is REJECTED when attempting to delete a Staff record where staff.clinic_id != owner.clinic_id.
 * Assert that a mock user with role secretary is REJECTED when attempting to delete any Staff record.
Medical Safety (F-002):
 * Assert that the analysis_prompt string does not contain the words "units" or "volume".
 * Assert that an executed perform_facial_analysis mock yields a TreatmentRecommendation with estimated_units=None and estimated_volume=None.
Gemini Runtime (F-003):
 * Assert that ProviderManager contains exactly one provider key: "gemini".
 * Assert that isinstance(providers["gemini"], GeminiProvider) is True.
 * Assert that startup_diagnostics correctly identifies the absence of GEMINI_API_KEY.
==================================================
11. ACCEPTANCE CRITERIA
 * [ ] PASS/FAIL: Given a Telegram user with no existing Staff or Patient record, get_user_clinic_id returns None (or throws an explicit error), and does NOT return Clinic.id = 1.
 * [ ] PASS/FAIL: Given a staff deletion request from an owner, the transaction is aborted if the target staff's clinic_id does not match the owner's clinic_id.
 * [ ] PASS/FAIL: The LLM prompt in perform_facial_analysis does not request dosage, units, or volume estimates.
 * [ ] PASS/FAIL: The patient_agent.py module successfully imports and instantiates the GeminiProvider.
 * [ ] PASS/FAIL: FreeLLMAPIProvider is completely unreachable from the ProviderRouter during standard execution.
==================================================
12. ROLLBACK PLAN
F-001 & F-008 (Auth/Tenant):
 * What can break: New users may be entirely blocked from interacting with the bot if onboarding flows relied heavily on the fallback.
 * Backup: Create a database snapshot prior to deployment.
 * Reversible: Highly reversible via Git revert.
 * Smoke test: Message the bot as an existing patient and ensure standard menus load.
F-002 (Medical Safety):
 * What can break: The LLM might fail JSON schema validation if it expects to populate units/volume.
 * Backup: None required (prompt change).
 * Reversible: Easily reversible via Git revert.
 * Smoke test: Run a single facial analysis workflow and verify the PDF is generated without units.
F-003 (Gemini):
 * What can break: Total AI failure if the GEMINI_API_KEY is invalid or missing in the production environment.
 * Backup: Ensure previous FREELLMAPI_API_KEY is not deleted from .env until Gemini is proven stable.
 * Reversible: Revert patient_agent.py and __init__.py.
 * Smoke test: Trigger a standard conversational FAQ and verify a valid response is returned.
==================================================
13. IMPLEMENTATION ORDER
Step 1: Secure Tenant Boundaries (F-001)
 * Files: utils/role_utils.py, bot.py
 * Prerequisite: None.
 * Validation: Unknown users are rejected gracefully.
 * Rollback: Git revert.
Step 2: Enforce Object-Level Authorization (F-008)
 * Files: bot.py
 * Prerequisite: Step 1 (requires trustworthy clinic_id).
 * Validation: Cross-tenant staff deletion fails.
 * Rollback: Git revert.
Step 3: Enforce Medical Safety Boundaries (F-002)
 * Files: handlers/facial_analysis.py
 * Prerequisite: None.
 * Validation: PDF generates without dosage information.
 * Rollback: Git revert.
Step 4: Align AI Runtime to Gemini (F-003)
 * Files: llm/providers/__init__.py, patient_agent.py
 * Prerequisite: Valid Google Gemini API Key in the environment.
 * Validation: Bot successfully answers inquiries using the Gemini provider.
 * Rollback: Git revert and ensure old API keys remain available.
==================================================
14. STOP CONDITIONS
Implementation MUST STOP immediately if:
 * Removing the Clinic.first() fallback breaks the ability for legitimate new patients to be registered via authorized clinic invitation links (if such a mechanism currently exists but is undocumented).
 * The Google Gemini API key is missing or returning consistent 401 Unauthorized errors during testing.
 * The ProviderRouter fails to pass **kwargs properly to GeminiProvider, causing widespread generation failures.
 * Modifying the analysis_prompt causes the LLM to output malformed JSON that crashes the perform_facial_analysis parsing block.
==================================================
15. FINAL IMPLEMENTATION CHECKLIST
 * [x] F-001 implementation contract complete
 * [x] F-008 implementation contract complete
 * [x] F-002 safety boundary complete
 * [x] F-003 Gemini architecture contract complete
 * [x] Tests defined
 * [x] Acceptance criteria defined
 * [x] Rollback defined
 * [x] No unresolved architectural ambiguity
 * [x] No code modifications made
