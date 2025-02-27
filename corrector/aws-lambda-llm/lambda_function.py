import boto3
import json

"""
Mejoras en la configuración:
Ajustar temperature y top_p

temperature=0.1: Reduce la creatividad y hace que el modelo se adhiera más al input.
top_p=0.9: Limita la generación a las opciones más probables.
Limitar la cantidad de tokens generados

Importante: Configurar timeout >3seg (ej: 30s)
boto3 no permite configurar el timeout directamente, pero puedes usar botocore.config.Config.
"""

from botocore.config import Config
# Configurar timeout (ejemplo: 30 segundos)
config = Config(connect_timeout=30, read_timeout=30)

# Configurar cliente para Bedrock
bedrock_client = boto3.client('bedrock-runtime')  # Asegúrate de tener acceso configurado

def query_llm(prompt):
    """
    Envía una solicitud al modelo LLM a través de Amazon Bedrock.

    """
    try:
        payload = {
            "prompt": prompt,
            "temperature": 0.1,  # Reduce creatividad
            "top_p": 0.9,        # Limita generación a opciones probables
        }

        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/invoke_model.html#
        response = bedrock_client.invoke_model(
            # Reemplazar con el modelo LLM adecuado
            #modelId="meta.llama3-1-8b-instruct-v1:0", #not available on-demand!

            # Modelos LLAMA -> Reemplazar con el ARN de tu perfil de inferencia
            modelId="",
            
            #body=json.dumps({"prompt": prompt}),  # En modo default puede alucinar según las pruebas
            body=json.dumps(payload),

            contentType="application/json"
        )

        # Leer y convertir la respuesta a JSON
        response_body = json.loads(response['body'].read().decode('utf-8'))
        print(f"Log response: {response_body}")

        # Extraer la respuesta generada por el modelo
        return response_body.get("generation", "").strip()
    except Exception as e:
        print(f"Error al consultar el modelo LLM: {e}")
        raise e

def generate_prompt(cuerpo):
    """
    Genera un prompt adecuado para la corrección de texto.
    """
    return (
        f"Corrige el siguiente texto periodístico, revisando por ejemplo la correcta cantidad de espacios después de puntos y comas. "
        f"En el caso de detectar que los nombres propios corresponden al autor de la nota, eliminarlos. "
        f"También eliminar hashtags y errores que puedan estar originados en la captura del texto mediante scrapping: \n\n{cuerpo}"
    )

def lambda_handler(event, context):
    try:
        # Obtener el cuerpo desde el evento
        cuerpo = event.get("cuerpo", "")

        if not cuerpo:
            return {
                "statusCode": 400,
                "message": "El cuerpo de la noticia es requerido."
            }

        # Generar el prompt para el modelo LLM
        prompt = generate_prompt(cuerpo)

        # Consultar al modelo LLM
        corrected_cuerpo = query_llm(prompt)

        return {
            "statusCode": 200,
            "corrected_cuerpo": corrected_cuerpo
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "message": f"Error procesando la noticia: {str(e)}"
        }
