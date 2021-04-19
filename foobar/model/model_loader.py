import boto3
import torch


def download_model(s3_client, BUCKET, MODEL_FILE, LOCAL_FILE):
    try:
        s3_client.download_file(BUCKET, MODEL_FILE, LOCAL_FILE)
        model = torch.load(LOCAL_FILE)
        return model
    except Exception as e:
        print(f"Downloading {MODEL_FILE} model failed. ERROR: {e}")
        raise
