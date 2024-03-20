import io
import os
import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Response, UploadFile
from fontTools.ttLib import TTFont
from yuanfen import ErrorResponse, Logger, SuccessResponse

from . import __version__
from .converter import Converter
from .svg_cache import SvgCache
from .utils import generate_font_meta_cache, get_font_id, remove_font_svg_cache

logger = Logger()

# Constants
FONTS_DIR = "data/fonts"
CACHE_DIR = "data/cache"

# Environment variables
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
CACHE__ENABLED = os.getenv("CACHE__ENABLED", "true").lower() == "true"
CACHE__PERSISTENT = os.getenv("CACHE__PERSISTENT", "true").lower() == "true"
CACHE__MEM_CHARS_LIMIT = int(os.getenv("CACHE__MEM_CHARS_LIMIT", "10000"))

# Create necessary directories if not exists
os.makedirs(FONTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Display warning if ADMIN_TOKEN not set
if not ADMIN_TOKEN:
    logger.warning("ADMIN_TOKEN not set, everyone can access admin APIs")


svg_cache = SvgCache(CACHE__MEM_CHARS_LIMIT)


@asynccontextmanager
async def lifespan(_: FastAPI):
    for font_file in os.listdir(FONTS_DIR):
        if font_file.endswith(".ttf") or font_file.endswith(".otf"):
            font_path = f"{FONTS_DIR}/{font_file}"
            generate_font_meta_cache(TTFont(font_path), CACHE_DIR, font_file)
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


def admin_auth(admin_token: str = Header(None)):
    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.get("/health", summary="Health check")
def health_check():
    return SuccessResponse()


@app.get("/benchmark_base", summary="Benchmark baseline api")
def benchmark_base():
    return "Hello, World!"


@app.get("/font/{font_file}/char/{unicode}.svg", summary="Get character svg")
def get_character(font_file: str, unicode: str):
    if not os.path.exists(f"{FONTS_DIR}/{font_file}"):
        raise HTTPException(status_code=404, detail="Font not found")

    if CACHE__ENABLED:
        cache = get_cache(font_file, unicode)
        if cache["svg_content"]:
            return Response(content=cache["svg_content"], media_type="image/svg+xml")

        if os.path.exists(cache["svg_file_path"]):
            with open(cache["svg_file_path"], "r") as f:
                svg_content = f.read()
                save_cache_mem(font_file, unicode, svg_content)
                return Response(content=svg_content, media_type="image/svg+xml")

        converter = Converter(FONTS_DIR, font_file)
        svg_content = converter.convert(unicode)
        save_cache_mem(font_file, unicode, svg_content)
        save_cache_file(font_file, unicode, svg_content)
        return Response(content=svg_content, media_type="image/svg+xml")

    else:
        converter = Converter(FONTS_DIR, font_file)
        svg_content = converter.convert(unicode)
        return Response(content=svg_content, media_type="image/svg+xml")


@app.post("/font", summary="Upload font file (admin_token needed)", dependencies=[Depends(admin_auth)])
def upload(file: UploadFile):
    if file.content_type not in ["font/ttf", "font/otf"]:
        return ErrorResponse(message="Only support ttf or otf fonts")
    fileBytes = file.file.read()
    font = TTFont(io.BytesIO(fileBytes))
    font_id = get_font_id(font)
    extension = os.path.splitext(file.filename)[1].lower()
    font_file = f"{font_id}{extension}"

    with open(f"{FONTS_DIR}/{font_file}", "wb") as f:
        f.write(fileBytes)

    generate_font_meta_cache(font, CACHE_DIR, font_file)
    remove_font_svg_cache(CACHE_DIR, font_file)

    logger.info(f"{font_file} uploaded success")
    return SuccessResponse()


def get_cache(font_file: str, unicode: str):
    global svg_cache
    cache_key = f"{font_file}/{unicode}"
    if cache_key not in svg_cache:
        svg_cache[cache_key] = {
            "lock": threading.Lock(),
            "svg_content": None,
            "svg_file_path": f"{CACHE_DIR}/{font_file}/svg/{unicode}.svg",
        }
    return svg_cache[cache_key]


def save_cache_file(font_file: str, unicode: str, svg_content: str):
    cache = get_cache(font_file, unicode)
    if cache["lock"].acquire():
        try:
            os.makedirs(f"{CACHE_DIR}/{font_file}/svg", exist_ok=True)
            with open(cache["svg_file_path"], "w") as f:
                f.write(svg_content)
        finally:
            cache["lock"].release()


def save_cache_mem(font_file: str, unicode: str, svg_content: str):
    cache = get_cache(font_file, unicode)
    cache["svg_content"] = svg_content
