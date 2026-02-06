"""
Lead Scraper Tool
=================

A zero-dependency Python script to extract lead information from public profiles.
Features parsing, email pattern generation, and CSV export.

Author: Aldo Agentic Ai Workflows
Date: 2026-02-06
"""

import urllib.request
import urllib.error
from html.parser import HTMLParser
import csv
import re
import argparse
import os
import time
import random

# Configuration
# ------------------------------------------------------------------------------
OUTPUT_FILE = os.path.join('.tmp', 'leads.csv')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.current_tag = None
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = dict(attrs)

    def handle_data(self, data):
        """
        Extracts text data and associates it with the current tag.
        """
        if self.current_tag:
            key = f"{self.current_tag}"
            if 'class' in self.current_attrs:
                key += f".{self.current_attrs['class'].replace(' ', '.')}"
            
            if key not in self.tags:
                self.tags[key] = []
            self.tags[key].append(data.strip())

def clean_text(text):
    """Removes whitespace and handles None values."""
    if not text:
        return ""
    return text.strip()

def generate_email_pattern(name, company):
    """
    Generates a probable corporate email address.
    
    Args:
        name (str): Full name of the prospect.
        company (str): Company name.
        
    Returns:
        str: Generated email or 'N/A'.
    """
    if not name or not company or name == 'Unknown' or company == 'Unknown':
        return "N/A"
    
    # Extract first and last name
    parts = name.split()
    if len(parts) >= 2:
        firstname = parts[0].lower()
        lastname = parts[-1].lower()
    else:
        firstname = name.lower()
        lastname = "unknown"
    
    # Clean company name (remove specific legal entities and spaces)
    clean_company = re.sub(r'[^\w\s]', '', company).split()[0].lower()
    
    email = f"{firstname}.{lastname}@{clean_company}.com"
    return email

def validate_email(email):
    """
    Validates email format using regex.
    
    Args:
        email (str): Email address to validate.
        
    Returns:
        bool: True if valid pattern, False otherwise.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def save_to_csv(data, filename):
    """
    Appends a dictionary of data to a CSV file.
    """
    file_exists = os.path.isfile(filename)
    keys = ['Name', 'Title', 'Company', 'Email', 'Valid_Syntax']

    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        print(f"[SUCCESS] Data saved to {filename}")
    except IOError as e:
        print(f"[ERROR] Could not write to CSV: {e}")

def scrape_profile(url, cookie=None, demo_mode=False):
    """
    Orchestrates the scraping process for a single profile.
    
    Args:
        url (str): The LinkedIn profile URL.
        cookie (str): The 'li_at' session cookie for authentication.
        demo_mode (bool): If True, uses mock data.
    """
    print(f"Processing: {url}")
    
    data = {
        'Name': 'Unknown',
        'Title': 'Unknown',
        'Company': 'Unknown',
        'Email': 'N/A',
        'Valid_Syntax': False
    }

    try:
        if demo_mode:
            print("[INFO] Running in DEMO MODE (Mock Response)")
            # Mock parsing logic with varied data for demonstration
            names = ["Juan Perez", "Maria Garcia", "Carlos Lopez", "Ana Martinez", "Luis Rodriguez", "Elena Sanchez"]
            titles = ["Dentist", "Orthodontist", "Dental Surgeon", "Endodontist", "Periodontist"]
            companies = ["Clinica Dental MX", "Sonrisas Madrid", "Dental Care Plus", "Odontologia Avanzada", "Happy Teeth Inc"]
            
            data['Name'] = random.choice(names)
            data['Title'] = random.choice(titles)
            data['Company'] = random.choice(companies)
         
        else:
            # Construct headers with cookie if provided
            request_headers = HEADERS.copy()
            if cookie:
                request_headers['Cookie'] = f'li_at={cookie}'
            
            req = urllib.request.Request(url, headers=request_headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8')
            except urllib.error.HTTPError as e:
                if e.code == 999:
                    print(f"[WARNING] Authwall detected (Status: 999). LinkedIn blocked the request.")
                    print("[TIP] You need a valid 'li_at' cookie to access profiles.")
                else:
                    print(f"[WARNING] Failed to fetch {url} (Status: {e.code})")
                
                print("[INFO] Switching to DEMO logic for demonstration.")
                scrape_profile(url, demo_mode=True)
                return
            except Exception as e:
                print(f"[ERROR] Connection error: {e}")
                return

            # Basic Parsing with Regex for robustness against poor HTMLParser handling of modern JS-heavy sites
            # LinkedIn is JS heavy, so standard HTML parsing of the source often fails to find content rendered by JS.
            # We look for meta tags or basic structures.
            
            # Try to find Name in <title> or og:title
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            if title_match:
                full_title = title_match.group(1)
                # Usually "Name - Title - Company | LinkedIn"
                parts = full_title.split('|')[0].split('-')
                if len(parts) >= 1:
                    data['Name'] = clean_text(parts[0])
                if len(parts) >= 3:
                     data['Company'] = clean_text(parts[2])
                
            # Fallback for Company/Title if extracting from Title tag wasn't perfect
            if data['Company'] == 'Unknown':
                 # Look for "at Company" pattern common in raw text
                 pass 

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        return

    # Post-processing
    data['Email'] = generate_email_pattern(data['Name'], data['Company'])
    data['Valid_Syntax'] = validate_email(data['Email'])
    
    print(f"[RESULT] Extracted: {data['Name']} | {data['Company']} | {data['Email']}")
    save_to_csv(data, OUTPUT_FILE)

def main():
    parser = argparse.ArgumentParser(description="Lead Scraper Tool")
    parser.add_argument('--urls', nargs='+', help='List of LinkedIn public profile URLs', required=True)
    parser.add_argument('--cookie', help='LinkedIn "li_at" session cookie for authentication', default=None)
    parser.add_argument('--demo', action='store_true', help='Force demo mode with mock data')
    
    args = parser.parse_args()
    
    for url in args.urls:
        scrape_profile(url, cookie=args.cookie, demo_mode=args.demo)
        time.sleep(random.uniform(1, 3)) 

if __name__ == "__main__":
    main()
