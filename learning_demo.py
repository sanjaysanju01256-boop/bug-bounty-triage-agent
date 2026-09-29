from src.agent import hindsight, BANK_ID

query = """
A user can change the order ID in GET /api/orders/1042
and access another user's order information.
This appears to be an IDOR / BOLA authorization issue.
"""

print("=" * 60)
print("HINDSIGHT LEARNING CURVE DEMO")
print("=" * 60)

print("\nNEW FINDING:")
print(query.strip())

print("\n🧠 RECALLING HISTORICAL CONTEXT...\n")

results = hindsight.recall(
    bank_id=BANK_ID,
    query=query
)

print(f"Recalled {len(results.results)} historical memories.\n")

for i, result in enumerate(results.results[:5], 1):
    print(f"--- Memory {i} ---")
    print(result.text[:350])
    print()

print("=" * 60)
print("LEARNING PROOF: RELATED HISTORICAL CONTEXT FOUND")
print("=" * 60)
