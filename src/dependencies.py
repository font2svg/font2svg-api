import os

from fastapi import Header, HTTPException


def admin_auth(admin_token: str = Header(None)):
    if admin_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
