# Mortgage Rate Monitoring Dashboard

A minimal Python-based dashboard that tracks key macro-financial signals to infer near-term mortgage rate direction.

## Overview

This project visualizes three core indicators:

* **10-Year Treasury Yield (^TNX)** – primary leading indicator for mortgage rates
* **MOVE Index (^MOVE)** – bond market volatility / stress indicator
* **30-Year Mortgage Rate (FRED: MORTGAGE30US)** – lagging confirmation series

The goal is to provide a simple, high-signal view of where mortgage rates are likely heading.

---

## Requirements

* Python 3.9+
* FRED API key (free from [https://fred.stlouisfed.org](https://fred.stlouisfed.org))

---

## Setup

### 1. Create virtual environment

```bash
python3 -m venv mortgage-env
source mortgage-env/bin/activate  # macOS/Linux
# or
mortgage-env\\Scripts\\activate  # Windows
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
FRED_API_KEY=your_fred_api_key_here
```

---

## Usage

Run the dashboard script:

```bash
python mortgage_dashboard.py
```

This will generate a 3-panel chart:

1. 10-Year Treasury Yield
2. MOVE Index (bond volatility)
3. 30-Year Mortgage Rate

---

## Data Sources

* **FRED (Federal Reserve Economic Data)** – mortgage rates
* **Yahoo Finance** – Treasury yields and MOVE index proxies

---

## Interpretation Guide

### 10-Year Treasury Yield

Primary directional signal:

* Rising yields → mortgage rates likely increasing
* Falling yields → mortgage rates likely decreasing

### MOVE Index

Measures bond market volatility:

* High MOVE → unstable rate environment, slower pass-through
* Low MOVE → smoother rate transmission

### Mortgage Rates

Lagging confirmation series reflecting lender pricing.

---

## Limitations

* Mortgage data is weekly and lagging
* Yahoo Finance tickers are proxies, not official bond instruments
* This is an indicator tool, not a prediction model

---

## Optional Enhancements

* Streamlit live dashboard
* Alerts when 10Y crosses moving averages
* Email or webhook notifications
* Intraday futures integration (ZN futures)

---

## License

Use freely for personal or internal analysis.
