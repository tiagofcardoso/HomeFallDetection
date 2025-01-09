import cv2

TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_FROM = 'whatsapp:+14155238886'
TWILIO_TO = 'whatsapp:+14155238886'

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
