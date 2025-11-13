#!/usr/bin/env python3
"""
download_wiki_fullres_images.py
Downloads *full-resolution* images from a Wikipedia article page.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

HEADERS = {
    "User-Agent": "WikiFullResImageDownloader/1.0 (contact: your_email@example.com)",
    "Accept-Language": "en-US,en;q=0.9",
}

WIKI_BASE = "https://en.wikipedia.org"
API_URL = WIKI_BASE + "/w/api.php"


def get_fullres_image_url(file_title):
    """Get full-resolution URL for a File: page title via MediaWiki API."""
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    }
    resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    pages = data.get("query", {}).get("pages", {})
    for p in pages.values():
        info = p.get("imageinfo")
        if info and "url" in info[0]:
            return info[0]["url"]
    return None


def sanitize_filename(name):
    name = unquote(name)
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name


def download_file(url, dest_path):
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)


def download_wiki_images(topic, save_dir="wiki_images"):
    os.makedirs(save_dir, exist_ok=True)
    url = f"{WIKI_BASE}/wiki/{topic.replace(' ', '_')}"
    print(f"[+] Fetching article: {url}")

    # get HTML
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise RuntimeError(f"Failed to fetch page ({res.status_code})")

    soup = BeautifulSoup(res.text, "html.parser")

    # Collect possible File: links (those lead to full-res info)
    file_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/wiki/File:"):
            file_links.add(urljoin(WIKI_BASE, href))

    print(f"[+] Found {len(file_links)} file pages referenced.")

    downloaded = 0
    for file_url in file_links:
        file_title = file_url.split("/wiki/")[-1]
        file_title = unquote(file_title)
        print(f" -> Resolving {file_title} ...")
        try:
            fullres_url = get_fullres_image_url(file_title)
            if not fullres_url:
                print(f"    ⚠️ No full-res image found for {file_title}")
                continue

            filename = sanitize_filename(os.path.basename(fullres_url))
            dest_path = os.path.join(save_dir, filename)

            key_word = ["projection", "map", "location"]

            if any(word in filename for word in key_word):
                print(f"    Downloading: {fullres_url}")
                download_file(fullres_url, dest_path)
                downloaded += 1
                time.sleep(0.2)  # be polite

        except Exception as e:
            print(f"    ⚠️ Failed for {file_title}: {e}")

    print(f"\n✅ Done. Downloaded {downloaded} images to '{save_dir}'.\n")


if __name__ == "__main__":
    topic = input("Enter Wikipedia topic (e.g., Germany): ").strip()
    download_wiki_images(topic)
