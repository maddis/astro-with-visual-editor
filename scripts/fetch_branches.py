import requests
import os
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import shutil

# Fix the path to be inside the project directory
import pathlib
import sys

# Get number of branches from first arg and default to 5
num_branches = int(sys.argv[1]) if len(sys.argv) > 1 else 5

SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = str(PROJECT_DIR / "src" / "content" / "branch")
URL = "https://welovepets.care/wp-json/wp/v2/pages?categories=80&per_page={}&page=1".format(num_branches)

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
    """Extract image URLs from HTML content"""
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    
    # Look for images in various contexts
    for img in soup.find_all("img"):
        # Check both src and data-src attributes
        src = img.get("src") or img.get("data-src")
        if src and not src.startswith("data:"):
            image_urls.append(src)
    
    # Look for background images in style attributes
    for elem in soup.find_all(attrs={"style": True}):
        style = elem["style"]
        if "background-image" in style:
            match = re.search(r"url\\(['\"]?([^'\"\\)]+)['\"]?\\)", style)
            if match and not match.group(1).startswith("data:"):
                image_urls.append(match.group(1))
    
    return list(dict.fromkeys(image_urls))  # Remove duplicates

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

def extract_section_content(markdown_content, section_keywords, end_keywords=None):
    """Extract content for a specific section based on keywords"""
    section_content = ""
    lines = markdown_content.split('\n')
    in_section = False
    
    if not end_keywords:
        end_keywords = []
    
    # Add common section headers as end keywords if not already included
    common_section_headers = [
        "favourite places", "favorite places", "areas covered", "surrounding areas",
        "our services", "pricing", "get in touch", "contact us", "our team",
        "testimonials", "about us"
    ]
    
    for header in common_section_headers:
        if header not in [k.lower() for k in end_keywords]:
            # Don't add the header if it's one of our target section keywords
            if header not in [k.lower() for k in section_keywords]:
                end_keywords.append(header)
    
    for i, line in enumerate(lines):
        # Check if this line starts a section we're interested in
        if not in_section:
            for keyword in section_keywords:
                if keyword.lower() in line.lower():
                    in_section = True
                    section_content += line + '\n'
                    break
            continue
            
        # Check if this line ends the section
        should_end = False
        
        # Check for heading markers (###, ##, #)
        if line.startswith('###') or line.startswith('##') or line.startswith('# '):
            # Check if the heading contains any of our end keywords
            for keyword in end_keywords:
                if keyword.lower() in line.lower():
                    should_end = True
                    break
        else:
            # For non-heading lines, check if they contain exact end keywords
            for keyword in end_keywords:
                # Use a more precise check - the keyword should be a significant part of the line
                if keyword.lower() in line.lower() and len(keyword) > 5:
                    # Check if it looks like a heading (even without # markers)
                    if line.strip() == keyword or line.strip().startswith(keyword + ':') or line.strip().startswith(keyword + ' -'):
                        should_end = True
                        break
            
        if should_end:
            in_section = False
        else:
            section_content += line + '\n'
            
    return section_content.strip()

def extract_summary(markdown_content):
    """Extract the main summary content"""
    # Usually the first paragraphs before any specific sections
    return extract_section_content(
        markdown_content, 
        ["We Love Pets", "is your trusted", "specialise"], 
        ["areas covered", "favourite places", "our services", "get in touch"]
    )

def extract_areas_covered(markdown_content):
    """Extract areas covered content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["surrounding areas", "areas covered", "areas we cover", "postcodes"]
    )

def extract_favourite_places(markdown_content):
    """Extract favourite places content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["favourite places", "favorite places", "best places", "walking spots"]
    )

def extract_services(markdown_content):
    """Extract services content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["our services", "services we offer", "we specialise", "pet services"]
    )

def extract_cta(markdown_content):
    """Extract call to action content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["get in touch", "contact us", "book now", "call us today"]
    )

