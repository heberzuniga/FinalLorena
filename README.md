# Bienestar & Belleza — Streamlit (Failsafe)

- `show_image()` con 3 rutas: numpy → bytes → HTML base64.
- Fuentes Unicode (DejaVu/Noto/Arial) o limpieza ASCII si falta TTF.
- Compatible con versiones de Streamlit sin `border=`.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cloud
Sube a GitHub y apunta a `app.py`.
