from flask import Flask, request, jsonify, render_template, session
from app.client import query_llama3
from app.security import log_query
from app.dlp import block_if_pii
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Valid credentials
VALID_CREDENTIALS = {
    "admin": {"password": "admin123", "role": "admin"},
    "auditor": {"password": "auditor456", "role": "auditor"}
}

@app.route("/")
def home():
    # Serve the HTML UI
    return render_template("index.html")
 
@app.route("/login", methods=["POST"])
def login():
    """Authenticate user and create session"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Validate credentials
    if username not in VALID_CREDENTIALS:
        return jsonify({"error": "Invalid username or password"}), 401
    
    user_data = VALID_CREDENTIALS[username]
    if user_data["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create session
    session["username"] = username
    session["role"] = user_data["role"]
    
    return jsonify({"message": "Login successful", "username": username, "role": user_data["role"]}), 200

@app.route("/logout", methods=["POST"])
def logout():
    """Logout user and clear session"""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/secure-query", methods=["POST"])
def secure_query():
    """
    Secure query endpoint with authentication and DLP protection
    
    Security checks:
    1. User authentication (session required)
    2. Role-based authorization (admin/auditor)
    3. Data Loss Prevention (PII detection)
    """
    # Check if user is authenticated
    if "username" not in session:
        return jsonify({"error": "Not authenticated. Please login first"}), 401
    
    user_role = session.get("role")
    if user_role not in ["admin", "auditor"]:
        return jsonify({"error": "Unauthorized role"}), 403

    data = request.get_json()
    prompt = data.get("prompt")
    username = session.get("username")

    # DLP Check: Detect if prompt contains PII
    should_block, error_message, pii_types = block_if_pii(prompt)
    if should_block:
        return jsonify({"error": error_message}), 400

    # Log the query
    log_query(username, prompt)

    # Query the model
    response = query_llama3(prompt)

    # Return JSON response
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run()