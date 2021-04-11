import numpy as np
import torch


def train_model(model, device, train_batches, val_batches=None, num_epochs=200):

    train_losses = []
    val_losses = []
    best_loss = np.Inf
    val_loss = None

    learning_rate = 1e-3
    criterion = torch.nn.MSELoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        batch_losses = []
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

            batch_loss = loss.item()
            batch_losses.append(batch_loss)

            if val_batches is not None:
                with torch.no_grad():
                    model.eval()
                    val_batch_losses = []
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

        val_losses_mean = np.mean(val_batch_losses)
        batch_losses_mean = np.mean(batch_losses)
        print(
            f"Epoch {epoch}: train loss {batch_losses_mean}, val loss {val_losses_mean}"
        )
        val_losses.append(val_losses_mean)
        train_losses.append(batch_losses_mean)

    return model.eval(), train_losses, val_losses
