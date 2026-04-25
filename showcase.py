import time
import cv2

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # polegar
    (0, 5), (5, 6), (6, 7), (7, 8),            # indicador
    (5, 9), (9, 10), (10, 11), (11, 12),       # médio
    (9, 13), (13, 14), (14, 15), (15, 16),     # anular
    (13, 17), (17, 18), (18, 19), (19, 20),    # mínimo
    (0, 17), (5, 9), (9, 13), (13, 17),        # palma
]

GESTURE_COLORS = {
    "scroll": (0, 200, 255),
    "pinch":  (100, 255, 100),
    "fist":   (60, 60, 255),
    "none":   (180, 180, 180),
}

GESTURE_LABELS = {
    "scroll": "Scroll",
    "pinch":  "Minimize",
    "fist":   "Close",
    "none":   "",
}


def _draw_landmarks(frame, landmarks, color: tuple) -> None:
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], color, 2, cv2.LINE_AA)

    for i, pt in enumerate(pts):
        radius = 6 if i in (4, 8) else 4
        cv2.circle(frame, pt, radius, color, -1, cv2.LINE_AA)
        cv2.circle(frame, pt, radius, (255, 255, 255), 1, cv2.LINE_AA)


def run_showcase(tracker, cam_index: int, sensitivity: float) -> None:
    import actions

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        state = tracker.process(frame)

        if tracker.landmarks:
            _draw_landmarks(frame, tracker.landmarks, GESTURE_COLORS[state.gesture])

        label = GESTURE_LABELS[state.gesture]
        if label:
            cv2.putText(frame, label, (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                        GESTURE_COLORS[state.gesture], 3, cv2.LINE_AA)

        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now
        cv2.putText(frame, f"{fps:.0f} FPS", (frame.shape[1] - 100, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2, cv2.LINE_AA)

        cv2.imshow("Air Mouse — Showcase (q to quit)", frame)
        _dispatch(state, sensitivity)

        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


def _dispatch(state, sensitivity: float) -> None:
    import actions

    if state.gesture == "scroll" and abs(state.scroll_delta) > 0.002:
        actions.scroll(state.scroll_delta, sensitivity)
    elif state.gesture == "pinch":
        actions.minimize_window()
    elif state.gesture == "fist":
        actions.close_window()
