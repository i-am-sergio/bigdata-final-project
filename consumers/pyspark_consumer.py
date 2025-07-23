from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col

spark = SparkSession.builder \
    .appName("KafkaDataToHive") \
    .enableHiveSupport() \
    .getOrCreate()

# Leer desde HDFS
df_humidity = spark.read.text("hdfs://localhost:9000/user/heros/humidity_data.txt")
df_pressure = spark.read.text("hdfs://localhost:9000/user/heros/pressure_data.txt")
df_temperature = spark.read.text("hdfs://localhost:9000/user/heros/temperature_data.txt")

# Separar en columnas
def parse_df(df):
    return df.withColumn("timestamp", split(col("value"), " \\| ").getItem(0)) \
             .withColumn("topic",     split(col("value"), " \\| ").getItem(1)) \
             .withColumn("value",     split(col("value"), " \\| ").getItem(2)) \
             .drop("value")

df_humidity = parse_df(df_humidity)
df_pressure = parse_df(df_pressure)
df_temperature = parse_df(df_temperature)

# Crear tablas (si no existen)
spark.sql("CREATE DATABASE IF NOT EXISTS kafka_data")

df_humidity.write.mode("overwrite").saveAsTable("kafka_data.humidity")
df_pressure.write.mode("overwrite").saveAsTable("kafka_data.pressure")
df_temperature.write.mode("overwrite").saveAsTable("kafka_data.temperature")
