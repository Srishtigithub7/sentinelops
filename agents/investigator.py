from datetime import datetime
from typing import Any


class IncidentInvestigator:
    """
    SentinelOps incident investigation engine.

    This component correlates signals extracted from production
    logs and produces evidence-backed hypotheses.
    """

    def __init__(self, analysis: dict[str, Any]):
        self.analysis = analysis

        self.hypotheses = []

    def detect_database_pool_incident(self) -> None:
        """
        Detect database connection pool exhaustion.
        """

        pool_usage = self.analysis.get(
            "max_pool_utilization"
        )

        pool_exhausted = self.analysis.get(
            "pool_exhausted_events",
            0
        )

        timeouts = self.analysis.get(
            "connection_timeouts",
            0
        )

        if pool_usage == 100:
            score = 40

            evidence = [
                "Database connection pool reached 100% utilization."
            ]

            if pool_exhausted > 0:
                score += 30

                evidence.append(
                    "Database connection pool exhaustion was reported."
                )

            if timeouts > 0:
                score += 20

                evidence.append(
                    f"{timeouts} database connection timeouts were detected."
                )

            self.hypotheses.append(
                {
                    "cause": "Database connection pool exhaustion",
                    "score": score,
                    "evidence": evidence,
                }
            )

    def detect_api_impact(self) -> None:
        """
        Determine whether the database issue affected the API.
        """

        max_response_time = self.analysis.get(
            "max_response_time_ms"
        )

        critical_events = self.analysis.get(
            "critical_events",
            []
        )

        api_events = [
            event
            for event in critical_events
            if event["service"] == "api-gateway"
        ]

        if max_response_time and max_response_time > 1000:

            evidence = [
                f"Maximum API response time reached "
                f"{max_response_time} ms."
            ]

            if api_events:
                evidence.append(
                    "Critical API gateway events were detected."
                )

            self.hypotheses.append(
                {
                    "cause": "API degradation caused by downstream dependency failure",
                    "score": 25,
                    "evidence": evidence,
                }
            )

    def detect_deployment_correlation(
        self,
        events: list[dict[str, Any]]
    ) -> None:
        """
        Look for a deployment occurring before the incident.
        """

        deployment_events = [
            event
            for event in events
            if event["service"] == "deployment"
        ]

        if not deployment_events:
            return

        first_deployment = deployment_events[0]

        deployment_time = datetime.strptime(
            first_deployment["time"],
            "%H:%M:%S"
        )

        critical_events = self.analysis.get(
            "critical_events",
            []
        )

        for event in critical_events:

            critical_time = datetime.strptime(
                event["time"],
                "%H:%M:%S"
            )

            time_difference = (
                critical_time - deployment_time
            ).total_seconds()

            # Deployment happened shortly before the incident.
            if 0 <= time_difference <= 300:

                self.hypotheses.append(
                    {
                        "cause": "Recent deployment may have triggered the incident",
                        "score": 20,
                        "evidence": [
                            "A deployment occurred shortly before "
                            "the first critical incident.",
                            (
                                f"Deployment-to-incident interval: "
                                f"{int(time_difference)} seconds."
                            ),
                        ],
                    }
                )

                break

    def rank_hypotheses(self) -> list[dict[str, Any]]:
        """
        Rank hypotheses according to evidence score.
        """

        return sorted(
            self.hypotheses,
            key=lambda item: item["score"],
            reverse=True
        )

    def investigate(
        self,
        events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Execute the complete investigation.
        """

        self.hypotheses = []

        self.detect_database_pool_incident()

        self.detect_api_impact()

        self.detect_deployment_correlation(
            events
        )

        ranked = self.rank_hypotheses()

        root_cause = (
            ranked[0]
            if ranked
            else None
        )

        return {
            "root_cause": root_cause,
            "hypotheses": ranked,
            "investigation_status": (
                "ROOT_CAUSE_IDENTIFIED"
                if root_cause
                else "INSUFFICIENT_EVIDENCE"
            ),
        }