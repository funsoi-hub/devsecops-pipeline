"""DELIBERATELY VULNERABLE. Do not deploy.

This app exists only so the pipeline's self-test can prove each scanner catches
real problems. Every issue below is intentional and labelled.
"""

import sqlite3
import subprocess

import yaml
from flask import Flask, request

app = Flask(__name__)

# [Gitleaks] hard-coded credential committed to git (fake value)
PAYMENTS_API_KEY = "a9f3c1e7b2d84f6a9e0c5b7d1a2f4e8c7b6d5a4f"


@app.route("/user")
def get_user():
    # [Semgrep/Bandit] SQL injection: user input concatenated into SQL
    conn = sqlite3.connect("users.db")
    name = request.args.get("name", "")
    rows = conn.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall()
    return {"rows": rows}


@app.route("/ping")
def ping():
    # [Semgrep/Bandit] OS command injection via shell=True
    host = request.args.get("host", "127.0.0.1")
    return subprocess.check_output("ping -c 1 " + host, shell=True)


@app.route("/config", methods=["POST"])
def load_config():
    # [Bandit] unsafe YAML deserialisation (can construct arbitrary objects)
    return {"config": str(yaml.load(request.data, Loader=yaml.Loader))}


if __name__ == "__main__":
    # [Bandit] Flask debug mode exposes an interactive debugger (remote code execution)
    app.run(host="0.0.0.0", debug=True)
