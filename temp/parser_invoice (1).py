import re
from utils import clean_text, extract_match, format_currency

def parse_transactions(text):
    """
    Extract individual transaction items from the invoice OCR text.
    Returns a list of dictionaries, one per line item.
    """
    lines = text.split("\n")
    transactions = []
    start_extracting = False

    for line in lines:
        line = line.strip()

        if "designation" in line.lower() and ("qté" in line.lower() or "quantité" in line.lower()):
            start_extracting = True
            continue

        if start_extracting:
            if not line or "thank you" in line.lower():
                break

            parts = [p.strip() for p in re.split(r'\||\s{2,}', line) if p.strip()]
            if len(parts) >= 6:
                transaction = {
                    "label": parts[0],
                    "quantity": parts[1],
                    "unit_price": parts[2],
                    "item_discount": parts[3],
                    "item_total_ht": parts[4],
                    "tax_percentage": parts[5],
                    "tax": parts[6] if len(parts) > 6 else "N/A"
                }
                transactions.append(transaction)

    return transactions

def parse_invoice(text):
    """
    Extract structured fields from OCR text of an invoice.
    Missing fields return 'N/A'.
    """
    text = clean_text(text)

    invoice_number = extract_match(r"(invoice|facture)\s*(no\.?|numéro)?\s*[:\-]?\s*([A-Za-z0-9\-\/]+)", text, 3)
    invoice_date = extract_match(r"(invoice\s*date|date\s*facture)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)
    delivery_date = extract_match(r"(delivery\s*date|date\s*livraison)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)
    due_date = extract_match(r"(due\s*date|date\s*echeance)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)

    client_name = extract_match(r"(billed\s*to|client)\s*[:\-]?\s*([A-Z][a-zA-Z\s&]+)", text, 2)
    client_address = extract_match(r"client\s*address\s*[:\-]?\s*(.+?)(?=\s{2,}|provider|invoice|facture)", text, 1)

    provider_name = extract_match(r"(provider|from|issuer)\s*[:\-]?\s*([A-Z][a-zA-Z\s&]+)", text, 2)
    provider_address = extract_match(r"provider\s*address\s*[:\-]?\s*(.+?)(?=\s{2,}|client|invoice)", text, 1)

    client_ice_or_if = extract_match(r"(client\s*)?(ice|if)\s*[:\-]?\s*([A-Za-z0-9]+)", text, 3)
    provider_ice_or_if = extract_match(r"(provider\s*)?(ice|if)\s*[:\-]?\s*([A-Za-z0-9]+)", text, 3)

    sub_total_ht = extract_match(r"(sub\s*total|sous\s*total\s*ht)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    vat_amount = extract_match(r"(montant\s*tva|vat\s*amount)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    vat_percent = extract_match(r"tva\s*[:\-]?\s*(\d{1,2})\s*%", text, 1)

    total_ttc = extract_match(r"(total\s*ttc|total\s*amount\s*incl\.?\s*tax)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    discount = extract_match(r"(remise|discount)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    delivery_fee = extract_match(r"(livraison|delivery\s*fee)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    other_charges = extract_match(r"(other\s*charges|frais\s*divers)\s*[:\-]?\s*([0-9.,]+)", text, 2)

    transactions = parse_transactions(text)

    return {
        "document_type": "invoice",
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "delivery_date": delivery_date,
        "due_date": due_date,
        "client_name": client_name,
        "client_address": client_address,
        "provider_name": provider_name,
        "provider_address": provider_address,
        "client_ice_or_if": client_ice_or_if,
        "provider_ice_or_if": provider_ice_or_if,
        "sub_total_ht": sub_total_ht,
        "vat_amount": vat_amount,
        "vat_percent": vat_percent,
        "total_ttc": total_ttc,
        "discount": discount,
        "delivery_fee": delivery_fee,
        "other_charges": other_charges,
        "transactions": transactions
    }
