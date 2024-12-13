import json
from langchain_google_genai import GoogleGenerativeAI
import os
from src.oracle_db import insert_row

def get_plate(text):
    # Configuración de la API de Google Generative AI
    llm = GoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ['API_KEY_GEMINI'])

    prompt = f"""
    Extrae información de un texto sobre placas de vehículos colombianos:
    - Formato de placas de carros: ABC-123.
    - Formato de placas de motos: ABC-12A.
    Teniendo en cuenta lo anterior, elimina todos los espacios, extrae la placa y el tipo de vehículo (carro o moto) del siguiente texto:
    Texto proporcionado: "{text}"
    Recuerda, si en el texto tiene el formato (abc12a, abc 12a para moto lo tomaras con este formato ABC-12A) (y en caso de los carros si recibes la placa con este formato abc123, abc 123, retornaras con este tipo de formato ABC-123 ), tu lo tomaras con este y así mismo para los carros.
    Si el texto contiene espacios entre los caracteres de la placa, elimínalos y formatea la placa correctamente.
    Responde estrictamente en formato JSON. Si no puedes extraer una placa válida, responde con:
    {{
        "placa": null,
        "tipo_vehiculo": null,
        "error": "Motivo del error aquí."
    }}
    """

    try:
        response = llm.invoke(prompt)
        print("la response es:", response)

        if not response:
            raise ValueError("Respuesta vacía del servicio externo")

        response = json.loads(response)
        placa = response.get("placa")
        tipo_vehiculo = response.get("tipo_vehiculo")
        error = response.get("error")

        if placa is None:
            print("no se obtuvo la placa por esto: ", error)
            return {
                'placa': None,
                'tipo_vehiculo': None,
                'error': error
            }
        else:
            return {
                'placa': placa,
                'tipo_vehiculo': tipo_vehiculo
            }

    except Exception as e:
        print("Error inesperado:", e)
        return {
            'placa': None,
            'tipo_vehiculo': None,
            'error': str(e)
        }
        
def comprobation(text):
    # Configuración de la API de Google Generative AI
    llm = GoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ['API_KEY_GEMINI'])

    prompt = f"""
    Texto proporcionado: "{text}"
    Determina si el texto es una confirmación.
    
    Respuestas afirmativas incluyen (pero no se limitan a):
    - sí, si, correcto, cierto, afirmativo, exacto, ok, está bien
    
    Respuestas negativas incluyen (pero no se limitan a):
    - no, negativo, incorrecto, falso, equivocado, error
    
    Responde únicamente "true" o "false".
    """

    try:
        # Llama al modelo para generar contenido
        response = llm.invoke(prompt)  # Envía el prompt al modelo Gemini Pro y obtiene una respuesta.

        print("la response es:", response)

        # Convertir la respuesta a un valor booleano
        response = response.strip().lower()
        if response == "true":
            return True
        elif response == "false":
            return False
        else:
            raise ValueError("Respuesta inesperada del modelo")

    except Exception as e:
        print("Error inesperado:", e)
        return False