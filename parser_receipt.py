import re
from utils import clean_text, extract_match, format_currency

def parse_receipt(text):
    """
    Extract structured fields from a receipt OCR'd text.
    Returns a dictionary with header and items (transactions).
    """
    text = clean_text(text)
    lines = text.split("\n")

    # --- Header Info ---
    header = {
        "document_type": "receipt",
        "receipt_number": extract_match(r"(receipt|ticket|invoice)\s*#?[:\-]?\s*([A-Za-z0-9\-/]+)", text, 2),
        "date": extract_match(r"(date)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2),
        "time": extract_match(r"(time)\s*[:\-]?\s*(\d{1,2}:\d{2}(?:\s*[APMapm]{2})?)", text, 2),
        "shop_name": extract_match(r"^(.*(?:store|mart|shop|restaurant|bakery|pharmacy))", text, 1),
        "address": extract_match(r"(address)\s*[:\-]?\s*(.+?)(?=\s{2,}|date|time|phone|$)", text, 2),
        "total_amount_paid": format_currency(
            extract_match(r"(total\s*(amount)?\s*(paid)?|grand\s*total)\s*[:\-]?\s*([0-9.,]+)", text, 4)
        ),
        "payment_method": extract_match(r"(payment\s*method|paid\s*by)\s*[:\-]?\s*(cash|card|credit|debit)", text, 2),
    }

    # --- Transactions / Items ---
    items = []
    item_section_started = False
    header_keywords = ["item", "description", "qty", "quantity", "unit", "price", "total"]
    ignore_lines = ["subtotal", "vat", "tax", "discount", "total", "thank you"]

    for line in lines:
        line = line.strip()

        # Detect beginning of item table
        if any(h in line.lower() for h in header_keywords):
            item_section_started = True
            continue

        if item_section_started:
            if not line or any(kw in line.lower() for kw in ignore_lines):
                continue

            # Tokenize using multiple spaces or pipe symbol
            parts = [p.strip() for p in re.split(r"\s{2,}|\|", line) if p.strip()]

            if len(parts) >= 3:
                item = {
                    "label": parts[0],
                    "quantity": parts[1],
                    "unit_price": parts[2],
                    "total_ht": parts[3] if len(parts) > 3 else parts[2],
                    "tax_percent": "",  # Receipts often do not show tax %, leave blank
                    "discount": "",     # If not available
                }
                items.append(item)

    return {
        "header": header,
        "transactions": items
    }
