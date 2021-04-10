# LSTM architecture is implemented as part of the ML pipeline
import numpy as np
import torch


def train_model(model, device, train_batches, val_batches=None, num_epochs=200):

    learning_rate = 1e-3
    best_loss = np.Inf
    val_loss = None
    history = dict(train=[], val=[])

    criterion = torch.nn.MSELoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        train_losses = []
        for batch_ndx, train_batch in enumerate(train_batches):
            model.train()
            x_train, y_train = train_batch
            batch_size = x_train.size(0)
            x_train = x_train.to(device)
            y_train = y_train.to(device)
            model.init_hidden(batch_size, device)
            outputs = model(x_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            train_loss = loss.item()
            train_losses.append(train_loss)

            if val_batches is not None:
                with torch.no_grad():
                    model.eval()
                    val_losses = []
                    for _, val_batch in enumerate(val_batches):
                        x_val, y_val = val_batch
                        batch_size = x_val.size(0)
                        x_val = x_val.to(device)
                        y_val = y_val.to(device)
                        model.init_hidden(batch_size, device)
                        pred = model(x_val)
                        loss = criterion(pred, y_val)
                        val_loss = loss.item()
                        val_losses.append(val_loss)
                        if val_loss < best_loss:
                            best_loss = val_loss
                        if val_loss < 0.05:
                            break
            print(
                f"Batch {batch_ndx} Epoch {epoch}: train loss {train_loss} val loss {val_loss}"
            )
        history["val"].append(np.mean(val_losses))
        history["train"].append(np.mean(train_losses))

    print(f"best validation loss = {best_loss}")
    return model.eval(), history, best_loss
