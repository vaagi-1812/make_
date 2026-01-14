from ultralytics import YOLO
import torch

if __name__ == '__main__':
    # 1. Check if GPU is actually available
    if torch.cuda.is_available():
        print(f"✅ GOOD NEWS: GPU Detected: {torch.cuda.get_device_name(0)}")
        device = 0 # Use the RTX 3070
    else:
        print("⚠️ WARNING: GPU not found. Training will be SLOW on CPU.")
        device = 'cpu'

    # 2. Load the model
    model = YOLO('yolo11n.pt')

    # 3. Train
    print("Starting Training on RTX 3070...")
    model.train(
        data='dataset/data.yaml',
        epochs=100,      # You can do 100 epochs easily now
        imgsz=640,
        batch=16,        # RTX 3070 has 8GB VRAM, so batch=16 is safe
        device=device,   # Forces GPU use
        plots=True
    )
    print("Training Complete!")