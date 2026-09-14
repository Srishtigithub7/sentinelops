from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT SENTINELOPS ENGINE
# ============================================================

from tools.log_analyzer import run_analysis
from agents.investigator import IncidentInvestigator
from tools.retriever import KnowledgeRetriever
from tools.evidence import EvidenceCorrelator
from agents.report_generator import IncidentReportGenerator


# ============================================================
# FILE PATHS
# ============================================================

LOG_FILE = (
    PROJECT_ROOT
    / "data"
    / "logs"
    / "production_api.log"
)

KNOWLEDGE_DIR = (
    PROJECT_ROOT
    / "data"
    / "runbooks"
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="SentinelOps API",
    description="AI-powered production incident investigation API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "name": "SentinelOps",
        "status": "operational",
        "version": "1.0.0"
    }


# ============================================================
# RUN INVESTIGATION
# ============================================================

@app.get("/api/investigate")
def investigate():

    # --------------------------------------------------------
    # PHASE 1 — LOG ANALYSIS
    # --------------------------------------------------------

    result = run_analysis(
        str(LOG_FILE)
    )

    events = result["events"]
    analysis = result["analysis"]

    # --------------------------------------------------------
    # PHASE 2 — INVESTIGATION
    # --------------------------------------------------------

    investigator = IncidentInvestigator(
        analysis
    )

    investigation = investigator.investigate(
        events
    )

    # --------------------------------------------------------
    # PHASE 3 — RAG
    # --------------------------------------------------------

    retriever = KnowledgeRetriever(
        str(KNOWLEDGE_DIR)
    )

    query = (
        "database connection pool exhausted "
        "connection timeout API 503 high latency"
    )

    retrieved = retriever.search(
        query,
        top_k=3
    )

    # --------------------------------------------------------
    # PHASE 4 — EVIDENCE
    # --------------------------------------------------------

    correlator = EvidenceCorrelator(
        analysis=analysis,
        investigation=investigation,
        retrieved_knowledge=retrieved,
    )

    evidence_package = (
        correlator.build_evidence_package()
    )

    # --------------------------------------------------------
    # PHASE 5 — REPORT
    # --------------------------------------------------------

    generator = IncidentReportGenerator()

    report = generator.generate_report(
        evidence_package
    )

    # --------------------------------------------------------
    # RETURN DATA TO FRONTEND
    # --------------------------------------------------------

    return {
        "status": "ROOT_CAUSE_IDENTIFIED",

        "incident": report,

        "analysis": analysis,

        "investigation": investigation,

        "knowledge": retrieved
    }