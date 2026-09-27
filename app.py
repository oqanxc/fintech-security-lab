import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
from vulnerable_endpoints.sql_injection import sqli_bp
app.register_blueprint(sqli_bp)
from vulnerable_endpoints.crlf_injection import crlf_bp
app.register_blueprint(crlf_bp)
from vulnerable_endpoints.xss import xss_bp
app.register_blueprint(xss_bp)

SECRET_KEY = os.getenv("SECRET_KEY", "default_safe_dev_key")
DATABASE = "test.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'AdminPassword123!')")
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "service": "DevSecOps Demo API",
        "endpoints": ["/go?url=test", "/search?username=test", "/greet?name=test"]
    })

# (B608): SQL Injection remediated.
@app.route("/user", methods=["GET"])
def get_user():
    username = request.args.get("username", "")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
   
    query = "SELECT id, username FROM users WHERE username = ?"
    
    try:
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"id": user[0], "username": user[1]})
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error Occured"}), 500

if __name__ == "__main__":
    init_db()
    #  0.0.0.0 listening for Docker container compatilibity.
    app.run(host="0.0.0.0", port=5000)  # nosec B104


# TEST SECRET - PIPELINE TRUFFLEHOG GATE VERIFICATION
# GENERIC = "_1234567890abcdef1234567890abcdef12345678"




    # trigger fresh pipeline run.