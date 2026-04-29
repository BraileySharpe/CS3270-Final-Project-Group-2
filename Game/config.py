import chess

BOARD_SIZE = 8
SQUARE_SIZE = 92

LIGHT_COLOR = "#F7E7CE"
DARK_COLOR = "#B07D62"

HIGHLIGHT_COLOR = "#F6F669"
MOVE_DOT_COLOR = "#2E8B57"
LAST_MOVE_COLOR = "#BFD7EA"
CHECK_COLOR = "#FF8C8C"

APP_BG = "#E5E7EB"
PANEL_BG = "#F9FAFB"
PANEL_BORDER = "#D1D5DB"
TEXT_PRIMARY = "#111827"
TEXT_MUTED = "#6B7280"
BUTTON_PRIMARY = "#2563EB"
BUTTON_SECONDARY = "#374151"

SELECTED_BLUE = "#375A7F"

UNSELECTED_BG = "#E5E7EB"
UNSELECTED_TEXT = "#111827"

HOVER_BG = "#D1D5DB"

SIDEBAR_WIDTH = 330
WINDOW_PADDING = 8

FONT_LARGE = ("Segoe UI", 20, "bold")
FONT_MEDIUM = ("Segoe UI", 11)
FONT_SMALL = ("Consolas", 10)
FONT_PIECE = ("Segoe UI Symbol", 45)

UNICODE_PIECES = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}

PIECE_NAMES = {
    chess.PAWN: "Pawn",
    chess.KNIGHT: "Knight",
    chess.BISHOP: "Bishop",
    chess.ROOK: "Rook",
    chess.QUEEN: "Queen",
    chess.KING: "King",
}

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}