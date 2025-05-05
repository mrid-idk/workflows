import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import re

def get_lag_date():
    """Returns date string in '30-Apr-2025' format."""
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

def sanitize_filename(date_str):
    """Removes special characters for filename compatibility."""
    return re.sub(r'[^A-Za-z0-9]', '', date_str)

def get_session_with_cookie():
    """Establishes session and handles NSE's cookie mechanism."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    })
    # Trigger initial request to set cookies
    session.get("https://www.nseindia.com", timeout=10)
    return session

def download_csv(session, lag_date, save_path):
    """Downloads the report CSV using final URL."""
    base_url = "https://www.nseindia.com/api/reports"
    encoded_params = (
        "?archives=%5B%7B%22name%22%3A%22CM%20-%20Margin%20Trading%20Disclosure%22%2C"
        "%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C"
        "%22section%22%3A%22equities%22%7D%5D"
        f"&date={lag_date}&type=equities&mode=single"
    )
    final_url = base_url + encoded_params

    response = session.get(final_url, timeout=30)

    # Check if response is a file download
    content_disp = response.headers.get("Content-Disposition", "")
    if response.ok and "attachment" in content_disp:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded CSV for {lag_date}")
    else:
        raise Exception(f"❌ Failed to download. Status: {response.status_code}, Headers: {response.headers}")

def main():
    lag_date = get_lag_date()
    file_safe_date = sanitize_filename(lag_date)
    Path("data").mkdir(exist_ok=True)

    file_name = f"mrg_trading_{file_safe_date}.csv"
    save_path = Path("data") / file_name

    session = get_session_with_cookie()
    download_csv(session, lag_date, save_path)

if __name__ == "__main__":
    main()
