import re
import requests
from urllib.parse import urlparse
import difflib

# Known safe domains
KNOWN_DOMAINS = ["google.com", "facebook.com", "twitter.com", "github.com", "youtube.com", "chatgpt.com", "stackoverflow.com",
    "reddit.com","wikipedia.org","amazon.com","ebay.com","microsoft.com","apple.com","netflix.com","openai.com","dropbox.com","pinterest.com","tumblr.com","paypal.com","quora.com","medium.com","nytimes.com","bbc.com","cnn.com","yahoo.com","bing.com","whatsapp.com","telegram.org","tiktok.com","spotify.com","soundcloud.com","slack.com","notion.so","airbnb.com","uber.com","zoom.us"]

# Blacklisted domains
BLACKLISTED_DOMAINS = ["malicious.com","phishing.com","badwebsite.net","evil.com","hacksite.org","dangeroussite.io","fakebank.com","stealsinfo.net","clickfraud.com","virusdownload.com","spammydomain.org","scamalert.com","fakepaypal.com","fakegoogle.com","malwaretest.com","phishingsite.com","trojanexample.com","dangerouslink.net","keyloggerdownload.com","untrustedsite.org"]

# SQL Injection patterns (basic, query parameters only)
SQLI_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
    r"((\%3D)|(=))[^\\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))"
]

# XSS patterns (basic, case-insensitive, query parameters only)
XSS_PATTERNS = [
    r"<script.*?>",  # opening script tag
    r"</script>",    # closing script tag
    r"javascript:",  # javascript: pseudo-protocol
    r"onerror=",     # onerror attribute
    r"onload=",      # onload attribute
]

def normalize_domain_for_check(domain: str) -> str:
    """Remove www. prefix for typo checking."""
    if domain.startswith("www."):
        return domain[4:].lower()
    return domain.lower()

def is_typo_domain(domain: str) -> bool:
    """
    Detects if the domain is a typo of a known domain using fuzzy matching.
    """
    domain_check = normalize_domain_for_check(domain)
    for legit in KNOWN_DOMAINS:
        ratio = difflib.SequenceMatcher(None, domain_check, legit).ratio()
        if ratio > 0.85 and domain_check != legit:  # similarity threshold
            return True
    return False

def check_url(url: str) -> dict:
    """
    Checks URL for blacklists, typos, SQLi, and XSS.
    Returns dictionary with status, reason, and score.
    """
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()  # keep www. for display
    query = parsed.query.lower()    # only check query parameters

    # Blacklist check
    for bad in BLACKLISTED_DOMAINS:
        if bad in domain:
            return {"status": "Unsafe", "reason": f"Domain {bad} is blacklisted", "score": 0}

    # Typo check
    if is_typo_domain(domain):
        return {"status": "Risky", "reason": "Domain looks like a typo of a known domain", "score": 20}

    # SQLi check (query parameters only)
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return {"status": "Unsafe", "reason": "Potential SQL Injection detected", "score": 30}

    # XSS check (query parameters only)
    for pattern in XSS_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return {"status": "Unsafe", "reason": "Potential XSS detected", "score": 40}

    # Optional: check if site is reachable
    try:
        response = requests.get(url, timeout=5)

        if response.status_code >= 400:
            return {"status": "Risky", "reason": f"HTTP status {response.status_code}", "score": 50}

    except requests.exceptions.Timeout:
        return {"status": "Unsafe", "reason": "Connection timed out", "score": 10}

    except requests.exceptions.ConnectionError:
        return {"status": "Unsafe", "reason": "Could not connect to the server", "score": 10}

    except requests.exceptions.TooManyRedirects:
        return {"status": "Unsafe", "reason": "Too many redirects (possible redirect loop)", "score": 15}

    except requests.exceptions.SSLError:
        return {"status": "Unsafe", "reason": "SSL certificate error (site may be unsafe)", "score": 20}

    except requests.exceptions.InvalidURL:
        return {"status": "Unsafe", "reason": "Invalid URL format", "score": 5}

    except requests.exceptions.RequestException as e:
        return {"status": "Unsafe", "reason": f"Unexpected error: {e}", "score": 10}

    return {"status": "Safe", "reason": "No issues detected", "score": 100}
    
    
    
    