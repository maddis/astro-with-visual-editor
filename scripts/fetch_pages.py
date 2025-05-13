import requests
import os
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

OUTPUT_DIR = "../output_markdown/branches"
URL = "https://welovepets.care/wp-json/wp/v2/pages?categories=80&per_page=10&page=1"

def extract_text_editors(html):
    soup = BeautifulSoup(html, "html.parser")
    text_editors = []
    text_editors_markdown = []
    for widget in soup.find_all(attrs={"data-widget_type": "text-editor.default"}):
        widget_html = str(widget)
        markdown = md(widget_html, heading_style="ATX")
        text_editors_markdown.append(markdown.strip())
        text = widget.get_text(separator="\n", strip=True)
        if text:
            text_editors.append(text)
    return text_editors, text_editors_markdown

def extract_image_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    for widget in soup.find_all(attrs={"data-widget_type": "image.default"}):
        for img in widget.find_all("img"):
            src = img.get("src")
            if src:
                image_urls.append(src)
    return image_urls

def extract_typeform_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    typeform_urls = set()
    for tag in soup.find_all(['iframe', 'script', 'a']):
        for attr in ['src', 'href']:
            val = tag.get(attr)
            if val and re.search(r'typeform', val, re.IGNORECASE):
                typeform_urls.add(val)
        for attr, val in tag.attrs.items():
            if attr.startswith('data-') and isinstance(val, str) and re.search(r'typeform', val, re.IGNORECASE):
                typeform_urls.add(val)
    return list(typeform_urls)

def extract_google_maps_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    maps_urls = set()
    for tag in soup.find_all(True):
        for attr in ['src', 'href']:
            val = tag.get(attr)
            if val and 'maps.google.com' in val:
                maps_urls.add(val)
        for attr, val in tag.attrs.items():
            if attr.startswith('data-') and isinstance(val, str) and 'maps.google.com' in val:
                maps_urls.add(val)
    return list(maps_urls)

def fetch_and_write_markdown():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    response = requests.get(URL)
    response.raise_for_status()
    pages = response.json()
    for page in pages:
        slug = page.get("slug")
        title = page.get("title", {}).get("rendered", "")
        content = page.get("content", {}).get("rendered", "")
        excerpt = page.get("excerpt", {}).get("rendered", "")
        date = page.get("date", "")
        link = page.get("link", "")
        text_editors, text_editors_markdown = extract_text_editors(content)
        filtered_image_urls = [url for url in extract_image_urls(content) if "ProCare-Certification" not in url]
        # Download images and build local paths
        local_image_urls = []
        images_dir = os.path.join(OUTPUT_DIR, "images", slug)
        os.makedirs(images_dir, exist_ok=True)
        for img_url in filtered_image_urls:
            filename = os.path.basename(img_url.split("?")[0])
            local_path = os.path.join("images", slug, filename)
            full_local_path = os.path.join(OUTPUT_DIR, "images", slug, filename)
            try:
                if not os.path.exists(full_local_path):
                    img_resp = requests.get(img_url, timeout=15)
                    img_resp.raise_for_status()
                    with open(full_local_path, "wb") as img_file:
                        img_file.write(img_resp.content)
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
                continue
            local_image_urls.append(local_path)
        typeform_urls = extract_typeform_urls(content)
        filtered_typeform_urls = [url for url in typeform_urls if url.startswith('https://form.typeform.com') or url.startswith('form.typeform.com')]
        google_maps_urls = extract_google_maps_urls(content)
        frontmatter = {
            "title": title,
            "date": date,
            "excerpt": excerpt,
            "link": link,
            "slug": slug,
            "local_image_urls": local_image_urls,
            "local_image_count": len(local_image_urls),
            "typeform_urls": filtered_typeform_urls,
            "google_maps_urls": google_maps_urls
        }
        md_filename = os.path.join(OUTPUT_DIR, f"{slug}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(frontmatter, f, allow_unicode=True)
            f.write("---\n\n")
            # Write markdownified content as the body
            if text_editors_markdown:
                f.write("\n\n".join(text_editors_markdown))
                f.write("\n\n")
    print(f"Created {len(pages)} markdown files in '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    fetch_and_write_markdown()
