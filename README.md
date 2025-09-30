# Bienestar & Belleza — Streamlit (Compat)
Versión compatible con más entornos de Streamlit/Pillow:
- Envia bytes a `st.image` (no objetos PIL).
- Evita `border=` en `st.container` cuando no está disponible.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cloud
Sube a GitHub y haz deploy el archivo `app.py`.
