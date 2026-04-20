import chess
from config import PIECE_NAMES

def format_move_entry(board_before: chess.Board, move: chess.Move) -> str:
    """
    Build a readable move description using the position BEFORE the move.
    Example:
        White Pawn: e2 -> e4
        Black Knight: g8 -> f6
    """
    piece = board_before.piece_at(move.from_square)
    if piece is None:
        return board_before.san(move)

    color_name = "White" if piece.color == chess.WHITE else "Black"
    piece_name = PIECE_NAMES[piece.piece_type]
    from_sq = chess.square_name(move.from_square)
    to_sq = chess.square_name(move.to_square)
    san = board_before.san(move)

    promotion_text = ""
    if move.promotion:
        promotion_piece = PIECE_NAMES[move.promotion]
        promotion_text = f", promotes to {promotion_piece}"

    capture_text = ""
    if board_before.is_capture(move):
        capture_text = ", capture"

    return (
        f"{color_name} {piece_name}: {from_sq} -> {to_sq}"
        f"{capture_text}{promotion_text}"
    )


def rebuild_history_from_board(board: chess.Board) -> list[str]:
    """
    Rebuild readable move history from the current board move stack.
    Returns one line per half-move.
    """
    temp_board = chess.Board()
    lines = []

    for index, move in enumerate(board.move_stack, start=1):
        entry = format_move_entry(temp_board, move)
        move_no = (index + 1) // 2
        prefix = f"{move_no}." if temp_board.turn == chess.WHITE else f"{move_no}..."
        lines.append(f"{prefix} {entry}")
        temp_board.push(move)

    return lines