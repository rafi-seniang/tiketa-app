"""A studio seat map as a PNG for the MCP tools: free, taken and chosen seats, and when it was drawn."""

import io

from PIL import Image, ImageDraw, ImageFont

from app.utils.seat_layout import AISLE_AFTER_SEAT, WALKWAY_BEFORE_ROW, seat_rows

BACKGROUND = "#faf9f6"
INK = "#18181b"
MUTED = "#64748b"
LINE = "#94a3b8"
TAKEN = "#cbd5e1"
CHOSEN = "#0f766e"
# fill, outline, label colour of each seat state
SEAT_COLOURS = {"free": ("#ffffff", LINE, INK), "taken": (TAKEN, LINE, MUTED), "chosen": (CHOSEN, CHOSEN, "#ffffff")}

PAD = 24
SEAT_W, SEAT_H, GAP = 32, 24, 4
AISLE_W, WALKWAY_H, LABEL_W = 20, 22, 24
TOP = 106  # below the title, subtitle and screen


def render_seat_map_png(
    taken_seat_ids: set[str], chosen_seat_ids: set[str] | None = None, *, title: str, subtitle: str, as_of: str
) -> bytes:
    chosen = chosen_seat_ids or set()
    rows = seat_rows()
    seats_per_row = len(rows[0][1])
    room_w = seats_per_row * (SEAT_W + GAP) - GAP + AISLE_W
    width = 2 * (PAD + LABEL_W) + room_w
    height = TOP + len(rows) * (SEAT_H + GAP) + WALKWAY_H + 56
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font, text_font, seat_font = (ImageFont.load_default(size) for size in (20, 13, 11))

    draw.text((PAD, PAD), title, fill=INK, font=title_font)
    draw.text((PAD, PAD + 28), subtitle, fill=MUTED, font=text_font)
    left = PAD + LABEL_W
    draw.rounded_rectangle((left + room_w * 0.12, 78, left + room_w * 0.88, 84), radius=3, fill=TAKEN)
    draw.text((width / 2, 95), "SCREEN", fill=MUTED, font=seat_font, anchor="mm")

    y = TOP
    for row, seat_ids in rows:
        if row == WALKWAY_BEFORE_ROW:
            draw.text((width / 2, y + WALKWAY_H / 2), "WALKWAY", fill=MUTED, font=seat_font, anchor="mm")
            y += WALKWAY_H
        middle = y + SEAT_H / 2
        draw.text((PAD + LABEL_W / 2, middle), row, fill=MUTED, font=text_font, anchor="mm")
        draw.text((width - PAD - LABEL_W / 2, middle), row, fill=MUTED, font=text_font, anchor="mm")
        for number, seat_id in enumerate(seat_ids, start=1):
            x = left + (number - 1) * (SEAT_W + GAP) + (AISLE_W if number > AISLE_AFTER_SEAT else 0)
            state = "chosen" if seat_id in chosen else "taken" if seat_id in taken_seat_ids else "free"
            fill, outline, label = SEAT_COLOURS[state]
            draw.rounded_rectangle((x, y, x + SEAT_W, y + SEAT_H), radius=4, fill=fill, outline=outline)
            draw.text((x + SEAT_W / 2, middle), seat_id, fill=label, font=seat_font, anchor="mm")
        y += SEAT_H + GAP

    legend_y = y + 18
    x = PAD
    for state in ("free", "taken", "chosen") if chosen else ("free", "taken"):
        fill, outline, _ = SEAT_COLOURS[state]
        draw.rounded_rectangle((x, legend_y - 7, x + 14, legend_y + 7), radius=3, fill=fill, outline=outline)
        draw.text((x + 20, legend_y), state.capitalize(), fill=MUTED, font=text_font, anchor="lm")
        x += 90
    # Seats change, so the picture says when it was drawn
    draw.text((width - PAD, legend_y), f"Seats as of {as_of}", fill=MUTED, font=text_font, anchor="rm")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()
