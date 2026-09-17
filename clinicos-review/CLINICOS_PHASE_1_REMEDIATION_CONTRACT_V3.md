
CLINICOS_PHASE_1_REMEDIATION_CONTRACT_V3.md

# CLINICOS PHASE 1 — REMEDIATION CONTRACT V3
## STATUS
Authoritative remediation contract for the post-implementation Phase 1 failures identified by:
`CLINICOS_PHASE_1_POST_IMPLEMENTATION_AUDIT_REPORT.md`
This contract supersedes any informal implementation instruction for the specific findings listed below.
This contract does NOT redesign Clinicos.
It does NOT authorize Phase 2 work.
It does NOT authorize unrelated refactoring.
Its sole purpose is to remediate the verified Phase 1 defects and produce executable evidence that the defects have been resolved.
---
# 1. ROLE
You are acting as a senior software engineer, application security engineer, medical-AI safety engineer, and test engineer.
Your task is to implement ONLY the remediation defined in this document.
You must:
1. Inspect the current repository.
2. Verify the reported defects against the current source.
3. Implement the minimum safe changes required to resolve them.
4. Create or repair executable tests that exercise the actual production paths.
5. Execute the relevant tests whenever the environment permits.
6. Perform static verification where runtime verification is unavailable.
7. Produce a detailed remediation report.
8. Clearly distinguish executed verification from static inspection.
Do not expand the scope.
---
# 2. AUTHORITATIVE DOCUMENTS
The following documents remain authoritative:
1. `CLINICOS_ARCHITECTURE_CHANGE_SET.md`
2. `CLINICOS_REMEDIATION_BASELINE.md`
3. `CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT_V2.md`
4. `CLINICOS_PHASE_1_POST_IMPLEMENTATION_AUDIT_REPORT.md`
5. This document:
   `CLINICOS_PHASE_1_REMEDIATION_CONTRACT_V3.md`
