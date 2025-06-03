import re
from utils import clean_text, extract_match

def parse_transactions(text):
    lines = text.split("\n")
    transactions = []
    start_extracting = False

    for line in lines:
        line = line.strip()

        if re.search(r"(désignation|designation)", line.lower()) and re.search(r"(qté|quantité)", line.lower()):
            start_extracting = True
            continue

        if start_extracting:
            if not line or "merci" in line.lower() or "total" in line.lower():
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
                }
                transactions.append(transaction)

    return transactions

def parse_invoice(text):
    text = clean_text(text)

    invoice_number = extract_match(r"(facture\s*(numéro)?|invoice\s*(number)?)\s*[:\-]?\s*([A-Za-z0-9\-/]+)", text, 4)
    invoice_date = extract_match(r"(date\s*(facture|invoice))\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 3)
    delivery_date = extract_match(r"(date\s*livraison|delivery\s*date)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)
    due_date = extract_match(r"(date\s*échéance|due\s*date)\s*[:\-]?\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})", text, 2)

    client_name = extract_match(r"(client|nom\s*client)\s*[:\-]?\s*([A-Z][a-zA-Z\s&]+)", text, 2)
    client_address = extract_match(r"(adresse\s*client|client\s*address)\s*[:\-]?\s*(.+?)(?=\s{2,}|provider|facture|invoice)", text, 2)

    provider_name = extract_match(r"(fournisseur|issuer|provider|nom\s*fournisseur)\s*[:\-]?\s*([A-Z][a-zA-Z\s&]+)", text, 2)
    provider_address = extract_match(r"(adresse\s*fournisseur|provider\s*address)\s*[:\-]?\s*(.+?)(?=\s{2,}|client|invoice)", text, 2)

    client_ice_or_if = extract_match(r"(ice|if)\s*client\s*[:\-]?\s*([A-Za-z0-9]+)", text, 2)
    provider_ice_or_if = extract_match(r"(ice|if)\s*(fournisseur|provider)\s*[:\-]?\s*([A-Za-z0-9]+)", text, 3)

    sub_total_ht = extract_match(r"(sous\s*total\s*ht|sub\s*total)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    vat_amount = extract_match(r"(montant\s*tva|vat\s*amount)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    vat_percent = extract_match(r"(tva\s*[:\-]?)\s*(\d{1,2})\s*%", text, 2)

    total_ttc = extract_match(r"(total\s*ttc|total\s*amount\s*incl\.?\s*tax)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    discount = extract_match(r"(remise|discount)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    delivery_fee = extract_match(r"(livraison|delivery\s*fee)\s*[:\-]?\s*([0-9.,]+)", text, 2)
    other_charges = extract_match(r"(frais\s*divers|other\s*charges)\s*[:\-]?\s*([0-9.,]+)", text, 2)

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
