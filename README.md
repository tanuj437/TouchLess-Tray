# Touchless Tray 🛒🤖
## Overview
Touchless Tray is an system that enables users to interact with a virtual cart using hand gestures. It leverages computer vision techniques for gesture recognition, allowing for a seamless and contactless shopping experience.

## Features
✅ Real-time hand tracking using OpenCV and MediaPipe.

✅ Gesture-based cart management (add/remove items).

✅ Smooth integration with a GUI for an interactive experience.

✅ Modular and scalable code structure.

## Tech Stack
Python 🐍

OpenCV 🖼️ (Computer Vision)

MediaPipe 🖐️ (Hand Tracking)

Tkinter/PyQt (GUI)

Multithreading (Efficient Processing)


## Installation
- Clone the repository:
```
git clone https://github.com/your-username/touchless-tray.git
cd touchless-tray
```
- Install dependencies:
```
pip install -r requirements.txt
```
- Run the application:
```
python main.py
```

## File Structure
```
📂 Touchless-Tray  
│── 📜 main.py              # Entry point of the application  
│── 📜 ui.py                # Handles the GUI components  
│── 📜 camera_feed.py       # Manages camera input and gesture tracking  
│── 📜 cart_manager.py      # Processes gestures and updates the cart  
│── 📜 utils.py             # Utility functions  
│── 📜 requirements.txt     # Dependencies  
└── 📜 README.md            # Documentation
```

## Usage
Launch the application.

Position your hand in front of the camera.

Use predefined gestures to add or remove items from the cart.
