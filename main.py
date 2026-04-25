#!/usr/bin/env python3
import argparse
import sys
import time

import cv2

import actions
from tracker import HandTracker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Air Mouse — control your computer with hand gestures via webcam."
    )
    parser.add_argument("--showcase", action="store_true",
                        help="Show webcam window with hand landmark overlay")
    parser.add_argument("--cam", type=int, default=0,
                        help="Webcam device index (default: 0)")
    parser.add_argument("--sensitivity", type=float, default=30.0,
                        help="Scroll sensitivity multiplier (default: 30)")
    return parser.parse_args()


def run_silent(tracker: HandTracker, cam_index: int, sensitivity: float) -> None:
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Air Mouse running silently. Press Ctrl+C to stop.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            state = tracker.process(frame)

            if state.gesture == "scroll" and abs(state.scroll_delta) > 0.002:
                actions.scroll(state.scroll_delta, sensitivity)
            elif state.gesture == "pinch":
                actions.minimize_window()
            elif state.gesture == "fist":
                actions.close_window()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()


def main() -> None:
    args = parse_args()
    tracker = HandTracker()

    try:
        if args.showcase:
            from showcase import run_showcase
            run_showcase(tracker, args.cam, args.sensitivity)
        else:
            run_silent(tracker, args.cam, args.sensitivity)
    finally:
        tracker.close()


if __name__ == "__main__":
    main()
