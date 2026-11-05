import sys

def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    print (f"Read {len(text)} characters from {path}")  
    print()
    print(text)


if __name__ == "__main__":
    main()    