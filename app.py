import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import streamlit as st
from rules import PatientInput, predict_state

from utils.ui_data import log_prediction, load_stats
from utils.ui_style import style_cards, style_sidebar, header

style_cards()
style_sidebar()

# Valores de sesión base
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False
    submitted = False

# Configuración básica de la página
st.set_page_config(
    page_title="Clasificador de Enfermedades",
    page_icon="🏥",
    layout="centered",
)

st.sidebar.title("Navegación")
mode = st.sidebar.radio("Seleccionar vista", ["Realizar predicción", "Ver reporte"])

st.sidebar.markdown("---")

if mode == "Realizar predicción":
    # Mostrar formulario solo si no se ha enviado aún
    if not st.session_state["form_submitted"]:
        header()
        with st.form("patient_form"):
            st.markdown("### Datos del paciente")

            age = st.number_input(
                "Edad (años)",
                min_value=0,
                max_value=120,
                value=30,
                step=1,
                key="age_input",
            )
            severity = st.slider(
                "Severidad de síntomas (0–10)",
                min_value=0.0,
                max_value=10.0,
                value=5.0,
                step=0.1,
                key="severity_input",
            )
            duration_days = st.number_input(
                "Duración de los síntomas (días)",
                min_value=0,
                max_value=3650,
                value=10,
                step=1,
                key="duration_input",
            )

            # Preguntas de tipo Checkbox
            st.markdown("---")
            st.markdown("### Información adicional")
            st.markdown("Por favor, responde las siguientes preguntas si aplica:")

            has_chronic_disease = st.checkbox(
                "4. ¿El paciente tiene una **enfermedad crónica** diagnosticada? (p.ej. cáncer, EPOC, insuficiencia cardíaca)",
                key="chronic_disease_input",
            )

            has_metastasis = st.checkbox(
                "5. ¿Se conoce **enfermedad metastásica** o compromiso avanzado de órganos vitales?",
                key="metastasis_input",
            )

            recent_weight_loss = st.checkbox(
                "6. ¿Ha tenido **pérdida de peso significativa** reciente (>5% en los últimos 3 meses)?",
                key="weight_loss_input",
            )

            is_bedridden = st.checkbox(
                "7. ¿Permanece la mayor parte del día **encamado** o con movilidad muy reducida?",
                key="bedridden_input",
            )

            refractory_pain = st.checkbox(
                "8. ¿Presenta **dolor intenso** a pesar de un tratamiento analgésico adecuado?",
                key="refractory_pain_input",
            )

            multiple_organ_failure = st.checkbox(
                "9. ¿Hay evidencia de **falla de más de un órgano mayor** (renal, hepático, respiratorio, etc.)?",
                key="multiple_organ_failure_input",
            )

            # Imagen diagnóstica reciente
            st.markdown("---")
            st.markdown("### Imagen diagnóstica (opcional)")

            image_file = st.file_uploader(
                "Cargar imagen diagnóstica más reciente (formato .jpg / .jpeg / .png, opcional)",
                type=["jpg", "jpeg", "png"],
                key="image_file_input",
            )

            # Si no se ha enviado el formulario aún, mostrar el botón de envío
            st.markdown("")
            submitted = st.form_submit_button("Predecir estado", type="secondary")
            if submitted:
                st.session_state["form_submitted"] = True
                st.rerun()

    # Mostrar resultados si el formulario fue enviado
    elif st.session_state["form_submitted"]:
        header()

        with st.form("result_form"):
            # Logica para limpiar el formulario
            if st.form_submit_button("Nueva predicción", type="primary"):
                for key in [
                    "age_input",
                    "severity_input",
                    "duration_input",
                    "chronic_disease_input",
                    "metastasis_input",
                    "weight_loss_input",
                    "bedridden_input",
                    "refractory_pain_input",
                    "multiple_organ_failure_input",
                    "image_file_input",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state["form_submitted"] = False
                st.rerun()

            # Construir el objeto PatientInput y "predecir"
            has_recent_imaging = st.session_state.get("image_file_input") is not None

            try:
                patient = PatientInput(
                    age=int(st.session_state.get("age_input")),
                    severity=float(st.session_state.get("severity_input")),
                    duration_days=int(st.session_state.get("duration_input")),
                    has_chronic_disease=bool(
                        st.session_state.get("chronic_disease_input")
                    ),
                    has_metastasis=bool(st.session_state.get("metastasis_input")),
                    recent_weight_loss=bool(st.session_state.get("weight_loss_input")),
                    is_bedridden=bool(st.session_state.get("bedridden_input")),
                    refractory_pain=bool(st.session_state.get("refractory_pain_input")),
                    multiple_organ_failure=bool(
                        st.session_state.get("multiple_organ_failure_input")
                    ),
                    has_recent_imaging=bool(has_recent_imaging),
                )
                state, explanation = predict_state(patient)

                with st.expander("Ver detalle de los datos de entrada"):
                    st.json(
                        {
                            "age": patient.age,
                            "severity": patient.severity,
                            "duration_days": patient.duration_days,
                            "has_chronic_disease": patient.has_chronic_disease,
                            "has_metastasis": patient.has_metastasis,
                            "recent_weight_loss": patient.recent_weight_loss,
                            "is_bedridden": patient.is_bedridden,
                            "refractory_pain": patient.refractory_pain,
                            "multiple_organ_failure": patient.multiple_organ_failure,
                            "has_recent_imaging": patient.has_recent_imaging,
                        }
                    )

                if state == "NO ENFERMO":
                    st.success(f"✅ Estado estimado: **{state}**")
                elif state in ["ENFERMEDAD CRÓNICA", "ENFERMEDAD AGUDA"]:
                    st.error(f"❗️ Estado estimado: **{state}**")
                elif state == "ENFERMEDAD TERMINAL":
                    st.error(f"🛑 Estado estimado: **{state}**")
                else:
                    st.info(f"🔵 Estado estimado: **{state}**")

                st.markdown(f"**Explicación:** {explanation}")

                # Registrar la predicción en el log
                log_prediction(state, explanation, patient)

                if st.session_state.get("image_file_input") is not None:
                    st.info(
                        "**Doctor:** Se ha cargado una imagen diagnóstica reciente. "
                        "Es necesario revisarla manualmente antes de tomar cualquier decisión clínica."
                    )

                    with st.expander("Ver imagen diagnóstica cargada"):
                        st.image(
                            st.session_state.get("image_file_input"),
                            caption="Imagen diagnóstica cargada (vista previa)",
                            use_container_width=True,
                        )

            except Exception as e:
                st.error(f"Ocurrió un error al calcular la predicción: {e}")

    st.markdown("")
    [col1, col2, col3] = st.columns([3, 4, 3])  # Espaciar el botón al centro
    try:
        with col2:
            df = pd.read_json("predictions_log.jsonl", lines=True)
            st.download_button(
                "Descargar listado de predicciones",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="Reporte.csv",
                mime="text/csv",
                type="secondary",
            )
    except (FileNotFoundError, ValueError) as e:
        st.info(
            "No hay predicciones registradas aún. Realiza una predicción para generar el reporte."
        )
    except Exception as e:
        st.error(f"Ocurrió un error al descargar el informe. \nDetalles: {e}")

    st.markdown("---")
    st.caption("Demo de MLOps / prototipado de modelo médico basado en reglas.")

# --- Vista de reporte ---
elif mode == "Ver reporte":
    st.title("Reporte de predicciones")

    stats = load_stats()

    total_by_state = stats["total_by_state"]
    last_five = stats["last_five"]
    last_timestamp = stats["last_timestamp"]

    if not total_by_state and not last_five:
        st.info(
            "Aún no hay predicciones registradas. Realiza algunas predicciones primero."
        )
    else:
        view = st.segmented_control(
            "Escoja la vista:",
            ["Estadísticas", "Predicciones"],
            default="Estadísticas",
        )

        st.markdown("---")

        if view == "Predicciones":
            try:
                df = pd.read_json("predictions_log.jsonl", lines=True)
                st.dataframe(
                    df.sort_values(by="timestamp", ascending=False),
                    width="content",
                )
            except Exception as e:
                st.error(f"Ocurrió un error al cargar la tabla de predicciones: {e}")

        else:
            st.subheader("Número total de predicciones por categoría")

            for state, count in total_by_state.items():
                st.write(f"- **{state}**: {count} predicción(es)")

            st.markdown("### Últimas 5 predicciones")
            for rec in reversed(last_five):  # más reciente primero
                st.markdown(
                    f"- `{rec.get('timestamp')}` — **{rec.get('state')}** "
                    f"(edad: {rec.get('inputs', {}).get('age')}, "
                    f"sev: {rec.get('inputs', {}).get('severity')}, "
                    f"días: {rec.get('inputs', {}).get('duration_days')})"
                )

            st.markdown("### Fecha de la última predicción")
            if last_timestamp:
                st.write(f"📅 Última predicción registrada: `{last_timestamp}` (UTC)")
            else:
                st.write("No se pudo determinar la fecha de la última predicción.")

    st.markdown("---")
    st.caption(
        "El reporte se genera a partir de las predicciones almacenadas en el archivo de logs."
    )
