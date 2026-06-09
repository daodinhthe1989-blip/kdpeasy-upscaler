# 🖼️ KDPEasy AI Upscaler

A simple, beginner-friendly desktop app for converting images to **print-ready 300 DPI** — perfect for KDP (Kindle Direct Publishing), book covers, interior pages, and other print projects.

Built with [Streamlit](https://streamlit.io/) and [Pillow](https://python-pillow.org/).

---

## ✨ Features

- 📤 Upload **JPG** and **PNG** images
- 🖨️ Convert to **print-ready 300 DPI**
- 📐 **Keeps original aspect ratio** automatically
- 📏 Optional resize to a specific **print width in inches**
- 💾 Export as **PNG** (with transparency) or **JPG** (smaller files)
- 👀 Live **image preview** before and after conversion
- ⬇️ One-click **download** of the converted image
- 🎨 Modern, clean UI — beginner friendly

---

## 📦 Requirements

- **Python 3.9+**
- pip (comes with Python)

---

## 🚀 How to run locally

### 1. Open a terminal in the project folder

```powershell
cd C:\Users\Admin\Downloads\KDPEasy-Upscaler
```

### 2. (Recommended) Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run app.py
```

Streamlit will open the app automatically in your default browser at:

```
http://localhost:8501
```

If it doesn't open automatically, just copy the URL from the terminal into your browser.

---

## 🧭 How to use the app

1. **Upload** a JPG or PNG image using the upload box.
2. Review the original image info (dimensions, current DPI).
3. Choose your **output format** — PNG or JPG.
4. *(Optional)* Tick **"Resize for a specific print width"** and enter your target width in inches. The height is calculated automatically to keep the aspect ratio.
5. Click **✨ Convert to 300 DPI**.
6. Preview the converted image and click **⬇️ Download** to save it.

The downloaded file will be saved as:

```
<original-name>_300dpi.png   (or .jpg)
```

---

## ❓ FAQ

**What does "300 DPI" actually do?**
DPI (dots per inch) is metadata that tells printers how many pixels to put in each printed inch. Setting it to 300 DPI is the publishing-industry standard for sharp, professional prints. If you also choose a target print width, the app upscales the pixel dimensions so the image fills that physical size cleanly.

**Will my image quality drop?**
The DPI change alone never reduces quality — it's just metadata. If you upscale to a larger print size, the app uses **Lanczos resampling** (high-quality) to enlarge the image.

**JPG or PNG — which should I pick?**
- **PNG** → keeps transparent backgrounds; larger file size. Best for covers with transparency.
- **JPG** → smaller files; no transparency. Best for photos and full-page artwork.

---

## 🛑 Stopping the app

In the terminal where Streamlit is running, press **Ctrl + C**.

---

Made for self-publishers — happy publishing! 📚
