import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
from kafka import KafkaProducer
import json
from datetime import datetime
import random
import math
import pytz

# Configuración del sensor DHT11 (conectado al pin GPIO4)
dht_device = adafruit_dht.DHT11(board.D4)

# Configuración del sensor MQ-2 (conectado al pin GPIO17)
GPIO.setmode(GPIO.BCM)  # Usamos el esquema de numeración BCM
GPIO.setup(17, GPIO.IN)  # Configuramos GPIO17 como entrada (DO del MQ-2)

# Crear un productor de Kafka
producer = KafkaProducer(
    bootstrap_servers=['44.201.73.142:9092'],  # Dirección del broker de Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializar los datos a JSON
)

# Variables para almacenar la última lectura exitosa
last_temperature = None
last_humidity = None
last_mq2_status = None
last_light_intensity = None
last_sound_level = None

# Información estática
sensor_id_temperature = "temp-001"
sensor_id_humidity = "humid-001"
sensor_id_gas = "gas-001"
sensor_id_light = "light-001"
sensor_id_sound = "sound-001"

location_temperature = "RoomPaul"
location_humidity = "Roof"
location_gas = "kitchen"
location_light = "room"
location_sound = "office"

device_type_temperature = "dht11-temperature"
device_type_humidity = "dht11-humidity"
device_type_gas = "mq-2-gas"
device_type_light = "light-sensor"
device_type_sound = "sound-sensor"

# Función para leer DHT11
def read_dht11():
    """Lee los valores de temperatura y humedad del sensor DHT11."""
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if temperature is not None and humidity is not None:
            return temperature, humidity
        else:
            return None, None
    except RuntimeError:
        return None, None

# Función para leer MQ-2
def read_mq2():
    """Lee el valor digital del sensor MQ-2."""
    if GPIO.input(17) == GPIO.LOW:  # Gas Detectado
        return 1
    else:  # Sin Gas Detectado
        return 0 

# Función para simular el sensor de luz
def read_light_sensor():
    """Genera un valor realista para la intensidad de luz (en lux)."""
    # Obtener la hora actual
    hour = datetime.now().hour

    # Simulación de luz realista según la hora del día
    if 6 <= hour < 18:  # Durante el día
        base_light = random.uniform(600, 1000)  # Alta luz (600-1000 lux)
        light_variation = random.uniform(-100, 100)  # Variación aleatoria (por nubes, etc.)
        light_intensity = base_light + light_variation
    else:  # Durante la noche
        light_intensity = random.uniform(0, 20)  # Baja luz (0-20 lux)

    # Asegurarse de que el valor sea positivo
    return max(light_intensity, 0)

# Función para simular el sensor de sonido
def read_sound_sensor():
    """Genera un valor realista para el nivel de sonido (en decibelios)."""
    # Obtener la hora actual
    hour = datetime.now().hour

    # Simulación de ruido realista según la hora del día
    if 6 <= hour < 22:  # Durante el día (ruidos más altos)
        base_sound = random.uniform(50, 80)  # Sonido más alto (50-80 dB)
        sound_variation = random.uniform(-10, 10)  # Variación aleatoria
        sound_level = base_sound + sound_variation
    else:  # Durante la noche (ruidos más bajos)
        sound_level = random.uniform(20, 40)  # Sonido más bajo (20-40 dB)

    # Asegurarse de que el valor sea positivo
    return max(sound_level, 0)

# Obtener el timestamp actual
#def get_timestamp():
#    """Devuelve el timestamp actual en formato ISO 8601"""
#    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# Obtener el timestamp actual en Lima, Perú (UTC-5)
def get_timestamp():
    """Devuelve el timestamp actual en formato ISO 8601 para Lima, Perú (UTC-5)"""
    lima_tz = pytz.timezone('America/Lima')  # Zona horaria de Lima
    lima_time = datetime.now(lima_tz)  # Obtener la hora actual en Lima
    return lima_time.strftime('%Y-%m-%dT%H:%M:%SZ')  # Formato ISO 8601

# Bucle principal
try:
    while True:
        # Leer los datos del sensor DHT11
        temperature, humidity = read_dht11()

        # Leer el estado del sensor MQ-2
        mq2_status = read_mq2()

        # Leer los datos de los sensores simulados
        light_intensity = read_light_sensor()
        sound_level = read_sound_sensor()

        # Enviar los datos al topic 'temperature' (temperatura)
        if temperature is not None:
            message_temperature = {
                "timestamp": get_timestamp(),
                "sensor_id": sensor_id_temperature,
                "location": location_temperature,
                "temperature_celsius": temperature,
                "device_type": device_type_temperature
            }
            producer.send('temperature', value=message_temperature)
            print(f"Mensaje enviado al topic 'temperature': {message_temperature}")

        # Enviar los datos al topic 'humidity' (humedad)
        if humidity is not None:
            message_humidity = {
                "timestamp": get_timestamp(),
                "sensor_id": sensor_id_humidity,
                "location": location_humidity,
                "humidity_percent": humidity,
                "device_type": device_type_humidity
            }
            producer.send('humidity', value=message_humidity)
            print(f"Mensaje enviado al topic 'humidity': {message_humidity}")
        # Enviar el estado del sensor MQ-2 al topic 'pressure' (gas detectado)
        message_gas = {
            "timestamp": get_timestamp(),
            "sensor_id": sensor_id_gas,
            "location": location_gas,
            "gas_status": mq2_status,
            "device_type": device_type_gas
        }
        producer.send('pressure', value=message_gas)
        print(f"Mensaje enviado al topic 'pressure': {message_gas}")

        # Enviar los datos del sensor de luz al topic 'light' (intensidad de luz)
        message_light = {
            "timestamp": get_timestamp(),
            "sensor_id": sensor_id_light,
            "location": location_light,
            "light_intensity": light_intensity,
            "device_type": device_type_light
        }
        producer.send('light', value=message_light)
        print(f"Mensaje enviado al topic 'light': {message_light}")

        # Enviar los datos del sensor de sonido al topic 'sound' (nivel de sonido)
        message_sound = {
            "timestamp": get_timestamp(),
            "sensor_id": sensor_id_sound,
            "location": location_sound,
            "sound_level": sound_level,
            "device_type": device_type_sound
        }
        producer.send('sound', value=message_sound)
        print(f"Mensaje enviado al topic 'sound': {message_sound}")

        # Actualizar las últimas lecturas válidas
        if temperature is not None and humidity is not None:
            last_temperature = temperature
            last_humidity = humidity
            last_mq2_status = mq2_status
            last_light_intensity = light_intensity
            last_sound_level = sound_level

        # Esperar 1 segundo antes de la siguiente lectura
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPrograma detenido por el usuario")
finally:
    # Limpiar la configuración de GPIO al finalizar
    GPIO.cleanup()
    # Cerrar el productor de Kafka
    producer.close()
