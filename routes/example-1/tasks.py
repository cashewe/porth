from camau import Task


async def fraud_checker(request):
    return {**request, "handled-by": "standard"}


async def policy_checker(request):
    return {**request, "handled-by": "priority"}


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
