from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common import Configuration
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, RollingPolicy
from pyflink.common.serialization import Encoder
import json

# ========================
# 1. Crear entorno remoto de ejecución en cluster Flink
# ========================
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(-1)
config = Configuration()
config.set_string(
    "pipeline.jars",
    "file:///home/hadoop/jars/flink-connector-kafka-1.17.1.jar;file:///home/hadoop/jars/kafka-clients-3.3.2.jar"
)
env.configure(config)

# ========================
# 2. Configuración de Kafka
# ========================
kafka_props = {
    'bootstrap.servers': '54.144.73.0:9092',  # Asegúrate que sea accesible desde los TaskManagers
    'group.id': 'flink-sensor-group',
    'auto.offset.reset': 'latest'
}

# ========================
# 3. Función segura para parsear JSON
# ========================
def safe_json_loads(record):
    try:
        return json.loads(record)
    except Exception:
        return {}
rolling_policy = RollingPolicy.default_rolling_policy()

# ========================
# 4. Función para crear sinks genéricos
# ========================
def add_kafka_sink(topic, path_prefix, file_prefix):
    consumer = FlinkKafkaConsumer(
        topics=topic,
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    stream = env.add_source(consumer).map(
        lambda x: safe_json_loads(x),
        output_type=Types.MAP(Types.STRING(), Types.STRING())
    )
    stream_string = stream.map(
        lambda x: json.dumps(x),
        output_type=Types.STRING()
    )
    sink = FileSink.for_row_format(
        base_path=f'hdfs://fedora:9000/sensordata/{path_prefix}',
        encoder=Encoder.simple_string_encoder()
    ).with_rolling_policy(
        rolling_policy
    ).with_output_file_config(
        OutputFileConfig.builder()
        .with_part_prefix(file_prefix)
        .with_part_suffix(".txt")
        .build()
    ).build()
    stream_string.sink_to(sink)

# ========================
# 5. Agregar sinks para todos los tópicos
# ========================
add_kafka_sink("temperature", "temperature", "temp")
add_kafka_sink("humidity", "humidity", "humid")
add_kafka_sink("pressure", "pressure", "press")
add_kafka_sink("sound", "sound", "sound")
add_kafka_sink("light", "light", "light")

# ========================
# 6. Ejecutar el job en cluster
# ========================
env.execute("Kafka to HDFS File - All Sensors")