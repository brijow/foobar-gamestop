import os
import numpy as np
import pandas as pd
import torch
from foobar.model.lstm import LSTM
from foobar.trainer.lstm_trainer import train_model
from foobar.data_loader.s3_bucket_util import *
from foobar.ml_preprocessing.timeseries_preprocessing import (
    generate_window,
    create_batch_set,
    scale,
    split,
)

S3_FILE_NAME_WIDE = "wide.csv"
LOCAL_FILE_PATH_WIDE = "foobar/data/processed/wide.csv"

BUCKET_NAME = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)
s3_client = boto3.client("s3")

# time step = 1 hour so train time windows is day * hour
train_window_list = [24 * 1, 24 * 2, 24 * 5, 24 * 10]
prediction_horizon_list = [1, 2, 5, 24 * 1, 24 * 2]

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

feature_set_finn = [
    "volume",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
]

feature_set_wide = [
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
    "close_price",
]
feature_set_eng = [
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
    "closeprice",
]

# choose a feature set for training
feature_label_cols = feature_set_wide
feature_cols = feature_label_cols[:-1]
label_cols = feature_label_cols[-1]

# choose the train window and prediction horizon
train_window = train_window_list[1]
prediction_horizon = prediction_horizon_list[0]
print('train window: ', train_window)
print('prediction horizon: ', prediction_horizon)


if __name__ == "__main__":
    df = download_csv(s3_client, BUCKET_NAME ,S3_FILE_NAME_WIDE, LOCAL_FILE_PATH_WIDE)
    df["datetime"] = pd.to_datetime(df["hour"], format="%Y-%m-%d %H:%M:%S")
    df_gamestop = df.set_index("datetime")

    train_org_df = df_gamestop[df_gamestop.index.year == 2020]

    train_datetime_list = list(train_org_df.index)

    train_df = train_org_df[feature_label_cols]

    label_train = train_df[label_cols]

    train_set, train_scaler = scale(train_df, feature_cols)
    train_set, val_set = split(train_set, 0.8)
    label_train, label_val = split(label_train, 0.8)

    train_seq, num_features = generate_window(
        train_set, label_train, train_window, prediction_horizon
    )
    val_seq, _ = generate_window(
        val_set, label_val, train_window, prediction_horizon
    )

    x_train, _ = train_seq
    x_val, _ = val_seq
    train_batch_size = int(len(x_train) * 0.5)
    val_batch_size = int(len(x_val) * 1)

    train_batches = create_batch_set(train_seq, batch_size=300)
    val_batches = create_batch_set(val_seq, batch_size=100)

    # instantiate a LSTM model and train the model
    model = LSTM(input_size=num_features, seq_length=train_window)
    model.to(device)

    model, train_losses, val_losses = train_model(
        model, device, train_batches, val_batches, num_epochs=100
    )

    print("Saving...")
    state_wide = {
        "model": model.state_dict(),
        "scaler": train_scaler,
        "feature_set": feature_label_cols,
        "train_loss": train_losses,
        "val_loss": val_losses,
        "pred_horizon": prediction_horizon,
        "train_window": train_window,
    }

    if not os.path.isdir("checkpoint"):
        os.mkdir("checkpoint")
    torch.save(state_wide, f"./checkpoint/m{2}-v2.pth")
    # s3_client.upload_file(file_name, bucket, object_name)

    plt.plot(train_losses_wide, label="Training loss")
    plt.plot(val_losses_wide, label="Test loss")
    plt.legend()
