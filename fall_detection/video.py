import cv2
from .config import VIDEO_SOURCE, VIDEO_OUTPUT, VIDEO_CODEC, VIDEO_FPS
from .config import VIDEO_SOURCE, VIDEO_OUTPUT, VIDEO_CODEC, VIDEO_FPS, VIDEO_DIR
import os


def get_video_capture():
    # Tentar algumas vezes antes de desistir
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            cap = cv2.VideoCapture(VIDEO_SOURCE)
            if not cap.isOpened():
                if attempt < max_attempts - 1:
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    continue
                raise Exception(f"Could not open camera {VIDEO_SOURCE}")

            # Configurar propriedades da câmera
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)

            # Verificar se as configurações foram aplicadas
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # Testar alguns frames
            for _ in range(3):
                ret, frame = cap.read()
                if not ret:
                    raise Exception("Failed to grab test frames")

            print(f"Camera initialized successfully: {
                  frame_width}x{frame_height} @ {fps}fps")
            return cap, frame_width, frame_height

        except Exception as e:
            if attempt == max_attempts - 1:
                raise Exception(f"Failed to initialize camera after {
                                max_attempts} attempts: {str(e)}")
            cap.release() if cap is not None else None


def get_video_writer(frame_width, frame_height):
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    video_output_path = os.path.join(VIDEO_DIR, VIDEO_OUTPUT)
    return cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*VIDEO_CODEC), VIDEO_FPS, (frame_width, frame_height))
