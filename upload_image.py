from google.cloud import storage

storage_account_key_file = 'C:/Users/Matei/Desktop/licenta/Licenta/backend/src/main/resources/gcp-credentials.json'

storage_client = storage.Client.from_service_account_json(storage_account_key_file)
bucket_name = 'matei-storage'

def upload_blob(source_file_name, destination_blob_name):

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    return blob.public_url
