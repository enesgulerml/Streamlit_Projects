import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
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

@st.cache_data(ttl=60*60*4) 
def get_historical_data(ticker, start_date, end_date):
    """Fetches historical price data (OHLCV) from Yahoo Finance API."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        return data
    except Exception as e:
        st.error(f"Data fetching error for {ticker}: {e}")
        return pd.DataFrame()

def calculate_max_drawdown(series):
    """Calculates Maximum Drawdown (MDD) as a percentage."""
    cumulative_returns = (1 + series.pct_change().dropna()).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns / peak) - 1
    return drawdown.min() * 100

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Global Market Dynamic Analysis Panel",
    page_icon="📈",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- Sidebar Controls ---
st.sidebar.title("🛠️ Analysis Settings")
st.sidebar.markdown("---")

# 1. Asset Selection
selected_asset_name = st.sidebar.selectbox(
    "Select Asset for Analysis:",
    list(TICKERS.keys()),
    index=0 
)
selected_ticker = TICKERS[selected_asset_name]

# 2. Date Range Selection
today = date.today()
one_year_ago = today - timedelta(days=365)
start_date = st.sidebar.date_input("Start Date:", one_year_ago, max_value=today)
end_date = st.sidebar.date_input("End Date:", today, max_value=today)

if start_date >= end_date:
    st.sidebar.error("Start date must be before the end date.")
    st.stop()

# 3. Technical Analysis Setting (Moving Average)
window_ma = st.sidebar.slider("Moving Average Window (Days):", 
                              min_value=10, max_value=200, value=50, step=10)

st.sidebar.markdown("---")
st.sidebar.caption("Use the menu on the left for other analysis pages.")


# --- Main Dashboard Title ---
st.title(f"🌍 {selected_asset_name} Dynamic Performance Summary")
st.markdown("Professional-grade candlestick chart and core financial metrics.")
st.markdown("---")


# --- Fetch Data ---
data_df = get_historical_data(selected_ticker, start_date, end_date)

if data_df.empty:
    st.error("Could not fetch data for the selected asset in the specified range.")
    st.stop()

# --- Robust Price Column Selection ---
price_column = 'Adj Close' if 'Adj Close' in data_df.columns else 'Close'
close_prices = data_df[price_column]
# ------------------------------------

# --- Core Metric Cards (4 columns) ---
st.subheader("📊 Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)

# 1. Total Return Calculation (FIX: Explicitly convert to float)
initial_price = float(close_prices.iloc[0])
final_price = float(close_prices.iloc[-1]) # FIX: This now ensures final_price is a float.
total_return = (final_price / initial_price - 1) * 100
total_return = float(total_return) # Ensure final result is float

# 2. Volatility (Annualized Standard Deviation) (FIX: Explicitly convert to float)
daily_change = close_prices.pct_change().dropna()
annualized_volatility = float(np.std(daily_change) * np.sqrt(252) * 100)

# 3. Maximum Drawdown (FIX: Explicitly convert to float)
max_dd_series = calculate_max_drawdown(close_prices)
max_dd = float(max_dd_series)

# Display Metrics
col1.metric(
    label="Total Return (%)",
    value=f"{total_return:.2f} %",
    delta=f"{total_return:.2f}" if total_return != 0 else "0.00"
)

col2.metric(
    label="Annualized Volatility (%)",
    value=f"{annualized_volatility:.2f} %"
)

col3.metric(
    label="Max Drawdown (MDD) (%)",
    value=f"{max_dd:.2f} %",
    delta=f"{max_dd:.2f}"
)

col4.metric(
    label="Current Price ($)",
    value=f"${final_price:.2f}" # final_price is now guaranteed to be a float!
)

st.markdown("---")

# --- Professional Visualization: Interactive Candlestick Chart (Plotly) ---

# Calculate Moving Average 
data_df['MA'] = data_df['Close'].rolling(window=window_ma).mean()

st.subheader(f"📈 {selected_asset_name} Price Action and {window_ma}-Day MA")

fig = go.Figure(data=[
    # Candlestick Chart
    go.Candlestick(
        x=data_df.index,
        open=data_df['Open'],
        high=data_df['High'],
        low=data_df['Low'],
        close=data_df['Close'],
        name='Candlestick'
    ),
    # Moving Average (MA)
    go.Scatter(
        x=data_df.index,
        y=data_df['MA'],
        mode='lines',
        line=dict(color='#FF5733', width=2),
        name=f'{window_ma}-Day MA'
    )
])

# Layout settings: Hide range slider for a cleaner look
fig.update_layout(
    xaxis_rangeslider_visible=False,
    title_text=f"{selected_asset_name} Price Chart",
    yaxis_title='Price ($)',
    height=650,
    template="plotly_dark", 
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
