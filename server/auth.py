from __future__ import annotations

import os

from fastapi import Header, HTTPException, status


DEFAULT_API_TOKEN = "dev-token"


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    expected_token = os.getenv("TEACHERSKILLS_API_SERVER_TOKEN", DEFAULT_API_TOKEN)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    provided_token = authorization.removeprefix("Bearer ").strip()
    if provided_token != expected_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
