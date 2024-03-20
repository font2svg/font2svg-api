import os
import random
import threading

from fastapi import FastAPI, HTTPException, Response
from yuanfen import Logger

from .converter import Converter
from .svg_cache import SvgCache
from .utils import get_unicode_str_from_charcode

# Constants
FONTS_DIR = "data/fonts"
CACHE_DIR = "data/cache"
FONT_FILE = "LXGWWenKai-Regular.ttf"

unicode_list = []
svg_cache = SvgCache(10000)


logger = Logger()
app = FastAPI()


@app.get("/benchmark/baseline", summary="Benchmark of baseline")
def benchmark_base():
    return "Hello, World!"


@app.get("/benchmark/cache_off", summary="Benchmark of cache off")
def benchmark_cache_off():
    converter = Converter(FONTS_DIR, FONT_FILE)
    svg_content = converter.convert(random.choice(unicode_list))
    return Response(content=svg_content, media_type="image/svg+xml")


@app.get("/benchmark/cache_file", summary="Benchmark of file cache hit")
def benchmark_cache_file():
    unicode = random.choice(unicode_list)
    cache = get_cache(FONT_FILE, unicode)
    if os.path.exists(cache["svg_file_path"]):
        with open(cache["svg_file_path"], "r") as f:
            svg_content = f.read()
            return Response(content=svg_content, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="SVG file not found")


@app.get("/benchmark/cache_mem", summary="Benchmark of memory cache hit")
def benchmark_cache_mem():
    unicode = random.choice(unicode_list)
    cache = get_cache(FONT_FILE, unicode)
    if cache["svg_content"]:
        return Response(content=cache["svg_content"], media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="SVG content not found")


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


for i in range(0, 1000):
    unicode = get_unicode_str_from_charcode(random.randint(0x4E00, 0x9FFF))
    converter = Converter(FONTS_DIR, FONT_FILE)
    svg_content = converter.convert(unicode)
    save_cache_mem(FONT_FILE, unicode, svg_content)
    save_cache_file(FONT_FILE, unicode, svg_content)
    unicode_list.append(unicode)
    logger.info(f"Cache for {unicode} generated")
