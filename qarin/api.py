"""The answering model: Jev, by TypeSafe. One request carries one profile and up to 50 items."""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
PER_CALL = 50


def get_key():
    """TYPESAFE_API_KEY from the environment, else from a .env file in the current folder or the repository root."""
    k = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if k:
        return k
    for env in (Path.cwd() / ".env", Path(__file__).resolve().parents[1] / ".env"):
        if env.is_file():
            for line in env.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if line.startswith("TYPESAFE_API_KEY") and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("No API key. Set TYPESAFE_API_KEY in your environment or in a .env file (see .env.example).")


def question(text, options):
    """The question each item is put as: the respondent is the person in the profile."""
    return {"type": "score",
            "instructions": ("How would the person in the profile respond to this statement on a "
                             f"questionnaire about themselves?\n\nStatement: {text}"),
            "criteria": [f"This person would answer '{o}'." for o in options]}


def body(state, items, formats):
    return {"state": state, "model": MODEL,
            "questions": {i["item_id"]: question(i["text"], formats[i["format"]]) for i in items}}


def post(payload, key, timeout=90.0, retries=6):
    """One request, retried with backoff on rate limits, server errors and network errors."""
    data = json.dumps(payload).encode("utf-8")
    wait = 2.0
    for attempt in range(retries + 1):
        req = urllib.request.Request(ENDPOINT, data=data, method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "qarin-digital-twins/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:1000]
            if (e.code in (429, 529) or e.code >= 500) and attempt < retries:
                time.sleep(wait); wait = min(wait * 2, 60); continue
            raise SystemExit(f"HTTP {e.code} from the answering model: {msg}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == retries:
                raise SystemExit(f"network error after {retries} retries: {e}")
            time.sleep(wait); wait = min(wait * 2, 60)


def probabilities(response, items, formats):
    """{item_id: [p1..pK]} normalized, or None where the model returned nothing for an item."""
    ans = response.get("answers", {}) or {}
    out = {}
    for i in items:
        K = len(formats[i["format"]])
        pr = (ans.get(i["item_id"]) or {}).get("probabilities") or {}
        p = [float(pr.get(str(k), 0.0) or 0.0) for k in range(K)]
        s = sum(p)
        out[i["item_id"]] = [x / s for x in p] if s > 0 else None
    return out
