import cv2
import mediapipe as mp
from ultralytics import YOLO
from .video import get_video_capture, get_video_writer
from .alert import send_alert
import time


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


def is_falling(pose_landmarks, mp_pose):
    if not pose_landmarks:
        return False

    # Get necessary landmarks
    nose = pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
    left_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_ankle = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]

    # Calculate average positions
    hip_y = (left_hip.y + right_hip.y) / 2
    knee_y = (left_knee.y + right_knee.y) / 2
    ankle_y = (left_ankle.y + right_ankle.y) / 2

    # Check if the nose is below the hips, knees are close to the ground, and head is near the ground
    is_nose_below_hip = nose.y > hip_y
    is_knee_near_ground = knee_y > ankle_y * 0.9
    is_head_near_ground = nose.y > ankle_y * 0.9

    return is_head_near_ground


def detect_fall():
    try:
        model, mp_pose, pose = init_model()
        cap, frame_width, frame_height = get_video_capture()
        out = get_video_writer(frame_width, frame_height)

        fall_detected = False
        fall_start_time = None
        fall_duration_threshold = 1

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            person_detections = [
                det for det in results[0].boxes if det.cls == 0]

            for det in person_detections:
                x1, y1, x2, y2 = map(int, det.xyxy[0].tolist())
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pose_results = pose.process(rgb_frame)

                if is_falling(pose_results.pose_landmarks, mp_pose):
                    if not fall_detected:
                        fall_detected = True
                        fall_start_time = time.time()
                    elif time.time() - fall_start_time >= fall_duration_threshold:
                        cv2.putText(frame, "Fall Detected!", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        send_alert()
                else:
                    fall_detected = False
                    fall_start_time = None

            out.write(frame)
            cv2.imshow('Fall Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error in fall detection: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_fall()
