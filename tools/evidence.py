from typing import Any


class EvidenceCorrelator:
    """
    Combines incident signals, root-cause hypotheses,
    and retrieved operational knowledge into one
    structured evidence package.
    """

    def __init__(
        self,
        analysis: dict[str, Any],
        investigation: dict[str, Any],
        retrieved_knowledge: list[dict[str, Any]],
    ):
        self.analysis = analysis
        self.investigation = investigation
        self.retrieved_knowledge = retrieved_knowledge

    def build_evidence_package(self) -> dict[str, Any]:

        root_cause = self.investigation.get(
            "root_cause"
        )

        evidence = {
            "incident_summary": {
                "total_events": self.analysis.get(
                    "total_events"
                ),
                "errors": self.analysis.get(
                    "error_count"
                ),
                "warnings": self.analysis.get(
                    "warning_count"
                ),
                "connection_timeouts": self.analysis.get(
                    "connection_timeouts"
                ),
                "max_pool_utilization": self.analysis.get(
                    "max_pool_utilization"
                ),
                "max_response_time_ms": self.analysis.get(
                    "max_response_time_ms"
                ),
            },

            "root_cause_candidate": (
                root_cause["cause"]
                if root_cause
                else None
            ),

            "root_cause_score": (
                root_cause["score"]
                if root_cause
                else 0
            ),

            "root_cause_evidence": (
                root_cause["evidence"]
                if root_cause
                else []
            ),

            "alternative_hypotheses": [
                {
                    "cause": hypothesis["cause"],
                    "score": hypothesis["score"],
                }
                for hypothesis in self.investigation.get(
                    "hypotheses",
                    []
                )[1:]
            ],

            "knowledge": [
                {
                    "source": item["source"],
                    "similarity": round(
                        item["score"],
                        3
                    ),
                    "content": item["text"],
                }
                for item in self.retrieved_knowledge
            ],
        }

        return evidence

    def print_evidence_package(
        self,
        package: dict[str, Any]
    ) -> None:

        print()
        print("=" * 60)
        print("             EVIDENCE PACKAGE")
        print("=" * 60)

        print()
        print("INCIDENT SIGNALS")
        print("-" * 60)

        for key, value in package[
            "incident_summary"
        ].items():

            print(
                f"{key:<30}: {value}"
            )

        print()
        print("PRIMARY ROOT CAUSE")
        print("-" * 60)

        print(
            package["root_cause_candidate"]
        )

        print(
            f"Confidence score: "
            f"{package['root_cause_score']}"
        )

        print()
        print("SUPPORTING EVIDENCE")
        print("-" * 60)

        for evidence in package[
            "root_cause_evidence"
        ]:

            print(
                f"• {evidence}"
            )

        print()
        print("ALTERNATIVE HYPOTHESES")
        print("-" * 60)

        for hypothesis in package[
            "alternative_hypotheses"
        ]:

            print(
                f"• {hypothesis['cause']} "
                f"(score: {hypothesis['score']})"
            )

        print()
        print("RETRIEVED OPERATIONAL KNOWLEDGE")
        print("-" * 60)

        for item in package[
            "knowledge"
        ]:

            print(
                f"\nSource: {item['source']}"
            )

            print(
                f"Similarity: {item['similarity']}"
            )

            print(
                item["content"]
            )

        print()
        print("=" * 60)