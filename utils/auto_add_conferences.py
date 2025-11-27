#!/usr/bin/env python3
"""
Automatically find and add missing conference entries based on predictions.
This script should be run periodically to keep the conference data up to date.

Usage:
    python utils/auto_add_conferences.py [--dry-run] [--conference CONF_NAME]
"""

import re
import yaml
import sys
import argparse
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote, urljoin

# Configuration
CONFERENCES_DIR = Path(__file__).parent.parent / "_data" / "conferences"
CURRENT_YEAR = datetime.now().year


def load_conference_data():
    """Load all conference data from YAML files."""
    all_conferences = []
    for yml_file in sorted(CONFERENCES_DIR.glob("*.yml")):
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


def get_conference_file(title):
    """Get the YAML file path for a conference title."""
    # Convert title to filename (lowercase, remove special chars)
    filename = title.lower().replace(' ', '').replace('-', '').replace('&', '')
    filename = re.sub(r'[^a-z0-9]', '', filename)
    return CONFERENCES_DIR / f"{filename}.yml"


def search_google(title, year):
    """Search Google for conference website."""
    # First try to find "important dates" page specifically
    query_important_dates = f'"{title}" {year} "important dates" OR "important-dates" site:google.com'
    search_url = f"https://www.google.com/search?q={quote(query_important_dates)}"

    links = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find result links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.startswith('/url?q='):
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    if any(domain in actual_url for domain in ['sites.google.com', 'github.io', '.org', '.edu', '.com']):
                        if ('important' in actual_url.lower() and 'date' in actual_url.lower()) or \
                           (title.lower() in link.get_text().lower() and str(year) in link.get_text()):
                            links.append(actual_url)
    except Exception as e:
        print(f"  Error searching important dates: {e}")

    # If no important dates page found, search for general CFP
    if not links:
        query = f'"{title}" {year} "call for papers" OR "cfp" site:google.com'
        search_url = f"https://www.google.com/search?q={quote(query)}"

        try:
            response = requests.get(search_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find result links
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and href.startswith('/url?q='):
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        if any(domain in actual_url for domain in ['sites.google.com', 'github.io', '.org', '.edu', '.com']):
                            if title.lower() in link.get_text().lower() or str(year) in link.get_text():
                                links.append(actual_url)
        except Exception as e:
            print(f"  Error searching CFP: {e}")

    return list(dict.fromkeys(links))[:5]  # Remove duplicates, return top 5


def find_important_dates_link(url):
    """Try to find an 'Important Dates' link on the page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for links containing "important" and "date"
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                href = link.get('href', '').lower()
                if ('important' in link_text and 'date' in link_text) or \
                   ('important' in href and 'date' in href):
                    # Resolve relative URLs
                    if href.startswith('http'):
                        return href
                    else:
                        return urljoin(url, href)
    except Exception:
        pass
    return None


def extract_conference_info(url, title, year):
    """Extract conference information from a webpage."""
    info = {
        'link': url,
        'deadline': None,
        'abstract_deadline': None,
        'place': None,
        'date': None,
        'start': None,
        'end': None,
        'timezone': 'UTC-12'
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        # First, try to find "Important Dates" link and follow it
        important_dates_url = find_important_dates_link(url)
        if important_dates_url and important_dates_url != url:
            print(f"      Found 'Important Dates' link: {important_dates_url}")
            url = important_dates_url

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            text_lower = text.lower()

            # First, try to find "Important Dates" section
            important_dates_section = None
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
                heading_text = heading.get_text().lower()
                if 'important' in heading_text and 'date' in heading_text:
                    # Get the section content - look for next elements
                    section_text = heading.get_text()
                    # Try to get content after the heading
                    current = heading.next_sibling
                    count = 0
                    while current and count < 10:  # Get next 10 siblings
                        if hasattr(current, 'get_text'):
                            section_text += ' ' + current.get_text()
                        current = current.next_sibling
                        count += 1
                    important_dates_section = section_text
                    break

            # If we found important dates section, prioritize that text
            search_text = important_dates_section.lower(
            ) if important_dates_section else text_lower

            # Extract deadline - look for common patterns
            deadline_patterns = [
                # Pattern: "Paper submission deadline: MM/DD/YYYY" or "Deadline: MM/DD/YYYY"
                r'(?:paper\s+)?(?:submission\s+)?deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                # Pattern: "MM/DD/YYYY (deadline|submission|due)"
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})[:\s]*(?:\(.*?\))?[:\s]*(?:deadline|submission|due)',
                # Pattern: "Submission: MM/DD/YYYY"
                r'submission[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                # Pattern: "Due: MM/DD/YYYY"
                r'due[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            ]

            for pattern in deadline_patterns:
                matches = re.finditer(pattern, search_text)
                for match in matches:
                    month, day, year_part = match.groups()
                    if len(year_part) == 2:
                        year_part = '20' + year_part
                    # Check if this looks like a deadline (not too far in past/future)
                    try:
                        deadline_date = datetime(
                            int(year_part), int(month), int(day))
                        # Accept deadlines from previous year (for conferences in early year) to next year
                        if deadline_date.year >= year - 1 and deadline_date.year <= year + 1:
                            if not info['deadline'] or deadline_date.year == year or deadline_date.year == year - 1:
                                info['deadline'] = f"{year_part}-{month.zfill(2)}-{day.zfill(2)} 23:59:59"
                                break
                    except (ValueError, TypeError):
                        pass
                if info['deadline']:
                    break

            # Extract abstract deadline
            abstract_patterns = [
                r'abstract[:\s]+(?:deadline|due|submission)[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})[:\s]*(?:\(.*?\))?[:\s]*abstract',
            ]

            for pattern in abstract_patterns:
                matches = re.finditer(pattern, search_text)
                for match in matches:
                    month, day, year_part = match.groups()
                    if len(year_part) == 2:
                        year_part = '20' + year_part
                    try:
                        abstract_date = datetime(
                            int(year_part), int(month), int(day))
                        if abstract_date.year >= year - 1 and abstract_date.year <= year + 1:
                            info['abstract_deadline'] = f"{year_part}-{month.zfill(2)}-{day.zfill(2)} 23:59:59"
                            break
                    except (ValueError, TypeError):
                        pass
                if info['abstract_deadline']:
                    break

            # Extract location
            location_patterns = [
                r'(?:venue|location|place|held in)[:\s]+([A-Z][a-zA-Z\s,]+(?:USA|UK|Italy|Japan|China|Canada|Germany|France|Spain|Netherlands|Australia))',
                r'([A-Z][a-zA-Z\s,]+(?:USA|UK|Italy|Japan|China|Canada|Germany|France|Spain|Netherlands|Australia))',
            ]

            for pattern in location_patterns:
                match = re.search(pattern, text)
                if match:
                    info['place'] = match.group(1).strip()
                    break

            # Extract conference dates
            date_patterns = [
                r'(\w+)\s+(\d{1,2})[-\s]+(\d{1,2})[,\s]+(\d{4})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})[-\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text)
                if match:
                    # Try to parse dates
                    info['date'] = match.group(0)
                    break

    except Exception as e:
        print(f"    Error extracting info: {e}")

    return info


def create_conference_entry(title, year, latest_entry, found_info):
    """Create a new conference entry."""
    # Generate ID
    conf_id = title.lower().replace(' ', '').replace('-', '').replace('&', '')
    conf_id = re.sub(r'[^a-z0-9]', '', conf_id) + str(year)

    entry = {
        'title': title,
        'year': year,
        'id': conf_id,
        'link': found_info.get('link', latest_entry.get('link', '#')),
        'deadline': found_info.get('deadline', 'TBA'),
        'timezone': found_info.get('timezone', latest_entry.get('timezone', 'UTC-12')),
        'place': found_info.get('place', 'TBA'),
        'date': found_info.get('date', f'TBA, {year}'),
        'sub': latest_entry.get('sub', 'ML'),
    }

    if found_info.get('abstract_deadline'):
        entry['abstract_deadline'] = found_info['abstract_deadline']

    if found_info.get('start'):
        entry['start'] = found_info['start']
    if found_info.get('end'):
        entry['end'] = found_info['end']

    if latest_entry.get('hindex'):
        entry['hindex'] = latest_entry['hindex']

    if latest_entry.get('full_name'):
        entry['full_name'] = latest_entry['full_name']

    return entry


def add_conference_to_file(title, new_entry, dry_run=False):
    """Add a conference entry to its YAML file."""
    yml_file = get_conference_file(title)

    if not yml_file.exists():
        print(f"  Creating new file: {yml_file.name}")
        if not dry_run:
            conferences = [new_entry]
            with open(yml_file, 'w', encoding='utf-8') as f:
                yaml.dump(conferences, f, default_flow_style=False,
                          sort_keys=False, allow_unicode=True)
            return True
        else:
            print(f"    [DRY RUN] Would create: {yml_file}")
            return True

    # Load existing entries
    try:
        with open(yml_file, 'r', encoding='utf-8') as f:
            conferences = yaml.safe_load(f) or []

        # Check if entry already exists
        for conf in conferences:
            if conf.get('year') == new_entry['year']:
                print(
                    f"  Entry for {title} {new_entry['year']} already exists!")
                return False

        # Add new entry at the beginning (most recent first)
        conferences.insert(0, new_entry)

        if not dry_run:
            with open(yml_file, 'w', encoding='utf-8') as f:
                yaml.dump(conferences, f, default_flow_style=False,
                          sort_keys=False, allow_unicode=True)
            print(f"  ✓ Added {title} {new_entry['year']} to {yml_file.name}")
        else:
            print(f"  [DRY RUN] Would add to {yml_file.name}:")
            print(f"    {yaml.dump([new_entry], default_flow_style=False)}")

        return True
    except Exception as e:
        print(f"  Error updating {yml_file}: {e}")
        return False


def find_missing_conferences(specific_conference=None):
    """Find conferences that should have entries but don't."""
    all_conferences = load_conference_data()

    # Group by title
    by_title = {}
    for conf in all_conferences:
        title = conf.get('title', '').split('[')[0].strip()
        if title not in by_title:
            by_title[title] = []
        by_title[title].append(conf)

    missing = []
    for title, entries in by_title.items():
        if specific_conference and title.lower() != specific_conference.lower():
            continue

        entries.sort(key=lambda x: x.get('year', 0), reverse=True)
        latest = entries[0]
        latest_year = latest.get('year', 0)

        # Check if we should have current or next year's entry
        if latest_year < CURRENT_YEAR:
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


def main():
    parser = argparse.ArgumentParser(
        description='Automatically find and add missing conference entries')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be added without making changes')
    parser.add_argument('--conference', type=str,
                        help='Process only a specific conference')
    args = parser.parse_args()

    print("Finding missing conference entries...")
    missing = find_missing_conferences(args.conference)

    if not missing:
        print("No missing conferences found!")
        return 0

    print(f"\nFound {len(missing)} conferences that might need entries:\n")

    added_count = 0
    for conf_info in missing:
        title = conf_info['title']
        year = conf_info['suggested_year']
        latest = conf_info['latest_entry']

        print(f"Processing: {title} {year}")
        print(
            f"  Latest entry: {latest.get('year')} ({latest.get('link', 'N/A')})")

        # Search for website
        print(f"  Searching for {year} website...")
        links = search_google(title, year)

        if not links:
            print("  ⚠ No website found. Skipping.")
            continue

        print(f"  Found {len(links)} potential links:")

        # Prioritize "important dates" pages
        important_dates_links = [
            link for link in links if 'important' in link.lower() and 'date' in link.lower()]
        other_links = [
            link for link in links if link not in important_dates_links]
        sorted_links = important_dates_links + other_links

        best_link = None
        best_info = {}

        for link in sorted_links[:3]:  # Check top 3 links
            print(f"    Checking: {link}")
            info = extract_conference_info(link, title, year)
            # Prioritize links with deadlines or important dates pages
            if info.get('deadline') or 'important' in link.lower():
                if not best_link or (info.get('deadline') and not best_info.get('deadline')):
                    best_link = link
                    best_info = info
            elif info.get('place') or 'call' in link.lower() or 'cfp' in link.lower():
                if not best_link:
                    best_link = link
                    best_info = info
            time.sleep(1)  # Be polite

        if best_link:
            best_info['link'] = best_link
            entry = create_conference_entry(title, year, latest, best_info)

            if add_conference_to_file(title, entry, args.dry_run):
                added_count += 1
            time.sleep(2)  # Be polite between conferences
        else:
            print("  ⚠ Could not extract sufficient information. Skipping.")

        print()

    print("=" * 60)
    if args.dry_run:
        print(f"[DRY RUN] Would add {added_count} conference entries.")
    else:
        print(f"✓ Added {added_count} conference entries.")
    print("\nNote: Please verify all information from official conference websites.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
