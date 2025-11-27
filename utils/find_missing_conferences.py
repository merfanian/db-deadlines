#!/usr/bin/env python3
"""
Utility script to find and add missing conference entries.
Searches for conferences that are predicted but not yet in the data files.
"""

import os
import re
import yaml
import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

# Configuration
CONFERENCES_DIR = Path(__file__).parent.parent / "_data" / "conferences"
CURRENT_YEAR = datetime.now().year


def load_conference_data():
    """Load all conference data from YAML files."""
    all_conferences = []
    for yml_file in CONFERENCES_DIR.glob("*.yml"):
        try:
            with open(yml_file, 'r', encoding='utf-8') as f:
                conferences = yaml.safe_load(f)
                if conferences:
                    if isinstance(conferences, list):
                        all_conferences.extend(conferences)
                    else:
                        all_conferences.append(conferences)
        except Exception as e:
            print(f"Error loading {yml_file}: {e}")
    return all_conferences


def get_latest_year_for_conference(conferences, title):
    """Get the latest year entry for a given conference title."""
    matching = [c for c in conferences if c.get('title') == title]
    if not matching:
        return None
    matching.sort(key=lambda x: x.get('year', 0), reverse=True)
    return matching[0]


def search_conference_website(title, year):
    """Search for conference website using Google search."""
    query = f"{title} {year} call for papers site:google.com OR site:github.io OR site:org"

    # Use a simple web search approach
    # In production, you might want to use Google Custom Search API
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract potential links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('sites.google.com' in href or 'github.io' in href or '.org' in href):
                    if '/cfp' in href.lower() or 'call' in href.lower() or 'papers' in href.lower():
                        links.append(href)
            return links[:3]  # Return top 3 results
    except Exception as e:
        print(f"Error searching for {title} {year}: {e}")

    return []


def extract_deadline_from_page(url):
    """Attempt to extract deadline information from a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()

            # Look for deadline patterns
            deadline_patterns = [
                r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'submission[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'due[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ]

            for pattern in deadline_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error extracting from {url}: {e}")

    return None


def find_missing_conferences():
    """Find conferences that should have entries but don't."""
    all_conferences = load_conference_data()

    # Group by title
    by_title = {}
    for conf in all_conferences:
        title = conf.get('title', '').split(
            '[')[0].strip()  # Remove track info
        if title not in by_title:
            by_title[title] = []
        by_title[title].append(conf)

    missing = []
    for title, entries in by_title.items():
        entries.sort(key=lambda x: x.get('year', 0), reverse=True)
        latest = entries[0]
        latest_year = latest.get('year', 0)

        # Check if we should have next year's entry
        if latest_year < CURRENT_YEAR:
            # Check if there's an entry for current year or next year
            has_current = any(e.get('year') == CURRENT_YEAR for e in entries)
            has_next = any(e.get('year') == CURRENT_YEAR + 1 for e in entries)

            if not has_current and not has_next:
                missing.append({
                    'title': title,
                    'latest_year': latest_year,
                    'suggested_year': CURRENT_YEAR,
                    'latest_entry': latest
                })

    return missing


def create_conference_entry(title, year, latest_entry, website_url=None):
    """Create a new conference entry based on template and found information."""
    conf_id = f"{title.lower().replace(' ', '').replace('-', '')}{year}"

    entry = {
        'title': title,
        'year': year,
        'id': conf_id,
        'link': website_url or latest_entry.get('link', '#'),
        'deadline': 'TBA',
        'timezone': latest_entry.get('timezone', 'UTC-12'),
        'place': 'TBA',
        'date': f'TBA, {year}',
        'sub': latest_entry.get('sub', 'ML'),
    }

    # Try to extract more info if website is provided
    if website_url:
        deadline = extract_deadline_from_page(website_url)
        if deadline:
            # Parse and format deadline
            try:
                # Try to parse the deadline
                # This is simplified - you might need more robust parsing
                entry['deadline'] = deadline
            except:
                pass

    return entry


def main():
    """Main function to find and suggest missing conferences."""
    print("Finding missing conference entries...")
    missing = find_missing_conferences()

    if not missing:
        print("No missing conferences found!")
        return

    print(f"\nFound {len(missing)} conferences that might need entries:")
    print("-" * 60)

    for conf in missing[:10]:  # Limit to first 10
        title = conf['title']
        year = conf['suggested_year']
        latest = conf['latest_entry']

        print(f"\n{title} {year}")
        print(f"  Latest entry: {latest.get('year')}")
        print(f"  Latest link: {latest.get('link', 'N/A')}")

        # Search for new website
        print(f"  Searching for {year} website...")
        links = search_conference_website(title, year)

        if links:
            print(f"  Found potential links:")
            for link in links:
                print(f"    - {link}")

            # Suggest creating entry
            suggested_url = links[0] if links else None
            entry = create_conference_entry(title, year, latest, suggested_url)

            print(f"\n  Suggested entry:")
            print(f"    ID: {entry['id']}")
            print(f"    Link: {entry['link']}")
            print(f"    Deadline: {entry['deadline']}")
        else:
            print(f"  No website found. You may need to search manually.")

        time.sleep(1)  # Be polite to servers

    print("\n" + "=" * 60)
    print("Note: This script provides suggestions. Please verify information")
    print("from official conference websites before adding entries.")


if __name__ == "__main__":
    main()
