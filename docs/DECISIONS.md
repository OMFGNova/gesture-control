## M0.1–M0.3 — Environment & Git setup (2026-10-12)

### Decisions
- **Python 3.11 via the `py` launcher**: `python` isn't on PATH globally (it hits the Store alias). Created the venv with `py -3.11 -m venv .venv`.
- **cmd, not PowerShell**: avoids PowerShell's execution-policy issues. VS Code's default terminal should be set to Command Prompt.
- **MediaPipe Tasks API (HandLandmarker), not `mp.solutions`**: `mediapipe.solutions` was removed in 0.10.31, so most online tutorials are outdated. Landmarks will be drawn manually with OpenCV.
- **No CUDA/PyTorch for M1**: not needed for MediaPipe hands. Reason to be confirmed in M1.1.
- **Git is local only for now**: GitHub remote to be added after M0.

### Alternatives rejected
- Pinning old mediapipe (≤0.10.21) to use `mp.solutions`: a dead-end API.
- Committing the venv: large, machine-specific, and replaced by `requirements.txt`.

### Concepts learned
- `-m` runs a module using *that specific* interpreter. `python -m pip` > plain `pip`, because it avoids installing into the wrong environment.
- `activate` puts `.venv\Scripts` at the front of PATH, and the first match wins. `deactivate` restores it.
- cmd paths: use `\`, not `/` (`/` means a switch). A leading `\` means the drive root. No leading slash means relative.
- `>` overwrites a file and `>>` appends. `pip freeze` pins dependencies too (e.g. numpy for OpenCV).
- `.gitignore` is committed and shared. It only affects untracked files, so write it before the first `git add`.
- Ignore generated, machine-specific, huge, or secret files. Commit what you wrote.
- LF vs CRLF warnings are harmless on Windows for now.
- Commit = local, push = remote.

### Next tasks
- [x] Fix Git identity: `git config --global user.name "..."` and `git commit --amend --reset-author --no-edit`. **Done when** `git log` shows your name.
- [x] Add `__pycache__/` and `.vscode/` to `.gitignore` and commit. **Done when** `git status` is clean after running a script.
- [x] Set VS Code's default terminal to Command Prompt. **Done when** a new terminal opens in cmd.
- [x] M0.4 `src/cam_check.py`: open camera, read one frame, print `isOpened()` and `frame.shape`. **Done when** it prints `True` plus a shape, and you can explain each number.
- [x] M0.5: live window loop, quit on `q`, release and destroy. **Done when** `q` closes cleanly with no hang.
- [ ] M0.6: mirror the frame and show FPS. **Done when** FPS is visible on the feed. Commit. (moved to 2026-10-14)

### Open questions
- Should `models/*.task` be committed or ignored? (decide in M1.2)
- When should the GitHub remote be created: after M0, or after M1?
- Which mediapipe version should be pinned? Check that Windows wheels exist for Python 3.11 before installing.

## M0.4–M0.5 — Camera check + live preview loop (2026-10-14)

### Decisions
- Two scripts: `src/cam_check.py` (one-frame diagnostic, rerun when the camera misbehaves) and `src/cam_live.py` (live loop that will grow into the pipeline).
- Fail fast: `raise SystemExit(...)` if `cap.isOpened()` is False; `break` if `ret` is False.
- Live loop uses `cv2.waitKey(1)`; quit on `q`; always `cap.release()` + `cv2.destroyAllWindows()`.

### Alternatives rejected
- Single script for both: loses the quick "camera or code?" diagnostic.
- `waitKey(0)`: blocks on every frame (frame-by-frame stepping, not live video).
- Printing the "camera not open" message and continuing: the program runs on with a dead camera.

### Concepts learned
- `frame.shape` = (height, width, channels) → (480, 640, 3). NumPy is rows first, while "640×480" is width × height.
- OpenCV frames are **BGR**, uint8 0–255. Grayscale is 2D: (H, W).
- `cap.read()` → (ret, frame). On failure frame is `None`, so check `ret` before use.
- `isOpened()` asks; `release()` frees.
- `waitKey(ms)`: waits for a key **and** drives window redraws; returns the key code.
- Read tracebacks from the **first** failure (`opened False`), not the last line.
- Debug hardware before code. "Camera index out of range" + `opened False` was a loose USB.
- Git: `--amend --reset-author --no-edit` (only before pushing); `.gitignore` doesn't untrack already-committed files (`git rm --cached`); a trailing `/` matches directories only.
- Use `git status` before `git add .`; prefer naming files.
- Claude Chat = learning/concepts/debugging. Claude Code = typing what I already understand ("hint only" if learning).

### Next tasks
- [ ] M0.6 Mirror the frame + show FPS in `cam_live.py`. **Done when** the preview moves like a mirror and an FPS number updates on screen.
- [ ] M1.1 Install `mediapipe` in the venv, add it to `requirements.txt`. **Done when** `python -c "import mediapipe; print(mediapipe.__version__)"` works.
- [ ] M1.2 Download the `hand_landmarker.task` model into `models/`. Decide whether to gitignore it. **Done when** the file exists and the decision is noted.
- [ ] M1.3 `src/hand_check.py`: one frame → BGR→RGB → `mp.Image` → `HandLandmarker.detect()` → print the number of hands and landmark 8 (index fingertip). **Done when** it prints 21 landmarks for a visible hand and I can explain the x/y/z values.
- [ ] M1.4 Draw landmarks on the live feed in `cam_live.py`. **Done when** dots track my hand in real time.

### Open questions
- Rename branch `master` → `main` before adding the GitHub remote?
- Pin versions in `requirements.txt` (e.g. `opencv-python==x.y.z`)?
- IMAGE vs VIDEO running mode for HandLandmarker in the live loop?

## 2026-10-15 — M0.6 → M1.4: Mirror/FPS, MediaPipe setup, live landmarks

### Decided
- **Mirror once, right after `cap.read()`** (`cv2.flip(frame, 1)`) and use the flipped frame for everything after, so on-screen direction = code direction.
- **FPS from the lap time between iterations** (`now - prev_time` with `time.perf_counter()`), so it covers the whole loop, including detection.
- **Dependencies:** hand-written `requirements.txt` listing direct imports only, pinned with `==` (`opencv-contrib-python`, `mediapipe`). Only one OpenCV package installed.
- **Model weights gitignored** (`models/`), with a download link in the README, so large future weights won't bloat the repo history.
- **Live loop uses VIDEO running mode** (`detect_for_video`, synchronous). Landmarker created once, before the loop. Timestamp = `int(now * 1000)`.
- **`num_hands=1` for gesture control** (2+ hands → conflicting commands, bystanders triggering actions, wasted FPS). Multi-hand only as a future demo option.

### Rejected
- `pip freeze` → dumps sub-dependencies and OS-specific pins.
- Unpinned requirements → future installs may break the API.
- Committing the `.task` file → acceptable at ~7 MB, but the habit matters for bigger models later.
- LIVE_STREAM mode → async callback adds complexity we don't need yet.
- Colab `draw_landmarks_on_image` snippet → no index labels, and `cv2_imshow` is Colab-only. Wrote my own drawing loop.
- Two OpenCV packages → both write to the same `cv2` folder and overwrite each other.

### Concepts learned
- `frame.shape` = (height, width, channels). OpenCV is BGR, and MediaPipe needs RGB. Skipping the conversion fails *silently* (worse accuracy, no error).
- `waitKey(1)` keeps the loop running and refreshes the window. `waitKey(0)` blocks until a keypress.
- `perf_counter()` only means something as a *difference* between two calls.
- `hand_landmarks` = list of hands → each a list of 21 points. x, y are normalised 0–1 (like YOLO labels), y=0 is the **top**, and z is rough depth relative to the wrist (noisy). `hand_world_landmarks` = metres, scale-invariant.
- Landmark indices 0–20 (0 wrist, 4 thumb tip, 8 index tip). Don't renumber.
- VIDEO mode uses the timestamp for **tracking**: it reuses the previous frame's hand location to skip the palm detector.
- Two-stage cost: detector ≈ fixed per frame, and the per-detection stage scales with the number of hands.
- Git: commits are local until a remote is added. `git rm --cached` untracks a file. Pushed files stay in history.

### Baselines
- No detection: ~30 FPS (readings up to 50 are jitter). Webcam caps at ~30.
- 1–2 hands: ~30 FPS (camera-bound, so this doesn't show the detection cost).
- 4 hands: ~20 FPS (~50 ms/frame, now detection-bound).

### Next tasks
- [ ] Set `num_hands=1` in `cam_live.py`. **Done when:** only one hand is drawn even with two in view.
- [ ] Time `detect_for_video` alone. **Done when:** the average detection ms is printed or shown, and noted here.
- [ ] Compute thumb–index distance (landmarks 4 & 8) and show it live. **Done when:** the number visibly drops when pinching.
- [ ] Make the pinch distance scale-invariant. **Done when:** the value stays roughly constant when moving an open hand closer to or further from the camera.

### Open questions
- How to normalise pinch distance: divide by a hand-size reference (e.g. wrist→middle-finger base), or use world landmarks?
- Pinch threshold: fixed number, or calibrated per user?
- Commit or gitignore `CLAUDE.md`? (Review its content as a recruiter would.)