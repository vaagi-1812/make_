import cv2
from ultralytics import YOLO

# --- CONFIG ---
video_path = 'turnaround clip.mp4'
model = YOLO('best.pt')
cap = cv2.VideoCapture(video_path)
cap = cv2.VideoCapture(video_path)

# Logic Variables
phases = {
    "DEBOARDING": False,
    "CLEANING": False,
    "BOARDING": False,
    "LUGGAGE": False
}
cleaning_seen_count = 0

cap = cv2.VideoCapture(video_path)
print("Analyzing video... (Press 'q' to quit early)")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Run AI
    results = model(frame, verbose=False)
    detected = []

    # See what objects are in this frame
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        detected.append(label)

    # --- THE LOGIC ---
    # 1. Check for Cleaning Crew (The Sandwich Separator)
    if "cleaning_crew_vehicle" in detected:
        cleaning_seen_count += 1
        phases["CLEANING"] = True

    # 2. Check for Luggage
    if "luggage_vehicle" in detected:
        phases["LUGGAGE"] = True

    # 3. Check for Bridge (Deboarding vs Boarding)
    if "bridge_connected" in detected:
        # If we haven't seen cleaning yet -> It's DEBOARDING
        if cleaning_seen_count < 10:
            phases["DEBOARDING"] = True
        # If we HAVE seen cleaning (and it's gone or active) -> It's BOARDING
        else:
            phases["BOARDING"] = True

    # Show the video with boxes
    cv2.imshow('Turnaround AI', results[0].plot())
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()

# --- FINAL REPORT ---
print("\n" + "=" * 30)
print("   TURNAROUND REPORT")
print("=" * 30)
print(f"✅ Deboarding Phase: {'DETECTED' if phases['DEBOARDING'] else 'Not Detected'}")
print(f"✅ Cleaning Phase:   {'DETECTED' if phases['CLEANING'] else 'Not Detected'}")
print(f"✅ Boarding Phase:   {'DETECTED' if phases['BOARDING'] else 'Not Detected'}")
print(f"✅ Luggage Handling: {'DETECTED' if phases['LUGGAGE'] else 'Not Detected'}")