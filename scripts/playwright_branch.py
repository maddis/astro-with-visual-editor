import os
import shutil
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def make_folder(path):
    os.makedirs(path, exist_ok=True)

def get_resource_type(url):
    if url.endswith(".css"):
        return "css"
    elif url.endswith(".js"):
        return "js"
    elif any(url.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
        return "img"
    elif any(url.endswith(ext) for ext in [".woff", ".woff2", ".ttf", ".eot"]):
        return "fonts"
    else:
        return "other"

def download_file(session, url, folder):
    try:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = "index"
        local_path = os.path.join(folder, filename)

        if os.path.exists(local_path):
            return local_path  # Already downloaded

        r = session.get(url, timeout=15)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(r.content)
            print(f"Downloaded: {url}")
            return local_path
        else:
            print(f"Failed to download {url} (status {r.status_code})")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def scrape_site(url, output_folder):
    make_folder(output_folder)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print("Loading page...")
        page.goto(url, wait_until='networkidle')

        html = page.content()
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        session = requests.Session()
        asset_map = {}

        # Set up /public/ folder structure
        public_root = os.path.join(output_folder, "public")
        folders = {
            "css": os.path.join(public_root, "css"),
            "js": os.path.join(public_root, "js"),
            "img": os.path.join(public_root, "img"),
            "fonts": os.path.join(public_root, "fonts"),
            "other": os.path.join(public_root, "other"),
        }
        for folder in folders.values():
            make_folder(folder)

        # Download assets and map references
        for tag in page.locator("link, script, img").element_handles():
            src = tag.get_attribute("href") or tag.get_attribute("src")
            if src and not src.startswith("data:"):
                full_url = urljoin(base_url, src)
                resource_type = get_resource_type(full_url)
                folder = folders.get(resource_type, folders["other"])

                downloaded_path = download_file(session, full_url, folder)
                if downloaded_path:
                    rel_path = os.path.relpath(downloaded_path, output_folder).replace('\\', '/')
                    absolute_path = f"/{rel_path}"
                    asset_map[src] = absolute_path

        # Replace references in HTML with absolute /public/ paths
        for original, absolute in asset_map.items():
            html = html.replace(original, absolute)

        # Save final HTML
        html_path = os.path.join(output_folder, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        browser.close()
        print(f"\n🎉 Saved page to {html_path}")
        print("✅ Resources stored in /public")

if __name__ == "__main__":
    url = "https://welovepets.care/branch/cambourne/"
    output_folder = "branch"

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    scrape_site(url, output_folder)
