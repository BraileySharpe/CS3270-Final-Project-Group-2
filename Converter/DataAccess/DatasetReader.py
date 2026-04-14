
import os

import kagglehub
import pandas as pd
# Download latest version
path = kagglehub.dataset_download("ronakbadhe/chess-evaluations")


def get_dataset(row_count: int = None) -> pd.DataFrame:
    chess_data = os.path.join(path, "chessData.csv")
    with open(chess_data) as csvfile:
        pd_data = pd.read_csv(csvfile, nrows=row_count)
        return pd_data


if __name__ == "__main__":
    get_dataset()