import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput.mouse import Button as MouseButton, Controller
from pynput.keyboard import Controller as KeyboardController
import time

# Initialize Mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
draw = mp.solutions.drawing_utils

# Get screen dimensions
screen_width, screen_height = pyautogui.size()
mouse = Controller()
keyboard = KeyboardController()

# Virtual Keyboard Setup
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["Space", "Enter", "Back"]]  # Added Space, Enter, and Backspace keys
finalText = ""

class KeyButton:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(KeyButton([100 * j + 50, 100 * i + 50], key))

# Utility Functions
def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    return angle

def get_distance(landmark_list):
    if len(landmark_list) < 2:
        return 0
    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
    x1, y1 = int(x1 * screen_width), int(y1 * screen_height)
    x2, y2 = int(x2 * screen_width), int(y2 * screen_height)
    return np.hypot(x2 - x1, y2 - y1)

# Function to detect mode (mouse or keyboard)
def detect_mode(landmarks_list, previous_wrist_y):
    if len(landmarks_list) < 21:
        return None, previous_wrist_y

    wrist_y = landmarks_list[0][1]  # Y-coordinate of the wrist

    if wrist_y < previous_wrist_y - 0.05:  # Threshold for upward movement
        return "keyboard", wrist_y

    if wrist_y > previous_wrist_y + 0.05:  # Threshold for downward movement
        return "mouse", wrist_y

    return None, wrist_y

# Function to move the mouse pointer
def move_mouse(index_finger_tip):
    if index_finger_tip is not None:
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y * screen_height)
        pyautogui.moveTo(x, y, duration=0.1)

# Function to detect gestures for mouse control
def detect_mouse_gestures(frame, landmarks_list, processed):
    if len(landmarks_list) >= 21:
        index_finger_tip = None
        if processed.multi_hand_landmarks:
            hand_landmarks = processed.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]

        thumb_index_dist = get_distance([landmarks_list[4], landmarks_list[8]])

        if thumb_index_dist < 250:
            move_mouse(index_finger_tip)

        elif is_left_click(landmarks_list, thumb_index_dist):
            mouse.press(MouseButton.left)
            mouse.release(MouseButton.left)
            cv2.putText(frame, "left click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif is_right_click(landmarks_list, thumb_index_dist):
            mouse.press(MouseButton.right)
            mouse.release(MouseButton.right)
            cv2.putText(frame, "right click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        elif is_double_click(landmarks_list, thumb_index_dist):
            pyautogui.doubleClick()
            cv2.putText(frame, "double click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

# Helper functions for gesture detection
def is_left_click(landmarks_list, thumb_index_dist):
    angle = get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    return angle < 50 and thumb_index_dist > 250

def is_right_click(landmarks_list, thumb_index_dist):
    angle = get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12])
    return angle < 50 and thumb_index_dist > 250

def is_double_click(landmarks_list, thumb_index_dist):
    angle1 = get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])
    angle2 = get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12])
    return angle1 < 70 and angle2 < 70 and thumb_index_dist < 300

# Function to draw the virtual keyboard
def draw_keyboard(frame, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(frame, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return frame

# Function to detect keyboard input
def detect_keyboard_input(frame, landmarks_list, buttonList, finalText, last_key_press_time):
    if len(landmarks_list) < 21:
        return finalText, last_key_press_time

    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        if x < landmarks_list[8][0] * frame.shape[1] < x + w and y < landmarks_list[8][1] * frame.shape[0] < y + h:
            cv2.rectangle(frame, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
            cv2.putText(frame, button.text, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

            dist = get_distance([landmarks_list[8], landmarks_list[12]])
            if dist < 30 and (time.time() - last_key_press_time) > 0.3:
                if button.text == "Back":
                    finalText = finalText[:-1]
                elif button.text == "Space":
                    finalText += " "
                elif button.text == "Enter":
                    finalText += "\n"
                else:
                    finalText += button.text
                last_key_press_time = time.time()

    cv2.rectangle(frame, (50, 550), (1000, 600), (175, 0, 175), cv2.FILLED)
    cv2.putText(frame, finalText, (60, 580),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    return finalText, last_key_press_time

# Main function
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    current_mode = None
    finalText = ""
    last_key_press_time = 0
    previous_wrist_y = 0.5

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            landmarks_list = []

            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

                for lm in hand_landmarks.landmark:
                    landmarks_list.append([lm.x, lm.y])

                mode, previous_wrist_y = detect_mode(landmarks_list, previous_wrist_y)
                if mode:
                    current_mode = mode

                if current_mode == "mouse":
                    detect_mouse_gestures(frame, landmarks_list, processed)
                elif current_mode == "keyboard":
                    frame = draw_keyboard(frame, buttonList)
                    finalText, last_key_press_time = detect_keyboard_input(frame, landmarks_list, buttonList, finalText, last_key_press_time)

            cv2.imshow('Hand Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
