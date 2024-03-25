import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from yuanfen import Logger, SuccessResponse

from . import __version__
from .constants import ADMIN_TOKEN, CACHE_DIR, FONTS_DIR
from .routers import fonts

logger = Logger()


# Create necessary directories if not exists
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Display warning if ADMIN_TOKEN not set
if not ADMIN_TOKEN:
    logger.warning("ADMIN_TOKEN not set, everyone can access admin APIs")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(f"api service started, version: {__version__}")
    yield
    logger.info("api service stopped")


app = FastAPI(
    title="Font2svg Api",
    summary="Font2svg server-side project, written in Python.",
    version=__version__,
    lifespan=lifespan,
)
app.include_router(fonts.router)


@app.get("/health", summary="Health check", tags=["Others"])
def health_check():
    return SuccessResponse()
