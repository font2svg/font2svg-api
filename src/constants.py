import os

# Constants
FONTS_DIR = "data/fonts"
CACHE_DIR = "data/cache"

# Environment variables
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
CACHE__ENABLED = os.getenv("CACHE__ENABLED", "true").lower() == "true"
CACHE__PERSISTENT = os.getenv("CACHE__PERSISTENT", "true").lower() == "true"
CACHE__MEM_CHARS_LIMIT = int(os.getenv("CACHE__MEM_CHARS_LIMIT", "10000"))

# references:
# https://learn.microsoft.com/zh-cn/typography/opentype/spec/name
# https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html
FONT_NAME_IDS = {
    "COPYRIGHT_NOTICE": 0,
    "FAMILY_NAME": 1,
    "SUBFAMILY_NAME": 2,
    "UNIQUE_IDENTIFIER": 3,
    "FULL_NAME": 4,
    "VERSION_STRING": 5,
    "POST_SCRIPT_NAME": 6,
    "TRADEMARK": 7,
    "MANUFACTURER_NAME": 8,
    "DESIGNER_NAME": 9,
    "DESCRIPTION": 10,
    "VENDOR_URL": 11,
    "DESIGNER_URL": 12,
    "LICENSE_DESCRIPTION": 13,
    "LICENSE_INFO_URL": 14,
    "RESERVED": 15,
    "TYPOGRAPHIC_FAMILY_NAME": 16,
    "TYPOGRAPHIC_SUBFAMILY_NAME": 17,
    "COMPATIBLE_FULL_NAME": 18,
    "SAMPLE_TEXT": 19,
    "POST_SCRIPT_CID_NAME": 20,
    "WWS_FAMILY_NAME": 21,
    "WWS_SUBFAMILY_NAME": 22,
    "LIGHT_BACKGROUND_PALETTE": 23,
    "DARK_BACKGROUND_PALETTE": 24,
    "VARIATIONS_POST_SCRIPT_PREFIX": 25,
}
