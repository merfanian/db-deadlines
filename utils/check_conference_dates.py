#!/usr/bin/env python3
"""
Check existing conferences for updated deadline information by accessing
their "Important Dates" pages directly.
"""

import yaml
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

CONFERENCES_DIR = Path(__file__).parent.parent / "_data" / "conferences"
CURRENT_YEAR = datetime.now().year


def find_important_dates_link(base_url):
    """Find Important Dates link from a conference website."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for links containing "important" and "date"
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                href = link.get('href', '')
                if ('important' in link_text and 'date' in link_text) or \
                   ('important' in href.lower() and 'date' in href.lower()):
                    if href.startswith('http'):
                        return href
                    else:
                        return urljoin(base_url, href)
    except Exception:
        pass
    return None


def extract_deadlines_from_page(url):
    """Extract deadline information from a page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            text_lower = text.lower()

            deadlines = {}

            # Look for "Important Dates" section
            important_section = None
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
                if 'important' in heading.get_text().lower() and 'date' in heading.get_text().lower():
                    # Get content after heading
                    section_text = heading.get_text()
                    current = heading.next_sibling
                    count = 0
                    while current and count < 15:
                        if hasattr(current, 'get_text'):
                            section_text += ' ' + current.get_text()
                        current = current.next_sibling
                        count += 1
                    important_section = section_text
                    break

            search_text = important_section.lower() if important_section else text_lower

            # Extract paper submission deadline
            # Handle both numeric and written date formats
            month_names = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12',
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }

            patterns = [
                # Written dates: "deadline: January 12th, 2025" or "deadline January 12, 2025"
                r'(?:paper\s+)?(?:submission\s+)?deadline[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
                r'submission[:\s]+deadline[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
                r'deadline[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
                # Numeric dates: "deadline: 01/12/2025"
                r'(?:paper\s+)?(?:submission\s+)?deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'submission[:\s]+deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, search_text, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) == 3:
                        month_str, day, year_part = groups
                        # Check if month is a name or number
                        if month_str.lower() in month_names:
                            month = month_names[month_str.lower()]
                        else:
                            month = month_str

                        if len(year_part) == 2:
                            year_part = '20' + year_part
                        try:
                            deadline_date = datetime(
                                int(year_part), int(month), int(day))
                            # Only include future dates
                            if deadline_date > datetime.now():
                                deadlines['deadline'] = f"{year_part}-{month.zfill(2)}-{day.zfill(2)} 23:59:59"
                                break
                        except (ValueError, TypeError):
                            pass
                if deadlines.get('deadline'):
                    break

            # Extract abstract deadline
            abstract_patterns = [
                # Written dates
                r'abstract[:\s]+(?:deadline|due|submission)[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
                r'abstract[:\s]+(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
                # Numeric dates
                r'abstract[:\s]+(?:deadline|due|submission)[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'abstract[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            ]

            for pattern in abstract_patterns:
                matches = re.finditer(pattern, search_text, re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) == 3:
                        month_str, day, year_part = groups
                        # Check if month is a name or number
                        if month_str.lower() in month_names:
                            month = month_names[month_str.lower()]
                        else:
                            month = month_str

                        if len(year_part) == 2:
                            year_part = '20' + year_part
                        try:
                            abstract_date = datetime(
                                int(year_part), int(month), int(day))
                            # Only include future dates
                            if abstract_date > datetime.now():
                                deadlines[
                                    'abstract_deadline'] = f"{year_part}-{month.zfill(2)}-{day.zfill(2)} 23:59:59"
                                break
                        except (ValueError, TypeError):
                            pass
                if deadlines.get('abstract_deadline'):
                    break

            return deadlines
    except Exception as e:
        return {'error': str(e)}

    return {}


def check_conference(conf_entry):
    """Check a single conference entry for updated information."""
    title = conf_entry.get('title', '')
    year = conf_entry.get('year', 0)
    link = conf_entry.get('link', '')
    current_deadline = conf_entry.get('deadline', 'TBA')

    if not link or link == '#' or year < CURRENT_YEAR - 1:
        return None

    # Try to find Important Dates page
    important_dates_url = find_important_dates_link(link)
    if not important_dates_url:
        # Try common patterns
        base_url = link.rstrip('/')
        common_paths = [
            '/important-dates',
            '/important_dates',
            '/dates',
            '/call-for-papers',
            '/cfp',
        ]
        for path in common_paths:
            test_url = base_url + path
            try:
                response = requests.get(
                    test_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                if response.status_code == 200 and 'important' in response.text.lower() and 'date' in response.text.lower():
                    important_dates_url = test_url
                    break
            except:
                continue

    if important_dates_url:
        deadlines = extract_deadlines_from_page(important_dates_url)
        if deadlines and not deadlines.get('error'):
            return {
                'title': title,
                'year': year,
                'link': link,
                'important_dates_url': important_dates_url,
                'current_deadline': current_deadline,
                'found_deadlines': deadlines
            }

    return None


def main():
    """Check all conferences for updated deadline information."""
    print("Checking conferences for updated deadline information...")
    print("=" * 70)

    all_conferences = []
    for yml_file in sorted(CONFERENCES_DIR.glob("*.yml")):
        try:
            with open(yml_file, 'r', encoding='utf-8') as f:
                conferences = yaml.safe_load(f) or []
                if conferences:
                    for conf in conferences:
                        conf['_source_file'] = yml_file.name
                        all_conferences.append(conf)
        except Exception as e:
            print(f"Error loading {yml_file}: {e}")

    # Filter to recent conferences (current year or next year)
    recent_confs = [c for c in all_conferences
                    if c.get('year', 0) >= CURRENT_YEAR - 1 and c.get('year', 0) <= CURRENT_YEAR + 1]

    print(f"\nChecking {len(recent_confs)} recent conferences...\n")

    updated = []
    for conf in recent_confs:
        result = check_conference(conf)
        if result:
            updated.append(result)
            print(f"\n✓ {result['title']} {result['year']}")
            print(f"  Current deadline: {result['current_deadline']}")
            if result['found_deadlines'].get('deadline'):
                print(
                    f"  Found deadline: {result['found_deadlines']['deadline']}")
            if result['found_deadlines'].get('abstract_deadline'):
                print(
                    f"  Found abstract deadline: {result['found_deadlines']['abstract_deadline']}")
            print(f"  Source: {result['important_dates_url']}")

    print("\n" + "=" * 70)
    print(f"Found updated information for {len(updated)} conferences.")
    print("\nNote: Please verify all information before updating YAML files.")


if __name__ == "__main__":
    main()
