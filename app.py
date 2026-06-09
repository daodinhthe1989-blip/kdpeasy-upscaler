import io
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="KDPEasy AI Upscaler",
    page_icon="🖼️",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .main > div { padding-top: 2rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%); }
    .block-container { max-width: 1200px; }
    h1 { color: #1f2937; font-weight: 700; }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover { background-color: #4338ca; color: white; }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }
    .stDownloadButton>button:hover { background-color: #059669; color: white; }
    div[data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #cbd5e1;
    }
    .info-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 1rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

TARGET_DPI = 300


def convert_to_300dpi(image: Image.Image, output_format: str, target_width_in: float | None = None):
    """Set DPI metadata to 300 and optionally resize to a target print width in inches."""
    img = image.copy()

    if target_width_in and target_width_in > 0:
        target_w_px = int(round(target_width_in * TARGET_DPI))
        aspect = img.height / img.width
        target_h_px = int(round(target_w_px * aspect))
        img = img.resize((target_w_px, target_h_px), Image.LANCZOS)

    buf = io.BytesIO()
    save_kwargs = {"dpi": (TARGET_DPI, TARGET_DPI)}

    if output_format == "JPG":
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=95, dpi=(TARGET_DPI, TARGET_DPI), optimize=True)
    else:
        img.save(buf, format="PNG", **save_kwargs)

    buf.seek(0)
    return buf, img.size


st.title("🖼️ KDPEasy AI Upscaler")
st.markdown(
    "<p style='color:#64748b;font-size:1.05rem;'>"
    "Convert your images to print-ready <b>300 DPI</b> for KDP and other publishing platforms."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload an image (JPG or PNG)",
    type=["jpg", "jpeg", "png"],
    help="Drag & drop or browse for a JPG/PNG file.",
)

if uploaded_file is None:
    st.markdown(
        "<div class='info-card'>"
        "<b>How it works</b><br>"
        "1. Upload a JPG or PNG image<br>"
        "2. (Optional) Choose your target print width in inches<br>"
        "3. Pick PNG or JPG output<br>"
        "4. Download your 300 DPI print-ready file"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    image = Image.open(uploaded_file)
    orig_w, orig_h = image.size
    orig_dpi = image.info.get("dpi", (72, 72))

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📷 Original")
        st.image(image, width="stretch")
        st.markdown(
            f"""
            <div class='info-card'>
                <b>Filename:</b> {uploaded_file.name}<br>
                <b>Dimensions:</b> {orig_w} × {orig_h} px<br>
                <b>Current DPI:</b> {int(orig_dpi[0])} × {int(orig_dpi[1])}<br>
                <b>Aspect ratio:</b> {orig_w / orig_h:.3f}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.subheader("⚙️ Settings")

        output_format = st.radio(
            "Output format",
            options=["PNG", "JPG"],
            horizontal=True,
            help="PNG keeps transparency; JPG is smaller in size.",
        )

        resize_for_print = st.checkbox(
            "Resize for a specific print width",
            value=False,
            help="Useful if you need an exact physical size at 300 DPI.",
        )

        target_width_in = None
        if resize_for_print:
            target_width_in = st.number_input(
                "Target print width (inches)",
                min_value=1.0,
                max_value=40.0,
                value=round(orig_w / 300, 2),
                step=0.5,
            )
            est_h_in = target_width_in * (orig_h / orig_w)
            st.caption(
                f"Estimated print size: **{target_width_in:.2f} × {est_h_in:.2f} in** "
                f"at 300 DPI (aspect ratio preserved)."
            )

        st.markdown("")

        if st.button("✨ Convert to 300 DPI", width="stretch"):
            with st.spinner("Converting…"):
                buf, new_size = convert_to_300dpi(image, output_format, target_width_in)
                st.session_state["converted"] = {
                    "buf": buf.getvalue(),
                    "format": output_format,
                    "size": new_size,
                    "name": uploaded_file.name.rsplit(".", 1)[0],
                }
            st.success("Done! Your image is ready for download.")

    if "converted" in st.session_state:
        st.markdown("---")
        st.subheader("✅ Converted Image")

        conv = st.session_state["converted"]
        new_w, new_h = conv["size"]
        ext = "png" if conv["format"] == "PNG" else "jpg"
        mime = "image/png" if conv["format"] == "PNG" else "image/jpeg"
        out_name = f"{conv['name']}_300dpi.{ext}"

        col_a, col_b = st.columns([1, 1], gap="large")
        with col_a:
            st.image(conv["buf"], caption="Preview", width="stretch")
        with col_b:
            st.markdown(
                f"""
                <div class='info-card'>
                    <b>Output:</b> {conv['format']}<br>
                    <b>Dimensions:</b> {new_w} × {new_h} px<br>
                    <b>DPI:</b> 300 × 300<br>
                    <b>Print size:</b> {new_w / 300:.2f} × {new_h / 300:.2f} in
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                label=f"⬇️ Download {conv['format']}",
                data=conv["buf"],
                file_name=out_name,
                mime=mime,
                width="stretch",
            )

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#94a3b8;font-size:0.85rem;'>"
    "Made for self-publishers • KDPEasy AI Upscaler"
    "</p>",
    unsafe_allow_html=True,
)
