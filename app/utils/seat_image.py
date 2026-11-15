"""A studio seat map as a PNG, drawn in pure Python for the MCP tools: free, taken and chosen seats."""

import struct
import zlib
from dataclasses import dataclass

from app.utils.seat_layout import AISLE_AFTER_SEAT, WALKWAY_BEFORE_ROW, seat_rows

# 5x7 pixel glyphs for crisp, dependency-free labels inside the PNG canvas
_FONT_5X7: dict[str, tuple[str, ...]] = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "10000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
}

Color = tuple[int, int, int]
_BG: Color = (250, 249, 246)
_INK: Color = (24, 24, 27)
_MUTED: Color = (100, 116, 139)
_SCREEN_FILL: Color = (203, 213, 225)
_FREE_FILL: Color = (255, 255, 255)
_FREE_BORDER: Color = (148, 163, 184)
_TAKEN_FILL: Color = (203, 213, 225)
_TAKEN_BORDER: Color = (148, 163, 184)
_TAKEN_INK: Color = (100, 116, 139)
_CHOSEN_FILL: Color = (15, 118, 110)
_CHOSEN_BORDER: Color = (13, 148, 136)
_WHITE: Color = (255, 255, 255)

_PAD_X = 24
_PAD_Y = 18
_HEADER_H = 40
_SCREEN_H = 24
_SEAT_W = 30
_SEAT_H = 24
_SEAT_GAP = 4
_AISLE_W = 20
_ROW_GAP = 5
_WALKWAY_H = 20
_LABEL_W = 22
_FOOTER_H = 28


@dataclass(frozen=True)
class _SeatBox:
    seat_id: str
    row: str
    x: int
    y: int
    state: str


@dataclass(frozen=True)
class _RowLabelPos:
    row: str
    y: int
    has_walkway_above: bool


@dataclass(frozen=True)
class _Layout:
    width: int
    height: int
    screen_x: int
    screen_y: int
    screen_w: int
    walkway_y: int | None
    seats: list[_SeatBox]
    rows: list[_RowLabelPos]
    footer_y: int


def _build_layout(taken_seat_ids: set[str], chosen_seat_ids: set[str] | None) -> _Layout:
    chosen = chosen_seat_ids or set()
    rows_data = seat_rows()
    seats_per_row = len(rows_data[0][1]) if rows_data else 18
    room_w = seats_per_row * _SEAT_W + (seats_per_row - 1) * _SEAT_GAP + _AISLE_W
    width = _PAD_X * 2 + _LABEL_W * 2 + room_w
    left_x = _PAD_X + _LABEL_W
    screen_y = _PAD_Y + _HEADER_H
    y = screen_y + _SCREEN_H + 14

    boxes: list[_SeatBox] = []
    row_positions: list[_RowLabelPos] = []
    walkway_y: int | None = None

    for row_letter, seat_ids in rows_data:
        has_walkway = row_letter == WALKWAY_BEFORE_ROW
        if has_walkway:
            walkway_y = y + (_WALKWAY_H - 7) // 2
            y += _WALKWAY_H
        row_positions.append(_RowLabelPos(row=row_letter, y=y, has_walkway_above=has_walkway))
        x = left_x
        for index, seat_id in enumerate(seat_ids, start=1):
            state = "chosen" if seat_id in chosen else "taken" if seat_id in taken_seat_ids else "free"
            boxes.append(_SeatBox(seat_id=seat_id, row=row_letter, x=x, y=y, state=state))
            x += _SEAT_W + _SEAT_GAP
            if index == AISLE_AFTER_SEAT:
                x += _AISLE_W
        y += _SEAT_H + _ROW_GAP

    footer_y = y + 8
    height = footer_y + _FOOTER_H + _PAD_Y
    return _Layout(
        width=width,
        height=height,
        screen_x=left_x + int(room_w * 0.12),
        screen_y=screen_y,
        screen_w=int(room_w * 0.76),
        walkway_y=walkway_y,
        seats=boxes,
        rows=row_positions,
        footer_y=footer_y,
    )


