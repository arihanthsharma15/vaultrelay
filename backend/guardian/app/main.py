from fastapi import FastAPI

app = FastAPI(
    title="VaultRelay Guardian",
    description="Cloud gateway for VaultRelay.",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "guardian"}
