CLINICOS_PHASE_1_POST_IMPLEMENTATION_AUDIT_PROMPT.md

# CLINICOS PHASE 1 — POST-IMPLEMENTATION FORENSIC AUDIT PROMPT
## ROLE
You are acting as a senior software security auditor, application architect, and medical-AI safety engineer.
You are auditing the CURRENT Clinicos repository AFTER the Phase 1 implementation was performed.
This is a FORENSIC AUDIT.
You are NOT an implementer during this task.
You must NOT modify, create, delete, rename, refactor, format, or otherwise alter ANY repository file.
Your job is to determine whether the implemented Phase 1 changes actually satisfy the authoritative architecture, remediation baseline, and Phase 1 implementation contract.
Do not assume that an implementation is correct because the previous implementation report says it is complete.
Treat the repository itself as the primary source of truth.
---
# 1. AUTHORITATIVE DOCUMENTS
The following documents define the requirements you must audit against:
1. `CLINICOS_ARCHITECTURE_CHANGE_SET.md`
2. `CLINICOS_REMEDIATION_BASELINE.md`
3. `CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT_V2.md`
These documents are authoritative for this audit.
If the implementation report conflicts with the repository or these authoritative documents, the repository and authoritative documents take precedence.
If an older document conflicts with `CLINICOS_ARCHITECTURE_CHANGE_SET.md`, follow the Architecture Change Set.
Do not reinterpret requirements to make the current implementation pass.
---
# 2. AUDIT OBJECTIVE
Determine whether Phase 1 is genuinely complete.
The audit must independently verify:
- F-001 Tenant Isolation
- F-002 Medical Safety
- F-003 Gemini-Only Runtime
- F-004 Communication Architecture
- F-005 Reliability
- F-006 Knowledge Retrieval
- F-007 Client/Business Logic Separation
- F-008 Authorization
The primary implementation targets are F-001, F-002, F-003, and F-008.
F-004 through F-007 must also be checked for regression, unintended changes, or accidental violations introduced by the Phase 1 implementation.
Do not assume that unchanged code is correct merely because Phase 1 did not explicitly modify it.
---
# 3. ABSOLUTE AUDIT RULES
## 3.1 NO MODIFICATIONS
Do not modify the repository.
Do not:
- edit files
- create files
- delete files
- rename files
- install project dependencies
- change configuration
- modify environment variables
- change database state
- change production data
- commit changes
- generate patches
- auto-fix lint errors
- auto-format files
Read-only investigation only.
If a command would modify repository state, do not run it.
---
## 3.2 NO ASSUMPTIONS
Never conclude that something works merely because:
- the code looks reasonable
- a function exists
- a test exists
- a report claims success
- a prompt says the model should behave safely
- a provider file exists
- a security check appears to be present
You must trace the actual execution path.
---
## 3.3 EVIDENCE REQUIRED
Every important finding must include:
- exact file path
- exact function/class/module
- relevant line number or line range where available
- concise explanation of the evidence
- impact
- PASS / FAIL / BLOCKED / NOT VERIFIED classification
Do not make unsupported claims.
---
# 4. FIRST STEP — REPOSITORY INTEGRITY CHECK
Before auditing individual findings:
1. Inspect repository status.
2. Inspect the complete directory tree.
3. Identify all files modified during Phase 1.
4. Identify any modified files not mentioned in the previous implementation report.
5. Inspect the relevant git diff if available.
6. Compare the actual changed files against the previous implementation report.
7. Identify uncommitted changes.
8. Identify newly created test files.
9. Identify deleted or renamed files.
10. Verify whether any secrets, API keys, tokens, credentials, or environment values were introduced.
Do not expose any real secret values in your report.
If secrets are discovered, report only:
- file path
- variable name
- type of secret
- whether it is tracked or untracked
Never print the secret itself.
---
# 5. EXPECTED PHASE 1 FILES
The previous implementation reported modifications to files including:
- `clinicos-main/utils/role_utils.py`
- `clinicos-main/llm/providers/__init__.py`
- `clinicos-main/patient_agent.py`
- `clinicos-main/handlers/facial_analysis.py`
- `clinicos-main/bot.py`
And tests including:
- `tests/conftest.py`
- `tests/test_tenant_isolation.py`
- `tests/test_authorization.py`
- `tests/test_medical_safety.py`
- `tests/test_gemini_runtime.py`
And:
- `CLINICOS_PHASE_1_IMPLEMENTATION_REPORT.md`
Do NOT assume this list is complete.
Search the entire repository for all changes and dependencies.
Report:
### Expected Changed Files
Files explicitly reported as changed.
### Unexpected Changed Files
Files actually changed but not reported.
### Missing Expected Changes
Files that should have changed according to the contract but did not.
---
# 6. F-001 — TENANT ISOLATION
## Requirement
Clinicos must never infer a user's clinic from an arbitrary database record.
There must be no fallback such as:
```python
db.query(Clinic).first()

for tenant resolution.

If a trusted user-to-clinic relationship cannot be established:

clinic_id = None

or an equivalent fail-closed result must occur.

Tenant-owned operations must then be rejected.

⸻

6.1 Audit get_user_clinic_id

Inspect:

clinicos-main/utils/role_utils.py

Audit:

get_user_clinic_id

Verify:

1. Staff identity resolution.
2. Patient identity resolution.
3. Behavior for unknown users.
4. Behavior for users with incomplete identity records.
5. Behavior for users with invalid clinic relationships.
6. Whether any fallback clinic exists.
7. Whether a first clinic is ever selected.
8. Whether tenant identity can be inferred from unrelated records.
9. Whether database sessions are safely closed.
10. Whether errors fail closed.

Search the entire repository for:

get_user_clinic_id(

Audit EVERY caller.

For every caller, verify that:

clinic_id is None

cannot accidentally become:

* first clinic
* default clinic
* global clinic
* arbitrary clinic
* null interpreted as unrestricted access

⸻

7. F-001 — PATIENT CREATION AND EXISTING PATIENT LOOKUP

Inspect:

bot.py

especially:

get_or_create_patient_by_telegram

Audit both branches:

Existing patient

Verify that an existing patient returned by Telegram identity lookup belongs to the trusted clinic context.

A function must not simply return an existing patient without verifying tenant ownership if a clinic context is supplied.

Explicitly test the conceptual scenario:

Actor clinic = A
Telegram identity belongs to patient in clinic B

Determine whether the function:

* rejects
* returns cross-tenant patient
* silently rebinds
* creates duplicate identity
* behaves ambiguously

Any cross-tenant object exposure is a FAIL.

New patient

Verify that:

* unknown user + no trusted clinic = reject
* new patient cannot be created without trusted clinic
* patient is created only under the authenticated/trusted clinic
* no global fallback exists

⸻

8. F-001 — CROSS-TENANT ACCESS SEARCH

Search the entire repository for patterns such as:

Clinic.first
query(Clinic).first
first()
clinic_id =
clinic_id=
Patient.query
Staff.query
db.query(Staff)
db.query(Patient)

Do not automatically classify every occurrence as a vulnerability.

Determine whether any operation can access or mutate another tenant’s data without an explicit tenant boundary.

Audit:

* patient reads
* patient writes
* staff reads
* staff writes
* appointments
* knowledge items
* treatment records
* facial analysis records
* reports
* conversations
* leads
* follow-ups
* clinic settings

Report only evidence-based findings.

⸻

9. F-008 — AUTHORIZATION

Audit all staff-management authorization paths.

At minimum inspect:

add_staff_confirm
remove_staff_callback

Verify that authorization follows:

authenticated actor
        ↓
trusted identity
        ↓
trusted clinic
        ↓
required role
        ↓
target object exists
        ↓
target object belongs to same clinic
        ↓
mutation

The mutation must happen ONLY after all authorization checks pass.

⸻

10. F-008 — OWNER-ONLY STAFF MUTATIONS

For each staff mutation:

Verify:

1. Actor identity is resolved.
2. Actor clinic is resolved.
3. Missing clinic fails closed.
4. Actor role is explicitly checked.
5. Required role is OWNER.
6. Target staff exists.
7. Target staff belongs to actor’s clinic.
8. Cross-tenant target is rejected.
9. Unauthorized users cannot mutate.
10. No mutation occurs on authorization failure.

Check both:

Add Staff

Verify the created staff record uses the actor’s trusted clinic.

It must NOT accept an arbitrary client-provided clinic ID as authoritative.

Remove Staff

Verify the target staff is checked against actor clinic before deletion.

Also inspect:

* malformed callback data
* invalid staff IDs
* missing staff
* cross-tenant staff
* non-owner actor
* unknown actor

Determine whether each path fails safely.

⸻

11. F-002 — MEDICAL SAFETY

This is the highest-priority audit area.

The safety requirement is NOT satisfied merely by modifying an LLM prompt.

The implementation must have a programmatic safety boundary.

The required conceptual flow is:

patient input
    ↓
medical/image processing
    ↓
LLM request
    ↓
LLM output
    ↓
parse
    ↓
PROGRAMMATIC SAFETY GATE
    ↓
validated safe representation
    ↓
persistence
    ↓
PDF/report generation
    ↓
patient delivery

Unsafe content must not bypass the gate.

⸻

12. F-002 — FULL FACIAL ANALYSIS EXECUTION TRACE

Inspect the COMPLETE implementation of:

clinicos-main/handlers/facial_analysis.py

Especially:

perform_facial_analysis

Do not inspect only the changed lines.

Trace the entire function from:

1. image reception
2. image validation
3. facial processing
4. prompt construction
5. LLM invocation
6. response parsing
7. safety validation
8. database persistence
9. PDF/report creation
10. Telegram delivery
11. exception handling
12. fallback behavior

Document the exact execution sequence.

⸻

13. F-002 — SAFETY GATE LOCATION

Determine exactly where the programmatic safety gate occurs.

It MUST occur:

AFTER LLM output exists
AND
AFTER parsing/normalization
AND
BEFORE persistence
AND
BEFORE patient delivery

If unsafe content is persisted before validation:

FAIL.

If unsafe content can be sent to the patient before validation:

FAIL.

If safety filtering happens only during PDF generation:

FAIL.

If safety filtering happens only in Telegram delivery:

FAIL.

If only the prompt attempts to prevent unsafe output:

FAIL.

⸻

14. F-002 — SAFETY GATE SCOPE

Do not assume checking only:

estimated_units
estimated_volume
description

is sufficient.

Inspect the complete output schema.

Identify every patient-facing field, including but not limited to:

* recommendation
* treatment type
* treatment name
* description
* summary
* rationale
* area
* dosage
* dose
* volume
* units
* concentration
* frequency
* duration
* medication
* prescription
* procedural instructions
* disclaimers
* generated report text
* nested dictionaries
* lists
* arbitrary model-generated strings

Determine whether unsafe content can appear in another field and bypass the gate.

⸻

15. F-002 — NUMERIC DOSING / PRESCRIPTIVE CONTENT

The system must not deliver patient-facing prescriptive treatment dosing generated by the AI.

Audit whether the gate catches variations such as:

10 units
10 unit
10U
10 U
1 ml
1 mL
1 cc
0.5 cc
20 mg
20mg
2% concentration
inject 10 units
use 1 mL
administer 20 mg

Also inspect non-numeric prescriptive language.

The audit should determine whether the implementation:

* blocks unsafe output
* safely transforms it
* rejects the entire response
* accidentally allows it

A narrow regex is not automatically sufficient.

Evaluate actual coverage.

⸻

16. F-002 — RAW LLM RESPONSE LEAKAGE

This is mandatory.

Inspect every variable holding the raw LLM response.

Examples:

llm_response
response_text
report_text
raw_response

Determine whether the raw LLM output can reach:

* Telegram
* PDF
* database
* logs
* exception messages
* user-visible error messages

especially when:

json.loads(...)

fails.

A parse failure must NOT create a bypass where unsafe raw LLM text is delivered directly.

If raw LLM output can reach a patient without passing through the safety gate:

FAIL.

⸻

17. F-002 — PERSISTENCE SAFETY

Inspect every database write after facial analysis.

Determine:

1. What exact data is persisted?
2. Is it the raw LLM output?
3. Is it normalized output?
4. Is it safety-gated output?
5. Can unsafe fields survive in database objects?
6. Can a partially unsafe recommendation still be persisted?

The rule is:

unsafe AI output must not be persisted as approved patient-facing medical content.

If persistence occurs before safety validation:

FAIL.

⸻

18. F-002 — DELIVERY SAFETY

Trace the exact data passed to:

* PDF generator
* Telegram message sender
* document sender
* any other patient-facing channel

Verify that the exact object delivered is derived from safety-gated content.

Do not accept a conclusion based on the fact that the gate exists elsewhere in the function.

Trace data flow.

⸻

19. F-002 — PROMPT SAFETY

Inspect the new facial-analysis prompt.

Verify that it no longer requests:

* exact dosing
* units
* volumes
* definitive prescriptions
* definitive diagnosis
* guaranteed outcomes

However:

A safe prompt alone is NOT sufficient.

Classify prompt-level protection separately from programmatic enforcement.

⸻

20. F-002 — HUMAN REVIEW REQUIREMENT

Compare the current implementation against the Phase 1 contract.

Determine whether human review is required for this phase.

If human review is required, determine whether there is an actual enforcement gate.

Do not count text such as:

consult a clinician

as a human-review gate unless the system actually prevents patient delivery until review occurs.

⸻

21. F-003 — GEMINI-ONLY RUNTIME

The target runtime is:

Google Gemini only

No FreeLLMAPI runtime.

No DeepSeek runtime.

No OpenRouter runtime.

No OpenAI runtime.

No Mistral runtime.

No provider fallback.

No dynamic provider substitution.

The internal AI abstraction may remain.

Multiple Gemini models are allowed.

⸻

22. F-003 — PROVIDER GRAPH AUDIT

Inspect:

patient_agent.py
llm/provider_manager.py
llm/provider_router.py
llm/providers/

Reconstruct the runtime provider graph.

Determine:

1. Where ProviderManager is instantiated.
2. What providers are passed to it.
3. Whether exactly Gemini is active.
4. Whether provider registration can inject legacy providers.
5. Whether ProviderRouter can discover providers dynamically.
6. Whether ProviderRouter can select legacy providers.
7. Whether failure of Gemini causes another provider to be attempted.
8. Whether any fallback path exists.
9. Whether environment variables can activate another provider.
10. Whether imports instantiate legacy providers indirectly.

⸻

23. F-003 — LEGACY PROVIDER SEARCH

Search the entire repository for:

FreeLLMAPIProvider
freellmapi
DeepSeekProvider
deepseek
OpenRouterProvider
openrouter
OpenAIProvider
openai
MistralProvider
mistral

Classify every occurrence:

* active runtime
* imported but unreachable
* dead code
* test-only
* documentation-only
* configuration-only
* dangerous fallback path

Legacy files may remain physically present.

Their physical existence is NOT itself a failure.

Their ability to participate in the active runtime IS a failure.

⸻

24. F-003 — MISSING GEMINI KEY

Inspect behavior when:

GEMINI_API_KEY

is missing.

The contract allows the application to start in a degraded state if explicitly designed that way.

Verify:

* no legacy provider activates
* no fallback provider activates
* no silent provider substitution occurs
* diagnostics clearly identify missing Gemini configuration
* AI-dependent operations fail safely

Do not treat “application starts” as equivalent to “AI works.”

⸻

25. F-003 — PROVIDER ROUTER

Inspect:

llm/provider_router.py

Even if it was not modified.

Verify that the router cannot:

* fall back to FreeLLMAPI
* fall back to DeepSeek
* fall back to OpenRouter
* select a provider based on score
* discover providers from arbitrary configuration
* dynamically switch to a non-Gemini provider

If ProviderRouter is retained only for compatibility, prove that it is effectively Gemini-only at runtime.

⸻

26. F-003 — PROVIDER MANAGER

Inspect:

llm/provider_manager.py

Determine whether its design allows:

providers = {
    "gemini": ...,
    "freellmapi": ...
}

to be passed accidentally.

If the abstraction permits arbitrary providers but the runtime supplies only Gemini, classify this as:

acceptable architecture

provided that no active call path can introduce or select another provider.

⸻

27. F-004 — COMMUNICATION ARCHITECTURE REGRESSION

Inspect whether Phase 1 introduced or preserved direct Telegram API usage in new code.

Search for:

requests.post
api.telegram.org
Bot(
send_message
send_document
send_photo

Identify direct communication calls.

Determine whether they are:

* existing legacy architecture
* Phase 1 changes
* new regressions

Do not expand the scope unnecessarily, but report material Phase 1 regressions.

⸻

28. F-005 — RELIABILITY REGRESSION

Inspect Phase 1 changes for:

* blocking operations
* unhandled exceptions
* retry loops
* unsafe database transactions
* resource leaks
* failure paths that leave partial state

Pay particular attention to:

database writes
LLM calls
PDF generation
Telegram delivery

Determine whether Phase 1 introduced new partial-failure scenarios.

⸻

29. F-006 — KNOWLEDGE REGRESSION

Inspect whether Phase 1 changes modified the existing knowledge retrieval behavior.

Do not redesign F-006 in this audit.

Only identify:

* regressions
* unintended behavior
* security implications
* tenant isolation implications

If the existing system uses exact matching rather than RAG, record this as existing architecture unless Phase 1 was required to fix it.

⸻

30. F-007 — CLIENT / BUSINESS LOGIC REGRESSION

Inspect whether Phase 1 changes added new business logic directly into Telegram handlers.

Determine whether any new code:

* creates business objects directly from untrusted client data
* bypasses service-layer authorization
* accepts client-provided clinic IDs
* performs business decisions without policy enforcement

Again, distinguish:

pre-existing architecture

from:

Phase 1 regression

⸻

31. TEST FORENSIC AUDIT

This section is mandatory.

Do not assume tests are valid simply because they exist.

Inspect every Phase 1 test.

⸻

32. TEST INVENTORY VS ACCEPTANCE MATRIX

Compare:

CLINICOS_PHASE_1_IMPLEMENTATION_CONTRACT_V2.md

acceptance criteria against the actual tests.

For every claimed test, verify:

1. Does the test actually exist?
2. Does the test name match?
3. Does it exercise the actual production path?
4. Does it assert the required behavior?
5. Could it pass even if production code were broken?
6. Does it use mocks that bypass the behavior being tested?

Identify “phantom tests” where the implementation report claims a test exists but it does not.

⸻

33. MEDICAL SAFETY TEST VALIDITY

Inspect:

tests/test_medical_safety.py

This is especially important.

Determine whether the test:

* imports the real safety gate
* invokes the actual production function/path
* passes unsafe output through the real implementation
* verifies that unsafe content is blocked before persistence
* verifies that unsafe content is blocked before delivery

A test that simply duplicates the production regex or safety logic inside the test is NOT a valid integration test.

If the test manually recreates the production safety logic without calling it, classify it as insufficient.

⸻

34. GEMINI TEST VALIDITY

Inspect:

tests/test_gemini_runtime.py

Verify that tests establish:

* Gemini is present when configured
* GeminiProvider is the active provider
* no FreeLLMAPI provider is active
* no legacy provider is reachable
* no fallback occurs
* missing Gemini key does not activate another provider

A test that only asserts:

"freellmapi" not in providers

is insufficient to establish Gemini-only runtime.

⸻

35. TENANT TEST VALIDITY

Inspect:

tests/test_tenant_isolation.py

Verify tests cover:

1. unknown user
2. unknown user cannot create patient
3. existing patient same clinic
4. existing patient wrong clinic
5. cross-tenant object access
6. absence of first-clinic fallback

A test that mocks database behavior incorrectly may create a false positive.

Determine whether the mock accurately represents the actual SQLAlchemy query chain.

⸻

36. AUTHORIZATION TEST VALIDITY

Inspect:

tests/test_authorization.py

Verify tests cover:

* owner + same clinic + valid target = allowed
* owner + different clinic + valid target = denied
* secretary + same clinic = denied
* secretary + different clinic = denied
* patient + same clinic = denied
* unknown actor = denied
* missing clinic = denied
* invalid target = denied
* no mutation on denial

Do not require tests outside the contract unless they materially affect security.

⸻

37. TEST EXECUTION

If a valid execution environment is available:

Run the appropriate tests WITHOUT modifying the repository.

At minimum attempt:

pytest tests/

Also, if available:

python -m compileall .

and relevant import checks.

Record:

* exact command
* environment availability
* collection count
* passed
* failed
* skipped
* errors
* warnings
* traceback summary where relevant

If execution is impossible:

DO NOT claim PASS.

Use:

BLOCKED

or:

NOT VERIFIED

as appropriate.

⸻

38. STATIC VS EXECUTABLE VERIFICATION

Explicitly distinguish:

STATICALLY VERIFIED

The code can be inspected and the property is supported by the source.

EXECUTABLY VERIFIED

The actual test/runtime behavior was executed successfully.

NOT VERIFIED

The environment or evidence is insufficient.

FAILED

The implementation violates the requirement.

Never convert:

STATICALLY VERIFIED

into:

PASS

when the contract requires runtime verification.

⸻

39. IMPORT AND SYNTAX AUDIT

Inspect all changed Python files.

Attempt to verify:

* syntax validity
* imports
* circular import risk
* missing dependencies
* incorrect module paths
* undefined names
* unused critical imports
* provider initialization errors

Do not modify anything to make imports work.

⸻

40. DATA FLOW AUDIT

For each P0 finding, create an explicit data-flow trace.

At minimum:

Tenant

Telegram identity
→ identity lookup
→ clinic resolution
→ authorization
→ database object

Medical safety

Image
→ analysis
→ Gemini
→ raw output
→ parse
→ safety gate
→ persistence
→ PDF
→ Telegram

Gemini

Application
→ Patient Agent
→ Provider Manager
→ Provider Router
→ Gemini Provider
→ Gemini API

Authorization

Telegram actor
→ identity
→ role
→ clinic
→ target object
→ same-tenant check
→ mutation

Identify any bypass.

⸻

41. SECURITY BOUNDARY AUDIT

Verify that untrusted client input cannot directly control:

* clinic ID
* patient ID
* staff ID
* authorization role
* provider selection
* AI provider
* medical safety state
* approval state

Client-supplied identifiers must be treated as untrusted until resolved against trusted server-side identity and tenant context.

⸻

42. SECRET SAFETY

Search for:

GEMINI_API_KEY
BOT_TOKEN
API_KEY
SECRET
PASSWORD
TOKEN
OPENROUTER
DEEPSEEK
FREELLMAPI

Do not print secret values.

Verify that no actual credentials were added to:

* source files
* markdown files
* test fixtures
* logs
* reports
* examples
* configuration committed to the repository

If a secret appears, report the location without revealing the value.

⸻

43. REGRESSION AUDIT

Compare the implementation against the pre-Phase-1 behavior.

Identify whether Phase 1 caused:

* unrelated breakage
* import breakage
* database breakage
* Telegram handler breakage
* appointment breakage
* staff-management breakage
* facial-analysis breakage
* AI initialization breakage

Do not demand unrelated architectural rewrites.

Only report material regressions caused by the implementation.

⸻

44. CRITICAL QUESTIONS THAT MUST BE ANSWERED

Your final report MUST explicitly answer these questions.

Q1

Can an unknown Telegram user ever be assigned to the first clinic in the database?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q2

Can a patient identity from Clinic B be returned or mutated while operating under Clinic A?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q3

Can a non-owner delete staff?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q4

Can an owner delete staff belonging to another clinic?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q5

Can unsafe AI-generated medical content reach a patient without passing through a programmatic safety gate?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q6

Can raw LLM output bypass the safety gate through a parse-error or exception path?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q7

Can unsafe AI output be persisted before safety validation?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q8

Can a non-Gemini provider participate in the active runtime?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q9

Can Gemini failure trigger provider substitution?

Answer:

YES / NO / NOT VERIFIED

with evidence.

Q10

Do the Phase 1 tests actually exercise production behavior?

Answer:

YES / NO / PARTIALLY / NOT VERIFIED

with evidence.

Q11

Does the implementation report claim tests or guarantees that are not actually supported by the repository?

Answer:

YES / NO

with evidence.

⸻

45. FINDING SEVERITY

Use:

P0 = Critical
P1 = High
P2 = Medium
P3 = Low

Use P0 for issues that violate non-negotiable architecture or create serious security/medical-safety exposure.

Examples:

* cross-tenant access
* unsafe medical output reaching patients
* non-Gemini provider fallback
* authorization bypass

⸻

46. REQUIRED FINAL REPORT

Create:

CLINICOS_PHASE_1_POST_IMPLEMENTATION_AUDIT_REPORT.md

ONLY if the environment permits creation without modifying the repository.

If creating the report would violate the read-only requirement, do not create it; instead provide the complete report content in your response.

The report must contain:

CLINICOS PHASE 1 — POST-IMPLEMENTATION FORENSIC AUDIT REPORT

1. Audit Metadata

Include:

* audit date
* repository state
* commit/hash if available
* execution environment
* whether tests were executable
* authoritative documents used

2. Executive Status

Use exactly one:

PHASE 1 PASS
PHASE 1 FAIL
PHASE 1 BLOCKED
PHASE 1 NOT VERIFIED

Do NOT use:

statically complete

as the final completion status.

If any P0 acceptance criterion fails, overall status cannot be PASS.

If mandatory executable verification was impossible, overall status must not be PASS unless the contract explicitly permits that exact condition.

⸻

47. ACCEPTANCE MATRIX

Create a table:

ID	Requirement	Status	Evidence	Test Evidence	Notes
F-001	Tenant Isolation	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-002	Medical Safety	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-003	Gemini Only	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-004	Communication	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-005	Reliability	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-006	Knowledge	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-007	Client Architecture	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…
F-008	Authorization	PASS/FAIL/BLOCKED/NOT VERIFIED	…	…	…

⸻

48. REQUIRED DETAILED SECTIONS

The report must contain:

A. Repository Change Inventory

B. F-001 Tenant Isolation Audit

C. F-002 Medical Safety Audit

D. F-003 Gemini Runtime Audit

E. F-004 Communication Regression Audit

F. F-005 Reliability Regression Audit

G. F-006 Knowledge Regression Audit

H. F-007 Client Architecture Regression Audit

I. F-008 Authorization Audit

J. Test Inventory and Validity Audit

K. Test Execution Results

L. Secret and Credential Audit

M. Data Flow Analysis

N. Security Boundary Analysis

O. Regression Analysis

P. Critical Questions

Q. Findings

For each finding include:

ID
Severity
Requirement
Status
File
Function/Class
Evidence
Impact
Required Remediation

⸻

49. REMEDIATION RULE

You are auditing, not fixing.

For every FAIL:

Describe what must be fixed.

Do NOT implement the fix.

Do NOT provide modified code unless explicitly requested in a later task.

The next implementation phase will be based on your audit findings.

⸻

50. NO FALSE PASS CONDITION

The following are NOT sufficient evidence of PASS:

* “The code appears correct.”
* “The implementation report says complete.”
* “The prompt prevents this.”
* “A test file exists.”
* “The test logically represents the requirement.”
* “The environment probably supports it.”
* “The legacy provider is not normally used.”
* “The safety gate exists somewhere in the function.”
* “The application starts.”

Only evidence-based verification counts.

⸻

51. STOP CONDITIONS

Stop the audit and report BLOCKED if:

* the repository cannot be inspected completely
* critical source files are missing
* required authoritative documents are unavailable
* the execution environment prevents required verification
* the implementation depends on unavailable external state that cannot be safely inspected

Do not fabricate results.

⸻

52. FINAL AUDITOR STATEMENT

At the end of the report include:

AUDIT CONCLUSION
Phase 1 is accepted only if every mandatory P0 acceptance criterion is satisfied and all required verification evidence is available.
No implementation report, prompt-level instruction, or existence of tests is sufficient by itself.
The repository implementation and executable evidence are the source of truth.

⸻

53. IMPORTANT FINAL INSTRUCTION

Perform the audit now.

Do not modify the repository.

Do not implement fixes.

Do not optimize code.

Do not refactor.

Do not clean up unrelated code.

Do not delete legacy providers.

Do not add new architecture.

Do not silently correct problems.

Your responsibility is to produce an independent, evidence-based forensic assessment of whether the CURRENT Clinicos Phase 1 implementation actually satisfies the authoritative requirements.

The final output must clearly distinguish:

PASS
FAIL
BLOCKED
NOT VERIFIED

and must never present unexecuted or unsupported claims as verified success.
