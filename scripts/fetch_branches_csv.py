import requests
from bs4 import BeautifulSoup
import json

def fetch_branch_data(num_branches=5):
    url = f"https://welovepets.care/wp-json/wp/v2/pages?categories=80&per_page={num_branches}&page=1"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []
    
    branches_data = []
    for branch in response.json():
        content = branch.get('content', {}).get('rendered', '')
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all text editor widgets
        text_editors = soup.find_all(class_='elementor-widget-text-editor')
        
        # Get first and second summaries if they exist
        first_summary = text_editors[1].get_text(strip=True) if len(text_editors) > 0 else ''
        second_summary = text_editors[2].get_text(strip=True) if len(text_editors) > 1 else ''
        
        branch_info = {
            'title': branch.get('title', {}).get('rendered', ''),
            'first_summary': first_summary,
            'second_summary': second_summary
        }
        branches_data.append(branch_info)
    
    return branches_data

if __name__ == '__main__':
    import csv
    from datetime import datetime
    
    branches = fetch_branch_data()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'branch_data_{timestamp}.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'first_summary', 'second_summary']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for branch in branches:
            writer.writerow(branch)
    
    print(f"Data saved to {output_file}")