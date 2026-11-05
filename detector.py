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

def normalize(name):
    for fake, real in LOOKALIKE_CHARS.items():
        name = name.replace(fake, real)
    return name

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    msg = email.message_from_string(text)
    display_name, address = parseaddr(msg.get("From", ""))
    print(f"Sender: name '{display_name}', address {address}")
    print()

    print(f"  normalized: {normalize(address)}")
        
    links= find_links(text)
    print(f"Links: found {len(links)}")
    for link in links:
        reasons = check_link(link)
        if reasons:
            print(f"  SUSPICIOUS: {link}")
            for r in reasons:
                print(f"    - {r}")
        else:
            print(f"  ok: {link}")

if __name__ == "__main__":
    main()    