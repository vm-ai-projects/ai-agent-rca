# AI Incident RCA Agent

An AI-powered Root Cause Analysis agent that analyzes incident logs and stack traces to produce structured RCA reports. Built with Claude Sonnet 4.6 (Anthropic) and delivered in three progressive implementations — from a CLI script to a production-ready REST API.

---

## Live Demo

**[Launch Web App →](https://vm-ai-projects.github.io/ai-agent-rca/)**

Paste any stack trace or upload a log file and get an AI-generated RCA report in seconds.

---

## Architecture Evolution

This project deliberately shows three stages of architectural maturity:

```
v1  CLI Script       → Python script, terminal input/output
       ↓
v2  Web Application  → Standalone browser app, no backend required
       ↓
v3  REST API         → Flask microservice, callable by any system
```

Each version solves the same problem at a different level of enterprise readiness.

---

## Versions

### v1 — Python CLI Agent (`v1-python-script/`)

A command-line agent that reads incident logs from a file or uses a built-in sample, calls the Claude API, and prints a structured RCA report to the terminal with token usage metrics.

**Run:**
```bash
pip install anthropic python-dotenv
python rca_agent.py
python rca_agent.py --input logs.txt --output report.json
```

**Features:**
- Accepts log files via `--input` flag
- Saves JSON report via `--output` flag
- Prints token usage with visual progress bars
- Estimated cost per API call

---

### v2 — Standalone Web App (`v2-web-app/`)

A single-file HTML/JS web application that runs entirely in the browser. No server, no build tools — just open the file or visit the GitHub Pages URL.

**Run:**
```
Open index.html in any browser
```

**Features:**
- Paste logs or upload a `.txt` / `.log` file
- Rendered RCA report with severity badge and timeline
- Download report as a `.txt` file
- Token usage panel with progress bars and cost estimate
- API key entered by user — never stored or transmitted elsewhere

---

### v3 — Flask REST API (`v3-flask-api/`)

A production-pattern REST microservice that exposes the RCA agent as an HTTP endpoint. Any system — monitoring tools, Slack bots, CI pipelines, or other services — can call it.

**Run:**
```bash
pip install flask flask-cors anthropic python-dotenv
python app.py
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| POST | `/analyze` | Analyze logs and return RCA report |

**Request:**
```json
POST /analyze
Content-Type: application/json

{
  "logs": "ERROR OutOfMemoryError Java heap space at IIRSearchService..."
}
```

**Response:**
```json
{
  "report": {
    "title": "Java Heap OutOfMemoryError in IIRSearchService",
    "severity": "Critical",
    "summary": "...",
    "root_causes": ["..."],
    "affected_components": ["..."],
    "timeline": [{"time": "03:42", "event": "..."}],
    "immediate_actions": ["..."],
    "long_term_fixes": ["..."]
  },
  "usage": {
    "input_tokens": 240,
    "output_tokens": 892,
    "total_tokens": 1132,
    "input_pct": 0.12,
    "output_pct": 10.89,
    "estimated_cost": 0.0141
  }
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Claude Sonnet 4.6 (Anthropic) |
| Backend | Python 3.14, Flask, flask-cors |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| API Client | anthropic Python SDK |
| Config | python-dotenv |
| Hosting | GitHub Pages (v2) |

---

## Setup

**1. Clone the repository:**
```bash
git clone https://github.com/vm-ai-projects/ai-agent-rca.git
cd ai-agent-rca
```

**2. Get an Anthropic API key:**

Sign up at [console.anthropic.com](https://console.anthropic.com) and generate an API key.

**3. Set the API key:**
```bash
# Windows
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"

# Mac / Linux
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**4. Install dependencies:**
```bash
pip install anthropic python-dotenv flask flask-cors
```

---

## Token Economics

This agent uses Claude Sonnet 4.6 with the following token limits and pricing:

| | Limit | Price |
|-|-------|-------|
| Input | 200,000 tokens | $3.00 / 1M tokens |
| Output | 8,192 tokens | $15.00 / 1M tokens |

A typical RCA analysis costs approximately **$0.01–0.02 USD (₹1–2)**.

---

## Sample Output

```
INCIDENT : Java Heap OutOfMemoryError in IIRSearchService
SEVERITY : Critical

SUMMARY
The IIRSearchService JVM process exhausted its allocated heap memory,
triggering a fatal OutOfMemoryError. Search service became unresponsive,
impacting end users. Root cause is unbounded memory consumption due to
large query result sets and insufficient heap configuration.

ROOT CAUSES
  1. Insufficient JVM heap size configured for peak load
  2. Potential memory leak from unclosed resources or unbounded caches
  3. Large search queries returning excessive result sets loaded into heap
  4. No memory usage monitoring or alerting in place

IMMEDIATE ACTIONS
  1. Restart IIRSearchService JVM with increased -Xmx allocation
  2. Capture heap dump on next occurrence for analysis
  3. Enable real-time heap monitoring via JVisualVM or APM agent

LONG-TERM FIXES
  1. Analyze heap dump to identify memory leak root cause
  2. Implement pagination and result size limits on search queries
  3. Add heap usage alerts at 70% and 85% thresholds
  4. Introduce circuit breaker to reject requests under memory pressure
```

---

## Author

**Vivek Mishra** — Senior Technical Architect  
[GitHub](https://github.com/vm-ai-projects) · [LinkedIn](https://linkedin.com/in/vivek-mishra)

---

*Built with Claude Sonnet 4.6 · Anthropic API*