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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataframe = generate_training_data()

train_df, test_df = train_test_split(dataframe, test_size=0.3, random_state=56)

mean = train_df["Evaluation"].mean()
std= train_df["Evaluation"].std()

train_df["Evaluation"] = (train_df["Evaluation"] - mean) / std
test_df["Evaluation"] = (test_df["Evaluation"] - mean) / std

train_dataset = MyDataset(train_df)
test_dataset = MyDataset(test_df)


train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

class CNN_Model(nn.Module):
	def __init__(self):
		super().__init__()
		self.feature_extract= nn.Sequential(
			nn.Conv2d(12, 32, kernel_size=3, padding=1),
			nn.ReLU(),
			nn.Conv2d(32, 64, kernel_size=3, padding=1),
			nn.ReLU(), 
			nn.Conv2d(64, 128, kernel_size=3, padding=1),
			nn.ReLU(),
		)
		self.fc= nn.Sequential(
			nn.Flatten(), 
			nn.Linear(128*8*8, 256),
			nn.ReLU(), 
			nn.Linear(256,1)
		)

	def forward(self,x):
		x = self.feature_extract(x)
		x = self.fc(x)
		return x

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


