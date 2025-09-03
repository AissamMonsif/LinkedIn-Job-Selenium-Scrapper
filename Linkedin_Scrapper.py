import logging
from linkedin_scraper.cli import main as _main

logging.basicConfig(filename="scraping.log", level=logging.INFO)

def main():
    return _main()

if __name__ == "__main__":
    raise SystemExit(main())
