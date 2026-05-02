import os
import json
import requests

from backend.schemas import DisruptionInput
from backend.severity_model import get_severity_label

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def build_prompt(payload):
    severity_label = get_severity_label(payload.severity)
    delay_str = f"{payload.delay_minutes} minutes" if payload.delay_minutes else "unknown duration"
    dep_str   = f" at {payload.scheduled_departure}" if payload.scheduled_departure else ""
    notes_str = f"\nAdditional context: {payload.notes}" if payload.notes else ""
    return f"""Generate THREE airport disruption messages as JSON with keys: passenger, pilot, staff.
Flight: {payload.flight_number} ({payload.airline})
Route: {payload.origin} to {payload.destination}{dep_str}
Delay: {delay_str}
Type: {payload.disruption_type or "Unspecified"}
Severity: {payload.severity}/10 ({severity_label}){notes_str}
Return ONLY JSON: {{"passenger": "...", "pilot": "...", "staff": "..."}}"""

def generate_disruption_messages(payload):
    api_key = ""
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Respond with valid JSON only. No markdown, no code blocks."},
            {"role": "user",   "content": build_prompt(payload)}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=30)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    parsed = json.loads(content)
    return {
        "passenger": str(parsed.get("passenger", "No message generated.")),
        "pilot":     str(parsed.get("pilot",     "No message generated.")),
        "staff":     str(parsed.get("staff",     "No message generated.")),
    }