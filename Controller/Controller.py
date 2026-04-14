from Converter.DataAccess.DatasetReader import get_dataset
from Converter.Parse.FEN_Parser import FEN_Parser


def run():
    parser = FEN_Parser()
    data_rows = get_dataset(300)
    fen_data = data_rows["FEN"]
    for row in fen_data:
        tensor = parser.generate_matrices(row) #tensor can be used from here


if __name__ == "__main__":
    run()