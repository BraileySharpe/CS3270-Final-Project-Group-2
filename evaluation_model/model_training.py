import torch
from mock_data import generate_data
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, random_split, Dataset
from torch.utils.data import Dataset

class MyDataset(Dataset):
	def __init__(self, data):
		self.data = data

	def __len__(self):
		return len(self.data)

	def __getitem__(self, idx):
		tensor, evaluation = self.data[idx]

		tensor = torch.tensor(tensor, dtype=torch.float32)
		evaluation = torch.tensor(evaluation, dtype=torch.float32)

		return tensor, evaluation

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

mock_dataset = generate_data()

dataset = MyDataset(mock_dataset)

train_size = int(0.7 * len(dataset))
test_size = len(dataset) - train_size

train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

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
			nn.AdaptiveAvgPool2d(1),
		)
		self.fc1= nn.Linear(128, 1)

	def forward(self,x):
		x = self.feature_extract(x)
		x = torch.flatten(x, 1)
		x = self.fc1(x)
		return x

model = CNN_Model().to(device)

train_losses = []
test_losses = []


criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=5)

num_epochs = 10


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



