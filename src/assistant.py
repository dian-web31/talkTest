import os
from mistralai import Mistral
import json
from dotenv import load_dotenv

load_dotenv()

# Configuración inicial de Mistral AI
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

def get_plate(text):
    prompt = f"""
    Debes eliminar espacios y extraer la placa y el tipo de vehículo de un texto.
    Extrae información de un texto sobre placas de vehículos colombianos:
    - Formato de placas de carros: ABC-123.
    - Formato de placas de motos: ABC-12A.
    Ten en cuenta que las placas de carros y motos siempre estarán en mayúsculas y separadas con un guion (-) al momento de dar la respuesta.
    Teniendo en cuenta lo anterior, elimina todos los espacios, extrae la placa y el tipo de vehículo (carro o moto) del siguiente texto:
    Texto proporcionado: "{text}"
    Recuerda, si en el texto tiene el formato (en caso de las motos si se recibe esto: abc12a, abc 12a. Para moto lo tomaras con este formato ABC-12A) 
    (y en caso de los carros si recibes la placa con este formato abc123, abc 123 , retornaras con este tipo de formato ABC-123 ), tu lo tomaras con este y así mismo para los carros.
    Si el texto contiene espacios entre los caracteres de la placa, elimínalos y formatea la placa correctamente.
    Responde estrictamente en formato JSON. Si no puedes extraer una placa válida, responde con:
    {{
        "placa": null,
        "tipo_vehiculo": null,
        "error": "Motivo del error aquí."
    }}
    """

    try:
        # Llama al modelo Mistral para procesar el prompt
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content.strip()
        print("La respuesta es:", response_text)

        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
            print("La respuesta es:", response_text)

        response_json = json.loads(response_text)
        if response_json.get("placa") is None:
            error = response_json.get("error")
            print("No se obtuvo la placa por esto: ", error)
            return {
                'placa': None,
                'tipo_vehiculo': None,
                'error': error
            }
        else:
            print("Respuesta JSON:", response_json)
            placa = response_json.get("placa")
            tipo_vehiculo = response_json.get("tipo_vehiculo")
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
        # Llama al modelo Mistral para procesar el prompt
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response["choices"][0]["message"]["content"].strip().lower()
        print("La respuesta es:", response_text)

        if response_text == "true":
            return True
        elif response_text == "false":
            return False
        else:
            raise ValueError("Respuesta inesperada del modelo")

    except Exception as e:
        print("Error inesperado:", e)
        return False
