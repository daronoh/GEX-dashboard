import streamlit as st
import pandas as pd
from src.sidebar import sidebar
from src.gamma_calc import calculate_gamma_exposure
from src.plotting import plot_gamma_exposure
from src.scraper import scrape_data

def main():
    st.set_page_config(layout="wide")
    st.title("Gamma Exposure Dashboard")

    ticker = sidebar()
    if not ticker:
        st.info("Please enter a ticker symbol in the sidebar.")
        return

    try:
        with st.spinner(f"Loading {ticker} data..."):
            spot_price, options_data = scrape_data(ticker)
    except FileNotFoundError:
        st.error(f"File ./data/{ticker}_quotedata.csv not found.")
        return
    except Exception as e:
        st.exception(e)
        return

    st.header(f"Ticker: {ticker}")
    st.caption(f"Underlying spot: {spot_price:.2f}")

    gamma_exposure = calculate_gamma_exposure(options_data, spot_price)

    plot_gamma_exposure(gamma_exposure, spot_price)

if __name__ == "__main__":
    main()