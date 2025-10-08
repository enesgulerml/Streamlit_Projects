import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(
    page_title = "Simple Streamlit Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MAIN PART ---
st.title("Simple Interactive Data Explorer")
st.write("---")
st.markdown("""
Welcome to your first tiny Streamlit project! This app generates a synthetic
dataset and allows you to filter it using the sidebar controls.

Use the controls on the left to see the data and chart update in real-time.
""")

@st.cache_data
def load_data():
    with st.spinner("Generating synthetic dataset..."):
        time.sleep(0.5)

        N_ROWS = 100

        data = {
            "Date" : pd.to_datetime(pd.date_range(start='2023-01-01', periods=N_ROWS)),
            'Value_A' : np.random.randn(N_ROWS).cumsum() + 50,
            'Value_B' : np.random.randint(1,10, N_ROWS),
            'Category' : np.random.choice(["Red","Green","Blue","Yellow"], N_ROWS, p = [0.4, 0.3, 0.2, 0.1])
        }
        df = pd.DataFrame(data)
        return df

df = load_data()

st.sidebar.header("Filter Controls")

min_value_b = st.sidebar.slider(
    "Minimum Threshold for Value B:",
    min_value = df["Value_B"].min(),
    max_value = df["Value_B"].max(),
    value = int(df["Value_B"].median()),
    step=1
)

selected_categories = st.sidebar.multiselect(
    "Select Categories:",
    options = df["Category"].unique(),
    default = df["Category"].unique()
)

filtered_df = df[
    (df["Value_B"] >= min_value_b) &
    (df["Category"].isin(selected_categories))
]

st.subheader("Time Series Chart for Value A")

st.line_chart(filtered_df.set_index('Date')['Value_A'])

st.subheader("Filtered Data Table")
st.write("---")
st.info(f"Showing **{len(filtered_df)}** rows out of **{len(df)}** total based on your filters.")

st.dataframe(filtered_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**How to Run:**
1. Save this code as 'streamlit_app.py
2. Run in your terminal: 'streamlit run streamlit_app.py'
""")