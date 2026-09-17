# CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT.md

## 1. SCOPE

Phase 1 addresses ONLY the following prioritized foundation security and AI safety findings:
*   **F-001** — Tenant Isolation Fallback
*   **F-002** — Medical Safety Boundary in Facial Analysis
*   **F-003** — Gemini-Only Runtime
*   **F-008** — Object-Level Authorization / IDOR

The following items are explicitly **OUT OF SCOPE** for Phase 1:
- Communication Layer abstraction
- Durable Scheduler implementation
- Knowledge/RAG system implementation
- Full Agent Orchestrator build-out
- Telegram decoupling from core business logic
- Web/Mobile client API development
- Alembic database migration framework setup
- Major database schema redesigns
- Multi-provider architecture or new provider integrations

==================================================

## 2. REPOSITORY INSPECTION

### F-001: Tenant Isolation Fallback
*   **`utils/role_utils.py`**: The function `get_user_clinic_id` queries the `Staff` table, then the `Patient` table. If both fail, it falls back to `db.query(Clinic).first()` and silently assigns the user to that clinic.
*   **Callers of `get_user_clinic_id`**: `language_callback`, `main_menu_handler`, `appointment_confirm_callback`, `add_staff_confirm`, `show_staff_list`, `show_remove_staff`, and `remove_staff_callback` (all within `bot.py`).
*   **`bot.py` identity flows**: The helper function `get_or_create_patient_by_telegram` contains an identical hardcoded fallback (`clinic = db.query(Clinic).first()`) to create new patients in the first database clinic.
*   **Onboarding flow**: Currently, there is no explicit clinic-selection mechanism or invite-link parsing in the repository; it relies entirely on the `Clinic.first()` bypass for new users.

### F-002: Medical Safety Boundary
*   **`handlers/facial_analysis.py`**: The function `perform_facial_analysis` feeds images to MediaPipe and constructs a prompt for the AI.
*   **Prompt**: The prompt explicitly requests: *"For each recommendation, include estimated units/volume if possible"*.
*   **`TreatmentRecommendation` model**: The database model includes `estimated_units` and `estimated_volume` columns.
*   **PDF Generation**: `services/pdf_generator.py` conditionally renders units/volume if they exist in the dictionary payload.
*   **Physician Review Mechanism**: Missing. The PDF is delivered directly to the patient via Telegram.
*   **Safety Validation**: Missing. The JSON output from the LLM is directly mapped to the database object without clinical review gates.

### F-003: Gemini-Only Runtime
*   **`patient_agent.py`**: The `ProviderManager` is instantiated explicitly and exclusively with `{"freellmapi": FreeLLMAPIProvider()}`.
*   **`llm/providers/__init__.py`**: Only exports `FreeLLMAPIProvider`.
*   **`gemini_provider.py`**: Exists, uses `GEMINI_API_KEY`, and is compliant with the `BaseLLMProvider` interface, but is unreachable.
*   **`provider_router.py`**: Implements dynamic routing/fallback logic based on provider scores, but only ever sees the injected `freellmapi` provider.
*   **`config.py`**: Contains `FREELLMAPI_API_KEY`, `FREELLMAPI_BASE_URL`, and `GEMINI_API_KEY`.

### F-008: Object-Level Authorization / IDOR
*   **`bot.py` -> `remove_staff_callback`**: Parses `staff_id` from the callback data, queries the `Staff` table, and executes `db.delete(staff)`. There is zero validation of the executing user's role or clinic affiliation.
*   **`bot.py` -> `add_staff_confirm`**: Looks up `clinic_id` via the unsafe `get_user_clinic_id` fallback, then creates a new `Staff` record. It fails to check if the executing user possesses the `owner` role.
*   **Centralized Auth Utility**: Missing. Authorization relies on ad-hoc role lookups inside individual handlers.

==================================================

## 3. F-001 IMPLEMENTATION CONTRACT

1.  **Current identity resolution flow:** `get_user_clinic_id` checks `Staff`, then `Patient`, then blindly falls back to `Clinic.first()`.
2.  **Current trusted context:** A valid entry in the `Staff` or `Patient` tables associated with the user's Telegram ID.
3.  **Missing tenant context behavior:** Currently assigns the user to the first clinic in the DB.
4.  **Dependent callers:** All main UI and booking handlers in `bot.py` (`main_menu_handler`, `appointment_confirm_callback`, staff mutators).
5.  **Safest return type:** `get_user_clinic_id` MUST return `Optional[int]`. If no trusted record is found, it MUST return `None`.
6.  **Downstream handling:** All callers must check `if clinic_id is None:` and short-circuit execution.
7.  **Patient-facing behavior:** The bot must reply with a safe, localized fallback: *"You are not associated with any clinic. Please contact your clinic administrator for an invitation."*
8.  **Unknown user access:** An unknown user CANNOT access any clinic data.
9.  **Unknown user record creation:** An unknown user CANNOT create tenant-owned records. `get_or_create_patient_by_telegram` must be updated to require a valid `clinic_id` argument and must fail/return `None` if it is missing.
10. **Exact invariant enforced:** NO TRUSTED TENANT → NO TENANT-OWNED OPERATION. Silent tenant assignment is explicitly prohibited.

