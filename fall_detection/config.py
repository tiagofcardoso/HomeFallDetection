import cv2

TWILIO_ACCOUNT_SID = 'AC7d746a6c25ce284435434b65f7de6ea8'
TWILIO_AUTH_TOKEN = '559080bd8c51be7fffc0f92bb74cf6e5'
TWILIO_FROM = 'whatsapp:+14155238886'
TWILIO_TO = 'whatsapp:+351969683415'

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
