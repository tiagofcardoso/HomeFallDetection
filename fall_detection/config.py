import cv2
import os
from dotenv import load_dotenv

# Garantir que o .env seja carregado
load_dotenv()

# Twilio Configuration with validation
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')
TWILIO_TO = os.getenv('TWILIO_TO')

# Validar configurações do Twilio
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO]):
    print("\nWarning: Twilio credentials not fully configured")
    print("Please set the following environment variables in your .env file:")
    if not TWILIO_ACCOUNT_SID:
        print("- TWILIO_ACCOUNT_SID")
    if not TWILIO_AUTH_TOKEN:
        print("- TWILIO_AUTH_TOKEN")
    if not TWILIO_FROM:
        print("- TWILIO_FROM")
    if not TWILIO_TO:
        print("- TWILIO_TO")
    print("\nAlert messages will not be sent until these are configured.\n")

# Modificar as configurações de vídeo
VIDEO_SETTINGS = {
    'WIDTH': 640,
    'HEIGHT': 480,
    'FPS': 30,
    'SOURCE': 2,  # câmera externa
    'FALLBACK_SOURCE': 0  # câmera integrada como fallback
}

# Modificar a parte de detecção da câmera
VIDEO_SOURCE = VIDEO_SETTINGS['SOURCE']
try:
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"External camera not found, falling back to internal camera")
        VIDEO_SOURCE = VIDEO_SETTINGS['FALLBACK_SOURCE']
    cap.release()
except Exception:
    print(f"Error accessing external camera, falling back to internal camera")
    VIDEO_SOURCE = VIDEO_SETTINGS['FALLBACK_SOURCE']

VIDEO_DIR = 'fall_detection/videos'
VIDEO_OUTPUT = 'falldown.mp4'
VIDEO_CODEC = 'MJPG'
VIDEO_FPS = 60

# Adicionar configurações de detecção
FALL_DETECTION_SETTINGS = {
    'CONFIDENCE_THRESHOLD': 0.5,
    'FALL_DURATION_THRESHOLD': 1.0,     # segundos
    'HEIGHT_CHANGE_THRESHOLD': 0.3,     # % da altura do frame
    'HORIZONTAL_THRESHOLD': 0.15,       # diferença máxima entre ombro e quadril
    'FETAL_POSITION_THRESHOLD': 0.2,    # distância máxima entre joelho e quadril
    'HISTORY_SIZE': 10                  # frames para análise
}
