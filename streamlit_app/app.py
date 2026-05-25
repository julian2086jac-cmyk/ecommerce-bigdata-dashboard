# ============================================================
# streamlit_app/app.py
# Dashboard de e-commerce + chat con el agente
#
# Ejecucion: streamlit run streamlit_app/app.py
# ============================================================

import os
import sys
import json
import pandas as pd
import plotly.express as px
import streamlit as st

# Permite importar agente/ desde la raiz del proyecto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ------------------------------------------------------------
# CONFIGURACION DE LA PAGINA
# ------------------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Colombia | Big Data",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# CARGAR LOS DATOS
# ------------------------------------------------------------

DATA_DIR = os.path.join(ROOT, "data")

@st.cache_data
def cargar_datos():
    def leer(nombre):
        ruta = os.path.join(DATA_DIR, nombre)
        return pd.read_csv(ruta) if os.path.exists(ruta) else pd.DataFrame()

    return {
        "categorias": leer("agg_categorias.csv"),
        "ciudades":   leer("agg_ciudades.csv"),
        "pagos":      leer("agg_pagos.csv"),
        "mensual":    leer("agg_mensual.csv"),
        "estados":    leer("agg_estados.csv"),
    }

datos = cargar_datos()
datos_ok = not datos["categorias"].empty

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:
    st.title("🛒 E-Commerce Colombia")
    st.caption("Trabajo universitario — Big Data")
    st.divider()
    seccion = st.radio(
        "Navegación",
        ["📊 Dashboard", "🤖 Chat con IA"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("300,000 órdenes · 2022-2023")

# ------------------------------------------------------------
# SECCION 1: DASHBOARD
# ------------------------------------------------------------

if seccion == "📊 Dashboard":
    st.title("📊 Dashboard de Ventas E-Commerce")
    st.caption("Colombia · 2022-2023 · 300,000 órdenes")

    if not datos_ok:
        st.error("No se encontraron datos. Ejecuta primero el pipeline de Big Data.")
        st.code(
            "python bigdata/01_generar_dataset.py\n"
            "python bigdata/02_limpieza.py\n"
            "python bigdata/03_agregaciones.py"
        )
        st.stop()

    cat = datos["categorias"]
    ciu = datos["ciudades"]
    pag = datos["pagos"]
    men = datos["mensual"]
    est = datos["estados"]

    # a) Métricas globales
    total_ordenes  = int(cat["total_ordenes"].sum())
    ingreso_total  = float(cat["ingreso_total"].sum())
    ticket_prom    = float(cat["ticket_promedio"].mean())
    calif_prom     = float(cat["calificacion_promedio"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de órdenes",  f"{total_ordenes:,}")
    c2.metric("Ingreso total",     f"${ingreso_total:,.0f}")
    c3.metric("Ticket promedio",   f"${ticket_prom:,.2f}")
    c4.metric("Calificación prom", f"{calif_prom:.2f} / 5")

    st.divider()

    # b) Gráfico de barras — ingresos por categoría
    st.subheader("Ingresos por categoría")
    fig_bar = px.bar(
        cat.sort_values("ingreso_total"),
        x="ingreso_total",
        y="categoria",
        orientation="h",
        color="ingreso_total",
        color_continuous_scale="Blues",
        labels={"ingreso_total": "Ingreso total ($)", "categoria": "Categoría"},
        text_auto=".2s",
    )
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # c) Torta métodos de pago  +  d) Evolución mensual (lado a lado)
    col_pie, col_line = st.columns(2)

    with col_pie:
        st.subheader("Métodos de pago")
        fig_pie = px.pie(
            pag,
            names="metodo_pago",
            values="total_ordenes",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_line:
        st.subheader("Evolución mensual de órdenes")
        men_plot = men.copy()
        men_plot["periodo"] = (
            men_plot["anio"].astype(str) + "-"
            + men_plot["mes"].astype(str).str.zfill(2)
        )
        fig_line = px.line(
            men_plot,
            x="periodo",
            y="total_ordenes",
            markers=True,
            color_discrete_sequence=["#1f77b4"],
            labels={"periodo": "Periodo", "total_ordenes": "Órdenes"},
        )
        fig_line.update_layout(height=360, xaxis_tickangle=-45)
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # e) Tabla interactiva — top ciudades
    st.subheader("Top ciudades por ingreso")
    tabla_ciu = ciu[["ciudad", "departamento", "total_ordenes", "ingreso_total",
                      "ticket_promedio", "calificacion_promedio"]].copy()
    tabla_ciu.columns = ["Ciudad", "Departamento", "Órdenes", "Ingreso ($)",
                         "Ticket prom ($)", "Calificación"]
    st.dataframe(
        tabla_ciu.style.format({
            "Órdenes":       "{:,.0f}",
            "Ingreso ($)":   "${:,.0f}",
            "Ticket prom ($)": "${:,.2f}",
            "Calificación":  "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Extra: estados de envío
    st.divider()
    st.subheader("Estados de envío")
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.dataframe(
            est.rename(columns={
                "estado_envio":        "Estado",
                "total_ordenes":       "Órdenes",
                "ingreso_total":       "Ingreso ($)",
                "calificacion_promedio": "Calificación",
            }).style.format({
                "Órdenes":     "{:,.0f}",
                "Ingreso ($)": "${:,.0f}",
                "Calificación": "{:.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    with col_e2:
        fig_est = px.bar(
            est,
            x="estado_envio",
            y="total_ordenes",
            color="estado_envio",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"estado_envio": "Estado", "total_ordenes": "Órdenes"},
            text_auto=True,
        )
        fig_est.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_est, use_container_width=True)

# ------------------------------------------------------------
# SECCION 2: CHAT CON EL AGENTE
# ------------------------------------------------------------

elif seccion == "🤖 Chat con IA":
    st.title("🤖 Chat con el Agente de E-Commerce")
    st.caption("Pregúntale sobre ventas, categorías, ciudades, tendencias…")

    # API Key
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        api_key = st.text_input(
            "🔑 Ingresa tu OpenAI API Key para usar el chat:",
            type="password",
            placeholder="sk-...",
        )

    if not api_key:
        st.info("Ingresa una API Key de OpenAI para activar el chat.")
        st.stop()

    # Importar lógica del agente (sin ejecutar el CLI loop)
    os.environ["OPENAI_API_KEY"] = api_key
    try:
        from agente.agente import PROMPT, SCHEMA_HERRAMIENTAS, HERRAMIENTAS
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Error al cargar el agente: {e}")
        st.stop()

    # Historial en session_state
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Botón limpiar
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("🗑️ Limpiar chat"):
            st.session_state.mensajes = []
            st.rerun()

    # Mostrar historial
    for msg in st.session_state.mensajes:
        role = msg.get("role") if isinstance(msg, dict) else msg.role
        content = msg.get("content") if isinstance(msg, dict) else msg.content
        if role in ("user", "assistant") and content:
            with st.chat_message(role):
                st.write(content)

    # Input del usuario
    if pregunta := st.chat_input("Escribe tu pregunta sobre ventas, categorías, ciudades…"):
        st.session_state.mensajes.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.write(pregunta)

        with st.chat_message("assistant"):
            with st.spinner("Analizando datos…"):
                historial_api = [{"role": "system", "content": PROMPT}]
                for m in st.session_state.mensajes:
                    role = m.get("role") if isinstance(m, dict) else m.role
                    content = m.get("content") if isinstance(m, dict) else m.content
                    if role in ("user", "assistant") and content:
                        historial_api.append({"role": role, "content": content})

                respuesta_final = "Lo siento, no pude generar una respuesta."
                for _ in range(10):
                    respuesta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=historial_api,
                        tools=SCHEMA_HERRAMIENTAS,
                        tool_choice="auto",
                        temperature=0,
                    )
                    msg_api = respuesta.choices[0].message
                    historial_api.append(msg_api)

                    if not msg_api.tool_calls:
                        respuesta_final = msg_api.content
                        break

                    for tc in msg_api.tool_calls:
                        nombre  = tc.function.name
                        args    = json.loads(tc.function.arguments)
                        try:
                            resultado = str(HERRAMIENTAS[nombre](**args))
                        except Exception as e:
                            resultado = f"Error: {e}"
                        historial_api.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": resultado,
                        })

                st.write(respuesta_final)
                st.session_state.mensajes.append(
                    {"role": "assistant", "content": respuesta_final}
                )
