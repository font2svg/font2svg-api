import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fontTools.ttLib import TTFont
from yuanfen import Logger, SuccessResponse

from . import __version__
from .constants import ADMIN_TOKEN, CACHE_DIR, FONTS_DIR
from .routers import fonts
from .utils import generate_font_meta_cache_file

logger = Logger()


# Create necessary directories if not exists
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Display warning if ADMIN_TOKEN not set
if not ADMIN_TOKEN:
    logger.warning("ADMIN_TOKEN not set, everyone can access admin APIs")


@asynccontextmanager
async def lifespan(_: FastAPI):
    for font_file in os.listdir(FONTS_DIR):
        if font_file.endswith(".ttf") or font_file.endswith(".otf"):
            font_path = f"{FONTS_DIR}/{font_file}"
            generate_font_meta_cache_file(TTFont(font_path), CACHE_DIR, font_file)
            logger.info(f"font meta cache generated: {font_file}")
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
