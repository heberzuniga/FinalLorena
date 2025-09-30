# Bienestar & Belleza — Streamlit (Ultimate Compat)

- Usa DejaVuSans si está disponible (Pillow suele incluirla) para evitar UnicodeEncodeError.
- Si no existe TTF, limpia caracteres no ASCII cuando se dibuja texto en imágenes.
- `st.image` siempre recibe bytes PNG.
- Cards compatibles con versiones sin `border=`.

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cloud
Sube a GitHub y crea la app apuntando a `app.py`.
