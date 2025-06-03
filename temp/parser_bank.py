import re

def extract_field(pattern, text, group=1, fallback="N/A"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else fallback

def parse_bank_statement(text):
    """
    Extract structured fields from OCR text of a bank statement.
    Missing fields return 'N/A'.
    """
    lines = text.split("\n")

    # --- General Info ---
    rib = extract_field(r"(rib|iban)\s*[:\-]?\s*([A-Z0-9]+)", text, 2)
    solde_initial = extract_field(r"(solde\s*initial|starting\s*balance)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    solde_final = extract_field(r"(solde\s*final|ending\s*balance)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    currency = extract_field(r"(devise|currency)\s*[:\-]?\s*([A-Z]{3})", text, 2)
    period = extract_field(r"(période|statement\s*period)\s*[:\-]?\s*([\d/\-.\s]+)", text, 2)

    # --- Transactions ---
    transactions = []
    start_extracting = False

    for line in lines:
        line = line.strip()

        if "date" in line.lower() and "description" in line.lower() and ("debit" in line.lower() or "credit" in line.lower()):
            start_extracting = True
            continue

        if start_extracting:
            if not line or "solde" in line.lower():
                continue

            parts = [p.strip() for p in re.split(r'\||\s{2,}', line) if p.strip()]
            if len(parts) >= 4:
                transaction = {
                    "date": parts[0],
                    "description": parts[1],
                    "amount": parts[2],
                    "type": parts[3]  # e.g., "Credit" or "Debit"
                }
                transactions.append(transaction)

    return {
        "document_type": "bank_statement",
        "rib": rib,
        "solde_initial": solde_initial,
        "solde_final": solde_final,
        "currency": currency,
        "period": period,
        "transactions": transactions
    }