class _Canvas:
    def __init__(self, width: int, height: int, bg: Color) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray(bg) * (width * height)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: Color) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + w), min(self.height, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        row_bytes = bytes(color) * (x1 - x0)
        stride = self.width * 3
        span = (x1 - x0) * 3
        for py in range(y0, y1):
            start = py * stride + x0 * 3
            self.pixels[start : start + span] = row_bytes

    def stroke_rect(self, x: int, y: int, w: int, h: int, fill: Color, border: Color) -> None:
        self.fill_rect(x, y, w, h, border)
        if w > 2 and h > 2:
            self.fill_rect(x + 1, y + 1, w - 2, h - 2, fill)

    def draw_text(self, x: int, y: int, text: str, color: Color, scale: int = 1) -> None:
        cursor = x
        step = 6 * scale
        for ch in text.upper():
            glyph = _FONT_5X7.get(ch)
            if glyph is None:
                cursor += step
                continue
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cursor + gx * scale, y + gy * scale, scale, scale, color)
            cursor += step

    def text_width(self, text: str, scale: int = 1) -> int:
        if not text:
            return 0
        return len(text) * 6 * scale - scale

    def encode_png(self) -> bytes:
        stride = self.width * 3
        raw = bytearray()
        for py in range(self.height):
            raw.append(0)
            start = py * stride
            raw.extend(self.pixels[start : start + stride])
        ihdr = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=6)
        return b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                _png_chunk(b"IHDR", ihdr),
                _png_chunk(b"IDAT", idat),
                _png_chunk(b"IEND", b""),
            ]
        )


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def _colors_for_state(state: str) -> tuple[Color, Color, Color]:
    if state == "chosen":
        return (_CHOSEN_FILL, _CHOSEN_BORDER, _WHITE)
    if state == "taken":
        return (_TAKEN_FILL, _TAKEN_BORDER, _TAKEN_INK)
    return (_FREE_FILL, _FREE_BORDER, _INK)


def render_seat_map_png(
    taken_seat_ids: set[str],
    chosen_seat_ids: set[str] | None = None,
    *,
    title: str,
    subtitle: str,
    as_of: str,
) -> bytes:
    """Render the cinema seat map as an RGB PNG image with Free, Taken, and Chosen seats."""
    layout = _build_layout(taken_seat_ids, chosen_seat_ids)
    canvas = _Canvas(layout.width, layout.height, _BG)

    canvas.draw_text(_PAD_X, _PAD_Y, title[:48], _INK, scale=2)
    if subtitle:
        canvas.draw_text(_PAD_X, _PAD_Y + 20, subtitle[:80], _MUTED, scale=1)

    canvas.fill_rect(layout.screen_x, layout.screen_y, layout.screen_w, 6, _SCREEN_FILL)
    screen_label = "SCREEN (FRONT)"
    canvas.draw_text(
        layout.screen_x + (layout.screen_w - canvas.text_width(screen_label)) // 2,
        layout.screen_y + 10,
        screen_label,
        _MUTED,
        scale=1,
    )

    if layout.walkway_y is not None:
        walkway_text = "WALKWAY"
        canvas.draw_text(
            (layout.width - canvas.text_width(walkway_text)) // 2,
            layout.walkway_y,
            walkway_text,
            _MUTED,
            scale=1,
        )

    for row_pos in layout.rows:
        ly = row_pos.y + (_SEAT_H - 7) // 2
        canvas.draw_text(_PAD_X + 6, ly, row_pos.row, _MUTED, scale=1)
        canvas.draw_text(layout.width - _PAD_X - 12, ly, row_pos.row, _MUTED, scale=1)

    for seat in layout.seats:
        fill, border, text_color = _colors_for_state(seat.state)
        canvas.stroke_rect(seat.x, seat.y, _SEAT_W, _SEAT_H, fill, border)
        label = "--" if seat.state == "taken" else seat.seat_id
        tw = canvas.text_width(label)
        canvas.draw_text(seat.x + (_SEAT_W - tw) // 2, seat.y + (_SEAT_H - 7) // 2, label, text_color, scale=1)

    lx = _PAD_X
    legend_items: list[tuple[str, str]] = [("FREE", "free"), ("TAKEN", "taken")]
    if chosen_seat_ids:
        legend_items.append(("CHOSEN", "chosen"))
    for label, state in legend_items:
        fill, border, _ = _colors_for_state(state)
        canvas.stroke_rect(lx, layout.footer_y + 2, 14, 14, fill, border)
        canvas.draw_text(lx + 20, layout.footer_y + 6, label, _MUTED, scale=1)
        lx += 34 + canvas.text_width(label)
    # Seats change, so the picture says when it was drawn
    stamp = f"SEATS AS OF {as_of}"
    canvas.draw_text(layout.width - _PAD_X - canvas.text_width(stamp), layout.footer_y + 6, stamp, _MUTED, scale=1)

    return canvas.encode_png()
