from flask import Flask, request, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)
app.config["SITE_ACTIVE"] = True

# Configuration
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1461964964603625594/jH-XEtXJtxJm69mjlFViAi8BQWutT-P6wTioZ-tElKw3BlJihCEeuNB2AazCCIjgKQKU"
ADMIN_PASSWORD = "1844cool"
OWNER_PASSWORD = "deedee"
BLOCKED_IPS = ["51.158.54.22"]  # Add banned IPs here

def is_blocked():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    return ip in BLOCKED_IPS

# =================== HTML Templates ===================

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to jinx97</title>
    <style>
        body {
            background-color: #000;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding-top: 100px;
        }
        input[type="text"], input[type="password"] {
            padding: 10px;
            font-size: 16px;
            width: 250px;
            margin-bottom: 20px;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Welcome to Jinx97</h1>
    <form id="authForm">
        <input type="text" id="name" placeholder="Enter your name to authorize your acsess " required><br>
        <button type="submit">Authenticate</button>
    </form>
    <button onclick="location.href='/admin'">Admin Panel</button>
    <button onclick="location.href='/owner'">Owner Panel</button>

    <script>
        document.getElementById("authForm").onsubmit = async function(e) {
            e.preventDefault();
            const name = document.getElementById("name").value;
            const res = await fetch("/auth", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name })
            });
            const text = await res.text();
            if (text.startsWith("redirect:")) {
                window.location.href = text.replace("redirect:", "");
            } else {
                alert(text);
            }
        };
    </script>
</body>
</html>
"""

MEMBERS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Members Area</title></head>
<body style="background-color:black; color:white; text-align:center; padding-top:100px;">
    <h1>Welcome, Member!</h1>
    <p>You have successfully authenticated.</p>
    <a href="/">Back to Home</a>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Panel</title></head>
<body style="background-color:black; color:white; text-align:center; padding-top:100px;">
    <h1>Admin Panel</h1>
    <form id="adminForm">
        <input type="password" id="password" placeholder="Admin Password" required><br>
        <input type="text" id="message" placeholder="Message to send" required><br>
        <button type="submit">Send to Discord</button>
    </form>
    <script>
        document.getElementById("adminForm").onsubmit = async function(e) {
            e.preventDefault();
            const password = document.getElementById("password").value;
            const message = document.getElementById("message").value;
            const res = await fetch("/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password, message })
            });
            alert(await res.text());
        };
    </script>
</body>
</html>
"""

OWNER_HTML = """
<!DOCTYPE html>
<html>
<head><title>Owner Panel</title></head>
<body style="background-color:black; color:white; text-align:center; padding-top:100px;">
    <h1>Owner Panel</h1>
    <form id="toggleForm">
        <input type="password" id="password" placeholder="Owner Password" required><br>
        <button type="submit">Toggle Site Status</button>
    </form>
    <script>
        document.getElementById("toggleForm").onsubmit = async function(e) {
            e.preventDefault();
            const password = document.getElementById("password").value;
            const res = await fetch("/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password })
            });
            alert(await res.text());
        };
    </script>
</body>
</html>
"""

# =================== Routes ===================

@app.route("/", methods=["GET"])
def index():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    if not app.config["SITE_ACTIVE"]:
        return "🚫 The site is currently shut down by the owner.", 403
    return render_template_string(HTML_PAGE)

@app.route("/auth", methods=["POST"])
def auth():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    if not app.config["SITE_ACTIVE"]:
        return "🚫 The site is currently shut down by the owner.", 403

    data = request.get_json(silent=True)
    if not data or not data.get("name"):
        return "Name is required.", 400

    name = data["name"].strip()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    payload = { "content": f"✅ Auth by `{name}` from IP `{ip}` at {timestamp}" }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        return f"Webhook failed: {str(e)}", 500

    return "redirect:/members"

@app.route("/members", methods=["GET"])
def members():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    if not app.config["SITE_ACTIVE"]:
        return "🚫 The site is currently shut down by the owner.", 403
    return render_template_string(MEMBERS_HTML)

@app.route("/admin", methods=["GET"])
def admin():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    if not app.config["SITE_ACTIVE"]:
        return "🚫 The site is currently shut down by the owner.", 403
    return render_template_string(ADMIN_HTML)

@app.route("/send", methods=["POST"])
def send():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    if not app.config["SITE_ACTIVE"]:
        return "🚫 The site is currently shut down by the owner.", 403

    data = request.get_json(silent=True)
    if not data or data.get("password") != ADMIN_PASSWORD:
        return "❌ Incorrect password", 403

    message = data.get("message", "").strip()
    if not message:
        return "⚠️ Message cannot be empty", 400

    payload = { "content": f"📢 Admin Message: {message}" }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        return f"Webhook failed: {str(e)}", 500

    return "✅ Message sent to Discord"

@app.route("/owner", methods=["GET"])
def owner():
    if is_blocked():
        return "❌ You have been banned from this site", 403
    return render_template_string(OWNER_HTML)

@app.route("/toggle", methods=["POST"])
def toggle():
    if is_blocked():
        return "❌ You have been banned from this site", 403

    data = request.get_json(silent=True)
    if not data or data.get("password") != OWNER_PASSWORD:
        return "❌ Incorrect password", 403

    app.config["SITE_ACTIVE"] = not app.config["SITE_ACTIVE"]
    status = "🟢 Site is now ACTIVE" if app.config["SITE_ACTIVE"] else "🔴 Site is now SHUT DOWN"
    return status
