import cv2
import time
import mediapipe as mp
import math

# HELPER FUNCTIONS
def to_px(landmark, width, height):

    x = landmark.x * width
    y = landmark.y * height

    return (x, y)

def pinch_ratio(landmarks, width, height):
    thumb = to_px(landmarks[4], width, height)
    index =to_px(landmarks[8], width, height)

    wrist = to_px(landmarks[0], width, height)
    bottom_pinky = to_px(landmarks[17], width, height)

    palm_len = math.hypot(bottom_pinky[0] - wrist[0], bottom_pinky[1] - wrist[1])

    if palm_len < 10:
        return None
    else:
        pinch_dist = math.hypot(index[0] - thumb[0], index[1] - thumb[1])
        return pinch_dist/palm_len
# HELPER FUNCTIONS

# Path to model 
model_path = r"./models/hand_landmarker.task"

PINCH_ON = 0.35
PINCH_OFF = 0.45

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
pinching = False

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
            # Uses values of the hand landmarks to determine index and thumb for pinching 
            height, width, _ = flipped_frame.shape

            # converts hand_landmarker results to float of the ratio of the dimensions
            thumb_x, thumb_y = to_px(hand_landmarker_result.hand_landmarks[0][4], width, height)
            index_x, index_y =to_px(hand_landmarker_result.hand_landmarks[0][8], width, height)

            wrist_x, wrist_y = to_px(hand_landmarker_result.hand_landmarks[0][0], width, height)
            bottom_pinky_x, bottom_pinky_y = to_px(hand_landmarker_result.hand_landmarks[0][17], width, height)

            # To show all points on hand ---------
            # for hands in hand_landmarker_result.hand_landmarks:
            #     for index, position in enumerate(hands):
            #         px = int(position.x * width)
            #         py = int(position.y * height)

            #         cv2.circle(flipped_frame, (px, py), 5, (0, 255, 0), -1)
            #         cv2.putText(flipped_frame, str(index), (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            # --------------------------------------------
            
            # calculats dist from bottom pinky to wrist and pink distance from index to thumb

            ratio = pinch_ratio(hand_landmarker_result.hand_landmarks[0], width, height)
            
            if ratio is None:
                pinching = False
            else:
                cv2.putText(flipped_frame, f"ratio: {ratio:.2f}", (420, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 
                
                if ratio < PINCH_ON:
                    pinching = True
                elif ratio > PINCH_OFF:
                    pinching = False
                if pinching:
                    cv2.putText(flipped_frame, "PINCH", (int(width/2), int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))

            cv2.line(flipped_frame, (int(thumb_x), int(thumb_y)), (int(index_x), int(index_y)), (255, 0, 0), 2)
            # cv2.putText(flipped_frame, f"distance: {str(int(pinch_dist))}", (420, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))   
        else:
            pinching = False

        # normal cv2 stuff
        cv2.putText(flipped_frame, f"detect: {int(total_time/count)}", (250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.putText(flipped_frame, f"fps: {fps}", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.imshow("window", flipped_frame)
        check = cv2.waitKey(1)

        if check == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

