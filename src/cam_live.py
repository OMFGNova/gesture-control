import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not open")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("window", frame)
    check = cv2.waitKey(1)

    if check == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()