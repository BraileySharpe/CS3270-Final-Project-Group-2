##Generate random chess boards
##DATA FILE TENSOR 12x8x8
## 12 Layers to represent each type of peice on the board, 8 rows to represents the 8 rows of a chess board, 8 columns to represents the 8 columns of the chess board, and 0 or 1 to represent if a peice is there or not. 
## Example tensor[1][2][3] = 0. The previous means that at layer 1 which for this example we will call white pawns, row 2 & column 3. There is not a white pawn there because it is 0. 
## Example tensor[2][3][4] = 1. This means that at layer 2 which im calling white knight that there is a white knight there at row 3 and column 4, because its equal to 1. 

import random

NUM_TENSORS = 50
BOARD_SIZE = 8
LAYERS = 12

def empty_tensor():
	return [[[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)] for _ in range(LAYERS)]

def random_square(used):
	while True:
		r = random.randint(0,7)
		c = random.randint(0,7)
		if (r,c) not in used:
			used.add((r,c))
			return r,c

def generate_board():
	tensor = empty_tensor()
	used = set()
	
	piece_counts = {
		0:8, 1:2, 2:2, 3:2, 4:1, 5:1,   # white
		6:8, 7:2, 8:2, 9:2, 10:1, 11:1  # black
	}

	for layer,count in piece_counts.items():
		for _ in range(count):
			random_num = random.randint(0,1)
			if random_num == 0: 
			## a 50/50 if we generate that peice to have random num of peices on board
				continue
			r,c = random_square(used)
			tensor[layer][r][c] = 1

	return tensor
def mock_evalution(tensor):
	white_peices_count = 0
	black_peices_count = 0
	total_peices = 0
	for layer in range(LAYERS): 
		for row in range(BOARD_SIZE):
			for column in range(BOARD_SIZE):
				peice_there = tensor[layer][row][column]
				if peice_there == 1 and layer <= 5: 
					white_peices_count += 1
					total_peices += 1
				elif peice_there ==  1 and layer > 5: 
					black_peices_count += 1
					total_peices += 1
	evaluation = white_peices_count / total_peices  
	return evaluation
	

def generate_data():
	dataset = []
	for _ in range(NUM_TENSORS): 
		board = generate_board()
		evaluation = mock_evalution(board)
		dataset.append([board, evaluation])
	return dataset
	
if (__name__ == "__main__"): 
	dataset = generate_data()
	print(dataset)