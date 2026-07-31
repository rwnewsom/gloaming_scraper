# Development Mode
## Testing Configuration for Web Scraper

---

## Overview

Development mode (`dev_mode`) allows testing the scraper on a limited dataset without running a full production scrape.

**Benefits:**
- Test all scraping logic without long execution times
- Verify configuration works correctly
- Debug issues with small dataset
- Validate TOR integration quickly
- Test error handling without rate limiting concerns

---

## Configuration

### .ini Setting

```ini
[development]
dev_mode = false
dev_mode_max_pages = 2
```

**Parameters:**
- `dev_mode` — Enable/disable development mode (default: `false`)
- `dev_mode_max_pages` — Maximum pages to scan in dev mode (default: `2`)

### Usage

**Production (Full Scrape):**
```ini
[development]
dev_mode = false
```
Script will run until all pages are exhausted.

**Development (Limited Testing):**
```ini
[development]
dev_mode = true
dev_mode_max_pages = 2
```
Script will stop after scanning 2 pages maximum.

---

## Behavior

### When `dev_mode = false` (Production)
- Script runs normally
- Scans all available pages
- Processes all listings found
- No page limit enforced

### When `dev_mode = true` (Development)
- Script logs "DEV MODE ACTIVE" at startup
- Scans up to `dev_mode_max_pages` pages (default: 2)
- Stops pagination loop after limit reached
- Logs "Dev mode limit reached. Stopping after page 2"
- Proceeds to Phase 2 with only listings from first 2 pages
- Generates CSV with limited dataset
- Summary report clearly indicates dev mode was active

---

## Implementation Flow

### Phase 1: Pagination Loop with Dev Mode

```
Initialize page_counter = 0
Initialize dev_mode_max_pages = 2

For each page:
    ├─ Make API POST request
    ├─ Parse response (listings + pagination)
    ├─ Extract listings
    ├─ Increment page_counter
    │
    ├─ Check: if dev_mode AND page_counter >= dev_mode_max_pages
    │   ├─ Yes: Log "Dev mode limit reached"
    │   │        Break pagination loop
    │   └─ No: Continue to next page
    │
    └─ Check pagination for next page
        ├─ If next exists: loop continues
        └─ If last page: loop exits
```

### Counter Placement

- `page_counter` increments **after** parsing each page
- Check happens **before** attempting next page
- If limit reached on page 2, that page's data is included
- No attempt to fetch page 3

---

## Examples

### Example 1: Dev Mode Enabled (Columbus Listings)

**Config:**
```ini
[development]
dev_mode = true
dev_mode_max_pages = 2
```

**Execution:**
```
[INFO] Configuration loaded: dev_mode = true
[INFO] DEV MODE ACTIVE: Max 2 pages will be scanned
[INFO] Connecting to TOR...
[INFO] TOR connected. Exit IP: 203.0.113.45
[API] Page 1: 10 listings found
[API] Page 2: 10 listings found
[DEV] Dev mode limit reached. Stopping after page 2
[INFO] Phase 1 complete: 20 listings found (limited by dev mode)
[INFO] Phase 2: Processing 20 listings...
[INFO] Phase 2 complete: 20 posts enriched with user data
[EXPORT] Generated scrape_results.csv (20 rows)

Summary:
========
DEV MODE - Limited to 2 pages
Total posts found: 20
Pages scanned: 2 (dev mode max)
Complete data: 18
Partial data: 2
Execution time: 45 seconds
```

### Example 2: Production Mode (Full Scrape)

**Config:**
```ini
[development]
dev_mode = false
```

**Execution:**
```
[INFO] Configuration loaded: dev_mode = false
[INFO] Production mode: No page limit
[INFO] Connecting to TOR...
[INFO] TOR connected. Exit IP: 203.0.113.45
[API] Page 1: 10 listings found
[API] Page 2: 10 listings found
[API] Page 3: 10 listings found
...
[API] Page 47: 5 listings found (last page)
[INFO] Phase 1 complete: 465 listings found (all pages)
[INFO] Phase 2: Processing 465 listings...
[INFO] Phase 2 complete: 465 posts enriched with user data
[EXPORT] Generated scrape_results.csv (465 rows)

Summary:
========
Total posts found: 465
Pages scanned: 47 (all available)
Complete data: 450
Partial data: 15
Execution time: 3245 seconds
```

---

## Logging

### Dev Mode Indicators

**Startup:**
```
[INFO] Configuration loaded: config.ini
[INFO] Dev mode: ENABLED
[INFO] Dev mode max pages: 2
[INFO] DEV MODE ACTIVE: Max 2 pages will be scanned
```

**During Scraping:**
```
[API] Page 1: 10 listings found
[API] Page 2: 10 listings found
[DEV] Dev mode limit reached. Stopping after page 2
```

**In Summary Report:**
```
DEV MODE - Limited to 2 pages
Total posts found: 20
Pages scanned: 2 (dev mode max)
```

---

## Use Cases

### Use Case 1: Initial Testing
- Enable dev mode with max 2 pages
- Test full pipeline works end-to-end
- Verify TOR connection
- Check CSV generation
- Validate configuration

### Use Case 2: Debugging
- Enable dev mode
- Test specific error handling with small dataset
- Debug parsing issues with manageable output
- Verify retry logic works

### Use Case 3: Configuration Validation
- Enable dev mode
- Test new TOR settings
- Verify proxy routing
- Confirm email validation rules
- Test malformed URL handling

### Use Case 4: Performance Testing
- Run with dev mode to get baseline timing
- Compare execution time: 2 pages vs full scrape
- Estimate total execution time for production
- Plan scheduling and resource allocation

---

## Best Practices

1. **Always test with dev mode first**
   - Before running production scrape
   - After any configuration changes
   - After code modifications

2. **Keep dev mode disabled in production**
   - Set `dev_mode = false` before deployment
   - Use separate config files (dev.ini vs prod.ini) if needed

3. **Log dev mode status clearly**
   - Easy to see in output if dev mode is active
   - Prevents accidental partial scrapes

4. **Use consistent max_pages value**
   - Default 2 pages for quick testing
   - Change to 5-10 pages for more thorough testing if needed

---

## Configuration Examples

**Development .ini:**
```ini
[urls]
initial_url = https://www.foobarbaz.com/Path-to-test
base_url = https://www.foobarbaz.com

[scraping]
batch_size = 5
request_delay = 1.0
malformed_url_threshold = 10

[retry]
max_retries = 3
max_delay = 60

[tor]
use_tor = true
tor_host = 127.0.0.1
tor_port = 9050

[development]
dev_mode = true
dev_mode_max_pages = 2
```


## Notes

- Dev mode is a **configuration setting**, not a code branch
- Can toggle on/off without changing Python code
- Page counter is **incremental** (0, 1, 2, ...)
- Limit check happens **after** parsing each page
- All other scraping logic runs identically in both modes
- Error handling is identical in both modes
- TOR connection works the same in both modes
