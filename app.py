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

# ---------------- Customers ----------------
@app.route("/api/customers")
def api_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers ORDER BY customer_id DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ---------------- Instruments ----------------
@app.route("/api/instruments")
def api_instruments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM instruments WHERE status='Active'")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ---------------- Services ----------------
@app.route("/api/services")
def api_services():
    status = request.args.get("status", None)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if status:
        cursor.execute("SELECT s.service_id, s.service_type, s.service_date, s.status, i.instrument_name, c.customer_name FROM services s JOIN instruments i ON s.instrument_id=i.instrument_id JOIN customers c ON s.customer_id=c.customer_id WHERE s.status=%s ORDER BY s.service_date DESC", (status,))
    else:
        cursor.execute("SELECT s.service_id, s.service_type, s.service_date, s.status, i.instrument_name, c.customer_name FROM services s JOIN instruments i ON s.instrument_id=i.instrument_id JOIN customers c ON s.customer_id=c.customer_id ORDER BY s.service_date DESC")
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=False)

