# ============================================================
# agente/agente.py
# Agente de IA para analizar ventas de e-commerce
#
# Ejecucion: python agente/agente.py
# ============================================================

import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

client = OpenAI()

# ============================================================
# PROMPT DEL AGENTE
# ============================================================
# Esta es la unica parte que debes personalizar.
# Define aqui quien es el agente, que sabe y como debe responder.
# ============================================================

PROMPT = """
Eres un analista de datos experto en e-commerce colombiano.
Tienes acceso a estadisticas reales de 300.000 ordenes de compra
realizadas entre 2022 y 2023 en Colombia.

Tu objetivo es responder preguntas sobre:
- Rendimiento por categoria de producto
- Ventas por ciudad y region
- Metodos de pago mas usados
- Evolucion de ventas en el tiempo
- Estados de envio y calidad del servicio

Reglas:
- Usa siempre las herramientas disponibles para dar datos reales
- Responde en español, de forma clara y con numeros concretos
- Si te preguntan algo que no esta en los datos, dilo claramente
- Cuando des porcentajes o promedios, incluye el contexto
"""

# ============================================================
# HERRAMIENTAS
# ============================================================

def cargar(archivo):
    ruta = f"data/{archivo}"
    if not os.path.exists(ruta):
        return pd.DataFrame()
    return pd.read_csv(ruta)

DF_CAT      = cargar("agg_categorias.csv")
DF_CIUDAD   = cargar("agg_ciudades.csv")
DF_PAGOS    = cargar("agg_pagos.csv")
DF_MENSUAL  = cargar("agg_mensual.csv")
DF_ESTADOS  = cargar("agg_estados.csv")


def estadisticas_categoria(categoria):
    if DF_CAT.empty:
        return "Datos no disponibles. Ejecuta 03_agregaciones.py"
    fila = DF_CAT[DF_CAT["categoria"].str.lower() == categoria.lower()]
    if fila.empty:
        return f"Categoria no encontrada. Opciones: {DF_CAT['categoria'].tolist()}"
    r = fila.iloc[0]
    return (
        f"{r['categoria']}:\n"
        f"  Ordenes:            {int(r['total_ordenes']):,}\n"
        f"  Unidades vendidas:  {int(r['total_unidades']):,}\n"
        f"  Ingreso total:      ${float(r['ingreso_total']):,.0f}\n"
        f"  Ticket promedio:    ${float(r['ticket_promedio']):,.2f}\n"
        f"  Calificacion prom:  {float(r['calificacion_promedio']):.2f}/5\n"
        f"  Con descuento:      {float(r['pct_con_descuento']):.1f}%"
    )


def comparar_categorias(metrica):
    if DF_CAT.empty:
        return "Datos no disponibles."
    validas = ["total_ordenes", "ingreso_total", "ticket_promedio", "calificacion_promedio"]
    if metrica not in validas:
        return f"Metrica invalida. Usa: {validas}"
    ordenado = DF_CAT.sort_values(metrica, ascending=False)
    texto = f"Ranking por {metrica}:\n"
    for i, (_, r) in enumerate(ordenado.iterrows(), 1):
        texto += f"  {i}. {r['categoria']}: {r[metrica]}\n"
    return texto


def ventas_por_ciudad(n):
    if DF_CIUDAD.empty:
        return "Datos no disponibles."
    n = min(int(n), 10)
    top = DF_CIUDAD.sort_values("ingreso_total", ascending=False).head(n)
    texto = f"Top {n} ciudades por ingreso:\n"
    for i, (_, r) in enumerate(top.iterrows(), 1):
        texto += f"  {i}. {r['ciudad']} ({r['departamento']}): ${float(r['ingreso_total']):,.0f} | {int(r['total_ordenes']):,} ordenes\n"
    return texto


def metodos_de_pago():
    if DF_PAGOS.empty:
        return "Datos no disponibles."
    texto = "Metodos de pago:\n"
    for _, r in DF_PAGOS.iterrows():
        texto += f"  {r['metodo_pago']}: {int(r['total_ordenes']):,} ordenes | ${float(r['ingreso_total']):,.0f}\n"
    return texto


