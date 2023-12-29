import json

from nltk_utils import tokenize, stemming, bag_of_words
import string
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import NeuralNet

print("Please wait a moment... The training process is getting underway!")
with open('../data/new_intents.json', 'r') as file:
    intents = json.load(file)
all_words = []
tags = []
xy = []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        if isinstance(pattern, str):
            tokenize_word = tokenize(pattern)
            all_words.extend(tokenize_word)
            xy.append((tokenize_word, tag))
        elif isinstance(pattern, dict):
            name = pattern['name']
            id = pattern['id']
            tokenize_word = [name, id]
            all_words.extend(tokenize_word)
            xy.append((tokenize_word, tag))
punctuation_chars = list(string.punctuation)
unnecessary_words = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
                     'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with']
ignore_bag_of_words = punctuation_chars + unnecessary_words
all_words = [stemming(word) for word in all_words if word not in ignore_bag_of_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    list_of_words = bag_of_words(pattern_sentence, all_words)
    X_train.append(list_of_words)
    label = tags.index(tag)
    y_train.append(label)
X_train = np.array(X_train)
y_train = np.array(y_train)


class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.X_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

batch_size = 8
input_size = len(all_words)  # input size equals to length of list or in other words length of all_words
hidden_size = 8
output_size = len(tags)
learning_rate = 0.001
num_epochs = 1000
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size)

# loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
loss = None
progress = None
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(device, dtype=torch.int64)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 100 == 0:
        if progress is not None:
            print(f"Loading... {progress:.2f}%")
        else:
            print("Loading... 0%")
        progress = ((epoch + 1) / num_epochs) * 100

print("Completing... 100.00%")
print(f"Final Loss: {loss.item():.4f}")
print("Training process has been completed. Thanks for waiting patiently!")
print("File saved to data.pth")
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}
FILE = "../data.pth"
torch.save(data, FILE)

