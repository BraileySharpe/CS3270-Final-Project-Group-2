import numpy as np
import torch
from torch.utils.data import Dataset

from Converter.Parse.FEN_Parser import FEN_Parser


def parse_advantage(value):
    """
    Convert engine eval strings into a numeric target.

    Examples:
    "56"   -> 56.0
    "-10"  -> -10.0
    "#+13" -> 10000.0
    "#-3"  -> -10000.0
    42     -> 42.0
    """
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    value = str(value).strip()

    if value.startswith("#"):
        if "+" in value:
            return 10000.0
        if "-" in value:
            return -10000.0
        return 0.0

    return float(value)


class ChessPositionDataset(Dataset):
    def __init__(
        self,
        df,
        fen_column: str = "FEN",
        target_column: str = "advantage",
        normalize_target: bool = True,
    ):
        self.df = df.reset_index(drop=True)
        self.fen_column = fen_column
        self.target_column = target_column
        self.normalize_target = normalize_target
        self.parser = FEN_Parser()

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        fen = self.df.loc[idx, self.fen_column]
        raw_target = self.df.loc[idx, self.target_column]

        x = self.parser.generate_matrices(fen).astype(np.float32)
        y = np.float32(parse_advantage(raw_target))

        if self.normalize_target:
            y = np.clip(y, -1000, 1000) / 1000.0

        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)