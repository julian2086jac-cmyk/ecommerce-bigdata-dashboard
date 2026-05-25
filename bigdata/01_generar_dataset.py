# ============================================================
# 01_generar_dataset.py
# Genera el dataset de ventas de e-commerce Colombia
# 500.000 ordenes de compra entre 2022 y 2023
#
# Ejecucion: python bigdata/01_generar_dataset.py
# ============================================================

import os
import numpy as np
import pandas as pd

np.random.seed(42)
N = 500_000

CATEGORIAS  = ["Electronica", "Ropa", "Hogar", "Deportes", "Libros", "Belleza", "Juguetes"]
PRODUCTOS   = {
    "Electronica": ["Celular", "Audifonos", "Tablet", "Smartwatch", "Parlante"],
    "Ropa":        ["Camiseta", "Pantalon", "Zapatos", "Chaqueta", "Vestido"],
    "Hogar":       ["Lampara", "Cojin", "Olla", "Cuadro", "Tapete"],
    "Deportes":    ["Tenis", "Bicicleta", "Pesa", "Colchoneta", "Raqueta"],
    "Libros":      ["Novela", "Autoayuda", "Historia", "Ciencia", "Cocina"],
    "Belleza":     ["Crema", "Perfume", "Shampoo", "Maquillaje", "Serum"],
    "Juguetes":    ["Lego", "Muneca", "Carro", "Puzzle", "Peluche"],
}
METODOS_PAGO = ["Tarjeta", "PSE", "Efectivo", "Contraentrega", "Nequi"]
ESTADOS      = ["Entregado", "En_camino", "Pendiente", "Cancelado"]
CIUDADES     = {
    "Bogota":        "Cundinamarca",
    "Medellin":      "Antioquia",
    "Cali":          "Valle del Cauca",
    "Barranquilla":  "Atlantico",
    "Cartagena":     "Bolivar",
    "Bucaramanga":   "Santander",
    "Pereira":       "Risaralda",
    "Manizales":     "Caldas",
    "Cucuta":        "Norte de Santander",
    "Ibague":        "Tolima",
}

P_CATEGORIA  = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
P_PAGO       = [0.35, 0.25, 0.15, 0.15, 0.10]
P_ESTADO     = [0.72, 0.15, 0.08, 0.05]
P_CIUDAD     = [0.30, 0.20, 0.15, 0.10, 0.08, 0.06, 0.04, 0.03, 0.02, 0.02]

fechas = pd.date_range("2022-01-01", "2023-12-31", freq="h").astype(str)

categorias_col = np.random.choice(CATEGORIAS, N, p=P_CATEGORIA)
productos_col  = [np.random.choice(PRODUCTOS[c]) for c in categorias_col]
ciudades_col   = np.random.choice(list(CIUDADES.keys()), N, p=P_CIUDAD)
deptos_col     = [CIUDADES[c] for c in ciudades_col]

df = pd.DataFrame({
    "orden_id":       range(1, N + 1),
    "fecha":          np.random.choice(fechas, N),
    "cliente_id":     np.random.randint(1000, 50000, N),
    "categoria":      categorias_col,
    "producto":       productos_col,
    "cantidad":       np.random.randint(1, 6, N),
    "precio_unitario":np.round(np.random.uniform(15, 2500, N), 2),
    "descuento_pct":  np.where(np.random.random(N) < 0.35,
                               np.random.choice([5,10,15,20,25,30], N), 0),
    "metodo_pago":    np.random.choice(METODOS_PAGO, N, p=P_PAGO),
    "ciudad":         ciudades_col,
    "departamento":   deptos_col,
    "estado_envio":   np.random.choice(ESTADOS, N, p=P_ESTADO),
    "calificacion":   np.where(np.random.random(N) < 0.85,
                               np.random.randint(3, 6, N),
                               np.random.randint(1, 3, N)),
})

# Nulos realistas
df.loc[np.random.choice(N, 4000, replace=False), "calificacion"] = np.nan
df.loc[np.random.choice(N, 2000, replace=False), "descuento_pct"] = np.nan

os.makedirs("data", exist_ok=True)
df.to_csv("data/ecommerce.csv", index=False)

tam = os.path.getsize("data/ecommerce.csv") / 1e6
print(f"Dataset guardado: {len(df):,} filas | {tam:.1f} MB")
print(df.head(3).to_string())
