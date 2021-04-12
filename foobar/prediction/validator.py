import torch
import torch.nn as nn
import numpy as np
from foobar.ml_preprocessing.timeseries_preprocessing import generate_window


def validator(model, device, target_set, train_window, prediction_horizon):
    # model: trained model
    # target_set: timeseries
    target_seq = generate_window(target_set, train_window, prediction_horizon)

    truth, predictions, losses = [], [], []
    criterion = nn.L1Loss(reduction="sum").to(device)
    model.to(device)

    X_test, y_test = target_seq
    test_set_size = X_test.size(0)

    model.eval()
    with torch.no_grad():
        for i in range(test_set_size):
            x_i = X_test[i : i + 1]
            y_i = y_test[i : i + 1]
            x_i.to(device)
            y_i.to(device)
            model.init_hidden(x_i.size(0), device)
            y_pred = model(x_i)
            predictions.append(y_pred.cpu().numpy().flatten())
            loss = criterion(y_pred, y_i)
            losses.append(loss.item())

    truth = y_test.cpu().numpy().flatten()
    predictions = np.array(predictions).flatten()

    return predictions, truth
