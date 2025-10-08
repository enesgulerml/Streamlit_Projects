import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(
    page_title = "Professional Sales Dashboard",
    layout = "wide",
    initial_sidebar_state = "expanded",
)

@st.cache_data
def generate_sales_data(start_date=datetime(2023,1,1), days =365, seed=42):
    np.random.seed(seed)

    dates = [start_date + timedelta(days=i) for i in range(days)]

    data = {
        'Date' : dates,
        'Region' : np.random.choice(['North', 'South', 'East', 'West'], days),
        'Product' : np.random.choice(['Laptop', 'Monitor', 'Keyboard', 'Mouse', 'Webcam'], days, p = [0.3,0.25,0.2,0.15,0.1]),
        'Revenue' : np.random.normal(loc=1500, scale=800, size=days) * np.random.rand(days) * 2,
        'Units_Sold' : np.random.randint(1, 10, days)
    }

    df = pd.DataFrame(data)

    df['Revenue'] = df['Revenue'].abs()
    product_multipliers = {'Laptop': 4, 'Monitor': 2, 'Keyboard': 0.5, 'Mouse': 0.2, 'Webcam': 0.8}
    df["Revenue"] = df.apply(lambda row: row['Revenue'] * product_multipliers[row['Product']], axis = 1)

    return df.sort_values('Date').reset_index(drop=True)

df = generate_sales_data()

st.title("Sales Performance Analytics")
st.markdown("A dynamic dashboard for viewing regional and product sales trends.")

st.sidebar.header("Data Filters")

min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
date_range = st.sidebar.slider(
    'Select Date Range:',
    min_value = min_date,
    max_value = max_date,
    value = (min_date, max_date),
    format = "YYYY-MM-DD"
)
start_date_filter = datetime.combine(date_range[0], datetime.min.time())
end_date_filter = datetime.combine(date_range[1], datetime.max.time())

selected_regions = st.sidebar.multiselect(
    'Select Regions:',
    options = df["Region"].unique(),
    default= df["Region"].unique()
)

filtered_df = df[
    (df['Date'] >= start_date_filter) &
    (df['Date'] <= end_date_filter) &
    (df['Region'].isin(selected_regions))
]

if filtered_df.empty:
    st.error("No data available for the selected filters. Please adjust your criteria.")
    st.stop()

st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

total_revenue = filtered_df['Revenue'].sum()
total_units = filtered_df['Units_Sold'].sum()
avg_sale_value = filtered_df['Revenue'].sum() / filtered_df['Units_Sold'].sum() if total_units > 0 else 0
data_period = f"{date_range[0].strftime('%b %d')} - {date_range[1].strftime('%b %d')}"

with col1:
    st.metric(
        label = "Total Revenue",
        value = f"${total_revenue:.2f}",
        delta = f"Over {data_period}",
        delta_color = "off"
    )

with col2:
    st.metric(
        label = "Total Units Sold",
        value = f"{total_units:,}",
        delta = f"In {len(filtered_df['Date'].unique())} days"
    )

with col3:
    st.metric(
        label = "Average Sales Value",
        value=f"${avg_sale_value:,.2f}",
        delta = "Per unit sold"
    )

st.markdown("---")

st.subheader("Sales Trends & Distribution")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("##### Revenue Trend")
    daily_revenue = filtered_df.groupby(pd.to_datetime(filtered_df['Date'].dt.date))['Revenue'].sum().reset_index()
    daily_revenue.columns = ['Date', 'Total Revenue']

    chart_line = alt.Chart(daily_revenue).mark_line(point=True).encode(
        x=alt.X('Date', axis=alt.Axis(title='Date')),
        y=alt.Y('Total Revenue', axis=alt.Axis(title='Revenue ($)', format='$,.0f')),
        tooltip=[alt.Tooltip('Date'), alt.Tooltip('Total Revenue', format='$,.2f')]
    ).properties(
        title='Daily Revenue Over Time'
    ).interactive()

    st.altair_chart(chart_line, use_container_width=True)

with chart_col2:
    st.markdown("##### Revenue by Product")
    product_revenue = filtered_df.groupby('Product')['Revenue'].sum().reset_index()
    product_revenue.columns = ['Product', 'Total Revenue']

    chart_bar = alt.Chart(product_revenue).mark_bar().encode(
        x=alt.X('Total Revenue', axis=alt.Axis(title='Revenue ($)', format='$,.0f')),
        y=alt.Y('Product', sort='-x', axis=alt.Axis(title='Product Name')),
        color='Product',
        tooltip=[alt.Tooltip('Product'), alt.Tooltip('Total Revenue', format='$,.2f')]
    ).properties(
        title='Total Revenue by Product Category'
    ).interactive()

    st.altair_chart(chart_bar, use_container_width=True)

st.markdown("---")
st.subheader("Raw Filtered Data")
st.dataframe(filtered_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **How to Run This App:**
    1.  Install the required libraries: 
        `pip install streamlit pandas numpy altair`
    2.  Save this code as `sales_dashboard.py`.
    3.  Run in your terminal: `streamlit run sales_dashboard.py`
    """
)