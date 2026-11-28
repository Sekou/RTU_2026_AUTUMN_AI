import cv2

video_path = "2018_youbot_top_view.avi"
cap = cv2.VideoCapture(video_path)

from ultralytics import YOLO
model = YOLO("best.pt") 

while True:
    ret, frame = cap.read()

    # Restrict output to at most 1 detection per image
    results = model.predict(source=frame, max_det=1)
    frame_=frame.copy()

    # Extract the single detection's details
    result = results[0]
    if len(result.boxes) > 0:
        box = result.boxes[0]
        coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        confidence = box.conf[0].item()  # Confidence score
        class_id = int(box.cls[0].item())  # Class ID
        class_name = result.names[class_id]  # Class name
        frame_=cv2.rectangle(frame_, coords[:2], 
                                    coords[2:], (255,255,0), 2)
    
    # If the video reaches the end, reset to the first frame
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    cv2.imshow("image", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(30) & 0xFF == ord("q"):
        break    

cap.release()
cv2.destroyAllWindows()
