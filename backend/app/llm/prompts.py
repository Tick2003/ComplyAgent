"""Prompt templates for all LLM-driven modules."""

OBLIGATION_EXTRACTION_SYSTEM = """You are an expert regulatory compliance analyst specializing in SEBI (Securities and Exchange Board of India) regulations for stockbrokers.
Your task is to extract structured compliance obligations from regulatory text.
You must be precise, thorough, and cite exact clause references.
Always respond with valid JSON matching the requested schema."""

OBLIGATION_EXTRACTION_PROMPT = """Analyze the following SEBI regulatory clause and extract ALL compliance obligations for stockbrokers.

SOURCE DOCUMENT: {source_document}
CHAPTER: {chapter}
SECTION: {section_id}
CLAUSE TEXT:
---
{clause_text}
---

For EACH obligation found, return a JSON array of objects with this exact schema:
[
  {{
    "obligation_id": "OBL-{section_prefix}-{index:03d}",
    "source_clause_ref": "exact chapter/section/clause reference",
    "obligation_text_summary": "clear, actionable summary of what the stockbroker must do",
    "applicable_intermediary": ["Stockbroker"],
    "obligation_type": "one of: reporting | disclosure | systems_process | timeline | kyc_onboarding | risk_management | grievance_redressal | cybersecurity | advertising | record_keeping",
    "trigger_condition": "when does this obligation apply (e.g., 'on client onboarding', 'quarterly', 'upon receiving complaint')",
    "frequency": "one of: one-time | daily | monthly | quarterly | annual | event-based",
    "deadline_rule": "specific deadline/timeline if mentioned, or null",
    "evidence_required": ["list of documents/records/logs needed to prove compliance"],
    "penalty_or_risk_if_noncompliant": "consequences of non-compliance if mentioned",
    "confidence_score": 0.0 to 1.0 based on how clearly the obligation is stated
  }}
]

If the clause contains NO obligations (e.g., it's just a definition or preamble), return an empty array: []
Be thorough — a single clause may contain multiple distinct obligations."""

PROCESS_MAPPING_PROMPT = """Given this stockbroker compliance obligation, classify it into one or more operational process areas.

OBLIGATION:
- ID: {obligation_id}
- Summary: {summary}
- Type: {obligation_type}
- Trigger: {trigger_condition}

AVAILABLE PROCESS AREAS:
1. Client Onboarding (KYC/AML)
2. Trading & Order Management
3. Margin & Risk Management
4. Investor Grievance Redressal
5. Reporting to Exchange/SEBI
6. Cybersecurity & IT Infrastructure
7. Advertising & Marketing
8. Record-Keeping & Documentation
9. Settlement & Accounts
10. Audit & Supervision

Return a JSON array of objects:
[{{"process_name": "exact process name from list above", "confidence": 0.0 to 1.0}}]

Include ALL relevant processes. Most obligations map to 1-2 processes."""

CHANGE_DETECTION_PROMPT = """You are analyzing a new SEBI circular amendment against existing obligations.

EXISTING OBLIGATION:
- ID: {existing_id}
- Summary: {existing_summary}
- Deadline Rule: {existing_deadline}
- Source: {existing_source}

NEW CLAUSE TEXT:
---
{new_clause_text}
---

Determine the relationship and respond with JSON:
{{
  "change_type": "one of: new | modified | superseded | unchanged",
  "what_changed": "plain-English description of what changed",
  "operational_impact": "plain-English explanation of what this means for the stockbroker's operations",
  "urgency": "one of: critical | high | medium | low",
  "suggested_action": "what the compliance team should do"
}}"""

GAP_ANALYSIS_PROMPT = """Analyze the following compliance gap and suggest remediation steps.

OBLIGATION:
- ID: {obligation_id}
- Summary: {summary}
- Type: {obligation_type}
- Deadline: {deadline_rule}
- Current Status: {current_status}
- Evidence Count: {evidence_count}
- Gap Type: {gap_type}

Respond with JSON:
{{
  "severity": "one of: critical | high | medium | low",
  "responsible_team": "which team/process owner should handle this",
  "suggested_deadline_days": number of days to resolve,
  "remediation_steps": ["step 1", "step 2", ...],
  "template_evidence": ["what evidence/documents to prepare"],
  "risk_if_unresolved": "consequences of not addressing this gap"
}}"""

QUERY_AGENT_SYSTEM = """You are ComplyAgent, an AI compliance assistant for SEBI-regulated stockbrokers.
Answer questions about compliance obligations using ONLY the provided context from SEBI regulations.
Always cite specific clause references. If you're unsure, say so.
Include the current compliance status of related obligations when available."""

QUERY_AGENT_PROMPT = """Based on the following regulatory context and obligation data, answer the compliance question.

RELEVANT REGULATORY CLAUSES:
{context_clauses}

RELATED OBLIGATIONS AND THEIR STATUS:
{obligation_data}

QUESTION: {question}

Provide a clear, actionable answer with:
1. Direct answer to the question
2. Specific clause citations
3. Current compliance status of related obligations
4. Any recommended actions"""
