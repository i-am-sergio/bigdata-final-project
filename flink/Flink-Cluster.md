# Configuración de Flink en Clúster

## 1. Configurar nodos trabajadores

### En `hadoop/etc/hadoop/workers`

```
fedora
paul
aldo-nitro
```

### En `flink/conf/workers`

```
fedora
paul
aldo-nitro
```

## 2. Configurar nodo maestro

### En `flink/conf/masters` _(solo en el nodo maestro)_

```
fedora:8081
```

## 3. Configuración principal de Flink

### Editar `flink/conf/flink-conf.yaml` y ajustar las siguientes variables:

```yaml
# Dirección del JobManager
jobmanager.rpc.address: fedora # O localhost si aplica

# Puerto del JobManager
jobmanager.rpc.port: 6123

# Dirección de enlace del JobManager
jobmanager.bind-host: 0.0.0.0

# Memoria del JobManager
jobmanager.memory.process.size: 1600m

# Dirección de enlace del TaskManager
taskmanager.bind-host: 0.0.0.0

# Dirección del host del TaskManager
taskmanager.host: localhost

# Memoria del TaskManager
taskmanager.memory.process.size: 1728m

# Número de slots por TaskManager
taskmanager.numberOfTaskSlots: 1

# Paralelismo por defecto
parallelism.default: 1

# JARs del pipeline
pipeline.jars: file:///home/hadoop/jars/flink-connector-kafka-1.17.1.jar;file:///home/hadoop/jars/kafka-clients-3.3.2.jar

# Estrategia de tolerancia a fallos
jobmanager.execution.failover-strategy: region

# Configuración del API REST
rest.port: 8081
rest.address: fedora
rest.bind-address: fedora

# Ruta de Python (ajustar según la ruta del entorno en cada nodo)
python.executable: /home/hadoop/.pyenv/versions/pyspark-env/bin/python
```

## 4. Comandos para gestionar el clúster

### Iniciar el clúster:

```bash
$FLINK_HOME/bin/start-cluster.sh
```

### Detener el clúster:

```bash
$FLINK_HOME/bin/stop-cluster.sh
```
