"""
Intermediary Profile Configurations.
Switching regulatory scope is as simple as changing the profile.
"""
PROFILES = {
    "stockbroker": {
        "name": "Stockbroker",
        "sebi_category": "Stock Broker / Trading Member",
        "applicable_master_circular": "SEBI Master Circular for Stock Brokers (2025)",
        "process_areas": [
            "Client Onboarding (KYC/AML)",
            "Margin & Risk Management",
            "Trading & Order Management",
            "Settlement & Accounts",
            "Investor Grievance Redressal",
            "Cybersecurity & IT Infrastructure",
            "Reporting to Exchange/SEBI",
            "Record-Keeping & Documentation",
            "Advertising & Marketing",
            "Audit & Supervision",
        ],
        "obligation_types": [
            "kyc_onboarding", "risk_management", "reporting", "disclosure",
            "grievance_redressal", "cybersecurity", "record_keeping",
            "advertising", "systems_process", "timeline",
        ],
        "regulatory_chapters": [
            {"id": "CH1", "title": "Registration & Membership", "covered": True},
            {"id": "CH2", "title": "Code of Conduct", "covered": True},
            {"id": "CH3", "title": "KYC & Anti-Money Laundering", "covered": True},
            {"id": "CH4", "title": "Trading & Order Management", "covered": True},
            {"id": "CH5", "title": "Risk Management & Margins", "covered": True},
            {"id": "CH6", "title": "Settlement & Clearing", "covered": True},
            {"id": "CH7", "title": "Investor Grievance Redressal", "covered": True},
            {"id": "CH8", "title": "Cybersecurity Framework", "covered": True},
            {"id": "CH9", "title": "Reporting & Disclosures", "covered": True},
            {"id": "CH10", "title": "Advertising Guidelines", "covered": True},
            {"id": "CH11", "title": "Record-Keeping", "covered": True},
            {"id": "CH12", "title": "Inspection & Audit", "covered": True},
        ],
        "dpi_integrations": ["DigiLocker", "CKYC", "e-PAN", "Aadhaar e-KYC"],
    },
    "mutual_fund": {
        "name": "Mutual Fund",
        "sebi_category": "Asset Management Company (AMC)",
        "applicable_master_circular": "SEBI Master Circular for Mutual Funds",
        "process_areas": [
            "Fund Registration & Compliance",
            "NAV Computation",
            "Investor Onboarding",
            "Scheme Management",
            "Risk Management",
            "Disclosure & Reporting",
        ],
        "obligation_types": [
            "kyc_onboarding", "reporting", "disclosure", "risk_management",
            "record_keeping", "advertising", "systems_process",
        ],
        "regulatory_chapters": [],
        "dpi_integrations": ["DigiLocker", "CKYC", "e-PAN"],
    },
    "depository_participant": {
        "name": "Depository Participant",
        "sebi_category": "Depository Participant (DP)",
        "applicable_master_circular": "SEBI Master Circular for Depository Participants",
        "process_areas": [
            "Account Opening",
            "Dematerialization / Rematerialization",
            "Transfer & Transmission",
            "Pledge / Hypothecation",
            "Corporate Actions",
            "Investor Services",
        ],
        "obligation_types": [
            "kyc_onboarding", "reporting", "disclosure", "record_keeping",
            "systems_process", "grievance_redressal",
        ],
        "regulatory_chapters": [],
        "dpi_integrations": ["DigiLocker", "CKYC", "e-PAN", "Aadhaar e-KYC"],
    },
}


def get_profile(intermediary_type: str = "stockbroker") -> dict:
    """Get configuration for a specific intermediary type."""
    return PROFILES.get(intermediary_type, PROFILES["stockbroker"])


def list_profiles() -> list[dict]:
    """List all available intermediary profiles."""
    return [
        {"key": k, "name": v["name"], "category": v["sebi_category"]}
        for k, v in PROFILES.items()
    ]
