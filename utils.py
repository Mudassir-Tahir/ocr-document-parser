import re
import datetime
import os


def clean_text(text):
    """Removes line breaks, tabs, and extra whitespace."""
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def extract_match(pattern, text, group=1, fallback="N/A", flags=re.IGNORECASE | re.MULTILINE):
    """Extracts single match or returns fallback."""
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else fallback


def extract_all_matches(pattern, text, group=1, flags=re.IGNORECASE | re.MULTILINE):
    """Returns all matched groups in a list."""
    return [m.group(group).strip() for m in re.finditer(pattern, text, flags)]


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_currency(value):
    """Cleans and converts currency to float."""
    try:
        value = value.replace(",", "").replace("€", "").replace("$", "").replace("Rs", "").strip()
        return float(re.findall(r"-?\d+\.?\d*", value)[0])
    except Exception:
        return None


def format_date(value, fallback="N/A"):
    """Attempts to parse and standardize a date string."""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return fallback


def build_output_schema(doc_type, source_file, fields_dict, transactions=[]):
    return {
        "document_type": doc_type,
        "metadata": {
            "source_file": os.path.basename(source_file),
            "extracted_on": get_timestamp()
        },
        "fields": fields_dict,
        "transactions": transactions
    }
