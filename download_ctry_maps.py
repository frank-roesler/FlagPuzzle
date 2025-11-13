import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuration
OUTPUT_DIR = "country_outlines"
WIKIPEDIA_LIST_URL = "https://en.wikipedia.org/wiki/List_of_country_outlines"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_wikipedia_list(url):
    """Fetch and parse the Wikipedia list of country outlines."""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all country links (e.g., Afghanistan, Albania)
    for table in soup.find_all("table", class_="wikitable"):
        for row in table.find_all("tr")[1:]:  # Skip header row
            cols = row.find_all(["td", "th"])
            if len(cols) > 1:
                country_name = cols[0].get_text(strip=True)
                wiki_link_tag = cols[1].find("a")

                if wiki_link_tag and "href" in wiki_link_tag.attrs:
                    page_url = "https://en.wikipedia.org" + wiki_link_tag["href"]
                    extract_svg_from_page(page_url, country_name)


def extract_svg_from_page(url, country_name):
    """Fetch Wikipedia page and extract SVG image link."""
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find image link with format like File:LocationAfghanistan.svg
        for img_tag in soup.find_all("img", src=True):
            if "commons.wikimedia.org" in img_tag["src"] and "File:Location" in img_tag["src"]:
                svg_url = "https:" + img_tag["src"]

                # Download the SVG image
                filename = os.path.join(OUTPUT_DIR, f"{country_name}.svg")

                svg_response = requests.get(svg_url, headers=HEADERS)
                with open(filename, "wb") as f:
                    f.write(svg_response.content)

                print(f"Saved {country_name} to {filename}")
    except Exception as e:
        print(f"Error processing {url}: {e}")


if __name__ == "__main__":
    fetch_wikipedia_list(WIKIPEDIA_LIST_URL)
