import datetime # timestamp
import jwt # JSON Web Token (JWT) library for encoding and decoding tokens
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Secret key for JWT encoding and decoding. In a production environment, this should be stored securely and not hardcoded.

load_dotenv()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
AUTH_USERNAME = os.environ["AUTH_USERNAME"]
AUTH_PASSWORD = os.environ["AUTH_PASSWORD"]


@app.route("/api/v1/login", methods=["POST"]) #defining the login route for the authentication service. It accepts POST requests at the specified endpoint.
def login():
  data = request.get_json() 
  if not data or "username" not in data or "password" not in data:
    return (
        jsonify({"status": "fail", "message": "Username and password are required"}),
        400,
    )

  username = data.get("username")
  password = data.get("password")

  # Check if the provided username and password match the expected values.
  if username == AUTH_USERNAME and password == AUTH_PASSWORD:
    payload = {
        "sub": username,
        "role": "fintech_user",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"status": "success", "token": token})

  return jsonify({"status": "fail", "message": "Invalid credentials"}), 401


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001)