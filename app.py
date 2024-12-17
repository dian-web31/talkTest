import os  # Importa el módulo os para interactuar con el sistema operativo
import threading  # Importa el módulo threading para manejar hilos
import speech_recognition as sr  # Importa el módulo speech_recognition para reconocimiento de voz
from flask import Flask, render_template  # Importa Flask y render_template para crear la aplicación web
from flask_socketio import SocketIO, emit  # Importa SocketIO y emit para manejar la comunicación en tiempo real
from dotenv import load_dotenv  # Importa load_dotenv para cargar variables de entorno desde un archivo .env
from src.assistant import get_plate, comprobation  # Importa las funciones get_plate y comprobation del módulo assistant
from src.oracle_db import insert_row  # Importa la función insert_row del módulo oracle_db

load_dotenv()  # Carga las variables de entorno desde un archivo .env

# Crear aplicación Flask
app = Flask(__name__)  # Crea una instancia de la aplicación Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')  # Configura la clave secreta de la aplicación
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)  # Configura SocketIO para la aplicación Flask

# Reconocedor de voz
recognizer = sr.Recognizer()  # Crea una instancia del reconocedor de voz

# Variables de control
is_listening = False  # Variable para controlar si el reconocimiento está activo
stop_recognition = False  # Variable para controlar si se debe detener el reconocimiento
recognition_thread = None  # Variable para almacenar el hilo de reconocimiento
recognition_lock = threading.Lock()  # Crea un bloqueo para manejar el acceso concurrente

def continuous_recognition():
    global is_listening, stop_recognition  # Declara las variables globales

    while not stop_recognition:  # Bucle principal que se ejecuta mientras no se detenga el reconocimiento
        try:
            with sr.Microphone() as source:  # Usa el micrófono como fuente de audio
                # Ajustar para ruido ambiental
                recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta el reconocedor para el ruido ambiental

                # Escuchar audio
                print("Esperando audio...")  # Imprime un mensaje indicando que está esperando audio
                audio = recognizer.listen(source)  # Escucha el audio del micrófono

                # Reconocer texto
                text = recognizer.recognize_google(audio, language="es-CO")  # Reconoce el texto del audio usando Google
                print(f"Texto reconocido: {text}")  # Imprime el texto reconocido
                
                # Verificar comando de salida
                if text.lower() == "salir":  # Si el texto reconocido es "salir"
                    print("Comando de salida detectado")  # Imprime un mensaje indicando que se detectó el comando de salida
                    socketio.emit('recognition_result', {'text': text, 'status': 'exit'})  # Emite un evento de salida a través de SocketIO
                    stop_recognition = True  # Establece la variable para detener el reconocimiento
                    break  # Sale del bucle

                # Obtener información de la placa
                plate_info = get_plate(text)  # Llama a la función get_plate para obtener la información de la placa
                print(f"Información de placa recibida: {plate_info}")  # Imprime la información de la placa

                plate = plate_info.get('placa') # Obtiene la placa de la información
                
                # Emitir la información de la placa al cliente
                confirmacion = socketio.emit('recognition_result', {
                    'text': text,
                    'plate': plate,
                    'status': 'info'
                })  # Emite la información de la placa al cliente a través de SocketIO
                print(f"Confirmación de placa: {confirmacion}")  # Imprime la confirmación de la placa
                
                if confirmacion == None:  # Si se obtuvo una placa válida
                    confirmed = False  # Variable para controlar la confirmación del usuario
                    max_attempts = 3  # Limita los intentos para evitar un bucle infinito
                    attempts = 0  # Contador de intentos
                    
                    try:
                        if not confirmed and attempts < max_attempts:  # Bucle para pedir confirmación al usuario
                                
                            socketio.emit('waiting', {'message': 'Esperando 3 segundos...'})  # Emite un mensaje de espera al cliente
                            recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Ajusta el reconocedor para el ruido ambiental
                            audio = recognizer.listen(source)  # Escucha el audio del micrófono
                            confirmation_text = recognizer.recognize_google(audio, language="es-CO")  # Reconoce el texto del audio usando Google
                            confirmed = comprobation(confirmation_text)  # Llama a la función comprobation para verificar la confirmación
                            print(f"Confirmación de placa: {confirmed}")  # Imprime la confirmación de la placa
                                
                            if confirmed:  # Si el usuario confirma
                                # Insertar en base de datos
                                insert_row(plate_info['placa'], plate_info['tipo_vehiculo'])  # Inserta la información de la placa en la base de datos
                                socketio.emit('recognition_result', {
                                    'text': f"Placa reconocida: {plate_info['placa']} ({plate_info['tipo_vehiculo']})",
                                    'status': 'success',
                                    'type': 'plate'
                                })  # Emite un evento de éxito al cliente a través de SocketIO
                            else:  # Si el usuario no confirma
                                attempts += 1  # Incrementa el contador de intentos
                                socketio.emit('recognition_result', {
                                    'text': 'Por favor, repita la placa.',
                                    'status': 'error'
                                })  # Emite un evento de error al cliente a través de SocketIO                    
                                    
                        else:  # Si no se confirmó después del número máximo de intentos
                            socketio.emit('recognition_result', {
                                'text': 'Número máximo de intentos alcanzado. Continuando con el siguiente reconocimiento.',
                                'status': 'error'
                            })  # Emite un evento de error al cliente a través de SocketIO
                            break  # Sale del bucle

                    except sr.UnknownValueError:  # Si hubo un error inesperado
                        socketio.emit('recognition_result', {
                            'text': 'No se entendió la confirmación, por favor repita la placa.',
                            'status': 'error'   
                        })

                else:  # Si no se pudo procesar la placa
                    socketio.emit('recognition_result', {
                        'text': 'No se pudo procesar la placa',
                        'status': 'error'
                    })  # Emite un evento de error al cliente a través de SocketIO

                # Delay de 3 segundos
                socketio.emit('waiting', {'message': 'Esperando 3 segundos...'})  # Emite un mensaje de espera al cliente a través de SocketIO
                socketio.sleep(3)   # Espera 3 segundos

        except sr.UnknownValueError:  # Si no se entendió el audio
            socketio.emit('recognition_result', {
                'text': 'No se entendió el audio',
                'status': 'error'
            })  # Emite un evento de error al cliente a través de SocketIO

        except sr.RequestError as e:  # Si hubo un error en la solicitud
            socketio.emit('recognition_result', {
                'text': f'Error en solicitud: {e}',
                'status': 'error'
            })  # Emite un evento de error al cliente a través de SocketIO

        except Exception as e:  # Si hubo un error inesperado
            socketio.emit('recognition_result', {
                'text': f'Error inesperado: {e}',
                'status': 'error'
            })  # Emite un evento de error al cliente a través de SocketIO

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza la plantilla index.html

