"""
Mock Amendment Circular for Demo Scenario (Section 7):
SEBI reduces investor grievance resolution SLA from 21 days to 7 days.

This creates a simple text file simulating a SEBI amendment circular
that can be converted to PDF for the demo.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

AMENDMENT_TEXT = """
SECURITIES AND EXCHANGE BOARD OF INDIA

CIRCULAR

SEBI/HO/MIRSD/MIRSD-PoD-2/P/CIR/2025/112

July 01, 2025

To,
All Stock Brokers through Stock Exchanges

Subject: Amendment to Investor Grievance Redressal Timelines for Stock Brokers

1. SEBI has been receiving representations from investors regarding the need for
faster resolution of their grievances by stock brokers. After due deliberation and
in consultation with stock exchanges, it has been decided to amend the timelines
for investor grievance redressal as specified in the Master Circular for Stock
Brokers dated June 17, 2025.

Chapter VII - Investor Grievance Redressal - Amended Provisions

2. Clause 3.1 of Chapter VII of the Master Circular for Stock Brokers is hereby
amended as follows:

2.1 Resolution Timeline: Every stock broker shall resolve all investor grievances
and complaints within 7 (seven) calendar days from the date of receipt of the
complaint, as against the earlier timeline of 21 calendar days. This reduced
timeline shall apply to all categories of complaints including but not limited
to trade-related disputes, fund settlement issues, and service-related complaints.

2.2 Acknowledgement Timeline: The timeline for sending acknowledgement to the
complainant remains at 24 hours from receipt of complaint. However, the
acknowledgement must now include an estimated resolution date not exceeding
7 calendar days.

2.3 Escalation Framework: If a complaint cannot be resolved within 7 calendar days,
the stock broker shall:
(a) Escalate the matter to a designated senior officer (at least one level above
the initial handler) within 5 calendar days;
(b) Inform the complainant in writing about the escalation and revised timeline;
(c) Ensure resolution within a maximum extended period of 14 calendar days,
with documented justification for the extension.

2.4 Enhanced Reporting: Stock brokers shall submit a weekly grievance status report
to the stock exchange, replacing the current monthly reporting requirement.
The report shall include:
(a) Number of complaints received during the week;
(b) Number of complaints resolved within 7 days;
(c) Number of complaints pending beyond 7 days with reasons;
(d) Average resolution time.

2.5 SCORES Platform Update: All complaints and their resolution status must be
updated on the SCORES platform within 24 hours of any status change.

3. Penalty Framework:
3.1 Stock brokers failing to resolve complaints within the revised 7-day timeline
on a repeated basis shall be liable for enhanced penalties as determined by
the stock exchanges in consultation with SEBI.
3.2 A resolution rate below 90% within the 7-day window in any calendar month
shall trigger a special inspection by the stock exchange.

4. Effective Date: These amended provisions shall come into effect from August 01, 2025.

5. Stock Exchanges are directed to:
(a) Bring the provisions of this circular to the notice of all stock brokers;
(b) Make necessary amendments to their bye-laws, rules, and regulations;
(c) Put in place monitoring systems to track compliance with the revised timelines;
(d) Report to SEBI on a monthly basis regarding compliance levels.

6. This circular is issued in exercise of the powers conferred under Section 11(1)
of the Securities and Exchange Board of India Act, 1992.

Sd/-
General Manager
Market Intermediaries Regulation and Supervision Department
"""


def create_mock_amendment_pdf():
    """Create a mock amendment circular as a text file (for demo parsing)."""
    os.makedirs("data/circulars", exist_ok=True)
    filepath = "data/circulars/amendment_grievance_sla_2025.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(AMENDMENT_TEXT)
    print(f"✅ Created mock amendment circular: {filepath}")

    # Also create a simple PDF using reportlab if available, otherwise text only
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        pdf_path = "data/circulars/amendment_grievance_sla_2025.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        for para in AMENDMENT_TEXT.strip().split("\n\n"):
            story.append(Paragraph(para.replace("\n", "<br/>"), styles["Normal"]))
            story.append(Spacer(1, 12))
        doc.build(story)
        print(f"✅ Created PDF: {pdf_path}")
    except ImportError:
        print("⚠️  reportlab not installed — text file created instead of PDF")
        print("   Install with: pip install reportlab")


if __name__ == "__main__":
    create_mock_amendment_pdf()
