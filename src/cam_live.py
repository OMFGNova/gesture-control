import cv2
import time
import mediapipe as mp
import math
import pyautogui

# HELPER FUNCTIONS
def pinch_ratio_3d(landmarks):
    """Ratio between distance of tip of index and tip of thumb

    Args:
        landmarks: landmark results from detection of hand using mediapipe

    Returns:
        float: ratio
    """
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

def is_curled(landmarks, tip, knuckle):
    """Check finger is curled
    
    Args:
        landmarks: landmark results from detection of hand using mediapipe
        tip: index of tip of finger
        knuckle: index of knuckle of finger

    Returns:
        Boolean
    """
    wrist = (landmarks[0].x, landmarks[0].y, landmarks[0].z)

    tip = (landmarks[tip].x, landmarks[tip].y, landmarks[tip].z)
    knuckle = (landmarks[knuckle].x, landmarks[knuckle].y, landmarks[knuckle].z)

    wrist_tip = math.dist(wrist, tip)
    wrist_knuckle = math.dist(wrist, knuckle)
 
    return True if wrist_tip < wrist_knuckle else False
# HELPER FUNCTIONS

# Path to model 
model_path = r"./models/hand_landmarker.task"

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
clutch_on = False
ref = None
ZOOM_IN_STEP = 1.25
ZOOM_OUT_STEP = 1/ZOOM_IN_STEP

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
            thumb_x, thumb_y = (hand_landmarker_result.hand_landmarks[0][4].x * width, hand_landmarker_result.hand_landmarks[0][4].y * height)
            index_x, index_y = (hand_landmarker_result.hand_landmarks[0][8].x * width, hand_landmarker_result.hand_landmarks[0][8].y * height)

            # check if the clutch condition is true (pinky, ring, middle curled)
            pinky, ring = is_curled(hand_landmarker_result.hand_world_landmarks[0], 20, 17), is_curled(hand_landmarker_result.hand_world_landmarks[0], 16, 13)
            middle, index = is_curled(hand_landmarker_result.hand_world_landmarks[0], 12, 9), is_curled(hand_landmarker_result.hand_world_landmarks[0], 8, 5)
            clutch = pinky and ring and middle and not index
            fist = pinky and ring and middle and index

            # check state of clutch, (on or off)
            if clutch_on:
                # if clutch_on True, when pinky ring and middle not curled it will be turned off
                if not (pinky and ring and middle):
                    clutch_on = False
            else:
                # if clutch_on False, when pinky ring and middle and not index true it will turn True
                if clutch:
                    clutch_on = True

            # if clutch_on true, clutch print else if fist true print fist etc
            if clutch_on:
                cv2.putText(flipped_frame, f"clutch", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 
            elif fist:
                cv2.putText(flipped_frame, f"fist", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 
            else:
                cv2.putText(flipped_frame, f"-", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

            # calculats dist from bottom pinky to wrist and pink distance from index to thumb
            ratio = pinch_ratio_3d(hand_landmarker_result.hand_world_landmarks[0])

            if ratio is not None:
                cv2.putText(flipped_frame, f"ratio: {ratio:.2f}", (420, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 
                if clutch_on and ref is None:
                    ref = ratio
                elif not clutch_on:
                    ref = None

                if ref is None:
                    cv2.putText(flipped_frame, f"ratio/ref: -", (220, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))     
                    cv2.putText(flipped_frame, f"ref: -", (420, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 
                else:
                    change = ratio/ref

                    if change > ZOOM_IN_STEP:
                        ref = ratio
                        print("ZOOM IN")
                        pyautogui.hotkey("ctrl", "+")
                    elif change < ZOOM_OUT_STEP:
                        ref = ratio
                        print("ZOOM OUT")
                        pyautogui.hotkey("ctrl", "-")

                    cv2.putText(flipped_frame, f"ratio/ref: {change:.2f}", (220, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))     
                    cv2.putText(flipped_frame, f"ref: {ref:.2f}", (420, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0)) 

            cv2.line(flipped_frame, (int(thumb_x), int(thumb_y)), (int(index_x), int(index_y)), (255, 0, 0), 2)

        else:
            clutch_on = False
            ref = None

        # normal cv2 stuff
        cv2.putText(flipped_frame, f"detect: {int(total_time/count)}", (250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.putText(flipped_frame, f"fps: {fps}", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
        cv2.imshow("window", flipped_frame)
        check = cv2.waitKey(1)

        if check == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

