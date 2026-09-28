import os
import hindsight_client
from google import genai
from dotenv import load_dotenv

load_dotenv()

gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
hindsight = hindsight_client.Hindsight(base_url="https://api.hindsight.vectorize.io", 
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "bug-bounty-triage")


def triage_vulnerability(vulnerability_description: str) -> str:
    memories = []

    try:
        results = hindsight.recall(
            bank_id=BANK_ID,
            query=vulnerability_description
        )
        memories = [m.text for m in results]
    except Exception as e:
        print(f"Hindsight recall note: {e}")

    memory_context = "\n".join(
        f"- {m}" for m in memories
    ) if memories else "No relevant historical triage patterns found yet."

    system_instruction = f"""
You are an expert Bug Bounty Triage Agent with persistent memory.

Your role: Evaluate incoming security vulnerability submissions,
assign severity, identify cross-target patterns, and adapt to
researcher preferences over time.

--- HISTORICAL HINDSIGHT MEMORY CONTEXT ---
{memory_context}
------------------------------------------

Provide a concise professional triage summary:
Before the triage summary, analyze the historical Hindsight context and identify whether the current finding is:
- SAME FINDING: likely a duplicate of a previous submission.
- CROSS-TARGET PATTERN: a similar vulnerability pattern or root cause on a different target or endpoint.
- REGRESSION: a previously resolved issue that appears to have returned.

State the relationship only when supported by the historical evidence.

1. Vunerability Type & Estimated Severity
2. Historical Context / Pattern Match
3. Key Triage Recommendations
"""

    response = gemini.models.generate_content(
        model="gemini-3.8-flash",
        contents=vulnerability_description,
        config={"system_instruction": system_instruction}
    )

    agent_output = response.text

    try:
        hindsight.retain(
            bank_id=BANK_ID,
            content=(
                f"Submission: {vulnerability_description} | "
                f"Triage Outcome: {agent_output[:200]}..."
            )
        )
    except Exception as e:
        print(f"Hindsight retain note: {e}")

    return agent_output


if __name__ == "__main__":
    print("Testing Triage Agent Core...\n")

    sample_bug = (
        "Found an IDOR vulnerability on /api/v1/users/1024 "
        "allowing unauthorized profile modifications."
    )

    print("Input Bug:", sample_bug)
    print("\n--- Agent Response ---")
    print(triage_vulnerability(sample_bug))
