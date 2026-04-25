import torch
from evaluation_model.mock_data import generate_data
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, random_split, Dataset
from torch.utils.data import Dataset
from Controller.Controller import generate_training_data
from sklearn.model_selection import train_test_split


class MyDataset(Dataset):
	def __init__(self, data):
		self.data = data

	def __len__(self):
		return len(self.data)

	def __getitem__(self, idx):
		tensor = self.data.iloc[idx, 0]
		evaluation = self.data.iloc[idx, 1]
		
		tensor = torch.tensor(tensor, dtype=torch.float32)
		evaluation = torch.tensor(evaluation, dtype=torch.float32)

		return tensor, evaluation



class ResBlock(nn.Module):
	def __init__(self, channels):
		super().__init__()
		self.block = nn.Sequential(
			nn.Conv2d(channels, channels, kernel_size=3, padding=1),
			nn.BatchNorm2d(channels),
			nn.ReLU(),
			nn.Conv2d(channels, channels, kernel_size=3, padding=1),
			nn.BatchNorm2d(channels)
		)

	def forward(self, x):
		return torch.relu(x + self.block(x))



class CNN_Model(nn.Module):
	def __init__(self, input_planes=19, channels=64, num_blocks=20):
		super().__init__()

		
		self.input_layer = nn.Sequential(
			nn.Conv2d(input_planes, channels, kernel_size=3, padding=1),
			nn.BatchNorm2d(channels),
			nn.ReLU()
		)

		
		self.res_blocks = nn.Sequential(
			*[ResBlock(channels) for _ in range(num_blocks)]
		)

		

		self.value_head = nn .Sequential(
			nn.Conv2d(channels, 1, kernel_size=1),
			nn.BatchNorm2d(1),
			nn.ReLU(),
		)
		self.fc = nn.Sequential(
			nn.Flatten(),
			nn.Linear(8*8, 128),
			nn.ReLU(),
			nn.Linear(128, 1)
		)

	def forward(self, x):
		x = self.input_layer(x)
		x = self.res_blocks(x)
		x = self.value_head(x)
		x = self.fc(x)
		return x

def scores_to_policy(scores, temperature=1.0):
	scores = torch.tensor(scores, dtype=torch.float32)
	return torch.softmax(scores / temperature, dim=0)


if __name__ == "__main__": 
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

	dataframe = generate_training_data()

	train_df, test_df = train_test_split(dataframe, test_size=0.3, random_state=56)


	train_dataset = MyDataset(train_df)
	test_dataset = MyDataset(test_df)


	train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
	test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
	model = CNN_Model().to(device)

	train_losses = []
	test_losses = []


	criterion = nn.MSELoss()
	optimizer = optim.Adam(model.parameters(), lr=0.001)
	scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5)

	num_epochs = 40


	for epoch in range(num_epochs):

		model.train()
		train_loss = 0
		total = 0

		for tensor, evaluation in train_loader:

			tensor, evaluation = tensor.to(device), evaluation.to(device)
			optimizer.zero_grad()
			output = model(tensor)
		
			evaluation = evaluation.unsqueeze(1)
		
			loss = criterion(output, evaluation)
			loss.backward()
			optimizer.step()
		
			train_loss += loss.item()
	
		train_loss /= len(train_loader)
		train_losses.append(train_loss)
	
		model.eval()
		test_loss = 0 

		with torch.no_grad():
			for tensor, evaluation in test_loader:
				tensor, evaluation = tensor.to(device), evaluation.to(device)
				output = model(tensor)
				evaluation = evaluation.unsqueeze(1)
			
				loss = criterion(output, evaluation)
				test_loss += loss.item()

		test_loss /= len(test_loader)
		test_losses.append(test_loss)

		scheduler.step(test_loss)

		print(f"Epoch {epoch+1}/{num_epochs}")
		print(f"Train Loss: {train_loss:.4f}")
		print(f"Test  Loss: {test_loss:.4f}")
		print("-"*40)

	average_train_loss = sum(train_losses) / len(train_losses)
	print(f"Average Training Loss: {average_train_loss:.4f}")
	average_test_loss = sum(test_losses) / len(test_losses)
	print(f"Average Testing Loss: {average_test_loss:.4f}")

	torch.save(model.state_dict(), "evaluation_cnn_model.pth")
	print("Model Saved")
