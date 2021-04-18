import os
import numpy as np
import pandas as pd
import torch
from foobar.model.lstm import LSTM
from foobar.trainer.lstm_trainer import train_model
from foobar.data_loader.s3_bucket_util import download_csv
from foobar.ml_preprocessing.timeseries_preprocessing import (
    generate_window,
    create_batch_set,
    scale,
    split,
)

S3_FILE_NAME_WIDE = "wide.csv"
S3_FILE_NAME_GAMESTOP = "gme.csv"

LOCAL_FILE_PATH_WIDE = "foobar/data/processed/wide.csv"
LOCAL_FILE_PATH_GAMESTOP = "foobar/data/processed/gme.csv"

BUCKET = (
    os.environ.get("BUCKET_NAME")
    if os.environ.get("BUCKET_NAME")
    else "bb-s3-bucket-cmpt733"
)

train_window_list = [24*1, 24*2, 24*5, 24*10]
prediction_horizon_list = [1, 2, 5, 24*1, 24*2]

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

feature_set_narrow = ["openprice", "highprice", "lowprice", "volume", "closeprice"]

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
    "openprice",
    "highprice",
    "lowprice",
    "closeprice"
]

if __name__ == "__main__":
    df_wide = download_csv(BUCKET, S3_FILE_NAME_WIDE, LOCAL_FILE_PATH_WIDE)
    # df_gamestop = download_csv(BUCKET, S3_FILE_NAME_GAMESTOP, LOCAL_FILE_PATH_GAMESTOP)
    df_wide['datetime'] = pd.to_datetime(df_wide['hour'], format='%Y-%m-%d %H:%M:%S')
    df_wide = df_wide.set_index('datetime')

    train_df_wide = df_wide[df_wide.index.year == 2020]
    test_df_wide = df_wide[df_wide.index.year == 2021]

    train_datetime_list = list(train_df_wide.index)
    test_datetime_list = list(test_df_wide.index)

    train_set_wide, train_scaler_wide = scale(train_df_wide, feature_set_wide)
    test_set_wide, _ = scale(test_df_wide, feature_set_wide, train_scaler_wide)
    train_set_wide, val_set_wide = split(train_set_wide, 0.8)

    train_set_narrow, train_scaler_narrow = scale(train_df_wide, feature_set_narrow)
    test_set_narrow, _ = scale(test_df_wide, feature_set_narrow, train_scaler_narrow)
    train_set_narrow, val_set_narrow = split(train_set_narrow, 0.8)

    # datetime_target = test_datetime_list[train_window + prediction_horizon :]

    model_index = 0
    for train_window in train_window_list:
        for prediction_horizon in prediction_horizon_list:
            # for feature_set in feature_sets:
            if prediction_horizon > train_window:
                break

            # Generate data windows for training on wide table
            train_seq_wide, num_features_wide = generate_window(
                train_set_wide, train_window, prediction_horizon
            )
            val_seq_wide, _ = generate_window(
                val_set_wide, train_window, prediction_horizon
            )
            x, y = val_seq_wide
            print(y.shape)
            
            test_seq_wide, _ = generate_window(
                test_set_wide, train_window, prediction_horizon
            )

            # Generate data windows for training on financial data only
            train_seq_narrow, num_features_narrow = generate_window(
                train_set_narrow, train_window, prediction_horizon
            )
            val_seq_narrow, _ = generate_window(
                val_set_narrow, train_window, prediction_horizon
            )

            test_seq_narrow, _ = generate_window(
                test_set_narrow, train_window, prediction_horizon
            )

            # creating batchset for training
            train_batches_wide = create_batch_set(train_seq_wide)
            val_batches_wide = create_batch_set(val_seq_wide)

            train_batches_narrow = create_batch_set(train_seq_narrow)
            val_batches_narrow = create_batch_set(val_seq_narrow)

            model_wide = LSTM(input_size=num_features_wide, seq_length=train_window)
            model_narrow = LSTM(input_size=num_features_narrow, seq_length=train_window)

            model_wide.to(device)
            model_narrow.to(device)

            model_wide, train_losses_wide, val_losses_wide = train_model(
                model_wide, device, train_seq_wide, val_seq_wide, 50
            )
            model_narrow, train_losses_narrow, val_losses_narrow = train_model(
                model_narrow, device, train_seq_narrow, val_seq_narrow, 50
            )

            model_index += 1

            print("Saving...")
            state_wide = {
                "model": model_wide.state_dict(),
                "scaler": train_scaler_wide,
                "feature_set": feature_set_wide,
                "train_loss": train_losses_wide,
                "val_loss": val_losses_wide,
                "pred_horizon": prediction_horizon,
                "train_window": train_window,
            }

            state_narrow = {
                "model": model_narrow.state_dict(),
                "scaler": train_scaler_narrow,
                "feature_set": feature_set_narrow,
                "train_loss": train_losses_narrow,
                "val_loss": val_losses_narrow,
                "pred_horizon": prediction_horizon,
                "train_window": train_window,
            }

            if not os.path.isdir("checkpoint"):
                os.mkdir("checkpoint")
            torch.save(state_wide, f"./checkpoint/train_wide_{model_index}.pth")
            torch.save(state_narrow, f"./checkpoint/train_narrow_{model_index}.pth")

            # plt.plot(train_losses_wide, label="Training loss")
            # plt.plot(val_losses_wide, label="Test loss")
            # plt.legend()
