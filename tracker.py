from collections import deque
from dataclasses import dataclass
from typing import Optional
import time

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import numpy as np

MODEL_PATH = "hand_landmarker.task"

IDX_TIP = 8
IDX_MCP = 5
MID_TIP = 12
MID_MCP = 9
RING_TIP = 16
RING_MCP = 13
PINKY_TIP = 20
PINKY_MCP = 17
THUMB_TIP = 4

PINCH_THRESHOLD = 0.06
FIST_MARGIN = 0.0


@dataclass
class GestureState:
    gesture: str = "none"
    scroll_delta: float = 0.0


class HandTracker:
    def __init__(self, smoothing_window: int = 5):
        options = mp_vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._y_history: deque[float] = deque(maxlen=smoothing_window)
        self._prev_y: Optional[float] = None
        self.landmarks = None
        self.last_result = None
        self._start_ms = int(time.time() * 1000)

    def process(self, bgr_frame) -> GestureState:
        import cv2
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(time.time() * 1000) - self._start_ms

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        self.last_result = result

        state = GestureState()
        if not result.hand_landmarks:
            self._prev_y = None
            self._y_history.clear()
            self.landmarks = None
            return state

        lm = result.hand_landmarks[0]
        self.landmarks = lm

        if self._is_fist(lm):
            state.gesture = "fist"
        elif self._is_pinch(lm):
            state.gesture = "pinch"
        elif self._is_two_fingers_up(lm):
            state.gesture = "scroll"
            state.scroll_delta = self._compute_scroll_delta(lm)

        return state

    def _finger_up(self, lm, tip: int, mcp: int) -> bool:
        return lm[tip].y < lm[mcp].y

    def _finger_down(self, lm, tip: int, mcp: int) -> bool:
        return lm[tip].y > lm[mcp].y + FIST_MARGIN

    def _is_two_fingers_up(self, lm) -> bool:
        return (
            self._finger_up(lm, IDX_TIP, IDX_MCP)
            and self._finger_up(lm, MID_TIP, MID_MCP)
            and self._finger_down(lm, RING_TIP, RING_MCP)
            and self._finger_down(lm, PINKY_TIP, PINKY_MCP)
        )

    def _is_pinch(self, lm) -> bool:
        dx = lm[THUMB_TIP].x - lm[IDX_TIP].x
        dy = lm[THUMB_TIP].y - lm[IDX_TIP].y
        dist = (dx**2 + dy**2) ** 0.5
        hand_size = abs(lm[0].y - lm[MID_MCP].y) or 0.1
        return (dist / hand_size) < PINCH_THRESHOLD

    def _is_fist(self, lm) -> bool:
        pairs = [(IDX_TIP, IDX_MCP), (MID_TIP, MID_MCP), (RING_TIP, RING_MCP), (PINKY_TIP, PINKY_MCP)]
        return all(self._finger_down(lm, t, m) for t, m in pairs)

    def _compute_scroll_delta(self, lm) -> float:
        current_y = lm[IDX_TIP].y
        self._y_history.append(current_y)
        smoothed_y = float(np.mean(self._y_history))
        if self._prev_y is None:
            self._prev_y = smoothed_y
            return 0.0
        delta = self._prev_y - smoothed_y
        self._prev_y = smoothed_y
        return delta

    def close(self) -> None:
        self._landmarker.close()
