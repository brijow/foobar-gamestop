import boto3
import torch


def download_model(BUCKET, MODEL_FILE, LOCAL_FILE):
    try:
        s3_client = boto3.client("s3")
        s3_client.download_file(BUCKET, MODEL_FILE, LOCAL_FILE)
        train_result = torch.load(LOCAL_FILE)
        return train_result
    except Exception as e:
        print(f"Downloading {MODEL_FILE} model failed. ERROR: {e}")
        raise
