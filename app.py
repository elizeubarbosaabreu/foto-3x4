import streamlit as st
from rembg import remove
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="Foto 3x4", page_icon="📷")

st.title("📷 Gerador de Foto 3x4")
st.markdown("Faça upload de uma foto e gere uma foto 3x4 com fundo branco.")

ASPECT = 3 / 4

uploaded = st.file_uploader("Envie uma foto", type=["png", "jpg", "jpeg", "webp"])

if uploaded:
    img = Image.open(uploaded).convert("RGBA")

    with st.spinner("Removendo fundo e detectando rosto..."):
        nobg = remove(img)

        alpha = np.array(nobg.split()[-1])
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)

        if rows.any() and cols.any():
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]

            person_h = rmax - rmin
            person_cx = (cmin + cmax) / 2
            face_cy = rmin + person_h * 0.2

            crop_h = min(img.height, int(img.width / ASPECT))
            crop_w = int(crop_h * ASPECT)

            if crop_h > person_h * 1.1:
                crop_h = int(person_h * 1.15)
                crop_w = int(crop_h * ASPECT)

            x = int(person_cx - crop_w / 2)
            y = int(face_cy - crop_h * 0.25)

            x = max(0, min(x, img.width - crop_w))
            y = max(0, min(y, img.height - crop_h))

            if x + crop_w > img.width:
                x = img.width - crop_w
            if y + crop_h > img.height:
                y = img.height - crop_h

            cropped = img.crop((x, y, x + crop_w, y + crop_h))
            cropped_nobg = remove(cropped)

            white_bg = Image.new("RGBA", cropped_nobg.size, (255, 255, 255, 255))
            white_bg.paste(cropped_nobg, mask=cropped_nobg.split()[3])
            final = white_bg.convert("RGB")
        else:
            crop_h = min(img.height, int(img.width / ASPECT))
            crop_w = int(crop_h * ASPECT)
            x = (img.width - crop_w) // 2
            y = (img.height - crop_h) // 3
            cropped = img.crop((x, y, x + crop_w, y + crop_h))
            cropped_nobg = remove(cropped)
            white_bg = Image.new("RGBA", cropped_nobg.size, (255, 255, 255, 255))
            white_bg.paste(cropped_nobg, mask=cropped_nobg.split()[3])
            final = white_bg.convert("RGB")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(img, width="stretch")
    with col2:
        st.subheader("Foto 3x4")
        st.image(final, width="stretch")

    buf = io.BytesIO()
    final.save(buf, format="JPEG", quality=95)
    st.download_button(
        "📥 Baixar Foto 3x4",
        buf.getvalue(),
        "foto_3x4.jpg",
        "image/jpeg",
    )

st.divider()
st.link_button("🌐 Visite meu site", "https://elizeubarbosa.com.br/", use_container_width=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://ebook-ste-com-python-e-streamlit.vercel.app/images/capa.jpg", width=200)
    st.caption("Aprenda a criar seus próprios apps com Python e Streamlit no ebook [Criação de Apps Web com Python e Streamlit](https://ebook-ste-com-python-e-streamlit.vercel.app/).")
