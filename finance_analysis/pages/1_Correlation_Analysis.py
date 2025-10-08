import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from scipy.stats import spearmanr
from datetime import date, timedelta

# --- CONSTANTS and HELPER FUNCTIONS (Integrated for stability) ---

TICKERS = {
    'S&P 500 (Index)': '^GSPC',
    'NASDAQ (Index)': '^IXIC',
    'Gold (Commodity)': 'GC=F',
    'Crude Oil (WTI)': 'CL=F',
    'Euro/USD (FX)': 'EURUSD=X',
    'Microsoft (Stock)': 'MSFT',
    'Tesla (Stock)': 'TSLA'
}


@st.cache_data
def get_multiple_adj_close_data(tickers, start_date, end_date):
    """Fetches Adjusted Close price data for multiple assets, falling back to Close."""
    try:
        # Download data for all ticker symbols
        data = yf.download(list(tickers.values()), start=start_date, end=end_date, progress=False)

        if data.empty: return pd.DataFrame()

        # --- ROBUST COLUMN SELECTION LOGIC for Multi-Ticker DataFrames ---
        if 'Adj Close' in data.columns.get_level_values(0):
            data = data['Adj Close']
        else:
            # If 'Adj Close' is missing (Indices, FX, Commodities), use 'Close'
            data = data['Close']

        # Rename columns to their descriptive names
        name_map = {v: k for k, v in tickers.items()}
        data.rename(columns=name_map, inplace=True)

        return data
    except Exception as e:
        st.error(f"Multi-asset data fetching error: {e}")
        return pd.DataFrame()


def calculate_correlation(df, method='pearson'):
    """Calculates the correlation matrix using specified method (Pearson or Spearman)."""
    if method == 'spearman':
        df_cleaned = df.dropna()
        if df_cleaned.empty:
            return pd.DataFrame(index=df.columns, columns=df.columns)

        corr_matrix, _ = spearmanr(df_cleaned, axis=0)
        corr_df = pd.DataFrame(corr_matrix, index=df_cleaned.columns, columns=df_cleaned.columns)
        return corr_df
    else:  # Pearson (default)
        return df.corr(method=method)


# --- Page Settings ---
st.set_page_config(page_title="Correlation Analysis", page_icon="🔗", layout="wide")

st.title("🔗 Dynamic Asset Correlation Analysis")
st.markdown("Examine the relationship between selected assets using an interactive heatmap.")
st.markdown("---")

# --- Sidebar Controls ---
st.sidebar.header("Correlation Settings")

# Date Range
today = date.today()
two_years_ago = today - timedelta(days=365 * 2)
start_date = st.sidebar.date_input("Start Date:", two_years_ago, max_value=today)
end_date = st.sidebar.date_input("End Date:", today, max_value=today)

# Correlation Method
correlation_method = st.sidebar.selectbox(
    "Correlation Method:",
    ['pearson', 'spearman'],
    help="Pearson measures linear correlation. Spearman measures monotonic (rank) correlation."
)

# Asset Selection (Multi-select)
selected_assets = st.sidebar.multiselect(
    "Assets to Include in Analysis:",
    list(TICKERS.keys()),
    default=list(TICKERS.keys())[:4]
)

# --- Data Fetching and Calculation ---
if len(selected_assets) < 2:
    st.warning("Please select at least two assets for correlation analysis.")
    st.stop()

# Filter Tickers for selected assets
filtered_tickers = {k: TICKERS[k] for k in selected_assets}
data_df = get_multiple_adj_close_data(filtered_tickers, start_date, end_date)

if data_df.empty or len(data_df.columns) < 2:
    st.error("Could not fetch sufficient data for the selected assets or period.")
    st.stop()

# --- Correlation Matrix Calculation ---
corr_matrix = calculate_correlation(data_df, method=correlation_method)

st.subheader(f"📅 Correlation Matrix ({correlation_method.capitalize()})")
st.write(f"Analysis Time Range: From **{start_date}** to **{end_date}**.")

# --- Professional Visualization: Plotly Heatmap ---

fig = px.imshow(
    corr_matrix,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale=px.colors.diverging.RdBu,
    range_color=[-1, 1],
    labels=dict(x="Asset 1", y="Asset 2", color="Correlation Value"),
    title=f"{correlation_method.capitalize()} Correlation Heatmap"
)

# Rotate axis labels for better readability
fig.update_xaxes(side="top", tickangle=-45)
fig.update_layout(height=600, width=800, template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Note: Correlation ranges from -1 (inverse relationship) to +1 (direct relationship) or 0 (no relationship).")
