import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
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
        data = yf.download(list(tickers.values()), start=start_date, end=end_date, progress=False)

        if data.empty: return pd.DataFrame()

        if 'Adj Close' in data.columns.get_level_values(0):
            data = data['Adj Close']
        else:
            data = data['Close']

        name_map = {v: k for k, v in tickers.items()}
        data.rename(columns=name_map, inplace=True)

        return data
    except Exception as e:
        st.error(f"Multi-asset data fetching error: {e}")
        return pd.DataFrame()


def calculate_max_drawdown(series):
    """Calculates Maximum Drawdown (MDD) as a percentage."""
    cumulative_returns = (1 + series.pct_change().dropna()).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns / peak) - 1
    return drawdown.min() * 100


def calculate_sharpe_ratio(series, risk_free_rate=0.04):
    """Calculates the Sharpe Ratio (Risk-Adjusted Return)."""
    daily_returns = series.pct_change().dropna()
    annualized_return = daily_returns.mean() * 252
    annualized_volatility = daily_returns.std() * np.sqrt(252)

    if annualized_volatility == 0:
        return 0.0

    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    return sharpe_ratio


# --- Page Settings ---
st.set_page_config(page_title="Risk Metrics Comparison", page_icon="🛡️", layout="wide")

st.title("🛡️ Risk and Return Metrics Comparison")
st.markdown("Examine the risk-adjusted returns (Sharpe) and worst-case drawdowns (MDD) of various assets.")
st.markdown("---")

# --- Sidebar Controls ---
st.sidebar.header("Metrics Settings")

# Date Range
today = date.today()
three_years_ago = today - timedelta(days=365 * 3)
start_date = st.sidebar.date_input("Start Date:", three_years_ago, max_value=today)
end_date = st.sidebar.date_input("End Date:", today, max_value=today)

# Risk-Free Rate Input
risk_free_rate_input = st.sidebar.number_input(
    "Annual Risk-Free Rate (%):",
    min_value=0.0,
    max_value=10.0,
    value=4.0,
    step=0.5
)
risk_free_rate = risk_free_rate_input / 100.0

# Asset Selection (Multi-select)
selected_assets = st.sidebar.multiselect(
    "Assets to Compare:",
    list(TICKERS.keys()),
    default=list(TICKERS.keys())
)

# --- Data Fetching and Calculation ---
if len(selected_assets) < 1:
    st.warning("Please select at least one asset for comparison.")
    st.stop()

# Filter Tickers for selected assets
filtered_tickers = {k: TICKERS[k] for k in selected_assets}
data_df = get_multiple_adj_close_data(filtered_tickers, start_date, end_date)

if data_df.empty:
    st.error("Could not fetch data for the selected assets.")
    st.stop()

# --- Metric Calculation and Results Table ---
results = []
for column in data_df.columns:
    # Ensure data is numeric
    asset_series = pd.to_numeric(data_df[column], errors='coerce').dropna()
    if asset_series.empty: continue

    # Calculate metrics, ensuring they are simple floats for the table
    sharpe = float(calculate_sharpe_ratio(asset_series, risk_free_rate))
    mdd = float(calculate_max_drawdown(asset_series))

    # Calculate Annualized Return
    total_return = (asset_series.iloc[-1] / asset_series.iloc[0] - 1) * 100
    days_diff = (end_date - start_date).days
    if days_diff == 0: days_diff = 1
    annualized_return = float(((1 + total_return / 100) ** (365 / days_diff) - 1) * 100)

    results.append({
        'Asset': column,
        f'Sharpe Ratio (RFR={risk_free_rate_input}%)': f"{sharpe:.2f}",
        'Annualized Return (%)': f"{annualized_return:.2f}",
        'Maximum Drawdown (MDD) (%)': f"{mdd:.2f}",
        'Sharpe_Sort': sharpe
    })

results_df = pd.DataFrame(results).sort_values(by='Sharpe_Sort', ascending=False)
results_df = results_df.drop(columns=['Sharpe_Sort'])  # Remove numerical column

st.subheader("📚 Comparative Risk Metrics Table")
st.dataframe(results_df, use_container_width=True, hide_index=True)

st.markdown("---")

# --- Visualization: Sharpe Ratio (Bar Chart) ---
st.subheader("📈 Asset Ranking by Sharpe Ratio")

# Get float values for Sharpe Ratio
plot_data = results_df.copy()
# Convert Sharpe Ratio back to float for plotting
plot_data['Sharpe'] = plot_data[f'Sharpe Ratio (RFR={risk_free_rate_input}%)'].astype(str).str.replace('%', '').astype(
    float)

fig_sharpe = px.bar(
    plot_data,
    x='Asset',
    y='Sharpe',
    title=f'Sharpe Ratio (Risk-Adjusted Return) - RFR={risk_free_rate_input}%',
    color='Sharpe',
    color_continuous_scale=px.colors.sequential.Plotly3,
    template="plotly_dark"
)
fig_sharpe.update_layout(yaxis_title='Sharpe Ratio', xaxis_title='Asset')
st.plotly_chart(fig_sharpe, use_container_width=True)

st.caption("""
**Sharpe Ratio:** Measures the return of an investment compared to its risk. A higher value is better.  
**Maximum Drawdown (MDD):** Shows the biggest percentage drop from a peak to a trough.
""")
