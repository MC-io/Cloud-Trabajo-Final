import boto3
import json
import time

# Inicializar el cliente de Rekognition
def initialize_rekognition_client(aws_access_key_id, aws_secret_access_key, region_name):
    return boto3.client(
        'rekognition',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

# Iniciar el análisis de video
def start_label_detection(rekognition_client, bucket_name, video_name):
    response = rekognition_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': video_name
            }
        }
    )
    return response['JobId']

# Esperar a que el trabajo se complete
def wait_for_label_detection(rekognition_client, job_id):
    while True:
        response = rekognition_client.get_label_detection(JobId=job_id)
        status = response['JobStatus']
        if status in ['SUCCEEDED', 'FAILED']:
            return response
        print("Esperando el análisis del video...")
        time.sleep(5)

# Guardar resultados en un archivo JSON
def save_results_to_json(data, json_output_path):
    with open(json_output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # Usar indent=4 para una mejor legibilidad
    print(f"Resultados guardados en {json_output_path}")

# Main function
def main():
    # Configuración de las credenciales y parámetros
    aws_access_key_id = ''
    aws_secret_access_key = ''
    region_name = 'us-east-1'  # Cambia a la región deseada
    bucket_name = 'video-prueba2'
    video_name = 'video-corto.mp4'  # Asegúrate de que sea un archivo de video válido
    json_output_path = 'metadata.json'
    
    try:
        # Inicializar cliente
        rekognition_client = initialize_rekognition_client(aws_access_key_id, aws_secret_access_key, region_name)

        # Iniciar la detección de etiquetas
        job_id = start_label_detection(rekognition_client, bucket_name, video_name)
        print(f"Job started with ID: {job_id}")

        # Esperar el resultado del análisis
        response = wait_for_label_detection(rekognition_client, job_id)

        # Guardar resultados en JSON
        save_results_to_json(response, json_output_path)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
