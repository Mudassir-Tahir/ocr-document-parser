import re
from utils import clean_text, extract_match

def parse_transactions(text):
    lines = text.split("\n")
    transactions = []
    start_extracting = False
    header_index = {}

    for i, line in enumerate(lines):
        clean_line = line.strip()

        if re.search(r"(désignation|designation)", clean_line.lower()) and re.search(r"(qté|quantité)", clean_line.lower()):
            header_line = re.split(r'\s{2,}|\t|\|', clean_line)
            for idx, word in enumerate(header_line):
                label = word.strip().lower()
                if "désignation" in label:
                    header_index["label"] = idx
                elif "qté" in label or "quantité" in label:
                    header_index["quantity"] = idx
                elif "pu" in label:
                    header_index["unit_price"] = idx
                elif "remise" in label:
                    header_index["item_discount"] = idx
                elif "montant" in label or "ht" in label:
                    header_index["item_total_ht"] = idx
                elif "tva" in label or "%" in label:
                    header_index["tax_percentage"] = idx
            start_extracting = True
            continue

        if start_extracting:
            if not clean_line or len(clean_line) < 5 or "total" in clean_line.lower():
                break

            values = re.split(r'\s{2,}|\t|\|', clean_line)
            values = [v.strip() for v in values if v.strip()]
            if len(values) < 2:
                continue

            transaction = {
                "label": values[header_index["label"]] if "label" in header_index and header_index["label"] < len(values) else "N/A",
                "quantity": values[header_index["quantity"]] if "quantity" in header_index and header_index["quantity"] < len(values) else "N/A",
                "unit_price": values[header_index["unit_price"]] if "unit_price" in header_index and header_index["unit_price"] < len(values) else "N/A",
                "item_discount": values[header_index["item_discount"]] if "item_discount" in header_index and header_index["item_discount"] < len(values) else "N/A",
                "item_total_ht": values[header_index["item_total_ht"]] if "item_total_ht" in header_index and header_index["item_total_ht"] < len(values) else "N/A",
                "tax_percentage": values[header_index["tax_percentage"]] if "tax_percentage" in header_index and header_index["tax_percentage"] < len(values) else "N/A",
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
