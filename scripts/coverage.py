#!/usr/bin/env python
import requests
import csv
import os
import pathlib
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# This is relative to the script location
SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent

# URLs
SITEMAP_URL = "https://welovepets.care/sitemap.xml"
CATEGORIES_URL = "https://welovepets.care/wp-json/wp/v2/categories"
PAGES_URL_TEMPLATE = "https://welovepets.care/wp-json/wp/v2/pages?categories={}&per_page=100"
POSTS_URL = "https://welovepets.care/wp-json/wp/v2/posts"

# Output files
SITEMAP_CSV = str(PROJECT_DIR / "sitemap.csv")
CATEGORIES_CSV = str(PROJECT_DIR / "categories.csv")
POSTS_CSV = str(PROJECT_DIR / "posts.csv")
WORDPRESS_URLS_CSV = str(PROJECT_DIR / "wordpress_urls.csv")
COMPARISON_CSV = str(PROJECT_DIR / "comparison.csv")

def fetch_sitemap_urls():
    """
    Fetch all URLs from the sitemap and return them as a list
    """
    print(f"Fetching URLs from sitemap: {SITEMAP_URL}")
    response = requests.get(SITEMAP_URL)
    response.raise_for_status()
    
    # Parse the XML
    root = ET.fromstring(response.content)
    
    # Extract all URLs (handling XML namespaces)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    
    # Check if this is a sitemap index (contains other sitemaps)
    sitemap_locs = root.findall('.//ns:sitemap/ns:loc', namespaces)
    if sitemap_locs:
        print(f"Found a sitemap index with {len(sitemap_locs)} sitemaps")
        # This is a sitemap index, we need to fetch each individual sitemap
        for sitemap_loc in sitemap_locs:
            sub_sitemap_url = sitemap_loc.text
            print(f"Fetching sub-sitemap: {sub_sitemap_url}")
            sub_response = requests.get(sub_sitemap_url)
            sub_response.raise_for_status()
            sub_root = ET.fromstring(sub_response.content)
            for url_element in sub_root.findall('.//ns:url/ns:loc', namespaces):
                urls.append(url_element.text)
    else:
        # This is a regular sitemap
        for url_element in root.findall('.//ns:url/ns:loc', namespaces):
            urls.append(url_element.text)
    
    print(f"Found {len(urls)} URLs in sitemap")
    return urls

def save_to_csv(file_path, data, headers):
    """
    Save data to a CSV file
    """
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Saved {len(data)} rows to {file_path}")

def fetch_categories():
    """
    Fetch all categories from the WordPress API
    """
    print(f"Fetching categories from: {CATEGORIES_URL}")
    categories = []
    page = 1
    
    while True:
        response = requests.get(f"{CATEGORIES_URL}?per_page=100&page={page}")
        if response.status_code == 400:  # No more pages
            break
        response.raise_for_status()
        
        batch = response.json()
        if not batch:  # Empty response
            break
            
        categories.extend(batch)
        page += 1
        
        # Check if we've reached the last page
        if len(batch) < 100:
            break
    
    print(f"Found {len(categories)} categories")
    return categories

def fetch_pages_for_category(category_id):
    """
    Fetch all pages for a specific category
    """
    url = PAGES_URL_TEMPLATE.format(category_id)
    pages = []
    page = 1
    
    while True:
        response = requests.get(f"{url}&page={page}")
        if response.status_code == 400:  # No more pages
            break
        response.raise_for_status()
        
        batch = response.json()
        if not batch:  # Empty response
            break
            
        pages.extend(batch)
        page += 1
        
        # Check if we've reached the last page
        if len(batch) < 100:
            break
    
    return pages

def fetch_all_posts():
    """
    Fetch all posts from the WordPress API
    """
    print(f"Fetching posts from: {POSTS_URL}")
    posts = []
    page = 1
    
    while True:
        response = requests.get(f"{POSTS_URL}?per_page=100&page={page}")
        if response.status_code == 400:  # No more pages
            break
        response.raise_for_status()
        
        batch = response.json()
        if not batch:  # Empty response
            break
            
        posts.extend(batch)
        page += 1
        
        # Check if we've reached the last page
        if len(batch) < 100:
            break
    
    print(f"Found {len(posts)} posts")
    return posts

