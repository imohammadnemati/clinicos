# CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT_V2.md
## 0. DOCUMENT STATUS
**Document:** CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT_V2.md  
**Version:** 2.0  
**Status:** AUTHORITATIVE IMPLEMENTATION CONTRACT  
**Phase:** Phase 1 — Foundation Security and AI Runtime Hardening  
**Implementation Mode:** Controlled Repository Remediation  
**Modification Policy:** Minimal, evidence-driven, scope-constrained changes only
This document is an implementation contract.
The implementation agent MUST treat this document as an executable engineering specification and MUST NOT reinterpret the target architecture, expand the scope, or introduce unrelated architectural changes.
The implementation agent MUST inspect the repository before modifying files.
The implementation agent MUST preserve all existing architectural abstractions unless this contract explicitly requires their modification.
The implementation agent MUST NOT claim completion based on static inspection alone when an executable test is required.
---
# 1. PHASE 1 OBJECTIVE
Phase 1 establishes the minimum security and AI-runtime foundation required before Clinicos can safely proceed toward the broader target architecture.
Phase 1 addresses ONLY these findings:
- **F-001 — Tenant Isolation Fallback**
- **F-002 — Medical Safety Boundary in Facial Analysis**
- **F-003 — Gemini-Only Runtime**
- **F-008 — Object-Level Authorization / IDOR**
Phase 1 MUST produce:
1. A fail-closed tenant resolution mechanism.
2. Explicit object-level authorization for staff mutations.
3. A patient-facing medical safety boundary for facial analysis.
4. A Gemini-only production runtime.
5. Minimum executable regression tests covering all four findings.
6. A machine-verifiable implementation report.
Phase 1 MUST NOT attempt to complete the entire Clinicos target architecture.
---
# 2. NON-GOALS / EXPLICITLY OUT OF SCOPE
The following are explicitly OUT OF SCOPE for Phase 1:
- Communication Layer abstraction
- Durable Scheduler implementation
- Knowledge/RAG system implementation
- Full Agent Orchestrator build-out
- Telegram decoupling from core business logic
- Web client API development
- Android client development
- iOS client development
- Telegram Mini App development
- Alembic migration framework setup
- Major database schema redesign
- Database model redesign
- New database tables unless absolutely required for tests
- New AI provider integrations
- Multi-provider runtime architecture
- Provider fallback
- Provider marketplace
- Advanced AI routing
- Full centralized authorization middleware
- Full RBAC redesign
- Physician dashboard implementation
- Human-review dashboard implementation
- Full audit-event architecture
- Full notification abstraction
- Production observability redesign
- Infrastructure redesign
- Deployment platform migration
- Legacy provider deletion
- General codebase cleanup
- Formatting-only refactors
- Unrelated bug fixing
If an implementation opportunity falls outside this list, DO NOT implement it unless it is strictly necessary to satisfy an acceptance criterion in this contract.
---
# 3. AUTHORITATIVE ARCHITECTURAL RULES
The following rules are authoritative for Phase 1.
## 3.1 AI Provider Architecture
The target runtime path is:
Clinicos Core Platform
→ Clinicos AI Layer
→ Gemini Adapter
→ Google Gemini API
The active AI provider for Phase 1 is:
**Google Gemini only.**
FreeLLMAPI MUST NOT be used by the production runtime.
No AI provider fallback is permitted.
No multi-provider runtime routing is permitted.
The internal provider abstraction MUST remain intact.
Multiple Gemini models MAY exist in the future, but Phase 1 does not implement model-routing complexity unless already supported safely by the existing abstraction.
---
## 3.2 Tenant Isolation
The following invariant is mandatory:
> NO TRUSTED TENANT → NO TENANT-OWNED OPERATION
An unknown or untrusted Telegram identity MUST NOT be silently assigned to an arbitrary clinic.
`Clinic.first()` MUST NOT be used as a tenant-resolution fallback.
---
## 3.3 Authorization
Object-level authorization MUST be evaluated before mutation.
The authorization chain is:
Authentication
→ Actor Identity
→ Actor Role
→ Actor Tenant
→ Target Resource
→ Target Tenant
→ Ownership Match
→ Authorization Decision
→ Mutation
Authorization MUST fail closed.
---
## 3.4 Medical Safety
Facial analysis is an informational aesthetic analysis feature.
It MUST NOT autonomously provide:
- injection dosage
- injection units
- injection volume
- medication dosage
- definitive prescription
- patient-specific treatment quantity
- procedural dosing instructions
Prompt-level restrictions alone are insufficient.
The system MUST enforce a patient-facing output safety boundary after model generation and parsing and before persistence and delivery.
---
## 3.5 Secret Safety
No API key, token, password, credential, or secret MUST be:
- added to source code
- added to documentation
- added to tests
- printed to logs
- committed to Git
- included in implementation reports
Environment variables may be referenced by name only.
---
# 4. REPOSITORY INSPECTION REQUIREMENT
Before changing any code, inspect:
- all files directly involved in F-001
- all callers of `get_user_clinic_id`
- all callers of `get_or_create_patient_by_telegram`
- all staff mutation handlers
- all facial-analysis generation and persistence paths
- all provider initialization paths
- all provider routing paths
- all startup diagnostics
- all existing tests
- all configuration relevant to Gemini
- all imports of `FreeLLMAPIProvider`
- all imports of `GeminiProvider`
Do not assume that the files listed in this contract are the only files involved.
If additional files are discovered to be necessary, document them before modification.
Do not modify unrelated files merely because they contain legacy code.
---
# 5. FINDING F-001 — TENANT ISOLATION FALLBACK
## 5.1 Current Problem
The current implementation contains a tenant fallback equivalent to:
```python
db.query(Clinic).first()

when no trusted Staff or Patient identity is found.

This behavior is prohibited.

It can bind an unknown Telegram user to an arbitrary tenant.

⸻

5.2 Required Behavior

get_user_clinic_id MUST:

1. Attempt trusted Staff resolution.
2. Attempt trusted Patient resolution where appropriate.
3. Return the exact associated clinic_id when trusted identity exists.
4. Return None when no trusted tenant exists.
5. NEVER query Clinic.first() as a fallback.
6. NEVER infer a tenant from database ordering.
7. NEVER select the first available clinic.
8. NEVER silently create tenant membership.

Required invariant:

trusted identity + valid clinic_id → tenant access
no trusted identity → None

⸻

5.3 Return Contract

The function MUST support:

Optional[int]

or an equivalent nullable tenant identifier.

The exact implementation style may follow the existing codebase conventions.

⸻

5.4 Downstream Caller Requirements

Every caller of get_user_clinic_id MUST safely handle:

clinic_id is None

A caller MUST NOT:

* continue using a guessed clinic
* continue using Clinic 1
* continue using the first clinic
* create a tenant-owned record
* query tenant-owned data
* mutate tenant-owned data

unless an explicitly safe onboarding path exists.

⸻

5.5 Patient Creation

get_or_create_patient_by_telegram MUST NOT discover a tenant through:

Clinic.first()

The function MUST require a trusted clinic_id from the caller or another explicitly authorized tenant-binding mechanism.

If clinic_id is missing:

return None

or another safe failure consistent with existing code conventions.

It MUST NOT create a tenant-owned Patient record.

⸻

5.6 Unknown User Behavior

An unknown Telegram user MUST NOT gain access to:

* clinic information
* patient information
* staff information
* appointments
* knowledge items
* clinic settings
* tenant-owned analytics
* tenant-owned AI context

The bot MAY provide a safe localized response such as:

You are not associated with any clinic. Please contact your clinic administrator for an invitation.

The exact localized wording may follow the existing localization architecture.

⸻

5.7 Onboarding Preservation

The implementation agent MUST inspect whether a legitimate onboarding mechanism already exists.

If there is no safe onboarding mechanism, the existing insecure implicit onboarding MUST NOT be preserved merely for compatibility.

Blocking unknown users is the correct fail-closed behavior.

Do NOT invent a full invitation system in Phase 1.

⸻

5.8 F-001 Acceptance Tests

At minimum:

test_unknown_user_returns_no_tenant
test_unknown_user_cannot_create_patient
test_known_patient_resolves_clinic
test_known_staff_resolves_clinic
test_no_clinic_first_fallback_exists_in_tenant_resolution

Where practical, tests MUST verify behavior rather than merely inspect source strings.

⸻

6. FINDING F-008 — OBJECT-LEVEL AUTHORIZATION / IDOR

6.1 Affected Operations

Phase 1 MUST secure at minimum:

* remove_staff_callback
* add_staff_confirm

All related authorization paths MUST be inspected.

⸻

6.2 Required Authorization Chain

For staff mutation:

Telegram ID
→ Staff actor lookup
→ Actor role verification
→ Actor clinic verification
→ Target Staff lookup
→ Target clinic verification
→ Tenant ownership comparison
→ Owner authorization
→ Mutation

Every step MUST be fail-closed.

⸻

6.3 Actor Requirements

The actor MUST:

1. Be authenticated through the Telegram identity.
2. Resolve to a valid Staff record.
3. Have role owner.
4. Have a valid trusted clinic_id.

A Patient MUST NOT perform owner-only staff mutations.

A Secretary MUST NOT perform owner-only staff mutations.

An unknown user MUST NOT perform owner-only staff mutations.

⸻

6.4 Target Requirements

For staff deletion:

1. Target staff record MUST exist.
2. Target staff record MUST have a valid clinic_id.
3. Target clinic MUST match actor clinic.
4. Only then may deletion occur.

Equivalent tenant checks MUST apply to staff creation.

⸻

6.5 Ownership Rule

The following invariant MUST hold:

actor_clinic_id == target_staff.clinic_id

AND:

actor_role == "owner"

Both conditions are mandatory.

⸻

6.6 Fail-Closed Rule

If ANY required context is missing:

* actor missing
* actor role missing
* actor clinic missing
* target missing
* target clinic missing
* ownership mismatch

the operation MUST abort.

No mutation may occur.

⸻

6.7 Unauthorized Response

The user MUST receive a safe localized response equivalent to:

Unauthorized action.

Do not reveal:

* another clinic’s identity
* target staff details
* internal database identifiers beyond what is already visible
* authorization internals
* secrets

⸻

6.8 Security Logging

Unauthorized mutation attempts MUST emit a warning-level security log.

The log SHOULD contain:

* actor Telegram ID
* target staff ID
* attempted operation
* rejection reason where safe

The log MUST NOT contain:

* API keys
* access tokens
* passwords
* session secrets
* full patient medical information

⸻

6.9 No Premature Middleware Refactor

Do NOT introduce a complete centralized authorization middleware system in Phase 1.

Authorization MAY remain locally enforced in the affected handlers.

However, the implementation MUST avoid weakening tenant isolation to preserve existing behavior.

⸻

6.10 F-008 Acceptance Tests

At minimum:

test_owner_can_delete_staff_same_clinic
test_owner_cannot_delete_staff_different_clinic
test_secretary_cannot_delete_staff
test_patient_cannot_delete_staff
test_unknown_user_cannot_delete_staff
test_cross_tenant_staff_creation_is_rejected

Tests MUST verify that unauthorized mutations do not occur.

Testing only the returned message is insufficient.

⸻

7. FINDING F-002 — MEDICAL SAFETY BOUNDARY

7.1 Current Problem

The facial-analysis flow currently allows model output to contain fields such as:

* estimated_units
* estimated_volume

and can deliver generated treatment information directly to patients.

This is not acceptable for autonomous patient-facing facial analysis.

⸻

7.2 Prompt Safety Requirements

The facial-analysis prompt MUST NOT request:

* units
* volume
* dosage
* injection quantity
* procedural dosing
* medication dosage
* definitive prescriptions

The prompt MUST explicitly instruct the model that it must not provide such information.

A suitable instruction is:

Do not recommend specific dosages, units, or volumes.
Provide only aesthetic observations and general treatment categories.
Do not provide definitive medical prescriptions or patient-specific procedural quantities.

The exact wording may be adapted to the existing prompt architecture without weakening the rule.

⸻

8. F-002 OUTPUT SAFETY GATE

8.1 Mandatory Requirement

Prompt engineering is NOT considered a sufficient medical safety control.

A programmatic output safety gate MUST exist.

The gate MUST execute:

LLM generation
→ response parsing
→ safety validation
→ safe normalization
→ persistence
→ patient-facing rendering/delivery

Unsafe output MUST NOT reach persistence or patient delivery.

⸻

8.2 Safety Gate Location

The safety gate MUST execute immediately after successful structured parsing of the LLM output and BEFORE:

* TreatmentRecommendation persistence
* PDF generation for patient delivery
* Telegram patient delivery
* any other patient-facing output

⸻

8.3 Forbidden Structured Fields

The following fields MUST NOT contain patient-facing treatment quantities generated autonomously by the model:

estimated_units
estimated_volume
dosage
dose
injection_units
injection_volume
medication_dose
treatment_quantity

If the existing schema uses additional equivalent fields, those fields MUST also be inspected.

⸻

8.4 Unsafe Output Handling

If the model returns prohibited structured fields:

The system MUST NOT blindly persist them.

At minimum, the unsafe values MUST be neutralized before persistence.

For example:

estimated_units = None
estimated_volume = None

However, simply deleting structured fields is NOT sufficient if the unsafe information remains elsewhere in free text.

⸻

8.5 Free-Text Safety

The safety gate MUST also inspect relevant free-text recommendation content for obvious prohibited clinical quantity instructions.

Examples include:

* numeric injection quantities
* unit-based injection instructions
* volume-based injection instructions
* medication dosage instructions
* explicit patient-specific procedural dosing

If such unsafe content is detected, the system MUST prevent that content from being delivered to the patient.

The implementation MAY choose a conservative safe behavior such as:

block entire patient-facing recommendation

or:

replace unsafe content with a safe non-prescriptive summary

The selected behavior MUST be documented and tested.

⸻

9. MEDICAL SAFETY HIERARCHY

The safety gate MUST take precedence over commercial or conversational optimization.

The following hierarchy applies:

Medical Safety
>
Privacy
>
Authorization
>
Platform Policy
>
Domain Truth
>
Approved Knowledge
>
AI Reasoning
>
Commercial Optimization

The model’s output MUST NOT override the safety gate.

⸻

10. DATABASE PRESERVATION FOR F-002

The existing database fields:

estimated_units
estimated_volume

MUST remain unchanged in Phase 1.

Do NOT:

* remove columns
* rename columns
* create migrations
* modify database schema
* redesign TreatmentRecommendation

The safety boundary is a runtime behavior change.

⸻

11. PATIENT-FACING OUTPUT REQUIREMENT

Before any facial-analysis result is delivered to a patient:

1. AI output MUST be parsed.
2. Safety validation MUST run.
3. Unsafe quantities MUST be neutralized.
4. Unsafe free-text recommendations MUST be blocked or safely transformed.
5. Only the validated safe result may proceed to rendering.
6. Only the validated safe result may be sent to Telegram.

There MUST NOT be a code path that sends the raw LLM response directly to the patient.

⸻

12. PHYSICIAN REVIEW

A full physician-review workflow is OUT OF SCOPE for Phase 1.

Do NOT build:

* physician dashboard
* approval UI
* review queue
* clinical sign-off system

Phase 1 instead establishes a hard autonomous safety boundary.

Future phases MAY introduce physician review.

⸻

13. F-002 ACCEPTANCE TESTS

At minimum:

test_facial_analysis_prompt_safe
test_unsafe_structured_units_are_removed
test_unsafe_structured_volume_is_removed
test_unsafe_free_text_is_blocked
test_safe_facial_analysis_output_is_allowed
test_unsafe_output_cannot_reach_patient_delivery
test_unsafe_output_cannot_be_persisted

Tests MUST exercise the actual safety-gate function/path.

A test that only checks the prompt text is insufficient.

⸻

14. FINDING F-003 — GEMINI-ONLY RUNTIME

14.1 Target Runtime

The production runtime MUST use:

Clinicos Core
→ Internal AI abstraction
→ GeminiProvider
→ Google Gemini

⸻

14.2 ProviderManager

patient_agent.py MUST instantiate the provider manager with exactly one active runtime provider:

{
    "gemini": GeminiProvider()
}

The exact syntax may vary according to the existing implementation.

The semantic invariant MUST remain:

active runtime providers == exactly one
provider name == gemini
provider implementation == GeminiProvider

⸻

14.3 FreeLLMAPI

FreeLLMAPIProvider MUST NOT be:

* instantiated by the runtime
* injected into ProviderManager
* selected by ProviderRouter
* invoked by patient-agent execution
* used as a fallback
* used as a recovery provider

⸻

14.4 ProviderRouter

ProviderRouter MAY remain temporarily for compatibility with existing internal interfaces.

However, during standard production execution:

ProviderRouter active provider set == Gemini only

There MUST be no provider fallback.

There MUST be no multi-provider runtime routing.

There MUST be no provider score selection between Gemini and legacy providers.

⸻

14.5 Abstraction Preservation

The following abstractions MUST remain intact unless technically impossible:

* BaseLLMProvider
* GeminiProvider
* ProviderManager
* existing internal AI interfaces

Do NOT rewrite the application to call the Google Gemini SDK directly from business logic.

Gemini-specific implementation MUST remain isolated behind the AI abstraction.

⸻

15. LEGACY PROVIDERS

The following files MUST NOT be deleted during Phase 1 merely because they are legacy:

* freellmapi_provider.py
* openrouter_provider.py
* deepseek_provider.py
* openai_provider.py
* mistral_provider.py
* other legacy provider files discovered in the repository

They may remain physically present.

However:

Physically present legacy provider files MUST NOT imply runtime reachability.

The runtime must be Gemini-only.

Legacy cleanup is deferred to a future dedicated phase.

⸻

16. PROVIDER EXPORTS

llm/providers/__init__.py MUST expose GeminiProvider for the active runtime.

Removing FreeLLMAPIProvider from the active export surface is preferred if and only if this does not break unrelated legacy imports.

Do NOT perform broad legacy cleanup merely to make imports look clean.

The primary invariant is runtime reachability, not file deletion.

⸻

17. GEMINI CONFIGURATION

17.1 Required Configuration

The runtime MUST use:

GEMINI_API_KEY

The implementation MAY support existing optional configuration such as:

GEMINI_MODEL
GEMINI_MAX_TOKENS

only if already compatible with the repository architecture.

Do NOT introduce unnecessary configuration complexity.

⸻

17.2 Startup Diagnostics

startup_diagnostics() MUST check whether:

GEMINI_API_KEY

is configured.

If missing, it MUST emit a safe critical error equivalent to:

CRITICAL: GEMINI_API_KEY is not configured. AI responses will fail.

The exact logging syntax may follow project conventions.

⸻

17.3 Non-Fatal Startup

A missing Gemini API key MUST NOT crash the Telegram polling process solely because AI configuration is missing.

The bot MAY continue running deterministic functionality.

AI-dependent operations MUST fail safely.

⸻

17.4 Secret Logging

The implementation MUST NEVER log:

GEMINI_API_KEY=<actual-value>

or any secret-derived value.

Only the existence or absence of configuration may be logged.

⸻

18. GEMINI RUNTIME ACCEPTANCE TESTS

At minimum:

test_runtime_uses_gemini
test_runtime_provider_set_contains_only_gemini
test_freellmapi_is_not_runtime_provider
test_no_provider_fallback_occurs
test_missing_gemini_key_is_non_fatal
test_gemini_configuration_does_not_log_secret

Where possible, tests MUST instantiate the relevant runtime objects rather than relying only on source-code inspection.

⸻

19. TEST INFRASTRUCTURE

Phase 1 MUST establish a minimal executable pytest infrastructure.

Minimum expected files:

tests/
├── conftest.py
├── test_tenant_isolation.py
├── test_authorization.py
├── test_medical_safety.py
└── test_gemini_runtime.py

The exact test structure may differ if the repository already has an appropriate testing architecture.

Do NOT duplicate existing fixtures unnecessarily.

⸻

20. TEST QUALITY REQUIREMENTS

Tests MUST:

1. Execute against actual implementation code.
2. Verify security behavior.
3. Verify failure behavior.
4. Verify mutation prevention.
5. Verify Gemini-only runtime behavior.
6. Verify patient-facing safety boundaries.
7. Avoid testing only implementation details where behavior can be tested directly.

Mocking is permitted where required to isolate external services.

However, mocking MUST NOT turn all meaningful logic into assertions about mocked values.

⸻

21. REQUIRED TEST EXECUTION

The implementation agent MUST actually execute the test suite.

At minimum:

pytest

If the repository requires a different command, document the exact command used.

The implementation agent MUST NOT claim:

ALL TESTS PASS

unless the tests were actually executed.

⸻

22. TEST RESULT REPORTING

The final implementation report MUST include:

Test command:
Test environment:
Tests collected:
Tests passed:
Tests failed:
Tests skipped:
Tests errored:

For failures, include:

* test name
* failure reason
* relevant traceback summary
* whether failure is caused by Phase 1 changes
* whether additional work is required

Do not hide failing tests.

⸻

23. STATIC VS EXECUTABLE VERIFICATION

The implementation report MUST distinguish:

STATIC VERIFICATION

from:

EXECUTABLE VERIFICATION

Examples of static verification:

* source inspection
* import inspection
* grep/search
* AST inspection

Examples of executable verification:

* pytest
* runtime instantiation
* mocked handler execution
* provider initialization
* safety-gate execution

Static evidence MUST NOT be represented as an executed behavioral test.

⸻

24. EXACT FILE CHANGE PLAN

Expected primary files:

File	Expected Change	Finding	Required
utils/role_utils.py	Remove tenant fallback and return None when tenant cannot be trusted	F-001	YES
bot.py	Handle missing tenant, remove patient-creation fallback, enforce staff authorization, add Gemini startup diagnostics	F-001, F-003, F-008	YES
handlers/facial_analysis.py	Remove unsafe prompt requests and implement output safety gate	F-002	YES
patient_agent.py	Inject GeminiProvider as sole runtime provider	F-003	YES
llm/providers/__init__.py	Expose GeminiProvider for active runtime	F-003	YES
tests/*	Add executable Phase 1 regression tests	ALL	YES

Additional files MAY be changed only when:

1. required for the implementation,
2. justified by repository evidence,
3. documented in the final report,
4. directly related to Phase 1.

⸻

25. FROZEN FILES

The following files are frozen unless a blocking technical incompatibility is discovered:

* models.py
* database.py
* services/pdf_generator.py
* llm/provider_router.py
* llm/provider_manager.py
* legacy provider implementation files

If a frozen file MUST be modified:

1. STOP before making the modification.
2. Document why it is required.
3. Explain why the contract cannot be satisfied without it.
4. Identify the smallest possible change.
5. Continue only if the modification does not expand Phase 1 scope.

⸻

26. DATABASE CONSTRAINT

Phase 1 MUST NOT require a database schema migration.

Do NOT introduce:

* new mandatory columns
* renamed columns
* removed columns
* new foreign-key requirements
* schema-breaking constraints

Existing database structures MUST be preserved.

If a database migration becomes necessary, STOP and report the blocker.

⸻

27. IMPLEMENTATION METHOD

The implementation agent MUST follow this order:

Step 1 — Inspect

Inspect all relevant repository code and tests.

Step 2 — Establish Baseline

Confirm the actual current behavior of:

* F-001
* F-002
* F-003
* F-008

Step 3 — Implement F-001

Remove unsafe tenant fallback.

Step 4 — Implement F-008

Enforce actor role and tenant ownership.

Step 5 — Implement F-002

Implement prompt restrictions and programmatic output safety.

Step 6 — Implement F-003

Switch active runtime to Gemini-only.

Step 7 — Add/Update Tests

Implement minimum executable regression coverage.

Step 8 — Execute Tests

Run the real test suite.

Step 9 — Perform Runtime Verification

Where environment permits, verify actual initialization and execution paths.

Step 10 — Produce Final Report

Create:

CLINICOS_PHASE_1_IMPLEMENTATION_REPORT.md

⸻

28. MINIMAL-CHANGE PRINCIPLE

The implementation MUST prefer:

smallest safe change
>
local refactor
>
broad refactor

Do NOT refactor working code simply because it is architecturally imperfect.

Phase 1 is remediation, not a rewrite.

⸻

29. NO UNRELATED MODIFICATIONS

Do NOT modify:

* unrelated business logic
* unrelated UI
* unrelated database models
* unrelated provider implementations
* unrelated scheduling
* unrelated Telegram flows
* unrelated formatting
* unrelated dependencies

unless directly required to satisfy a Phase 1 acceptance criterion.

⸻

30. DEPENDENCY RULE

F-001 MUST be implemented before F-008.

Reason:

F-008 relies on a trustworthy actor tenant.

If tenant resolution is insecure, object-level authorization can become insecure even if role checks appear correct.

⸻

31. STOP CONDITIONS

Implementation MUST STOP and report a blocker if:

1. Removing Clinic.first() breaks an undocumented but critical production onboarding flow that cannot safely be blocked.
2. A legitimate onboarding flow exists but its tenant semantics cannot be established from repository evidence.
3. GeminiProvider is incompatible with the existing BaseLLMProvider or ProviderRouter interface.
4. Gemini-only execution cannot be enforced without modifying a frozen architectural component.
5. The facial-analysis output structure cannot be safely parsed.
6. Unsafe medical output cannot be blocked before patient delivery.
7. Authorization cannot be scoped to tenant ownership using the existing data model.
8. A database migration becomes necessary.
9. The required fix would require a major architectural rewrite.
10. The existing tests reveal unrelated production-critical failures that make safe verification impossible.

When a stop condition occurs:

* DO NOT invent a workaround.
* DO NOT silently weaken the requirement.
* DO NOT mark the finding as resolved.
* Document the blocker precisely.

⸻

32. ACCEPTANCE CRITERIA

Every criterion MUST receive:

PASS
FAIL
BLOCKED
NOT VERIFIED

Never use vague wording such as:

Looks good
Probably fixed
Should work
Implemented

without verification evidence.

⸻

F-001 Acceptance

A1

Given a Telegram user with no trusted tenant context:

get_user_clinic_id(user_id) == None

A2

Unknown users cannot access tenant-owned data.

A3

Unknown users cannot create tenant-owned Patient records.

A4

No tenant-resolution path uses Clinic.first() as a fallback.

A5

Known Staff resolves to the exact associated clinic.

A6

Known Patient resolves to the exact associated clinic.

⸻

F-008 Acceptance

A7

An owner can mutate a staff resource belonging to the owner’s own clinic, subject to existing business rules.

A8

An owner cannot mutate a staff resource belonging to another clinic.

A9

A secretary cannot perform owner-only staff mutations.

A10

A patient cannot perform owner-only staff mutations.

A11

An unknown user cannot perform owner-only staff mutations.

A12

Unauthorized mutation attempts do not modify the database.

A13

Unauthorized attempts produce a safe warning log.

⸻

F-002 Acceptance

A14

The facial-analysis prompt does not request dosage, units, volume, or procedural quantities.

A15

The prompt explicitly prohibits definitive dosage/quantity instructions.

A16

Structured unsafe fields are neutralized before persistence.

A17

Unsafe free-text medical quantity instructions are blocked or safely transformed.

A18

Unsafe AI output cannot reach patient-facing delivery.

A19

Unsafe AI output cannot be persisted as a patient-facing treatment recommendation.

A20

Safe aesthetic observations and general treatment categories remain functional.

A21

Existing database schema remains unchanged.

⸻

F-003 Acceptance

A22

The active runtime provider is exactly Gemini.

A23

GeminiProvider is instantiated through the internal AI abstraction.

A24

FreeLLMAPIProvider is not instantiated by the standard runtime.

A25

No provider fallback occurs.

A26

No multi-provider runtime routing occurs.

A27

Legacy provider files may remain physically present but are unreachable from the active runtime.

A28

Missing GEMINI_API_KEY does not crash the Telegram polling process.

A29

Missing Gemini configuration produces a safe critical log.

A30

No secret value appears in logs, tests, documentation, or source code.

⸻

33. NON-NEGOTIABLE SAFETY REQUIREMENTS

The following requirements MUST NOT be weakened to make tests pass:

1. No tenant fallback.
2. No cross-tenant staff mutation.
3. No unauthorized staff mutation.
4. No autonomous patient-facing dosage.
5. No autonomous patient-facing injection units.
6. No autonomous patient-facing treatment volume.
7. No raw unsafe facial-analysis output to patients.
8. Gemini-only runtime.
9. No FreeLLMAPI runtime fallback.
10. No secret exposure.
11. No false test claims.

⸻

34. ROLLBACK PLAN

All Phase 1 changes SHOULD remain code-level and Git-reversible.

Before production deployment:

1. Create a PostgreSQL backup/snapshot.
2. Preserve Staff and Patient mappings.
3. Deploy to staging where available.
4. Run the complete Phase 1 test suite.
5. Perform smoke testing.
6. Deploy to production only after acceptance criteria are verified.

Git rollback MAY be used if necessary.

Do NOT restore insecure tenant fallback merely to recover onboarding functionality.

If rollback is required, the security implications MUST be documented.

Never place legacy API keys or credentials into rollback documentation.

⸻

35. SMOKE TEST REQUIREMENTS

Where a staging/runtime environment is available, verify:

Known Patient

Send /start from a known patient Telegram identity.

Expected:

* trusted clinic resolution
* normal authorized behavior
* no cross-tenant access

Unknown User

Send /start from an unknown Telegram identity.

Expected:

* no tenant assignment
* no Clinic.first() fallback
* safe rejection/onboarding message
* no tenant-owned record creation

Staff Authorization

Verify:

* owner + same clinic → allowed when business rules permit
* owner + different clinic → rejected
* secretary → rejected
* patient → rejected
* unknown user → rejected

Facial Analysis

Verify:

* safe observations can be produced
* dosage/units/volume requests are absent
* unsafe model output cannot reach patient delivery

Gemini

Verify:

* Gemini provider initializes through abstraction
* FreeLLMAPI is not selected
* missing API key is handled safely

⸻

36. IMPLEMENTATION REPORT REQUIREMENTS

The implementation agent MUST create:

CLINICOS_PHASE_1_IMPLEMENTATION_REPORT.md

The report MUST contain the following sections:

1. Executive Summary
2. Repository Baseline
3. Files Modified
4. Files Not Modified
5. F-001 Resolution
6. F-008 Resolution
7. F-002 Resolution
8. F-003 Resolution
9. Safety Gate Design
10. Runtime Provider Verification
11. Test Infrastructure
12. Test Execution Results
13. Static Verification Results
14. Executable Verification Results
15. Acceptance Criteria Matrix
16. Security Considerations
17. Medical Safety Considerations
18. Known Limitations
19. Deferred Findings
20. Deployment Notes
21. Rollback Notes
22. Remaining Risks
23. Final Phase 1 Status

⸻

37. ACCEPTANCE MATRIX FORMAT

The final report MUST include a table similar to:

ID	Requirement	Status	Evidence	Test
A1	Unknown user has no tenant	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A2	Unknown user cannot access tenant data	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A3	Unknown user cannot create patient	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A7	Same-clinic owner authorization	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A8	Cross-tenant mutation blocked	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A14	Facial prompt safe	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A17	Unsafe free-text blocked	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A18	Unsafe output cannot reach patient	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A22	Gemini-only runtime	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A24	FreeLLMAPI unreachable	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name
A28	Missing Gemini key non-fatal	PASS/FAIL/BLOCKED/NOT VERIFIED	exact file/function	test name

⸻

38. EVIDENCE REQUIREMENT

Every claimed resolution MUST identify concrete evidence.

Preferred evidence:

file path
function/class
specific behavior
test name
test result

Do NOT rely on statements such as:

The architecture now follows the target design.

without implementation evidence.

⸻

39. LEGACY CODE REPORTING

Legacy provider files that remain untouched MUST be explicitly listed in the final report.

The report MUST distinguish:

Legacy files physically present

from:

Legacy providers reachable by active runtime

The desired state is:

Legacy files may exist
AND
legacy providers are unreachable from production runtime

⸻

40. DEPLOYMENT SAFETY

Before declaring Phase 1 production-ready:

* tests MUST have executed
* no critical Phase 1 test may fail
* no acceptance criterion may remain falsely marked PASS
* no secret may be committed
* no database migration may be required
* Gemini runtime path must be verified
* tenant isolation must be verified
* staff authorization must be verified
* patient-facing facial-analysis safety must be verified

If these conditions cannot be established, final status MUST NOT be:

PHASE 1 COMPLETE

Instead use:

PHASE 1 BLOCKED

or:

PHASE 1 NOT VERIFIED

as appropriate.

⸻

41. FINAL STATUS RULE

The implementation agent may declare:

PHASE 1 COMPLETE

ONLY if:

1. All required implementation changes are complete.
2. All mandatory tests have been executed.
3. All critical tests pass.
4. All mandatory acceptance criteria are PASS.
5. No stop condition remains unresolved.
6. No known critical security issue remains within Phase 1 scope.
7. No known critical medical-safety issue remains within Phase 1 scope.
8. Gemini-only runtime is verified.
9. FreeLLMAPI is unreachable from the active runtime.
10. No secret has been exposed.
11. The final implementation report is complete.

Otherwise, the final status MUST be:

PHASE 1 NOT COMPLETE

with the exact blockers documented.

⸻

42. FINAL ENGINEERING PRINCIPLE

Phase 1 is not successful because the code “looks cleaner.”

Phase 1 is successful only when the repository demonstrably enforces:

NO TRUSTED TENANT
→ NO TENANT-OWNED OPERATION
NO AUTHORIZATION
→ NO MUTATION
UNSAFE AI OUTPUT
→ NO PATIENT DELIVERY
GEMINI
→ ONLY ACTIVE AI PROVIDER
LEGACY PROVIDERS
→ NOT RUNTIME REACHABLE
NO EXECUTED TEST
→ NO CLAIM OF PASS

The implementation agent MUST prioritize:

Security
>
Medical Safety
>
Correctness
>
Testability
>
Reliability
>
Minimal Scope
>
Architectural Cleanliness

Do not sacrifice security or medical safety to preserve legacy behavior.

Do not expand Phase 1 into a rewrite.

Do not claim completion without executable evidence.

⸻

43. IMPLEMENTATION COMMAND

Execute Phase 1 now according to this contract.

Before editing:

1. Inspect the repository.
2. Confirm the actual current state.
3. Identify all relevant call paths.
4. Implement only the four findings.
5. Add executable regression tests.
6. Execute the tests.
7. Perform runtime verification where possible.
8. Generate:

CLINICOS_PHASE_1_IMPLEMENTATION_REPORT.md

Do not modify unrelated architecture.

Do not delete legacy provider files.

Do not introduce database migrations.

Do not expose secrets.

Do not claim PASS without evidence.

If a stop condition is encountered, stop the affected implementation path and report the blocker instead of inventing an unsafe workaround.

END OF IMPLEMENTATION CONTRACT
