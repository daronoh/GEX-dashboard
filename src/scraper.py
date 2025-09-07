import os
import pandas as pd
import requests
import json
import re

def parse_option_symbol(symbol):
    """
    Extract call/put flag and strike price from OCC option symbol.
    Example: SPXW260630P07900000 -> ('P', 790.0)
             SPX250919C00200000 -> ('C', 2000.0)
    """
    m = re.search(r'\d{6}([CP])(\d{8})$', symbol)
    if not m:
        return None, None, None
    expiry = m.group(0)
    option_type = m.group(1)
    strike_raw = m.group(2)
    # OCC strike: 8 digits, last 3 are decimals
    strike = int(strike_raw[:-3]) + int(strike_raw[-3:]) / 1000
    return expiry, option_type, strike

def scrape_data(ticker):
    """Scrape data from CBOE website and update if necessary"""
    if not os.path.exists("data"):
        os.makedirs("data")

    data_file_path = f"data/{ticker}.json"

    try:
        data = requests.get(
            f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{ticker}.json"
        )
        with open(data_file_path, "w") as f:
            json.dump(data.json(), f)

    except ValueError:
        data = requests.get(
            f"https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json"
        )
        with open(data_file_path, "w") as f:
            json.dump(data.json(), f)

    data = pd.DataFrame.from_dict(data.json())
    spot_price = data.loc["current_price", "data"]
    option_data = pd.DataFrame(data.loc["options", "data"])
    option_data = option_data[option_data['gamma'] != 0]
    option_data = option_data.dropna(subset=['gamma'])
    option_data[['expiry','option_type', 'strike']] = option_data['option'].apply(
        lambda x: pd.Series(parse_option_symbol(x))
    )
    option_data = option_data.dropna(subset=['expiry', 'option_type', 'strike'])
    return spot_price, option_data