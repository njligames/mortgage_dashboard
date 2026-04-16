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
from datetime import datetime
import traceback

# --- LOAD ENV ---
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

app = Flask(__name__)
CORS(app)

DEFAULT_START_DATE = "2019-06-06"


def normalize_close(data, ticker_name=None):
    if data is None or len(data) == 0:
        return pd.Series(dtype="float64")

    if isinstance(data, pd.Series):
        return data.dropna()

    if isinstance(data, pd.DataFrame):
        if data.empty:
            return pd.Series(dtype="float64")

        # Handle MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            try:
                if ("Close", ticker_name) in data.columns:
                    series = data[("Close", ticker_name)]
                else:
                    series = data["Close"]
                    if isinstance(series, pd.DataFrame):
                        series = series.iloc[:, 0]
            except Exception:
                series = data.iloc[:, 0]
        else:
            if "Close" in data.columns:
                series = data["Close"]
            else:
                series = data.iloc[:, 0]

        if isinstance(series, pd.DataFrame):
            series = series.squeeze()

        return series.dropna()

    return pd.Series(dtype="float64")


def series_to_json(series):
    return [
        {"date": pd.Timestamp(date).strftime("%Y-%m-%d"), "value": float(value)}
        for date, value in series.items()
        if pd.notna(value)
    ]


def get_treasury_data(start_date_str=DEFAULT_START_DATE):
    try:
        start = pd.Timestamp(start_date_str)
        end = datetime.today()

        raw = yf.download("^TNX", start=start, end=end, progress=False, auto_adjust=False)
        close_series = normalize_close(raw, "^TNX")

        return series_to_json(close_series)
    except Exception as e:
        print(f"Error fetching Treasury data: {e}")
        traceback.print_exc()
        return []


def get_move_data(start_date_str=DEFAULT_START_DATE):
    try:
        start = pd.Timestamp(start_date_str)
        end = datetime.today()

        raw = yf.download("^MOVE", start=start, end=end, progress=False, auto_adjust=False)
        close_series = normalize_close(raw, "^MOVE")

        return series_to_json(close_series)
    except Exception as e:
        print(f"Error fetching MOVE data: {e}")
        traceback.print_exc()
        return []


def get_mortgage_data(start_date_str=DEFAULT_START_DATE):
    try:
        if not FRED_API_KEY:
            print("FRED_API_KEY is not set")
            return []

        fred = Fred(api_key=FRED_API_KEY)
        mortgage = fred.get_series("MORTGAGE30US")

        start_date = pd.Timestamp(start_date_str)
        mortgage = mortgage.loc[start_date:].dropna()

        return series_to_json(mortgage)
    except Exception as e:
        print(f"Error fetching Mortgage data: {e}")
        traceback.print_exc()
        return []


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/treasury")
def api_treasury():
    try:
        start_date = request.args.get("start_date", DEFAULT_START_DATE)
        data = get_treasury_data(start_date)

        if not data:
            return jsonify({
                "success": False,
                "error": "No treasury data available",
                "data": []
            })

        return jsonify({
            "success": True,
            "label": "10-Year Treasury Yield",
            "unit": "%",
            "start_date": start_date,
            "data": data,
            "current_value": data[-1]["value"]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/move")
def api_move():
    try:
        start_date = request.args.get("start_date", DEFAULT_START_DATE)
        data = get_move_data(start_date)

        if not data:
            return jsonify({
                "success": False,
                "error": "No MOVE data available",
                "data": []
            })

        return jsonify({
            "success": True,
            "label": "MOVE Index",
            "unit": "",
            "start_date": start_date,
            "data": data,
            "current_value": data[-1]["value"]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/mortgage")
def api_mortgage():
    try:
        start_date = request.args.get("start_date", DEFAULT_START_DATE)
        data = get_mortgage_data(start_date)

        if not data:
            return jsonify({
                "success": False,
                "error": "No mortgage data available",
                "data": []
            })

        return jsonify({
            "success": True,
            "label": "30-Year Mortgage Rate",
            "unit": "%",
            "start_date": start_date,
            "data": data,
            "current_rate": data[-1]["value"]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        })


@app.route("/api/test")
def api_test():
    return jsonify({
        "success": True,
        "message": "API is working",
        "fred_key_set": bool(FRED_API_KEY),
        "default_start_date": DEFAULT_START_DATE,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


if __name__ == "__main__":
    print("=" * 60)
    print("Starting Mortgage Dashboard")
    print(f"FRED_API_KEY set: {bool(FRED_API_KEY)}")
    print(f"Default start date: {DEFAULT_START_DATE}")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)