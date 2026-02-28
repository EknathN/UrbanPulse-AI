from ultralytics import YOLO
import cv2
import time

# -----------------------------
# LOAD MODEL
# -----------------------------
model = YOLO("yolov8n.pt")

# -----------------------------
# LOAD VIDEO
# -----------------------------
cap = cv2.VideoCapture("traffic.mp4")

vehicle_classes = ["car", "truck", "bus", "motorbike"]

# -----------------------------
# MEMORY VARIABLES
# -----------------------------
object_memory = {}
prev_frame = None

litter_persist_until = 0
helmet_persist_until = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True)

    count = 0
    helmet_violation = False
    litter_detected = False

    person_boxes = []
    bike_boxes = []

    # -----------------------------
    # MOTION ANALYSIS
    # -----------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    motion_score = 0

    if prev_frame is not None:
        diff = cv2.absdiff(prev_frame, gray)
        motion_score = diff.sum()

    prev_frame = gray

    # -----------------------------
    # PROCESS DETECTIONS
    # -----------------------------
    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue

        for box in boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            track_id = int(box.id[0]) if box.id is not None else None
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # ---------------- VEHICLE COUNT ----------------
            if label in vehicle_classes:
                count += 1

            # ---------------- STORE PERSON & BIKE ----------------
            if label == "person":
                person_boxes.append((x1, y1, x2, y2))

            if label == "motorbike":
                bike_boxes.append((x1, y1, x2, y2))

            # ---------------- LITTER TRACKING ----------------
            if label in ["bottle", "cup"] and track_id is not None:

                center_y = (y1 + y2) // 2

                if track_id not in object_memory:
                    object_memory[track_id] = {
                        "prev_y": center_y,
                        "frames_low": 0
                    }
                else:
                    prev_y = object_memory[track_id]["prev_y"]

                    # Detect falling motion
                    if center_y - prev_y > 20:
                        object_memory[track_id]["frames_low"] += 1

                    # Object near bottom of frame
                    if y2 > frame.shape[0] * 0.75:
                        object_memory[track_id]["frames_low"] += 1

                    # Confirm litter
                    if object_memory[track_id]["frames_low"] > 12 and motion_score > 500000:
                        litter_persist_until = time.time() + 5

                    object_memory[track_id]["prev_y"] = center_y

    # -----------------------------
    # HELMET DETECTION (RIDER BASED)
    # -----------------------------
    for px1, py1, px2, py2 in person_boxes:
        for bx1, by1, bx2, by2 in bike_boxes:
            if px1 < bx2 and px2 > bx1 and py1 < by2 and py2 > by1:
                helmet_persist_until = time.time() + 5

    # -----------------------------
    # PERSISTENCE CHECK
    # -----------------------------
    if time.time() < litter_persist_until:
        litter_detected = True
    else:
        litter_detected = False

    if time.time() < helmet_persist_until:
        helmet_violation = True
    else:
        helmet_violation = False

    # -----------------------------
    # SAVE STATUS FILES
    # -----------------------------
    with open("vehicle_count.txt", "w") as f:
        f.write(str(count))

    with open("helmet_status.txt", "w") as f:
        f.write("1" if helmet_violation else "0")

    with open("litter_status.txt", "w") as f:
        f.write("1" if litter_detected else "0")

    # -----------------------------
    # SIGNAL LOGIC
    # -----------------------------
    if count > 20:
        green_time = 70
    elif count > 10:
        green_time = 50
    else:
        green_time = 30

    annotated_frame = results[0].plot()

    # -----------------------------
    # DISPLAY SECTION
    # -----------------------------
    cv2.putText(annotated_frame, f"Vehicle Count: {count}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    cv2.putText(annotated_frame, f"Green Time: {green_time} sec",
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 255), 2)

    # Helmet display
    if helmet_violation:
        helmet_text = "Helmet Violation Detected!"
        helmet_color = (0, 0, 255)
    else:
        helmet_text = "Helmet Status: OK"
        helmet_color = (0, 255, 0)

    cv2.putText(annotated_frame, helmet_text,
                (20, 120), cv2.FONT_HERSHEY_SIMPLEX,
                1, helmet_color, 2)

    # Litter display
    if litter_detected:
        litter_text = "LITTERING DETECTED!"
        litter_color = (0, 0, 255)
    else:
        litter_text = "Litter Status: Clean"
        litter_color = (0, 255, 0)

    cv2.putText(annotated_frame, litter_text,
                (20, 160), cv2.FONT_HERSHEY_SIMPLEX,
                1, litter_color, 2)

    cv2.imshow("UrbanPulse AI - Integrated System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()