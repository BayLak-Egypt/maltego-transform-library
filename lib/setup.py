import re

def detect_input_type(value):
    value = value.strip()
    if re.match(r"^\+?[0-9]{7,15}$", value): return "Phone"
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value): return "IP"
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value): return "Email"
    if re.match(r"^https?://", value): return "URL"
    if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value): return "Domain"
    if " " in value: return "Person"
    return "Phrase"

def get_maltego_type(input_type):
    mapping = {
        "IP": "maltego.IPv4Address",
        "Email": "maltego.EmailAddress",
        "Domain": "maltego.Domain",
        "Phone": "maltego.PhoneNumber",
        "URL": "maltego.URL",
        "Person": "maltego.Person",
        "Phrase": "maltego.Phrase"
    }
    return mapping.get(input_type, "maltego.Phrase")
