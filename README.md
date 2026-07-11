# ComplyAgent — Agentic Compliance Engine for SEBI-Regulated Stockbrokers

**SEBI Securities Market TechSprint — Problem Statement 2**
*Agentic Compliance: From Regulatory Text to Operational Action*

---

## 🏗️ Architecture

ComplyAgent is a full-stack RegTech web application that:

1. **Ingests** SEBI circular PDFs and parses them into clause-level chunks
2. **Extracts** structured compliance obligations using LLM (Google Gemini)
3. **Maps** each obligation to stockbroker operational processes
4. **Tracks** fulfilment status with evidence and append-only audit trail
5. **Detects** regulatory changes when new circulars are ingested
6. **Finds gaps** — overdue obligations, missing evidence, low-confidence rules
7. **Answers** natural-language compliance questions with cited references (RAG)

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS v4 |
| Backend | Python 3.12 + FastAPI |
| Database | SQLite (append-only audit design) |
| Vector Store | ChromaDB (for RAG) |
| LLM | Google Gemini 2.5 Flash |
| PDF Parsing | pdfplumber |
| Charts | Recharts |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))

### 1. Backend Setup

```bash
cd complyagent/backend

# Create .env file with your API key
echo GEMINI_API_KEY=your_api_key_here > .env

# Install Python dependencies
pip install -r requirements.txt

# Seed the database with mock data
python data/seed.py

# Create mock amendment circular for demo
python data/mock_amendment.py

# Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd complyagent/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

### 3. Open the App

Navigate to **http://localhost:5173** in your browser.

---

## 📋 Demo Scenario (Section 7)

The demo is pre-configured around this scenario:

> **SEBI issues a new circular reducing investor grievance resolution SLA from 21 days to 7 days.**

### Demo Steps:

1. **Dashboard** — View the compliance health score (71.9%) for Horizon Securities
2. **Obligation Explorer** — Browse 16 pre-loaded obligations across all process areas
3. **Ingest Circular** — Upload the mock amendment circular (auto-generated in `data/circulars/`)
4. **Change Feed** — Run the Change Detection Agent to see the SLA modification
5. **Gap Analysis** — Run the Gap-Finder Agent to flag breached SLAs and missing evidence
6. **Ask Agent** — Query: "What's our new grievance SLA and are we compliant?"

---

## 🧩 Module Overview

| Module | Description | Key Files |
|--------|-------------|-----------|
| **A** — Ingestion | PDF → clause chunks | `services/parser.py`, `routers/ingest.py` |
| **B** — Extraction | Clause → JSON obligations (LLM) | `services/extractor.py`, `llm/prompts.py` |
| **C** — Mapping | Obligation → process areas | `services/mapper.py` |
| **D** — Evidence Ledger | Append-only compliance tracking | `services/ledger.py`, `routers/evidence.py` |
| **E** — Agents | Change Detection, Gap-Finder, Query, Remediation | `services/*_agent.py`, `routers/agents.py` |
| **F** — Dashboard | Health score, charts, explorer, chat | `frontend/src/pages/` |

---

## 📊 Evaluation Metrics

| Metric | Target |
|--------|--------|
| Extraction accuracy | ≥ 85% on hand-verified clauses |
| Classification precision | ≥ 80% |
| Change-detection accuracy | ≥ 90% |
| Time saved | Manual ~40 hrs → ComplyAgent ~2 hrs |
| Gap detection | 100% of seeded gaps correctly flagged |

---

## 👥 Mock Firm Profile

**Horizon Securities Pvt. Ltd.** — Mid-size stockbroker

| Category | Count |
|----------|-------|
| Total Obligations | 16 |
| Compliant | 9 (56%) |
| Partially Compliant | 3 (19%) |
| Non-Compliant | 2 (13%) |
| Not Yet Due | 2 (13%) |

---

## 📁 Project Structure

```
complyagent/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── database.py       # SQLAlchemy setup
│   │   ├── models/           # ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic + agents
│   │   ├── llm/              # LLM client + prompts
│   │   └── vector_store/     # ChromaDB
│   ├── data/
│   │   ├── seed.py           # Database seeder
│   │   └── mock_amendment.py # Demo circular
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard, Explorer, Detail, Chat, etc.
│   │   ├── components/       # Layout, shared components
│   │   ├── services/         # API client
│   │   └── index.css         # Design system
│   └── package.json
└── README.md
```
