# ocr_engine.py

import pytesseract
from pdf2image import convert_from_path
from pytesseract import image_to_string, image_to_data
from PIL import Image
import os

# Set Tesseract and Poppler paths (edit as needed)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def convert_pdf_to_images(pdf_path):
    """Convert each page of PDF into an image."""
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    return images

def perform_ocr_on_images(images):
    """Run OCR on list of images and return full text."""
    full_text = ""
    for img in images:
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"
    return full_text

def perform_ocr_on_image(image_path):
    """Run OCR on a single image file (e.g., PNG, JPG)."""
    image = Image.open(image_path)
    return image_to_string(image)

def get_ocr_dataframe(image):
    return image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
