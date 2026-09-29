from src.agent import hindsight, BANK_ID

seed_findings = [
    """
[SYNTHETIC DEMO FINDING]
Program: DemoShop
Endpoint: GET /api/orders/1042
Vulnerability: IDOR / Broken Object Level Authorization
Severity: High
Impact: An authenticated user could access another user's order details by changing the order ID.
Triage outcome: Valid security finding. Authorization should be enforced against the requesting user's ownership.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: CloudBoard
Endpoint: GET /api/users/782/profile
Vulnerability: IDOR
Severity: High
Impact: Changing the numeric user ID exposed another user's profile information.
Triage outcome: Valid. Horizontal authorization failure.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: DemoForum
Endpoint: POST /profile/bio
Vulnerability: Stored XSS
Severity: High
Impact: JavaScript supplied in a profile biography was rendered to other users viewing the profile.
Triage outcome: Valid. Persistent cross-user script execution.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: MarketDemo
Endpoint: POST /api/coupons/apply
Vulnerability: Business Logic / Coupon Abuse
Severity: Medium
Impact: A single-use discount coupon could be applied repeatedly by replaying the checkout request.
Triage outcome: Valid logic flaw. Server-side coupon state must be enforced atomically.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: TicketDemo
Endpoint: POST /api/tickets/transfer
Vulnerability: Race Condition
Severity: High
Impact: Parallel requests could transfer the same ticket more than once.
Triage outcome: Valid concurrency issue. The state transition requires atomic server-side locking or equivalent protection.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: AccountDemo
Endpoint: POST /api/password/change
Vulnerability: Broken Authorization
Severity: High
Impact: A crafted request allowed a logged-in user to modify another account's password identifier.
Triage outcome: Valid if reproducible. Authorization must be tied to the authenticated account.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: MediaDemo
Endpoint: GET /api/files/download?file_id=8821
Vulnerability: Unauthorized File Access
Severity: High
Impact: Sequential file identifiers allowed access to files belonging to other users.
Triage outcome: Valid access-control issue closely related to IDOR/BOLA.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: BlogDemo
Endpoint: POST /api/comments
Vulnerability: Reflected/Stored Input Injection
Severity: Medium
Impact: Unsanitized comment content was rendered in a privileged moderation interface.
Triage outcome: Potential stored XSS. Requires confirmation of executable browser context.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: WalletDemo
Endpoint: POST /api/wallet/transfer
Vulnerability: Business Logic / Parameter Manipulation
Severity: Critical
Impact: Client-controlled transfer values could be modified without adequate server-side validation.
Triage outcome: Potential critical financial-impact issue. Requires controlled reproduction and authorization.
""",

    """
[SYNTHETIC DEMO FINDING]
Program: TeamDemo
Endpoint: POST /api/teams/invite
Vulnerability: Privilege / Role Manipulation
Severity: High
Impact: A lower-privileged team member could manipulate role parameters when inviting another account.
Triage outcome: Valid if the server accepts unauthorized role assignment. Requires server-side RBAC enforcement.
"""
]

print(f"Seeding {len(seed_findings)} synthetic findings into Hindsight...")

for index, finding in enumerate(seed_findings, start=1):
    try:
        hindsight.retain(
            bank_id=BANK_ID,
            content=finding.strip()
        )
        print(f"[{index}/10] RETAINED")
    except Exception as e:
        print(f"[{index}/10] FAILED: {type(e).__name__}: {e}")

print("SEED COMPLETE")
