import cv2

cap = cv2.VideoCapture(0)
print("Opened", cap.isOpened())

ret, frame = cap.read()
print("ret", ret)
print("shape", frame.shape)

cap.release()