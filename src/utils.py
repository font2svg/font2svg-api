import io
import json
import os
import shutil
import threading

from fontTools.ttLib import TTFont

from .constants import (
    CACHE__ENABLED,
    CACHE__MEM_CHARS_LIMIT,
    CACHE_DIR,
    FONT_NAME_IDS,
    FONTS_DIR,
)
from .models.cache import Cache

cache = Cache(CACHE__MEM_CHARS_LIMIT)


def get_font_id(font_file: str | bytes):
    font = TTFont(io.BytesIO(font_file)) if isinstance(font_file, bytes) else TTFont(f"{FONTS_DIR}/{font_file}")
    return font["name"].getDebugName(FONT_NAME_IDS["POST_SCRIPT_NAME"]).replace(" ", "-")


def get_font_meta_from_file(font_file: str):
    font_path = f"{FONTS_DIR}/{font_file}"
    if not os.path.exists(font_path):
        return None

    font_meta = {
        "font_file": font_file,
    }
    font = TTFont(font_path)

    for name_record in font["name"].names:
        for name_id_key in FONT_NAME_IDS.keys():
            if name_record.nameID == FONT_NAME_IDS[name_id_key]:
                if font_meta.get(name_id_key.lower()) is None:
                    font_meta[name_id_key.lower()] = []

                font_meta[name_id_key.lower()].append(
                    {
                        "platformId": name_record.platformID,
                        "encodingId": name_record.platEncID,
                        "langId": name_record.langID,
                        "value": name_record.toStr(),
                    }
                )
    return font_meta


def get_font_meta_from_cache(font_file: str):
    meta_cache_file_path = f"{CACHE_DIR}/{font_file}/font_meta.json"
    if not os.path.exists(meta_cache_file_path):
        return None
    with open(meta_cache_file_path, "r") as f:
        return json.load(f)


def get_font_meta(font_file: str):
    if CACHE__ENABLED:
        font_meta_cache = get_font_meta_from_cache(font_file)
        if font_meta_cache:
            return font_meta_cache
        else:
            font_meta = get_font_meta_from_file(font_file)
            save_font_meta_cache(font_file, font_meta)
            return font_meta
    else:
        return get_font_meta_from_file(font_file)


def save_font_meta_cache(font_file: str, font_meta: any):
    font_cache_dir = f"{CACHE_DIR}/{font_file}"
    os.makedirs(font_cache_dir, exist_ok=True)
    with open(f"{font_cache_dir}/font_meta.json", "w") as f:
        json.dump(font_meta, f, indent=4, ensure_ascii=False)


def remove_font_cache_files(font_file: str):
    font_cache_dir = f"{CACHE_DIR}/{font_file}"
    if os.path.exists(font_cache_dir):
        shutil.rmtree(font_cache_dir)


def get_charcode_from_unicode_str(unicode_str: str):
    return int(unicode_str, 16)


def get_charcode_from_char(char: str):
    return ord(char)


def get_unicode_str_from_char(char: str):
    return hex(ord(char))[2:].zfill(4).upper()


def get_unicode_str_from_charcode(charcode: int):
    return hex(charcode)[2:].zfill(4).upper()


def get_char_cache(font_file: str, unicode: str):
    cache_key = f"{font_file}/{unicode}"
    if cache_key not in cache:
        cache[cache_key] = {
            "lock": threading.Lock(),
            "svg_content": None,
            "svg_file_path": f"{CACHE_DIR}/{font_file}/svg/{unicode}.svg",
        }
    return cache[cache_key]


def save_char_cache(font_file: str, unicode: str, svg_content: str, skip_file: bool = False):
    char_cache = get_char_cache(font_file, unicode)
    char_cache["svg_content"] = svg_content
    if not skip_file and char_cache["lock"].acquire():
        try:
            os.makedirs(f"{CACHE_DIR}/{font_file}/svg", exist_ok=True)
            with open(char_cache["svg_file_path"], "w") as f:
                f.write(svg_content)
        finally:
            char_cache["lock"].release()
