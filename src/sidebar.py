import streamlit as st

def sidebar():
    ticker = st.sidebar.text_input("Ticker")
    return ticker