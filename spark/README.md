# Spark Backend

## Requisitos previos

Asegúrate de haber creado y activado el entorno virtual con `pyenv`, el mismo utilizado en Flink.

```bash
pyenv activate pyspark
```

Instala las dependencias necesarias:

```bash
python3 -m pip install flask flask-cors pyspark
```

## Ejecución

Ejecuta el backend con Spark:

```bash
spark-submit ./spark.py
```

Esto expondrá el servicio Flask en el puerto `5000`.

## Realizar consultas

Puedes hacer consultas HTTP al backend mediante la siguiente URL (reemplazando los parámetros según el caso):

```
http://localhost:5000/query?sensor=sound&fecha=2025-07-24&turno=noche
```

- `sensor`: nombre del sensor (por ejemplo, `sound`, `gas`, `humidity`, etc.)
- `fecha`: en formato `YYYY-MM-DD`
- `turno`: puede ser `mañana`, `tarde`, `noche` (sin tilde si se codifica como parámetro URL)
