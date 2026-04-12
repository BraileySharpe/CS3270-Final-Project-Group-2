from typing import Optional, Protocol
import chess


class MoveProvider(Protocol):
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Return a legal move for the current board state, or None."""

class RandomMoveProvider:
    """
    Temporary opponent implementation.
    Replace later with a model-backed provider.
    """
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        return legal_moves[0]


class ModelMoveProvider:
    """
    Future CNN-based move provider placeholder.
    """
    def __init__(self, model=None):
        self.model = model

    def board_to_features(self, board: chess.Board):
        raise NotImplementedError("Implement feature extraction for your CNN here.")

    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        raise NotImplementedError("Implement model inference and move selection here.")