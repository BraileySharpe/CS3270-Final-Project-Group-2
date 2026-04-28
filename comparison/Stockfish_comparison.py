import random

import chess
import chess.engine
import pandas as pd
import torch
import matplotlib.pyplot as plt

from Game.move_provider import ModelMoveProvider
from evaluation_model.mini_max_searcher import mini_max_searcher
from evaluation_model.negamax_searcher import negamax_searcher
from evaluation_model.model_training_tanh import CNN_Model_tanh
from evaluation_model.model_training import CNN_Model


class StockfishEvaluator:
    def __init__(self, engine_path, depth=10):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.depth = depth

    def evaluate_cp(self, board: chess.Board) -> int:
        info = self.engine.analyse(
            board,
            chess.engine.Limit(depth=self.depth)
        )

        score = info["score"].white()

        if score.is_mate():
            mate = score.mate()
            return 100000 if mate > 0 else -100000

        return score.score()

    def best_move(self, board: chess.Board) -> chess.Move:
        result = self.engine.play(
            board,
            chess.engine.Limit(depth=self.depth)
        )
        return result.move

    def close(self):
        self.engine.quit()

class ProviderStockfishComparer:
    def __init__(self, provider, stockfish: StockfishEvaluator):
        self.provider = provider
        self.stockfish = stockfish

    def compare_position(self, board: chess.Board):
        before_eval = self.stockfish.evaluate_cp(board)

        stockfish_move = self.stockfish.best_move(board)

        provider_move = self.provider.choose_move(board)

        if provider_move is None:
            return None

        if provider_move not in board.legal_moves:
            raise ValueError(f"Illegal move: {provider_move}")

        board_after_provider = board.copy()
        board_after_provider.push(provider_move)
        after_provider_eval = self.stockfish.evaluate_cp(board_after_provider)

        board_after_stockfish = board.copy()
        board_after_stockfish.push(stockfish_move)
        after_stockfish_eval = self.stockfish.evaluate_cp(board_after_stockfish)

        if board.turn == chess.WHITE:
            eval_loss = after_stockfish_eval - after_provider_eval
        else:
            eval_loss = after_provider_eval - after_stockfish_eval

        return {
            "fen": board.fen(),
            "turn": "white" if board.turn == chess.WHITE else "black",
            "provider_move": provider_move.uci(),
            "stockfish_move": stockfish_move.uci(),
            "before_eval_cp": before_eval,
            "after_provider_eval_cp": after_provider_eval,
            "after_stockfish_eval_cp": after_stockfish_eval,
            "eval_loss_cp": eval_loss,
            "matched_stockfish": provider_move == stockfish_move,
        }

    def compare_positions(self, positions):
        rows = []

        for board in positions:
            result = self.compare_position(board)
            if result is not None:
                rows.append(result)

        return pd.DataFrame(rows)


class RandomMoveProvider:
    def choose_move(self, board: chess.Board):
        moves = list(board.legal_moves)
        return random.choice(moves) if moves else None


class ModelVsDummyStockfishAnalyzer:
    def __init__(self, model_provider, dummy_provider, stockfish, model_side=chess.WHITE, max_plies=100):
        self.model_provider = model_provider
        self.dummy_provider = dummy_provider
        self.stockfish = stockfish
        self.model_side = model_side
        self.max_plies = max_plies

    def play_and_analyze(self):
        board = chess.Board()
        rows = []

        for ply in range(self.max_plies):
            if board.is_game_over():
                break

            is_model_turn = board.turn == self.model_side

            if is_model_turn:
                fen_before = board.fen()

                stockfish_before = self.stockfish.evaluate_cp(board)
                stockfish_best_move = self.stockfish.best_move(board)

                model_move = self.model_provider.choose_move(board)

                if model_move is None:
                    break

                if model_move not in board.legal_moves:
                    raise ValueError(f"Illegal model move: {model_move}")

                board_after_model = board.copy()
                board_after_model.push(model_move)
                stockfish_after_model = self.stockfish.evaluate_cp(board_after_model)

                board_after_stockfish = board.copy()
                board_after_stockfish.push(stockfish_best_move)
                stockfish_after_best = self.stockfish.evaluate_cp(board_after_stockfish)

                if board.turn == chess.WHITE:
                    eval_loss = stockfish_after_best - stockfish_after_model
                else:
                    eval_loss = stockfish_after_model - stockfish_after_best

                rows.append({
                    "ply": ply + 1,
                    "fen_before": fen_before,
                    "model_side": "white" if self.model_side == chess.WHITE else "black",
                    "model_move": model_move.uci(),
                    "stockfish_best_move": stockfish_best_move.uci(),
                    "stockfish_before_cp": stockfish_before,
                    "stockfish_after_model_cp": stockfish_after_model,
                    "stockfish_after_best_cp": stockfish_after_best,
                    "eval_loss_cp": eval_loss,
                    "matched_stockfish": model_move == stockfish_best_move,
                })

                board.push(model_move)

            else:
                dummy_move = self.dummy_provider.choose_move(board)

                if dummy_move is None:
                    break

                if dummy_move not in board.legal_moves:
                    raise ValueError(f"Illegal dummy move: {dummy_move}")

                board.push(dummy_move)

        return pd.DataFrame(rows), board

    def plot_eval_loss(self, df):
        plt.figure(figsize=(10, 5))
        plt.plot(df["ply"], df["eval_loss_cp"])
        plt.title("Model Eval Loss vs Stockfish During Game")
        plt.xlabel("Ply")
        plt.ylabel("Eval Loss in Centipawns")
        plt.show()

import os 
import sys
## change this path to reflect your stockfish download
pathToStockfish = "../../stockfish/stockfish-windows-x86-64-avx2.exe"
abs_path = os.path.abspath(pathToStockfish)


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ##tanh variant of the model
    tanh_model = CNN_Model_tanh().to(device)
    tanh_model.load_state_dict(torch.load("evaluation_cnn_model_tanh.pth", map_location=device))
    tanh_model.eval()
    
    ##non tanh variant of the model
    model = CNN_Model().to(device)
    model.load_state_dict(torch.load("evaluation_cnn_model.pth", map_location=device))
    model.eval()
    
    stockfish = StockfishEvaluator(
        engine_path=abs_path, 
        depth=3
    )

    try:
        model_provider = ModelMoveProvider(
            ##change the search type here to minimax/negamax
            searcher=negamax_searcher,
            model=tanh_model,
            depth=3,
            max_moves=10
        )

        dummy_provider = ModelMoveProvider(
            searcher=mini_max_searcher,
            model=tanh_model,
            depth=3,
            max_moves=10
        )

        analyzer = ModelVsDummyStockfishAnalyzer(
            model_provider=model_provider,
            dummy_provider=dummy_provider,
            stockfish=stockfish,
            model_side=chess.WHITE,
            max_plies=300
        )

        df, final_board = analyzer.play_and_analyze()

        print(df)
        print("Final board:")
        print(final_board)
        print("Final result:", final_board.result())

        if not df.empty:
            eval_losses = df["eval_loss_cp"].abs()

            print("Mean:", eval_losses.mean())
            print("Median:", eval_losses.median())
            print("Trimmed mean:", eval_losses[eval_losses <= eval_losses.quantile(0.95)].mean())
            print("90th percentile:", eval_losses.quantile(0.90))
            print("95th percentile:", eval_losses.quantile(0.95))
            print("Max:", eval_losses.max())
            print("Blunder rate >300cp:", (eval_losses > 300).mean())

            analyzer.plot_eval_loss(df)

    finally:
        stockfish.close()