from pathlib import Path
import sys

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
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
# MAIN PIPELINE
# ============================================================

def main():

    print()
    print("=" * 60)
    print("              SENTINELOPS")
    print("         INCIDENT INVESTIGATION")
    print("=" * 60)

    # ========================================================
    # PHASE 1 — LOG INTELLIGENCE
    # ========================================================

    print()
    print("[PHASE 1] Log intelligence")

    result = run_analysis(
        str(LOG_FILE)
    )

    events = result["events"]
    analysis = result["analysis"]

    print("✓ Production logs analyzed")

    # ========================================================
    # PHASE 2 — INCIDENT CORRELATION
    # ========================================================

    print()
    print("[PHASE 2] Incident correlation")

    investigator = IncidentInvestigator(
        analysis
    )

    investigation = investigator.investigate(
        events
    )

    print("✓ Incident signals correlated")

    # ========================================================
    # PHASE 3 — RAG KNOWLEDGE RETRIEVAL
    # ========================================================

    print()
    print("[PHASE 3] Operational knowledge retrieval")

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

    print(
        f"✓ Retrieved {len(retrieved)} knowledge chunks"
    )

    # ========================================================
    # PHASE 4 — EVIDENCE CORRELATION
    # ========================================================

    print()
    print("[PHASE 4] Evidence correlation")

    correlator = EvidenceCorrelator(
        analysis=analysis,
        investigation=investigation,
        retrieved_knowledge=retrieved,
    )

    evidence_package = (
        correlator.build_evidence_package()
    )

    print("✓ Evidence package created")

    # ========================================================
    # PHASE 5 — INCIDENT REPORT GENERATION
    # ========================================================

    print()
    print("[PHASE 5] Incident report generation")

    report_generator = IncidentReportGenerator()

    report = report_generator.generate_report(
        evidence_package
    )

    print("✓ Incident report generated")

    # ========================================================
    # FINAL INCIDENT REPORT
    # ========================================================

    print()
    print("=" * 60)
    print("              SENTINELOPS")
    print("          AI INCIDENT REPORT")
    print("=" * 60)

    print()
    print(
        f"INCIDENT ID     : {report['incident_id']}"
    )

    print(
        f"SEVERITY        : {report['severity']}"
    )

    print(
        f"CONFIDENCE      : {report['confidence']}%"
    )

    # --------------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------------

    print()
    print("ROOT CAUSE")
    print("-" * 60)

    print(
        report["root_cause"]
    )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    print()
    print("ROOT CAUSE EXPLANATION")
    print("-" * 60)

    print(
        report["explanation"]
    )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    print()
    print("EVIDENCE CHAIN")
    print("-" * 60)

    for evidence in report["evidence"]:
        print(
            f"• {evidence}"
        )

    # --------------------------------------------------------
    # CUSTOMER IMPACT
    # --------------------------------------------------------

    print()
    print("CUSTOMER IMPACT")
    print("-" * 60)

    print(
        report["customer_impact"]
    )

    # --------------------------------------------------------
    # ALTERNATIVE HYPOTHESES
    # --------------------------------------------------------

    print()
    print("ALTERNATIVE HYPOTHESES")
    print("-" * 60)

    for hypothesis in report["alternative_hypotheses"]:

        print(
            f"• {hypothesis['hypothesis']} "
            f"(score: {hypothesis['score']})"
        )

    # --------------------------------------------------------
    # RECOMMENDED ACTIONS
    # --------------------------------------------------------

    print()
    print("RECOMMENDED ACTIONS")
    print("-" * 60)

    for index, action in enumerate(
        report["recommended_actions"],
        start=1
    ):

        print(
            f"{index}. {action}"
        )

    # ========================================================
    # COMPLETION
    # ========================================================

    print()
    print("=" * 60)
    print("        INVESTIGATION COMPLETE")
    print("=" * 60)
    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()