---
name: directnic-record-types
description: Supported DNS record types for Directnic registrar and their constraints.
type: reference
license: MIT
compatibility: opencode
---

# Directnic DNS Record Types

Last verified: 2026-04-20 (Directnic web UI)

## Supported Record Types

| Type | Purpose | Value Format |
|------|---------|--------------|
| A | IPv4 address mapping | `192.0.2.1` |
| AAAA | IPv6 address mapping | `2001:db8::1` |
| ALIAS | Apex domain alias (CNAME equivalent for zone apex) | `target.example.com.` |
| CNAME | Canonical name alias (subdomains only) | `target.example.com.` |
| TXT | Arbitrary text (SPF, DKIM, verification) | `"v=spf1 include:..."` |
| SRV | Service locator | `10 5 5060 sip.example.com.` |
| MX | Mail exchange | `10 mail.example.com.` |

## Constraints

- **CNAME at apex is NOT supported.** Use ALIAS instead. A CNAME record at the zone apex conflicts with the SOA and NS records that must exist at the root. Directnic provides ALIAS as the apex-compatible alternative.
- **ALIAS is apex-only.** For subdomains, use CNAME.
- **SRV format:** priority weight port target (four space-separated fields).
- **MX format:** priority host (priority 0-65535, lower = preferred).
- **Trailing dot:** ALIAS, CNAME, SRV, and MX target values should end with a trailing dot for fully qualified domain names.

## Issue Reference

- GitHub Issue: #1092