"""
sql_injection.py

Deliberately vulnerable route used to verify that Bandit (SAST) catches(rule B608)

"""

from flask import Blueprint, request, jsonify
import sqlite3

sqli_bp = Blueprint("sql_injection", __name__)

DATABASE = "test.db"


@sqli_bp.route("/search")
def search():
    """
    VULNERABLE ENDPOINT.

    The 'username' query param is combined directly into a SQL
    string without using a parameterized query. Bandit  must flag
    this (B608:possible SQL injection)

    Test request:
        http://localhost:5000/search?username=admin' OR '1'='1
    """
    username = request.args.get("username", "")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # VULNERABLE LINE: raw string concatenation into SQL
    query = "SELECT id, username FROM users WHERE username = ?"

    try:
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "username": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    
    """query = "SELECT id, username FROM users WHERE username = '" + username + "'"

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "username": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500 """

    #  SAFE ALTERNATIVE using placeholder
    # query = "SELECT id, username FROM users WHERE username = ?"
    # cursor.execute(query, (username,))