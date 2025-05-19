import cv2
import mediapipe as mp
import json
import os

mp_holistic = mp.solutions.holistic

def extraer_landmarks_desde_video(video_path, output_path):
    holistic = mp_holistic.Holistic(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(video_path)
    frames_landmarks = []
    frame_count = 0
    valid_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image_rgb)

        pose_lms = results.pose_world_landmarks
        left_hand_lms = results.left_hand_landmarks
        right_hand_lms = results.right_hand_landmarks

        if pose_lms:
            valid_frames += 1
            frame_data = {
                'pose': [(lm.x, lm.y, lm.z) for lm in pose_lms.landmark],
                'left_hand': [(lm.x, lm.y, lm.z) for lm in left_hand_lms.landmark] if left_hand_lms else None,
                'right_hand': [(lm.x, lm.y, lm.z) for lm in right_hand_lms.landmark] if right_hand_lms else None
            }
            frames_landmarks.append(frame_data)

    cap.release()
    holistic.close()

    if frames_landmarks:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(frames_landmarks, f, indent=2)
        print(f"✅ Landmarks guardados en: {output_path}")
        print(f"🟢 Frames válidos: {valid_frames} de {frame_count}")
    else:
        print("⚠️ No se detectaron landmarks válidos en ningún frame.")
        print("👉 Verifica que el video tenga buena iluminación y visibilidad del cuerpo y manos.")

if __name__ == "__main__":
    video = "entrenamiento/videos/hola.mp4"
    salida = "../landmarks_generados/hola_landmarks.json"
    extraer_landmarks_desde_video(video, salida)
