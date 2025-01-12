import cv2
import mediapipe as mp
from ultralytics import YOLO
from .video import get_video_capture, get_video_writer
from .alert import send_alert
from .config import VIDEO_SOURCE
import time
import numpy as np
import traceback


def init_model():
    model = YOLO("yolo11x.pt")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return model, mp_pose, pose


def calculate_angles(a, b, c):
    """Calcula o ângulo entre três pontos."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)


def calculate_velocity(current_pos, prev_pos, fps):
    """Calcula a velocidade de movimento."""
    if prev_pos is None:
        return 0
    return np.linalg.norm(np.array(current_pos) - np.array(prev_pos)) * fps


def is_falling(pose_landmarks, mp_pose, prev_landmarks=None, fps=30):
    if not pose_landmarks:
        return False, 0

    # Extrair landmarks principais
    landmarks = {
        'nose': pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE],
        'left_shoulder': pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER],
        'right_shoulder': pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER],
        'left_hip': pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP],
        'right_hip': pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP],
        'left_knee': pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE],
        'right_knee': pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE],
        'left_ankle': pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE],
        'right_ankle': pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    }

    # Calcular posições médias
    mid_shoulder = [(landmarks['left_shoulder'].x + landmarks['right_shoulder'].x)/2,
                    (landmarks['left_shoulder'].y + landmarks['right_shoulder'].y)/2]
    mid_hip = [(landmarks['left_hip'].x + landmarks['right_hip'].x)/2,
               (landmarks['left_hip'].y + landmarks['right_hip'].y)/2]
    mid_ankle = [(landmarks['left_ankle'].x + landmarks['right_ankle'].x)/2,
                 (landmarks['left_ankle'].y + landmarks['right_ankle'].y)/2]

    # 1. Verificar se a pessoa está no chão
    is_on_ground = False
    ground_score = 0

    # Verificar altura em relação ao chão (usando tornozelos como referência)
    body_parts_near_ground = 0
    for part in ['nose', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']:
        if abs(landmarks[part].y - mid_ankle[1]) < 0.3:  # Próximo ao nível do chão
            body_parts_near_ground += 1
            ground_score += 20

    is_on_ground = body_parts_near_ground >= 2

    # 2. Verificar orientação do corpo
    vertical_alignment = abs(mid_shoulder[1] - mid_hip[1])
    is_horizontal = vertical_alignment < 0.15

    if is_horizontal:
        ground_score += 30

    # 3. Verificar movimento
    if prev_landmarks is not None:
        movement = np.linalg.norm(
            np.array([landmarks['nose'].y]) - prev_landmarks)
        is_still = movement < 0.02  # Threshold baixo para detectar imobilidade
        if is_still:
            ground_score += 25

    # Retornar score para avaliação de imobilidade
    return is_on_ground and is_horizontal, ground_score


def detect_fall():
    cap = None
    out = None
    prev_nose_pos = None
    immobility_start_time = None
    immobility_duration = 5.0  # 5 segundos de imobilidade
    fall_scores_history = []

    try:
        print("Initializing camera...")
        cap, frame_width, frame_height = get_video_capture()

        print("Initializing model...")
        model, mp_pose, pose = init_model()

        print("Setting up video writer...")
        out = get_video_writer(frame_width, frame_height)

        fall_detected = False
        person_recovered = False

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)

            if len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    if box.cls.cpu().numpy()[0] == 0:  # pessoa
                        conf = box.conf.cpu().numpy()[0]
                        if conf > 0.5:
                            x1, y1, x2, y2 = map(
                                int, box.xyxy.cpu().numpy()[0])

                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pose_results = pose.process(rgb_frame)

                            if pose_results.pose_landmarks:
                                current_nose_pos = np.array([
                                    pose_results.pose_landmarks.landmark[
                                        mp_pose.PoseLandmark.NOSE].y
                                ])

                                is_on_ground, ground_score = is_falling(
                                    pose_results.pose_landmarks,
                                    mp_pose,
                                    prev_nose_pos
                                )

                                # Verificar imobilidade no chão
                                if is_on_ground and ground_score > 60:
                                    if immobility_start_time is None:
                                        immobility_start_time = time.time()
                                        status_text = "Possible fall detected..."
                                    else:
                                        immobility_time = time.time() - immobility_start_time
                                        if immobility_time >= immobility_duration:
                                            if not fall_detected:
                                                fall_detected = True
                                                try:
                                                    send_alert(
                                                        "ALERT: Person has fallen and is not moving!")
                                                except Exception as e:
                                                    print(
                                                        f"Alert not sent: {str(e)}")
                                            # Novo código para alertas periódicos
                                            elif immobility_time % 30 == 0:  # A cada 30 segundos
                                                try:
                                                    send_alert(f"ALERT: Person still on ground for {
                                                               int(immobility_time)} seconds!")
                                                except Exception as e:
                                                    print(
                                                        f"Alert not sent: {str(e)}")

                                            status_text = f"FALL DETECTED! Immobile for {
                                                int(immobility_time)}s"
                                            cv2.rectangle(
                                                frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                        else:
                                            status_text = f"Monitoring... {
                                                int(immobility_time)}s"
                                else:
                                    immobility_start_time = None
                                    if fall_detected:
                                        fall_detected = False
                                        person_recovered = True
                                        try:
                                            send_alert(
                                                "UPDATE: Person has moved from ground position")
                                        except Exception as e:
                                            print(f"Alert not sent: {str(e)}")
                                    status_text = "Monitoring..."
                                    cv2.rectangle(
                                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                                # Mostrar status no canto superior direito
                                text_size = cv2.getTextSize(
                                    status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
                                text_x = frame.shape[1] - text_size[0] - 10
                                text_y = text_size[1] + 20

                                # Definir cor do fundo baseado no status
                                if fall_detected:
                                    bg_color = (0, 0, 255)  # Vermelho
                                    text_color = (255, 255, 255)  # Branco
                                elif immobility_start_time is not None:
                                    bg_color = (0, 255, 255)  # Amarelo
                                    text_color = (0, 0, 0)  # Preto
                                else:
                                    bg_color = (0, 255, 0)  # Verde
                                    text_color = (0, 0, 0)  # Preto

                                # Desenhar fundo e texto
                                cv2.rectangle(frame,
                                              (text_x - 10, text_y -
                                               text_size[1] - 10),
                                              (text_x +
                                               text_size[0] + 10, text_y + 10),
                                              bg_color,
                                              -1)
                                cv2.putText(frame, status_text,
                                            (text_x, text_y),
                                            cv2.FONT_HERSHEY_SIMPLEX,
                                            0.9, text_color, 2)

                                prev_nose_pos = current_nose_pos

            cv2.imshow('Fall Detection', frame)
            out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        if cap is not None:
            cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_fall()
