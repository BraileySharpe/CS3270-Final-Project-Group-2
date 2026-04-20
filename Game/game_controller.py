from dataclasses import dataclass
from typing import Optional
import chess

from config import PIECE_VALUES
from move_history import format_move_entry, rebuild_history_from_board


@dataclass
class MoveResult:
    success: bool
    message: str
    history_entry: Optional[str] = None
    move: Optional[chess.Move] = None


class GameController:
    def __init__(self, initial_time_seconds: int = 600, use_timer: bool = True):
        self.initial_time_seconds = initial_time_seconds
        self.use_timer = use_timer

        self.board = chess.Board()
        self.last_move: Optional[chess.Move] = None
        self.game_over = False

        self.white_time = initial_time_seconds
        self.black_time = initial_time_seconds

    def reset(self) -> None:
        self.board.reset()
        self.last_move = None
        self.game_over = False
        self.white_time = self.initial_time_seconds
        self.black_time = self.initial_time_seconds

    def legal_targets_for(self, square: chess.Square) -> list[chess.Square]:
        return [move.to_square for move in self.board.legal_moves if move.from_square == square]

    def build_move(self, from_square: chess.Square, to_square: chess.Square) -> Optional[chess.Move]:
        piece = self.board.piece_at(from_square)
        if piece is None:
            return None

        if piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(to_square)
            if (piece.color == chess.WHITE and target_rank == 7) or (
                piece.color == chess.BLACK and target_rank == 0
            ):
                return chess.Move(from_square, to_square, promotion=chess.QUEEN)

        return chess.Move(from_square, to_square)

    def try_make_move(self, from_square: chess.Square, to_square: chess.Square) -> MoveResult:
        if self.game_over:
            return MoveResult(False, "The game is already over.")

        move = self.build_move(from_square, to_square)
        if move is None:
            return MoveResult(False, "No piece selected.")

        if move not in self.board.legal_moves:
            return MoveResult(False, "Illegal move.")

        history_entry = format_move_entry(self.board, move)
        self.board.push(move)
        self.last_move = move
        self._update_game_over()

        return MoveResult(
            success=True,
            message="Move played.",
            history_entry=history_entry,
            move=move,
        )

    def push_external_move(self, move: chess.Move) -> MoveResult:
        if self.game_over:
            return MoveResult(False, "The game is already over.")

        if move not in self.board.legal_moves:
            return MoveResult(False, "Opponent returned an illegal move.")

        history_entry = format_move_entry(self.board, move)
        self.board.push(move)
        self.last_move = move
        self._update_game_over()

        return MoveResult(
            success=True,
            message="Opponent move played.",
            history_entry=history_entry,
            move=move,
        )

    def undo(self, against_opponent: bool) -> bool:
        if not self.board.move_stack:
            return False

        if against_opponent and len(self.board.move_stack) >= 2:
            self.board.pop()
            self.board.pop()
        else:
            self.board.pop()

        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        self.game_over = False
        return True

    def tick(self) -> bool:
        """
        Decrease the current side's clock by 1 second.
        Returns True if a timeout caused the game to end.
        """
        if not self.use_timer or self.game_over:
            return False

        if self.board.turn == chess.WHITE:
            self.white_time = max(0, self.white_time - 1)
            if self.white_time == 0:
                self.game_over = True
                return True
        else:
            self.black_time = max(0, self.black_time - 1)
            if self.black_time == 0:
                self.game_over = True
                return True

        return False

    def get_material_score(self) -> tuple[int, int]:
        white_score = 0
        black_score = 0

        for piece in self.board.piece_map().values():
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                white_score += value
            else:
                black_score += value

        return white_score, black_score

    def get_material_advantage_text(self) -> str:
        white_score, black_score = self.get_material_score()
        diff = white_score - black_score

        if diff > 0:
            return f"White +{diff}"
        if diff < 0:
            return f"Black +{abs(diff)}"
        return "Equal"

    def get_white_score_text(self) -> str:
        white_score, _ = self.get_material_score()
        return f"White Material: {white_score}"

    def get_black_score_text(self) -> str:
        _, black_score = self.get_material_score()
        return f"Black Material: {black_score}"

    def get_timer_text(self, color: chess.Color) -> str:
        total = self.white_time if color == chess.WHITE else self.black_time
        minutes = total // 60
        seconds = total % 60
        return f"{minutes:02}:{seconds:02}"

    def status_text(self) -> str:
        if self.game_over:
            if self.use_timer and self.white_time == 0:
                return "White lost on time"
            if self.use_timer and self.black_time == 0:
                return "Black lost on time"
            if self.board.is_checkmate():
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                return f"Checkmate - {winner} wins"
            if self.board.is_stalemate():
                return "Stalemate"
            if self.board.is_insufficient_material():
                return "Draw by insufficient material"
            return "Game Over"

        return "White to move" if self.board.turn == chess.WHITE else "Black to move"

    def info_text(self) -> str:
        if self.use_timer and self.white_time == 0:
            return "White ran out of time."
        if self.use_timer and self.black_time == 0:
            return "Black ran out of time."
        if self.board.is_checkmate():
            return "The game has ended."
        if self.board.is_stalemate():
            return "The game has ended in a draw."
        if self.board.is_insufficient_material():
            return "The game has ended in a draw."
        if self.board.can_claim_threefold_repetition():
            return "Threefold repetition can be claimed."
        if self.board.is_check():
            player = "White" if self.board.turn == chess.WHITE else "Black"
            return f"{player} is in check."
        return "Make your move."

    def history_lines(self) -> list[str]:
        return rebuild_history_from_board(self.board)

    def _update_game_over(self) -> None:
        self.game_over = (
            self.board.is_checkmate()
            or self.board.is_stalemate()
            or self.board.is_insufficient_material()
            or (self.use_timer and (self.white_time == 0 or self.black_time == 0))
        )