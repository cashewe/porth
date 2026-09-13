from camau import Task


async def stable_predictor(request):
    return {**request, "model": "stable", "risk-score": 0.36}


async def candidate_predictor(request):
    return {**request, "model": "candidate", "risk-score": 0.72}


async def fraud_checker(request):
    return {**request, "handled-by": "fraud-service", "risk": 0.55}


async def policy_checker(request):
    return {**request, "handled-by": "policy-service", "risk": 0.45}


async def risk_scorer(request):
    return {**request, "risk-score": 0.63}


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
    "review-queue": Task(
        review_queue,
        healthcheck=priority_healthcheck,
    ),
    "approval-service": Task(
        approval_service,
        healthcheck=priority_healthcheck,
    ),
}
