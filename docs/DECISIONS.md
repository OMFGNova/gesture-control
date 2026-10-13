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
- [ ] Fix Git identity: `git config --global user.name "..."` and `git commit --amend --reset-author --no-edit`. **Done when** `git log` shows your name.
- [ ] Add `__pycache__/` and `.vscode/` to `.gitignore` and commit. **Done when** `git status` is clean after running a script.
- [ ] Set VS Code's default terminal to Command Prompt. **Done when** a new terminal opens in cmd.
- [ ] M0.4 `src/cam_check.py`: open camera, read one frame, print `isOpened()` and `frame.shape`. **Done when** it prints `True` plus a shape, and you can explain each number.
- [ ] M0.5: live window loop, quit on `q`, release and destroy. **Done when** `q` closes cleanly with no hang.
- [ ] M0.6: mirror the frame and show FPS. **Done when** FPS is visible on the feed. Commit.

### Open questions
- Should `models/*.task` be committed or ignored? (decide in M1.2)
- When should the GitHub remote be created: after M0, or after M1?
- Which mediapipe version should be pinned? Check that Windows wheels exist for Python 3.11 before installing.