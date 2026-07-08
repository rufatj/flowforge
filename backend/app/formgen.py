"""Standalone HTML test form for a workflow's webhook trigger.

Inspects the first webhook node (method + path) and builds a self-contained
dark-themed page that submits JSON to the webhook URL with fetch(), showing
the response inline. No external assets, safe to render in an iframe.
"""
from __future__ import annotations

import json
from typing import Any

from app.n8n import webhook_nodes, webhook_urls

_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>FlowForge test form</title><style>
  body {{ font-family: system-ui, sans-serif; background: #0a0a0f; color: #e4e4e7;
         max-width: 560px; margin: 40px auto; padding: 0 16px; }}
  textarea {{ width: 100%; min-height: 130px; background: #101017; color: #e4e4e7;
         border: 1px solid #2a2a33; border-radius: 8px; padding: 12px;
         font-family: ui-monospace, monospace; font-size: 13px; }}
  button {{ margin-top: 12px; background: #38bdf8; color: #050508; border: 0;
         border-radius: 999px; padding: 10px 22px; font-weight: 600; cursor: pointer; }}
  pre {{ background: #101017; border: 1px solid #2a2a33; border-radius: 8px;
         padding: 12px; white-space: pre-wrap; font-size: 12px; }}
  .muted {{ color: #71717a; font-size: 13px; }}
</style></head><body>
  <h2>Trigger this workflow</h2>
  <p class="muted">{method} <code>{url}</code></p>
  <label for="payload">Payload (JSON)</label>
  <textarea id="payload">{sample}</textarea>
  <button onclick="send()">Send to webhook</button>
  <pre id="out" class="muted">Response will appear here.</pre>
  <script>
    async function send() {{
      const out = document.getElementById("out");
      out.textContent = "Sending...";
      try {{
        const body = JSON.parse(document.getElementById("payload").value);
        const resp = await fetch("{url}", {{ method: "{method}",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify(body) }});
        out.textContent = "HTTP " + resp.status + "\\n" + await resp.text();
      }} catch (e) {{ out.textContent = "Error: " + e.message; }}
    }}
  </script>
</body></html>"""

_NO_WEBHOOK = (
    "<!doctype html><html><body style='font-family:system-ui;background:#0a0a0f;"
    "color:#a1a1aa;padding:32px'>This workflow has no webhook trigger, so there "
    "is nothing to test with a form.</body></html>"
)


def build_test_form(workflow: dict[str, Any]) -> str:
    nodes, urls = webhook_nodes(workflow), webhook_urls(workflow)
    if not nodes or not urls:
        return _NO_WEBHOOK
    method = str(nodes[0].get("parameters", {}).get("httpMethod", "POST")).upper()
    sample = json.dumps({"message": "hello from FlowForge"}, indent=2)
    return _PAGE.format(url=urls[0], method=method if method != "GET" else "POST", sample=sample)
