# Gesture Control

Control your computer with webcam hand gestures (zoom, scroll, switch tabs, pause/resume music), using OpenCV + MediaPipe.

## Setup (Windows, cmd)

```
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
mkdir models
```

Download `hand_landmarker.task` from the [MediaPipe Hand Landmarker models page](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/index#models) and place it in `models/`.

## Run

```
python cam_live.py
```

Press `q` to quit.