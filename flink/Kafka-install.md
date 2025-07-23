# Apache Kafka (Zookeeper o KRaft)

## Paso 1: Descargar e Instalar Kafka

```bash
sudo curl -O https://downloads.apache.org/kafka/3.7.0/kafka_2.13-3.7.0.tgz
sudo tar -xvzf kafka_2.13-3.7.0.tgz
sudo mv kafka_2.13-3.7.0 kafka
```

## Estructura del Proyecto

```
kafka/
├── bin/
├── config/
│   ├── server.properties         <- Configuración del broker
│   ├── zookeeper.properties      <- Configuración del zookeeper (si se usa)
│   └── kraft/server.properties   <- Configuración para KRaft (modo sin Zookeeper)
```

## Opción 1: Configurar Kafka con Zookeeper

### Configurar Zookeeper en cada instancia

Editar el archivo `config/zookeeper.properties`:

```properties
tickTime=2000
initLimit=10
syncLimit=5
server.1=172.31.81.3:2888:3888
server.2=172.31.93.126:2888:3888
server.3=172.31.80.158:2888:3888
4lw.commands.whitelist=stat,ruok,conf
```

### Asignar id a cada nodo en Zookeeper

```bash
mkdir -p /tmp/zookeeper
echo 1 | sudo tee /tmp/zookeeper/myid # En la instancia 1
echo 2 | sudo tee /tmp/zookeeper/myid # En la instancia 2
echo 3 | sudo tee /tmp/zookeeper/myid # En la instancia 3
```

### Configurar Kafka Broker (`config/server.properties`)

Ejemplo para el nodo 2 (`broker.id=2`):

```properties
broker.id=2
log.dirs=/tmp/kafka-logs
zookeeper.connect=172.31.81.3:2181,172.31.93.126:2181,172.31.80.158:2181
listeners=PLAINTEXT://172.31.93.126:9092
advertised.listeners=PLAINTEXT://172.31.93.126:9092
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2
zookeeper.connection.timeout.ms=18000
```

### Iniciar Zookeeper y Kafka

```bash
# En cada nodo:
./bin/zookeeper-server-start.sh config/zookeeper.properties
./bin/kafka-server-start.sh config/server.properties
```

---

## Opción 2: Configurar Kafka con KRaft (sin Zookeeper)

### Editar `config/kraft/server.properties`

Ejemplo para el nodo 1 (`node.id=1`, IP `172.31.93.211`):

```properties
node.id=1
process.roles=broker,controller
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
advertised.listeners=PLAINTEXT://172.31.93.211:9092
inter.broker.listener.name=PLAINTEXT
controller.quorum.voters=1@172.31.93.211:9093,2@172.31.85.82:9093,3@172.31.83.140:9093
log.dirs=/tmp/kraft-combined-logs
```

### Generar UUID

```bash
/opt/kafka/bin/kafka-storage.sh random-uuid
```

Guarda el UUID generado, será usado en todos los nodos.

### Formatear almacenamiento en cada nodo

```bash
/opt/kafka/bin/kafka-storage.sh format -t <UUID> -c /opt/kafka/config/kraft/server.properties
```

### Iniciar Kafka en modo KRaft

```bash
./bin/kafka-server-start.sh config/kraft/server.properties
```

## Comando para Verificar Versión de Kafka

```bash
./bin/kafka-topics.sh --version
```

O alternativamente:

```bash
./bin/kafka-run-class.sh kafka.Kafka --version
```
