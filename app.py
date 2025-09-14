import streamlit as st
import pandas as pd
from src.sidebar import sidebar
from src.gamma_calc import calculate_gamma_exposure
from src.plotting import plot_total_gamma_exposure, plot_call_put_gamma_exposure, plot_gamma_exposure_profile
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
            spot_price, options_data, reporting_date = scrape_data(ticker)
    except FileNotFoundError:
        st.error(f"File ./data/{ticker}_quotedata.csv not found.")
        return
    except Exception as e:
        st.exception(e)
        return

    st.header(f"Ticker: {ticker}")
    st.caption(f"Underlying spot: {spot_price:.2f}")
    st.caption(f"Data as of: {reporting_date}")

    gamma_exposure = calculate_gamma_exposure(options_data, spot_price)
    plot_total_gamma_exposure(gamma_exposure, spot_price)
    plot_call_put_gamma_exposure(gamma_exposure, spot_price)
    plot_gamma_exposure_profile(options_data, spot_price, reporting_date)

if __name__ == "__main__":
    main()