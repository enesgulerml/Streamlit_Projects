# 📈 Global Markets Dynamic Analysis Dashboard (Streamlit)
This project is an interactive, web-based financial analysis application developed using Python's powerful financial libraries (yfinance, pandas, plotly) and the Streamlit framework. It allows users to deeply analyze the performance, risk metrics, and correlations of various financial assets, including popular stocks, indices, commodities, and FX pairs.

# 🌟 Key Features
This multi-page Streamlit application offers three main analysis sections:

## 1. Dynamic Performance Summary (Main Page)
Visualization of a selected asset's (Stock, Index, Commodity, FX) Live Candlestick Chart (plotly).
    
Dynamic adjustment of the Moving Average (MA) window.

Critical metrics for the asset: Total Return, Annualized Volatility, and Maximum Drawdown (MDD).

## 2. Correlation Analysis
Heatmap visualization showing the relationship between multiple selected assets.

Option to select the correlation calculation method (Pearson or Spearman).

Analysis of how closely assets are related for portfolio diversification.

## 3. Risk Metrics Comparison
Comparison of Risk-Adjusted Return (Sharpe Ratio) and Maximum Drawdown (MDD) values for all selected assets.

Dynamic calculation of the Sharpe Ratio by setting the Risk-Free Rate.

Visualization of assets with the best risk/return ratios on a bar chart.

## ⚙️ Setup and Running
Follow these steps to run the project on your local machine.

Prerequisites
Python 3.8+

pip or conda package manager

### Step 1: Clone the Repository
git clone [https://github.com/enesgulerml/Streamlit_Projects.git](https://github.com/enesgulerml/Streamlit_Projects.git)
cd Streamlit_Projects

### Step 2: Create a Virtual Environment (Recommended)
Create and activate a virtual environment to isolate the project:

# If using Conda:
conda create -n finance_env python=3.10
conda activate finance_env

# If using Venv:
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\activate # Windows

### Step 3: Install Dependencies
Install all necessary libraries for the project from the requirements.txt file:

pip install -r requirements.txt

### Step 4: Run the Application
Start the Streamlit application:

streamlit run app.py

The application will automatically open in your browser (usually at http://localhost:8501).

# 🛠️ Technologies Used
Python: The main language of the project.

Streamlit: For building the interactive web application.

Pandas & NumPy: For financial data processing and calculations.

yfinance: For fetching financial data (stocks, indices, commodities).

Plotly: For creating professional and interactive charts (Candlestick Chart, Heatmap).

# 🤝 Contributing
Your feedback and contributions are valued! If you would like to contribute to the project:

Fork the repository.

Create a new feature branch (git checkout -b feature/great-new-feature).

Commit your changes (git commit -m 'feat: added a great new feature').

Push the branch (git push origin feature/great-new-feature).

Open a Pull Request.

# 📜 License
This project is licensed under the MIT License. See the LICENSE file for more details.
