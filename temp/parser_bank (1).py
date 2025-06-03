import re

def extract_field(pattern, text, group=1, fallback="N/A"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else fallback

def parse_bank_statement(text):
    """
    Parse a bank statement using English headers and robust table detection.
    Returns structured fields and transactions.
    """
    lines = text.split("\n")

    # --- General Info ---
    opening_balance = extract_field(r"(opening balance)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    closing_balance = extract_field(r"(closing balance)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    statement_date = extract_field(r"(statement date)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})", text, 2)
    period_covered = extract_field(r"(period covered|date range)\s*[:\-]?\s*(.+?)(?=\n|$)", text, 2)
    currency = extract_field(r"(currency)\s*[:\-]?\s*([A-Z]{3})", text, 2)

    # --- Transactions ---
    transactions = []
    start_extracting = False

    for line in lines:
        line = line.strip()

        # Start when table header appears
        if re.search(r"date\s+description\s+(debit|credit).*", line.lower()):
            start_extracting = True
            continue

        if start_extracting:
            if not line:
                continue

            # Try splitting a typical transaction line
            parts = [p.strip() for p in re.split(r'\s{2,}', line) if p.strip()]

            if len(parts) >= 4:
                transaction = {
                    "date": parts[0],
                    "description": parts[1],
                    "debit": parts[2] if "debit" in line.lower() else "N/A",
                    "credit": parts[3] if "credit" in line.lower() else "N/A"
                }
                transactions.append(transaction)
            elif len(parts) >= 3:
                transaction = {
                    "date": parts[0],
                    "description": parts[1],
                    "amount": parts[2],
                    "type": "credit" if "-" not in parts[2] else "debit"
                }
                transactions.append(transaction)

    return {
        "document_type": "bank_statement",
        "statement_date": statement_date,
        "period_covered": period_covered,
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "currency": currency,
        "transactions": transactions
    }
