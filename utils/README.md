# Conference Data Utilities

This directory contains utilities for managing conference data.

## auto_add_conferences.py

Automatically finds and adds missing conference entries by searching Google for conference websites and extracting call-for-paper information.

### Features

- Automatically detects conferences that should have current/next year entries but don't
- Searches Google for conference websites
- Extracts deadline, location, and date information from websites
- Adds entries to the appropriate YAML files in `_data/conferences/`

### Usage

```bash
# Dry run (see what would be added without making changes)
python utils/auto_add_conferences.py --dry-run

# Actually add missing conferences
python utils/auto_add_conferences.py

# Process only a specific conference
python utils/auto_add_conferences.py --conference "IWSDS"
```

### Requirements

```bash
pip install pyyaml beautifulsoup4 requests
```

### How It Works

1. **Detection**: Scans all conference YAML files to find conferences where the latest entry is from a past year
2. **Search**: Uses Google search to find the conference website for the current/next year
3. **Extraction**: Parses the website to extract:
   - Submission deadline
   - Abstract deadline (if available)
   - Conference location
   - Conference dates
   - Timezone
4. **Creation**: Creates a new entry following the existing YAML format
5. **Addition**: Adds the entry to the appropriate YAML file (creates new file if needed)

### Notes

- The script is polite to servers (adds delays between requests)
- Always verify extracted information from official conference websites
- Some conferences may require manual review if the website structure is unusual
- The script preserves existing entries and adds new ones at the beginning

## find_missing_conferences.py

A simpler utility that just identifies missing conferences without automatically adding them. Useful for manual review.

### Usage

```bash
python utils/find_missing_conferences.py
```

This will list conferences that might need entries and suggest potential websites, but won't modify any files.

## Integration with Prediction Feature

The "Potential Call for Papers" feature in the main website will automatically show predicted deadlines for conferences that don't have entries yet. Predictions skip year N+1 until year N has a confirmed (non-predicted, non-TBA) entry.

You can use these utilities to:

1. Run `find_missing_conferences.py` to see what's missing
2. Run `auto_add_conferences.py --dry-run` to preview what would be added
3. Run `auto_add_conferences.py` to automatically add verified entries
4. Manually review and edit any entries that need correction

## Example Workflow

```bash
# 1. Check what's missing
python utils/find_missing_conferences.py

# 2. Preview what would be added
python utils/auto_add_conferences.py --dry-run

# 3. Add the entries
python utils/auto_add_conferences.py

# 4. Review the changes
git diff _data/conferences/

# 5. Test the site
bundle exec jekyll serve
```

