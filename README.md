# E-Commerce Colombia — Big Data con LLM
**Autor:** Julian Andres Cardona Alzate  
**Materia:** Big Data — Actividad 4

---

## Pasos para correr el proyecto

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Dashboard

```bash
streamlit run streamlit_app/app.py
```

Se abre automáticamente en: **http://localhost:8501**

> La API key de OpenAI ya está configurada en el archivo `.env`.  
> Los datos ya están procesados en la carpeta `data/` — no es necesario correr ningún script adicional.

---

## Estructura del proyecto

```
├── informe_ecommerce.pdf     → Informe final de la actividad
├── agente/agente.py          → Agente de IA (OpenAI GPT-4o-mini)
├── bigdata/
│   ├── 01_generar_dataset.py → Genera 300,000 órdenes sintéticas
│   ├── 02_limpieza.py        → Limpieza con PySpark
│   └── 03_agregaciones.py    → Cálculo de estadísticas
├── data/agg_*.csv            → Datos listos para el dashboard
└── streamlit_app/app.py      → Dashboard interactivo
```

---

## Regenerar los datos (opcional)

Requiere Java instalado y ejecutar en orden:

```bash
python bigdata/01_generar_dataset.py
python bigdata/02_limpieza.py
python bigdata/03_agregaciones.py
```
