import cv2
import time
import mediapipe as mp

# Path to model 
model_path = r"./models/hand_landmarker.task"

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not open")

base_options = mp.tasks.BaseOptions
hand_landmarker = mp.tasks.vision.HandLandmarker
hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
vision_runningmode = mp.tasks.vision.RunningMode

options = hand_landmarker_options(
    base_options = base_options(model_asset_path=model_path),
    running_mode=vision_runningmode.VIDEO,
    num_hands=4
)

prev_time = time.perf_counter()

with hand_landmarker.create_from_options(options) as landmarker:
    while True:
        now = time.perf_counter()
        dt = now - prev_time
        time_stamp_ms = int(now * 1000)
        fps = str(int(1/dt))
        prev_time = now
        ret, frame = cap.read()

        if not ret:
            break

        flipped_frame = cv2.flip(frame, 1)
        colour_flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=colour_flipped_frame)

        hand_landmarker_result = landmarker.detect_for_video(mp_image, time_stamp_ms)

        if not len(hand_landmarker_result.handedness):
            print("No hands detected")
        else:
            height, width, _ = flipped_frame.shape

            for hands in hand_landmarker_result.hand_landmarks:
                for index, position in enumerate(hands):
                    px = int(position.x * width)
                    py = int(position.y * height)

                    cv2.circle(flipped_frame, (px, py), 5, (0, 255, 0), -1)
                    cv2.putText(flipped_frame, str(index), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)


        flipped_frame = cv2.putText(flipped_frame, "fps: " + fps, (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.imshow("window", flipped_frame)
        check = cv2.waitKey(1)

        if check == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()