def evolucion_mensual(anio):
    if DF_MENSUAL.empty:
        return "Datos no disponibles."
    tabla = DF_MENSUAL.copy()
    if int(anio) in [2022, 2023]:
        tabla = tabla[tabla["anio"] == int(anio)]
    tabla = tabla.sort_values(["anio", "mes"])
    meses = ["","Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    texto = f"Evolucion mensual ({anio if int(anio) else 'todos'}):\n"
    for _, r in tabla.iterrows():
        var = f"{r['variacion_pct']:+.1f}%" if pd.notna(r.get("variacion_pct")) else "base"
        texto += f"  {int(r['anio'])} {meses[int(r['mes'])]}: {int(r['total_ordenes']):,} ordenes | ${float(r['ingreso_total']):,.0f} | var: {var}\n"
    return texto


def estados_de_envio():
    if DF_ESTADOS.empty:
        return "Datos no disponibles."
    texto = "Estados de envio:\n"
    for _, r in DF_ESTADOS.iterrows():
        texto += f"  {r['estado_envio']}: {int(r['total_ordenes']):,} ordenes | calif: {float(r['calificacion_promedio']):.2f}/5\n"
    return texto


def resumen_general():
    if DF_CAT.empty:
        return "Datos no disponibles."
    total_ordenes = int(DF_CAT["total_ordenes"].sum())
    total_ingreso = float(DF_CAT["ingreso_total"].sum())
    mejor_cat     = DF_CAT.loc[DF_CAT["ingreso_total"].idxmax(), "categoria"]
    mejor_ciudad  = DF_CIUDAD.loc[DF_CIUDAD["ingreso_total"].idxmax(), "ciudad"] if not DF_CIUDAD.empty else "N/A"
    mejor_pago    = DF_PAGOS.loc[DF_PAGOS["total_ordenes"].idxmax(), "metodo_pago"] if not DF_PAGOS.empty else "N/A"
    return (
        f"Resumen general:\n"
        f"  Total ordenes:       {total_ordenes:,}\n"
        f"  Ingreso total:       ${total_ingreso:,.0f}\n"
        f"  Categoria top:       {mejor_cat}\n"
        f"  Ciudad top:          {mejor_ciudad}\n"
        f"  Metodo de pago top:  {mejor_pago}"
    )


HERRAMIENTAS = {
    "estadisticas_categoria": estadisticas_categoria,
    "comparar_categorias":    comparar_categorias,
    "ventas_por_ciudad":      ventas_por_ciudad,
    "metodos_de_pago":        metodos_de_pago,
    "evolucion_mensual":      evolucion_mensual,
    "estados_de_envio":       estados_de_envio,
    "resumen_general":        resumen_general,
}

SCHEMA_HERRAMIENTAS = [
    {"type":"function","function":{"name":"estadisticas_categoria","description":"Estadisticas de una categoria de producto.","parameters":{"type":"object","properties":{"categoria":{"type":"string","description":"Nombre de la categoria: Electronica, Ropa, Hogar, Deportes, Libros, Belleza, Juguetes"}},"required":["categoria"]}}},
    {"type":"function","function":{"name":"comparar_categorias","description":"Compara y rankea todas las categorias por una metrica.","parameters":{"type":"object","properties":{"metrica":{"type":"string","description":"total_ordenes, ingreso_total, ticket_promedio, calificacion_promedio"}},"required":["metrica"]}}},
    {"type":"function","function":{"name":"ventas_por_ciudad","description":"Top N ciudades por ingreso.","parameters":{"type":"object","properties":{"n":{"type":"integer","description":"Cuantas ciudades mostrar (maximo 10)"}},"required":["n"]}}},
    {"type":"function","function":{"name":"metodos_de_pago","description":"Estadisticas de todos los metodos de pago.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"evolucion_mensual","description":"Evolucion de ordenes e ingresos mes a mes.","parameters":{"type":"object","properties":{"anio":{"type":"integer","description":"2022, 2023 o 0 para todos"}},"required":["anio"]}}},
    {"type":"function","function":{"name":"estados_de_envio","description":"Estadisticas por estado de envio.","parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{"name":"resumen_general","description":"Resumen ejecutivo de todo el dataset.","parameters":{"type":"object","properties":{}}}},
]

# ============================================================
# LOOP DEL AGENTE (solo cuando se ejecuta directamente)
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  Agente de E-commerce Colombia")
    print("  Escribe 'salir' para terminar")
    print("=" * 50)

    if not os.path.exists("data/agg_categorias.csv"):
        print("\nERROR: Ejecuta primero:")
        print("  python bigdata/01_generar_dataset.py")
        print("  python bigdata/02_limpieza.py")
        print("  python bigdata/03_agregaciones.py")
        sys.exit(1)

    historial = []

    while True:
        print()
        pregunta = input("Tu: ").strip()
        if pregunta.lower() in ["salir", "exit", "quit", ""]:
            print("Hasta luego!")
            break

        historial.append({"role": "user", "content": pregunta})
        print("Pensando...", end=" ", flush=True)

        for _ in range(10):
            respuesta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": PROMPT}] + historial,
                tools=SCHEMA_HERRAMIENTAS,
                tool_choice="auto",
                temperature=0,
            )
            msg = respuesta.choices[0].message
            historial.append(msg)

            if not msg.tool_calls:
                print(f"\n\nAgente: {msg.content}")
                break

            for tc in msg.tool_calls:
                nombre = tc.function.name
                args   = json.loads(tc.function.arguments)
                try:
                    resultado = str(HERRAMIENTAS[nombre](**args))
                except Exception as e:
                    resultado = f"Error: {e}"
                historial.append({"role": "tool", "tool_call_id": tc.id, "content": resultado})
