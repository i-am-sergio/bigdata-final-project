from pyspark.sql import SparkSession

# Iniciar sesión de Spark con soporte para Hive
spark = SparkSession.builder \
    .appName("QueryKafkaTables") \
    .enableHiveSupport() \
    .getOrCreate()

# Mostrar tablas disponibles
print("📋 Tablas en la base de datos 'kafka_data':")
spark.sql("SHOW TABLES IN kafka_data").show()

# Consultar y mostrar las 10 primeras filas de cada tabla
print("\n🌡️ Datos de temperatura:")
spark.sql("SELECT * FROM kafka_data.temperature LIMIT 10").show(truncate=False)

print("\n💧 Datos de humedad:")
spark.sql("SELECT * FROM kafka_data.humidity LIMIT 10").show(truncate=False)

print("\n🌀 Datos de presión:")
spark.sql("SELECT * FROM kafka_data.pressure LIMIT 10").show(truncate=False)
