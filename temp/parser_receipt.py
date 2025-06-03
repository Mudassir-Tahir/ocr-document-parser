import re

def extract_field(pattern, text, group=1, fallback="N/A"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else fallback

def parse_receipt(text):
    """
    Extract structured fields from a receipt OCR'd text.
    Returns dictionary with general info and list of items.
    """
    lines = text.split("\n")

    # --- General Info ---
    receipt_number = extract_field(r"(receipt|ticket)\s*#?[:\-]?\s*([A-Za-z0-9\-/]+)", text, 2)
    date = extract_field(r"(date)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)
    time = extract_field(r"(time)\s*[:\-]?\s*(\d{1,2}:\d{2}(\s*[APMapm]{2})?)", text, 2)
    total_amount_paid = extract_field(r"(total\s*(paid)?|amount)\s*[:\-]?\s*([0-9.,]+)", text, 3)
    payment_method = extract_field(r"(payment\s*method|paid\s*by)\s*[:\-]?\s*(cash|card|credit|debit)", text, 2)
    shop_name = extract_field(r"^(.*(?:store|mart|shop|restaurant|bakery|pharmacy))", text, 1)
    address = extract_field(r"(address)\s*[:\-]?\s*(.+?)(?=\s{2,}|date|time|phone)", text, 2)

    # --- Items ---
    items = []
    start_items = False

    for line in lines:
        line = line.strip()

        if "item" in line.lower() and "qty" in line.lower():
            start_items = True
            continue

        if start_items:
            if not line or "total" in line.lower():
                break

            parts = [p.strip() for p in re.split(r'\||\s{2,}', line) if p.strip()]
            if len(parts) >= 3:
                item = {
                    "label": parts[0],
                    "quantity": parts[1],
                    "price": parts[2],
                    "total": parts[3] if len(parts) > 3 else "N/A"
                }
                items.append(item)

    return {
        "document_type": "receipt",
        "receipt_number": receipt_number,
        "date": date,
        "time": time,
        "shop_name": shop_name,
        "address": address,
        "total_amount_paid": total_amount_paid,
        "payment_method": payment_method,
        "items": items
    }
