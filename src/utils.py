import json
import os

from fontTools.ttLib import TTFont

# references:
# https://learn.microsoft.com/zh-cn/typography/opentype/spec/name
# https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html
name_id_dict = {
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


def get_font_id(font: TTFont):
    return font["name"].getDebugName(name_id_dict["POST_SCRIPT_NAME"]).replace(" ", "-")


def get_font_info(font: TTFont):
    font_info = {}
    for name_record in font["name"].names:
        for name_id_key in name_id_dict.keys():
            if name_record.nameID == name_id_dict[name_id_key]:
                if font_info.get(name_id_key.lower()) is None:
                    font_info[name_id_key.lower()] = []

                font_info[name_id_key.lower()].append(
                    {
                        "platformId": name_record.platformID,
                        "encodingId": name_record.platEncID,
                        "langId": name_record.langID,
                        "value": name_record.toStr(),
                    }
                )
    return font_info


def get_font_info_from_cache(font_file: str):
    cache_folder = f"data/cache/{font_file}"
    with open(f"{cache_folder}/font_info.json", "r") as f:
        return json.load(f)


def generate_font_info_cache(font: TTFont, font_file: str):
    font_info = get_font_info(font)

    cache_folder = f"data/cache/{font_file}"
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    with open(f"{cache_folder}/font_info.json", "w") as f:
        json.dump(font_info, f, indent=4, ensure_ascii=False)


def remove_font_svg_cache(font_file: str):
    svg_cache_folder = f"data/cache/{font_file}/svg"
    if os.path.exists(svg_cache_folder):
        for file in os.listdir(svg_cache_folder):
            os.remove(f"{svg_cache_folder}/{file}")


def get_charcode_from_unicode_str(unicode_str: str):
    return int(unicode_str, 16)


def get_charcode_from_char(char: str):
    return ord(char)


def get_unicode_str_from_char(char: str):
    return hex(ord(char))[2:].zfill(4).upper()


def get_unicode_str_from_charcode(charcode: int):
    return hex(charcode)[2:].zfill(4).upper()
