import streamlit as st
import json
import os
import datetime
from ocr_engine import convert_pdf_to_images, perform_ocr_on_images, perform_ocr_on_image
from doc_classifier import identify_document_type
from parser_invoice import parse_invoice, parse_transactions_layout_aware
from parser_receipt import parse_receipt
from parser_bank import parse_bank_statement
from utils import build_output_schema
from logger import log_info, log_error
from error_handler import catch_errors

st.set_page_config(page_title="OCR Extraction Tool", layout="wide")
st.title("📄 Smart OCR Document Parser")

uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

@catch_errors
def process_ocr(file_path, display_name):
    log_info(f"[UI] File received: {display_name}")

    # OCR phase
    if file_path.lower().endswith(".pdf"):
        images = convert_pdf_to_images(file_path)
        text = perform_ocr_on_images(images)
    else:
        text = perform_ocr_on_image(file_path)

    st.subheader("📝 OCR Extracted Text")
    st.text_area("Extracted Text", text, height=300)

    document_type = identify_document_type(text)
    st.success(f"📌 Detected Document Type: {document_type.upper()}")
    log_info(f"[UI] Detected document type: {document_type}")

    extracted_data = {}

    if document_type == "invoice":
        log_info("[UI] Running invoice parser")
        extracted_data = parse_invoice(text)
        transactions = parse_transactions_layout_aware(file_path)
        if transactions:
            extracted_data["transactions"] = transactions

    elif document_type == "receipt":
        log_info("[UI] Running receipt parser")
        extracted_data = parse_receipt(text)

    elif document_type == "bank_statement":
        log_info("[UI] Running bank statement parser")
        extracted_data = parse_bank_statement(text)

    else:
        log_error("[UI] Could not identify document type")
        st.warning("⚠️ Could not determine document type. Only showing OCR text.")
        return

    fields = {k: v for k, v in extracted_data.items() if k != "transactions"}
    transactions = extracted_data.get("transactions", [])
    output = build_output_schema(document_type, file_path, fields, transactions)

    # Show extracted fields
    st.subheader("📋 Extracted Header Fields")
    st.write(fields)

    st.subheader("🧾 Extracted Transactions")
    st.write(transactions)

    st.subheader("📤 Final Output (JSON)")
    st.json(output)

    # Save JSON for download
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"{document_type}_output_{timestamp}.json"
    output_path = os.path.join("output", file_name)
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    with open(output_path, "rb") as f:
        st.download_button("💾 Download JSON", f, file_name=file_name)

if uploaded_file:
    ext = uploaded_file.name.split('.')[-1]
    temp_file_path = f"temp_upload.{ext}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info(f"⏳ Processing file: {uploaded_file.name}")
    process_ocr(temp_file_path, uploaded_file.name)
