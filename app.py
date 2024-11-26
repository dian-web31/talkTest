import speech_recognition as sp
from src import oracle_db as db
import gradio as gr

def transcribe(audio):
    recognizer = sp.Recognizer()
    with sp.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="es-CO")
        db.insert_row(text)
    return text

iface = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(sources="microphone"),
    outputs="text",
    live=True,
    streaming=False
)
iface.launch()