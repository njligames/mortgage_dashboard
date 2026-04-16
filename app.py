import os
from dotenv import load_dotenv
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import traceback

# --- LOAD ENV ---
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

app = Flask(__name__)
CORS(app)

# --- HELPER FUNCTIONS ---

def get_treasury_data(days=180):
    """Fetch 10-Year Treasury Yield data"""
    end = datetime.today()
    start = end - timedelta(days=days)
    
    try:
        print(f"Fetching Treasury data from {start} to {end}")
        data = yf.download("^TNX", start=start, end=end, progress=False)
        
        print(f"Treasury raw data shape: {data.shape}")
        print(f"Treasury columns: {data.columns.tolist()}")
        
        if data.empty:
            print("Treasury data is empty!")
            return []
        
        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data["Close"]["^TNX"]
        else:
            close_data = data["Close"]
        
        # Convert to Series if needed
        if isinstance(close_data, pd.DataFrame):
            close_data = close_data.squeeze()
        
        print(f"Treasury close data length: {len(close_data)}")
        
        result = []
        for date, value in close_data.items():
            if pd.notna(value):
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value)
                })
        
        print(f"Treasury result length: {len(result)}")
        return result
        
    except Exception as e:
        print(f"Error fetching Treasury data: {e}")
        traceback.print_exc()
        return []


def get_move_data(days=180):
    """Fetch MOVE Index (bond volatility) data"""
    end = datetime.today()
    start = end - timedelta(days=days)
    
    try:
        print(f"Fetching MOVE data from {start} to {end}")
        data = yf.download("^MOVE", start=start, end=end, progress=False)
        
        print(f"MOVE raw data shape: {data.shape}")
        
        if data.empty:
            print("MOVE data is empty!")
            return []
        
        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data["Close"]["^MOVE"]
        else:
            close_data = data["Close"]
        
        if isinstance(close_data, pd.DataFrame):
            close_data = close_data.squeeze()
        
        print(f"MOVE close data length: {len(close_data)}")
        
        result = []
        for date, value in close_data.items():
            if pd.notna(value):
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value)
                })
        
        print(f"MOVE result length: {len(result)}")
        return result
        
    except Exception as e:
        print(f"Error fetching MOVE data: {e}")
        traceback.print_exc()
        return []


def get_mortgage_data(start_year=2018):
    """Fetch 30-Year Mortgage Rate data from FRED"""
    try:
        if not FRED_API_KEY:
            print("FRED_API_KEY is not set!")
            return []
        
        print(f"Fetching Mortgage data from {start_year}")
        fred = Fred(api_key=FRED_API_KEY)
        mortgage = fred.get_series("MORTGAGE30US")
        
        print(f"Mortgage raw data length: {len(mortgage)}")
        
        start_date = datetime(start_year, 1, 1)
        mortgage = mortgage.loc[start_date:]
        
        print(f"Mortgage filtered data length: {len(mortgage)}")
        
        result = []
        for date, value in mortgage.items():
            if pd.notna(value):
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value)
                })
        
        print(f"Mortgage result length: {len(result)}")
        return result
        
    except Exception as e:
        print(f"Error fetching Mortgage data: {e}")
        traceback.print_exc()
        return []


# --- ROUTES ---

@app.route("/")
def dashboard():
    """Render the main dashboard page"""
    return render_template("dashboard.html")


@app.route("/api/treasury")
def api_treasury():
    """API endpoint for Treasury yield data"""
    try:
        days = request.args.get("days", 180, type=int)
        data = get_treasury_data(days)
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No treasury data available",
                "data": []
            })
        
        return jsonify({
            "success": True,
            "data": data,
            "label": "10-Year Treasury Yield",
            "unit": "%",
            "current_value": data[-1]["value"] if data else None
        })
    except Exception as e:
        print(f"API Treasury error: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/move")
def api_move():
    """API endpoint for MOVE index data"""
    try:
        days = request.args.get("days", 180, type=int)
        data = get_move_data(days)
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No MOVE data available",
                "data": []
            })
        
        return jsonify({
            "success": True,
            "data": data,
            "label": "MOVE Index",
            "unit": "",
            "current_value": data[-1]["value"] if data else None
        })
    except Exception as e:
        print(f"API MOVE error: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/mortgage")
def api_mortgage():
    """API endpoint for mortgage rate data"""
    try:
        start_year = request.args.get("start_year", 2018, type=int)
        data = get_mortgage_data(start_year)
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No mortgage data available",
                "data": []
            })
        
        current_rate = data[-1]["value"] if data else None
        
        return jsonify({
            "success": True,
            "data": data,
            "label": "30-Year Mortgage Rate",
            "unit": "%",
            "current_rate": current_rate
        })
    except Exception as e:
        print(f"API Mortgage error: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/test")
def api_test():
    """Test endpoint to verify API is working"""
    return jsonify({
        "success": True,
        "message": "API is working",
        "fred_key_set": bool(FRED_API_KEY),
        "timestamp": datetime.now().isoformat()
    })


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    print("=" * 50)
    print("Starting Mortgage Dashboard")
    print(f"FRED_API_KEY set: {bool(FRED_API_KEY)}")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)