"""The studio layout every showtime uses, as in Tiketa v1: rows A to M, an aisle after seat 9, row K a walkway."""

ROWS_FRONT_TO_BACK = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "L", "M")
SEATS_PER_ROW = 18
AISLE_AFTER_SEAT = 9
WALKWAY_BEFORE_ROW = "L"

ALL_SEAT_IDS = frozenset(f"{row}{number}" for row in ROWS_FRONT_TO_BACK for number in range(1, SEATS_PER_ROW + 1))
SEATS_PER_SHOWTIME = len(ALL_SEAT_IDS)

# What a model needs to know to place "in the middle", "by the aisle" or "next to each other" on the map
SEAT_MAP_LEGEND = (
    f"-- is a taken seat and | the only aisle, between seats {AISLE_AFTER_SEAT} and {AISLE_AFTER_SEAT + 1}. "
    f"Seats 1 and {SEATS_PER_ROW} are against the walls. Seats are next to each other when they share a row and have "
    "consecutive numbers on the same side of the aisle. The centre of the hall is rows E to H, seats 6 to 13."
)


def seat_rows() -> list[tuple[str, list[str]]]:
    """Each row with its seat ids from left to right, front row first."""
    return [(row, [f"{row}{number}" for number in range(1, SEATS_PER_ROW + 1)]) for row in ROWS_FRONT_TO_BACK]


def seat_map_text(taken_seat_ids: set[str]) -> str:
    """The seat map as a model reads it: one line per row, taken seats as --, the aisle as |."""

    def row_line(row: str, seat_ids: list[str]) -> str:
        shown = ["--" if seat_id in taken_seat_ids else seat_id for seat_id in seat_ids]
        line = f"{' '.join(shown[:AISLE_AFTER_SEAT])} | {' '.join(shown[AISLE_AFTER_SEAT:])}"
        return f"(walkway)\n{line}" if row == WALKWAY_BEFORE_ROW else line

    row_lines = [row_line(row, seat_ids) for row, seat_ids in seat_rows()]
    return "\n".join(["SCREEN (front)", *row_lines, "BACK"])
