# ============================================================
# 03_agregaciones.py
# Calcula resumenes estadisticos y los guarda como CSV
#
# Ejecucion: python bigdata/03_agregaciones.py
# ============================================================

import os
import pyspark

# Necesario en Windows: apuntar HADOOP_HOME al directorio de PySpark
os.environ.setdefault("HADOOP_HOME", os.path.dirname(pyspark.__file__))
os.environ.setdefault("hadoop.home.dir", os.environ["HADOOP_HOME"])

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

# ------------------------------------------------------------
# INICIAR SPARK Y LEER EL PARQUET
# ------------------------------------------------------------

spark = SparkSession.builder \
    .appName("EcommerceAgregaciones") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("data/ecommerce_limpio.parquet")
df.cache()
print("Filas:", df.count())

total_ordenes = df.count()

# ------------------------------------------------------------
# AGREGACION 1: POR CATEGORIA
# ------------------------------------------------------------

categorias = df.groupBy("categoria").agg(
    F.count("orden_id").alias("total_ordenes"),
    F.sum("cantidad").alias("total_unidades"),
    F.round(F.sum("total_venta"), 2).alias("ingreso_total"),
    F.round(F.avg("total_venta"), 2).alias("ticket_promedio"),
    F.round(F.avg("calificacion"), 2).alias("calificacion_promedio"),
    F.round(F.avg("tiene_descuento") * 100, 2).alias("pct_con_descuento")
).orderBy(F.desc("ingreso_total"))

categorias.toPandas().to_csv("data/agg_categorias.csv", index=False)
print("Guardado: data/agg_categorias.csv")

# ------------------------------------------------------------
# AGREGACION 2: POR CIUDAD
# ------------------------------------------------------------

ciudades = df.groupBy("ciudad", "departamento").agg(
    F.count("orden_id").alias("total_ordenes"),
    F.round(F.sum("total_venta"), 2).alias("ingreso_total"),
    F.round(F.avg("total_venta"), 2).alias("ticket_promedio"),
    F.round(F.avg("calificacion"), 2).alias("calificacion_promedio")
).filter(F.col("total_ordenes") > 500) \
 .orderBy(F.desc("ingreso_total"))

ciudades.toPandas().to_csv("data/agg_ciudades.csv", index=False)
print("Guardado: data/agg_ciudades.csv")

# ------------------------------------------------------------
# AGREGACION 3: POR METODO DE PAGO
# ------------------------------------------------------------

pagos = df.groupBy("metodo_pago").agg(
    F.count("orden_id").alias("total_ordenes"),
    F.round(F.sum("total_venta"), 2).alias("ingreso_total")
).withColumn(
    "pct_of_total_ordenes",
    F.round(F.col("total_ordenes") / total_ordenes * 100, 2)
).orderBy(F.desc("total_ordenes"))

pagos.toPandas().to_csv("data/agg_pagos.csv", index=False)
print("Guardado: data/agg_pagos.csv")

# ------------------------------------------------------------
# AGREGACION 4: EVOLUCION MENSUAL
# ------------------------------------------------------------

ventana = Window.orderBy("anio", "mes")

mensual = df.groupBy("anio", "mes").agg(
    F.count("orden_id").alias("total_ordenes"),
    F.round(F.sum("total_venta"), 2).alias("ingreso_total"),
    F.round(F.avg("calificacion"), 2).alias("calificacion_promedio")
).orderBy("anio", "mes")

mensual = mensual.withColumn(
    "variacion_pct",
    F.round(
        (F.col("ingreso_total") - F.lag("ingreso_total").over(ventana))
        / F.lag("ingreso_total").over(ventana) * 100,
        2
    )
)

mensual.toPandas().to_csv("data/agg_mensual.csv", index=False)
print("Guardado: data/agg_mensual.csv")

# ------------------------------------------------------------
# AGREGACION 5: POR ESTADO DE ENVIO
# ------------------------------------------------------------

estados = df.groupBy("estado_envio").agg(
    F.count("orden_id").alias("total_ordenes"),
    F.round(F.sum("total_venta"), 2).alias("ingreso_total"),
    F.round(F.avg("calificacion"), 2).alias("calificacion_promedio")
).orderBy(F.desc("total_ordenes"))

estados.toPandas().to_csv("data/agg_estados.csv", index=False)
print("Guardado: data/agg_estados.csv")

# ------------------------------------------------------------
# CERRAR SPARK
# ------------------------------------------------------------

spark.stop()
print("Todas las agregaciones completadas.")
