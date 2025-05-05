# Sortify

**Sortify** is a lightweight web application and CLI tool that sorts PDF pages based on page numbers found anywhere at the bottom of each page. Built with Python and a minimal front end, Sortify uses OCR to detect page numbers, automatically reorders the pages, and outputs a new sorted PDF.

---

## 🚀 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Installation](#installation)
5. [Usage](#usage)

   * [Command-Line Interface](#command-line-interface)
   * [Web UI](#web-ui)
6. [Configuration](#configuration)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

---

## 📝 Overview

When you scan or compile multi-page documents, the original pagination can be lost or scrambled. **Sortify** solves this by:

1. Converting each PDF page to an image.
2. Cropping the bottom region where page numbers typically reside.
3. Running OCR (via Tesseract) to extract page numbers.
4. Reordering pages according to the detected numbers.
5. Saving a new, sorted PDF.

All of this happens automatically, whether you call Sortify from the command line or upload a file via the Web UI.

---

## ✨ Features

* **OCR-based detection** of page numbers (works on scanned and digital PDFs)
* **Automatic sorting** with warnings for missing or duplicate numbers
* **Manual correction** support for edge cases
* **Dual interface**: CLI script and responsive web UI
* **Drag-and-drop** file upload
* **Progress indicator** (loading spinner)
* **One-click download** of the sorted PDF

---

## 🛠️ Tech Stack

* **Python 3.8+**
* **Flask** – lightweight web server
* **pdf2image** & **Pillow** – convert PDF pages to images
* **pytesseract** – OCR engine for digit recognition
* **JavaScript** (vanilla) – frontend logic for upload/download and drag-and-drop
* **HTML5 & CSS3** – modern, responsive UI following Apple HIG principles

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<YOUR-USERNAME>/Sortify.git
   cd Sortify
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**

   * **macOS**: `brew install tesseract`
   * **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   * **Windows**: Download and install from [UB Mannheim](https://github.com/tesseract-ocr/tesseract)

---

## 🚩 Usage

### Command-Line Interface

Run the sorting script directly:

```bash
python pdf_sorter.py
```

1. Enter the path to your input PDF.
2. Enter the desired output path for the sorted PDF.
3. (Optional) Add manual corrections in the `corrections` dictionary if OCR fails on specific pages.

### Web UI

1. **Start the Flask server**

   ```bash
   export FLASK_APP=app.py      # macOS/Linux
   set FLASK_APP=app.py         # Windows
   flask run
   ```
2. Navigate to `http://localhost:5000` in your browser.
3. Drag & drop or click to select a PDF.
4. Click **Upload & Sort**.
5. Download your sorted PDF when it’s ready.

---

## 🔧 Configuration

* **OCR Region**: Adjust the crop percentage in `pdf_sorter.py` if your page numbers appear outside the default bottom area.
* **Manual Corrections**: Inside `pdf_sorter.py`, you can override detected numbers:

  ```python
  corrections = {
      0: 1,  # Page image index 0 is actually page number 1
      5: 6   # etc.
  }
  ```

---

## 📂 Project Structure

```
Sortify/
├─ app.py               # Flask backend routes
├─ pdf_sorter.py        # Core sorting logic (OCR + PDF reorder)
├─ static/
│  ├─ styles.css        # Custom CSS (Apple HIG inspired)
│  └─ script.js         # Frontend logic
├─ templates/
│  └─ index.html        # Main UI template
├─ requirements.txt     # Python dependencies
├─ README.md            # This file
└─ .gitignore
```

---

## ❓ Troubleshooting

* **OCR misses page numbers**: Increase `dpi` in `convert_from_path`, expand the crop region, or add manual corrections.
* **Tesseract not found**: Ensure `pytesseract.pytesseract.tesseract_cmd` points to your Tesseract binary.
* **Slow performance on large PDFs**: Reduce `dpi` or batch-process smaller documents.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add YourFeature"`
4. Push to branch: `git push origin feature/YourFeature`
5. Open a Pull Request

Please follow the existing code style and include tests for any new functionality.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
