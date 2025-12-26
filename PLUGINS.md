# OSINT Framework - Plugin Directory

## Overview

The OSINT Framework currently includes **7 specialized plugins** covering 6 different search types. Each plugin is designed to work independently and can be used individually or combined for comprehensive OSINT investigations.

## Plugin Summary Table

| # | Plugin Name | Search Types | Status | Requires API Key | System Dependencies |
|---|------------|--------------|--------|------------------|---------------------|
| 1 | Sherlock | USERNAME | ⚠️ Partial | No | sherlock CLI |
| 2 | WHOIS | DOMAIN, IP | ✅ Working | No | whois |
| 3 | DNS Lookup | DOMAIN | ✅ Working | No | dig/dnsutils |
| 4 | Have I Been Pwned | EMAIL | ⚠️ Limited | Optional | None |
| 5 | Email Validator | EMAIL | ✅ Working | No | dig/nslookup |
| 6 | IP Geolocation | IP | ✅ Working | No | None |
| 7 | Phone Number Lookup | PHONE | ✅ Working | No | None |

## Search Type Coverage

- **USERNAME**: 1 plugin (Sherlock)
- **EMAIL**: 2 plugins (Have I Been Pwned, Email Validator)
- **DOMAIN**: 2 plugins (WHOIS, DNS Lookup)
- **IP**: 2 plugins (WHOIS, IP Geolocation)
- **PHONE**: 1 plugin (Phone Number Lookup)
- **URL**: 0 plugins (future expansion)

## Detailed Plugin Information

### 1. Sherlock Plugin

**Status**: ⚠️ Partially Working (requires sherlock CLI tool)

**Purpose**: Username enumeration across social media platforms

**Search Types**: USERNAME

**How it Works**:
- Executes the Sherlock command-line tool
- Searches 300+ social media sites and platforms
- Returns list of found profiles with URLs
- Uses JSON output for structured data

**Installation**:
```bash
pip install sherlock-project
```

**Example Usage**:
```python
# Search for username "john_doe"
result = engine.run_single_plugin("Sherlock", "john_doe", SearchType.USERNAME)
```

**Output Data**:
- `username`: Queried username
- `profiles_found`: Number of matches
- `profiles`: List of profile objects with site and URL
- `total_sites_checked`: Total sites queried

**Limitations**:
- Requires external CLI tool
- Subject to rate limiting on some sites
- Some sites may have changed, causing false positives

---

### 2. WHOIS Plugin

**Status**: ✅ Fully Working

**Purpose**: Domain registration and IP ownership information

**Search Types**: DOMAIN, IP

**How it Works**:
- Uses system `whois` command
- Parses WHOIS output for structured data
- Extracts registrar, dates, nameservers, status

**Installation**:
```bash
sudo apt-get install whois
```

**Example Usage**:
```python
# Domain lookup
result = engine.run_single_plugin("WHOIS", "example.com", SearchType.DOMAIN)

# IP lookup
result = engine.run_single_plugin("WHOIS", "8.8.8.8", SearchType.IP)
```

**Output Data**:
- `raw_output`: Full WHOIS text
- `domain_name`: Registered domain
- `registrar`: Domain registrar
- `creation_date`: Domain registration date
- `expiration_date`: Domain expiration date
- `name_servers`: List of authoritative nameservers
- `status`: Domain status codes

**Use Cases**:
- Domain ownership investigation
- Expiration date checking
- Registrar identification
- Nameserver enumeration

---

### 3. DNS Lookup Plugin

**Status**: ✅ Fully Working

**Purpose**: DNS record enumeration and discovery

**Search Types**: DOMAIN

**How it Works**:
- Uses `dig` command (or `nslookup` as fallback)
- Queries multiple DNS record types
- Returns structured DNS data

**Installation**:
```bash
sudo apt-get install dnsutils
```

**Example Usage**:
```python
# DNS enumeration
result = engine.run_single_plugin("DNS Lookup", "example.com", SearchType.DOMAIN)
```

**Output Data**:
- `domain`: Queried domain
- `A`: IPv4 addresses
- `AAAA`: IPv6 addresses
- `MX`: Mail exchange servers
- `NS`: Nameservers
- `TXT`: Text records
- `CNAME`: Canonical name records

