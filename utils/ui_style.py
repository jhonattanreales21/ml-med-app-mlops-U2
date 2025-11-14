import streamlit as st

# === Paleta de color ===
PRIMARY_RED = "#C62828"  # Rojo principal (botones, títulos)
SECONDARY_RED = "#E53935"  # Rojo claro (enlaces, resaltados)
LIGHT_RED = "#FDECEA"  # Fondo suave para tarjetas o alertas
YELLOW_ACCENT = "#FFCA28"  # Amarillo cálido para acentos
LIGHT_GRAY = "#F9F6F6"  # Fondo general neutro rosado/grisáceo
DARK_GRAY = "#3A3A3A"  # Texto principal
MID_GRAY = "#7D7D7D"  # Texto secundario
WHITE = "#FFFFFF"  # Elementos blancos


def header():
    st.title("Clasificador de Enfermedades")
    st.write(
        """
    Esta aplicación simula un **modelo médico basado en reglas**.
    Ingresa los datos del paciente y obtendrás un estado estimado junto con una breve explicación.
    """
    )


def style_cards():
    """Add card-like styling for containers or dataframes (soft shadow and rounded corners)."""
    st.markdown(
        f"""
        <style>
        .stDataFrame, .stTable {{
            border-radius: 12px;
            background-color: {WHITE};
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }}
        .stContainer {{
            padding: 22px !important;
            border: 1px solid #dcdcdc;
            border-radius: 12px;
            background-color: #f9f9f9;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            margin-top: 20px;
            margin-bottom: 30px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_sidebar():
    """Style sidebar area: background, button color, and spacing."""
    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background-color: {LIGHT_RED};
            color: {DARK_GRAY};
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {PRIMARY_RED};
            color: {WHITE};
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
