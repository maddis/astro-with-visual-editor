import requests
import os
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import pathlib
from datetime import datetime
import json

# This is relative to the script location
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = str(PROJECT_DIR / "output_markdown" / "blogs")
URL = "https://welovepets.care/wp-json/wp/v2/posts?categories=71&per_page=50"

# Define supported countries and their language codes
COUNTRIES = {
    "uk": {"language": "en"},  # Default English
    "se": {"language": "sv"}   # Swedish
}

def extract_text_editors(html):
    """Extract text content from text-editor widgets in HTML"""
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
    
    # If no text editors found, try to convert the entire content
    if not text_editors_markdown:
        markdown = md(html, heading_style="ATX")
        text_editors_markdown.append(markdown.strip())
    
    return text_editors, text_editors_markdown

def extract_image_urls(html):
    """Extract image URLs from HTML content"""
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    
    # Look for images in image widgets
    for widget in soup.find_all(attrs={"data-widget_type": "image.default"}):
        for img in widget.find_all("img"):
            src = img.get("src")
            if src:
                image_urls.append(src)
    
    # Also look for images directly in the content
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src not in image_urls:
            image_urls.append(src)
    
    return image_urls

def extract_categories_and_tags(post):
    """Extract categories and tags from post data"""
    categories = []
    tags = []
    
    # Extract categories
    if 'categories' in post:
        categories = post.get('categories', [])
    
    # Extract tags
    if 'tags' in post:
        tags = post.get('tags', [])
    
    return categories, tags

def format_date(date_str):
    """Format date string to YYYY-MM-DD format"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d')
    except Exception:
        return date_str

def extract_author(post):
    """Extract author information from post data"""
    author_id = post.get('author', 0)
    # In a real implementation, you might want to fetch author details
    # using the WordPress API with the author ID
    return author_id

def create_blog_path(post, country_code):
    """Create a path for the blog based on date, slug, and country code"""
    date_str = post.get('date', '')
    slug = post.get('slug', '')
    
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        day = date_obj.strftime('%d')
        return f"{country_code}/{year}/{month}/{day}/{slug}"
    except Exception:
        # Fallback if date parsing fails
        return f"{country_code}/{slug}"

def add_translation_note(markdown, target_language):
    """Add a note about translation for non-English content"""
    if target_language == 'en':
        return markdown
    
    language_names = {
        'sv': 'Swedish'
    }
    
    language_name = language_names.get(target_language, target_language.upper())
    note = f"\n\n> **Note:** This content is available in {language_name}. The actual translation would be implemented in a production environment.\n\n"
    
    return note + markdown

def fetch_and_write_blogs():
    """Fetch blog posts and write them as markdown files for each country"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    response = requests.get(URL)
    response.raise_for_status()
    posts = response.json()
    total_files = 0
    
    # Process posts for each country
    for country_code, country_info in COUNTRIES.items():
        country_total = 0
        target_language = country_info['language']
        
        print(f"Processing posts for country: {country_code} (language: {target_language})")
        
        for post in posts:
            # Use the original post for all countries (no translation for now)
            current_post = post
            
            slug = current_post.get("slug", "")
            title = current_post.get("title", {}).get("rendered", "")
            content = current_post.get("content", {}).get("rendered", "")
            excerpt = current_post.get("excerpt", {}).get("rendered", "")
            date = current_post.get("date", "")
            formatted_date = format_date(date)
            link = current_post.get("link", "")
            author = extract_author(current_post)
            categories, tags = extract_categories_and_tags(current_post)
            
            # Extract content
            text_editors, text_editors_markdown = extract_text_editors(content)
            image_urls = extract_image_urls(content)
            
            # Create blog path based on date, slug, and country code
            blog_path = create_blog_path(current_post, country_code)
            blog_dir = os.path.join(OUTPUT_DIR, os.path.dirname(blog_path))
            os.makedirs(blog_dir, exist_ok=True)
            
            # Download images and build local paths
            local_image_urls = []
            images_dir = os.path.join(blog_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            for img_url in image_urls:
                filename = os.path.basename(img_url.split("?")[0])
                local_path = os.path.join("images", filename)
                full_local_path = os.path.join(images_dir, filename)
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
            
            # Combine all markdown content
            all_markdown = "\n\n".join(text_editors_markdown) if text_editors_markdown else ""
            
            # Add translation note for non-English content
            if target_language != 'en':
                all_markdown = add_translation_note(all_markdown, target_language)
            
            # Create frontmatter
            frontmatter = {
                "title": title,
                "date": formatted_date,
                "excerpt": BeautifulSoup(excerpt, "html.parser").get_text().strip(),
                "link": link,
                "slug": slug,
                "layout": "layout-blog.njk",
                "permalink": f"/blog/{blog_path}/",
                "author": author,
                "categories": categories,
                "tags": tags,
                "local_image_urls": local_image_urls,
                "local_image_count": len(local_image_urls),
                "country": country_code,
                "language": target_language
            }
            
            # Write markdown file
            md_filename = os.path.join(blog_dir, f"{slug}.md")
            with open(md_filename, "w", encoding="utf-8") as f:
                f.write("---\n")
                yaml.dump(frontmatter, f, allow_unicode=True, sort_keys=False)
                f.write("---\n\n")
                f.write(all_markdown)
            
            country_total += 1
            total_files += 1
        
        print(f"Created {country_total} markdown files for country: {country_code}")
    
    print(f"Created a total of {total_files} blog markdown files in '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    fetch_and_write_blogs()
