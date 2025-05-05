import os
import re
import pytesseract
from typing import Optional, Dict, List
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
from tqdm import tqdm

# Add these imports for the file dialogs
import tkinter as tk
from tkinter import filedialog

# Optional: configure if Tesseract isn’t on your PATH
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

def threshold(px: int) -> int:
    return 0 if px < 150 else 255

def detect_page_number_dynamic(
    image: Image.Image,
    page_index: int,
    manual_corrections: Optional[Dict[int, int]] = None
) -> Optional[int]:
    trials = [
        {'w_ratio': 0.35, 'h_ratio': 0.06, 'max_chunks': 12},
        {'w_ratio': 0.50, 'h_ratio': 0.10, 'max_chunks': 6},
        {'w_ratio': 1.00, 'h_ratio': 0.20, 'max_chunks': 3},
        {'w_ratio': 1.00, 'h_ratio': 0.50, 'max_chunks': 1},
    ]
    ocr_configs = [
        "--psm 6 -c tessedit_char_whitelist=0123456789",
        "--psm 3 -c tessedit_char_whitelist=0123456789"
    ]
    width, height = image.size

    for trial in trials:
        w, h, mc = trial['w_ratio'], trial['h_ratio'], trial['max_chunks']
        for i in range(mc):
            y1 = int(height * (1 - (i + 1) * h))
            y2 = int(height * (1 - i * h))
            x1 = int(width * (1 - w))
            x2 = width

            chunk = image.crop((x1, y1, x2, y2))
            chunk = chunk.resize((chunk.width * 2, chunk.height * 2),
                                 resample=Image.Resampling.LANCZOS)
            chunk = chunk.convert("L")
            chunk = ImageEnhance.Contrast(chunk).enhance(2.0)
            chunk = chunk.filter(ImageFilter.MedianFilter())
            chunk = chunk.point(threshold, '1')

            for cfg in ocr_configs:
                text = pytesseract.image_to_string(chunk, config=cfg)
                matches = re.findall(r'\b(\d{3})\b', text.strip())
                if matches:
                    nums = [int(m) for m in matches]
                    plausible = [n for n in nums if 100 <= n <= 999]
                    if plausible:
                        return max(plausible)

    if manual_corrections and page_index in manual_corrections:
        return manual_corrections[page_index]
    return None

def sort_pdf_by_ocr(
    input_pdf: str,
    output_pdf: str,
    manual_corrections: Optional[Dict[int, int]] = None
) -> None:
    if not os.path.isfile(input_pdf):
        raise FileNotFoundError(f"Input not found: {input_pdf}")

    images = convert_from_path(input_pdf, dpi=200)
    page_map: Dict[int, List[int]] = {}
    failed_pages: List[int] = []
    manual_corrections = manual_corrections or {}

    print("\n🔍 Scanning pages for three-digit numbers…\n")
    for idx, img in tqdm(enumerate(images), total=len(images), desc="OCR"):
        num = detect_page_number_dynamic(img, idx, manual_corrections)
        if num is None:
            print(f"❌ Page {idx+1}: no three-digit number found.")
            failed_pages.append(idx)
        else:
            page_map.setdefault(num, []).append(idx)
            print(f"✅ Page {idx+1}: detected #{num}")

    if not page_map:
        raise RuntimeError("No three-digit page numbers detected on any page.")

    # Retry undetected pages up to 3 times
    undetected = failed_pages.copy()
    retries = 0
    max_retries = 3
    while undetected and retries < max_retries:
        retries += 1
        print(f"\n🔄 Retry pass #{retries} on undetected pages…")
        newly = []
        for idx in undetected:
            num = detect_page_number_dynamic(images[idx], idx, manual_corrections)
            if num is not None:
                page_map.setdefault(num, []).append(idx)
                newly.append(idx)
                print(f"🔖 Page {idx+1}: finally detected #{num}")
        undetected = [i for i in undetected if i not in newly]
    failed_pages = undetected

    # Flatten sorted and then append unsorted
    sorted_idxs: List[int] = []
    for pg in sorted(page_map):
        sorted_idxs.extend(page_map[pg])

    sorted_imgs = [images[i] for i in sorted_idxs]
    unsorted_imgs = [images[i] for i in failed_pages]
    final_imgs = sorted_imgs + unsorted_imgs

    if not output_pdf.lower().endswith(".pdf"):
        output_pdf += ".pdf"
    final_imgs[0].save(output_pdf, save_all=True, append_images=final_imgs[1:])

    print(f"\n📄 Saved sorted PDF to: {output_pdf}")
    print("\n--- Summary ---")
    print(f"Total pages:             {len(images)}")
    print(f"Pages sorted by number:  {len(sorted_imgs)}")
    print(f"Pages unsorted (appended): {len(unsorted_imgs)}")
    if any(len(v) > 1 for v in page_map.values()):
        print("ℹ️  Duplicate numbers were grouped together.")

if __name__ == "__main__":
    # hide the root Tk window
    root = tk.Tk()
    root.withdraw()

    # open file dialog to pick the PDF
    input_pdf = filedialog.askopenfilename(
        title="Select PDF to sort",
        filetypes=[("PDF files","*.pdf")])
    if not input_pdf:
        print("No file selected, exiting.")
        exit()

    # save dialog for output
    output_pdf = filedialog.asksaveasfilename(
        title="Save sorted PDF as",
        defaultextension=".pdf",
        filetypes=[("PDF files","*.pdf")])
    if not output_pdf:
        print("No output path selected, exiting.")
        exit()

    corrections: Dict[int, int] = {
        # e.g. 0: 100
    }
    try:
        sort_pdf_by_ocr(input_pdf, output_pdf, manual_corrections=corrections)
    except Exception as e:
        print(f"\n⚠️  ERROR: {e}")
