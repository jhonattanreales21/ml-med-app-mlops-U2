# rules.py
from dataclasses import dataclass


@dataclass
class PatientInput:
    age: int  # años
    severity: float  # severidad de síntomas 0–10
    duration_days: int  # duración de síntomas en días
    has_chronic_disease: bool  # enfermedad crónica diagnosticada
    has_metastasis: bool  # metástasis / enfermedad muy avanzada
    recent_weight_loss: bool  # pérdida de peso importante reciente
    is_bedridden: bool  # pasa la mayor parte del día encamado
    refractory_pain: bool  # dolor intenso pese a tratamiento
    multiple_organ_failure: bool  # falla de ≥2 órganos

    has_recent_imaging: bool  # ¿se cargó imagen diagnóstica reciente?


# Estados posibles
NO_ENFERMO = "NO ENFERMO"
LEVE = "ENFERMEDAD LEVE"
AGUDA = "ENFERMEDAD AGUDA"
CRONICA = "ENFERMEDAD CRÓNICA"
TERMINAL = "ENFERMEDAD TERMINAL"


def predict_state(inp: PatientInput) -> tuple[str, str]:
    """
    Simula la predicción del modelo usando reglas simples.
    Devuelve (estado, explicación).

    Lógica (orden importante):
    - Si la duración > 30 días ⇒ CRÓNICA
    - Si severidad ≥ 6 y duración ≤ 30 ⇒ AGUDA
    - Si severidad ∈ [3,5] y duración ≤ 7 ⇒ LEVE
    - Si severidad ≤ 2 y duración ≤ 2 y edad < 65 ⇒ NO ENFERMO
    - En cualquier otro caso, por seguridad clínica mínima ⇒ LEVE

    Retorna: (estado, explicación)
    """
    age = inp.age
    sev = inp.severity
    dur = inp.duration_days

    # Validaciones básicas
    if age < 0 or dur < 0 or not (0 <= sev <= 10):
        raise ValueError(
            "Entradas inválidas: age>=0, duration_days>=0, severity en [0,10]."
        )

    # --- Reglas para ENFERMEDAD TERMINAL ---
    red_flags = sum(
        [
            inp.has_metastasis,
            inp.multiple_organ_failure,
            inp.is_bedridden,
            inp.refractory_pain,
            inp.has_chronic_disease,
            inp.recent_weight_loss,
        ]
    )
    razones = []
    if inp.has_metastasis:
        razones.append("metástasis")
    if inp.multiple_organ_failure:
        razones.append("fallo multiorgánico")
    if inp.is_bedridden:
        razones.append("paciente encamado")
    if inp.refractory_pain:
        razones.append("dolor refractario")
    if inp.has_chronic_disease:
        razones.append("enfermedad crónica de base")
    if inp.recent_weight_loss:
        razones.append("pérdida de peso significativa")

    long_course = dur > 180 or (dur > 90 and inp.has_chronic_disease)

    if sev >= 8 and red_flags >= 2 and long_course:
        explicacion = (
            "Síntomas muy intensos y curso prolongado con varios criterios de mal pronóstico "
            f"({', '.join(razones)}). Se clasifica como ENFERMEDAD TERMINAL."
        )

        if inp.has_recent_imaging:
            explicacion += " Existen imágenes diagnósticas recientes que deben revisarse en detalle por el médico."

        return TERMINAL, explicacion

    elif red_flags >= 4:
        return (
            TERMINAL,
            "Múltiples criterios de mal pronóstico presentes; se clasifica como ENFERMEDAD TERMINAL.",
        )

    # --- Reglas para ENFERMEDAD CRÓNICA ---
    if dur > 30 and inp.has_chronic_disease:
        return (
            CRONICA,
            "Síntomas >30 días en paciente con enfermedad crónica de base sugieren condición crónica.",
        )

    if dur > 60:
        return CRONICA, "Síntomas prolongados (>60 días) sugieren curso crónico."

    # --- Reglas para ENFERMEDAD AGUDA ---
    if sev >= 6:
        return AGUDA, "Alta severidad con duración corta-media sugiere cuadro agudo."

    # --- Reglas para ENFERMEDAD LEVE / NO ENFERMO ---
    if 3 <= sev <= 5 and dur <= 7:
        return (
            LEVE,
            "Severidad moderada y pocos días: cuadro leve y autolimitado probable.",
        )

    if sev <= 2 and dur <= 2 and age < 65 and not inp.has_chronic_disease:
        return (
            NO_ENFERMO,
            "Síntomas muy leves y breves en persona sin comorbilidad importante.",
        )

    # Caso por defecto
    return LEVE, "Caso fuera de reglas estrictas; se clasifica como leve por seguridad."
