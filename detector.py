import sys
import re
from urllib.parse import urlparse

#finds the links in the text
def find_links(text):
    return re.findall(r"https?://[^\s]+", text)

#checks if the link is an ip address
def is_ip_link(link):
    return re.match(r"https?://\d+\.\d+\.\d+\.\d+", link) is not None

def get_host(link):
    return urlparse(link).hostname or ""

def real_domain(host):
    parts = host.split(".")
    return ".".join(parts[-2:])

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    links= find_links(text)
    print(f"Links: found {len(links)}")
    for link in links:
        host = get_host(link)
        print(f"  {link}")
        print(f"    host: {host}")
        print(f"    real domain: {real_domain(host)}")
        if is_ip_link(link):
            print("    - IP address instead of domain")


if __name__ == "__main__":
    main()    