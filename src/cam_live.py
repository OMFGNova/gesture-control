import cv2
import time
import mediapipe as mp
import math
import pyautogui

# HELPER FUNCTIONS
def to_px(landmark, width, height):

    x = landmark.x * width
    y = landmark.y * height

    return (x, y)

def pinch_ratio_3d(landmarks):
    thumb = (landmarks[4].x, landmarks[4].y, landmarks[4].z)
    index = (landmarks[8].x, landmarks[8].y, landmarks[8].z)

    wrist = (landmarks[0].x, landmarks[0].y, landmarks[0].z)
    bottom_pinky = (landmarks[17].x, landmarks[17].y, landmarks[17].z)

    palm_len = math.dist(wrist, bottom_pinky)

    if palm_len < 0.02:
        return None
    else:
        pinch_dist = math.dist(thumb, index)
        return pinch_dist/palm_len
# HELPER FUNCTIONS

# Path to model 
model_path = r"./models/hand_landmarker.task"

PINCH_ON = 0.4
PINCH_OFF = 2.3

# Capture picture frame from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Camera not open")

# Create instance of mediapipe
base_options = mp.tasks.BaseOptions
hand_landmarker = mp.tasks.vision.HandLandmarker
hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
vision_runningmode = mp.tasks.vision.RunningMode

options = hand_landmarker_options(
    base_options = base_options(model_asset_path=model_path),
    running_mode=vision_runningmode.VIDEO,
    num_hands=1
)

# Loop that continuously uses live webcam
prev_time = time.perf_counter()
total_time = 0
count = 0
pinch = None
debounce = 0
N = 5

with hand_landmarker.create_from_options(options) as landmarker:
    while True:
        # recording of fps, detect ms
        now = time.perf_counter()
        dt = now - prev_time
        time_stamp_ms = int(now * 1000)
        fps = str(int(1/dt))
        prev_time = now
        ret, frame = cap.read()

        if not ret:
            break

        # cv2 is in BGR, this changes to RGB and flips cam so its mirrored
        flipped_frame = cv2.flip(frame, 1)
        colour_flipped_frame = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=colour_flipped_frame)

        # detection of frame
        start_detect_time = time.perf_counter()
        hand_landmarker_result = landmarker.detect_for_video(mp_image, time_stamp_ms)
        end_detect_time = time.perf_counter()
        total_time += (end_detect_time - start_detect_time) * 1000
        count += 1

        if hand_landmarker_result.handedness:
            # Uses values of the hand landmarks to determine index and thumb for pinch
            height, width, _ = flipped_frame.shape


            # converts hand_landmarker results to float of the ratio of the dimensions
            thumb_x, thumb_y = to_px(hand_landmarker_result.hand_landmarks[0][4], width, height)
            index_x, index_y =to_px(hand_landmarker_result.hand_landmarks[0][8], width, height)

            wrist_x, wrist_y = to_px(hand_landmarker_result.hand_landmarks[0][0], width, height)
            bottom_pinky_x, bottom_pinky_y = to_px(hand_landmarker_result.hand_landmarks[0][17], width, height)

            # calculats dist from bottom pinky to wrist and pink distance from index to thumb
            ratio = pinch_ratio_3d(hand_landmarker_result.hand_landmarks[0])
            
            if ratio is None:
                pinch = None
                debounce = 0
            else:
                cv2.putText(flipped_frame, f"ratio: {ratio:.2f}", (420, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 

                if pinch is None:
                    if ratio < PINCH_ON:
                        pinch = True
                    elif ratio > PINCH_OFF:
                        pinch = False

                    debounce = 0 
                else:
                    if not pinch:
                        flip = ratio < PINCH_ON
                    else:
                        flip = ratio > PINCH_OFF

                    if flip:
                        debounce += 1
                    else:
                        debounce = 0

                    if debounce >= N:
                        pinch = not pinch
                        debounce = 0
                        if pinch:
                            print("ZOOM OUT")
                            # pyautogui.hotkey("ctrl", "-")
                        else:
                            print("ZOOM IN")
                            # pyautogui.hotkey("ctrl", "+")

            cv2.line(flipped_frame, (int(thumb_x), int(thumb_y)), (int(index_x), int(index_y)), (255, 0, 0), 2)
            # cv2.putText(flipped_frame, f"distance: {str(int(pinch_dist))}", (420, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))   
        else:
            pinch = None
            debounce = 0 

        # normal cv2 stuff
        cv2.putText(flipped_frame, f"detect: {int(total_time/count)}", (250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.putText(flipped_frame, f"fps: {fps}", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.imshow("window", flipped_frame)
        check = cv2.waitKey(1)

        if check == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

