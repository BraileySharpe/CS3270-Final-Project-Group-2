
import torch
import torch.nn as nn
import torch.nn.functional as F

class ChessCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=12, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))   # (B, 32, 8, 8)
        x = F.relu(self.conv2(x))   # (B, 64, 8, 8)
        x = F.relu(self.conv3(x))   # (B, 128, 8, 8)

        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)             # (B, 1)

        return x.squeeze(1)         # (B,)