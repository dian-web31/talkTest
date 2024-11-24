import speech_recognition as sp


def speech_to_text():
    rec = sp.Recognizer()

    my_micro = sp.Microphone(device_index=1)
    on_air = True
    response = {"data":None}

    while on_air:
        try:
            with my_micro as source:
                print("say something...")
                audio = rec.listen(source)
                to_text = rec.recognize_google(audio, language="es-CO")
                print("You said: {}".format(to_text))
                response["data"] = to_text
                
                if to_text == "salir":
                    on_air = False

        except Exception as e:
            print("Error: {}".format(e))
        
speech_to_text()

