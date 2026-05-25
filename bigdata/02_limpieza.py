# ============================================================
# 02_limpieza.py
# Lee el CSV con PySpark y aplica limpieza de datos
#
# Ejecucion: python bigdata/02_limpieza.py
# ============================================================

import os
import pyspark

# Necesario en Windows: apuntar HADOOP_HOME al directorio de PySpark
os.environ.setdefault("HADOOP_HOME", os.path.dirname(pyspark.__file__))
os.environ.setdefault("hadoop.home.dir", os.environ["HADOOP_HOME"])

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ------------------------------------------------------------
# PASO 1: INICIAR SPARK
# ------------------------------------------------------------

spark = SparkSession.builder \
    .appName("EcommerceLimpieza") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ------------------------------------------------------------
# PASO 2: LEER EL CSV
# ------------------------------------------------------------

df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("data/ecommerce.csv")

# ------------------------------------------------------------
# PASO 3: EXPLORAR LOS DATOS
# ------------------------------------------------------------

df.printSchema()
df.show(5, truncate=False)
print("Total filas:", df.count())

# ------------------------------------------------------------
# PASO 4: RELLENAR NULOS
# ------------------------------------------------------------

promedio_calificacion = df.agg(F.avg("calificacion")).collect()[0][0]
print(f"Promedio calificacion: {promedio_calificacion:.2f}")

df = df.fillna({
    "calificacion": promedio_calificacion,
    "descuento_pct": 0.0
})

# ------------------------------------------------------------
# PASO 5: ELIMINAR FILAS INVALIDAS
# ------------------------------------------------------------

df = df.filter(
    (F.col("precio_unitario") > 0) &
    (F.col("cantidad") > 0)
)
print("Filas tras limpieza:", df.count())

# ------------------------------------------------------------
# PASO 6: CREAR COLUMNAS NUEVAS
# ------------------------------------------------------------

df = df.withColumn(
    "total_venta",
    F.col("precio_unitario") * F.col("cantidad") * (1 - F.col("descuento_pct") / 100)
)
df = df.withColumn(
    "tiene_descuento",
    F.when(F.col("descuento_pct") > 0, 1).otherwise(0)
)
df = df.withColumn("anio", F.year(F.col("fecha")))
df = df.withColumn("mes",  F.month(F.col("fecha")))
df = df.withColumn("hora", F.hour(F.col("fecha")))
df = df.withColumn("ruta", F.concat(F.col("ciudad"), F.lit(">"), F.col("departamento")))

df.show(3, truncate=False)

# ------------------------------------------------------------
# PASO 7: GUARDAR COMO PARQUET
# Usamos toPandas() para escribir el archivo evitando la
# dependencia de winutils.exe en Windows
# ------------------------------------------------------------

pandas_df = df.toPandas()
# Spark solo lee timestamps en microsegundos; pyarrow por defecto usa nanosegundos
pandas_df["fecha"] = pandas_df["fecha"].astype("datetime64[us]")
pandas_df.to_parquet("data/ecommerce_limpio.parquet", index=False)
print("Parquet guardado en data/ecommerce_limpio.parquet")

# ------------------------------------------------------------
# PASO 8: CERRAR SPARK
# ------------------------------------------------------------

spark.stop()
print("Pipeline de limpieza completado.")
