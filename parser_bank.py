import re
from utils import clean_text, extract_match

def parse_bank_statement(text):
    """
    Parses bank statement text and extracts general information and transactions.
    Returns structured data matching expected schema.
    """
    text = clean_text(text)
    lines = text.split("\n")

    # --- General Info Extraction with Fallbacks ---
    header = {
        "statement_date": extract_match(r"(statement\s*date)\s*[:\-]?\s*(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4})", text, 2),
        "period_covered": extract_match(r"(period\s*covered|date\s*range)\s*[:\-]?\s*(.+?)(?=\n|$)", text, 2),
        "opening_balance": extract_match(r"(opening\s*balance)\s*[:\-]?\s*([0-9.,\-]+)", text, 2),
        "closing_balance": extract_match(r"(closing\s*balance)\s*[:\-]?\s*([0-9.,\-]+)", text, 2),
        "currency": extract_match(r"(currency)\s*[:\-]?\s*([A-Z]{3})", text, 2),
        "account_number": extract_match(r"(account\s*number|iban)\s*[:\-]?\s*([A-Z0-9\- ]{5,})", text, 2),
        "account_holder": extract_match(r"(account\s*holder|client\s*name)\s*[:\-]?\s*(.+)", text, 2)
    }

    # --- Transaction Parsing ---
    transactions = []
    collecting = False
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect start of transaction block
        if re.search(r"date\s+description.*(amount|debit|credit)", line.lower()):
            collecting = True
            continue

        if collecting:
            # Look for typical transaction lines or multi-line entries
            if re.match(r"\d{2}[\/\-\.]\d{2}[\/\-\.]\d{2,4}", line):
                if buffer:
                    transactions.append(parse_transaction_line(buffer))
                    buffer = []
                buffer.append(line)
            else:
                buffer.append(line)

    # Final transaction if buffer isn't empty
    if buffer:
        transactions.append(parse_transaction_line(buffer))

    return {
        "document_type": "bank_statement",
        "header": header,
        "transactions": transactions
    }

def parse_transaction_line(lines):
    """
    Reconstruct and parse a transaction line from buffered lines.
    Returns a dictionary with date, description, amount, and type.
    """
    full_line = " ".join(lines)
    parts = re.split(r'\s{2,}', full_line.strip())

    # Default schema
    transaction = {
        "date": "",
        "description": "",
        "amount": "",
        "type": ""
    }

    # Case: full split line with clear parts
    if len(parts) >= 3:
        transaction["date"] = parts[0]
        transaction["description"] = parts[1]
        amount_str = parts[2]

        transaction["amount"] = amount_str
        transaction["type"] = "credit" if "-" not in amount_str else "debit"

    else:
        # Fallback: attempt to parse from full_line
        match = re.match(r"(?P<date>\d{2}[\/\-\.]\d{2}[\/\-\.]\d{2,4})\s+(?P<desc>.+?)\s+(-?[0-9.,]+)", full_line)
        if match:
            transaction["date"] = match.group("date")
            transaction["description"] = match.group("desc")
            transaction["amount"] = match.group(3)
            transaction["type"] = "credit" if "-" not in match.group(3) else "debit"

    return transaction