**Record Types Queried**:
- **A**: IPv4 address records
- **AAAA**: IPv6 address records
- **MX**: Mail server records (with priority)
- **NS**: Authoritative nameserver records
- **TXT**: Text records (SPF, DKIM, verification)
- **CNAME**: Alias records

**Use Cases**:
- Email server identification
- Subdomain discovery
- DNS configuration validation
- Mail security analysis (SPF/DKIM)

---

### 4. Have I Been Pwned Plugin

**Status**: ⚠️ Limited (public API has restrictions)

**Purpose**: Email breach detection

**Search Types**: EMAIL

**How it Works**:
- Queries Have I Been Pwned API v3
- Checks if email appears in known data breaches
- Returns breach details and affected data classes
- Rate limited to 1 request per 1.5 seconds

**Installation**: No special requirements (uses public API)

**API Notes**:
- Public API has access restrictions
- Some features require API key (paid)
- Rate limited: 1 request per 1.5 seconds
- No authentication required for basic checks

**Example Usage**:
```python
# Check for breaches
result = engine.run_single_plugin("Have I Been Pwned", "test@example.com", SearchType.EMAIL)
```

**Output Data (if breached)**:
- `email`: Queried email
- `breached`: True/False
- `breach_count`: Number of breaches found
- `breaches`: List of breach objects with:
  - `name`: Breach name
  - `title`: Human-readable title
  - `domain`: Breached domain
  - `breach_date`: When breach occurred
  - `pwn_count`: Number of accounts affected
  - `data_classes`: Types of data exposed (passwords, emails, etc.)
  - `is_verified`: Whether breach is verified
  - `is_sensitive`: Whether breach contains sensitive data

**Use Cases**:
- Email security assessment
- Breach awareness
- Password reset recommendations
- Security audits

**Limitations**:
- API restrictions may cause 401 errors without key
- Rate limiting (1 req/1.5s)
- Only checks public breaches

---

### 5. Email Validator Plugin

**Status**: ✅ Fully Working

**Purpose**: Email address validation and verification

**Search Types**: EMAIL

**How it Works**:
- Validates email format with regex
- Checks domain existence via DNS
- Verifies MX records for mail delivery
- Calculates validation score

**Installation**: No special requirements

**Example Usage**:
```python
# Validate email
result = engine.run_single_plugin("Email Validator", "user@example.com", SearchType.EMAIL)
```

**Output Data**:
- `email`: Queried email
- `format_valid`: RFC-compliant format check
- `domain_exists`: Domain DNS check
- `has_mx_records`: Mail exchange record check
- `mx_records`: List of MX servers
- `domain`: Extracted domain
- `local_part`: Extracted local part (before @)
- `validation_passed`: Overall validation result
- `validation_score`: Percentage score with assessment

**Validation Steps**:
1. **Format Check**: RFC 5322 compliant regex
2. **Domain Check**: DNS A record lookup
3. **MX Check**: Mail exchange record verification

**Scoring**:
- 100%: Valid - All checks passed
- 66-99%: Likely Valid - Format and domain valid
- 33-65%: Questionable - Only format valid
- 0-32%: Invalid - Format check failed

**Use Cases**:
- Email list validation
- User input verification
- Deliverability assessment
- Domain verification

---

### 6. IP Geolocation Plugin

**Status**: ✅ Fully Working

**Purpose**: IP address geolocation and network information

**Search Types**: IP

**How it Works**:
- Uses free ip-api.com service
- No API key required
- Returns geographic and network data
- Rate limited to 45 requests per minute

**Installation**: No special requirements

**Example Usage**:
```python
# Geolocate IP
result = engine.run_single_plugin("IP Geolocation", "8.8.8.8", SearchType.IP)
```

**Output Data**:
- `ip`: Queried IP address
- `country`: Country name
- `country_code`: ISO country code
- `region`: Region/state name
- `region_code`: Region code
- `city`: City name
- `zip_code`: Postal code
- `latitude`: Latitude coordinate
- `longitude`: Longitude coordinate
- `timezone`: Timezone string
- `isp`: Internet Service Provider
- `organization`: Org name
- `as_number`: Autonomous System number

**API Provider**: ip-api.com (free tier)

