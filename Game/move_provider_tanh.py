from typing import Optional, Protocol
import chess
import torch

from evaluation_model.mini_max_searcher import mini_max_searcher
from evaluation_model.model_training import CNN_Model
from Converter.Parse.FEN_Parser import FEN_Parser

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN_Model().to(device)
model.load_state_dict(torch.load("evaluation_cnn_model.pth", map_location=device))
model.eval()


class MoveProvider(Protocol):
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Return a legal move for the current board state, or None."""

class ModelMoveProvider:
    def __init__(self, model=None):
        """
        Instanties the move provider with the model and a field to hold the neighboring states in FEN notation
        initialized by calling board_to_neighboring_states()
        """
        self.model = model
        self.neighboring_states_FEN = None

    def board_to_neighboring_states(self, board: chess.Board):
        """
        Takes a chess board and makes a mock board of all neighboring chess positions stored as FEN notation
        """
        currentStateFEN = board.fen()
        mockBoard = chess.Board(currentStateFEN)

        neighboring_states_FEN = []

        legal_moves = list(board.legal_moves)
        for legal_move in legal_moves:
            mockBoard.push(legal_move)
            neighboring_states_FEN.append((legal_move, mockBoard.fen()))
            mockBoard.pop()

        self.neighboring_states_FEN = neighboring_states_FEN

    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Evaluates all legal moves using the value head of the model,
        converts the scores into a softmax probability distribution,
        and selects the move with the highest probability.
        """
        self.board_to_neighboring_states(board)
        FEN_parser = FEN_Parser()

        scores = []
        moves = []
        for legal_move, FEN_state in self.neighboring_states_FEN:
            numpy_arr = FEN_parser.generate_matrices(FEN_state)
            tensor = torch.from_numpy(numpy_arr).to(device).unsqueeze(0)

            with torch.no_grad():
                state_evaluation = self.model(tensor)
                score = state_evaluation.item()

            scores.append(score)
            moves.append(legal_move)

        score_tensor = torch.tensor(scores, dtype=torch.float32)

        temperature = 1.0
        probabilities = torch.softmax(score_tensor / temperature, dim=0)

        best_index = torch.argmax(probabilities).item()
        best_move = moves[best_index]

        self.neighboring_states_FEN = None
        return best_move


class ModelMinimaxProvider:
    def __init__(self, model, searcher, depth=3, max_moves=12):
        self.model = model
        self.parser = FEN_Parser()
        self.device = device

        self.searcher = searcher(
            model=self.model,
            parser=self.parser,
            device=self.device,
            depth=depth,
            max_moves=max_moves
        )

    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        return self.searcher.find_best_move(board)


model_moveProvider = ModelMinimaxProvider(model=model, depth=3, max_moves=10)

if __name__ == "__main__":
    mockBoard = chess.Board()
    print(model_moveProvider.choose_move(mockBoard))
