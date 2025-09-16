import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
from functions import horas_laborales

# -------- Streamlit App --------
st.title("Calculadora de Horas Laborales")

opcion = st.radio(
    "Selecciona una opción:",
    ["1️⃣ Ingresar dos fechas", "2️⃣ Subir un Excel"]
)

# ---------------- OPCIÓN 1 ----------------
if opcion == "1️⃣ Ingresar dos fechas":
    st.subheader("Cálculo entre dos fechas")

    fecha_inicio = st.date_input("Fecha de inicio")
    hora_inicio_str = st.text_input("Hora de inicio (HH:MM o HH:MM:SS)", "08:00")
    fecha_fin = st.date_input("Fecha de fin")
    hora_fin_str = st.text_input("Hora de fin (HH:MM o HH:MM:SS)", "17:00")

    if st.button("Calcular diferencia"):
        try:
            hora_inicio = datetime.datetime.strptime(hora_inicio_str, "%H:%M:%S").time() \
                if len(hora_inicio_str.split(":")) == 3 \
                else datetime.datetime.strptime(hora_inicio_str, "%H:%M").time()

            hora_fin = datetime.datetime.strptime(hora_fin_str, "%H:%M:%S").time() \
                if len(hora_fin_str.split(":")) == 3 \
                else datetime.datetime.strptime(hora_fin_str, "%H:%M").time()

            dt_inicio = datetime.datetime.combine(fecha_inicio, hora_inicio)
            dt_fin = datetime.datetime.combine(fecha_fin, hora_fin)

            resultado = horas_laborales(dt_inicio, dt_fin)
            st.success(f"La diferencia es: {resultado:.2f} horas laborales")

        except ValueError:
            st.error("⚠️ Por favor ingresa la hora en formato válido (HH:MM o HH:MM:SS)")

# ---------------- OPCIÓN 2 ----------------
else:
    st.subheader("Subir un Excel con fechas")

    archivo = st.file_uploader("Sube un archivo Excel", type=["xlsx"])

    if archivo is not None:
        df = pd.read_excel(archivo)
        st.write("📊 Vista previa de los datos:")
        st.dataframe(df)

        columnas = df.columns.tolist()
        col_inicio = st.selectbox("Selecciona columna de inicio", columnas)
        col_fin = st.selectbox("Selecciona columna de fin", columnas)

        if st.button("Aplicar función"):
            # convertir a datetime por seguridad
            df[col_inicio] = pd.to_datetime(df[col_inicio], errors="coerce").dt.tz_localize(None)
            df[col_fin] = pd.to_datetime(df[col_fin], errors="coerce").dt.tz_localize(None)

            df["Horas Laborales"] = df.apply(
                lambda x: horas_laborales(x[col_inicio], x[col_fin])
                if pd.notnull(x[col_inicio]) and pd.notnull(x[col_fin]) else None,
                axis=1
            )

            st.success("✅ Cálculo realizado")
            st.dataframe(df)

            # ---- Descarga ----
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Resultados")
                processed_data = output.getvalue()
                return processed_data

            st.download_button(
                label="📥 Descargar Excel con resultados",
                data=to_excel(df),
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )