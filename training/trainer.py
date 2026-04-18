import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

from Converter.DataAccess.DatasetReader import get_dataset
from model.model import ChessCNN
from training.ChessDataset import ChessPositionDataset
from Converter.Parse.FEN_Parser import FEN_Parser


def train_model():
    # Load your dataframe
    df = get_dataset()

    print("Columns in dataset:", df.columns.tolist())
    print("Number of rows:", len(df))

    # Change "advantage" here if your column has a different name
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    train_dataset = ChessPositionDataset(
        train_df,
        fen_column="FEN",
        target_column="Evaluation"
    )
    val_dataset = ChessPositionDataset(
        val_df,
        fen_column="FEN",
        target_column="Evaluation"
    )

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    model = ChessCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    num_epochs = 3

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * X_batch.size(0)

        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                preds = model(X_batch)
                loss = criterion(preds, y_batch)
                val_loss += loss.item() * X_batch.size(0)

        val_loss /= len(val_loader.dataset)

        print(f"Epoch {epoch + 1}/{num_epochs} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f}")

    return model


def predict_advantage(model, fen: str) -> float:
    parser = FEN_Parser()
    x = parser.generate_matrices(fen)

    x = torch.tensor(x, dtype=torch.float32).unsqueeze(0)

    device = next(model.parameters()).device
    x = x.to(device)

    model.eval()
    with torch.no_grad():
        pred = model(x).item()

    # undo normalization
    return pred * 1000.0


if __name__ == "__main__":
    model = train_model()
    torch.save(model.state_dict(), "chess_cnn.pth")
    # Example prediction on one sample
    df = get_dataset(5)
    sample_fen = df["FEN"].iloc[0]

    pred = predict_advantage(model, sample_fen)

    print("\nSample FEN:")
    print(sample_fen)
    print("Predicted advantage:", pred)