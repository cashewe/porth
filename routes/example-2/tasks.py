from camau import Task


async def stable_predictor(request):
    risk_score = 0.2 if request["amount"] < 1_000 else 0.5
    return {**request, "model": "stable", "model-risk-score": risk_score}


async def candidate_predictor(request):
    risk_score = 0.3 if request["amount"] < 1_000 else 0.6
    return {**request, "model": "candidate", "model-risk-score": risk_score}


async def batch_predictor(request):
    risk_score = 0.25 if request["amount"] < 1_000 else 0.55
    return {**request, "model": "batch", "model-risk-score": risk_score}


async def fraud_checker(request):
    risk_score = 0.1
    if request["account-age-days"] < 30:
        risk_score += 0.5
    if request["country"] in {"IR", "KP"}:
        risk_score += 0.4
    return {
        "request-id": request["request-id"],
        "customer-id": request["customer-id"],
        "risk-score": min(risk_score, 0.99),
        "provider": "fraud-service",
    }


async def policy_checker(request):
    approved = request["currency"] in {"EUR", "GBP", "USD"}
    return {
        "request-id": request["request-id"],
        "approved": approved,
        "reason": "accepted" if approved else "unsupported-currency",
    }


async def risk_scorer(request):
    return {
        "request-id": request["request-id"],
        "model": request["model"],
        "risk-score": request["model-risk-score"],
    }


async def risk_aggregator(request):
    fraud_signal = request["fraud-signal"]
    policy_signal = request["policy-signal"]
    model_signal = request["model-signal"]
    risk_score = max(fraud_signal["risk-score"], model_signal["risk-score"])
    if not policy_signal["approved"]:
        risk_score = 0.95
    return {
        "request-id": fraud_signal["request-id"],
        "model": model_signal["model"],
        "risk-score": risk_score,
    }


async def review_queue(request):
    return {**request, "decision": "manual-review", "reviewed": True}


async def approval_service(request):
    return {**request, "decision": "approved", "reviewed": False}


async def priority_healthcheck():
    return True


tasks = {
    "stable-predictor": Task(
        stable_predictor,
        healthcheck=priority_healthcheck,
    ),
    "candidate-predictor": Task(
        candidate_predictor,
        healthcheck=priority_healthcheck,
    ),
    "batch-predictor": Task(
        batch_predictor,
        healthcheck=priority_healthcheck,
    ),
    "fraud-checker": Task(
        fraud_checker,
        healthcheck=priority_healthcheck,
    ),
    "policy-checker": Task(
        policy_checker,
        healthcheck=priority_healthcheck,
    ),
    "risk-scorer": Task(
        risk_scorer,
        healthcheck=priority_healthcheck,
    ),
    "risk-aggregator": Task(
        risk_aggregator,
        healthcheck=priority_healthcheck,
    ),
    "review-queue": Task(
        review_queue,
        healthcheck=priority_healthcheck,
    ),
    "approval-service": Task(
        approval_service,
        healthcheck=priority_healthcheck,
    ),
}
