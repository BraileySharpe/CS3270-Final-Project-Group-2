import chess

BOARD_SIZE = 8
SQUARE_SIZE = 80

LIGHT_COLOR = "#F7E7CE"
DARK_COLOR = "#B07D62"
HIGHLIGHT_COLOR = "#F6F669"
MOVE_DOT_COLOR = "#2E8B57"
LAST_MOVE_COLOR = "#BFD7EA"
CHECK_COLOR = "#FF8C8C"

SIDEBAR_WIDTH = 340
WINDOW_PADDING = 12

FONT_LARGE = ("Segoe UI", 20, "bold")
FONT_MEDIUM = ("Segoe UI", 12)
FONT_SMALL = ("Consolas", 10)
FONT_PIECE = ("Arial", 36)

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