import numpy as np
import torch


def train_model(model, device, train_batches, val_batches=None, num_epochs=200):

    train_losses = []
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

        batch_losses_mean = np.mean(batch_losses)
        print(f"Epoch {epoch}: train loss {batch_losses_mean}")
        train_losses.append(batch_losses_mean)

    return model.eval(), train_losses
