# Flink Configuration

Este proyecto demuestra cómo configurar un pipeline de procesamiento de datos en tiempo real usando **Apache Flink**, **Apache Kafka** y **HDFS**, con scripts de producción y consumo en **Python** (Flink Py).

## 🔧 Requisitos previos

- Java 8
- Hadoop y HDFS instalados y configurados (`$HADOOP_HOME`) 3.3.6
- Hive instalado (`$HIVE_HOME`) 3.1.3
- Kafka instalado y corriendo (`localhost:9092`) 3.7.0
- Python 3.9.18 (preferiblemente gestionado con `pyenv`)
- Entorno virtual con PyFlink: `pyspark-env`

## 1. Instalar Flink

```bash
wget https://dlcdn.apache.org/flink/flink-1.17.2/flink-1.17.2-bin-scala_2.12.tgz
tar -xzf flink-1.17.2-bin-scala_2.12.tgz
mv flink-1.17.2 flink
```

## 2. Configurar variables de entorno

Agrega al final de tu `~/.bashrc`:

```bash
sudo nano ~/.bashrc
```

```bash
export FLINK_HOME=/home/hadoop/flink
export PATH=$PATH:$FLINK_HOME/bin
export HADOOP_CLASSPATH=$(hadoop classpath | tr ':' '\n' | grep -v 'commons-cli-1.2.jar' | tr '\n' ':')
```

Aplica los cambios:

```bash
source ~/.bashrc
```

## 3. Integrar Hive y corregir dependencias

Copia los JAR necesarios desde Hive:

```bash
cp $HIVE_HOME/lib/hive-exec-3.1.3.jar $FLINK_HOME/lib/
cp $HIVE_HOME/lib/hive-metastore-3.1.3.jar $FLINK_HOME/lib/
cp $HIVE_HOME/lib/libfb303-0.9.3.jar $FLINK_HOME/lib/
cp $HIVE_HOME/lib/libthrift-0.9.3.jar $FLINK_HOME/lib/
cp $HIVE_HOME/lib/*.jar $FLINK_HOME/lib/
```

Reemplaza la versión incompatible de `commons-cli`:

```bash
rm $FLINK_HOME/lib/commons-cli-1.2.jar
wget https://repo1.maven.org/maven2/commons-cli/commons-cli/1.4/commons-cli-1.4.jar -P $FLINK_HOME/lib/
```

## 4. Añadir dependencias de Kafka y Python

```bash
wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.17.1/flink-connector-kafka-1.17.1.jar -P ~/jars
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.3.2/kafka-clients-3.3.2.jar -P ~/jars
wget https://repo1.maven.org/maven2/org/apache/flink/flink-python/1.17.1/flink-python-1.17.1.jar -P $FLINK_HOME/lib/
```

Verifica que el conector Python fue copiado correctamente:

```bash
ls $FLINK_HOME/lib | grep python
```

## 5. Instalar PyFlink

Activa tu entorno virtual y luego instala PyFlink:

```bash
pyenv activate pyspark-env
python3 -m pip install apache-flink
```

## 6. Inicializar Servicios

### 6.1 Iniciar Hadoop

```bash
start-all.sh
```

### 6.2 Iniciar Zookeeper y Kafka

```bash
./bin/zookeeper-server-start.sh config/zookeeper.properties
./bin/kafka-server-start.sh config/server.properties
```

### 6.3 Iniciar Flink Cluster

```bash
$FLINK_HOME/bin/start-cluster.sh
```

### 6.4 Crear carpeta en HDFS

```bash
hdfs dfs -mkdir -p /sensordata/temperature
```

### 6.5 Crear tópico Kafka

```bash
./bin/kafka-topics.sh --create --topic temperature --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

---

## 7. Consumidor Python con Flink

```bash
$FLINK_HOME/bin/flink run -py ./consumer.py
```

---

## 8. Detener Flink

```bash
$FLINK_HOME/bin/stop-cluster.sh
```
