# app.py (failsafe)
# ------------------------------------------------------------
# Bienestar & Belleza — Streamlit (Failsafe)
# - show_image(): intenta st.image con numpy array; si falla, usa HTML base64.
# - Fuentes Unicode (DejaVu/Noto/Arial) o limpieza ASCII si no hay TTF.
# - Cards compatibles (border fallback).
# ------------------------------------------------------------

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
import math
import random
import base64
import numpy as np
from contextlib import contextmanager

st.set_page_config(
    page_title="Bienestar & Belleza",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#7C3AED"
PRIMARY_SOFT = "#EDE9FE"
STAR = "⭐"
HEART = "💜"
CHECK = "✅"

def css():
    st.markdown(
        f"""
        <style>
            .hero {{
                background: linear-gradient(135deg, {PRIMARY} 0%, #C084FC 100%);
                color: white;
                padding: 48px 28px;
                border-radius: 18px;
            }}
            .tag {{
                display:inline-block;
                padding: 4px 10px;
                border-radius: 999px;
                background: {PRIMARY_SOFT};
                color: {PRIMARY};
                font-weight: 600;
                font-size: 12px;
                margin-right: 6px;
            }}
            .price {{
                font-weight: 700;
                font-size: 18px;
                color: {PRIMARY};
            }}
            footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
css()

# ---------- Compat helpers ----------
@contextmanager
def card():
    try:
        with st.container(border=True):
            yield
    except TypeError:
        with st.container():
            yield

def to_png_bytes(img: Image.Image) -> bytes:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def show_image(img: Image.Image, use_container_width=True):
    """Muestra imagen con múltiples rutas de compatibilidad."""
    try:
        # 1) Intentar como arreglo numpy (muy compatible con st.image)
        arr = np.array(img.convert("RGB"))
        return st.image(arr, use_container_width=use_container_width)
    except Exception:
        pass
    try:
        # 2) Intentar bytes PNG
        png = to_png_bytes(img)
        return st.image(png, use_container_width=use_container_width)
    except Exception:
        pass
    # 3) Fallback HTML base64
    try:
        png = to_png_bytes(img)
        b64 = base64.b64encode(png).decode("ascii")
        st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;height:auto;border-radius:12px;" />', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"No se pudo mostrar la imagen: {e}")

def try_load_font(name: str, size: int):
    try:
        return ImageFont.truetype(name, size), True
    except Exception:
        return None, False

def load_fonts():
    for fname in ("DejaVuSans.ttf", "NotoSans-Regular.ttf", "Arial.ttf", "arial.ttf"):
        f, ok = try_load_font(fname, 48)
        if ok:
            f_title = f
            f_sub, ok2 = try_load_font(fname, 22)
            if not ok2:
                f_sub = f_title
            return f_title, f_sub, True
    return ImageFont.load_default(), ImageFont.load_default(), False

def safe_text(text: str, unicode_ok: bool) -> str:
    if text is None:
        return None
    if unicode_ok:
        return text
    # quitar no-ASCII
    return text.encode("ascii", "ignore").decode("ascii")

# ---------- Generación de imágenes ----------
def gradient_image(size=(800, 600), c1=(124, 58, 237), c2=(20, 184, 166)):
    w, h = size
    base = Image.new("RGB", size, c1)
    top = Image.new("RGB", size, c2)
    mask = Image.new("L", size)
    mask.putdata([int(255 * (y / h)) for y in range(h) for _ in range(w)])
    base.paste(top, (0, 0), mask)
    return base

def draw_text_center(img, text, subtitle=None):
    draw = ImageDraw.Draw(img)
    font_title, font_sub, unicode_ok = load_fonts()
    text = safe_text(text, unicode_ok)
    subtitle = safe_text(subtitle, unicode_ok)

    W, H = img.size
    max_width = int(W * 0.85)

    # Wrap título
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        try:
            width = draw.textlength(test, font=font_title)
        except Exception:
            width = len(test) * 10
        if width <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    total_h = len(lines) * 56 + (34 if subtitle else 0)
    y = (H - total_h) // 2

    for ln in lines:
        try:
            w = draw.textlength(ln, font=font_title)
        except Exception:
            w = len(ln) * 10
        draw.text(((W - w) / 2, y), ln, fill="white", font=font_title)
        y += 56

    if subtitle:
        try:
            w = draw.textlength(subtitle, font=font_sub)
        except Exception:
            w = len(subtitle) * 8
        draw.text(((W - w) / 2, y + 8), subtitle, fill="white", font=font_sub)
    return img

def product_image(title, color1, color2, overlay=""):
    img = gradient_image((720, 480), color1, color2)
    if overlay:
        title = f"{title}\n{overlay}"
    return draw_text_center(img, title)

def hero_image():
    subtitle = "Cuidado de la piel • Cabello • Spa • Maquillaje • Fitness"
    img = gradient_image((1800, 520), (124, 58, 237), (192, 132, 252))
    return draw_text_center(img, "Bienestar & Belleza", subtitle)

# ---------- Datos ----------
random.seed(42)
CATEGORIES = ["Cuidado de la Piel","Cabello","Spa & Aromaterapia","Maquillaje","Fitness & Wellness"]

PALETTE = {
    "Cuidado de la Piel": ((244,114,182),(251,191,36)),
    "Cabello": ((56,189,248),(99,102,241)),
    "Spa & Aromaterapia": ((16,185,129),(59,130,246)),
    "Maquillaje": ((244,63,94),(168,85,247)),
    "Fitness & Wellness": ((34,197,94),(20,184,166)),
}

PRODUCTS = [
    {"id":"SK-01","name":"Serum Vitamina C 15%","desc":"Ilumina y unifica el tono.","price":119.0,"rating":4.8,"cat":"Cuidado de la Piel"},
    {"id":"SK-02","name":"Hidratante Hyaluron 3D","desc":"Hidratación profunda 24h.","price":99.0,"rating":4.7,"cat":"Cuidado de la Piel"},
    {"id":"SK-03","name":"Protector Solar SPF 50+","desc":"Textura ligera, no graso.","price":89.0,"rating":4.9,"cat":"Cuidado de la Piel"},
    {"id":"SK-04","name":"Limpieza Enzimática","desc":"Suave con la barrera cutánea.","price":79.0,"rating":4.6,"cat":"Cuidado de la Piel"},
    {"id":"HB-01","name":"Shampoo Fortify+","desc":"Reduce la caída, brillo natural.","price":59.0,"rating":4.5,"cat":"Cabello"},
    {"id":"HB-02","name":"Acondicionador Nutrify","desc":"Puntas selladas y suaves.","price":62.0,"rating":4.6,"cat":"Cabello"},
    {"id":"HB-03","name":"Mascarilla Keratin Pro","desc":"Reparación intensa.","price":85.0,"rating":4.8,"cat":"Cabello"},
    {"id":"HB-04","name":"Aceite Capilar Ligero","desc":"Frizz-control, acabado seda.","price":70.0,"rating":4.7,"cat":"Cabello"},
    {"id":"SP-01","name":"Difusor Ultrasónico","desc":"Ambiente relajante inmediato.","price":140.0,"rating":4.7,"cat":"Spa & Aromaterapia"},
    {"id":"SP-02","name":"Set 3 Aceites Esenciales","desc":"Lavanda, Eucalipto, Citrus.","price":95.0,"rating":4.6,"cat":"Spa & Aromaterapia"},
    {"id":"SP-03","name":"Sales de Baño Mineral","desc":"Descontracturante natural.","price":55.0,"rating":4.4,"cat":"Spa & Aromaterapia"},
    {"id":"SP-04","name":"Vela Aromática Premium","desc":"Cera de soya, 50h.","price":60.0,"rating":4.5,"cat":"Spa & Aromaterapia"},
    {"id":"MK-01","name":"Base HD Soft-Matte","desc":"Cobertura media, larga duración.","price":130.0,"rating":4.7,"cat":"Maquillaje"},
    {"id":"MK-02","name":"Paleta Sombras 12","desc":"Mate & shimmer balanceado.","price":110.0,"rating":4.6,"cat":"Maquillaje"},
    {"id":"MK-03","name":"Máscara Volumen 3D","desc":"Pestañas elevadas y densas.","price":72.0,"rating":4.6,"cat":"Maquillaje"},
    {"id":"MK-04","name":"Labial Suede Long-Wear","desc":"Color intenso 12h.","price":65.0,"rating":4.5,"cat":"Maquillaje"},
    {"id":"FT-01","name":"Colágeno + Vitamina C","desc":"Soporte articular y piel.","price":120.0,"rating":4.5,"cat":"Fitness & Wellness"},
    {"id":"FT-02","name":"Proteína Whey 900g","desc":"Recovery & lean mass.","price":180.0,"rating":4.7,"cat":"Fitness & Wellness"},
    {"id":"FT-03","name":"Mat de Yoga Antideslizante","desc":"Con bolsa, 6mm.","price":95.0,"rating":4.6,"cat":"Fitness & Wellness"},
    {"id":"FT-04","name":"Banda Elástica Set 5","desc":"Resistencias progresivas.","price":68.0,"rating":4.5,"cat":"Fitness & Wellness"},
]

if "img_cache" not in st.session_state:
    st.session_state.img_cache = {}

def get_product_image(pid, title, cat):
    if pid in st.session_state.img_cache:
        return st.session_state.img_cache[pid]
    c1, c2 = PALETTE[cat]
    img = product_image(title, c1, c2, overlay="Bienestar & Belleza")
    st.session_state.img_cache[pid] = img
    return img

if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(pid, qty=1):
    st.session_state.cart[pid] = st.session_state.cart.get(pid, 0) + qty

def remove_from_cart(pid):
    if pid in st.session_state.cart:
        del st.session_state.cart[pid]

def empty_cart():
    st.session_state.cart = {}

def cart_total():
    total = 0.0
    for pid, qty in st.session_state.cart.items():
        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if prod:
            total += prod["price"] * qty
    return total

def cart_receipt():
    lines = []
    lines.append("=== Comprobante Bienestar & Belleza ===")
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("---------------------------------------")
    for pid, qty in st.session_state.cart.items():
        prod = next((p for p in PRODUCTS if p["id"] == pid), None)
        if not prod:
            continue
        lines.append(f"{prod['name']} x{qty}  Bs. {prod['price']:.2f} c/u  =  Bs. {prod['price']*qty:.2f}")
    lines.append("---------------------------------------")
    lines.append(f"TOTAL: Bs. {cart_total():.2f}")
    lines.append("¡Gracias por tu preferencia! 💜")
    return "\n".join(lines).encode()

# Sidebar
with st.sidebar:
    st.markdown("### Filtros")
    selected_cats = st.multiselect("Categorías", options=CATEGORIES, default=CATEGORIES)
    min_price = min(p["price"] for p in PRODUCTS)
    max_price = max(p["price"] for p in PRODUCTS)
    price_range = st.slider("Rango de precio (Bs.)", float(min_price), float(max_price), (float(min_price), float(max_price)))
    q = st.text_input("Buscar producto", placeholder="ej.: serum, proteína, vela…")
    st.markdown("---")
    st.markdown("### 🛒 Carrito")
    if st.session_state.cart:
        for pid, qty in st.session_state.cart.items():
            prod = next((p for p in PRODUCTS if p["id"] == pid), None)
            if not prod: continue
            cols = st.columns([3,1,1])
            with cols[0]:
                st.write(f"**{prod['name']}**")
                st.caption(f"Bs. {prod['price']:.2f} x {qty}")
            with cols[1]:
                if st.button("➖", key=f"minus_{pid}"):
                    st.session_state.cart[pid] = max(1, st.session_state.cart[pid]-1)
            with cols[2]:
                if st.button("🗑️", key=f"del_{pid}"):
                    remove_from_cart(pid)
        st.markdown(f"**Total:** Bs. {cart_total():.2f}")
        c1, c2 = st.columns(2)
        with c1:
            st.button("Vaciar", on_click=empty_cart)
        with c2:
            st.download_button("Descargar comprobante", data=cart_receipt(), file_name="comprobante.txt", mime="text/plain")
    else:
        st.caption("Tu carrito está vacío.")

# HERO
hero = hero_image()
st.markdown('<div class="hero">', unsafe_allow_html=True)
show_image(hero, use_container_width=True)
st.markdown(
    """
    <div style="margin-top:12px;">
        <span class="tag">Envíos 24-48h</span>
        <span class="tag">Pago seguro</span>
        <span class="tag">Garantía 30 días</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# Destacados
st.subheader(f"{HEART} Destacados de Hoy")
featured = random.sample(PRODUCTS, 6)
cols = st.columns(3)
for i, prod in enumerate(featured):
    with cols[i % 3]:
        with card():
            img = get_product_image(prod["id"], prod["name"], prod["cat"])
            show_image(img, use_container_width=True)
            st.markdown(f"**{prod['name']}**")
            st.caption(prod["desc"])
            st.markdown(f"{STAR * int(round(prod['rating']))} · {prod['rating']:.1f}")
            st.markdown(f"<span class='price'>Bs. {prod['price']:.2f}</span>", unsafe_allow_html=True)
            st.caption(f"Categoría: {prod['cat']}")
            st.button("Añadir al carrito", key=f"add_feat_{prod['id']}", on_click=add_to_cart, args=(prod["id"], 1))

st.markdown("---")

# Catálogo
st.subheader("Catálogo por Categorías")
def match_filters(prod):
    if prod["cat"] not in selected_cats: return False
    if not (price_range[0] <= prod["price"] <= price_range[1]): return False
    if q:
        text = f"{prod['name']} {prod['desc']}".lower()
        if q.lower().strip() not in text: return False
    return True

filtered = [p for p in PRODUCTS if match_filters(p)]
st.caption(f"Mostrando {len(filtered)} de {len(PRODUCTS)} productos.")

visible_cats = [c for c in CATEGORIES if any(p["cat"] == c for p in filtered)]
if not visible_cats:
    st.info("No hay productos que coincidan con los filtros actuales. Ajusta la búsqueda o el rango de precios.")
else:
    tabs = st.tabs(visible_cats)
    for idx, cat in enumerate(visible_cats):
        with tabs[idx]:
            cat_items = [p for p in filtered if p["cat"] == cat]
            rows = (len(cat_items) + 2) // 3
            for r in range(rows):
                row_items = cat_items[r*3:(r+1)*3]
                ccols = st.columns(3)
                for j, prod in enumerate(row_items):
                    with ccols[j]:
                        with card():
                            img = get_product_image(prod["id"], prod["name"], prod["cat"])
                            show_image(img, use_container_width=True)
                            st.markdown(f"**{prod['name']}**")
                            st.caption(prod["desc"])
                            st.markdown(f"{STAR * int(round(prod['rating']))} · {prod['rating']:.1f}")
                            st.markdown(f"<span class='price'>Bs. {prod['price']:.2f}</span>", unsafe_allow_html=True)
                            st.button("Añadir al carrito", key=f"add_{prod['id']}", on_click=add_to_cart, args=(prod["id"], 1))

st.markdown("---")

# Promos
st.subheader("Promos & Bundles")
promo_cols = st.columns(3)
promos = [
    {"title":"Rutina Glow (Piel)","items":["Serum Vitamina C 15%","Hidratante Hyaluron 3D","Protector Solar SPF 50+"],"price":279.0,"save":28.0,"cat":"Cuidado de la Piel","id":"PM-01"},
    {"title":"Cabello Radiante","items":["Shampoo Fortify+","Acondicionador Nutrify","Mascarilla Keratin Pro"],"price":179.0,"save":27.0,"cat":"Cabello","id":"PM-02"},
    {"title":"Spa en Casa","items":["Difusor Ultrasónico","Set 3 Aceites Esenciales","Vela Aromática Premium"],"price":259.0,"save":36.0,"cat":"Spa & Aromaterapia","id":"PM-03"},
]
for i, pm in enumerate(promos):
    with promo_cols[i]:
        c1, c2 = PALETTE[pm["cat"]]
        img = product_image(pm["title"], c1, c2, overlay="PROMO")
        with card():
            show_image(img, use_container_width=True)
            st.markdown(f"**{pm['title']}**")
            st.caption(" + ".join(pm["items"]))
            st.markdown(f"**Bs. {pm['price']:.2f}**  · Ahorras **Bs. {pm['save']:.2f}**")
            st.button("Añadir promo", key=f"add_{pm['id']}", on_click=add_to_cart, args=(pm["id"], 1))

if "promo_prices_injected" not in st.session_state:
    PRODUCTS.extend([
        {"id":"PM-01","name":"Bundle: Rutina Glow (Piel)","desc":"Set 3 pasos para piel luminosa.","price":279.0,"rating":4.8,"cat":"Cuidado de la Piel"},
        {"id":"PM-02","name":"Bundle: Cabello Radiante","desc":"Nutrición, fuerza y brillo.","price":179.0,"rating":4.7,"cat":"Cabello"},
        {"id":"PM-03","name":"Bundle: Spa en Casa","desc":"Ambiente relajante total.","price":259.0,"rating":4.7,"cat":"Spa & Aromaterapia"},
    ])
    st.session_state.promo_prices_injected = True

st.markdown("---")

# Testimonios
st.subheader("Testimonios")
tcols = st.columns(3)
testimonials = [
    ("María G.", "El serum de Vitamina C me cambió la piel. Textura ligera y efecto glow inmediato."),
    ("Carla R.", "El set de spa huele increíble, ideal para desconectarme después del trabajo."),
    ("Daniel A.", "La proteína y el mat de yoga: combo perfecto. Entrega rápida y todo impecable."),
]
for i, (name, text) in enumerate(testimonials):
    with tcols[i]:
        with card():
            avatar = gradient_image((720, 220), (200, 200, 255), (180, 240, 220))
            draw_text_center(avatar, f"{HEART} {name}", "")
            show_image(avatar, use_container_width=True)
            st.markdown(f"_{text}_")
            st.markdown(f"{CHECK} Compra verificada")

st.markdown("---")

with st.expander("Preguntas Frecuentes (FAQ)"):
    st.markdown("""
- **¿Hacen envíos?** Sí, a todo el país en 24-48 horas.
- **¿Puedo devolver un producto?** Claro, tienes 30 días con empaque original.
- **¿Los productos son originales?** 100% originales y con garantía del fabricante.
- **¿Métodos de pago?** Tarjetas, transferencias y billeteras digitales.
- **¿Piel sensible?** Recomendamos probar en una pequeña zona 24h antes de uso continuo.
    """)

st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Contáctanos")
    st.markdown("📧 hola@bienestarybelleza.example")
    st.markdown("📱 +591 700-00000")
with c2:
    st.markdown("### Horarios")
    st.markdown("Lun–Vie: 9:00–19:00  \nSáb: 9:00–13:00")
with c3:
    st.markdown("### Suscríbete")
    email = st.text_input("Tu correo", key="newsletter_email", placeholder="tu@correo.com")
    if st.button("Quiero recibir novedades"):
        if email and "@" in email:
            st.success("¡Te has suscrito! Bienvenida/o a la familia 💜")
        else:
            st.error("Por favor, ingresa un correo válido.")

st.caption("© 2025 Bienestar & Belleza — Hecho con Streamlit")