@socketio.on('start_recognition')
def handle_start_recognition():
    global is_listening, stop_recognition, recognition_thread  # Declara las variables globales

    with recognition_lock:  # Adquiere el bloqueo para manejar el acceso concurrente
        if recognition_thread is not None and recognition_thread.is_alive():  # Si el hilo de reconocimiento ya está en curso
            emit('recognition_result', {'text': 'El reconocimiento ya está en curso', 'status': 'error'})  # Emite un evento de error al cliente a través de SocketIO
            return

        # Reiniciar banderas
        is_listening = True  # Establece la variable para indicar que el reconocimiento está activo
        stop_recognition = False  # Establece la variable para indicar que no se debe detener el reconocimiento

        # Iniciar reconocimiento en un hilo separado
        recognition_thread = threading.Thread(target=continuous_recognition)  # Crea un nuevo hilo para el reconocimiento continuo
        recognition_thread.start()  # Inicia el hilo de reconocimiento

        emit('recognition_started', {'message': 'Reconocimiento iniciado'})  # Emite un evento de inicio al cliente a través de SocketIO

@socketio.on('stop_recognition')
def handle_stop_recognition():
    global is_listening, stop_recognition  # Declara las variables globales

    print('Stop recognition event received')  # Imprime un mensaje indicando que se recibió el evento de detener el reconocimiento
    is_listening = False  # Establece la variable para indicar que el reconocimiento no está activo
    stop_recognition = True  # Establece la variable para detener el reconocimiento

    emit('recognition_stopped', {'message': 'Reconocimiento detenido'})  # Emite un evento de detención al cliente a través de SocketIO

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5003, allow_unsafe_werkzeug=True)  # Ejecuta la aplicación Flask con SocketIO