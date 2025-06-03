from ocr_engine import convert_pdf_to_images, perform_ocr_on_images, perform_ocr_on_image
from doc_classifier import identify_document_type
from parser_invoice import parse_invoice
from parser_receipt import parse_receipt
from parser_bank import parse_bank_statement
import sys
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

    print(f"\n✅ {document_type.capitalize()} data saved to: {output_path}")


def main():
    file_path = input("Enter the path to the PDF or image file: ").strip()

    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        return

    try:
        # OCR
        if file_path.lower().endswith(".pdf"):
            print("Processing PDF...")
            images = convert_pdf_to_images(file_path)
            text = perform_ocr_on_images(images)
        else:
            print("Processing Image...")
            text = perform_ocr_on_image(file_path)

        # Classify
        document_type = identify_document_type(text)
        print("\n=== Document Type: {} ===".format(document_type.upper()))

        # Invoice
        if document_type == "invoice":
            extracted_data = parse_invoice(text)
            print("\n--- Parsed Invoice Fields ---")
            for k, v in extracted_data.items():
                if k != "transactions":
                    print(f"{k}: {v}")
                else:
                    print("\nTransactions:")
                    for idx, tx in enumerate(v, 1):
                        print(f"  Item {idx}:")
                        for field, value in tx.items():
                            print(f"    {field}: {value}")
            save_json(extracted_data, "invoice")

        # Receipt
        elif document_type == "receipt":
            extracted_data = parse_receipt(text)
            print("\n--- Parsed Receipt Fields ---")
            for k, v in extracted_data.items():
                if k != "items":
                    print(f"{k}: {v}")
                else:
                    print("\nItems:")
                    for idx, item in enumerate(v, 1):
                        print(f"  Item {idx}:")
                        for field, value in item.items():
                            print(f"    {field}: {value}")
            save_json(extracted_data, "receipt")

        # Bank Statement
        elif document_type == "bank_statement":
            extracted_data = parse_bank_statement(text)
            print("\n--- Parsed Bank Statement Fields ---")
            for k, v in extracted_data.items():
                if k != "transactions":
                    print(f"{k}: {v}")
                else:
                    print("\nTransactions:")
                    for idx, tx in enumerate(v, 1):
                        print(f"  Transaction {idx}:")
                        for field, value in tx.items():
                            print(f"    {field}: {value}")
            save_json(extracted_data, "bank_statement")

        else:
            print("Document type is UNKNOWN. No parser applied.")

    except Exception as e:
        print("An error occurred during OCR processing:", str(e))


if __name__ == "__main__":
    main()
