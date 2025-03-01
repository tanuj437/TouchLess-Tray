import cv2
import mediapipe as mp
import time
from hand_tracking import HandTracker

class CameraFeed:
    def __init__(self, cart_manager):
        self.cart_manager = cart_manager
        self.cap = cv2.VideoCapture(0)
        self.hand_tracker = HandTracker()

    def start_camera_loop(self, label):
        """Continuously update the camera feed."""
        def update():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                index_finger_pos = self.hand_tracker.detect_hand(frame)
                self.cart_manager.process_gesture(index_finger_pos)
                cv2.imshow("Camera Feed", frame)
            
            label.after(10, update)

        update()
