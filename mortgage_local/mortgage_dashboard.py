import os
from dotenv import load_dotenv
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import mplcursors
from fredapi import Fred
from datetime import datetime, timedelta


# --- LOAD ENV ---
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY not found in .env file")

# --- CONFIG ---
end = datetime.today()
start_short = end - timedelta(days=180)  # For Treasury and MOVE
start_long = datetime(2018, 1, 1)  # For Mortgage rates

# --- DATA SOURCES ---

# 10Y Treasury Yield proxy (6 months)
us10y = yf.download("^TNX", start=start_short, end=end)["Close"]
if isinstance(us10y, pd.DataFrame):
    us10y = us10y.squeeze()

# MOVE Index (bond volatility) (6 months)
move = yf.download("^MOVE", start=start_short, end=end)["Close"]
if isinstance(move, pd.DataFrame):
    move = move.squeeze()

# Mortgage rates (FRED) - from 2018
fred = Fred(api_key=FRED_API_KEY)
mortgage = fred.get_series("MORTGAGE30US")
mortgage = mortgage.loc[start_long:end]

# --- ALIGN DATA FOR SHORT-TERM VIEW ---
df_short = pd.DataFrame({
    "US10Y": us10y,
    "MOVE": move
})
df_short = df_short.ffill()

# --- CREATE INTERACTIVE PLOT ---
plt.style.use('seaborn-v0_8-darkgrid')

fig, axes = plt.subplots(3, 1, figsize=(14, 10))
fig.suptitle('Mortgage & Interest Rate Dashboard', fontsize=14, fontweight='bold')

# Plot 1: 10-Year Treasury Yield
line1, = axes[0].plot(df_short.index, df_short["US10Y"], 'b-', linewidth=1.5, label='10Y Treasury')
axes[0].set_title("10-Year Treasury Yield (Last 6 Months)")
axes[0].set_ylabel("Yield (%)")
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right')

# Plot 2: MOVE Index
line2, = axes[1].plot(df_short.index, df_short["MOVE"], 'r-', linewidth=1.5, label='MOVE Index')
axes[1].set_title("MOVE Index - Bond Volatility (Last 6 Months)")
axes[1].set_ylabel("Index Value")
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right')

# Plot 3: 30-Year Mortgage Rate (from 2018)
line3, = axes[2].plot(mortgage.index, mortgage.values, 'g-', linewidth=1.5, label='30Y Mortgage')
axes[2].set_title("30-Year Mortgage Rate (Since 2018)")
axes[2].set_ylabel("Rate (%)")
axes[2].set_xlabel("Date")
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right')

# Add horizontal line for current rate
current_rate = mortgage.iloc[-1]
axes[2].axhline(y=current_rate, color='darkgreen', linestyle='--', alpha=0.7, label=f'Current: {current_rate:.2f}%')
axes[2].legend(loc='upper right')

# --- ENABLE INTERACTIVE CURSORS ---
# This allows clicking on points to see values

cursor1 = mplcursors.cursor(line1, hover=False)
cursor2 = mplcursors.cursor(line2, hover=False)
cursor3 = mplcursors.cursor(line3, hover=False)

@cursor1.connect("add")
def on_add1(sel):
    date = pd.Timestamp(sel.target[0], unit='D').strftime('%Y-%m-%d')
    sel.annotation.set(
        text=f"Date: {date}\nYield: {sel.target[1]:.2f}%",
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.9)
    )

@cursor2.connect("add")
def on_add2(sel):
    date = pd.Timestamp(sel.target[0], unit='D').strftime('%Y-%m-%d')
    sel.annotation.set(
        text=f"Date: {date}\nMOVE: {sel.target[1]:.2f}",
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.9)
    )

@cursor3.connect("add")
def on_add3(sel):
    date = pd.Timestamp(sel.target[0], unit='D').strftime('%Y-%m-%d')
    sel.annotation.set(
        text=f"Date: {date}\nRate: {sel.target[1]:.2f}%",
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.9)
    )

# --- ADD ZOOM/PAN INSTRUCTIONS ---
instructions = """
Navigation Controls:
• Pan: Click and drag with left mouse button
• Zoom: Scroll wheel or use rectangle zoom (click zoom icon in toolbar)
• Reset: Press 'h' for home view
• Click on any point to see date and value
"""
fig.text(0.02, 0.02, instructions, fontsize=8, verticalalignment='bottom',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.subplots_adjust(bottom=0.12)  # Make room for instructions

# Enable interactive mode for zooming/panning
plt.ion()
plt.show(block=True)