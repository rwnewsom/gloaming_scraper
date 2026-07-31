# TOR Integration Design
## Web Scraper with TOR Anonymization

---

## Overview

All HTTP requests (both API calls and detail page fetches) will be routed through TOR (The Onion Router) using SOCKS5 proxy.

**Benefits:**
- Anonymized IP address
- Reduced detection risk from target website
- Ability to rotate identity between requests (optional)

---

## Architecture

### TOR Setup Requirements

**TOR Daemon:**
- Must be running on localhost (`127.0.0.1`)
- SOCKS5 proxy port: `9050` (standard)
- Control port: `9051` (optional, for identity rotation)

**Installation (macOS/Linux):**
```bash
brew install tor
# or
apt-get install tor

# Start TOR
tor
```

### Configuration (.ini)

```ini
[tor]
use_tor = true
tor_host = 127.0.0.1
tor_port = 9050
tor_socks_version = 5
tor_control_port = 9051
tor_control_password = 
rotate_tor_identity = false
rotate_identity_interval = 10
```

**Parameters:**
- `use_tor` — Enable/disable TOR routing
- `tor_host` / `tor_port` — SOCKS5 proxy address
- `tor_socks_version` — SOCKS version (5 recommended)
- `tor_control_port` — Control port for identity rotation (optional)
- `tor_control_password` — Password for control port (often blank locally)
- `rotate_tor_identity` — Rotate TOR circuit every N requests
- `rotate_identity_interval` — Number of requests before rotation

---

## Implementation Strategy

### TORManager Class

**Responsibilities:**
1. Verify TOR daemon is accessible at startup
2. Initialize SOCKS5 session proxy
3. Optional: rotate TOR identity periodically
4. Log connection status and IP changes

**Key Methods:**
```python
class TORManager:
    def __init__(self, config):
        # Initialize TOR connection
        # Verify SOCKS5 proxy is accessible
        # Test connection with probe request
        
    def get_session(self):
        # Return requests.Session() configured with TOR proxy
        
    def rotate_identity(self):
        # Send SOCKS SIGNAL via control port
        # Wait for circuit to reset (~2-3 seconds)
        # Log new IP address
        
    def verify_connection(self):
        # Make test request through TOR
        # Verify IP address is not local
```

### APIClient Integration

**Proxy Configuration:**
```python
# In APIClient.__init__()
proxies = {
    'http': f'socks5://{tor_host}:{tor_port}',
    'https': f'socks5://{tor_host}:{tor_port}'
}
self.session.proxies.update(proxies)
```

**All requests automatically route through TOR:**
- API calls to configured endpoints
- Detail page fetches for data extraction

### Identity Rotation (Optional)

If `rotate_tor_identity = true`:
- After every N requests (configurable), request new circuit
- TOR assigns new exit node and IP
- Useful for avoiding rate limiting or detection
- **Cost:** ~2-3 seconds per rotation

---

## Error Handling

### TOR-Specific Errors

**Startup Errors:**
- TOR daemon not running → **Stop with clear error message**
- SOCKS5 port unreachable → **Stop with clear error message**
- Test request fails → **Stop with diagnostics**

**Runtime Errors:**
- Connection timeout through TOR → retry with exponential backoff
- TOR circuit error mid-request → rotate identity (if enabled) and retry
- SOCKS protocol error → log and retry

**Fallback Strategy:**
- If TOR fails repeatedly (10+ retries): stop gracefully
- Never fallback to non-TOR requests (would defeat purpose)

### Logging

**Log TOR Status:**
```
[TOR] Connected to 127.0.0.1:9050 (SOCKS5h)
[TOR] Exit IP: 203.0.113.45
[TOR] Identity rotated after 10 requests
[API] POST to configured endpoint via TOR
[Error] TOR SOCKS error: connection refused (retry 1/5)
```

---

## Request Flow with TOR

```
1. Initialize TORManager
   ↓
2. Verify TOR connection (test request)
   ↓
3. Get current exit IP (log for verification)
   ↓
4. For each page:
   ├─ Make POST through TOR SOCKS5 proxy
   ├─ Parse response
   ├─ [Optional] Rotate identity after N requests
   └─ Log all activity with TOR status
   ↓
5. For each detail page:
   ├─ Make GET through TOR SOCKS5 proxy
   ├─ Extract data
   └─ Log with TOR status
   ↓
6. Generate report including TOR anonymization confirmation
```

---

## Dependencies

**Python Libraries:**
```bash
pip install requests[socks]
# or
pip install requests PySocks

# Optional (for identity rotation):
pip install stem
```

**External:**
- TOR daemon (Homebrew, apt, or Docker)

---

## Configuration Example

**Full .ini with TOR:**
```ini
[urls]
initial_url = <search-page-url>
base_url = <base-url>

[scraping]
batch_size = 5
request_delay = 2.0
malformed_url_threshold = 10

[phase_2]
listing_delay = 5.0

[retry]
max_retries = 5
max_delay = 180

[tor]
use_tor = true
tor_host = 127.0.0.1
tor_port = 9050
tor_socks_version = 5
tor_control_port = 9051
tor_control_password = 
rotate_tor_identity = false
rotate_identity_interval = 10

[validation]
malformed_email_threshold = 5
```

---

## Pre-Implementation Checklist

- [ ] TOR daemon installed locally
- [ ] TOR daemon can be started and runs stably
- [ ] SOCKS5 proxy accessible at 127.0.0.1:9050
- [ ] Python dependencies (requests[socks]) available
- [ ] Test SOCKS5 connection with curl or Python probe
- [ ] Decide on identity rotation strategy (yes/no, interval)
- [ ] Finalize .ini configuration with TOR settings
- [ ] Plan for logging and verification (check exit IP regularly)

---

## Testing Strategy

**Before Full Scrape:**
1. Test TOR connection at startup
2. Verify exit IP is not local
3. Make 1-2 test API calls through TOR
4. Confirm responses are received correctly
5. Log all connection details
6. Run on small batch (5 pages) with identity rotation enabled to verify

---

## Performance Notes

- **Startup:** ~2-3 seconds to verify TOR connection
- **Per Request:** No significant overhead (TOR routing is transparent)
- **Identity Rotation:** ~2-3 seconds per rotation (if enabled)
- **Recommendation:** Rotate identity every 10-20 requests (balance anonymity vs speed)

---

## Notes

- All requests MUST go through TOR (no exceptions)
- Never disable TOR once enabled (defeats anonymization purpose)
- Log exit IP periodically to verify anonymization is working
- Be respectful of website and server resources (use proper delays)
