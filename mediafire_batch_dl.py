import requests
import os
from bs4 import BeautifulSoup
import time

# ==============================
# CONFIG
# ==============================
FOLDER_KEY = "3svttldmy696v"  # <-- your folder key
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.mediafire.com/"
}


# ==============================
# STEP 1: Get folder file list
# ==============================
def get_folder_files(folder_key):
    url = "https://www.mediafire.com/api/1.5/folder/get_content.php"

    params = {
        "content_type": "files",
        "filter": "all",
        "order_by": "name",
        "order_direction": "asc",
        "chunk": 1,
        "version": "1.5",
        "folder_key": folder_key,
        "response_format": "json"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    return data["response"]["folder_content"]["files"]


# ==============================
# STEP 2: Extract real download link
# ==============================
def extract_real_download_link(file_page_url):
    response = requests.get(file_page_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    button = soup.find("a", {"id": "downloadButton"})
    if button:
        return button["href"]
    return None


# ==============================
# STEP 3: Download actual file
# ==============================
def download_file(download_url, filename):
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    with requests.get(download_url, headers=headers, stream=True, allow_redirects=True) as r:
        r.raise_for_status()

        # Make sure we're not saving HTML
        if "text/html" in r.headers.get("Content-Type", ""):
            print(f"❌ Skipped {filename} (HTML detected)")
            return

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

    print(f"✅ Downloaded: {filename}")


# ==============================
# MAIN
# ==============================
files = get_folder_files(FOLDER_KEY)

print(f"Found {len(files)} files\n")

for file in files:
    filename = file["filename"]
    file_page = file["links"]["normal_download"]

    print(f"Processing: {filename}")

    real_link = extract_real_download_link(file_page)

    if real_link:
        download_file(real_link, filename)
        time.sleep(1)  # small delay to avoid rate limit
    else:
        print(f"❌ Could not extract link for {filename}")

print("\nAll done.")