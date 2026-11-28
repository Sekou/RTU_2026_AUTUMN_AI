# Запрос ИИ: how to program py cv2 loop avi video
# pip install opencv-python --break-system-packages
# TODO: выпрямить изображение; обучить нейросеть на детекцию

import cv2

bb = None
bb_= None
class_id=1

sample_ind=0

video_path = "2018_youbot_top_view.avi"
cap = cv2.VideoCapture(video_path)
W=cap.get(cv2.CAP_PROP_FRAME_WIDTH)
H=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(W, H)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Calculate delay in milliseconds to match the video's original FPS
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps) if fps > 0 else 30

def draw_bb(event,x,y,flags,param):
    global bb,bb_,class_id
    L,R = event == cv2.EVENT_LBUTTONDOWN, event == cv2.EVENT_RBUTTONDOWN
    if L or R:
        w,h=70,70
        bb=[x-w//2, y-h//2, w, h]
        bb_=[(bb[0]+w//2)/W, (bb[1]/H+h//2), bb[2]/W, bb[3]/H]
        cv2.rectangle(frame, bb[:2], bb[2:], (255, 0, 0), 2)

cv2.namedWindow("image")
cv2.setMouseCallback("image",draw_bb)

while True:
    ret, frame = cap.read()

    # If the video reaches the end, reset to the first frame
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame_=frame.copy()
    if bb is not None:
        bb_color=(255, 0, 0) if class_id == 0 else (100, 100, 100)
        frame_=cv2.rectangle(frame_, bb[:2], 
                            [bb[0]+bb[2], bb[1]+bb[3]], bb_color, 2)
        cv2.putText(frame_,f"{class_id}",
                    (20,30),cv2.FONT_HERSHEY_DUPLEX,1,(0,0,255),2)
    cv2.imshow("image", frame_)

    # 0
    z=cv2.waitKey(delay)
    if z & 0xFF == ord("0"):
        class_id=0    
    # 1
    if z & 0xFF == ord("1"):
        class_id=1   
    # Press 'q' to exit the loop
    if z & 0xFF == ord("q"):
        break    
    # Press 's' to save sample
    if z & 0xFF == ord("s"):
        #TODO: проверять наличие подпапок
        cv2.imwrite(f"dataset/images/sample_{sample_ind}.jpg", frame)
        with open(f"dataset/labels/sample_{sample_ind}.txt", "w") as f:
            s=f"{class_id} {bb_[0]:.3f} {bb_[1]:.3f} {bb_[2]:.3f} {bb_[3]:.3f}"
            print(s)
            f.write(s)
            print(f"Saved {sample_ind} sample")
            sample_ind+=1

cap.release()
cv2.destroyAllWindows()
