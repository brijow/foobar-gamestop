import boto3
import pandas as pd

def download_csv(s3_client, BUCKET, CSV_FILE, LOCAL_FILE):
    try:
        s3_client.download_file(BUCKET, CSV_FILE, LOCAL_FILE)
        df = pd.read_csv(LOCAL_FILE)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Downloading {CSV_FILE} model failed. ERROR: {e}")
        raise