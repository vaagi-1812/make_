import shutil
import os

# Define paths
source_folder = "dataset/labels/train"
dest_folder = "dataset/labels/val"

# Create destination if it doesn't exist
os.makedirs(dest_folder, exist_ok=True)

# Get all text files
files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]

print(f"Copying {len(files)} labels from Train to Val...")

for file in files:
    shutil.copy(f"{source_folder}/{file}", f"{dest_folder}/{file}")

print("✅ Done! Now your 'val' folder has labels too.")