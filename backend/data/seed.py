"""
Database seeder — populates ComplyAgent with realistic mock data for the demo.

Mock firm: Horizon Securities Pvt. Ltd.
Pre-populates: obligations, compliance statuses, evidence, audit trail.
Includes the demo scenario setup (grievance SLA at 21 days).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, date, timedelta
import random

from app.database import SessionLocal, init_db
from app.models.circular import Circular, ClauseChunk
from app.models.obligation import Obligation, ObligationProcessMap
from app.models.evidence import Evidence, ComplianceStatus
from app.models.audit_log import AuditLog
from app.models.user import User
from app.vector_store.store import add_chunks_to_store

# ── Mock Obligations Data ─────────────────────────────────────────────
MOCK_OBLIGATIONS = [
    {
        "obligation_id": "OBL-KYC-001",
        "source_clause_ref": "Chapter IV, Clause 2.1",
        "obligation_text_summary": "Complete KYC verification for all new clients before allowing trading, including PAN verification, address proof, and in-person verification or video-based IPV",
        "obligation_type": "kyc_onboarding",
        "trigger_condition": "On new client onboarding",
        "frequency": "event-based",
        "deadline_rule": "Before first trade execution",
        "evidence_required": ["KYC form", "PAN card copy", "Address proof", "IPV record", "Client master report"],
        "penalty_or_risk_if_noncompliant": "SEBI administrative action, suspension of trading terminal",
        "confidence_score": 0.95,
        "process": "Client Onboarding (KYC/AML)",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-KYC-002",
        "source_clause_ref": "Chapter IV, Clause 3.4",
        "obligation_text_summary": "Perform periodic KYC re-verification for existing clients at least once every 2 years for regular clients and annually for high-risk clients",
        "obligation_type": "kyc_onboarding",
        "trigger_condition": "Periodic — based on client risk category",
        "frequency": "annual",
        "deadline_rule": "Within 2 years of last KYC for regular, 1 year for high-risk",
        "evidence_required": ["Updated KYC records", "Risk categorization report", "Re-verification log"],
        "penalty_or_risk_if_noncompliant": "Regulatory warning, potential client account freeze",
        "confidence_score": 0.88,
        "process": "Client Onboarding (KYC/AML)",
        "compliance_status": "partially_compliant",
    },
    {
        "obligation_id": "OBL-MARGIN-001",
        "source_clause_ref": "Chapter V, Clause 1.2",
        "obligation_text_summary": "Collect upfront margins from clients before trade execution as per SEBI's peak margin norms. Maintain records of margin collection and reporting.",
        "obligation_type": "risk_management",
        "trigger_condition": "On every trade execution",
        "frequency": "daily",
        "deadline_rule": "Before trade execution (T+0)",
        "evidence_required": ["Daily margin collection report", "Client margin ledger", "Exchange margin filing"],
        "penalty_or_risk_if_noncompliant": "Penalty by exchange, short-collection charges",
        "confidence_score": 0.92,
        "process": "Margin & Risk Management",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-MARGIN-002",
        "source_clause_ref": "Chapter V, Clause 2.5",
        "obligation_text_summary": "Report daily margin status to the exchange by end of day. Any shortfall in margin collection must be reported within T+1.",
        "obligation_type": "reporting",
        "trigger_condition": "Daily at market close",
        "frequency": "daily",
        "deadline_rule": "By end of trading day (T+0) for margin status, T+1 for shortfall",
        "evidence_required": ["Daily margin report to exchange", "Shortfall report if applicable"],
        "penalty_or_risk_if_noncompliant": "Exchange penalty, increased surveillance",
        "confidence_score": 0.90,
        "process": "Margin & Risk Management",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-GRIEVANCE-001",
        "source_clause_ref": "Chapter VII, Clause 3.1",
        "obligation_text_summary": "Resolve all investor grievances within 21 calendar days from the date of receipt. Maintain a grievance redressal log with timestamps for receipt, acknowledgement, and resolution.",
        "obligation_type": "grievance_redressal",
        "trigger_condition": "On receipt of investor complaint",
        "frequency": "event-based",
        "deadline_rule": "21 calendar days from receipt of complaint",
        "evidence_required": ["Complaint register", "Acknowledgement to investor", "Resolution record", "SCORES platform log"],
        "penalty_or_risk_if_noncompliant": "SEBI administrative action, adverse observation in inspection report",
        "confidence_score": 0.93,
        "process": "Investor Grievance Redressal",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-GRIEVANCE-002",
        "source_clause_ref": "Chapter VII, Clause 4.2",
        "obligation_text_summary": "Register and update all investor complaints on SEBI's SCORES platform. Ensure acknowledgement within 24 hours of receipt.",
        "obligation_type": "grievance_redressal",
        "trigger_condition": "On receipt of investor complaint",
        "frequency": "event-based",
        "deadline_rule": "Acknowledgement within 24 hours",
        "evidence_required": ["SCORES registration screenshot", "Acknowledgement email/SMS to investor"],
        "penalty_or_risk_if_noncompliant": "SEBI penalty, exchange action",
        "confidence_score": 0.91,
        "process": "Investor Grievance Redressal",
        "compliance_status": "partially_compliant",
    },
    {
        "obligation_id": "OBL-CYBER-001",
        "source_clause_ref": "Chapter IX, Clause 1.3",
        "obligation_text_summary": "Implement a comprehensive cybersecurity framework including firewalls, intrusion detection systems, data encryption, and access controls as per SEBI's cybersecurity circular.",
        "obligation_type": "cybersecurity",
        "trigger_condition": "Ongoing — must be maintained at all times",
        "frequency": "one-time",
        "deadline_rule": "Continuous compliance required",
        "evidence_required": ["Cybersecurity policy document", "Firewall configuration logs", "IDS/IPS reports", "Access control matrix", "Annual VAPT report"],
        "penalty_or_risk_if_noncompliant": "SEBI enforcement action, potential trading suspension, data breach liability",
        "confidence_score": 0.87,
        "process": "Cybersecurity & IT Infrastructure",
        "compliance_status": "non_compliant",
    },
    {
        "obligation_id": "OBL-CYBER-002",
        "source_clause_ref": "Chapter IX, Clause 2.1",
        "obligation_text_summary": "Report all cybersecurity incidents to SEBI and relevant stock exchanges within 6 hours of detection. Maintain incident response logs.",
        "obligation_type": "cybersecurity",
        "trigger_condition": "On detection of cybersecurity incident",
        "frequency": "event-based",
        "deadline_rule": "Within 6 hours of incident detection",
        "evidence_required": ["Incident report", "Communication to SEBI", "Communication to exchange", "Incident response log"],
        "penalty_or_risk_if_noncompliant": "Severe regulatory action, potential suspension",
        "confidence_score": 0.85,
        "process": "Cybersecurity & IT Infrastructure",
        "compliance_status": "not_yet_due",
    },
    {
        "obligation_id": "OBL-REPORT-001",
        "source_clause_ref": "Chapter VI, Clause 1.1",
        "obligation_text_summary": "Submit monthly net worth certificate to the stock exchange, certified by a qualified auditor, within 30 days of month end.",
        "obligation_type": "reporting",
        "trigger_condition": "Monthly",
        "frequency": "monthly",
        "deadline_rule": "Within 30 days of month end",
        "evidence_required": ["Net worth certificate", "Auditor certification", "Exchange submission receipt"],
        "penalty_or_risk_if_noncompliant": "Exchange penalty, potential trading restriction",
        "confidence_score": 0.94,
        "process": "Reporting to Exchange/SEBI",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-REPORT-002",
        "source_clause_ref": "Chapter VI, Clause 2.3",
        "obligation_text_summary": "File quarterly compliance report with SEBI covering all regulatory obligations, pending investor complaints, and audit observations.",
        "obligation_type": "reporting",
        "trigger_condition": "Quarterly",
        "frequency": "quarterly",
        "deadline_rule": "Within 15 days of quarter end",
        "evidence_required": ["Quarterly compliance report", "SEBI filing receipt", "Board acknowledgement"],
        "penalty_or_risk_if_noncompliant": "SEBI administrative warning, increased inspection frequency",
        "confidence_score": 0.89,
        "process": "Reporting to Exchange/SEBI",
        "compliance_status": "non_compliant",
    },
    {
        "obligation_id": "OBL-RECORD-001",
        "source_clause_ref": "Chapter VIII, Clause 1.2",
        "obligation_text_summary": "Maintain all client records, trade records, and correspondence for a minimum period of 5 years from the date of transaction/communication.",
        "obligation_type": "record_keeping",
        "trigger_condition": "Ongoing",
        "frequency": "one-time",
        "deadline_rule": "Minimum 5 years retention",
        "evidence_required": ["Record retention policy", "Data backup logs", "Archival records"],
        "penalty_or_risk_if_noncompliant": "Regulatory action, inability to respond to regulatory inquiries",
        "confidence_score": 0.92,
        "process": "Record-Keeping & Documentation",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-ADVERT-001",
        "source_clause_ref": "Chapter X, Clause 1.1",
        "obligation_text_summary": "All advertisements and promotional materials must include SEBI registration number, risk disclaimers, and must not contain misleading claims about guaranteed returns.",
        "obligation_type": "advertising",
        "trigger_condition": "On publication of any advertisement",
        "frequency": "event-based",
        "deadline_rule": "Before publication of advertisement",
        "evidence_required": ["Advertisement approval records", "Compliance review checklist", "Published advertisement copies"],
        "penalty_or_risk_if_noncompliant": "SEBI penalty, direction to withdraw advertisement, reputational damage",
        "confidence_score": 0.86,
        "process": "Advertising & Marketing",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-SETTLE-001",
        "source_clause_ref": "Chapter V, Clause 4.1",
        "obligation_text_summary": "Settle client running accounts at least once every 30 days for active clients and 90 days for inactive clients. Provide settlement statement to client.",
        "obligation_type": "systems_process",
        "trigger_condition": "Periodic settlement cycle",
        "frequency": "monthly",
        "deadline_rule": "Every 30 days (active) / 90 days (inactive)",
        "evidence_required": ["Settlement register", "Client settlement statements", "Fund transfer records"],
        "penalty_or_risk_if_noncompliant": "Exchange penalty, client complaint",
        "confidence_score": 0.91,
        "process": "Settlement & Accounts",
        "compliance_status": "partially_compliant",
    },
    {
        "obligation_id": "OBL-AUDIT-001",
        "source_clause_ref": "Chapter XI, Clause 1.1",
        "obligation_text_summary": "Conduct internal audit on a half-yearly basis by an independent qualified professional (CA/CS/CMA). Submit audit report to exchange within 3 months of half-year end.",
        "obligation_type": "systems_process",
        "trigger_condition": "Half-yearly",
        "frequency": "quarterly",
        "deadline_rule": "Audit within each half-year, report within 3 months of half-year end",
        "evidence_required": ["Internal audit report", "Auditor qualification proof", "Exchange submission receipt", "Management response to audit findings"],
        "penalty_or_risk_if_noncompliant": "Exchange action, increased regulatory scrutiny",
        "confidence_score": 0.90,
        "process": "Audit & Supervision",
        "compliance_status": "not_yet_due",
    },
    {
        "obligation_id": "OBL-TRADING-001",
        "source_clause_ref": "Chapter III, Clause 2.1",
        "obligation_text_summary": "Issue electronic contract notes to clients for all executed trades within 24 hours of trade execution, including all mandatory disclosures.",
        "obligation_type": "disclosure",
        "trigger_condition": "On trade execution",
        "frequency": "daily",
        "deadline_rule": "Within 24 hours of trade execution",
        "evidence_required": ["Contract note templates", "Delivery logs", "Client confirmation records"],
        "penalty_or_risk_if_noncompliant": "Client complaint, exchange penalty",
        "confidence_score": 0.93,
        "process": "Trading & Order Management",
        "compliance_status": "compliant",
    },
    {
        "obligation_id": "OBL-RISK-001",
        "source_clause_ref": "Chapter V, Clause 3.2",
        "obligation_text_summary": "Implement a robust risk management system including real-time position monitoring, client-wise exposure limits, and automated square-off mechanisms for margin shortfalls.",
        "obligation_type": "risk_management",
        "trigger_condition": "Ongoing — system must be operational during market hours",
        "frequency": "daily",
        "deadline_rule": "Continuous during market hours",
        "evidence_required": ["RMS configuration document", "Alert mechanism logs", "Square-off execution records", "Exposure limit settings"],
        "penalty_or_risk_if_noncompliant": "Exchange penalty, potential trading restriction, client loss liability",
        "confidence_score": 0.88,
        "process": "Margin & Risk Management",
        "compliance_status": "compliant",
    },
]

# Mock clause chunks for vector store
MOCK_CHUNKS = [
    {
        "chunk_id": "MCSB2025-CH4-S2.1-0001",
        "chapter": "Chapter IV - KYC & Client Onboarding",
        "section_id": "2.1",
        "page_number": 12,
        "text": "Every stockbroker shall ensure that Know Your Client (KYC) norms are complied with for all clients before commencing trading. This includes verification of PAN, address proof, and in-person verification (IPV) which may be conducted via video-based identification process. The stockbroker shall maintain complete records of KYC documentation.",
    },
    {
        "chunk_id": "MCSB2025-CH5-S1.2-0002",
        "chapter": "Chapter V - Margin & Risk Management",
        "section_id": "1.2",
        "page_number": 23,
        "text": "Stockbrokers shall collect upfront margins from clients as prescribed by SEBI from time to time. The collection of margins shall be in accordance with the peak margin norms. Stockbrokers shall report daily margin collection status to the respective stock exchanges.",
    },
    {
        "chunk_id": "MCSB2025-CH7-S3.1-0003",
        "chapter": "Chapter VII - Investor Grievance Redressal",
        "section_id": "3.1",
        "page_number": 38,
        "text": "Every stockbroker shall resolve all investor grievances and complaints within 21 calendar days from the date of receipt of the complaint. The stockbroker shall maintain a grievance redressal log with timestamps for receipt, acknowledgement, and resolution. All complaints must also be registered on SEBI's SCORES platform.",
    },
    {
        "chunk_id": "MCSB2025-CH9-S1.3-0004",
        "chapter": "Chapter IX - Cybersecurity",
        "section_id": "1.3",
        "page_number": 52,
        "text": "Stockbrokers shall implement a comprehensive cybersecurity and cyber resilience framework as specified by SEBI. This includes deployment of firewalls, intrusion detection and prevention systems, data encryption for sensitive client data, and robust access control mechanisms. Annual Vulnerability Assessment and Penetration Testing (VAPT) shall be conducted.",
    },
    {
        "chunk_id": "MCSB2025-CH6-S1.1-0005",
        "chapter": "Chapter VI - Reporting Requirements",
        "section_id": "1.1",
        "page_number": 30,
        "text": "Stockbrokers shall submit a monthly net worth certificate to the stock exchange, duly certified by a qualified statutory auditor, within 30 calendar days from the end of each month. The net worth shall be computed as per the prescribed formula including paid-up capital, free reserves, and securities at market value.",
    },
    {
        "chunk_id": "MCSB2025-CH7-S4.2-0006",
        "chapter": "Chapter VII - Investor Grievance Redressal",
        "section_id": "4.2",
        "page_number": 40,
        "text": "The stockbroker shall register and update all investor complaints on SEBI's SCORES platform within 24 hours of receipt. An acknowledgement shall be sent to the investor within 24 hours confirming receipt of the complaint and providing the expected timeline for resolution.",
    },
    {
        "chunk_id": "MCSB2025-CH9-S2.1-0007",
        "chapter": "Chapter IX - Cybersecurity",
        "section_id": "2.1",
        "page_number": 55,
        "text": "Any cybersecurity incident or breach shall be reported to SEBI and the relevant stock exchanges within 6 hours of detection. The stockbroker shall maintain detailed incident response logs including the nature of the incident, systems affected, data compromised if any, and remedial actions taken.",
    },
    {
        "chunk_id": "MCSB2025-CH3-S2.1-0008",
        "chapter": "Chapter III - Trading & Contract Notes",
        "section_id": "2.1",
        "page_number": 8,
        "text": "Electronic contract notes shall be issued to clients for all executed trades within 24 hours of trade execution. Contract notes must include all mandatory disclosures as prescribed by the exchange, including brokerage charges, taxes, and transaction charges.",
    },
    {
        "chunk_id": "MCSB2025-CH10-S1.1-0009",
        "chapter": "Chapter X - Advertising & Marketing",
        "section_id": "1.1",
        "page_number": 60,
        "text": "All advertisements and promotional materials published by stockbrokers must prominently display the SEBI registration number and appropriate risk disclaimers. No advertisement shall contain any claim of guaranteed or assured returns. Past performance disclaimers must be included where historical data is presented.",
    },
    {
        "chunk_id": "MCSB2025-CH5-S4.1-0010",
        "chapter": "Chapter V - Settlement of Running Accounts",
        "section_id": "4.1",
        "page_number": 28,
        "text": "Running accounts of clients shall be settled by the stockbroker at least once in every 30 calendar days for active clients and once in every 90 calendar days for inactive clients. A detailed settlement statement shall be sent to the client within 5 working days of settlement.",
    },
]


def seed_database():
    """Seed the database with mock data for the demo."""
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Circular).first()
        if existing:
            print("[WARN] Database already seeded. Skipping.")
            return

        print("[SEED] Seeding database with mock data...")

        # ── Users ──────────────────────────────────────────────
        users = [
            User(name="Priya Sharma", email="priya.sharma@horizonsec.com", role="compliance_officer", hashed_password="mock_hashed"),
            User(name="Rajesh Kumar", email="rajesh.kumar@horizonsec.com", role="compliance_head", hashed_password="mock_hashed"),
        ]
        for u in users:
            db.add(u)
        db.commit()
        print(f"  [OK] Created {len(users)} users")

        # ── Master Circular ───────────────────────────────────
        circular = Circular(
            title="Master Circular for Stock Brokers",
            circular_number="SEBI/HO/MIRSD/MIRSD-PoD-1/P/CIR/2025/093",
            source_url="https://www.sebi.gov.in/legal/master-circulars/jun-2025/master-circular-for-stock-brokers.html",
            effective_date=date(2025, 6, 17),
            status="extracted",
            circular_type="master_circular",
            summary=f"Master Circular consolidating all SEBI guidelines for stockbrokers. Parsed 10 clause chunks, extracted {len(MOCK_OBLIGATIONS)} obligations.",
        )
        db.add(circular)
        db.commit()
        db.refresh(circular)
        print(f"  [OK] Created master circular (ID: {circular.id})")

        # ── Clause Chunks ─────────────────────────────────────
        for chunk_data in MOCK_CHUNKS:
            chunk = ClauseChunk(
                circular_id=circular.id,
                chunk_id=chunk_data["chunk_id"],
                chapter=chunk_data["chapter"],
                section_id=chunk_data["section_id"],
                page_number=chunk_data["page_number"],
                text=chunk_data["text"],
                effective_date=date(2025, 6, 17),
            )
            db.add(chunk)
        db.commit()
        print(f"  [OK] Created {len(MOCK_CHUNKS)} clause chunks")

        # Add to vector store
        chunks_for_vector = [{**c, "circular_id": circular.id} for c in MOCK_CHUNKS]
        add_chunks_to_store(chunks_for_vector)
        print("  [OK] Added chunks to vector store")

        # ── Obligations ───────────────────────────────────────
        for obl_data in MOCK_OBLIGATIONS:
            obl = Obligation(
                obligation_id=obl_data["obligation_id"],
                source_chunk_id=next((c["chunk_id"] for c in MOCK_CHUNKS if obl_data["source_clause_ref"].split(",")[0].strip() in c.get("chapter", "")), None),
                circular_id=circular.id,
                source_clause_ref=obl_data["source_clause_ref"],
                obligation_text_summary=obl_data["obligation_text_summary"],
                applicable_intermediary=["Stockbroker"],
                obligation_type=obl_data["obligation_type"],
                trigger_condition=obl_data["trigger_condition"],
                frequency=obl_data["frequency"],
                deadline_rule=obl_data["deadline_rule"],
                evidence_required=obl_data["evidence_required"],
                penalty_or_risk_if_noncompliant=obl_data["penalty_or_risk_if_noncompliant"],
                confidence_score=obl_data["confidence_score"],
                review_status="approved",
                reviewed_by="Priya Sharma",
                reviewed_at=datetime.utcnow() - timedelta(days=30),
                status="active",
            )
            db.add(obl)
            db.commit()
            db.refresh(obl)

            # Process mapping
            process_map = ObligationProcessMap(
                obligation_id=obl.id,
                process_name=obl_data["process"],
                confidence=0.95,
                is_override=False,
                mapped_by="system",
            )
            db.add(process_map)

            # Compliance status
            cs = ComplianceStatus(
                obligation_id=obl.id,
                status=obl_data["compliance_status"],
                changed_by="Priya Sharma",
                changed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                notes=f"Initial status assessment for {obl_data['obligation_id']}",
            )
            db.add(cs)

            # Evidence for compliant obligations
            if obl_data["compliance_status"] == "compliant":
                for i, ev_title in enumerate(obl_data["evidence_required"][:2]):
                    evidence = Evidence(
                        obligation_id=obl.id,
                        evidence_type=random.choice(["document", "link", "checkbox"]),
                        title=ev_title,
                        content=f"Evidence verified and on file — {ev_title}",
                        uploaded_by="Priya Sharma",
                        uploaded_at=datetime.utcnow() - timedelta(days=random.randint(5, 60)),
                    )
                    db.add(evidence)

            # Audit log entries
            audit = AuditLog(
                entity_type="obligation",
                entity_id=obl_data["obligation_id"],
                action="extracted",
                new_value=obl_data["obligation_text_summary"][:200],
                user="system",
                timestamp=datetime.utcnow() - timedelta(days=35),
            )
            db.add(audit)

            audit2 = AuditLog(
                entity_type="obligation",
                entity_id=obl_data["obligation_id"],
                action="reviewed",
                old_value="pending_review",
                new_value="approved",
                user="Priya Sharma",
                timestamp=datetime.utcnow() - timedelta(days=30),
            )
            db.add(audit2)

        db.commit()
        print(f"  [OK] Created {len(MOCK_OBLIGATIONS)} obligations with statuses and evidence")

        # ── Summary ───────────────────────────────────────────
        compliant = sum(1 for o in MOCK_OBLIGATIONS if o["compliance_status"] == "compliant")
        partial = sum(1 for o in MOCK_OBLIGATIONS if o["compliance_status"] == "partially_compliant")
        non_compliant = sum(1 for o in MOCK_OBLIGATIONS if o["compliance_status"] == "non_compliant")
        not_due = sum(1 for o in MOCK_OBLIGATIONS if o["compliance_status"] == "not_yet_due")

        print(f"\n--- Horizon Securities Pvt. Ltd. - Compliance Dashboard ---")
        print(f"   Total Obligations: {len(MOCK_OBLIGATIONS)}")
        print(f"   [OK] Compliant: {compliant}")
        print(f"   [!!] Partially Compliant: {partial}")
        print(f"   [XX] Non-Compliant: {non_compliant}")
        print(f"   [..] Not Yet Due: {not_due}")
        print(f"\n[SEED] Database seeding complete!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
