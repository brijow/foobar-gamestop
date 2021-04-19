import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns
from foobar.model.model_loader import *
from foobar.model.lstm import LSTM
from foobar.data_loader.s3_bucket_util import *
from foobar.ml_preprocessing.timeseries_preprocessing import (
    generate_window,
    scale,
)

S3_FILE_NAME_WIDE = "wide.csv"
LOCAL_FILE_PATH_WIDE = "foobar/data/processed/wide.csv"

BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
s3_client = boto3.client("s3")

MODEL_FILE = "m2.pth"
LOCAL_FILE = MODEL_FILE

feature_label_cols = [
    "avg_all_post_pos",
    "avg_all_post_neg",
    "avg_all_post_neu",
    "cnt_all_user",
    "cnt_all_tag",
    "cnt_all_post",
    "cnt_all_comments",
    "avg_gme_post_pos",
    "avg_gme_post_neg",
    "avg_gme_post_neu",
    "cnt_gme_user",
    "cnt_gme_tag",
    "cnt_gme_post",
    "cnt_gme_comments",
    "volume",
    "open_price",
    "high_price",
    "low_price",
    "close_price"
]

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")


def predict(model, device, target_set):
    # model: trained model
    # target_set: timeseries
    observed, predicted, losses = [], [], []
    criterion = nn.L1Loss(reduction="sum").to(device)
    model.to(device)
    print(device)

    X_test, y_test = target_set
    set_size = X_test.size(0)

    # model.init_hidden(X_test.size(0), device)
    # y_pred = model(X_test)

    with torch.no_grad():
        model.eval()
        for i in range(set_size):
            x_i = X_test[i : i + 1]
            y_i = y_test[i : i + 1]
            x_i.to(device)
            y_i.to(device)
            model.init_hidden(x_i.size(0), device)
            y_pred = model(x_i)
            loss = criterion(y_pred, y_i)
            predicted.append(y_pred.item())
            losses.append(loss.item())

    observed = y_test.cpu().numpy().flatten()
    predictions = np.array(predicted).flatten()
    losses = np.array(losses).flatten()
    return predictions, observed, losses


if __name__ == "__main__":

    # Download processed data from S3 bucker for prediction
    df = download_csv(s3_client, BUCKET_NAME ,S3_FILE_NAME_WIDE, LOCAL_FILE_PATH_WIDE)
    
    df["datetime"] = pd.to_datetime(df["hour"], format="%Y-%m-%d %H:%M:%S")
    df_gamestop = df.set_index("datetime")

    test_org_df = df_gamestop[df_gamestop.index.year == 2021]

    test_datetime_list = list(test_org_df.index)

    feature_cols = feature_label_cols[:-1]
    label_cols = feature_label_cols[-1]
    print(feature_label_cols)

    test_df = test_org_df[feature_label_cols]
    label_test = test_df[label_cols]

    # download the model form S3 Bucket for predictions
    train_result = download_model(s3_client, BUCKET_NAME ,MODEL_FILE, LOCAL_FILE)

    # feature_label_cols = train_result["feature_set"]

    prediction_horizon = int(train_result["pred_horizon"])
    train_window = int(train_result["train_window"])
    train_scaler = train_result["scaler"]

    num_features = len(feature_label_cols)

    target_set, _ = scale(test_df, feature_cols, train_scaler)

    datetime_target = test_datetime_list[train_window + prediction_horizon :]

    target_seq, _ = generate_window(
        target_set, label_test, train_window, prediction_horizon
    )

    model = LSTM(input_size=num_features, seq_length=train_window)
    model.load_state_dict(train_result["model"])

   # predictions
    predictions, observed, pred_losses = predict(model, device, target_seq)

    plt.plot(datetime_target, predictions, label="Predicted")
    plt.plot(datetime_target, observed, label="Observed")
    plt.xticks(rotation=45)
    plt.legend()

    plt.plot(datetime_target, pred_losses, label="Prediction Loss")
    plt.xticks(rotation=45)
    plt.legend()
    print(f"Prediction loss mean = {np.mean(pred_losses)}")

    plt.figure(figsize=(16, 9))
    sns.displot(pred_losses, bins=100, kde=True)
    plt.title("Loss Distribution on Short Squeeze Dataset", fontsize=14)

    test_org_df[label_cols].plot()
    test_org_df["prediction"].plot()
