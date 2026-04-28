from typing import Optional
import chess
import torch

from Converter.Parse.FEN_Parser import FEN_Parser


PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.2,
    chess.BISHOP: 3.3,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0,
}


class mini_max_searcher:
    def __init__(
        self,
        model,
        parser: FEN_Parser,
        device,
        depth=2,
        max_moves=12,
        use_model=True,
    ):
        self.model = model
        self.parser = parser
        self.device = device
        self.depth = depth
        self.max_moves = max_moves
        self.use_model = use_model

        self.model.eval()

        self.eval_cache = {}
        self.tt = {}

    def board_key(self, board: chess.Board):
        try:
            return board.transposition_key()
        except AttributeError:
            return board._transposition_key()

    def material_eval(self, board: chess.Board) -> float:
        score = 0.0

        for piece in board.piece_map().values():
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value

        return score / 10.0

    def evaluate_board(self, board: chess.Board) -> float:
        key = self.board_key(board)

        if key in self.eval_cache:
            return self.eval_cache[key]

        if board.is_checkmate():
            score = -9999 if board.turn == chess.WHITE else 9999

        elif board.is_stalemate() or board.is_insufficient_material():
            score = 0.0

        else:
            material_score = self.material_eval(board)

            if self.use_model:
                nparr = self.parser.generate_matrices(board.fen())
                tensor = torch.from_numpy(nparr).float().unsqueeze(0).to(self.device)

                with torch.inference_mode():
                    model_score = self.model(tensor).item()

                score = model_score + 0.5 * material_score
            else:
                score = material_score

        self.eval_cache[key] = score
        return score

    def ordered_moves(self, board: chess.Board):
        moves = list(board.legal_moves)

        def move_score(move):
            score = 0.0

            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)

                if victim is None and board.is_en_passant(move):
                    victim_value = PIECE_VALUES[chess.PAWN]
                elif victim is not None:
                    victim_value = PIECE_VALUES[victim.piece_type]
                else:
                    victim_value = 0.0

                attacker_value = (
                    PIECE_VALUES[attacker.piece_type]
                    if attacker is not None
                    else 0.0
                )

                score += 100.0 + 10.0 * victim_value - attacker_value

            if move.promotion:
                score += 900.0 + PIECE_VALUES.get(move.promotion, 0.0)


            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)

            if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
                score += 5.0

            return score

        moves = sorted(moves, key=move_score, reverse=True)


        return moves[: self.max_moves]

    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        key = (self.board_key(board), depth)

        if key in self.tt:
            return self.tt[key]

        if depth == 0 or board.is_game_over():
            score = self.evaluate_board(board)
            self.tt[key] = score
            return score

        if board.turn == chess.WHITE:
            best_score = -float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

        else:
            best_score = float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                best_score = min(best_score, score)
                beta = min(beta, best_score)

                if beta <= alpha:
                    break

        self.tt[key] = best_score
        return best_score

    def find_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        if not list(board.legal_moves):
            return None

        self.eval_cache.clear()
        self.tt.clear()

        best_move = None

        if board.turn == chess.WHITE:
            best_score = -float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(
                    board,
                    self.depth - 1,
                    -float("inf"),
                    float("inf"),
                )
                board.pop()

                if score > best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(
                    board,
                    self.depth - 1,
                    -float("inf"),
                    float("inf"),
                )
                board.pop()

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move