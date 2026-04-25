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
    def __init__(self, model, parser: FEN_Parser, device, depth=2):
        self.model = model
        self.parser = parser
        self.device = device
        self.depth = depth

    def material_eval(self, board: chess.Board) -> float:
        score = 0.0

        for piece in board.piece_map().values():
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value

        return score / 10.0

    def evaluate_board(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -9999 if board.turn == chess.WHITE else 9999

        if board.is_stalemate():
            return 0.0

        if board.is_insufficient_material():
            return 0.0

        nparr = self.parser.generate_matrices(board.fen())
        tensor = torch.from_numpy(nparr).float().unsqueeze(0).to(self.device)

        with torch.no_grad():
            model_score = self.model(tensor).item()

        material_score = self.material_eval(board)

        return model_score + 0.5 * material_score

    def ordered_moves(self, board: chess.Board):
        moves = list(board.legal_moves)

        def move_score(move):
            score = 0

            if board.is_capture(move):
                score += 10

            board.push(move)

            if board.is_checkmate():
                score += 10000
            elif board.is_check():
                score += 50

            board.pop()

            return score

        return sorted(moves, key=move_score, reverse=True)

    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if board.turn == chess.WHITE:
            best_score = -float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                best_score = max(best_score, score)
                alpha = max(alpha, score)

                if beta <= alpha:
                    break

            return best_score

        else:
            best_score = float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                best_score = min(best_score, score)
                beta = min(beta, score)

                if beta <= alpha:
                    break

            return best_score

    def find_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        best_move = None

        if board.turn == chess.WHITE:
            best_score = -float("inf")

            for move in self.ordered_moves(board):
                board.push(move)
                score = self.minimax(
                    board,
                    self.depth - 1,
                    -float("inf"),
                    float("inf")
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
                    float("inf")
                )
                board.pop()

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move