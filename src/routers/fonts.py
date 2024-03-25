import os

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from yuanfen import ErrorResponse, Logger, SuccessResponse

from ..constants import CACHE__ENABLED, FONTS_DIR
from ..dependencies import admin_auth
from ..models.converter import Converter
from ..utils import (
    get_char_cache,
    get_font_id,
    get_font_meta,
    get_font_meta_from_cache,
    remove_font_cache_files,
    save_char_cache,
)

router = APIRouter(prefix="/fonts", tags=["Fonts"])
logger = Logger()


@router.post("/", summary="Upload font file (admin_token needed)", dependencies=[Depends(admin_auth)])
def upload_font(file: UploadFile):
    if file.content_type not in ["font/ttf", "font/otf"]:
        return ErrorResponse(message="Only support ttf or otf fonts")
    fileBytes = file.file.read()
    font_id = get_font_id(fileBytes)
    extension = os.path.splitext(file.filename)[1].lower()
    font_file = f"{font_id}{extension}"
    with open(f"{FONTS_DIR}/{font_file}", "wb") as f:
        f.write(fileBytes)
    remove_font_cache_files(font_file)
    font_meta = get_font_meta(font_file)
    logger.info(f"{font_file} uploaded success")
    return SuccessResponse(data=font_meta)


@router.get("/", summary="Get all uploaded fonts (admin_token needed)", dependencies=[Depends(admin_auth)])
def get_fonts():
    fonts = []
    for file in os.listdir(FONTS_DIR):
        if file.endswith(".ttf") or file.endswith(".otf"):
            font_meta = get_font_meta_from_cache(file) or get_font_meta(file)
            if font_meta:
                fonts.append(font_meta)
    return SuccessResponse(data=fonts)


@router.get("/{font_file}", summary="Get font meta (admin_token needed)", dependencies=[Depends(admin_auth)])
def get_font(font_file: str):
    font_meta = get_font_meta_from_cache(font_file) or get_font_meta(font_file)
    if font_meta is None:
        raise HTTPException(status_code=404, detail="Font not found")
    return SuccessResponse(data=font_meta)


@router.delete("/{font_file}", summary="Delete font file (admin_token needed)", dependencies=[Depends(admin_auth)])
def delete_font(font_file: str):
    font_path = f"{FONTS_DIR}/{font_file}"
    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found")
    os.remove(font_path)
    remove_font_cache_files(font_file)
    logger.info(f"{font_file} deleted success")
    return SuccessResponse()


@router.get("/{font_file}/characters/{unicode}.svg", summary="Get character svg")
def get_character(font_file: str, unicode: str):
    if not os.path.exists(f"{FONTS_DIR}/{font_file}"):
        raise HTTPException(status_code=404, detail="Font not found")

    if CACHE__ENABLED:
        cache = get_char_cache(font_file, unicode)
        if cache["svg_content"]:
            return Response(content=cache["svg_content"], media_type="image/svg+xml")

        if os.path.exists(cache["svg_file_path"]):
            with open(cache["svg_file_path"], "r") as f:
                svg_content = f.read()
                save_char_cache(font_file, unicode, svg_content, skip_file=True)
                return Response(content=svg_content, media_type="image/svg+xml")

        converter = Converter(FONTS_DIR, font_file)
        svg_content = converter.convert(unicode)
        save_char_cache(font_file, unicode, svg_content)
        return Response(content=svg_content, media_type="image/svg+xml")

    else:
        converter = Converter(FONTS_DIR, font_file)
        svg_content = converter.convert(unicode)
        return Response(content=svg_content, media_type="image/svg+xml")
