# Hand-Gesture-Keyboard-Control-System


The **Hand Gesture Keyboard Control System** is a Python-based project that uses a webcam and Mediapipe's Hand Tracking module to control the mouse and keyboard through hand gestures. This project enables users to interact with their computer in an intuitive and touchless way.

## Features

- **Mouse Control**:
  - Move the mouse pointer using hand gestures.
  - Perform left-click, right-click, and double-click gestures.

- **Virtual Keyboard**:
  - Type using a virtual keyboard displayed on the screen.
  - Supports keys like letters, space, enter, and backspace.

- **Mode Switching**:
  - Switch between "mouse" and "keyboard" modes based on hand position.

## Requirements

- Python 3.7 or higher
- Webcam
- Libraries:
  - `opencv-python`
  - `mediapipe`
  - `pyautogui`
  - `numpy`
  - `pynput`

## Installation

1. Clone the repository or download the project files.
2. Install the required Python libraries:
   ```bash
   pip install opencv-python mediapipe pyautogui numpy pynput
