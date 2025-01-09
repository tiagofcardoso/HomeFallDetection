import cv2
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')
TWILIO_TO = os.getenv('TWILIO_TO')

VIDEO_SOURCE = 2  # default to external webcam
try:
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        VIDEO_SOURCE = 0  # fallback to onboard webcam
        cap = cv2.VideoCapture(VIDEO_SOURCE)
    cap.release()
except ImportError:
    VIDEO_SOURCE = 0

VIDEO_DIR = 'fall_detection/videos'
VIDEO_OUTPUT = 'falldown.mp4'
VIDEO_CODEC = 'MJPG'
VIDEO_FPS = 60
