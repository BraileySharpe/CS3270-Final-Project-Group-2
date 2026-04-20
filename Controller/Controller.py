
from Converter.DataAccess.DatasetReader import get_dataset
from Converter.Parse.FEN_Parser import FEN_Parser

def generate_training_data():
    parser = FEN_Parser()
    data_rows = get_dataset(2000)
    data_rows = data_rows.rename(columns={"FEN" : "tensor"})
    for row in data_rows.itertuples(): 
        data_rows.loc[row.Index, "tensor"] = parser.generate_matrices(row.tensor)
        evaluation = data_rows.loc[row.Index, "Evaluation"]
        if evaluation.startswith("#"): 
            evaluation = evaluation.strip("#")
        evaluation = int(evaluation)
        data_rows.loc[row.Index, "Evaluation"] = evaluation
    return data_rows


if __name__ == "__main__":
    training_data = generate_training_data()
    print(training_data.head())