# References:
# - https://www.freetype.org/freetype2/docs/reference/ft2-outline_processing.html#ft_outline_decompose
# - https://gist.github.com/GaryLee/04dd0537fc501724b0f3af329864bcf1

import json
import os
from tempfile import gettempdir
from xml.dom import minidom

from freetype import Face
from svgpathtools import CubicBezier, Line, Path, QuadraticBezier, disvg, parse_path
from yuanfen import Version, time

from .. import __version__
from ..utils import get_charcode_from_unicode_str


class Converter:
    version = Version.parse(__version__)

    def __init__(self, fonts_dir: str, font_file: str, color: str = "#000000"):
        self.face = Face(f"{fonts_dir}/{font_file}")
        self.font_file = font_file
        self.color = color
        self._reset()

    def _reset(self):
        self._svg_paths = []
        self._lastX = 0
        self._lastY = 0

    def _last_xy_to_complex(self):
        return self._tuple_to_complex((self._lastX, self._lastY))

    def _tuple_to_complex(self, xy):
        return xy[0] + xy[1] * 1j

    def _vector_to_complex(self, v):
        return v.x + v.y * 1j

    def _vectors_to_points(self, vectors):
        return [(v.x, v.y) for v in vectors if v is not None]

    def _callback_move_to(self, *args):
        self._lastX, self._lastY = args[0].x, args[0].y

    def _callback_line_to(self, *args):
        line = Line(
            self._last_xy_to_complex(),
            self._vector_to_complex(args[0]),
        )
        self._svg_paths.append(line)
        self._lastX, self._lastY = args[0].x, args[0].y

    def _callback_conic_to(self, *args):
        curve = QuadraticBezier(
            self._last_xy_to_complex(),
            self._vector_to_complex(args[0]),
            self._vector_to_complex(args[1]),
        )
        self._svg_paths.append(curve)
        self._lastX, self._lastY = args[1].x, args[1].y

    def _callback_cubic_to(self, *args):
        curve = CubicBezier(
            self._last_xy_to_complex(),
            self._vector_to_complex(args[0]),
            self._vector_to_complex(args[1]),
            self._vector_to_complex(args[2]),
        )
        self._svg_paths.append(curve)
        self._lastX, self._lastY = args[2].x, args[2].y

    def _calc_view_box(self, metrics):
        view_box_min_x = 0
        view_box_min_y = -self.face.ascender
        view_box_width = metrics.horiAdvance
        view_box_height = self.face.ascender - self.face.descender
        return f"{view_box_min_x} {view_box_min_y} {view_box_width} {view_box_height}"

    def convert(self, unicode: str):
        self._reset()
        self.face.load_char(get_charcode_from_unicode_str(unicode))
        outline = self.face.glyph.outline
        metrics = self.face.glyph.metrics
        outline.decompose(
            context=None,
            move_to=self._callback_move_to,
            line_to=self._callback_line_to,
            conic_to=self._callback_conic_to,
            cubic_to=self._callback_cubic_to,
        )
        path = (
            Path(*self._svg_paths).scaled(1, -1)
            if len(self._svg_paths) > 0
            else parse_path(f"M 0,{-self.face.ascender} L {metrics.horiAdvance},{-self.face.ascender} L {metrics.horiAdvance},{-self.face.descender} L 0,{-self.face.descender} Z")
        )

        desc = {
            "creator": "font2svg",
            "version": str(self.version),
            "font_file": self.font_file,
            "unicode": unicode,
            "baseline": -self.face.descender,
            "underline": self.face.underline_position - self.face.descender,
            "underlineThickness": self.face.underline_thickness,
            "width": metrics.horiAdvance,
            "height": self.face.ascender - self.face.descender,
        }
        attr = {
            "desc": json.dumps(desc),
            "width": f"{metrics.horiAdvance}px",
            "height": f"{self.face.ascender - self.face.descender}px",
            "viewBox": self._calc_view_box(metrics),
            "preserveAspectRatio": "xMidYMid meet",
        }
        temp_filename = os.path.join(gettempdir(), f"font2svg_temp_{time.current_timestamp()}.svg")
        drawing = disvg(
            paths=path,
            attributes=[{"fill": self.color, "fill-opacity": None if len(self._svg_paths) > 0 else 0}],
            svg_attributes=attr,
            paths2Drawing=True,
            filename=temp_filename,
        )
        drawing.save()
        return minidom.parse(temp_filename).toprettyxml()
