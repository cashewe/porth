from camau import Task


async def fraud_checker(request):
    transaction = request["transaction"]
    customer = request["customer"]
    risk_score = 0.1
    if transaction["amount"] >= 1_000:
        risk_score += 0.5
    if customer["account-age-days"] < 30:
        risk_score += 0.3

    return {
        "transaction-id": transaction["id"],
        "risk-score": min(risk_score, 0.99),
        "requires-review": risk_score >= 0.4,
    }


async def policy_checker(request):
    transaction = request["transaction"]
    customer = request["customer"]
    approved = transaction["currency"] in {"EUR", "GBP", "USD"} and customer[
        "country"
    ] not in {"IR", "KP"}
    return {
        "transaction-id": transaction["id"],
        "approved": approved,
        "reason": "accepted" if approved else "unsupported-market",
    }


async def priority_healthcheck():
    return True


tasks = {
    "fraud-checker": Task(
        fraud_checker,
        healthcheck=priority_healthcheck,
    ),
    "policy-checker": Task(
        policy_checker,
        healthcheck=priority_healthcheck,
    ),
}
