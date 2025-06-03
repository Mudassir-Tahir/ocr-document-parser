# doc_classifier.py

def identify_document_type(text):
    """
    Identify document type: invoice, receipt, or bank_statement.
    Uses strong keyword logic and debugging tips.
    """
    text_lower = text.lower()

    # --- Strong Indicators ---
    if "receipt" in text_lower and ("payment method" in text_lower or "transaction id" in text_lower or "provider info" in text_lower or "date of receipt" in text_lower):
        print("[Debug] Detected keywords: 'receipt' + 'payment method' or 'transaction id' → Classified as RECEIPT")
        return "receipt"

    if "invoice" in text_lower and ("invoice no" in text_lower or "facture" in text_lower or "client info" in text_lower or "date of invoice" in text_lower):
        print("[Debug] Detected keywords: 'invoice', 'invoice no', or 'facture' → Classified as INVOICE")
        return "invoice"

    if "bank statement" in text_lower and ("rib" in text_lower or "solde" in text_lower or "bank name" in text_lower or "account number" in text_lower or "statement of account" in text_lower or "releve bancaire" in text_lower):
        print("[Debug] Detected keywords: 'releve bancaire', 'rib', or 'solde' → Classified as BANK STATEMENT")
        return "bank_statement"

    # --- Secondary Keyword Groups ---
    invoice_keywords = [
        "invoice", "facture", "invoice no", "vat", "tva",
        "total ttc", "pro forma invoice", "subtotal", "freight", "tax rate"
    ]
    receipt_keywords = ["cash", "amount paid", "till", "credit card", "customer copy"]
    bank_keywords = ["date valeur", "date operation", "credit", "debit"]

    # --- Keyword Scoring ---
    score = {
        "invoice": sum(k in text_lower for k in invoice_keywords),
        "receipt": sum(k in text_lower for k in receipt_keywords),
        "bank_statement": sum(k in text_lower for k in bank_keywords),
    }

    # Get highest scoring type
    best_match = max(score, key=score.get)

    if score[best_match] > 0:
        print(f"[Debug] Keyword score → Invoice: {score['invoice']}, Receipt: {score['receipt']}, Bank: {score['bank_statement']} → Chose: {best_match.upper()}")
        return best_match

    # Fallback
    print("[Debug] No strong match found → Classified as UNKNOWN")
    return "unknown"