def normalize_url(url):
    """
    Normalize a URL for comparison (remove trailing slashes, etc.)
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    return f"{parsed.scheme}://{parsed.netloc}{path}"

def compare_urls(sitemap_urls, category_urls):
    """
    Compare URLs from sitemap and categories and generate a report
    """
    # Normalize URLs for comparison
    normalized_sitemap = {normalize_url(url) for url in sitemap_urls}
    normalized_category = {normalize_url(url) for url in category_urls}
    
    # Find URLs in sitemap but not in categories
    in_sitemap_only = normalized_sitemap - normalized_category
    
    # Find URLs in categories but not in sitemap
    in_category_only = normalized_category - normalized_sitemap
    
    # Calculate coverage percentage
    if normalized_category:
        coverage_percentage = (len(normalized_category) - len(in_category_only)) / len(normalized_category) * 100
    else:
        coverage_percentage = 0
    
    print(f"Coverage: {coverage_percentage:.2f}%")
    print(f"URLs in sitemap only: {len(in_sitemap_only)}")
    print(f"URLs in categories only: {len(in_category_only)}")
    
    # Prepare comparison data for CSV
    comparison_data = []
    
    # Add URLs in sitemap only
    for url in sorted(in_sitemap_only):
        comparison_data.append([url, "Sitemap Only", "Missing in Categories"])
    
    # Add URLs in categories only
    for url in sorted(in_category_only):
        comparison_data.append([url, "Missing in Sitemap", "Categories Only"])
    
    # Save comparison to CSV
    save_to_csv(COMPARISON_CSV, comparison_data, ["URL", "Sitemap Status", "Categories Status"])
    
    return coverage_percentage == 100

def main():
    # Fetch and save sitemap URLs
    sitemap_urls = fetch_sitemap_urls()
    sitemap_data = [[url] for url in sitemap_urls]
    save_to_csv(SITEMAP_CSV, sitemap_data, ["URL"])
    
    # Fetch categories
    categories = fetch_categories()
    
    # Fetch pages for each category
    category_pages = []
    category_urls = []
    
    for category in categories:
        category_id = category['id']
        category_name = category['name']
        print(f"Fetching pages for category: {category_name} (ID: {category_id})")
        
        pages = fetch_pages_for_category(category_id)
        print(f"Found {len(pages)} pages in category {category_name}")
        
        for page in pages:
            page_url = page['link']
            category_urls.append(page_url)
            category_pages.append([page_url, category_id, category_name])
    
    # Save category pages to CSV
    save_to_csv(CATEGORIES_CSV, category_pages, ["URL", "Category ID", "Category Name"])
    
    # Fetch all posts
    posts = fetch_all_posts()
    post_data = []
    post_urls = []
    
    for post in posts:
        post_url = post['link']
        post_urls.append(post_url)
        post_data.append([post_url, post['id'], post['title']['rendered']])
    
    # Save posts to CSV
    save_to_csv(POSTS_CSV, post_data, ["URL", "Post ID", "Post Title"])
    
    # Combine all WordPress URLs (both categories and posts)
    all_wordpress_urls = category_urls + post_urls
    wordpress_data = [[url] for url in all_wordpress_urls]
    save_to_csv(WORDPRESS_URLS_CSV, wordpress_data, ["URL"])
    
    # Compare URLs and check for 100% match
    print("\nComparing sitemap URLs with category URLs:")
    category_match = compare_urls(sitemap_urls, category_urls)
    
    print("\nComparing sitemap URLs with all WordPress URLs (categories + posts):")
    all_match = compare_urls(sitemap_urls, all_wordpress_urls)
    
    if all_match:
        print("\nSUCCESS: 100% match between sitemap and all WordPress URLs!")
    else:
        print("\nWARNING: Discrepancies found between sitemap and WordPress URLs.")
        print(f"Check {COMPARISON_CSV} for details.")

if __name__ == "__main__":
    main()
