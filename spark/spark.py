from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import json
from py4j.java_gateway import java_import
import os
from pyspark.sql import DataFrame
from flask_cors import CORS

# Crear la app Flask
app = Flask(__name__)
CORS(app)

spark = None  # variable global

sensor_prefixes = {
    "temperature": "temp",
    "humidity": "humid",
    "pressure": "press",
    "sound": "sound",
    "light": "light"
}

# Turnos definidos por horas
turno_horas = {
    'manana': (0, 12),
    'tarde': (12, 18),
    'noche': (18, 24)
}

def get_sensor_schema(sensor: str) -> StructType:
    base_fields = [
        StructField("timestamp", StringType(), True),
        StructField("sensor_id", StringType(), True),
        StructField("location", StringType(), True),
        StructField("device_type", StringType(), True)
    ]

    sensor_fields = {
        "temperature": StructField("temperature_celsius", DoubleType(), True),
        "humidity": StructField("humidity_percent", DoubleType(), True),
        "light": StructField("light_intensity", DoubleType(), True),
        "pressure": StructField("gas_status", DoubleType(), True),
        "sound": StructField("sound_level", DoubleType(), True)
    }

    if sensor not in sensor_fields:
        raise ValueError(f"Sensor no soportado: {sensor}")

    return StructType(base_fields + [sensor_fields[sensor]])

def get_spark():
    global spark
    if spark is None or spark._jsc is None:
        spark = SparkSession.builder \
            .appName("HDFS Sensor Query") \
            .config("spark.hadoop.fs.defaultFS", "hdfs://fedora:9000") \
            .getOrCreate()
    return spark

@app.route("/query", methods=["GET"])
def query_sensor_data():
    sensor = request.args.get("sensor")
    fecha = request.args.get("fecha")
    turno = request.args.get("turno")

    if not sensor or not fecha or not turno:
        return jsonify({"error": "Faltan parámetros: sensor, fecha o turno"}), 400

    if turno not in turno_horas:
        return jsonify({"error": "Turno inválido (mañana, tarde, noche)"}), 400

    if sensor not in sensor_prefixes:
        return jsonify({"error": f"Sensor desconocido: {sensor}"}), 400

    try:
        spark = get_spark()
        sc = spark.sparkContext

        # Importar clases de Hadoop para verificar rutas
        java_import(sc._jvm, "org.apache.hadoop.fs.Path")
        java_import(sc._jvm, "org.apache.hadoop.fs.FileSystem")
        java_import(sc._jvm, "org.apache.hadoop.conf.Configuration")

        hora_min, hora_max = turno_horas[turno]
        prefix = sensor_prefixes[sensor]
        raw_dirs = [
            f"/sensordata/{sensor}/{fecha}--{str(h).zfill(2)}"
            for h in range(hora_min, hora_max)
        ]

        dfs = []
        fs = sc._jvm.FileSystem.get(sc._jsc.hadoopConfiguration())
        Path = sc._jvm.Path

        for dir_path in raw_dirs:
            hdfs_path = Path(dir_path)
            if fs.exists(hdfs_path):
                print(f"📂 Directorio encontrado: {dir_path}")
                status_list = fs.listStatus(hdfs_path)
                for status in status_list:
                    file_path = status.getPath().toString()
                    try:
                        print(f"🔍 Leyendo archivo: {file_path}")
                        input_stream = fs.open(Path(file_path))
                        # Lee como bytearray y asegúrate de que sea texto
                        contenido = bytearray()
                        buffer = sc._gateway.jvm.java.io.BufferedInputStream(input_stream)
                        while True:
                            byte = buffer.read()
                            if byte == -1:
                                break
                            contenido.append(byte)
                        buffer.close()
                        input_stream.close()

                        contenido_str = contenido.decode("utf-8", errors="ignore")

                        if contenido_str.strip():  # si no está vacío
                            json_lines = contenido_str.strip().split("\n")
                            json_rdd = spark.sparkContext.parallelize(json_lines)
                            schema = get_sensor_schema(sensor)
                            df_part = spark.read.schema(schema).json(json_rdd)
                            dfs.append(df_part)
                    except Exception as e:
                        print(f"⚠️ Error leyendo archivo {file_path}: {e}")
            else:
                print(f"🚫 Carpeta no existe: {dir_path}")

        if not dfs:
            return jsonify([])
        df = dfs[0]
        for d in dfs[1:]:
            df = df.union(d)
        if df.rdd.isEmpty():
            return jsonify([])
        df = df.withColumn("timestamp", to_timestamp("timestamp"))            
        resultados = [json.loads(r) for r in df.toJSON().collect()]
        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
