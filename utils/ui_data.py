# app.py
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from rules import PatientInput

# Archivo donde se guardan las predicciones (dentro del contenedor /app)
LOG_FILE = Path("predictions_log.jsonl")


def log_prediction(state: str, explanation: str, patient: PatientInput) -> None:
    """Append una predicción al archivo JSON Lines."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "state": state,
        "explanation": explanation,
        "inputs": {
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
        },
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_stats():
    """Leer el log y calcular las estadísticas solicitadas."""
    if not LOG_FILE.exists():
        return {
            "total_by_state": {},
            "last_five": [],
            "last_timestamp": None,
        }

    records = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # ignorar líneas corruptas
                continue

    total_by_state = {}
    last_timestamp = None
    for rec in records:
        state = rec.get("state")
        total_by_state[state] = total_by_state.get(state, 0) + 1
        ts = rec.get("timestamp")
        if ts:
            if last_timestamp is None or ts > last_timestamp:
                last_timestamp = ts

    # Últimas 5 predicciones (las últimas del archivo)
    last_five = records[-5:] if len(records) >= 5 else records

    return {
        "total_by_state": total_by_state,
        "last_five": last_five,
        "last_timestamp": last_timestamp,
    }
