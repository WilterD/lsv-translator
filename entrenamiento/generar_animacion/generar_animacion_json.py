import json
import numpy as np
from scipy.spatial.transform import Rotation as R
import mediapipe as mp
import os

mp_holistic = mp.solutions.holistic
mp_hands = mp.solutions.hands

# Vectores base en T-pose
rest_directions = {
    'mixamorig:LeftArm': np.array([-1, 0, 0]),
    'mixamorig:LeftForeArm': np.array([-1, 0, 0]),
    'mixamorig:LeftHand': np.array([-1, 0, 0]),
    'mixamorig:RightArm': np.array([1, 0, 0]),
    'mixamorig:RightForeArm': np.array([1, 0, 0]),
    'mixamorig:RightHand': np.array([1, 0, 0]),
    'mixamorig:Spine': np.array([0, 1, 0]),
}

def calcular_rotacion(orig_vec, target_vec):
    orig = orig_vec / np.linalg.norm(orig_vec)
    target = target_vec / np.linalg.norm(target_vec)
    axis = np.cross(orig, target)
    angle = np.arccos(np.clip(np.dot(orig, target), -1.0, 1.0))
    if np.linalg.norm(axis) < 1e-6:
        return [0.0, 0.0, 0.0]
    axis = axis / np.linalg.norm(axis)
    rot = R.from_rotvec(axis * angle)
    return rot.as_euler('XYZ').tolist()

def generar_animacion(landmarks_path, salida_json, glosa="hola", fps=30):
    with open(landmarks_path, 'r') as f:
        frames_landmarks = json.load(f)

    LHip = mp_holistic.PoseLandmark.LEFT_HIP.value
    RHip = mp_holistic.PoseLandmark.RIGHT_HIP.value
    LShoulder = mp_holistic.PoseLandmark.LEFT_SHOULDER.value
    RShoulder = mp_holistic.PoseLandmark.RIGHT_SHOULDER.value
    LElbow = mp_holistic.PoseLandmark.LEFT_ELBOW.value
    LWrist = mp_holistic.PoseLandmark.LEFT_WRIST.value
    RElbow = mp_holistic.PoseLandmark.RIGHT_ELBOW.value
    RWrist = mp_holistic.PoseLandmark.RIGHT_WRIST.value

    animacion = {"glosa": glosa, "fps": fps, "frames": []}

    for frame_data in frames_landmarks:
        if 'pose' not in frame_data or not frame_data['pose']:
            continue  # Ignora frames sin pose

        pose = np.array(frame_data['pose'])
        pose_coords = np.stack([pose[:,0], pose[:,2], -pose[:,1]], axis=1)
        frame_bones = {}

        hip_center = (pose_coords[LHip] + pose_coords[RHip]) / 2
        shoulder_center = (pose_coords[LShoulder] + pose_coords[RShoulder]) / 2
        spine_vec = shoulder_center - hip_center
        frame_bones['mixamorig:Spine'] = calcular_rotacion(rest_directions['mixamorig:Spine'], spine_vec)

        v_upper_l = pose_coords[LElbow] - pose_coords[LShoulder]
        frame_bones['mixamorig:LeftArm'] = calcular_rotacion(rest_directions['mixamorig:LeftArm'], v_upper_l)

        v_fore_l = pose_coords[LWrist] - pose_coords[LElbow]
        frame_bones['mixamorig:LeftForeArm'] = calcular_rotacion(rest_directions['mixamorig:LeftForeArm'], v_fore_l)

        v_upper_r = pose_coords[RElbow] - pose_coords[RShoulder]
        frame_bones['mixamorig:RightArm'] = calcular_rotacion(rest_directions['mixamorig:RightArm'], v_upper_r)

        v_fore_r = pose_coords[RWrist] - pose_coords[RElbow]
        frame_bones['mixamorig:RightForeArm'] = calcular_rotacion(rest_directions['mixamorig:RightForeArm'], v_fore_r)

        # Detectar manos
        for hand, prefix in zip(['left_hand', 'right_hand'], ['Left', 'Right']):
            if hand in frame_data and frame_data[hand]:
                hand_lms = np.array(frame_data[hand])
                hand_coords = np.stack([hand_lms[:,0], hand_lms[:,2], -hand_lms[:,1]], axis=1)
                for i in range(1, 21-1):  # 20 landmarks, huesos entre pares
                    bone_name = f"mixamorig:{prefix}HandBone{i}"
                    v = hand_coords[i+1] - hand_coords[i]
                    frame_bones[bone_name] = calcular_rotacion(np.array([0, 0, 1]), v)

        animacion["frames"].append(frame_bones)

    os.makedirs(os.path.dirname(salida_json), exist_ok=True)
    with open(salida_json, 'w') as f:
        json.dump(animacion, f, indent=2)
    print(f"✅ Animación generada con {len(animacion['frames'])} frames → {salida_json}")

if __name__ == "__main__":
    entrada = "../landmarks_generados/hola_landmarks.json"
    salida = "../../backend/static/pose/hola.json"
    generar_animacion(entrada, salida, glosa="hola")