def extract_contact(markdown_content):
    """Extract contact content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["contact us", "get in touch", "book now", "call us today"]
    )

def extract_owner_name(markdown_content):
    """Extract owner name from the content by looking for 'Meet [Name]' pattern"""
    # Look for the pattern in the markdown content
    match = re.search(r'Meet ([A-Za-z]+(?:\s[A-Za-z]+)?)', markdown_content)
    if match:
        return match.group(1)
    return ""

def extract_phone_number(markdown_content):
    """Extract phone number from the content"""
    # Look for phone numbers in various formats with optional tel: prefix
    match = re.search(r'(?:tel:)?\s*([0-9]{5}\s*[0-9]{6}|[0-9]{11}|[0-9]{4}\s*[0-9]{3}\s*[0-9]{4})', markdown_content)
    if match:
        # Remove any spaces but keep as string to preserve leading zero
        return re.sub(r'\s+', '', match.group(1))
    return None

def extract_email(markdown_content):
    """Extract email from the content"""
    # Look for email addresses ending in @welovepets.email
    match = re.search(r'([a-zA-Z0-9._%+-]+@welovepets\.email)', markdown_content)
    if match:
        return match.group(1)
    return None

def extract_pricing(markdown_content):
    """Extract pricing content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["pricing", "prices", "costs", "cost"]
    )

def extract_guarantee(markdown_content):
    """Extract guarantee content from markdown"""
    return extract_section_content(
        markdown_content, 
        ["guarantee", "guaranteed", "guaranteed"]
    )

