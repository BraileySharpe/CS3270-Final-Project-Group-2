from typing import List
import chess
import numpy as np
import pandas as pd
from chess import PIECE_TYPES

from Converter.DataAccess.DatasetReader import get_dataset


class FEN_Parser:

    def generate_matrices(self, fen_row: str) -> np.ndarray:
        board = chess.Board(fen_row)

        #original 12 piece plan
        tensor = np.zeros((12, 8, 8), dtype=np.float32)

        for square, piece in board.piece_map().items():
            row = 7 - (square // 8)
            col = square % 8

            color_offset = 0 if piece.color == chess.WHITE else 6
            plane_index = color_offset + (piece.piece_type - 1)

            tensor[plane_index, row, col] = 1.0

        ## plane for which side it is to move 
        stm_plane = np.full((8, 8), 1.0 if board.turn == chess.WHITE else 0.0, dtype=np.float32)

        ## who has castling rights
        wk = np.full((8, 8), 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0, dtype=np.float32)
        wq = np.full((8, 8), 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0, dtype=np.float32)
        bk = np.full((8, 8), 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0, dtype=np.float32)
        bq = np.full((8, 8), 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0, dtype=np.float32)

        ## which squares are eligible for an en passant capture 
        ep_plane = np.zeros((8, 8), dtype=np.float32)
        if board.ep_square is not None:
            r = 7 - (board.ep_square // 8)
            c = board.ep_square % 8
            ep_plane[r][c] = 1.0

        
        ## half move clock which is normalized between [0,1]
        halfmove_plane = np.full((8, 8), min(board.halfmove_clock, 100) / 100.0, dtype=np.float32)

        ## stack all planes together
        final_planes = np.vstack([
            tensor,
            stm_plane[np.newaxis, :, :],
            wk[np.newaxis, :, :],
            wq[np.newaxis, :, :],
            bk[np.newaxis, :, :],
            bq[np.newaxis, :, :],
            ep_plane[np.newaxis, :, :],
            halfmove_plane[np.newaxis, :, :]
        ])

        return final_planes

if __name__ == "__main__":
    pd_data = get_dataset(100)
    parser = FEN_Parser()
    print(parser.generate_matrices(pd_data["FEN"][0]))
