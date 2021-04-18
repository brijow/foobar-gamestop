import torch
import pandas as pd
from foobar.ml_preprocessing.timeseries_preprocessing import generate_window, scale


def prediction(model, device, scaler, df, train_parameter_set):

    feature_set, train_window, prediction_horizon, target_col = train_parameter_set

    if target_col not in df.columns:
        df_target = df.copy()
        df_target[target_col] = -1.0
    else:
        # find index of the last null prediction
        df_null = df[df[target_col] == -1]
        last_null_prediction = df_null.index[0]
        startingindex = max((last_null_prediction - train_window), 0)
        df_target = df.iloc[startingindex :, :]
        # for i in range(df_null.shape[0]):
        #     if not df_null.iloc[i] and df_null.iloc[i + 1]:
        #         last_null_prediction = i + 1
        #         df_target = df.iloc[(last_null_prediction - train_window) :, :]
        #         break
    
    if len(df_target) - train_window - prediction_horizon <= 0:
        return None

    target_set, _ = scale(df_target, feature_set, scaler)
    target_seq, _ = generate_window(target_set, train_window, prediction_horizon)

    predictions = []
    model.to(device)

    X_test, y_test = target_seq
    test_set_size = X_test.size(0)

    model.eval()
    with torch.no_grad():
        for i in range(test_set_size):
            x_i = X_test[i : i + 1]
            x_i.to(device)
            model.init_hidden(x_i.size(0), device)
            y_pred = model(x_i)
            predictions.append(y_pred.item())
            # df_target.at[i + train_window, "prediction"] = y_pred.item()
    df_target[target_col] = pd.Series(predictions, dtype='float') 
    df_target = df_target.fillna(-1)
    return df_target
