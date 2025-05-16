import os
import json
from datetime import datetime
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")
if not API_KEY:
    raise RuntimeError("SERPAPI_API_KEY not set in .env")

def fetch_flights_json(outbound_date: str) -> dict:
    """
    Fetches structured JSON from SerpApi’s Google Flights engine
    for a one-way flight on the given outbound_date.
    """
    params = {
        "engine":        "google_flights",     # SerpApi engine name :contentReference[oaicite:2]{index=2}
        "departure_id":  "HAN",                # Hanoi – Noi Bai Intl :contentReference[oaicite:3]{index=3}
        "arrival_id":    "JFK,LGA,EWR",        # New York airports :contentReference[oaicite:4]{index=4}
        "outbound_date": outbound_date,        # e.g. "2025-05-14" :contentReference[oaicite:5]{index=5}
        "type":          "2",                  # 2 = one-way :contentReference[oaicite:6]{index=6}
        "travel_class":  "3",                  # 1 = Economy :contentReference[oaicite:7]{index=7} 2 = premium eco; 3 = business
        "hl":            "en",                 # UI language :contentReference[oaicite:8]{index=8}
        "gl":            "us",                 # locale :contentReference[oaicite:9]{index=9}
        "currency":      "USD",                # pricing in USD :contentReference[oaicite:10]{index=10}
        "api_key":       API_KEY
    }
    search = GoogleSearch(params)
    result = search.get_dict()               # Full JSON payload :contentReference[oaicite:11]{index=11}
    return {
        "booking_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "travel_date":  outbound_date,
        "data":         {
            "best_flights":  result.get("best_flights", []),
            "other_flights": result.get("other_flights", [])
        }
    }

def save_to_file(data: dict, filename: str = "flights25-6_busi.json"):
    """Write the flights JSON to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Exported flight data to {filename}")

if __name__ == "__main__":
    target_date = "2025-06-25"
    flights_json = fetch_flights_json(target_date)
    save_to_file(flights_json)
    # Optionally, print to console:
    print(json.dumps(flights_json, indent=2))
