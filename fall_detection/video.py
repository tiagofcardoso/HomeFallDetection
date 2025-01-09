import cv2
from .config import VIDEO_SOURCE, VIDEO_OUTPUT, VIDEO_CODEC, VIDEO_FPS
from .config import VIDEO_SOURCE, VIDEO_OUTPUT, VIDEO_CODEC, VIDEO_FPS, VIDEO_DIR
import os

def get_video_capture():
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cap, frame_width, frame_height

def get_video_writer(frame_width, frame_height):
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    video_output_path = os.path.join(VIDEO_DIR, VIDEO_OUTPUT)
    return cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), VIDEO_FPS, (frame_width, frame_height))
