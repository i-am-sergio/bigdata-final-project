from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common import Configuration
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, RollingPolicy
from pyflink.common.serialization import Encoder
import json

# ========================
# 1. Crear entorno de ejecución
# ========================

env = StreamExecutionEnvironment.get_execution_environment()
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
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flink-sensor-group',
    'auto.offset.reset': 'latest'
}
consumer = FlinkKafkaConsumer(
    topics='temperature',
    deserialization_schema=SimpleStringSchema(),
    properties=kafka_props
)

# ========================
# 3. Función segura para parsear JSON
# ========================
def safe_json_loads(record):
    try:
        return json.loads(record)
    except Exception:
        return {}

# ========================
# 4. Pipeline de procesamiento
# ========================
stream = env.add_source(consumer).map(
    lambda x: safe_json_loads(x),
    output_type=Types.MAP(Types.STRING(), Types.STRING())
)
string_stream = stream.map(
    lambda x: json.dumps(x),
    output_type=Types.STRING()
)

# ========================
# 5. Rolling policy personalizada
# ========================
rolling_policy = RollingPolicy.default_rolling_policy()

# ========================
# 6. Sink a HDFS con codificación de texto
# ========================
sink = FileSink.for_row_format(
    base_path='hdfs://fedora:9000/sensordata/temperature',
    encoder=Encoder.simple_string_encoder()
).with_rolling_policy(
    rolling_policy
).with_output_file_config(
    OutputFileConfig.builder()
    .with_part_prefix("temp")
    .with_part_suffix(".txt")
    .build()
).build()
string_stream.sink_to(sink)

# ========================
# 7. Ejecutar el job
# ========================
env.execute("Kafka to HDFS File - Temperature")
