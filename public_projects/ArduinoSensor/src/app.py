from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

engine = create_engine('sqlite:///temperature_data.db')

@app.route('/')
def index():
    return render_template('index.html')

# (live update)
@app.route('/api/realtime-data')
def realtime_data():
    query = "SELECT * FROM temperature_data ORDER BY timestamp DESC LIMIT 100"
    df = pd.read_sql(query, engine)
    return jsonify({
        "timestamps": df['timestamp'].tolist(),
        "temperatures": df['value'].tolist()
    })

@app.route('/api/last-day')
def last_day():
    query = """
    SELECT * FROM temperature_data
    WHERE timestamp >= datetime('now', '-1 days')
    ORDER BY timestamp ASC
    """
    df = pd.read_sql(query, engine)
    return jsonify({
        "timestamps": df['timestamp'].tolist(),
        "temperatures": df['value'].tolist()
    })

@app.route('/api/last-3-days')
def last_3_days():
    query = """
    SELECT * FROM temperature_data
    WHERE timestamp >= datetime('now', '-3 days')
    ORDER BY timestamp ASC
    """
    df = pd.read_sql(query, engine)
    return jsonify({
        "timestamps": df['timestamp'].tolist(),
        "temperatures": df['value'].tolist()
    })

@app.route('/api/all-data')
def all_data():
    query = "SELECT * FROM temperature_data ORDER BY timestamp ASC"
    df = pd.read_sql(query, engine)
    return jsonify({
        "timestamps": df['timestamp'].tolist(),
        "temperatures": df['value'].tolist()
    })

app.run(debug=True)
