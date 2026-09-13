from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz():
    """Is the app healthy?"""
    return {"status": "healthy"}
