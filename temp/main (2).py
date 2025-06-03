from ocr_engine import convert_pdf_to_images, perform_ocr_on_images, perform_ocr_on_image
from doc_classifier import identify_document_type
from parser_invoice import parse_invoice
from parser_receipt import parse_receipt
from parser_bank import parse_bank_statement
from logger import log_info, log_error
from error_handler import catch_errors
from utils import build_output_schema
import json
import datetime
import os

def save_json(data, document_type):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"{document_type}_output_{timestamp}.json"
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    log_info(f"✅ {document_type.capitalize()} data saved to: {output_path}")

@catch_errors
def main():
    file_path = input("Enter the path to the PDF or image file: ").strip()
    log_info(f"Received input file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    # OCR
    if file_path.lower().endswith(".pdf"):
        log_info(f"Processing PDF: {file_path}")
        images = convert_pdf_to_images(file_path)
        text = perform_ocr_on_images(images)
    else:
        log_info(f"Processing Image: {file_path}")
        text = perform_ocr_on_image(file_path)

    # Classification
    document_type = identify_document_type(text)
    log_info(f"Identified document type: {document_type} for file: {file_path}")

    if document_type == "invoice":
        log_info(f"Starting invoice parsing for: {file_path}")
        extracted_data = parse_invoice(text)

    elif document_type == "receipt":
        log_info(f"Starting receipt parsing for: {file_path}")
        extracted_data = parse_receipt(text)

    elif document_type == "bank_statement":
        log_info(f"Starting bank statement parsing for: {file_path}")
        extracted_data = parse_bank_statement(text)

    else:
        log_error(f"[FR06] Failed to identify document type for: {file_path}")
        raise ValueError("Unknown document type")

    fields = {k: v for k, v in extracted_data.items() if k != "transactions"}
    transactions = extracted_data.get("transactions", [])
    output_data = build_output_schema(document_type, file_path, fields, transactions)

    save_json(output_data, document_type)

if __name__ == "__main__":
    main()
