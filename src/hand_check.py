import cv2
import mediapipe as mp

# Path to model 
model_path = r"./models/hand_landmarker.task"

# Grab single image from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not open")

ret, frame = cap.read()

if not ret:
    raise SystemExit("return is false")

flipped_frame = cv2.flip(frame, 1)
colour_flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=colour_flipped_frame)

# Create a HandLandmarker Object
base_options = mp.tasks.BaseOptions
hand_landmarker = mp.tasks.vision.HandLandmarker
hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
vision_runningmode = mp.tasks.vision.RunningMode

options = hand_landmarker_options(
    base_options = base_options(model_asset_path=model_path),
    running_mode=vision_runningmode.IMAGE,
    num_hands=2
)

with hand_landmarker.create_from_options(options) as landmarker:
    hand_landmarker_result = landmarker.detect(mp_image)

if not len(hand_landmarker_result.handedness):
    print("No hands detected")
else:
    height, width, _ = flipped_frame.shape
    print(height, width)

    for hands in hand_landmarker_result.hand_landmarks:
        for index, position in enumerate(hands):
            # print(f"Index: {index} with positon x: {position.x:.3f}, position y: {position.y:.3f}, position z: {position.z:.3f}")
            px = int(position.x * width)
            py = int(position.y * height)

            cv2.circle(flipped_frame, (px, py), 5, (0, 255, 0), -1)
            cv2.putText(flipped_frame, str(index), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

cv2.imshow("landmarks", flipped_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


