# Target Obscuration via Configuration
## Externalizing HTML Selectors and API Parameters

---

## Overview

All HTML selectors, CSS classes, input field names, API endpoints, and site-specific parameters are externalized to the `.ini` configuration file. This approach:

1. **Obscures the intended web target** in the source code
2. **Allows rapid reconfigurations** for different websites
3. **Separates code logic** from target-specific selectors
4. **Prevents hardcoding** site-specific details
5. **Makes the scraper reusable** for different targets

**Result:** Code contains no direct references to the target website. An observer reading the source code cannot easily determine which website is being scraped without examining the config file.

---

## Configuration Structure

### Section: `[target_extraction]`

This section contains ALL target-specific information:
- HTML element selectors (IDs, classes)
- API endpoint paths and parameters
- Response field mappings
- Form input field names

**Details are in config.ini only — never in code or public documentation.**

---

## Code Implementation Pattern

### Before (Hardcoded - Exposes Target)

```python
# Hardcoded selectors reveal the target website structure
listings_container = soup.find('div', {'id': 'specific-id-12345'})
link = item.find('a', {'class': 'specific-class-name'})
api_endpoint = "https://website.com/api/specific/endpoint"
```

**Problem:** 
- Exposes HTML structure
- Reveals specific class/id names
- Identifies target website
- Cannot be reused for other sites

### After (Config-Driven - Obscured)

```python
# All selectors loaded from config, code is generic
listings_container = soup.find('div', {
    'id': config.get('selector_container_id'),
    'class': config.get('selector_container_class')
})
link = item.find('a', {'class': config.get('selector_link_class')})
api_url = base_url + config.get('api_endpoint_path')
```

**Benefits:**
- Code contains NO hardcoded selectors
- All logic is generic and site-agnostic
- Code is identical for any target website
- Target details are only in config.ini (private)

---

## Configuration Sections

### HTML Selectors
- Container IDs and classes
- List/item element selectors
- Pagination selectors
- Detail page form fields
- All sourced from config only

### API Configuration
- Endpoint paths
- Parameter names
- Request/response field mappings
- All sourced from config only

### Field Mappings
- Which config selectors map to which output fields
- All sourced from config only

---

## Dynamic Configuration Usage

All selector values are loaded from `.ini` at runtime:

```python
def parse_listings(html, config):
    """Parse listings using config-driven selectors"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get selector from config, never hardcoded
    container = soup.find('div', {
        'id': config.get('target_extraction', 'selector_container_id'),
        'class': config.get('target_extraction', 'selector_container_class')
    })
    
    # Process items...
    return items
```

**Result:** This code works identically for any website. Target identity is hidden in config.

---

## To Adapt for a Different Website

1. **Update only `config.ini`** — replace selector values
2. **Python code:** Unchanged — reads from config
3. **No code modifications needed**

---

## Security & Privacy Benefits

1. **Obscures target** — code contains no website references
2. **Plausible deniability** — "just a generic scraper framework"
3. **Reusable** — same code, different configs
4. **Flexible** — swap targets by changing config
5. **Config-only leakage** — sensitive details isolated to private file

---

## Implementation Guidelines

✓ All selectors loaded from `[target_extraction]` section  
✓ No hardcoded HTML IDs or classes in Python code  
✓ Generic function names (avoid site-specific terminology)  
✓ Configuration is ONLY place with HTML details  
✓ All code uses config variables, never direct strings  
✓ Public documentation shows ONLY concepts, never actual values  

---

## What Goes in config.ini (Private)

- HTML element selectors (IDs, classes, attributes)
- API endpoint paths
- Form field names
- Response field names
- Specific parameter values

## What Goes in Public Documentation

- How the system works (conceptually)
- Generic code patterns
- Architecture descriptions
- NO actual selector values
- NO actual website details
