from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='54.165.36.163:9092')

# Enviar un mensaje
topic = 'humidity'
msg = b'GAAAAA desde mi PC local....'

producer.send(topic, msg)
producer.flush()

print("Mensaje enviado!")