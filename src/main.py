import io
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Response, UploadFile
from fontTools.ttLib import TTFont
from freetype import Face
from yuanfen import Config, ErrorResponse, Logger, SuccessResponse

from . import __version__
from .converter import Converter
from .utils import generate_font_info_cache, get_font_id, remove_font_svg_cache

logger = Logger()

# Create necessary directories and config file if not exists
if not os.path.exists("data/fonts"):
    os.makedirs("data/fonts")
if not os.path.exists("data/cache"):
    os.makedirs("data/cache")
if not os.path.exists("data/config.yaml"):
    admin_token = secrets.token_urlsafe(16)
    logger.info("config.yaml not found")
    with open("data/config.yaml", "w") as f:
        f.write(f"admin_token: {admin_token}\n")
    logger.info(f"created config.yaml with random admin_token: {admin_token}")

config = Config("data/config.yaml")


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


def admin_auth(admin_token: str = Header(None)):
    if admin_token != config["admin_token"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.get("/health", summary="Health check")
def health_check():
    return SuccessResponse()


@app.get("/font/{font_file}/char/{unicode}.svg", summary="Get character svg")
def get_character(font_file: str, unicode: str):
    if not os.path.exists(f"data/fonts/{font_file}"):
        raise HTTPException(status_code=404, detail="Font not found")

    svg_cache_file_path = f"data/cache/{font_file}/svg/{unicode}.svg"

    if not os.path.exists(svg_cache_file_path):
        face = Face(f"data/fonts/{font_file}")
        converter = Converter(face, font_file)
        converter.generate_svg(unicode)

    with open(svg_cache_file_path, "r") as f:
        return Response(content=f.read(), media_type="image/svg+xml")


@app.post("/font", summary="Upload font file (admin_token needed)", dependencies=[Depends(admin_auth)])
def upload(file: UploadFile):
    if file.content_type not in ["font/ttf", "font/otf"]:
        return ErrorResponse(message="Only support ttf or otf fonts")
    fileBytes = file.file.read()
    font = TTFont(io.BytesIO(fileBytes))
    font_id = get_font_id(font)
    extension = os.path.splitext(file.filename)[1].lower()
    font_file = f"{font_id}{extension}"

    with open(f"data/fonts/{font_file}", "wb") as f:
        f.write(fileBytes)

    generate_font_info_cache(font, font_file)
    remove_font_svg_cache(font_file)

    logger.info(f"{font_file} uploaded success")
    return SuccessResponse()
