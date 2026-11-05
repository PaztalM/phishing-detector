import sys
import re

#finds the links in the text
def find_links(text):
    return re.findall(r"https?://[^\s]+", text)

#checks if the link is an ip address
def is_ip_link(link):
    return re.match(r"https?://\d+\.\d+\.\d+\.\d+", link) is not None

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    links= find_links(text)
    print(f"Links: found {len(links)}")
    for link in links:
        if is_ip_link(link):
            print(f"  SUSPICIOUS: {link}")
            print("    - IP address instead of domain")
        else:
            print(f"  ok: {link}")


if __name__ == "__main__":
    main()    