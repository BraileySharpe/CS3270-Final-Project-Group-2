import numpy as np
import chess
from Converter.DataAccess.DatasetReader import get_dataset
from Converter.Parse.FEN_Parser import FEN_Parser


def convert_to_FEN(tensor: np.ndarray) -> chess.Board:
    board = chess.Board(None)
    for i in range(12):
        matrix = tensor[i]
        color = chess.WHITE if i < 6 else chess.BLACK
        piece_type = (i % 6) + 1

        add_piece_board(piece_type, color, board, matrix)

    return board

def add_piece_board(piece_type, piece_color, board_to_add_on, matrix):
    piece = chess.Piece(piece_type, piece_color)
    for row in range(8):
        for col in range(8):
            if matrix[row][col] == 1:
                square = chess.square(col, 7 - row)
                board_to_add_on.set_piece_at(square, piece)
if __name__ == "__main__":
    pd_data = get_dataset(12)
    print(pd_data)
    parser = FEN_Parser()
    tensor = parser.generate_matrices(pd_data["FEN"][0])
    board_temp = chess.Board(pd_data["FEN"][0])


    convert_to_FEN(tensor)