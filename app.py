# app.py
import streamlit as st
from rules import PatientInput, predict_state

# Configuración básica de la página
st.set_page_config(
    page_title="Clasificador de Enfermedades",
    page_icon="🏥",
    layout="centered",
)

st.title("Clasificador de Enfermedades")
st.write(
    """
Esta aplicación simula un **modelo médico basado en reglas**.
Ingresa los datos del paciente y obtendrás un estado estimado junto con una breve explicación.
"""
)

# --- Formulario de entrada ---
with st.form("patient_form"):
    st.markdown("### Datos del paciente")

    age = st.number_input("Edad (años)", min_value=0, max_value=120, value=30, step=1)
    severity = st.slider(
        "Severidad de síntomas (0–10)",
        min_value=0.0,
        max_value=10.0,
        value=5.0,
        step=0.1,
    )
    duration_days = st.number_input(
        "Duración de los síntomas (días)", min_value=0, max_value=3650, value=10, step=1
    )

    # Preguntas de tipo Checkbox
    st.markdown("---")
    st.markdown("### Información adicional")
    st.markdown("Por favor, responde las siguientes preguntas si aplica:")

    has_chronic_disease = st.checkbox(
        "4. ¿El paciente tiene una **enfermedad crónica** diagnosticada? (p.ej. cáncer, EPOC, insuficiencia cardíaca)"
    )

    has_metastasis = st.checkbox(
        "5. ¿Se conoce **enfermedad metastásica** o compromiso avanzado de órganos vitales?"
    )

    recent_weight_loss = st.checkbox(
        "6. ¿Ha tenido **pérdida de peso significativa** reciente (>5% en los últimos 3 meses)?"
    )

    is_bedridden = st.checkbox(
        "7. ¿Permanece la mayor parte del día **encamado** o con movilidad muy reducida?"
    )

    refractory_pain = st.checkbox(
        "8. ¿Presenta **dolor intenso** a pesar de un tratamiento analgésico adecuado?"
    )

    multiple_organ_failure = st.checkbox(
        "9. ¿Hay evidencia de **falla de más de un órgano mayor** (renal, hepático, respiratorio, etc.)?"
    )

    # Imagen diagnóstica reciente
    st.markdown("---")
    st.markdown("### Imagen diagnóstica (opcional)")

    image_file = st.file_uploader(
        "Cargar imagen diagnóstica más reciente (formato .jpg / .jpeg, opcional)",
        type=["jpg", "jpeg"],
    )

    submitted = st.form_submit_button("Predecir estado")

# --- Lógica de predicción ---
if submitted:
    has_recent_imaging = image_file is not None

    try:
        patient = PatientInput(
            age=int(age),
            severity=float(severity),
            duration_days=int(duration_days),
            has_chronic_disease=bool(has_chronic_disease),
            has_metastasis=bool(has_metastasis),
            recent_weight_loss=bool(recent_weight_loss),
            is_bedridden=bool(is_bedridden),
            refractory_pain=bool(refractory_pain),
            multiple_organ_failure=bool(multiple_organ_failure),
            has_recent_imaging=bool(has_recent_imaging),
        )
        state, explanation = predict_state(patient)

        if state == "NO ENFERMO":
            st.success(f"✅ Estado estimado: **{state}**")
        elif state in ["ENFERMEDAD CRÓNICA", "ENFERMEDAD AGUDA"]:
            st.error(f"❗️ Estado estimado: **{state}**")
        elif state == "ENFERMEDAD TERMINAL":
            st.error(f"🛑 Estado estimado: **{state}**")
        else:
            st.info(f"🔵 Estado estimado: **{state}**")

        st.markdown(f"**Explicación:** {explanation}")

        if image_file is not None:
            st.info(
                "👨‍⚕️ **Doctor:** Se ha cargado una imagen diagnóstica reciente. "
                "Es necesario revisarla manualmente antes de tomar cualquier decisión clínica."
            )
            st.image(
                image_file,
                caption="Imagen diagnóstica cargada (vista previa)",
                use_column_width=True,
            )

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

    except Exception as e:
        st.error(f"⚠️ Ocurrió un error al calcular la predicción: {e}")

st.markdown("---")
st.caption("Demo de MLOps / prototipado de modelo médico basado en reglas.")
