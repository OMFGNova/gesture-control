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

## 2026-10-15 — M1.5 → M2: Scale-invariant pinch detection

### Decided
- `num_hands=1`: only one hand is needed for control; fewer outputs to handle.
- Pinch = thumb tip (4) ↔ index tip (8) pixel distance **divided by palm length** (wrist 0 ↔ pinky MCP 17). Measured ratio: open ≈ 1.6 (near and far), pinched ≈ 0.15–0.19.
- `PINCH_THRESHOLD = 0.4` (named constant). Sits in the gap with margin against both missed and false pinches.
- Guard: if palm_len < 10 px, skip the ratio (show `--`) instead of faking a value.

### Rejected
- Raw pixel distance: breaks when the hand moves nearer or farther from the camera.
- `palm_len = 1` fallback: produces a fake "open" ratio.
- World landmarks: not rejected, just not tested yet (see open questions).

### Measurements
- `detect_for_video`: ~6 ms/frame. Loop runs ~30 FPS, so it's camera-bound (cap.read() blocks), not compute-bound.

### Concepts learned
- VIDEO mode tracks the hand: the palm detector runs only when there's no hand; otherwise only the landmark model runs on a crop. Timestamps must strictly increase.
- `time.perf_counter()` for timing (monotonic, high-res).
- Keep floats for maths, `int()` only for drawing/display.
- Bug pattern (hit 3×): variable assigned in one branch, used outside it → crash or stale value.
- Foreshortening: rotating the hand shrinks 2D palm length and distorts the ratio.
- `cv2.putText` origin = bottom-left of the text. Centring: x = W/2 − tw/2, y = H/2 + th/2.
- `git commit -am` stages tracked, modified files only; new files need `git add`.

### Next tasks
- [ ] Hysteresis: two thresholds (enter pinch < T_on, exit pinch > T_off, T_on < T_off) with a `pinching` state variable. Done when: holding fingers near the threshold no longer flickers.
- [ ] Refactor: move pinch logic into `pinch_ratio(landmarks, w, h)` that returns a float or None. Done when: the main loop calls one function and behaviour is unchanged.
- [ ] (Optional) World landmarks comparison: show the 4↔8 world distance (cm) next to the ratio; record open/pinched × near/far. Done when: table filled and a choice written here.
- [ ] M3 start: map pinch in/out to zoom. Done when: changing pinch distance zooms a document.

### Open questions
- Is rotation (foreshortening) a real problem in use? If so: max of two palm lengths (0→17, 0→9) or world landmarks?
- For zoom: trigger on pinch state (on/off) or on change in ratio over time?

## 2026-10-17 — M2.1: Pinch hysteresis + `pinch_ratio()` refactor

**Decided**
- Replaced single threshold (0.4) with hysteresis: `PINCH_ON = 0.35` (enter), `PINCH_OFF = 0.45` (exit). Ratio must cross the whole 0.10 gap to change state, so ±0.02 jitter can't flicker it.
- `pinching` state lives outside the loop; reset to `False` when no hand is detected and when `palm_len < 10` (safe default).
- Moved px conversion, palm_len guard and ratio maths into `pinch_ratio(landmarks, width, height)` → returns ratio, or `None` if palm too small.

**Rejected**
- Single threshold: flickers when ratio hovers near it.
- Keeping `pinching` on bad palm_len frames: rejected for safety; may cause zoom stutter if hand turns edge-on. Revisit in M3.
- Passing 4 points separately to `pinch_ratio`: caller would need to know landmark indices and handle px conversion; passing whole hand keeps that inside.

**Concepts learned**
- Ratio is scale-invariant because both distances scale by the same factor with depth.
- Guard failure without `else` → stale value from previous frame (silent bug), not just `NameError`.
- Hysteresis: low threshold to enter, high to exit, keep state in the gap.
- State that must persist across frames is initialised before the loop.
- Stale state when the input disappears → reset explicitly.
- Pure functions can be unit-tested with fake inputs (no webcam).

**Next tasks**
- [ ] Clean up: 4-space indentation, guard before computing `pinch_dist`, remove stale threshold comment. *Done when:* code reads consistently, no outdated comments.
- [ ] Webcam test. *Done when:* half-pinch label steady, full pinch/release toggles, hand leaving clears "PINCH".
- [ ] (Optional) `tests/test_pinch.py` with one fake-landmark case (expect 0.3) and one `None` case. *Done when:* `pytest` passes.
- [ ] M3: design pinch → zoom (what drives zoom amount, how to send zoom to the OS).

**Open questions**
- Does the reset-on-small-palm cause noticeable stutter during zoom?
- Should zoom be driven by pinch state (on/off) or by *change* in ratio while pinching?

## M3.0: Pinch → zoom (discrete), signal fixes (2026-10-17)

### Decisions
- **Discrete zoom first, continuous later.** Zoom fires on the pinch-state *edge*: open→pinch = ZOOM OUT, pinch→open = ZOOM IN. Edge detection is reused later for fist↔open music control. Continuous zoom (Δratio while "engaged") is planned as M3 v2.
- **Switched to 3D world landmarks** (`hand_world_landmarks`, metres) for `pinch_ratio_3d`. In 2D, `palm_len` collapsed when the hand tilted, so the ratio spiked. Measured with 3D: steady pinch ~0.13–0.15, open ~3.3–3.5, occasional spikes to 1–2.
- **Thresholds from data:** PINCH_ON = 0.25, PINCH_OFF = 2.5, plus a **debounce** (N = 3 consecutive frames) to kill 1–2 frame spikes. Guard: `palm_len < 0.02 m → None`.
- **Unknown state:** `pinch = None` at start and on hand loss / `ratio is None`. The first confirmed state is set silently (no zoom). `prev_status` removed, since the debounced flip *is* the edge.
- **OS input:** `pyautogui` hotkeys (Ctrl+= / Ctrl+-), not shown working yet.

### Rejected
- **Zoom while `pinching` is True (state-driven):** can only zoom in one direction.
- **Raising PINCH_OFF alone to dodge spikes:** treats the symptom and leaves a small margin to a real open.
- **`keyboard` library:** global low-level hook on Windows, may need admin, poorly maintained.
- **Splitting edge detection out of the threshold branches *without* tracking why the state changed:** a lost hand would fire a false ZOOM IN. Superseded by the `None` state.

### Concepts to understand
- Hysteresis dead band vs. landmark noise; picking thresholds from measured min/max with margins.
- 2D normalised landmarks (fractions of the image) vs. 3D world landmarks (metres): why `width`/`height` aren't needed in 3D.
- Debounce = N consecutive "yes" frames; any "no" resets it (stops spikes accumulating).
- `not None` is True, so check `is None` before any `not pinch` logic.

### Next tasks
- [ ] Implement the `None` state (code from the 2026-10-17 chat). **Done when:** a hand entering already pinched prints nothing.
- [ ] Re-run the full test. **Done when:** wiggly pinch → no print; pinch → one ZOOM OUT; open → one ZOOM IN; hand leaves mid-pinch → no print.
- [ ] `scripts/test_zoom.py`: a standalone pyautogui zoom in/out. **Done when:** a browser page zooms in and back out.
- [ ] Swap the prints for hotkeys. **Done when:** pinch/open zooms a PDF or browser page.

### Open questions
- Should the first state out of `None` also be debounced? (A spike on entry → wrong start state → false zoom.)
- Lower PINCH_OFF toward ~2.0 now that the debounce exists?
- Remove the leftover 2D `pinch_ratio` and duplicate landmark code in the loop?