def extract_postcodes_from_content(content):
    """Extract postcode information from the areas covered content"""
    postcodes = []
    lines = content.split('\n')
    current_postcode = None
    current_areas = []
    
    for line in lines:
        # Look for postcode patterns like "CB23" or "PE19"
        postcode_match = re.search(r'\b([A-Z]{1,2}\d{1,2}[A-Z]?)\b', line)
        if postcode_match:
            # If we already have a postcode, save it before starting a new one
            if current_postcode:
                postcodes.append({
                    "code": current_postcode,
                    "areas": ", ".join(current_areas)
                })
            
            current_postcode = postcode_match.group(1)
            # Extract areas from the same line
            areas_text = re.sub(r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\b', '', line)
            areas_text = re.sub(r'[\*\–\-–]', '', areas_text).strip()
            current_areas = [area.strip() for area in areas_text.split(',') if area.strip()]
    
    # Don't forget to add the last postcode
    if current_postcode and current_areas:
        postcodes.append({
            "code": current_postcode,
            "areas": ", ".join(current_areas)
        })
    
    return postcodes

def extract_favourite_places_from_content(content):
    """Extract favourite places information from the content"""
    favourite_places = []
    lines = content.split('\n')
    current_place = None
    current_description = []
    
    for line in lines:
        # Look for place names that are bold or have specific formatting
        place_match = re.search(r'\*\*([^*]+)\*\*|^([A-Z][a-zA-Z\s]+)(?=\s)', line)
        if place_match:
            # If we already have a place, save it before starting a new one
            if current_place and current_description:
                favourite_places.append({
                    "name": current_place,
                    "description": " ".join(current_description)
                })
            
            current_place = place_match.group(1) if place_match.group(1) else place_match.group(2)
            # Extract description from the same line
            desc_text = re.sub(r'\*\*[^*]+\*\*', '', line).strip()
            current_description = [desc_text] if desc_text else []
        elif current_place and line.strip():
            # Continue adding to the current description
            current_description.append(line.strip())
    
    # Don't forget to add the last place
    if current_place and current_description:
        favourite_places.append({
            "name": current_place,
            "description": " ".join(current_description)
        })
    
    return favourite_places


def fetch_and_write_markdown():

    # Delete the output directory and all folders within it
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Fetching branch data from {URL}...")
    response = requests.get(URL)
    response.raise_for_status()
    pages = response.json()
    print(f"Found {len(pages)} branches to process")
    total_files = 0
        
    for page in pages:

        type = "branch"
        # Without "We Love Pets " prefix
        branchName = page.get("title", {}).get("rendered", "").split("We Love Pets ")[1]
        # Get date in the form YYYY-MM-DD
        pubDate = page.get("date", "")[:10]
        updatedDate = page.get("modified", "")[:10]

        slug = page.get("slug")
        title = page.get("title", {}).get("rendered", "")
        name = title.split("We Love Pets ")[1] if "We Love Pets " in title else title
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
        
        # For now, just record the image URLs without downloading them
        # This will make the script run much faster for testing
        for img_url in filtered_image_urls:
            filename = os.path.basename(img_url.split("?")[0])
            local_path = os.path.join(OUTPUT_DIR, "images", slug, filename)
            local_image_urls.append(local_path)
            
        print(f"  Processing branch: {slug}")
            
        typeform_urls = extract_typeform_urls(content)
        filtered_typeform_urls = [url for url in typeform_urls if url.startswith('https://form.typeform.com') or url.startswith('form.typeform.com')]
        google_maps_urls = extract_google_maps_urls(content)
        
        # Combine all markdown content
        all_markdown = "\n\n".join(text_editors_markdown) if text_editors_markdown else ""
        
        # Extract sections
        summary_content = extract_summary(all_markdown)
        areas_covered_content = extract_areas_covered(all_markdown)
        favourite_places_content = extract_favourite_places(all_markdown)
        services_content = extract_services(all_markdown)
        cta_content = extract_cta(all_markdown)
        pricing_content = extract_pricing(all_markdown)
        contact_content = extract_contact(all_markdown)
        guarantee_content = extract_guarantee(all_markdown)
        
        # Extract structured data from content
        postcodes = extract_postcodes_from_content(areas_covered_content)
        favourite_places = extract_favourite_places_from_content(favourite_places_content)
        
        # Track which sections exist for this branch
        sections = []
        if cta_content:
            sections.append("cta")
        if summary_content:
            sections.append("summary")
        if services_content:
            sections.append("services")
        if guarantee_content:
            sections.append("guarantee")
        if contact_content:
            sections.append("contact")
        if areas_covered_content:
            sections.append("areas_covered")
        if pricing_content:
            sections.append("pricing")
        if favourite_places_content:
            sections.append("favourite_places")
        
        # Create a single branch file with all data
        main_frontmatter = {
            "type": type,
            "branchName": branchName,
            "pubDate": pubDate,
            "updatedDate": updatedDate,
            "ownerName": extract_owner_name(all_markdown),
            "phoneNumber": extract_phone_number(all_markdown),
            "email": extract_email(all_markdown),
            # "title": title,
            # "name": name,
            # "date": date,
            # "excerpt": excerpt,
            # "link": link,
            # "slug": slug,
            # "layout": "layout-branch.njk",
            # "permalink": f"/branch/{slug}/",
            # "sections": ["cta", "summary", "services", "guarantee", "contact", "areas_covered", "pricing", "favourite_places"],
            # "local_image_urls": local_image_urls,
            # "local_image_count": len(local_image_urls),
            # "typeform_urls": filtered_typeform_urls,
            # "google_maps_urls": google_maps_urls,
            "areasSummary": "Our " + slug.capitalize() + " branch also covers surrounding areas. See the locations we cover listed below.",
            "postcodes": postcodes,
            # "favourite_places_summary": "We are extremely lucky to have so many beautiful dog walking spots in and around " + slug.capitalize() + ".",
            # "favourite_places": favourite_places
        }
        
        md_filename = os.path.join(OUTPUT_DIR, f"{slug}.md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(main_frontmatter, f, allow_unicode=True)
            f.write("---\n\n")
            # Write the main content
            # f.write(summary_content)
            f.write("\n\n")
        
        total_files += 1
    
    print(f"Created {total_files} markdown files in '{OUTPUT_DIR}' directory.")
    
    print(f"Created a total of {total_files} markdown files in '{OUTPUT_DIR}' directory.")
    print(f"- {len(pages)} unique branches")


if __name__ == "__main__":
    fetch_and_write_markdown()
