from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# ---------------- MySQL Connection ----------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306))
        )
        return conn
    except Exception as e:
        print("DB Connection Error:", e)
        return None

# ---------------- ROUTES ----------------
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------- LOGIN API ----------------
@app.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT name FROM users WHERE name=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"success": True, "email": user["name"]})
    else:
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=False)
