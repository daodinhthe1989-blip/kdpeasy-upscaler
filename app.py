import io
import hashlib
import requests
from PIL import Image
import streamlit as st
import replicate

# ═══════════════════════════════════════════════════════════════════
# 🔐 SECURITY SETTINGS — Edit these values to customize your app
# ═══════════════════════════════════════════════════════════════════
APP_PASSWORD = "KDPVIP2026"   # Change this to your secret password
BRAND_NAME = "KDPEasy Studio"  # Change this to your brand name
WELCOME_MESSAGE = "Welcome, VIP Customer!"  # Customize this greeting
# ═══════════════════════════════════════════════════════════════════

# 🤖 AI Model Configuration
AI_MODEL = "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa"

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
    .ai-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
    }
    .login-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 480px;
        margin: 3rem auto;
        text-align: center;
    }
    .login-card h2 { color: #1f2937; margin-bottom: 0.5rem; }
    .login-card .brand {
        color: #4f46e5; font-weight: 700;
        font-size: 1.1rem; margin-bottom: 1.5rem;
    }
    .login-card .desc {
        color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔐 PASSWORD GATE
# ═══════════════════════════════════════════════════════════════════
def check_password():
    """Returns True if user has entered the correct password."""
    if st.session_state.get("password_correct", False):
        return True

    st.markdown(
        f"""
        <div class='login-card'>
            <h2>🔐 {WELCOME_MESSAGE}</h2>
            <div class='brand'>✨ {BRAND_NAME} ✨</div>
            <div class='desc'>
                This is an exclusive AI tool for our valued customers.<br>
                Please enter your access password to continue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input(
            "🔑 Access Password",
            type="password",
            placeholder="Enter your password here...",
            key="password_input",
        )

        if st.button("🚀 Unlock App", width="stretch"):
            if password == APP_PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please contact support if you need access.")

        st.markdown(
            "<p style='text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:2rem;'>"
            "💡 Don't have a password? This tool is exclusive to our email subscribers.<br>"
            "Contact us to get access."
            "</p>",
            unsafe_allow_html=True,
        )

    return False


if not check_password():
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# 🎨 MAIN APP
# ═══════════════════════════════════════════════════════════════════

TARGET_DPI = 300

# 📚 KDP Book Size Presets (width × height in inches)
KDP_BOOK_SIZES = {
    "🔧 Custom (enter your own size)": None,
    "📕 6 × 9 in — Trade Paperback (most popular)": (6.0, 9.0),
    "📗 5 × 8 in — Mass Market": (5.0, 8.0),
    "📘 5.5 × 8.5 in — Digest": (5.5, 8.5),
    "📙 7 × 10 in — Textbook": (7.0, 10.0),
    "📓 8 × 10 in — Children's Book": (8.0, 10.0),
    "🎨 8.5 × 11 in — Letter (Coloring Book)": (8.5, 11.0),
    "📒 A4 — 8.27 × 11.69 in": (8.27, 11.69),
    "📰 A5 — 5.83 × 8.27 in": (5.83, 8.27),
    "📔 8.5 × 8.5 in — Square (Photo Book)": (8.5, 8.5),
    "🖼️ 8 × 8 in — Square (Children's)": (8.0, 8.0),
}


def get_image_hash(img_bytes: bytes, suffix: str = "") -> str:
    """Generate hash for caching AI results."""
    return hashlib.md5(img_bytes + suffix.encode()).hexdigest()


def ai_upscale(image_bytes: bytes, scale: int) -> bytes:
    """Upscale image using Real-ESRGAN via Replicate API."""
    api_token = st.secrets.get("REPLICATE_API_TOKEN", None)
    if not api_token:
        raise ValueError(
            "AI service is not configured. Please contact support."
        )

    client = replicate.Client(api_token=api_token)

    output = client.run(
        AI_MODEL,
        input={
            "image": io.BytesIO(image_bytes),
            "scale": scale,
            "face_enhance": False,
        },
    )

    # Handle different return types from Replicate
    if isinstance(output, list):
        output = output[0]

    # If it's a FileOutput object, read it directly
    if hasattr(output, "read"):
        return output.read()

    # Otherwise it's a URL — download it
    response = requests.get(str(output), timeout=120)
    response.raise_for_status()
    return response.content


def convert_to_300dpi(
    image: Image.Image,
    output_format: str,
    target_width_in: float | None = None,
    target_height_in: float | None = None,
    force_exact: bool = False,
):
    """Set DPI metadata to 300 and optionally resize to target dimensions."""
    img = image.copy()

    if target_width_in and target_width_in > 0:
        target_w_px = int(round(target_width_in * TARGET_DPI))

        if force_exact and target_height_in:
            target_h_px = int(round(target_height_in * TARGET_DPI))
        else:
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


# Header with logout button
header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.title("🖼️ KDPEasy AI Upscaler")
with header_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 Logout", width="stretch"):
        st.session_state["password_correct"] = False
        if "ai_cache" in st.session_state:
            del st.session_state["ai_cache"]
        if "converted" in st.session_state:
            del st.session_state["converted"]
        st.rerun()

st.markdown(
    f"<p style='color:#64748b;font-size:1.05rem;'>"
    f"Enhance your images with <b>AI</b> and convert to print-ready <b>300 DPI</b> for KDP.<br>"
    f"<span style='color:#4f46e5;font-weight:600;'>✨ Exclusive tool by {BRAND_NAME}</span>"
    f"</p>",
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
        "2. (Optional) Enhance quality with AI Upscaler<br>"
        "3. Choose a KDP book size preset<br>"
        "4. Download your 300 DPI print-ready file"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    # Read original image
    original_bytes = uploaded_file.getvalue()
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
            help="PNG preserves transparency; JPG has smaller file size.",
        )

        # ─── AI Enhancement Section ─────────────────────────────────
        st.markdown("**🤖 AI Enhancement**")
        use_ai = st.checkbox(
            "✨ Enhance with AI (Real-ESRGAN)",
            value=False,
            help="Use AI to enhance image quality and increase resolution. "
                 "Highly recommended for small or low-quality images.",
        )

        ai_scale = 4
        if use_ai:
            ai_scale = st.radio(
                "AI scale factor",
                options=[2, 4],
                index=1,
                horizontal=True,
                format_func=lambda x: f"{x}x ({'faster' if x == 2 else 'best quality'})",
                help="2x is faster. 4x produces the best quality.",
            )
            est_new_w = orig_w * ai_scale
            est_new_h = orig_h * ai_scale
            st.markdown(
                f"""
                <div class='ai-card'>
                    <b>🎯 After AI Enhancement:</b><br>
                    📐 New dimensions: <b>{est_new_w} × {est_new_h} px</b><br>
                    ⏱️ Processing time: ~10-30 seconds<br>
                    💎 Quality: Significantly improved
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ─── KDP Book Size Section ──────────────────────────────────
        st.markdown("**📚 KDP Book Size**")
        book_size_label = st.selectbox(
            "Select KDP book size",
            options=list(KDP_BOOK_SIZES.keys()),
            index=0,
            help="Pick a preset for popular KDP book sizes, or choose Custom.",
            label_visibility="collapsed",
        )

        target_width_in = None
        target_height_in = None
        force_exact = False

        preset = KDP_BOOK_SIZES[book_size_label]

        if preset is not None:
            target_width_in, target_height_in = preset
            needed_w_px = int(target_width_in * TARGET_DPI)
            needed_h_px = int(target_height_in * TARGET_DPI)

            st.info(
                f"📏 **Target print size:** {target_width_in} × {target_height_in} in  \n"
                f"📐 **Required pixels (300 DPI):** {needed_w_px} × {needed_h_px} px"
            )

            # Estimate post-AI dimensions
            effective_w = orig_w * (ai_scale if use_ai else 1)
            effective_h = orig_h * (ai_scale if use_ai else 1)

            if effective_w >= needed_w_px and effective_h >= needed_h_px:
                if use_ai:
                    st.success("✅ **With AI enhancement, your image will have enough pixels!**")
                else:
                    st.success("✅ **Image has enough pixels** — excellent print quality!")
            elif effective_w >= needed_w_px * 0.7 and effective_h >= needed_h_px * 0.7:
                st.warning(
                    f"⚠️ **Image is slightly small.** "
                    f"{'AI enhancement helps, but ' if not use_ai else ''}"
                    f"recommended source: ≥ {needed_w_px} × {needed_h_px} px."
                )
            else:
                if not use_ai:
                    st.error(
                        f"❌ **Image is TOO SMALL!** Print will be blurry.  \n"
                        f"💡 **Tip:** Enable AI Enhancement above for better quality!"
                    )
                else:
                    st.warning(
                        f"⚠️ Image is small even with AI. "
                        f"Recommended: source ≥ {needed_w_px // ai_scale} × {needed_h_px // ai_scale} px."
                    )

            # Aspect ratio check
            img_ratio = orig_w / orig_h
            target_ratio = target_width_in / target_height_in
            ratio_diff = abs(img_ratio - target_ratio) / target_ratio

            if ratio_diff > 0.02:
                st.markdown(
                    f"<div style='font-size:0.85rem;color:#64748b;'>"
                    f"📊 Original ratio: <b>{img_ratio:.3f}</b> | "
                    f"KDP target: <b>{target_ratio:.3f}</b> "
                    f"(off by {ratio_diff*100:.1f}%)"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                force_exact = st.checkbox(
                    "🔧 Force exact KDP dimensions (may stretch the image)",
                    value=False,
                )
            else:
                st.success("✨ Aspect ratio matches KDP — no distortion!")

        else:
            # Custom mode
            resize_for_print = st.checkbox(
                "Resize for a specific print width",
                value=False,
            )
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

        # ─── Main Convert Button ────────────────────────────────────
        if st.button("✨ Process & Convert to 300 DPI", width="stretch"):
            working_image = image

            # Step 1: AI Upscale (if enabled)
            if use_ai:
                cache_key = get_image_hash(original_bytes, f"_ai_{ai_scale}x")

                if "ai_cache" not in st.session_state:
                    st.session_state["ai_cache"] = {}

                if cache_key in st.session_state["ai_cache"]:
                    working_image = st.session_state["ai_cache"][cache_key]
                    st.info("✨ Using previously enhanced image (cached)")
                else:
                    try:
                        with st.spinner(
                            f"🤖 AI is enhancing your image ({ai_scale}x)... "
                            f"This may take 10-30 seconds. Please wait..."
                        ):
                            upscaled_bytes = ai_upscale(original_bytes, ai_scale)
                            working_image = Image.open(io.BytesIO(upscaled_bytes))
                            st.session_state["ai_cache"][cache_key] = working_image

                        new_w, new_h = working_image.size
                        st.success(
                            f"✨ AI Enhancement complete! "
                            f"New dimensions: **{new_w} × {new_h} px**"
                        )
                    except Exception as e:
                        st.error(
                            f"❌ AI Enhancement failed. Please try again or contact support.  \n"
                            f"Error: {str(e)[:200]}"
                        )
                        st.stop()

            # Step 2: DPI Conversion
            with st.spinner("Converting to 300 DPI..."):
                buf, new_size = convert_to_300dpi(
                    working_image,
                    output_format,
                    target_width_in,
                    target_height_in,
                    force_exact,
                )
                st.session_state["converted"] = {
                    "buf": buf.getvalue(),
                    "format": output_format,
                    "size": new_size,
                    "name": uploaded_file.name.rsplit(".", 1)[0],
                    "used_ai": use_ai,
                    "ai_scale": ai_scale if use_ai else None,
                }
            st.success("✅ Done! Your image is ready for download.")

    # ─── Converted Image Display ──────────────────────────────────
    if "converted" in st.session_state:
        st.markdown("---")
        st.subheader("✅ Converted Image")

        conv = st.session_state["converted"]
        new_w, new_h = conv["size"]
        ext = "png" if conv["format"] == "PNG" else "jpg"
        mime = "image/png" if conv["format"] == "PNG" else "image/jpeg"

        # Add suffix to filename if AI was used
        suffix = f"_ai{conv['ai_scale']}x_300dpi" if conv.get("used_ai") else "_300dpi"
        out_name = f"{conv['name']}{suffix}.{ext}"

        col_a, col_b = st.columns([1, 1], gap="large")
        with col_a:
            st.image(conv["buf"], caption="Preview", width="stretch")
        with col_b:
            ai_badge = (
                f"<span style='background:#fef3c7;color:#92400e;padding:0.2rem 0.5rem;"
                f"border-radius:6px;font-size:0.8rem;font-weight:600;'>"
                f"🤖 AI Enhanced ({conv['ai_scale']}x)</span><br><br>"
                if conv.get("used_ai") else ""
            )
            st.markdown(
                f"""
                <div class='info-card'>
                    {ai_badge}
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
    f"<p style='text-align:center;color:#94a3b8;font-size:0.85rem;'>"
    f"✨ Exclusive tool by <b>{BRAND_NAME}</b> • Powered by Real-ESRGAN AI"
    f"</p>",
    unsafe_allow_html=True,
)
