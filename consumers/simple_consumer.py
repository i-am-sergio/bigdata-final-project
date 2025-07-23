from kafka import KafkaConsumer

# Conexión al broker (cambia por IP pública o DNS del broker EC2)
bootstrap_servers = ['54.165.36.163:9092']
topic_name = 'humidity'

# Crear el consumidor
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',  # Para empezar desde el inicio del topic
    enable_auto_commit=True,
    group_id='grupo-consumidor-1'  # Identificador de grupo de consumidores
)

print(f"Esperando mensajes en el topic '{topic_name}'...")

# Escuchar mensajes
for message in consumer:
    print(f"[{message.topic}] {message.value.decode('utf-8')}")
