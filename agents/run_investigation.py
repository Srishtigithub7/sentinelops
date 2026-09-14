import sys
from pathlib import Path

# Add the SentinelOps project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))


from tools.log_analyzer import run_analysis
from agents.investigator import IncidentInvestigator


LOG_FILE = PROJECT_ROOT / "data" / "logs" / "production_api.log"


def main():

    print()
    print("=" * 60)
    print("           SENTINELOPS INVESTIGATION")
    print("=" * 60)

    # -----------------------------------------
    # STEP 1: Analyze raw production logs
    # -----------------------------------------

    print()
    print("[1/3] Analyzing production logs...")

    result = run_analysis(str(LOG_FILE))

    events = result["events"]
    analysis = result["analysis"]

    print("      ✓ Log analysis complete")

    # -----------------------------------------
    # STEP 2: Initialize investigator
    # -----------------------------------------

    print()
    print("[2/3] Correlating incident signals...")

    investigator = IncidentInvestigator(
        analysis
    )

    # -----------------------------------------
    # STEP 3: Investigate
    # -----------------------------------------

    print()
    print("[3/3] Generating investigation hypotheses...")

    investigation = investigator.investigate(
        events
    )

    print("      ✓ Investigation complete")

    # -----------------------------------------
    # RESULTS
    # -----------------------------------------

    print()
    print("=" * 60)
    print("                 INCIDENT RESULT")
    print("=" * 60)

    print()
    print(
        f"STATUS: {investigation['investigation_status']}"
    )

    print()
    print("ROOT CAUSE HYPOTHESES")
    print("-" * 60)

    for index, hypothesis in enumerate(
        investigation["hypotheses"],
        start=1
    ):

        print()
        print(
            f"[{index}] {hypothesis['cause']}"
        )

        print(
            f"Evidence Score: "
            f"{hypothesis['score']}"
        )

        print("Evidence:")

        for evidence in hypothesis["evidence"]:
            print(
                f"  • {evidence}"
            )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()