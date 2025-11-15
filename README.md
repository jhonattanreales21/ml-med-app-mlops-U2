# MLOps Medical App — Streamlit Demo

Esta aplicación es una **simulación de un modelo médico** desarrollado en Streamlit.  
El objetivo es predecir un **estado de enfermedad** (leve, aguda, crónica o no enfermo) a partir de datos básicos del paciente.  
La lógica se implementa mediante reglas definidas en el archivo `rules.py`.

> ⚠️ **Aviso:** Este proyecto es únicamente para fines educativos y de demostración de MLOps / prototipado.  

---

## 1. Estructura principal del proyecto

- `app.py` → Aplicación web en Streamlit (UI + llamada a las reglas).
- `rules.py` → Lógica de negocio / reglas determinísticas para clasificar el estado.
- `requirements.txt` → Dependencias de Python.
- `Dockerfile` → Definición del contenedor Docker para desplegar la app.
- `index.html` → (Opcional/legacy) Plantilla usada en la versión anterior en Flask.

--- 

## 2. Requisitos previos

- Tener instalado **Docker**  
  o, para ejecución local sin Docker:
- **Python 3.11** (o compatible) y `pip`.

---


## 3. Ejecución local (sin Docker)

Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar la aplicación Streamlit:

```bash
streamlit run app.py
```

Por defecto, Streamlit levantará la app en:
- http://localhost:8501, o en su defecto http://localhost:8502

---

## 4. Construir la imagen Docker

Desde la raíz del proyecto (donde está el Dockerfile):

```bash
docker build -t mlops-medical-app .
```

Este comando levanta una imagen con python:3.11, instala flask, copia el codigo fuente necesario para la app y expone el puerto 8000.


## 5. Ejecutar el contenedor Docker.

```bash
docker run -p 8000:8000 mlops-medical-app
```

Este comando mapea el puerto local 8000 al del contenedor y disponibiliza la app para ser accedida desde el navegador.  
Opcionalmente, se puede utilizar el flag "-d" antes de "-p" para correr el contenedor en segundo plano, y el flag "--name" despues de asignar los puertos para asignar un nombre al contenedor. Es decir:


```bash
docker run -d -p 8000:8000 --name medical-app mlops-medical-app
```

Una vez la aplicación este corriendo, estará disponible en:
http://localhost:8000

---

## 6. Funcionalidad - Como obtener resultados?

Una vez se encuentre en la aplicación, notará un formulario. Para obtener las predicciones/respuestas de la solución, por favor ingrese la información solicitada y presiona en el boton "predecir". Este recibe los siguientes parámetros:

| Parámetro | Tipo | Descripción |
|------------|------|-------------|
| `age` | int | Edad del paciente |
| `severity` | float | Severidad de síntomas (0 a 10) |
| `duration_days` | int | Días de duración de los síntomas |

La respuesta contiene:
- El **estado clínico** estimado (`NO ENFERMO`, `LEVE`, `AGUDA`, `CRÓNICA`)
- Una **explicación textual**
- Los **valores de entrada** procesados

Puedes realizar cuantas predicciones necesites; la app recalculará al reenviar el formulario.
