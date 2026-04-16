# 📊 Mortgage Rate Dashboard

A real-time, interactive web dashboard for tracking mortgage rates, treasury yields, and bond market volatility. Built with Flask and Plotly.js, this application helps homebuyers and real estate professionals make informed decisions about mortgage timing.

## 🎯 Features

- **Real-time Data**: Fetches latest mortgage rates, treasury yields, and volatility indices
- **Interactive Charts**: Pan, zoom, and hover for detailed data exploration
- **Educational Tooltips**: Learn what each metric means for your mortgage decision
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dynamic Insights**: Automated analysis of current market conditions
- **Historical Data**: View mortgage rate trends going back to 2018

## 📈 Data Sources

| Metric | Source | Update Frequency | Description |
|--------|--------|------------------|-------------|
| 30-Year Mortgage Rate | FRED API | Weekly (Thursday) | National average from Freddie Mac Primary Mortgage Market Survey |
| 10-Year Treasury Yield | Yahoo Finance | Daily | Closing yield on 10-year US Treasury bonds |
| MOVE Index | Yahoo Finance | Daily | Merrill Lynch Option Volatility Estimate - measures bond market volatility |

## 🧠 Why These Metrics Matter

### 30-Year Mortgage Rate
The rate you'll actually pay. A 1% difference on a \$400,000 loan equals approximately:
- **\$240/month** in payment difference
- **\$86,000** over the life of the loan

### 10-Year Treasury Yield
The leading indicator for mortgage rates. Mortgage lenders typically price loans 1.5-2.5% above the 10-year Treasury. When Treasury yields rise, mortgage rates usually follow within days.

### MOVE Index
Think of it as the "VIX for bonds." High volatility (>120) means uncertainty, causing lenders to add risk premiums. Low volatility (<90) often means tighter spreads and better mortgage rates relative to Treasuries.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.8+, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Plotly.js (WebGL-accelerated) |
| Data Fetching | yfinance, fredapi |
| Data Processing | pandas |
| HTTP Server | gunicorn (production) |

## 📋 Prerequisites

- Python 3.8 or higher
- FRED API Key (free)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mortgage-dashboard.git
cd mortgage-dashboard
```

## Federal Reserve Economic Data (FRED)

This project uses the **FRED API** to retrieve the 30-Year Fixed Rate Mortgage Average in the United States.

### What is FRED?

[FRED](https://fred.stlouisfed.org/) stands for **Federal Reserve Economic Data**. It is maintained by the **Federal Reserve Bank of St. Louis** and provides access to hundreds of thousands of economic time series from government agencies and other sources.

In this project, FRED is used for:

- **30-Year Fixed Mortgage Rate**
  - Series ID: `MORTGAGE30US`
  - Description: 30-Year Fixed Rate Mortgage Average in the United States
  - Source: Freddie Mac / FRED

### Why FRED is Used

FRED is a reliable source for historical U.S. mortgage rate data because:

- It provides long-term historical coverage
- It is widely used in economic and financial analysis
- It offers a stable API for programmatic access
- The data is maintained by a trusted Federal Reserve institution

### FRED API Key Setup

To use this dashboard, you need a free FRED API key.

#### Steps to get a FRED API key

1. Visit: [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Sign in or create a free account
3. Request an API key
4. Add the key to your `.env` file:

```env
FRED_API_KEY=your_api_key_here
```
