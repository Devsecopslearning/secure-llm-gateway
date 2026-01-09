from flask import Flask, request, jsonify, render_template
from app.client import query_llama3

app = Flask(__name__)

@app.route("/")
def home():
    # Serve the HTML UI
    return render_template("index.html")

@app.route("/secure-query", methods=["POST"])
def secure_query():
    api_key = request.headers.get("X-API-Key")
    user_role = request.headers.get("X-User-Role")
    data = request.get_json()

    # Security checks
    if api_key != "mysecretkey":
        return jsonify({"error": "Invalid API key"}), 403
    if user_role not in ["admin", "auditor"]:
        return jsonify({"error": "Unauthorized role"}), 403

    user = data.get("user")
    prompt = data.get("prompt")

    # Query the model
    response = query_llama3(prompt)

    # Return JSON response
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run()