==================================================

## 4. F-008 AUTHORIZATION CONTRACT

For `remove_staff_callback` and `add_staff_confirm`, the following chain MUST be enforced locally within the handlers:

Authentication (Telegram ID)
→ Actor Identity (Resolved via `Staff` table)
→ Actor Role (Verified via `get_user_role`)
→ Actor Tenant (Verified via `get_user_clinic_id`)
→ Target Resource (`Staff` record)
→ Target Tenant (`target_staff.clinic_id`)
→ Ownership Match (`Actor Tenant == Target Tenant`)
→ Authorization Decision (`Role == 'owner'` AND `Match == True`)
→ Mutation (`db.add` / `db.delete`)

**Specific Requirements:**
- **Required role:** `owner`.
- **Required clinic_id relationship:** The executing user's `clinic_id` must exactly match the `clinic_id` of the resource being mutated.
- **Rejection behavior:** Return a localized "Unauthorized action" message via `query.edit_message_text` or `message.reply_text`.
- **Fail closed:** If any context variable is missing (`None`), the operation aborts.
- **Audit event:** A `logger.warning` event must be emitted detailing the unauthorized attempt (including the actor's Telegram ID and the target `staff_id`), without exposing secrets.
- **Centralized Helper:** Phase 1 will enforce this directly in the handlers. Do NOT introduce a new centralized middleware architecture yet.

==================================================

## 5. F-002 MEDICAL SAFETY CONTRACT

The hard boundary in Phase 1 ensures that the AI cannot generate, and the patient cannot receive, definitive medical prescriptions (dosages, units, volumes) via autonomous facial analysis.

**Implementation Rules:**
1.  **Prompt Modification:** Remove all requests for `"estimated units/volume"` and `"priority"` from the `analysis_prompt` in `handlers/facial_analysis.py`. Explicitly add a system instruction: *"Do not recommend specific dosages, units, or volumes. Provide only aesthetic observations and general treatment categories."*
2.  **Output Safety Gate:** Introduce a validation step immediately after `json.loads(llm_response)`.
3.  **Validation Logic:** Iterate through the parsed recommendations. If any recommendation contains data in `estimated_units` or `estimated_volume` keys (due to hallucination), the system MUST delete those keys or set them to `None` before persisting to the database.
4.  **Database Preservation:** The `estimated_units` and `estimated_volume` fields in the `TreatmentRecommendation` schema MUST remain untouched to prevent migrations.
5.  **PDF/Patient Output:** By setting hallucinated/unsafe values to `None` in the parsing step, the existing `services/pdf_generator.py` logic (`if rec.get('estimated_units'):`) will safely omit the data from the patient-facing report.
6.  **Physician Review:** Do NOT build a physician review UI in this phase. The boundary is enforced by strictly blocking the data from being generated and persisted.

==================================================

## 6. F-003 GEMINI-ONLY IMPLEMENTATION CONTRACT

The target architecture enforces: `Clinicos Core Platform → Clinicos AI Layer → Gemini Adapter → Google Gemini API`.

**Implementation Rules:**
1.  **Runtime Provider:** `patient_agent.py` MUST instantiate `ProviderManager` exclusively with `{"gemini": GeminiProvider()}`.
2.  **Provider Export:** `llm/providers/__init__.py` MUST export `GeminiProvider`. The export of `FreeLLMAPIProvider` must be removed.
3.  **No Fallback / Routing:** `ProviderRouter` will be preserved to maintain the `_router.generate()` interface compatibility, but its internal logic will loop over exactly one provider (Gemini). No multi-provider routing can occur.
4.  **Abstraction Preservation:** The `ProviderManager` and `BaseLLMProvider` abstractions remain intact. Do NOT rewrite `patient_agent.py` to call `google.generativeai` directly.
5.  **Legacy Files:** Do NOT delete `provider_router.py`, `freellmapi_provider.py`, or other legacy provider files. They remain frozen and unreachable from the production runtime path.

==================================================

## 7. GEMINI CONFIGURATION CONTRACT

**Inspection & Rules:**
- **Required configuration:** `GEMINI_API_KEY` (already sourced in `config.py`).
- **Optional configuration:** `GEMINI_MODEL`, `GEMINI_MAX_TOKENS`.
- **Startup validation:** Modify `startup_diagnostics()` in `bot.py` to explicitly check `if not GEMINI_API_KEY:`.
- **Failure behavior:** If `GEMINI_API_KEY` is missing, the system MUST log a safe error (`"CRITICAL: GEMINI_API_KEY is not configured. AI responses will fail."`) but MUST NOT crash the Telegram polling loop. The bot should continue to run so deterministic functions (like basic menu navigation) remain alive.
- **Secret Safety:** Under no circumstances should the actual API key string be printed to standard output or logs.

==================================================

## 8. CROSS-FINDING DEPENDENCIES

- **F-001 (Tenant Isolation) MUST precede F-008 (Authorization):** The authorization logic relies on a trusted `get_user_clinic_id` to establish the Actor's Tenant. If F-001 is not fixed first, an unauthorized user could exploit the fallback to gain `Clinic.first()` permissions and bypass F-008 checks.
- **F-002 (Medical Safety) and F-003 (Gemini):** These are architecturally independent of the identity flows and can be implemented in any order. However, changing the AI provider to Gemini (F-003) may alter how the facial analysis prompt is interpreted; therefore, the output safety gate (F-002) acts as a necessary safeguard regardless of the active LLM.

==================================================

## 9. EXACT FILE CHANGE PLAN

| File | Expected Change | Reason | Finding | Risk | Required? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `utils/role_utils.py` | Remove `db.query(Clinic).first()` fallback. Return `None` if missing. | Prevent cross-tenant data leakage. | F-001 | MED | YES |
| `bot.py` | Add `None` checks for `clinic_id` across handlers. Remove `Clinic.first()` from patient creator. Enforce `owner` and `clinic_id` match in staff mutators. Check `GEMINI_API_KEY` on startup. | Ensure unassigned users are safely blocked. Prevent IDOR. Prevent silent AI crashes. | F-001, F-008, F-003 | HIGH | YES |
| `handlers/facial_analysis.py` | Remove dosage/volume requests from prompt. Add post-generation output safety gate. | Enforce medical safety boundaries. | F-002 | LOW | YES |
| `patient_agent.py` | Import and inject `GeminiProvider` into `ProviderManager` instead of `FreeLLMAPIProvider`. | Establish Gemini-only runtime invariant. | F-003 | LOW | YES |
| `llm/providers/__init__.py` | Export `GeminiProvider` only. | Clean up the active provider interface. | F-003 | LOW | YES |

**FILES FROZEN IN PHASE 1:**
- `models.py`: Frozen to prevent database schema migrations.
- `database.py`: Core DB connection logic is stable.
- `services/pdf_generator.py`: Safely ignores missing data inherently; changing it risks PDF layout breakage.
- `llm/provider_router.py`: Retained to preserve the internal AI abstraction interface without requiring a major refactor of caller files.
- `llm/providers/*_provider.py` (Legacy): Frozen. Will be cleaned up in a dedicated legacy-removal phase to limit Phase 1 scope.

==================================================

## 10. TEST CONTRACT

Phase 1 requires establishing a minimum `pytest` infrastructure.

**Infrastructure:**
- `tests/conftest.py` (Mock DB session, mock models)
- `tests/test_tenant_isolation.py`
- `tests/test_authorization.py`
- `tests/test_medical_safety.py`
- `tests/test_gemini_runtime.py`

**Tenant Isolation Tests:**
- `test_unknown_user_returns_no_tenant`: Assert `get_user_clinic_id(999)` returns `None`.
- `test_unknown_user_cannot_create_patient`: Assert `get_or_create_patient_by_telegram` fails safely or returns `None` if `clinic_id` is missing.
- `test_known_patient_resolves_clinic`: Assert valid patient ID returns exact `clinic_id`.

**Authorization Tests:**
- `test_owner_can_delete_staff_same_clinic`: Assert logic allows deletion when actor role is 'owner' and clinic IDs match.
- `test_owner_cannot_delete_staff_different_clinic`: Assert logic rejects deletion and emits warning log when clinic IDs mismatch.
- `test_secretary_cannot_delete_staff`: Assert logic rejects deletion for non-owner roles.

**Medical Safety Tests:**
- `test_facial_analysis_prompt_safe`: Assert prompt string does not contain "units" or "volume".
- `test_unsafe_ai_output_is_blocked`: Inject a mocked JSON response containing `estimated_units: "20"`. Assert that the parsing gate strips this value and sets `estimated_units` to `None` before returning the `TreatmentRecommendation` dictionary.

**Gemini Tests:**
- `test_runtime_uses_gemini`: Assert `providers` dict in `patient_agent.py` contains exactly `"gemini": GeminiProvider`.
- `test_freellmapi_unreachable`: Assert `FreeLLMAPIProvider` is not present in the runtime `ProviderManager`.
- `test_startup_diagnostics_missing_key`: Mock missing `GEMINI_API_KEY` and assert `startup_diagnostics` logs a CRITICAL error without throwing an exception that crashes the app.

==================================================

## 11. ACCEPTANCE CRITERIA

- [ ] PASS / FAIL: Given a Telegram user with no trusted tenant context, `get_user_clinic_id` returns `None`.
- [ ] PASS / FAIL: Given a missing `clinic_id`, `get_or_create_patient_by_telegram` returns `None` and does not query `Clinic.first()`.
- [ ] PASS / FAIL: Given a staff deletion request from an `owner`, the transaction is aborted if the target staff's `clinic_id` does not match the owner's `clinic_id`.
- [ ] PASS / FAIL: Given a staff creation/deletion request from a `secretary`, the transaction is safely rejected.
- [ ] PASS / FAIL: The LLM prompt in `perform_facial_analysis` does not request dosage, units, or volume estimates.
- [ ] PASS / FAIL: An AI response containing hallucinated `estimated_units` is intercepted, and the value is set to `None` before database insertion.
- [ ] PASS / FAIL: The `patient_agent.py` module successfully instantiates `ProviderManager` exclusively with `GeminiProvider`.
- [ ] PASS / FAIL: `FreeLLMAPIProvider` is completely unreachable from the `ProviderRouter` during standard execution.
- [ ] PASS / FAIL: Missing `GEMINI_API_KEY` results in a safe, non-fatal CRITICAL log entry during startup.

==================================================

## 12. ROLLBACK PLAN

- **What can break:** Users heavily reliant on the legacy onboarding flow (which silently created patients in Clinic 1) will be blocked from using the bot until a proper invitation/registration workflow is introduced.
- **What must be backed up:** Create a full snapshot of the PostgreSQL database prior to deployment, ensuring `Staff` and `Patient` mapping tables are preserved.
- **What is reversible:** All changes are strictly code-level Python modifications and are 100% reversible via standard Git rollback (`git revert`).
- **Deployment risk:** LOW. No database schema changes are occurring.
- **Smoke test:** Deploy to staging. Send a `/start` message from a known patient Telegram account and verify the main menu loads. Send a `/start` message from an unknown account and verify a safe rejection message is returned.

==================================================

## 13. IMPLEMENTATION ORDER

1.  **Step 1: Secure Tenant Boundaries (F-001)**
    - *Files:* `utils/role_utils.py`, `bot.py`
    - *Prerequisite:* None
    - *Validation:* Unit tests for `get_user_clinic_id`
    - *Rollback:* Git revert
2.  **Step 2: Enforce Object-Level Authorization (F-008)**
    - *Files:* `bot.py`
    - *Prerequisite:* Step 1
    - *Validation:* Unit tests for `remove_staff_callback` and `add_staff_confirm`
    - *Rollback:* Git revert
3.  **Step 3: Enforce Medical Safety Boundaries (F-002)**
    - *Files:* `handlers/facial_analysis.py`
    - *Prerequisite:* None
    - *Validation:* Unit tests for output safety gate
    - *Rollback:* Git revert
4.  **Step 4: Align AI Runtime to Gemini (F-003)**
    - *Files:* `patient_agent.py`, `llm/providers/__init__.py`, `bot.py`
    - *Prerequisite:* Valid Google Gemini API Key in `.env`
    - *Validation:* Unit tests for provider instantiation
    - *Rollback:* Git revert

==================================================

## 14. STOP CONDITIONS

Implementation MUST STOP and escalate if:
- Removing the `Clinic.first()` fallback breaks an undocumented but critical production onboarding path that cannot be quickly substituted with a safe rejection message.
- The `GeminiProvider` implementation is discovered to be incompatible with the `ProviderRouter` `**kwargs` abstraction, causing runtime crashes.
- The output safety gate in `facial_analysis.py` fails to parse Gemini's JSON structure, causing the entire facial analysis feature to crash.
- Authorization scoping requires joining tables that do not currently possess foreign key relationships in `models.py` (which would require a frozen DB schema migration).

==================================================

## 15. FINAL IMPLEMENTATION CHECKLIST

- [x] F-001 implementation contract complete
- [x] F-008 implementation contract complete
- [x] F-002 safety boundary complete
- [x] F-003 Gemini architecture contract complete
- [x] Tests defined
- [x] Acceptance criteria defined
- [x] Rollback defined
- [x] No unresolved architectural ambiguity
- [x] No code modifications made
