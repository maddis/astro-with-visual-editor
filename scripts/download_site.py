import os
import shutil
import subprocess
from html import unescape

def download_site(url, output_folder):
    # Step 1: Use wget to download all resources
    print(f"Downloading site: {url}")
    subprocess.run([
        "wget",
        "--recursive",                 # Download the entire page
        "--page-requisites",           # Get all assets like images, CSS
        "--html-extension",            # Save files with .html extension
        "--convert-links",             # Make links suitable for offline viewing
        "--no-parent",                 # Don't ascend to parent folders
        "--adjust-extension",          # Save the correct file extension
        "--directory-prefix", output_folder,  # Save to a specific folder
        "--domains", url.split('/')[2], # Limit download to domain
        url
    ], check=True)
    
    print(f"Downloaded site into: {output_folder}")

def decode_html_files(base_folder):
    # Step 2: Find and decode all HTML files
    print(f"Decoding HTML entities inside: {base_folder}")
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                decoded_content = unescape(content)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(decoded_content)
    print("Finished decoding HTML files.")

def main():
    url = "https://welovepets.care/branch/cambourne/"
    output_folder = "offline_site"

    # Clean output folder if exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    
    # Download and decode
    download_site(url, output_folder)
    decode_html_files(output_folder)

if __name__ == "__main__":
    main()
