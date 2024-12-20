from google.cloud import storage
import os

def upload_file_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage.

    Args:
        bucket_name (str): The name of the bucket.
        source_file_path (str): The path to the file to upload.
        destination_blob_name (str): The destination blob name in the bucket.
    """
    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(destination_blob_name)

        # Upload the file to GCS
        blob.upload_from_filename(source_file_path, content_type='image/jpeg')

        print(f"File uploaded to {destination_blob_name}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"

    bucket_name = "your-bucket-name"
    source_file_path = "path/to/your/local/file.txt"
    destination_blob_name = "destination/path/in/bucket/file.txt"

    upload_file_to_gcs(bucket_name, source_file_path, destination_blob_name)
