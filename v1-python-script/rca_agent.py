# ============================================================
# RCA Agent — AI-powered Incident Root Cause Analysis
# Author : Vivek Kumar Mishra
# Model  : Claude Sonnet 
# ============================================================

import os
import json
import argparse
import anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from .env file
load_dotenv()

# Claude Sonnet 4.6 client
client = anthropic.Anthropic()

# Model token limits
MAX_INPUT_TOKENS  = 200000
MAX_OUTPUT_TOKENS = 8192

# Agent system prompt — defines Claude's role and expected output format
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


def analyze_incident(logs):
    """Call Claude API with incident logs and return structured RCA report."""

    print("\n🤖 RCA Agent started — analyzing your logs...\n")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this incident and provide RCA:\n\n{logs}"
            }
        ]
    )

    response_text = response.content[0].text
    rca_report    = json.loads(response_text)

    return rca_report, response.usage


def print_report(report):
    """Print the RCA report in a readable format."""

    print("=" * 60)
    print(f"INCIDENT : {report['title']}")
    print(f"SEVERITY : {report['severity']}")
    print("=" * 60)

    print(f"\nSUMMARY\n{report['summary']}")

    print("\nROOT CAUSES")
    for i, cause in enumerate(report['root_causes'], 1):
        print(f"  {i}. {cause}")

    print("\nAFFECTED COMPONENTS")
    for component in report['affected_components']:
        print(f"  - {component}")

    if report.get('timeline'):
        print("\nTIMELINE")
        for event in report['timeline']:
            print(f"  {event['time']} — {event['event']}")

    print("\nIMMEDIATE ACTIONS")
    for i, action in enumerate(report['immediate_actions'], 1):
        print(f"  {i}. {action}")

    print("\nLONG-TERM FIXES")
    for i, fix in enumerate(report['long_term_fixes'], 1):
        print(f"  {i}. {fix}")

    print("\n" + "=" * 60)


def print_token_usage(usage):
    """Print token consumption, remaining capacity, and estimated cost."""

    input_tokens  = usage.input_tokens
    output_tokens = usage.output_tokens
    total_used    = input_tokens + output_tokens

    input_pct  = (input_tokens  / MAX_INPUT_TOKENS)  * 100
    output_pct = (output_tokens / MAX_OUTPUT_TOKENS) * 100

    input_remaining  = MAX_INPUT_TOKENS  - input_tokens
    output_remaining = MAX_OUTPUT_TOKENS - output_tokens

    # Sonnet 4.6 pricing: $3/M input tokens, $15/M output tokens
    estimated_cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)

    print("\n" + "=" * 60)
    print("TOKEN USAGE REPORT")
    print("=" * 60)

    print(f"\n📥 INPUT TOKENS")
    print(f"   Used       : {input_tokens:,}")
    print(f"   Remaining  : {input_remaining:,} of {MAX_INPUT_TOKENS:,}")
    print(f"   Usage      : {input_pct:.2f}%")

    print(f"\n📤 OUTPUT TOKENS")
    print(f"   Used       : {output_tokens:,}")
    print(f"   Remaining  : {output_remaining:,} of {MAX_OUTPUT_TOKENS:,}")
    print(f"   Usage      : {output_pct:.2f}%")

    print(f"\n📊 TOTAL THIS CALL")
    print(f"   Tokens     : {total_used:,}")
    print(f"   Est. cost  : ${estimated_cost:.6f} USD")

    # Visual progress bars
    bar_len = 30
    filled  = int((input_pct / 100) * bar_len)
    print(f"\n   Input  [{'█' * filled}{'░' * (bar_len - filled)}] {input_pct:.1f}%")

    filled  = int((output_pct / 100) * bar_len)
    print(f"   Output [{'█' * filled}{'░' * (bar_len - filled)}] {output_pct:.1f}%")

    print("=" * 60)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="AI-powered Incident RCA Agent")
    parser.add_argument("--input",  help="Path to log file",         required=False)
    parser.add_argument("--output", help="Path to save JSON report", required=False)
    args = parser.parse_args()

    if args.input:
        with open(args.input, 'r') as f:
            logs = f.read()
    else:
        # Built-in sample — Watchlist OOM incident
        logs = """
        [2026-05-01 03:42:11] ERROR - java.lang.OutOfMemoryError: Java heap space
        at com.sita.watchlist.search.IIRSearchService.executeSearch(IIRSearchService.java:247)
        [2026-05-01 03:42:11] WARN  - GC overhead limit exceeded, heap usage 98%
        [2026-05-01 03:42:12] ERROR - Tomcat node watchlist-node-01 unresponsive
        [2026-05-01 03:42:13] INFO  - Failover triggered to watchlist-node-02
        [2026-05-01 03:42:45] ERROR - watchlist-node-02 OutOfMemoryError: Java heap space
        [2026-05-01 03:42:46] CRITICAL - All nodes down, service unavailable
        Active threads at time of failure: 847
        Search result cache: DISABLED
        IIR field mapper: NOT FOUND for entity type WATCHLIST_ENTITY
        """

    report, usage = analyze_incident(logs)
    print_report(report)
    print_token_usage(usage)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✅ Report saved to: {args.output}")
