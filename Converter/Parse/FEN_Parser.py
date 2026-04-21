from typing import List
import chess
import numpy as np
import pandas as pd
from chess import PIECE_TYPES

from Converter.DataAccess.DatasetReader import get_dataset


class FEN_Parser:


    def generate_matrices(self, fen_row: str) -> np.ndarray:
        """
        Generates the chess board tensor where each matrix contains one piece types location
        Current format:
        0 - White Pawns
        1 - White Knights
        2 - White Bishop
        3-  White Rook
        4 - White Queen
        5 - White King
        6 - Black Pawns
        7 - Black Knights
        8 - Black Bishops
        9 - Black Rooks
        10 - Black Queens
        11 - Black Kings
        :param fen_row: the fen notation for the board to generate
        :return: the 12x8x8 chess tensor
        """
        board = chess.Board(fen_row)
        tensor = np.zeros((12, 8, 8), dtype=np.float32)
        for square, piece in board.piece_map().items():
            row = 7 - (square // 8)
            col = square % 8

            color_offset = 0 if piece.color == chess.WHITE else 6 #white stored in planes 0-5, black 6-11

            plane_index = color_offset + (piece.piece_type - 1) #selects the plane based on color and type
            tensor[plane_index, row, col] = 1

        return tensor

if __name__ == "__main__":
    pd_data = get_dataset(100)
    parser = FEN_Parser()
    print(parser.generate_matrices(pd_data["FEN"][0]))
