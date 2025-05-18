import cv2
import mediapipe as mp
import numpy as np
import json
import os

# Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False)
mp_drawing = mp.solutions.drawing_utils

# Diccionario de huesos simplificados (puedes ampliarlo según la estructura Mixamo)
bone_map = {
    "LeftArm": ("LEFT_SHOULDER", "LEFT_ELBOW"),
    "LeftForeArm": ("LEFT_ELBOW", "LEFT_WRIST"),
    "RightArm": ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    "RightForeArm": ("RIGHT_ELBOW", "RIGHT_WRIST"),
    "Spine": ("LEFT_HIP", "LEFT_SHOULDER"),
    "Neck": ("LEFT_SHOULDER", "NOSE"),
}

POSE_CONNECTIONS = mp_pose.PoseLandmark

def get_angle_from_points(a, b):
    """Devuelve vector ángulo simplificado (en radianes) desde punto a hacia b."""
    v = np.array(b) - np.array(a)
    theta_x = np.arctan2(v[1], v[2])
    theta_y = np.arctan2(v[0], v[2])
    theta_z = np.arctan2(v[1], v[0])
    return [float(theta_x), float(theta_y), float(theta_z)]

def extract_rotations_from_frame(landmarks):
    rotations = {}
    for bone, (start, end) in bone_map.items():
        if hasattr(POSE_CONNECTIONS, start) and hasattr(POSE_CONNECTIONS, end):
            p1 = landmarks[getattr(POSE_CONNECTIONS, start).value]
            p2 = landmarks[getattr(POSE_CONNECTIONS, end).value]
            if p1.visibility > 0.5 and p2.visibility > 0.5:
                pos1 = [p1.x, p1.y, p1.z]
                pos2 = [p2.x, p2.y, p2.z]
                rotations[f"mixamorig7:{bone}"] = get_angle_from_points(pos1, pos2)
    return rotations

def process_video(path, output_path="pose_output.json"):
    cap = cv2.VideoCapture(path)
    selected_frame = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        if results.pose_landmarks:
            selected_frame = results.pose_landmarks.landmark
            break  # tomamos solo el primer frame válido
    cap.release()

    if selected_frame:
        pose_data = extract_rotations_from_frame(selected_frame)
        with open(output_path, "w") as f:
            json.dump(pose_data, f, indent=2)
        print("Pose guardada en", output_path)
    else:
        print("No se detectó ninguna pose.")

# Ejemplo de uso
# process_video("videos/hola.mp4", "poses/hola.json")
