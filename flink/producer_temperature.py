from kafka import KafkaProducer
import json
import time
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sensor_id": "temp-001",
        "location": "Roof",
        "temperature_celsius": 24.8,
        "device_type": "dht11-temperature"
    }
    producer.send('temperature', value=data)
    print(f"Sent: {data}")
    time.sleep(5)
