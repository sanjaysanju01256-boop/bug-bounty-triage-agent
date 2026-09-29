import os
import time
from hindsight_client import Hindsight
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_config(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None

openrouter = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=get_config("OPENROUTER_API_KEY")
)

hindsight = Hindsight(
    api_key=get_config("HINDSIGHT_API_KEY")
)

BANK_ID = get_config("HINDSIGHT_BANK_ID") or "bug-bounty-triage"


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


1. Vulnerability Type & Estimated Severity
2. OWASP Top 10 Category — choose the most appropriate category ONLY from:
   - A01 — Broken Access Control
   - A03 — Injection
   - A04 — Insecure Design
   - A05 — Security Misconfiguration
   - A07 — Identification & Authentication Failures
   - A10 — SSRF
   If none clearly applies, state "Not one of the six configured categories."
3. Historical Context / Pattern Match
4. Key Triage Recommendations
"""

    try:
        response = openrouter.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": vulnerability_description}
            ]
        )

        agent_output = response.choices[0].message.content

        if not agent_output or not agent_output.strip():
            return "⚠️ The AI returned an empty response. Please try again."

    except Exception as e:
        print(f"OpenRouter error: {e}")
        return "⚠️ The AI service is temporarily unavailable. Please try again."


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

    if memories:
        agent_output += "\n\n--- 🧠 HINDSIGHT MEMORY USED ---\n"
        agent_output += memory_context

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
