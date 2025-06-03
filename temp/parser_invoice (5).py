
import re
from pdf2image import convert_from_path
from pytesseract import image_to_data, pytesseract
from collections import defaultdict

DEBUG = False

def extract_lines_with_boxes_from_image(image):
    df = image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip() != ""]
    lines = defaultdict(list)

    for _, row in df.iterrows():
        y = row["top"]
        text = row["text"]
        line_id = y
        for key in lines:
            if abs(key - y) < 8:
                line_id = key
                break
        lines[line_id].append((row["left"], text))

    return ["  ".join(word for _, word in sorted(words, key=lambda x: x[0])) for _, words in sorted(lines.items())]

def extract_field(pattern, text, group=1, fallback="N/A"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else fallback

def parse_invoice(text):
    text = text.replace("\n", " ").replace("  ", " ")

    return {
        "document_type": "invoice",
        "header": {
            "invoice_number": extract_field(r"(facture|invoice)\s*(n°|no|numéro)?\s*[:\-]?[\s]*([A-Za-z0-9\/\-]+)", text, 3),
            "invoice_date": extract_field(r"(date\s*facture|casablanca le|date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
            "delivery_date": extract_field(r"(livraison\s*le|delivery\s*date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
            "due_date": extract_field(r"(echeance|due date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
            "client_name": extract_field(r"client(?:\s*[:\-])?\s*(\S+@\S+|[A-Za-z0-9 \-]+)", text, 1),
            "client_ice_or_if": extract_field(r"(ice|if)\s*(client)?\s*[:\-]?\s*(\d+)", text, 3),
            "provider_name": extract_field(r"(fourni\w*|issuer|from)\s*[:\-]?\s*([A-Z][a-zA-Z\s&]+)", text, 2),
            "provider_ice_or_if": extract_field(r"(ice|if)\s*(fournisseur|provider)?\s*[:\-]?\s*(\d+)", text, 3),
            "sub_total_ht": extract_field(r"(sous\s*total\s*ht|sub\s*total)\s*[:\-]?\s*([\d\., ]+)", text, 2),
            "vat_amount": extract_field(r"(montant\s*tva|vat\s*amount)\s*[:\-]?\s*([\d\., ]+)", text, 2),
            "vat_percent": extract_field(r"tva\s*[:\-]?\s*(\d{1,2})\s*%", text, 1),
            "total_ttc": extract_field(r"(total\s*ttc|total\s*amount)\s*[:\-]?\s*([\d\., ]+)", text, 2),
            "discount": extract_field(r"(remise|discount)\s*[:\-]?\s*([\d\.,]+)", text, 2),
            "delivery_fee": extract_field(r"(livraison|delivery\s*fee)\s*[:\-]?\s*([\d\.,]+)", text, 2),
            "other_charges": extract_field(r"(frais divers|other charges)\s*[:\-]?\s*([\d\.,]+)", text, 2)
        },
        "transactions": []
    }

def parse_transactions_layout_aware(pdf_path, poppler_path=None):
    images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
    if not images:
        return []

    lines = extract_lines_with_boxes_from_image(images[0])
    if DEBUG:
        print("\n--- OCR LINES ---")
        for i, l in enumerate(lines): print(f"{i+1:02d}: {l}")

    header_keywords = ["désignation", "designation", "qté", "quantité", "pu", "prix", "montant", "total"]
    transactions = []
    header_line_idx = -1

    for i in range(len(lines) - 2):
        combined = " ".join([lines[i], lines[i+1], lines[i+2]]).lower()
        match_count = sum(1 for k in header_keywords if k in combined)
        if match_count >= 3:
            header_line_idx = i + 3
            break
    if header_line_idx == -1:
        for i, line in enumerate(lines):
            if any(k in line.lower() for k in header_keywords):
                header_line_idx = i + 1
                break
    if header_line_idx == -1:
        return []

    buffer = []
    current_tx = []
    for line in lines[header_line_idx:]:
        clean = line.strip().lower()
        if not clean or any(x in clean for x in ["total", "arrêtée", "signature", "merci"]):
            if current_tx:
                buffer.append(" ".join(current_tx))
            break

        if re.search(r"\b\d+\s+[\d\.,]+\b", line):
            if current_tx:
                buffer.append(" ".join(current_tx))
            current_tx = [line]
        else:
            current_tx.append(line)

    if current_tx:
        buffer.append(" ".join(current_tx))

    for line in buffer:
        parts = [p.strip() for p in line.split("  ") if p.strip()]
        if len(parts) >= 3:
            tx = {
                "label": parts[0],
                "quantity": parts[1] if len(parts) > 1 else "N/A",
                "unit_price": parts[2] if len(parts) > 2 else "N/A",
                "item_total_ht": parts[3] if len(parts) > 3 else "N/A",
                "item_discount": parts[4] if len(parts) > 4 else "N/A",
                "tax_percentage": parts[5] if len(parts) > 5 else "N/A"
            }
            transactions.append(tx)

    return transactions
