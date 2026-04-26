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
    EXACT = "EXACT"
    LOWERBOUND = "LOWERBOUND"
    UPPERBOUND = "UPPERBOUND"

    def __init__(self, model, parser: FEN_Parser, device, depth=3, max_moves=12):
        self.model = model
        self.parser = parser
        self.device = device
        self.depth = depth
        self.max_moves = max_moves

        self.eval_cache = {}
        self.transposition_table = {}

        self.model.eval()

    def board_key(self, board: chess.Board) -> str:
        return " ".join(board.fen().split(" ")[:4])

    def material_eval(self, board: chess.Board) -> float:
        score = 0.0

        for piece in board.piece_map().values():
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value

        return score / 10.0

    def evaluate_board(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -9999 if board.turn == chess.WHITE else 9999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        key = self.board_key(board)

        if key in self.eval_cache:
            model_score = self.eval_cache[key]
        else:
            nparr = self.parser.generate_matrices(board.fen())
            tensor = torch.from_numpy(nparr).float().unsqueeze(0).to(self.device)

            with torch.no_grad():
                model_score = self.model(tensor).item()

            self.eval_cache[key] = model_score

        material_score = self.material_eval(board)

        return model_score + material_score

    def move_order_score(self, board: chess.Board, move: chess.Move, tt_move: Optional[chess.Move] = None) -> float:
        if tt_move is not None and move == tt_move:
            return 1_000_000

        score = 0.0

        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)

            if victim is None and board.is_en_passant(move):
                victim_value = PIECE_VALUES[chess.PAWN]
            elif victim is not None:
                victim_value = PIECE_VALUES[victim.piece_type]
            else:
                victim_value = 0.0

            attacker_value = PIECE_VALUES[attacker.piece_type] if attacker else 0.0

            score += 10 * victim_value - attacker_value

        if move.promotion:
            score += PIECE_VALUES.get(move.promotion, 0.0) + 8.0

        board.push(move)
        if board.is_check():
            score += 2.0
        board.pop()

        return score

    def ordered_moves(self, board: chess.Board, tt_move: Optional[chess.Move] = None):
        moves = list(board.legal_moves)

        moves.sort(
            key=lambda move: self.move_order_score(board, move, tt_move),
            reverse=True
        )

        if self.max_moves is not None:
            return moves[:self.max_moves]

        return moves

    def tactical_moves(self, board: chess.Board):
        moves = []

        for move in board.legal_moves:
            if board.is_capture(move) or move.promotion:
                moves.append(move)

        moves.sort(
            key=lambda move: self.move_order_score(board, move),
            reverse=True
        )

        return moves

    def quiescence(self, board: chess.Board, alpha: float, beta: float) -> float:
        color = 1 if board.turn == chess.WHITE else -1
        stand_pat = color * self.evaluate_board(board)

        if stand_pat >= beta:
            return beta

        alpha = max(alpha, stand_pat)

        for move in self.tactical_moves(board):
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta

            alpha = max(alpha, score)

        return alpha

    def negamax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        alpha_original = alpha
        key = self.board_key(board)

        tt_entry = self.transposition_table.get(key)
        tt_move = None

        if tt_entry is not None:
            stored_depth, stored_score, stored_flag, stored_move = tt_entry
            tt_move = stored_move

            if stored_depth >= depth:
                if stored_flag == self.EXACT:
                    return stored_score
                elif stored_flag == self.LOWERBOUND:
                    alpha = max(alpha, stored_score)
                elif stored_flag == self.UPPERBOUND:
                    beta = min(beta, stored_score)

                if alpha >= beta:
                    return stored_score

        if depth == 0:
            return self.quiescence(board, alpha, beta)

        if board.is_game_over():
            color = 1 if board.turn == chess.WHITE else -1
            return color * self.evaluate_board(board)

        best_score = -float("inf")
        best_move = None

        for move in self.ordered_moves(board, tt_move):
            board.push(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        if best_score <= alpha_original:
            flag = self.UPPERBOUND
        elif best_score >= beta:
            flag = self.LOWERBOUND
        else:
            flag = self.EXACT

        self.transposition_table[key] = (depth, best_score, flag, best_move)

        return best_score

    def find_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        best_move = legal_moves[0]

        for current_depth in range(1, self.depth + 1):
            best_score = -float("inf")

            key = self.board_key(board)
            tt_entry = self.transposition_table.get(key)
            tt_move = tt_entry[3] if tt_entry is not None else None

            for move in self.ordered_moves(board, tt_move):
                board.push(move)
                score = -self.negamax(
                    board,
                    current_depth - 1,
                    -float("inf"),
                    float("inf")
                )
                board.pop()

                if score > best_score:
                    best_score = score
                    best_move = move

            self.transposition_table[key] = (
                current_depth,
                best_score,
                self.EXACT,
                best_move
            )

        return best_move
