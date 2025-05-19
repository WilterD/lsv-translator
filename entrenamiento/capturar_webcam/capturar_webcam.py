import cv2
import mediapipe as mp
import json
import os

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def capturar_sec_al_presionar(glosa="hola"):
    holistic = mp_holistic.Holistic(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(0)
    frames_landmarks = []
    capturando = False

    print("▶️ Presiona 'i' para iniciar, 'f' para finalizar y guardar, 'ESC' para salir sin guardar.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image_rgb)

        frame_show = frame.copy()
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame_show, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(frame_show, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(frame_show, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        estado = "CAPTURANDO..." if capturando else "ESPERANDO"
        cv2.putText(frame_show, f"Estado: {estado}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if capturando else (128, 128, 128), 2)

        cv2.imshow("Captura LSV", frame_show)
        key = cv2.waitKey(5) & 0xFF

        if key == ord('i'):
            print("✅ Iniciando captura...")
            capturando = True

        elif key == ord('f'):
            print("🛑 Finalizando captura...")
            capturando = False
            break

        elif key == 27:  # ESC
            print("❌ Cancelado por el usuario.")
            cap.release()
            cv2.destroyAllWindows()
            holistic.close()
            return

        if capturando and results.pose_world_landmarks:
            pose_lms = results.pose_world_landmarks
            left_hand = results.left_hand_landmarks
            right_hand = results.right_hand_landmarks
            frame_data = {
                "pose": [(lm.x, lm.y, lm.z) for lm in pose_lms.landmark],
                "left_hand": [(lm.x, lm.y, lm.z) for lm in left_hand.landmark] if left_hand else None,
                "right_hand": [(lm.x, lm.y, lm.z) for lm in right_hand.landmark] if right_hand else None
            }
            frames_landmarks.append(frame_data)

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()

    if frames_landmarks:
        output_path = f"../landmarks_generados/{glosa}_landmarks.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(frames_landmarks, f, indent=2)
        print(f"✅ {len(frames_landmarks)} frames guardados en: {output_path}")
    else:
        print("⚠️ No se capturaron landmarks válidos.")

if __name__ == "__main__":
    glosa = input("📝 Ingresa nombre de la glosa: ").strip().lower()
    capturar_sec_al_presionar(glosa)
