# from kafka import KafkaConsumer
# from hdfs import InsecureClient
# from datetime import datetime

# # Configura conexión a Kafka
# consumer = KafkaConsumer(
#     'humidity', 'pressure', 'temperature',
#     bootstrap_servers=['54.165.36.163:9092'],
#     auto_offset_reset='earliest',
#     group_id='hdfs-writer',
#     value_deserializer=lambda m: m.decode('utf-8')
# )

# # Conexión a HDFS (por defecto puerto 9870 o 50070 en algunos setups)
# hdfs_client = InsecureClient('http://localhost:9870', user='heros')

# # Ruta destino en HDFS
# hdfs_path = 'kafka_data.txt'

# # Crear archivo si no existe
# if not hdfs_client.status(hdfs_path, strict=False):
#     hdfs_client.write(hdfs_path, data='', overwrite=True)

# print("⏳ Esperando mensajes...")

# # Escuchar y guardar en HDFS
# for msg in consumer:
#     topic = msg.topic
#     value = msg.value
#     timestamp = datetime.now().isoformat()

#     line = f"{timestamp} | {topic} | {value}\n"

#     # Añadir al archivo en HDFS
#     with hdfs_client.write(hdfs_path, append=True, encoding='utf-8') as writer:
#         writer.write(line)

#     print(f"✅ Guardado: {line.strip()}")

from kafka import KafkaConsumer
from hdfs import InsecureClient
from datetime import datetime
import threading

# Conexión a HDFS
hdfs_client = InsecureClient('http://localhost:9870', user='heros')

# Topics y sus archivos HDFS respectivos
topics_files = {
    'humidity': 'humidity_data.txt',
    'pressure': 'pressure_data.txt',
    'temperature': 'temperature_data.txt',
}

# Crear archivos si no existen
for hdfs_path in topics_files.values():
    if not hdfs_client.status(hdfs_path, strict=False):
        hdfs_client.write(hdfs_path, data='', overwrite=True)

def consume_and_write(topic, hdfs_path):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['54.165.36.163:9092'],
        auto_offset_reset='earliest',
        group_id=f'hdfs-writer-{topic}',
        value_deserializer=lambda m: m.decode('utf-8')
    )

    print(f"🟢 Escuchando topic: {topic}")

    for msg in consumer:
        value = msg.value
        timestamp = datetime.now().isoformat()
        line = f"{timestamp} | {topic} | {value}\n"

        # Escribir en HDFS
        with hdfs_client.write(hdfs_path, append=True, encoding='utf-8') as writer:
            writer.write(line)

        print(f"✅ [{topic}] Guardado: {line.strip()}")

# Lanzar un hilo por cada topic
threads = []
for topic, hdfs_path in topics_files.items():
    t = threading.Thread(target=consume_and_write, args=(topic, hdfs_path))
    t.start()
    threads.append(t)

# Esperar a que los hilos terminen (nunca terminan en uso normal)
for t in threads:
    t.join()
