import cv2
import os
import shutil
import random

# --- CONFIG ---
VIDEO_PATH = 'turnaround clip.mp4'
CLASSES = ['bridge_connected', 'cleaning_crew_vehicle', 'luggage_vehicle']
OUTPUT_DIR = 'dataset'
FRAME_INTERVAL = 4  # Extract 1 image every 4 seconds


def main():
    # 1. Reset Folders
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    paths = [f"{OUTPUT_DIR}/images/train", f"{OUTPUT_DIR}/images/val",
             f"{OUTPUT_DIR}/labels/train", f"{OUTPUT_DIR}/labels/val"]
    for p in paths:
        os.makedirs(p, exist_ok=True)

    # 2. Extract Frames
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * FRAME_INTERVAL)
    count = 0
    saved = 0

    print("Extracting images...")
    while True:
        success, frame = cap.read()
        if not success: break

        if count % interval_frames == 0:
            subset = "train" if random.random() < 0.8 else "val"
            cv2.imwrite(f"{OUTPUT_DIR}/images/{subset}/frame_{saved:04d}.jpg", frame)
            saved += 1
        count += 1

    cap.release()

    # 3. Create YAML file for YOLO
    yaml_content = f"path: {os.path.abspath(OUTPUT_DIR)}\ntrain: images/train\nval: images/val\nnames:\n"
    for i, c in enumerate(CLASSES):
        yaml_content += f"  {i}: {c}\n"

    with open(f"{OUTPUT_DIR}/data.yaml", "w") as f:
        f.write(yaml_content)

    print(f"✅ Done! Created {saved} images in '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()