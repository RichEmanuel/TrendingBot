# =========================================================
# dashboard/app.py
# Simple Flask dashboard for TrendingBot data
# =========================================================
from flask import Flask, render_template_string, send_file
import sqlite3
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import io

DB_PATH = Path("../data/trends.db")
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>TrendingBot Dashboard</title>
<style>
body { font-family: Arial; margin: 40px; background: #111; color: #eee; }
h1 { color: #00ff88; }
table { border-collapse: collapse; width: 80%; }
th, td { border-bottom: 1px solid #444; padding: 8px; text-align: left; }
th { background: #222; }
</style>
</head>
<body>
<h1>Daily Trending Report ({{date}})</h1>
<h2>Top Items</h2>
<table>
<tr><th>Rank</th><th>Item</th><th>Score</th></tr>
{% for i, row in enumerate(rows, start=1) %}
  <tr><td>{{i}}</td><td>{{row[0]}}</td><td>{{"%.2f"|format(row[1])}}</td></tr>
{% endfor %}
</table>
<p>Generated {{date}}</p>
<img src="/chart/{{rows[0][0]}}" alt="chart" width="600">
</body>
</html>
"""

@app.route("/")
def index():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT item_name, AVG(score) FROM trends "
        "GROUP BY item_name ORDER BY AVG(score) DESC LIMIT 10;"
    )
    rows = cur.fetchall()
    con.close()
    return render_template_string(HTML, rows=rows, date=datetime.now().strftime("%Y-%m-%d %H:%M"))

@app.route("/chart/<item>")
def chart(item):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT timestamp, score FROM trends WHERE item_name=? ORDER BY timestamp ASC",
        (item,),
    )
    data = cur.fetchall()
    con.close()

    if not data:
        return "No data", 404

    times = [t for t, _ in data]
    scores = [s for _, s in data]

    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(times, scores, color="#00ff88", marker="o")
    ax.set_title(f"{item} Trend")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Score")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")
# =========================================================
#  Entry point
# =========================================================
if __name__ == "__main__":
    # run the flask development server
    print("🚀  Starting TrendingBot dashboard on http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)