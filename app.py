import os
import time
import threading
import speech_recognition as sr
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from src.assistant import get_plate

load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Reconocedor de voz
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Variable de control
is_listening = False
stop_recognition = False

def continuous_recognition():
    global is_listening, stop_recognition

    while not stop_recognition:
        try:
            with microphone as source:
                # Ajustar para ruido ambiental
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Escuchar audio
                print("Esperando audio...")
                audio = recognizer.listen(source)

                # Reconocer texto
                text = recognizer.recognize_google(audio, language="es-CO")

                # Verificar comando de salida
                if text.lower() == "salir":
                    print("Comando de salida detectado")
                    socketio.emit('recognition_result', {'text': text, 'status': 'exit'})
                    stop_recognition = True
                    break

                # Insertar en base de datos
                if get_plate(text):
                    # Emitir resultado
                    socketio.emit('recognition_result', {
                        'text': text,
                        'status': 'success'
                    })

                # Delay de 3 segundos
                socketio.emit('waiting', {'message': 'Esperando 3 segundos...'})
                time.sleep(3)

        except sr.UnknownValueError:
            socketio.emit('recognition_result', {
                'text': 'No se entendió el audio',
                'status': 'error'
            })

        except sr.RequestError as e:
            socketio.emit('recognition_result', {
                'text': f'Error en solicitud: {e}',
                'status': 'error'
            })

        except Exception as e:
            socketio.emit('recognition_result', {
                'text': f'Error inesperado: {e}',
                'status': 'error'
            })

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_recognition')
def handle_start_recognition():
    global is_listening, stop_recognition

    # Reiniciar banderas
    is_listening = True
    stop_recognition = False

    # Iniciar reconocimiento en un hilo separado
    recognition_thread = threading.Thread(target=continuous_recognition)
    recognition_thread.start()

    emit('recognition_started', {'message': 'Reconocimiento iniciado'})

@socketio.on('stop_recognition')
def handle_stop_recognition():
    global is_listening, stop_recognition

    print('Stop recognition event received')
    is_listening = False
    stop_recognition = True

    emit('recognition_stopped', {'message': 'Reconocimiento detenido'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5003, allow_unsafe_werkzeug=True)