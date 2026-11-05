import re
import sys
import email
from email.utils import parseaddr
from urllib.parse import urlparse

KNOWN_BRANDS = {
    "paypal": "paypal.com",
    "microsoft": "microsoft.com",
    "google": "google.com",
    "apple": "apple.com",
}

SUSPICIOUS_TLDS = {"xyz", "top", "click", "zip"}

LOOKALIKE_CHARS = {"0": "o", "1": "l", "3": "e", "5": "s", "rn": "m", "vv": "w"}

SUSPICIOUS_PHRASES = {
    "urgency": ["immediately", "urgent", "within 24 hours", "act now", "as soon as possible"],
    "threat": ["suspended", "locked", "unusual activity", "unauthorized", "will be closed"],
    "credentials": ["verify your account", "confirm your password", "log in", "update your details", "security code"],
    "money": ["payment", "invoice", "refund", "wire transfer", "gift card"],
    "generic greeting": ["dear customer", "dear user", "dear account holder"],
}

DANGEROUS_EXTENSIONS = {"exe", "scr", "js", "vbs", "bat", "cmd", "msi", "ps1", "jar"}
DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "jpg", "png", "txt"}

MACRO_EXTENSIONS = {"docm", "xlsm", "pptm"}
ARCHIVE_EXTENSIONS = {"zip", "rar", "7z", "iso"}

#finds the links in the text
def find_links(text):
    return re.findall(r"https?://[^\s]+", text)

#checks if the link is an ip address
def is_ip_link(link):
    return re.match(r"https?://\d+\.\d+\.\d+\.\d+", link) is not None

#returns the host of the link
def get_host(link):
    return urlparse(link).hostname or ""

#returns the real domain of the host
def real_domain(host):
    parts = host.split(".")
    return ".".join(parts[-2:])

#checks if the host pretends to be a known brand but has a different real domain
def brand_mismatch(host):
    domain = real_domain(host)
    for brand, official in KNOWN_BRANDS.items():
        if brand in host and domain != official:
            return brand
    return None

#checks if the host has a suspicious top-level domain
def has_suspicious_tld(host):
    return host.split(".")[-1] in SUSPICIOUS_TLDS

#check the link for suspicious characteristics and return reasons if any
def check_link(link):
    reasons = []
    host = get_host(link)

    if is_ip_link(link):
        reasons.append("IP address instead of domain")

    brand = brand_mismatch(host)
    if brand:
        reasons.append(f"pretends to be {brand}, real domain is {real_domain(host)}")

    if has_suspicious_tld(host):
        reasons.append(f"suspicious ending .{host.split('.')[-1]}")

    return reasons

#normalize the name by replacing lookalike characters with their real counterparts
def normalize(name):
    for fake, real in LOOKALIKE_CHARS.items():
        name = name.replace(fake, real)
    return name

#check the sender's email address and display name for suspicious characteristics
def check_sender(from_header):
    reasons = []
    display_name, address = parseaddr(from_header)
    domain = address.split("@")[-1].lower()
    real = real_domain(domain)
    name_part = real.split(".")[0]
    normalized = normalize(name_part)

    for brand, official in KNOWN_BRANDS.items():
        if real == official:
           continue
        if brand in normalized:
            if brand in name_part:
                reasons.append(f"domain {domain} uses the name {brand} but is not {official}")
            else:
                reasons.append(f"lookalike domain {domain} imitates {official}")     

        if brand in display_name.lower():
             reasons.append(f"display name '{display_name}' says {brand}, but the address is {address}")

    return reasons

#get the body of the email message, preferring text/plain parts
def get_body(msg):
    parts = []
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            parts.append(payload.decode(charset, errors="replace"))
    return "\n".join(parts)

def check_wording(subject, body):
    reasons = []
    text = f"{subject}\n{body}".lower()
    for category, phrases in SUSPICIOUS_PHRASES.items():
        found = [p for p in phrases if re.search(r"\b" + re.escape(p) + r"\b", text)]
        if found:
            reasons.append(f"{category}: {', '.join(found)}")
    return reasons

def get_attachments(msg):
    names = []
    for part in msg.walk():
        filename = part.get_filename()
        if filename:
            names.append(filename)
    return names

def check_attachment(filename):
    reasons = []
    parts = filename.lower().split(".")
    ext = parts[-1] if len(parts) > 1 else ""

    if ext in DANGEROUS_EXTENSIONS:
        reasons.append(f"dangerous file type .{ext}")

    if len(parts) > 2 and parts[-2] in DOCUMENT_EXTENSIONS and ext in DANGEROUS_EXTENSIONS | ARCHIVE_EXTENSIONS:
        reasons.append(f"double extension: looks like .{parts[-2]} but is really .{ext}")

    if ext in MACRO_EXTENSIONS:
        reasons.append(f"Office file with macros .{ext}")

    if ext in ARCHIVE_EXTENSIONS:
        reasons.append(f"compressed archive .{ext} can hide other files")   

    return reasons

def print_reasons(title, reasons):
    print(f"{title}:")
    if reasons:
        for r in reasons:
            print(f"  - {r}")
    else:
        print("  ok")

def print_items(title, items):
    print(f"{title}: found {len(items)}")
    for name, reasons in items.items():
        if reasons:
            print(f"  SUSPICIOUS: {name}")
            for r in reasons:
                print(f"    - {r}")
        else:
            print(f"  ok: {name}")

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    msg = email.message_from_string(text)
    print_reasons("Sender", check_sender(msg.get("From", "")))
    print_reasons("Wording", check_wording(msg.get("Subject", ""), get_body(msg)))

    attachments = {name: check_attachment(name) for name in get_attachments(msg)}
    links = {link: check_link(link) for link in find_links(text)}
    print_items("Attachments", attachments)
    print_items("Links", links)

if __name__ == "__main__":
    main()    