import boto3
import torch


def download_model(bucket, MODEL_FILE, LOCAL_FILE):
    try:
        bucket.download_file(MODEL_FILE, LOCAL_FILE)
        train_result = torch.load(LOCAL_FILE)
        return train_result
    except Exception as e:
        print(f"Downloading {MODEL_FILE} model failed. ERROR: {e}")
        raise
