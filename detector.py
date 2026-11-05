import sys
import re

def find_links(text):
    return re.findall(r"https?://[^/s]+", text)

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    links= find_links(text)
    print(f"Links: found {len(links)}")
    for link in links:
        print(f"  {link}")


if __name__ == "__main__":
    main()    