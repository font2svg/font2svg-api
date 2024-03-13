import io
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, UploadFile
from fontTools.ttLib import TTFont
from freetype import Face
from yuanfen import ErrorResponse, Logger, SuccessResponse

from . import __version__
from .converter import Converter
from .utils import generate_font_info_cache, get_font_id, remove_font_svg_cache

logger = Logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(f"api service started, version: {__version__}")
    if not os.path.exists("data/fonts"):
        os.makedirs("data/fonts")
    if not os.path.exists("data/cache"):
        os.makedirs("data/cache")
    yield
    logger.info("api service stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return SuccessResponse()


@app.get("/font/{font_file}/char/{unicode}.svg")
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


@app.post("/font/upload")
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
