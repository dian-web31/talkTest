import json
from langchain_google_genai import GoogleGenerativeAI
import os
from src.oracle_db import insert_row

def get_plate(text):

    #Configuración de la API de Google Generative AI
    llm = GoogleGenerativeAI(model='gemini-pro', google_api_key=os.environ['API_KEY_GEMINI'])

    # Prompt para extraer placas de vehículos
    prompt = f"""
    Extrae información de un texto sobre placas de vehículos colombianos:
    - Formato de placas de carros: ABC-123.
    - Formato de placas de motos: ABC-12A.
    Teniendo en cuenta lo anterior, extrae la placa y el tipo de vehículo (carro o moto) del siguiente texto:
    Texto proporcionado: "{text}" (Recuerda, si en el texto dice abc12a o abc 12a tu lo tomaras con este formato (ABC-12A)
    en mayuscula las letras y con un guion (-) separando las 3 primeras letras de las otras 3 y asi mismo para los carros)
    Responde estrictamente en formato JSON. Si no puedes extraer una placa válida(
    Recuerda que las placas validas son: - Formato de placas de carros: ABC-123.
    - Formato de placas de motos: ABC-12A.
    ), responde con:
    {{
        "placa": null,
        "tipo_vehiculo": null
        "error": "Motivo del error aquí."
    }}
    """


    try:
        # Llama al modelo para generar contenido
        response = llm.invoke(prompt)

        print("la response es:", response)

        response = json.loads(response)  # Convertir JSON string a diccionario
        placa = response.get("placa")
        tipo_vehiculo = response.get("tipo_vehiculo")
        error = response.get("error")


        if placa is None:
            print("no se obtuvo la placa por esot: ",error)
        else:
            # Insertar los datos en la base de datos
            insert_row(placa, tipo_vehiculo)


    except Exception as e:
        print("Error inesperado:", e)
