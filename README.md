# Gloaming Scraper
> Gloaming, twilight; from gloom to darken; a word common in Scotland and the North of England, as well as in America.
>> 'Lost Beauties of the English Language', Charles Mackay
> 
> “The French called this time of day 'l'heure bleue.' To the English it was 'the gloaming.' The very word 'gloaming' 
> reverberates, echoes - the gloaming, the glimmer, the glitter, the glisten, the glamour - carrying in its consonants 
> the images of houses shuttering, gardens darkening, grass-lined rivers slipping through the shadows. During the blue 
> nights you think the end of the day will never come. As the blue nights draw to a close (and they will, and they do) 
> you experience an actual chill, an apprehension of illness, at the moment you first notice; the blue light is going, 
> the days are already shortening, the summer is gone... Blue nights are the opposite of the dying of the brightness, 
> but they are also its warning.” 
> > ― 'Blue Nights', Joan Didion

## Overview

A web scraper for extracting data items using direct API calls via TOR for anonymization. This project 
demonstrates advanced scraping techniques including target obscuration, configuration-driven selectors, and 
privacy-focused implementation.

### Sample log output

(Yes, this is slow! Could be sped up in many ways, and the url/email validation isn't strictly necessary)

```2026-08-01 14:58:08,802 - __main__ - INFO - 
[PHASE 0] Setup & Configuration
2026-08-01 14:58:08,802 - __main__ - INFO - ------------------------------------------------------------
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - Dev mode: ENABLED
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - Dev mode max pages: 2
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - TOR: ENABLED
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - TOR proxy: 127.0.0.1:9050
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - TOR identity rotation: DISABLED
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - Batch size: 5
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - Request delay: 2.0s
2026-08-01 14:58:08,802 - redacted.config_manager - INFO - Loaded 40 target selectors from config
2026-08-01 14:58:08,802 - __main__ - INFO - TOR connection initialized
2026-08-01 14:58:08,802 - api_client - DEBUG - GET https://www.foobarbaz.com/robots.txt (attempt 1/6)
2026-08-01 14:58:10,354 - urllib3.connectionpool - DEBUG - https://www.foobarbaz.com:443 "GET /robots.txt HTTP/1.1" 200 24
2026-08-01 14:58:10,355 - __main__ - INFO - 
============================================================
2026-08-01 14:58:10,355 - __main__ - INFO - ROBOTS.TXT COMPLIANCE
2026-08-01 14:58:10,355 - __main__ - INFO - ============================================================
2026-08-01 14:58:10,355 - __main__ - INFO - User-agent: *
2026-08-01 14:58:10,355 - __main__ - INFO - Disallow:
2026-08-01 14:58:10,355 - __main__ - INFO - ============================================================
2026-08-01 14:58:10,356 - __main__ - INFO - Phase 0 complete: All components initialized
2026-08-01 14:58:10,356 - __main__ - INFO - ============================================================
2026-08-01 14:58:10,356 - __main__ - INFO - Web Scraper Started
2026-08-01 14:58:10,356 - __main__ - INFO - ============================================================
2026-08-01 14:58:10,356 - __main__ - INFO - 
[PHASE 1] List Scraping
2026-08-01 14:58:10,356 - __main__ - INFO - ------------------------------------------------------------
2026-08-01 14:58:10,356 - <SNIP/>
2026-08-01 14:58:12,982 - item_parser - DEBUG - No ul container found, parsing <li> elements directly
2026-08-01 14:58:12,985 - item_parser - INFO - Parsed 10 items
2026-08-01 14:58:12,985 - __main__ - INFO - Page 0: 10 items found
2026-08-01 14:58:12,986 - item_parser - DEBUG - Extracted next page number: 2
795 - __main__ - INFO - Dev mode limit reached. Stopping after page 2
2026-08-01 14:58:18,796 - __main__ - INFO - Phase 1 complete: 20 total items found
2026-08-01 14:58:18,796 - __main__ - INFO - 
[PHASE 2] Detail Scraping
2026-08-01 14:58:18,796 - __main__ - INFO - ------------------------------------------------------------
<SNIP/>
------------------------------------------------------------
2026-08-01 14:59:41,719 - csv_exporter - INFO - Exported 20 posts to output/scrape_results_FOO_8620_20260801.csv
2026-08-01 14:59:41,719 - __main__ - INFO - Phase 3 complete: All data exported
2026-08-01 14:59:41,719 - __main__ - INFO - 
============================================================
2026-08-01 14:59:41,719 - __main__ - INFO - SCRAPING SUMMARY
2026-08-01 14:59:41,719 - __main__ - INFO - ============================================================
2026-08-01 14:59:41,719 - __main__ - INFO - DEV MODE - Limited to 2 pages
2026-08-01 14:59:41,719 - __main__ - INFO - Total posts found: 20
2026-08-01 14:59:41,719 - __main__ - INFO - Posts with complete data: 20
2026-08-01 14:59:41,719 - __main__ - INFO - Posts with partial data: 0
2026-08-01 14:59:41,719 - __main__ - INFO - Malformed URLs: 0
2026-08-01 14:59:41,719 - __main__ - INFO - Malformed emails: 0
2026-08-01 14:59:41,719 - __main__ - INFO - Execution time: 103.0s
2026-08-01 14:59:41,719 - __main__ - INFO - ============================================================
```

### Why I made this project (with much appreciation to Claude Code)

I created this project to exercise advanced scripting skills and demonstrate best practices in secure, privacy-focused 
web automation. Key lessons I learned include:
- Reinforcing the importance of implementing Authentication and Authorization
- Have a robot.txt file
- Email obfuscation patterns can be detected and accounted for in scraping
- Check html for UGI/UII - hidden data is still accessible via scraping
- Privacy protection via anonymization layers (TOR)
---

## Project Structure

### Documentation Files

| File | Purpose |
|------|---------|
| **[TOR_INTEGRATION.md](TOR_INTEGRATION.md)** | TOR proxy integration design, configuration, and error handling strategy |
| **[DEV_MODE.md](DEV_MODE.md)** | Development mode feature for limited testing (max 2 pages) |
| **[TARGET_OBSCURATION.md](TARGET_OBSCURATION.md)** | Configuration-driven selector system to obscure intended web target |

### Code Files (Active Implementation)

| File | Purpose |
|------|---------|
| **gloaming_scraper.py** | Main orchestrator executing all phases (0-3) |
| **config_manager.py** | Configuration loading, validation, and access |
| **tor_manager.py** | TOR SOCKS5 proxy connection and management |
| **api_client.py** | HTTP requests through TOR with exponential backoff |
| **item_parser.py** | Phase 1: Pagination and item list extraction |
| **detail_parser.py** | Phase 2: Individual item page scraping and enrichment |
| **csv_exporter.py** | Phase 3: CSV export with config-driven field names |
| **validators.py** | URL and email validation with malformed tracking |
| **config.ini** | Complete configuration (all target details externalized) |

### Archived Reference Files

Reference-only files are located in `gloam_scraper_archive/`:
- web_scraper.py, web_scraper_pagination.py, web_scraper_pseudocode.txt
- plan.md, INSPECTION_REPORT.md

---

## Key Features

✅ **Direct API Calls** — Bypasses JavaScript rendering, uses AJAX endpoints directly  
✅ **TOR Integration** — All requests routed through TOR SOCKS5 proxy for anonymization  
✅ **Target Obscuration** — All HTML selectors externalized to `.ini` config file  
✅ **Batch Processing** — Configurable batch sizes with exponential backoff  
✅ **Pagination Traversal** — Automatic multi-page scraping via API  
✅ **Two-Phase Scraping** — List phase + detail phase for data enrichment  
✅ **Error Handling** — TOR-aware retry logic with detailed logging  
✅ **Dev Mode** — Limited testing mode for quick validation (max 2 pages)  
✅ **CSV Export** — Generates clean CSV with all extracted data  

---

## Quick Start

### Prerequisites

- Python 3.8+
- TOR daemon running on localhost:9050 (SOCKS5)
- Required packages: `requests[socks]`, `beautifulsoup4`, `pymongo` (or `bson`)

### Installation

```bash
pip install -r requirements.txt
```

### Running the Scraper

```bash
python gloaming_scraper.py
```

### Configuration

All settings are in `config.ini` with sections:
- `[urls]` — **initial_url** (city page) and base URL — cityid is extracted dynamically from initial URL
- `[scraping]` — Batch size, delays, thresholds
- `[retry]` — Exponential backoff parameters
- `[tor]` — TOR proxy settings
- `[development]` — Dev mode toggle
- `[target_extraction]` — HTML selectors and API config (obscures target)
- `[output_fields]` — CSV field name mappings
- `[detail_parser_fields]` — Detail page field names

**Key:** Change the `initial_url` to any city and the scraper automatically extracts the correct cityid from the hidden form field. No manual configuration needed.

For detailed configuration explanation, see **[TARGET_OBSCURATION.md](TARGET_OBSCURATION.md)**

---

## Architecture

### Phases

**Phase 0: Setup & Configuration**
- Load and validate `.ini` config
- Initialize TOR connection
- Extract cityid dynamically from initial URL
- Set up logging

**Phase 1: Data Extraction**
- Make API POST requests via TOR
- Parse JSON responses
- Extract items from HTML
- Handle pagination until complete
- (Respects dev mode limit if enabled)

**Phase 2: Detail Scraping**
- Fetch individual item pages via TOR
- Extract hidden form input values
- Enrich records with supplemental data

**Phase 3: Export**
- Generate CSV from collected data
- Create summary report
- Finalize logging

### Key Classes

- `ConfigManager` — Config loading and validation with nested section access
- `TORManager` — TOR SOCKS5 proxy connection and management
- `APIClient` — AJAX API requests via TOR with exponential backoff retry
- `ItemParser` / `PaginationExtractor` — Phase 1 pagination extraction and item parsing
- `DetailParser` — Phase 2 individual item page scraping and enrichment
- `CSVExporter` — Phase 3 CSV export with config-driven field names
- `URLValidator` / `EmailValidator` — Data validation with malformed tracking

---

## Configuration System

### Target Obscuration

All target-specific details are externalized to `config.ini`, preventing hardcoded selectors in Python code.

**[output_fields]** — CSV column names and database field mappings
- Defines which data fields are exported to CSV
- All field names configured externally

**[detail_parser_fields]** — Form input field names for detail scraping
- Maps which form fields to extract from detail pages
- All field mappings configured externally

**[target_extraction]** — HTML selectors and API configuration
- HTML element selectors (ids, classes)
- API endpoint path and parameters
- Response field mappings
- All configured externally, never hardcoded

**Key Benefit:** Python source code contains minimal target references. All selectors and URLs are external (in config.ini only).

Example:
```python
# Generic code (no target details revealed):
items_ul = soup.find('ul', {
    'id': config.get('target_extraction', 'selector_items_ul_id'),
    'class': config.get('target_extraction', 'selector_items_ul_class')
})
```

All logic is config-driven and target-agnostic.

---

## Development Mode

Enable in `.ini`:
```ini
[development]
dev_mode = true
dev_mode_max_pages = 2
```

**Effect:** Script stops after scanning 2 pages maximum (default). Useful for:
- Testing full pipeline
- Validating configuration
- Quick debugging
- Performance baseline

---

## TOR Integration

### Setup

1. Install TOR: `brew install tor` (or `apt-get install tor`)
2. Start TOR: `tor`
3. Verify SOCKS5 on 127.0.0.1:9050

### Configuration

```ini
[tor]
use_tor = true
tor_host = 127.0.0.1
tor_port = 9050
rotate_tor_identity = false
rotate_identity_interval = 10
```

### All Requests Route Through TOR
- API calls to data endpoint
- Fetch requests for detail pages
- All traffic anonymized

---

## Error Handling

- **Network Errors:** Exponential backoff with jitter
- **TOR Errors:** Reconnect logic, circuit rotation support
- **Parsing Errors:** Logged with context, continues to next item
- **Validation Failures:** Logged to separate files, configurable thresholds trigger stop
- **Dev Mode:** Logs clearly when limit reached

---

## Logging

All activity logged to dynamically-named file: `scraper_{city_name}_{cityid}_{date}.log`
- Startup info (config, dev mode, TOR status, extracted cityid)
- Scraping progress (page numbers, items found)
- API requests and responses
- Error events and retries with backoff delays
- TOR connection status and IP changes
- Summary statistics

---

## Output

All output files are organized in an `output/` directory:

```
output/
├── scrape_results_{city_name}_{cityid}_{date}.csv  — Extracted data
├── scraper_{city_name}_{cityid}_{date}.log         — Activity log
├── malformed_urls.txt                              — Invalid URLs
└── malformed_contact.txt                           — Invalid contact data
```

**Files:**
- **scrape_results_*.csv** — Extracted data with fields
- **scraper_*.log** — Complete activity log (DEBUG to file, INFO to console)
- **malformed_urls.txt** — URLs that failed validation (stops at configured threshold)
- **malformed_contact.txt** — Contact data that failed validation (stops at configured threshold)

---

## Status

**Phase:** Implementation Complete  
**Status:** All phases (0-3) implemented and tested

✅ Configuration system with target obscuration  
✅ TOR proxy integration with exponential backoff  
✅ Phase 1: Pagination and item extraction via API  
✅ Phase 2: Detail enrichment via individual page scraping  
✅ Phase 3: CSV export with validation  
✅ Development mode for testing  
✅ Comprehensive error handling and logging

---

## Multi-City / Multi-Region Usage

The scraper is designed for reusability across different search parameters without code changes:

**To scrape a different region:**
1. Update `initial_url` in `config.ini` to a different search page:
   ```ini
   [urls]
   initial_url = <search-page-url>
   base_url = <base-url>
   ```
2. Run the scraper — it automatically extracts the correct parameters from the page
3. The output CSV will contain results for that region

**Batch processing multiple searches:**
```bash
for search_url in "$URL1" "$URL2" "$URL3"; do
  sed -i "s|initial_url = .*|initial_url = $search_url|" config.ini
  python gloaming_scraper.py
  mv scrape_results.csv scrape_results_$(date +%s).csv
done
```

No hardcoded parameter values needed — the scraper dynamically extracts all required parameters from the initial page's form fields.

---

## Design Notes

- Direct API calls bypass JavaScript rendering layer
- Dynamic cityid extraction from initial URL enables multi-city reusability
- Data extraction via two-phase approach: list extraction → detail enrichment
- All configuration externalized to prevent target leakage in source code
- Exponential backoff retry strategy handles transient network failures
- TOR anonymization for all outbound requests
- Validation with configurable thresholds for data quality

---

## Related Documents

- [TOR_INTEGRATION.md](TOR_INTEGRATION.md) — Proxy setup and integration guide
- [DEV_MODE.md](DEV_MODE.md) — Testing mode documentation
- [TARGET_OBSCURATION.md](TARGET_OBSCURATION.md) — Configuration and target obscuration strategy

**Archived (in gloam_scraper_archive/):**
- plan.md — Full technical plan with all phases
- INSPECTION_REPORT.md — Website analysis findings
