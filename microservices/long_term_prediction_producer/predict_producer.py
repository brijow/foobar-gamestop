import numpy as np
import pandas as pd
from kafka import KafkaProducer

import time
import torch

# Kafka producer
KAFKA_BROKER_URL = (
    os.environ.get("KAFKA_BROKER_URL")
    if os.environ.get("KAFKA_BROKER_URL")
    else "localhost:9092"
)
TOPIC_NAME = (
    os.environ.get("TOPIC_NAME") if os.environ.get("TOPIC_NAME") else "short-term-pred"
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda x: x.encode("utf8"),
    api_version=(0, 11, 5),
)
# read historical data from cassandra and make predictions
# X.shape[0]

while True:
    with torch.no_grad():
        model.eval()
        x.to(device)
        model.init_hidden(x.shape[0])
        y_pred = model(x)
        close_price = y_pred.cpu().numpy().flatten()
        print(f"Next hour close price predicted: {close_price}")
        producer.send(TOPIC_NAME, value=close_price)
        time.sleep(3600)
