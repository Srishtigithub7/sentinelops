import os
import json
from openai import OpenAI


class LLMReasoner:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Please configure your OpenAI API key."
            )

        self.client = OpenAI(api_key=api_key)

    def generate_report(self, evidence_package):

        prompt = f"""
You are an experienced Site Reliability Engineer investigating a
production incident.

Analyze the following evidence package and generate a professional
incident investigation report.

EVIDENCE PACKAGE:

{json.dumps(evidence_package, indent=2)}

Return the result using exactly these sections:

1. INCIDENT SEVERITY
2. ROOT CAUSE
3. ROOT CAUSE EXPLANATION
4. EVIDENCE CHAIN
5. CUSTOMER IMPACT
6. CONTRIBUTING FACTORS
7. RECOMMENDED ACTIONS
8. ROLLBACK RECOMMENDATION
9. CONFIDENCE

Rules:

- Do not invent evidence.
- Base conclusions only on the provided evidence.
- Clearly distinguish confirmed evidence from hypotheses.
- Be concise and technical.
- Give practical production-safe recommendations.
"""

        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        return response.output_text