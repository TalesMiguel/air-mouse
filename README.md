# Air Mouse

Control your computer with hand gestures captured via webcam — no need to touch the keyboard or mouse.

## Gestures

| Gesture | Action |
|---------|--------|
| ☝️✌️ Two fingers moving up | Scroll (up/down based on direction) |
| 🤏 Pinch (thumb + index finger touch) | Minimize active window |
| ✊ Closed fist | Close active window |

> **Warning:** the close window gesture has a 2-second debounce to prevent accidents.

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Linux: `xdotool` installed

```bash
# Linux
sudo apt install xdotool
```

## Installation

```bash
git clone <repo>
cd air-mouse

uv venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

uv pip install -r requirements.txt
```

## Usage

```bash
# Silent mode (background, no window)
python main.py

# Showcase mode (window with landmark overlay)
python main.py --showcase

# Options
python main.py --cam 1          # use camera device index 1
python main.py --sensitivity 50 # faster scrolling (default: 30)
```

Press `q` or `ESC` to exit showcase mode.  
Press `Ctrl+C` to exit silent mode.

## How it works

The project uses [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) to detect 21 hand landmarks in real-time via webcam. Three gestures are identified based on these landmarks:

- **Scroll**: index and middle fingers raised and moving — the vertical delta is converted to page scroll.
- **Pinch**: distance between thumb and index finger below a threshold → `xdotool key super+Down`.
- **Fist**: all finger tips below their respective knuckles → `xdotool key alt+F4`.

In showcase mode, the landmarks are drawn over the webcam feed with colors indicating the active gesture.
