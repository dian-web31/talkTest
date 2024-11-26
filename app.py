import speech_recognition as sp
from src import oracle_db as db

def speech_to_text():
    rec = sp.Recognizer()

    my_micro = sp.Microphone(device_index=1)
    on_air = True

    while on_air:
        try:
            with my_micro as source:
                print("say something...")
                audio = rec.listen(source)
                to_text = rec.recognize_google(audio, language="es-CO")
                print("You said: {}".format(to_text))
                
                if to_text == "salir":
                    on_air = False
                else:
                    db.insert_row(to_text)

        except Exception as e:
            print("Error: {}".format(e))

if __name__ == "__main__":
    speech_to_text()