**Rate Limits**: 45 requests per minute

**Use Cases**:
- IP origin identification
- Geotargeting analysis
- Network attribution
- ISP identification
- Threat intelligence

**Accuracy**:
- Country: ~99% accurate
- City: ~80% accurate
- Coordinates: Approximate location

---

### 7. Phone Number Lookup Plugin

**Status**: ✅ Fully Working

**Purpose**: Phone number validation and country identification

**Search Types**: PHONE

**How it Works**:
- Validates phone number format
- Extracts country calling code
- Identifies country from code database
- Parses national number

**Installation**: No special requirements

**Example Usage**:
```python
# Analyze phone number
result = engine.run_single_plugin("Phone Number Lookup", "+1-555-123-4567", SearchType.PHONE)
```

**Output Data**:
- `original`: Original input
- `cleaned`: Normalized number
- `is_valid_format`: Format validation result
- `country_code`: Extracted country code (e.g., "1")
- `country`: Country name (e.g., "United States/Canada")
- `national_number`: Number without country code
- `is_international_format`: Whether number includes country code
- `total_digits`: Number of digits

**Country Code Database**: 150+ countries supported

**Validation Rules**:
- Must be 7-15 digits
- International format starts with +
- Country code must be recognized

**Use Cases**:
- Phone number validation
- Country identification
- International format conversion
- Contact list cleanup

**Limitations**:
- Does not validate if number actually exists
- Country code database may not be exhaustive
- No carrier information

---

## Plugin Performance

### Response Times (Typical)

| Plugin | Average Time | Notes |
|--------|-------------|-------|
| Phone Number Lookup | < 0.1s | Local processing |
| Email Validator | 0.5-2s | DNS lookups |
| IP Geolocation | 0.5-1s | API call |
| DNS Lookup | 1-3s | Multiple DNS queries |
| WHOIS | 2-5s | External WHOIS servers |
| Have I Been Pwned | 1.5-3s | API + rate limiting |
| Sherlock | 30-60s | Checks 300+ sites |

### Resource Usage

- **Memory**: < 100MB per plugin
- **CPU**: Low (network bound)
- **Network**: Varies by plugin
- **Disk**: Minimal (logs only)

## Using Multiple Plugins

### Search All Mode

Run all compatible plugins for a search type:

```python
# Search all email plugins
results = engine.run_all_plugins("user@example.com", SearchType.EMAIL, parallel=True)

# Results from: Email Validator + Have I Been Pwned
```

### Parallel vs Sequential

**Parallel** (default):
- Faster overall execution
- Uses ThreadPoolExecutor
- Configurable max_concurrent (default: 5)

**Sequential**:
- One plugin at a time
- Better for rate-limited APIs
- Easier debugging

## Future Plugin Ideas

Potential plugins for expansion:

- [ ] **Social Media API plugins** (Twitter, LinkedIn, Facebook)
- [ ] **Shodan** - Device/service search
- [ ] **TheHarvester** - Email/subdomain harvesting
- [ ] **SpiderFoot** - Automated OSINT
- [ ] **VirusTotal** - File/URL/IP reputation
- [ ] **URLScan** - URL analysis
- [ ] **AlienVault OTX** - Threat intelligence
- [ ] **Certificate Transparency** - SSL certificate search
- [ ] **GitHub** - Code/user search
- [ ] **Pastebin** - Paste search
- [ ] **Hunter.io** - Email finder
- [ ] **Clearbit** - Company data

## Contributing Plugins

See [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md) for detailed instructions on creating new plugins.

**Quick Start**:
1. Create `plugins/yourplugin_plugin.py`
2. Inherit from `PluginBase`
3. Implement required methods
4. Test with framework
5. Submit PR

## Plugin Status Definitions

- ✅ **Fully Working**: All features operational, no dependencies issues
- ⚠️ **Partial**: Works but has limitations or requires external tools
- ❌ **Not Working**: Currently broken or disabled
- 🔧 **In Development**: Being actively developed

## Support

For plugin-specific issues:
1. Check plugin status in this document
2. Verify system dependencies installed
3. Check API key requirements
4. Review plugin logs in `logs/osint_tool.log`
5. Open GitHub issue with plugin name in title
