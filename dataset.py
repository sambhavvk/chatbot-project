from datasets import load_dataset

# Download and load the dataset
ds = load_dataset("mteb/banking77")

# Access specific splits
train_data = ds["train"]