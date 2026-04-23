from __future__ import annotations

from fastapi import FastAPI

try:
    from server.routers.diagnosis import router as diagnosis_router
    from server.routers.grading import router as grading_router
except ModuleNotFoundError:  # pragma: no cover - for `cd server && uvicorn app:app`
    from routers.diagnosis import router as diagnosis_router
    from routers.grading import router as grading_router


app = FastAPI(title="TeacherSkills API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(grading_router)
app.include_router(diagnosis_router)
