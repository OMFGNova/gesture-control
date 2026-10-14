import cv2
import time

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not open")

prev_time = time.perf_counter()

while True:
    now = time.perf_counter()
    dt = now - prev_time
    fps = str(int(1/dt))
    prev_time = now
    ret, frame = cap.read()

    if not ret:
        break

    flipped_frame = cv2.flip(frame, 1)
    flipped_frame = cv2.putText(flipped_frame, "fps: " + fps, (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
    cv2.imshow("window", flipped_frame)
    check = cv2.waitKey(1)

    if check == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()