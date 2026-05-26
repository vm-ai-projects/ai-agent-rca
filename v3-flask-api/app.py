# ============================================================
# RCA Agent — Flask REST API
# Author : Vivek Mishra
# Model  : Claude Sonnet 4.6 (Anthropic)
# Endpoint: POST /analyze
# ============================================================

import os
import json
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS — allows browser (index.html) to call this API
# equivalent to @CrossOrigin in Spring Boot
CORS(app)

# Claude Sonnet 4.6 client
client = anthropic.Anthropic()

# Model token limits
MAX_INPUT_TOKENS  = 200000
MAX_OUTPUT_TOKENS = 8192

# Agent system prompt
SYSTEM_PROMPT = """
You are an expert Site Reliability Engineer and incident analyst.
Analyze the provided logs or incident description and produce a
structured Root Cause Analysis (RCA) report.

Respond ONLY with a valid JSON object (no markdown, no backticks)
with this exact structure:
{
  "title": "short incident title",
  "severity": "Critical | High | Medium | Low",
  "summary": "2-3 sentence plain-English summary of what happened",
  "root_causes": ["root cause 1", "root cause 2"],
  "affected_components": ["component 1", "component 2"],
  "timeline": [
    {"time": "HH:MM", "event": "what happened"}
  ],
  "immediate_actions": ["action 1", "action 2"],
  "long_term_fixes": ["fix 1", "fix 2"]
}
"""


# ── Health check endpoint ────────────────────────────────────
# GET /health — confirms the server is running
# equivalent to @GetMapping("/health") in Spring Boot
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model" : "claude-sonnet-4-6",
        "agent" : "RCA Agent v3"
    })


# ── Main RCA endpoint ────────────────────────────────────────
# POST /analyze — accepts logs, returns structured RCA report
# equivalent to @PostMapping("/analyze") in Spring Boot
@app.route('/analyze', methods=['POST'])
def analyze():

    # Parse incoming JSON request body
    # equivalent to @RequestBody in Spring Boot
    data = request.get_json()

    # Validate that logs field is present
    if not data or not data.get('logs'):
        return jsonify({
            "error": "Missing required field: logs"
        }), 400

    logs = data['logs']

    # Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role"   : "user",
                "content": f"Analyze this incident and provide RCA:\n\n{logs}"
            }
        ]
    )

    # Extract and parse the JSON response
    response_text = response.content[0].text
    rca_report    = json.loads(response_text)

    # Build token usage summary
    usage = {
        "input_tokens"    : response.usage.input_tokens,
        "output_tokens"   : response.usage.output_tokens,
        "total_tokens"    : response.usage.input_tokens + response.usage.output_tokens,
        "input_pct"       : round((response.usage.input_tokens  / MAX_INPUT_TOKENS)  * 100, 2),
        "output_pct"      : round((response.usage.output_tokens / MAX_OUTPUT_TOKENS) * 100, 2),
        "estimated_cost"  : round((response.usage.input_tokens * 0.000003) + (response.usage.output_tokens * 0.000015), 6)
    }

    # Return RCA report + token usage as JSON response
    # equivalent to ResponseEntity.ok(response) in Spring Boot
    return jsonify({
        "report": rca_report,
        "usage" : usage
    })


# ── Error handlers ───────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Start the server ─────────────────────────────────────────
# equivalent to SpringApplication.run() in Spring Boot
if __name__ == '__main__':
    print("\n🚀 RCA Agent API starting...")
    print("   Endpoint : http://localhost:5000/analyze")
    print("   Health   : http://localhost:5000/health")
    print("   Model    : claude-sonnet-4-6\n")
    app.run(debug=True, port=5000)