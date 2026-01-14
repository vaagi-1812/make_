import os

# Define paths
train_img_path = "dataset/images/train"
train_lbl_path = "dataset/labels/train"

# Get file lists
images = sorted([f for f in os.listdir(train_img_path) if f.endswith('.jpg') or f.endswith('.png')])
labels = sorted([f for f in os.listdir(train_lbl_path) if f.endswith('.txt')])

print(f"🔎 Found {len(images)} images and {len(labels)} label files.")

if len(labels) == 0:
    print("❌ CRITICAL ERROR: No label files found in 'dataset/labels/train'!")
    print("   -> Did you paste the text files there?")
else:
    # Check the first pair
    img_name = images[0]
    expected_label = img_name.rsplit('.', 1)[0] + ".txt"

    print(f"\nChecking first pair:")
    print(f"   Image: {img_name}")
    print(f"   Expected Label: {expected_label}")

    if expected_label in labels:
        print("✅ First pair matches! YOLO should see this.")

        # Check if file is empty
        with open(f"{train_lbl_path}/{expected_label}", 'r') as f:
            content = f.read()
            if len(content.strip()) == 0:
                print("⚠️ WARNING: The text file is EMPTY. Did you save the labels in CVAT?")
            else:
                print(f"✅ Label content found: {content.strip()}")
    else:
        print(f"❌ MISMATCH: Found image '{img_name}' but could NOT find '{expected_label}'")