# backend/utils/translator.py
def translate_text(text):
    glosas_dict = {
        "hola": "HOLA",
        "gracias": "GRACIAS",
        "si": "SI",
        "no": "NO",
        "como estas": "COMO_ESTAS"
    }
    return [glosas_dict.get(word, "DESCONOCIDO") for word in text.lower().split()]