When interpreting the defects, the post-implementation forensic audit report is authoritative for the findings, while the Architecture Change Set and Phase 1 contracts remain authoritative for architectural requirements.
Do not weaken a requirement to make the implementation pass.
---
# 3. SCOPE
This remediation is limited to:
```text
F-002-A  P0 Medical Safety Persistence/Delivery Bypass
F-002-B  P1 Facial Analysis Runtime Exception
F-009    P1 Medical Safety Test Validity
F-001-B  Potential Cross-Tenant Patient Identity Lookup

You may modify supporting code only when strictly necessary to resolve one of these findings.

Do not perform unrelated cleanup.

Do not redesign the AI architecture.

Do not redesign the database schema unless absolutely required to eliminate the identified tenant-isolation defect.

Do not implement Phase 2 features.

⸻

4. NON-NEGOTIABLE SAFETY PRINCIPLE

The following invariant MUST hold:

NO UNVALIDATED AI-GENERATED MEDICAL CONTENT
MAY REACH PATIENTS OR APPROVED CLINIC KNOWLEDGE

The safety boundary must be enforced programmatically.

Prompt instructions are supplementary only.

⸻

5. F-002-A — MEDICAL SAFETY PERSISTENCE AND DELIVERY BYPASS

5.1 Current Finding

The forensic audit identified that:

analysis_data

is modified by the safety gate, while:

llm_response

remains the raw Gemini response.

The raw response may subsequently be used as:

FacialAnalysis.report_text

and/or patient-facing output.

This violates the safety boundary.

⸻

6. REQUIRED MEDICAL SAFETY DATA FLOW

The facial-analysis pipeline MUST follow this conceptual sequence:

Image Input
    ↓
Facial Processing
    ↓
Gemini Request
    ↓
Raw Gemini Response
    ↓
Parse
    ↓
Normalize
    ↓
Programmatic Safety Gate
    ↓
Validated Safe Representation
    ↓
Persistence
    ↓
PDF / Report Generation
    ↓
Patient Delivery

The raw Gemini response MUST NOT bypass the safety gate.

⸻

7. RAW RESPONSE IS NEVER PATIENT-FACING

After Gemini returns:

llm_response

that variable must be considered untrusted.

It MUST NOT be directly used for:

* patient replies
* PDF content
* patient reports
* FacialAnalysis.report_text
* KnowledgeItem content
* approved recommendation fields
* any other approved patient-facing medical content

unless it has passed through an explicit safety-validation and normalization path.

⸻

8. SAFE REPRESENTATION REQUIREMENT

After successful parsing and safety validation, construct a canonical safe representation.

For example:

safe_analysis_data

or an equivalent clearly named object.

The exact variable name is implementation-dependent.

The important invariant is:

DATABASE
PDF
PATIENT MESSAGE
KNOWLEDGE BASE

must all derive from the validated representation.

They must not independently consume the raw LLM response.

⸻

9. F-002-A — PARSE FAILURE

JSON parsing failure MUST NOT create a raw-response delivery bypass.

If:

json.loads(llm_response)

fails:

The system MUST NOT:

report_text = llm_response

and then send that text to the patient.

The system must instead produce a safe failure state.

Acceptable behavior includes:

safe generic user-facing message
+
no unsafe AI content
+
optional internal diagnostic logging

The raw response may be retained for internal debugging ONLY if doing so complies with the existing privacy/security requirements.

It must never become patient-facing approved medical content.

⸻

10. F-002-A — PARSE SUCCESS

If JSON parsing succeeds:

1. Validate the expected structure.
2. Normalize the data.
3. Apply the programmatic medical safety gate.
4. Remove, neutralize, or reject unsafe content.
5. Produce the canonical safe representation.
6. Use ONLY that safe representation for persistence and delivery.

The raw response must not be used as a fallback.

⸻

11. F-002-A — SAFETY GATE REQUIREMENTS

The gate must inspect ALL relevant patient-facing content.

Do not restrict the gate to:

estimated_units
estimated_volume
description

It must account for all relevant fields generated by the model, including nested structures.

At minimum inspect:

recommendations
treatment names
treatment types
descriptions
summaries
rationales
areas
dosages
doses
volumes
units
concentrations
frequencies
durations
medications
procedural instructions
disclaimers
free-text fields
nested dictionaries
lists

The exact schema may differ in the repository.

Audit the actual schema and enforce safety over the actual patient-facing output structure.

⸻

12. F-002-A — PRESCRIPTIVE CONTENT

The patient-facing facial-analysis result must not provide AI-generated:

* exact dosing
* injection units
* medication dosage
* treatment volume
* concentration instructions
* prescription instructions
* procedural instructions that constitute individualized medical treatment orders

Examples that MUST NOT survive into patient-facing output include patterns such as:

10 units
10 U
1 ml
1 mL
1 cc
0.5 cc
20 mg
20mg
2% concentration
inject 10 units
administer 20 mg
use 1 mL

Do not assume one regex is sufficient.

The implementation must use a reasonable defense-in-depth approach appropriate to the existing data model.

⸻

13. F-002-A — SAFETY RESPONSE STRATEGY

For unsafe content, choose a deterministic safe behavior.

Acceptable strategies include:

Strategy A — Reject the unsafe recommendation

Remove the unsafe recommendation entirely.

Strategy B — Neutralize unsafe fields

Replace unsafe content with a safe non-prescriptive statement.

Strategy C — Reject the complete AI analysis

Return a generic safe message and require clinician review.

The selected strategy must be deterministic and must prevent unsafe content from reaching the patient.

Do not preserve unsafe content merely because another field appears safe.

⸻

14. F-002-A — PERSISTENCE INVARIANT

Before any database write related to facial analysis, prove that the data being persisted is safe.

Audit every write involving:

FacialAnalysis
TreatmentRecommendation
KnowledgeItem

and any other relevant model.

The persisted patient-facing report MUST derive from the validated representation.

Unsafe raw LLM output MUST NOT be stored as approved medical content.

⸻

15. F-002-A — KNOWLEDGE BASE PROTECTION

The audit identified a particularly dangerous path:

JSON parse failure
    ↓
raw llm_response
    ↓
save_to_knowledge
    ↓
KnowledgeItem

This MUST be eliminated.

AI-generated facial-analysis output must not automatically become authoritative clinic knowledge merely because it was generated successfully.

If the current behavior automatically calls:

save_to_knowledge(...)

inspect its semantics carefully.

Do not allow unverified or unsafe model output to poison the clinic knowledge base.

If Phase 1 requirements permit the knowledge write, ensure only validated safe content reaches it.

If the operation is not required for Phase 1, safely prevent unsafe/raw content from entering the knowledge base.

Do not redesign the Knowledge subsystem.

⸻

16. F-002-B — UNBOUNDLOCALERROR

The audit identified a runtime defect where:

report_text

may be referenced before assignment after successful JSON parsing and PDF generation.

This MUST be fixed.

The implementation must ensure that every execution path either:

1. assigns a safe value to report_text, or
2. does not reference it.

No execution path may raise:

UnboundLocalError

because of this variable.

⸻

17. F-002-B — NO RAW FALLBACK

Do NOT solve the UnboundLocalError by simply doing:

report_text = llm_response

at the top.

That would reintroduce the medical safety vulnerability.

Initialization must use a safe default and subsequent assignment must derive from validated content.

The fix must solve BOTH:

runtime correctness
AND
medical safety

⸻

18. F-002 — PATIENT DELIVERY

Trace the exact final patient-facing response.

Verify:

patient reply
PDF
document
photo
report

all derive from the safe representation.

There must be no alternative path that sends:

llm_response

directly.

Search the complete facial-analysis handler for every occurrence of:

llm_response
report_text
answer
reply_text
send_document
send_message
reply_document

and trace each use.

⸻

19. F-001-B — CROSS-TENANT PATIENT IDENTITY

The forensic audit identified a potential tenant-isolation problem:

get_or_create_patient_by_telegram
    ↓
get_patient_by_telegram_id
    ↓
global PatientAlias lookup

The lookup may not enforce tenant ownership.

This must be independently verified before changing code.

⸻

20. F-001-B — REQUIRED INVESTIGATION

Inspect:

get_or_create_patient_by_telegram
get_patient_by_telegram_id
Patient
PatientAlias

and every relevant caller.

Determine:

1. How Telegram identity is stored.
2. Whether PatientAlias is globally unique.
3. Whether the same Telegram identity can appear in multiple clinics.
4. Whether patient lookup is clinic-aware.
5. Whether an existing patient can be returned from another clinic.
6. Whether patient creation can merge identities across tenants.
7. Whether a caller supplies a trusted clinic ID.
8. Whether that clinic ID is validated against the actor.

Do not assume the audit finding is correct without tracing the implementation.

⸻

21. F-001-B — REQUIRED TENANT INVARIANT

For an operation operating under:

trusted_clinic_id = A

the system MUST NOT return or mutate a patient belonging to:

clinic B

where:

B != A

A cross-tenant identity must result in safe rejection or an explicitly isolated identity-handling path.

It must never silently merge or return the foreign patient.

⸻

22. F-001-B — UNKNOWN CLINIC

If:

trusted_clinic_id is None

the operation must fail closed.

It must NOT:

* search globally and accept the first match
* infer a clinic
* use Clinic.first()
* use a default clinic
* use another patient’s clinic
* use an arbitrary clinic

⸻

23. F-001-B — NO CLIENT-SUPPLIED TENANT AUTHORITY

Do not trust a client-supplied:

clinic_id

as the authoritative tenant boundary.

The trusted tenant must derive from server-side identity/authentication.

If a clinic ID is passed as an argument for technical reasons, verify that it matches the trusted actor context.

⸻

24. F-009 — TESTING REQUIREMENT

The medical safety tests MUST test the actual production behavior.

The test must NOT merely copy the implementation logic.

This is prohibited:

for rec in analysis_data.get("recommendations", []):
    ...

when that logic is simply duplicated inside the test without invoking the production safety boundary.

Tests must fail if the production safety gate is removed or broken.

⸻

25. F-009 — REQUIRED MEDICAL SAFETY TESTS

Create executable tests that exercise the actual production path.

At minimum cover:

Test 1 — Unsafe Structured Content

Provide model output containing:

estimated_units
estimated_volume

and verify the final patient-facing/persisted representation is safe.

Test 2 — Unsafe Free Text

Provide unsafe content in:

description
summary
rationale

and verify it cannot reach the patient.

Test 3 — Unsafe Nested Content

Place unsafe text inside nested structures or lists where applicable.

Verify it cannot bypass the safety gate.

Test 4 — JSON Parse Failure

Make the model return malformed/non-JSON output containing unsafe medical instructions.

Verify:

raw response is NOT sent to patient
raw response is NOT persisted as approved medical content

Test 5 — Successful Facial Analysis

Mock the Gemini response with safe valid data.

Execute the real facial-analysis production path.

Verify:

no UnboundLocalError

and verify the final response is delivered successfully.

Test 6 — Persistence Safety

Verify the object written to the database is derived from the validated representation.

It must not contain unsafe raw model output.

Test 7 — Knowledge Safety

If facial-analysis output can enter KnowledgeItem, verify that only safe validated content can be stored.

⸻

26. F-009 — TEST PRODUCTION BOUNDARY

Tests must invoke the actual production boundary.

Prefer:

perform_facial_analysis

or the actual lower-level production safety function if one exists.

Mock only external dependencies such as:

* Gemini API
* Telegram network
* database where appropriate
* PDF generation where appropriate

Do NOT mock away the safety logic itself.

⸻

27. F-009 — TEST DATA FLOW

A valid test should conceptually look like:

Mock Gemini response
        ↓
Actual production handler
        ↓
Actual parser
        ↓
Actual safety gate
        ↓
Actual persistence/delivery boundary
        ↓
Assertions

Not:

Copy safety logic into test
        ↓
Run copied logic
        ↓
PASS

⸻

28. F-009 — TENANT TESTS

Add or repair tests for:

Unknown user

unknown Telegram identity
+
no trusted clinic
=
rejected

Existing patient same clinic

Clinic A
+
patient belonging to Clinic A
=
allowed

Existing patient different clinic

Clinic A
+
patient belonging to Clinic B
=
rejected

No first-clinic fallback

Verify no path resolves an unknown user to:

db.query(Clinic).first()

⸻

29. F-009 — AUTHORIZATION REGRESSION TESTS

Do not remove existing authorization tests.

Ensure these continue to pass:

owner + same clinic + valid staff
    → allowed
owner + different clinic + valid staff
    → denied
secretary + same clinic
    → denied
unknown actor
    → denied

Only add tests directly relevant to this remediation.

⸻

30. F-003 — GEMINI REGRESSION PROTECTION

This remediation MUST NOT reintroduce legacy AI providers.

After changes, verify:

Gemini = active AI provider
FreeLLMAPI = inactive
DeepSeek = inactive
OpenRouter = inactive
OpenAI = inactive
Mistral = inactive

Do not delete legacy provider files merely because they are inactive.

Do not add provider fallback.

⸻

31. NO MULTI-PROVIDER FALLBACK

The following architecture remains mandatory:

Application
    ↓
AI Abstraction
    ↓
Gemini

If Gemini fails, acceptable behavior includes:

* retry
* timeout
* circuit breaker
* queue
* safe degradation
* deterministic response
* human handoff

NOT:

Gemini
    ↓ failure
FreeLLMAPI

or any other provider substitution.

⸻

32. MINIMUM-CHANGE PRINCIPLE

Use the smallest reasonable implementation that fully resolves the findings.

Do not:

* rewrite the facial-analysis subsystem
* rewrite the provider architecture
* migrate the database
* introduce a new framework
* redesign the Telegram bot
* implement RAG
* implement a new event system
* implement Phase 2
* redesign the entire authorization system

Only fix what is necessary.

⸻

33. DATABASE MIGRATION RESTRICTION

Do not create a database migration unless the tenant-isolation finding cannot be safely fixed without one.

If a migration appears necessary:

1. Stop before creating it.
2. Document why it is required.
3. Do not silently introduce schema changes.
4. Report the blocker.

⸻

34. ERROR HANDLING

All newly modified failure paths must:

* fail safely
* avoid leaking raw model output
* avoid leaking secrets
* avoid exposing internal stack traces to patients
* avoid leaving partial unsafe medical state
* close database resources correctly
* preserve existing application behavior where safe

⸻

35. LOGGING

Internal logging may contain diagnostic information only when consistent with the existing privacy/security requirements.

Do not log:

* API keys
* bot tokens
* credentials
* unnecessary patient-sensitive content
* full raw medical model output unless explicitly justified and already permitted

Prefer structured diagnostics such as:

medical_safety_blocked
medical_output_parse_failed
medical_output_validation_failed
tenant_mismatch
authorization_denied

⸻

36. REQUIRED IMPLEMENTATION ORDER

Perform the work in this order:

Step 1

Inspect and verify the current source.

Step 2

Fix F-002-A medical safety data-flow bypass.

Step 3

Fix F-002-B UnboundLocalError.

Step 4

Verify and fix F-001-B cross-tenant patient identity handling if confirmed.

Step 5

Replace invalid medical safety tests with real production-path tests.

Step 6

Add required tenant-isolation tests.

Step 7

Run tests.

Step 8

Run static checks.

Step 9

Review all modified files for unintended changes.

Step 10

Produce the remediation report.

Do not proceed to unrelated work.

⸻

37. REQUIRED VERIFICATION

If the environment permits execution, run at minimum:

pytest tests/

Also attempt appropriate static checks such as:

python -m compileall .

and relevant import checks.

Record exact commands and results.

⸻

38. EXECUTION STATUS RULES

Use:

PASS

only when the relevant behavior has been verified.

Use:

FAIL

when evidence shows the implementation violates the requirement.

Use:

BLOCKED

when required runtime verification cannot be performed because of environment limitations.

Use:

NOT VERIFIED

when evidence is insufficient.

Do not convert static inspection into runtime PASS.

⸻

39. TEST QUALITY REQUIREMENT

A test is valid only if:

1. It exercises production behavior.
2. It asserts the required invariant.
3. It can fail when production behavior is broken.
4. It does not simply duplicate implementation code.
5. Its mocks do not bypass the security/safety boundary being tested.

⸻

40. REQUIRED MUTATION-STYLE THINKING

For the critical safety tests, mentally verify:

“If the production safety gate were deleted or bypassed, would this test fail?”

If the answer is NO:

the test is insufficient.

For tenant isolation:

“If the first-clinic fallback or cross-tenant lookup were reintroduced, would this test fail?”

If NO:

the test is insufficient.

For Gemini:

“If FreeLLMAPI were reintroduced into the active provider graph, would this test fail?”

If NO:

the test is insufficient.

⸻

41. REQUIRED REPORT

After implementation and verification, create:

CLINICOS_PHASE_1_REMEDIATION_REPORT_V3.md

The report must contain:

CLINICOS PHASE 1 — REMEDIATION REPORT V3

1. Remediation Metadata

Include:

* date
* repository state
* commit/hash if available
* execution environment
* tests executed
* tests blocked
* authoritative documents

⸻

2. Overall Status

Use exactly one:

PHASE 1 REMEDIATION PASS
PHASE 1 REMEDIATION FAIL
PHASE 1 REMEDIATION BLOCKED
PHASE 1 REMEDIATION NOT VERIFIED

Do not use:

statically complete

as an overall completion status.

⸻

42. FINDING STATUS MATRIX

Create:

Finding	Severity	Status	Evidence	Test Evidence	Notes
F-002-A	P0	…	…	…	…
F-002-B	P1	…	…	…	…
F-009	P1	…	…	…	…
F-001-B	P1/P0 if applicable	…	…	…	…

Use the actual severity justified by the evidence.

⸻

43. FILE CHANGE INVENTORY

Report:

Modified Files

List every modified file.

Created Files

List every created file.

Deleted Files

List every deleted file.

Unexpected Changes

Identify anything outside the remediation scope.

⸻

44. F-002 MEDICAL SAFETY VERIFICATION

Explain:

1. Raw LLM response handling.
2. Parsing behavior.
3. Safety gate location.
4. Safety gate scope.
5. Persistence path.
6. PDF path.
7. Patient delivery path.
8. Knowledge-base path.
9. Parse-error behavior.
10. Exception behavior.

Include exact file/function references.

⸻

45. F-001 TENANT VERIFICATION

Explain:

1. Telegram identity resolution.
2. Clinic resolution.
3. Patient lookup.
4. PatientAlias behavior.
5. Existing patient handling.
6. Cross-tenant behavior.
7. Unknown-user behavior.

⸻

46. TEST VERIFICATION

Report:

Total tests collected:
Passed:
Failed:
Skipped:
Errors:
Blocked:

List important test names.

Explicitly identify any test that is static-only or insufficient.

⸻

47. RUNTIME VERIFICATION

For each executed command provide:

Command:
Result:
Exit status:
Interpretation:

If execution was blocked, explain exactly why.

⸻

48. REGRESSION CHECK

Verify that remediation did not reintroduce:

* FreeLLMAPI runtime
* multi-provider fallback
* tenant fallback
* authorization bypass
* direct raw LLM delivery
* secret leakage

⸻

49. FINAL ACCEPTANCE RULE

Phase 1 remediation may be declared:

PHASE 1 REMEDIATION PASS

ONLY if:

1. F-002-A is resolved.
2. F-002-B is resolved.
3. F-009 is resolved.
4. F-001-B is resolved if the audit confirms the vulnerability.
5. No P0 regression exists.
6. Required executable tests pass, when the environment permits execution.
7. No raw unsafe AI output can reach patients through the audited facial-analysis path.
8. No raw unsafe AI output can enter approved clinic knowledge through that path.
9. Gemini-only runtime remains intact.
10. Tenant isolation remains intact.
11. Authorization remains intact.

If required execution is blocked:

Do NOT claim PASS.

Use:

PHASE 1 REMEDIATION BLOCKED

unless the evidence supports another status.

⸻

50. CRITICAL FINAL INSTRUCTION

Do not optimize for making the report say PASS.

Optimize for making the implementation actually satisfy the requirements.

Do not hide failures.

Do not reinterpret failures as warnings.

Do not claim tests passed if they were not executed.

Do not claim production behavior is verified if only static inspection was possible.

Do not report a test as valid if it merely duplicates production logic.

Do not silently modify unrelated files.

Do not proceed to Phase 2.

The objective is not to make Clinicos appear complete.

The objective is to make the identified Phase 1 security, medical-safety, reliability, tenant-isolation, and testing defects actually correct and demonstrably verified.

After completing the remediation, output the complete contents of:

CLINICOS_PHASE_1_REMEDIATION_REPORT_V3.md

and clearly state the final verification status.
