import os, requests
from bs4 import BeautifulSoup
import re
import json
from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv
from datetime import datetime
# print(json.dumps(results, indent=2))
# 1. Load your SerpApi key from .env
# 1. Load your SerpApi API key from a .env file in the same folder

# Load API key
# Load your SerpApi API key from .env in the same directory
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")
if not API_KEY:
    raise RuntimeError("SERPAPI_API_KEY not set in .env")  # Ensure key is available :contentReference[oaicite:3]{index=3}

def fetch_html(outbound_date: str) -> str:
    """
    Fetches raw HTML for a one-way Google Flights search via SerpApi.
    """
    params = {
        "engine":        "google_flights",      # Google Flights engine :contentReference[oaicite:4]{index=4}
        "departure_id":  "HAN",                 # Hanoi (Noi Bai Intl) :contentReference[oaicite:5]{index=5}
        "arrival_id":    "JFK,LGA,EWR",         # All major NYC airports :contentReference[oaicite:6]{index=6}
        "outbound_date": outbound_date,         # e.g. "2025-05-14" :contentReference[oaicite:7]{index=7}
        "type":          "2",                   # 2 = One-way search :contentReference[oaicite:8]{index=8}
        "travel_class":  "1",                   # 1 = Economy :contentReference[oaicite:9]{index=9}
        "hl":            "en",                  # English UI :contentReference[oaicite:10]{index=10}
        "gl":            "us",                  # U.S. locale :contentReference[oaicite:11]{index=11}
        "currency":      "USD",                 # Prices in USD :contentReference[oaicite:12]{index=12}
        "show_hidden":   "true",                # Include hidden deals :contentReference[oaicite:13]{index=13}
        "deep_search":   "true",                # Full browser-style render :contentReference[oaicite:14]{index=14}
        "no_cache":      "true",                # Bypass SerpApi cache :contentReference[oaicite:15]{index=15}
        "output":        "html",                # Request raw HTML :contentReference[oaicite:16]{index=16}
        "api_key":       API_KEY
    }
    search = GoogleSearch(params)
    result = search.get_dict()    
    print(json.dumps(result, indent=2))# Use SerpApi client to fetch JSON dict :contentReference[oaicite:17]{index=17}
    html = result.get("html")
    if not html:
        raise RuntimeError("No HTML returned by SerpApi.")  
    return html

def parse_flights(html: str, travel_date: str) -> list[dict]:
    """
    Parses the raw HTML to extract flights matching the travel_date.
    Uses BeautifulSoup to locate each flight card.
    """
    soup = BeautifulSoup(html, "html.parser")   # Initialize parser :contentReference[oaicite:18]{index=18}
    records = []
    booking_date = datetime.now().strftime("%Y-%m-%d")  # e.g., "2025-05-11" :contentReference[oaicite:19]{index=19}

    # Each flight result is in a <div role="listitem">
    for card in soup.select('div[role="listitem"]'):  # CSS selector for flight cards :contentReference[oaicite:20]{index=20}
        airline_tag = card.select_one("div[data-test-id='airline-name'] span")  
        dep_tag     = card.select_one("div[data-test-id='departure-time']")
        arr_tag     = card.select_one("div[data-test-id='arrival-time']")
        price_tag   = card.select_one("div[data-test-id='price']")

        # Skip incomplete cards
        if not (airline_tag and dep_tag and arr_tag and price_tag):
            continue

        dep_time = dep_tag.get_text(strip=True)   # e.g. "02:10" :contentReference[oaicite:21]{index=21}
        arr_time = arr_tag.get_text(strip=True)   # e.g. "23:05" :contentReference[oaicite:22]{index=22}
        # Extract numeric price, remove any non-digits
        price_str = re.sub(r"[^\d\.]", "", price_tag.get_text())  
        price     = float(price_str)              # Convert to float for analysis :contentReference[oaicite:23]{index=23}

        # Append record if it matches the intended travel_date
        records.append({
            "booking_date":   booking_date,
            "travel_date":    travel_date,
            "airline":        airline_tag.get_text(strip=True),
            "departure_time": dep_time,
            "arrival_time":   arr_time,
            "price_usd":      price
        })
    return records

if __name__ == "__main__":
    TARGET_DATE = "2025-05-14"
    html_content = fetch_html(TARGET_DATE)
    flights = parse_flights(html_content, TARGET_DATE)
    if not flights:
        print(f"No flights found for travel_date={TARGET_DATE}")
    else:
        print(f"Found {len(flights)} flights for travel_date={TARGET_DATE} (booking_date={flights[0]['booking_date']}):")
        for f in flights:
            print(f"{f['airline']} {f['departure_time']}→{f['arrival_time']} : ${f['price_usd']}")