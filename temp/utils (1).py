import re
import datetime
import os

def clean_text(text):
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_match(pattern, text, group=1, fallback="N/A", flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else fallback

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_currency(value):
    try:
        return float(value.replace(",", "").strip())
    except:
        return None

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
