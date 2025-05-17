from flask import Flask, jsonify
from flask_cors import CORS
from vosk import Model, KaldiRecognizer
import pyaudio
import json
import queue
import threading
from utils.translator import translate_text

app = Flask(__name__)
CORS(app)

# Cargar el modelo Vosk
model = Model("vosk_model")
recognizer = KaldiRecognizer(model, 16000)

# Cola para almacenar resultados reconocidos
audio_queue = queue.Queue()

# Hilo para captura continua de audio
def recognize_loop():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000
    )
    stream.start_stream()

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                audio_queue.put(text)

# Endpoint para obtener el texto reconocido y glosas
@app.route("/api/get_text", methods=["GET"])
def get_text():
    if not audio_queue.empty():
        text = audio_queue.get()
        glosas = translate_text(text)
        return jsonify({"text": text, "glosas": glosas})
    return jsonify({"text": "", "glosas": []})

if __name__ == "__main__":
    # Iniciar hilo de reconocimiento
    thread = threading.Thread(target=recognize_loop)
    thread.daemon = True
    thread.start()

    # Iniciar servidor Flask
    app.run(host="0.0.0.0", port=5000)
