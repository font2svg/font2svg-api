import os
import random

from fastapi import FastAPI, HTTPException, Response
from yuanfen import Logger

from .models.cache import Cache
from .models.converter import Converter
from .utils import get_char_cache, get_unicode_str_from_charcode, save_char_cache

# Constants
FONTS_DIR = "data/fonts"
CACHE_DIR = "data/cache"
FONT_FILE = "LXGWWenKai-Regular.ttf"

unicode_list = []
cache = Cache(10000)


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
    char_cache = get_char_cache(FONT_FILE, unicode)
    if os.path.exists(char_cache["svg_file_path"]):
        with open(char_cache["svg_file_path"], "r") as f:
            svg_content = f.read()
            return Response(content=svg_content, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="SVG file not found")


@app.get("/benchmark/cache_mem", summary="Benchmark of memory cache hit")
def benchmark_cache_mem():
    unicode = random.choice(unicode_list)
    char_cache = get_char_cache(FONT_FILE, unicode)
    if char_cache["svg_content"]:
        return Response(content=char_cache["svg_content"], media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="SVG content not found")


for i in range(0, 1000):
    unicode = get_unicode_str_from_charcode(random.randint(0x4E00, 0x9FFF))
    converter = Converter(FONTS_DIR, FONT_FILE)
    svg_content = converter.convert(unicode)
    save_char_cache(FONT_FILE, unicode, svg_content)
    unicode_list.append(unicode)
    logger.info(f"Cache for {unicode} generated")
