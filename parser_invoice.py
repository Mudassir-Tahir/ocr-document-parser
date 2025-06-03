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
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace

    header = {
        "invoice_number": extract_field(r"(facture|invoice)\s*(n°|no|numéro)?\s*[:\-]?\s*([A-Za-z0-9\/\-]+)", text, 3),
        "invoice_date": extract_field(r"(date\s*facture|casablanca le|date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
        "delivery_date": extract_field(r"(livraison\s*le|delivery\s*date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
        "due_date": extract_field(r"(echeance|due\s*date)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 2),
        "client_name": extract_field(r"client\s*[:\-]?\s*([A-Z0-9\s\-]+)", text, 1),
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
    }

    # Fallback for invoice_date if not found
    if header["invoice_date"] == "N/A":
        header["invoice_date"] = extract_field(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, 1)

    return {
        "document_type": "invoice",
        "header": header,
        "transactions": []  # Populated separately
    }

def parse_transactions_layout_aware(pdf_path, poppler_path=None):
    images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
    if not images:
        return []

    lines = extract_lines_with_boxes_from_image(images[0])
    if DEBUG:
        print("\n--- OCR LINES ---")
        for i, l in enumerate(lines): print(f"{i+1:02d}: {l}")

    # Locate transactions block by detecting headers
    header_keywords = ["désignation", "designation", "qté", "quantité", "pu", "prix", "montant", "total"]
    header_line_idx = -1

    for i in range(len(lines)):
        line = lines[i].lower()
        if sum(1 for k in header_keywords if k in line) >= 3:
            header_line_idx = i + 1
            break

    if header_line_idx == -1:
        return []

    # Gather transaction lines
    buffer = []
    current_line = []
    for line in lines[header_line_idx:]:
        l_clean = line.strip().lower()
        if not l_clean or re.search(r"(total|signature|merci|arrêtée)", l_clean):
            if current_line:
                buffer.append(" ".join(current_line))
            break

        if re.search(r"\d{1,3}(?:[.,]\d{1,2})?\s+[\d.,]+\s+[\d.,]+", line):
            if current_line:
                buffer.append(" ".join(current_line))
            current_line = [line]
        else:
            current_line.append(line)

    if current_line:
        buffer.append(" ".join(current_line))

    # Reconstruct structured fields
    transactions = []
    for line in buffer:
        parts = [p.strip() for p in re.split(r"\s{2,}", line) if p.strip()]
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
