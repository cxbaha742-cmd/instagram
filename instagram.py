#!/usr/bin/env python3
"""
Instagram Account Contact Info Retriever (Own Account Only)
Author: Security Research (Ethical Use Only)
Description: Uses authenticated session to fetch your own email and phone number.
Requires: requests library (pip install requests)
"""

import requests
import json
import sys
from typing import Dict, List, Optional

# ======================= CONFIGURATION =======================
# Replace these with your actual values obtained from a logged-in Burp session.
# DO NOT share these credentials. Keep them secure.

YOUR_SESSION_ID = ""      # Example: "9876543210%3Ajohn_doe%3A12"
YOUR_CSRF_TOKEN = ""                    # Example: "xYZ789abcDEF123"
YOUR_IG_DID = ""                    # Example: "12345678-90ab-cdef-1234-567890abcdef"

# Proxy settings (set to None if not using Burp, or use your Burp proxy for debugging)
USE_BURP_PROXY = True   # Set to False to disable proxy
BURP_PROXY = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

# ======================= REQUEST HEADERS =======================
def build_headers(csrf_token: str, session_id: str, ig_did: str) -> Dict[str, str]:
    """Construct all required headers for Instagram API."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "X-IG-App-ID": "936619743392459",
        "X-IG-WWW-Claim": "0",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrf_token,
        "Origin": "https://www.instagram.com",
        "Referer": "https://www.instagram.com/accounts/contact_history/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cookie": f"sessionid={session_id}; csrftoken={csrf_token}; ig_did={ig_did}"
    }

# ======================= API CALL =======================
def fetch_contact_info(session_id: str, csrf_token: str, ig_did: str, use_proxy: bool = False) -> Optional[List[Dict]]:
    """
    Send GET request to Instagram's contact_history endpoint.
    Returns list of contact points (email/phone) or None on failure.
    """
    url = "https://i.instagram.com/api/v1/accounts/contact_history/"
    headers = build_headers(csrf_token, session_id, ig_did)
    proxies = BURP_PROXY if use_proxy else None
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=15)
        print(f"[*] HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return data.get("contact_points", [])
            else:
                print(f"[!] API returned non-ok status: {data}")
                return None
        else:
            print(f"[!] Request failed with status {response.status_code}")
            print(f"[!] Response body: {response.text[:500]}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error: {e}")
        return None

# ======================= OUTPUT FORMATTER =======================
def print_contact_info(contacts: List[Dict]) -> None:
    """Pretty print email and phone numbers."""
    if not contacts:
        print("[!] No contact points found. Your account may have no email/phone added.")
        return
    
    print("\n[+] Contact Information Retrieved Successfully:\n")
    for contact in contacts:
        ctype = contact.get("type", "unknown").upper()
        value = contact.get("value", "N/A")
        confirmed = "✓ Confirmed" if contact.get("confirmed") else "✗ Unconfirmed"
        print(f"  {ctype}: {value} ({confirmed})")
    print("\n[!] This information belongs to the authenticated account only.")

# ======================= MAIN =======================
def main():
    print("\n" + "="*60)
    print(" Instagram Account Contact Info Retriever (Own Account Only)")
    print("="*60 + "\n")
    
    # Validate configuration
    if "your_username" in YOUR_SESSION_ID or "AbC123" in YOUR_CSRF_TOKEN:
        print("[ERROR] You have not replaced the placeholder session credentials.")
        print("Please edit the script and set YOUR_SESSION_ID, YOUR_CSRF_TOKEN, and YOUR_IG_DID.")
        print("\nHow to obtain real values:")
        print("1. Open Burp Suite and configure your browser to use its proxy (127.0.0.1:8080).")
        print("2. Log into instagram.com in the browser.")
        print("3. In Burp -> HTTP history, find any request to i.instagram.com.")
        print("4. Copy the full Cookie header values: sessionid, csrftoken, ig_did.")
        print("5. Paste them into the script.\n")
        sys.exit(1)
    
    print("[*] Fetching contact history from Instagram API...")
    contacts = fetch_contact_info(YOUR_SESSION_ID, YOUR_CSRF_TOKEN, YOUR_IG_DID, USE_BURP_PROXY)
    
    if contacts is not None:
        print_contact_info(contacts)
    else:
        print("[!] Failed to retrieve contact information.")
        print("[*] Possible reasons: expired session, invalid CSRF token, or network issue.")
        print("[*] Try logging out and back in, then update the script with fresh cookies.")

if __name__ == "__main__":
    # Suppress insecure request warnings (since we use verify=False for Burp CA)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
