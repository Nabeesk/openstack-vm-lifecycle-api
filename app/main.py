from fastapi import FastAPI

from app.api.v1.vms import router as vms_router

app = FastAPI(
    title="OpenStack VM Lifecycle API (PoC)",
    version="0.1.0",
    description="Simple REST API for OpenStack-like VM lifecycle operations (local mock).",
)


@app.get("/healthz", tags=["health"])
def healthz() -> dict:
    return {"status": "ok"}


app.include_router(vms_router, prefix="/v1")
