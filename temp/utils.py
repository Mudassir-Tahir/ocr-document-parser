import re
import datetime

def clean_text(text):
    """
    Normalize text by stripping whitespace, extra newlines, and unwanted characters.
    """
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_match(pattern, text, group=1, fallback="N/A", flags=re.IGNORECASE):
    """
    Reusable regex extractor with fallback if not matched.
    """
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else fallback

def get_timestamp():
    """
    Return current timestamp in YYYY-MM-DD HH:MM:SS format.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_currency(value):
    """
    Convert string like '1,234.56' or '1234' to float, safely.
    """
    try:
        return float(value.replace(",", "").strip())
    except:
        return None
