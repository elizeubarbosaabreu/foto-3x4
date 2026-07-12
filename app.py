import streamlit as st
from rembg import remove
from PIL import Image
from fpdf import FPDF
import numpy as np
import io
import base64

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
    st.subheader("🖨️ Gerar PDF para Impressão")

    qtd = st.selectbox(
        "Quantidade de fotos",
        [1, 2, 4, 6, 8, 10, 12, 16, 20, 24],
        index=4,
    )

    if st.button("📄 Gerar PDF", use_container_width=True):
        pw, ph = 30, 40
        margin_y = 15
        page_w, page_h = 210, 297

        cols_pdf = int((page_w - 20) // pw)
        rows_pdf = int((page_h - 2 * margin_y) // ph)
        per_page = cols_pdf * rows_pdf

        grid_w = cols_pdf * pw
        margin_x = (page_w - grid_w) / 2

        photo_tmp = io.BytesIO()
        final.save(photo_tmp, format="JPEG", quality=75)
        photo_tmp.seek(0)

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(False)

        remaining = qtd
        while remaining > 0:
            pdf.add_page()
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.3)

            count = min(remaining, per_page)
            for i in range(count):
                col = i % cols_pdf
                row = i // cols_pdf
                px = margin_x + col * pw
                py = margin_y + row * ph

                pdf.rect(px, py, pw, ph)

                photo_tmp.seek(0)
                pdf.image(photo_tmp, x=px + 0.5, y=py + 0.5, w=pw - 1, h=ph - 1)

            remaining -= count

        pdf_buf = io.BytesIO()
        pdf.output(pdf_buf)
        pdf_buf.seek(0)

        pdf_bytes = pdf_buf.getvalue()
        st.session_state["pdf_data"] = pdf_bytes
        st.session_state["pdf_qtd"] = qtd

    if "pdf_data" in st.session_state:
        pdf_bytes = st.session_state["pdf_data"]
        qtd_saved = st.session_state["pdf_qtd"]
        filename = f"foto_3x4_{qtd_saved}fotos.pdf"

        st.download_button(
            f"📥 Baixar PDF ({qtd_saved} fotos)",
            pdf_bytes,
            filename,
            "application/pdf",
            use_container_width=True,
        )

        if len(pdf_bytes) < 500000:
            b64 = base64.b64encode(pdf_bytes).decode()
            st.markdown(
                f'<a href="data:application/pdf;base64,{b64}" download="{filename}" '
                f'style="display:block;text-align:center;padding:14px 28px;border-radius:12px;'
                f'background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:700;'
                f'font-size:1rem;text-decoration:none;margin-top:8px;">'
                f'📥 Baixar PDF (celular)</a>',
                unsafe_allow_html=True,
            )

st.divider()
st.link_button("🌐 Visite meu site", "https://elizeubarbosa.com.br/", use_container_width=True)
st.caption("© 2026 Prof. Elizeu Barbosa — Todos os direitos reservados.")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://ebook-ste-com-python-e-streamlit.vercel.app/images/capa.jpg", width=200)
    st.caption("Aprenda a criar seus próprios apps com Python e Streamlit no ebook [Criação de Apps Web com Python e Streamlit](https://ebook-ste-com-python-e-streamlit.vercel.app/).")
