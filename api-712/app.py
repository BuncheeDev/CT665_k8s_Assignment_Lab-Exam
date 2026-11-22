import html
import os
import socket
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

CSS = """
:root {
  --bg: #e6f4f6; --glass: rgba(255, 255, 255, 0.84); --glass-line: rgba(255, 255, 255, 0.95);
  --glass-ring: rgba(8, 145, 178, 0.16); --glass-shadow: 0 10px 30px rgba(15, 76, 92, 0.1), 0 1px 2px rgba(15, 76, 92, 0.06);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #fafdfe; --bg-input: #ffffff; --line: rgba(15, 60, 80, 0.1); --line-strong: rgba(5, 150, 105, 0.32);
  --text: #15303a; --text-dim: #587080; --title: #0a2430;
  --indigo: #4f46e5; --indigo-bg: #eef2ff; --indigo-line: rgba(79, 70, 229, 0.4);
  --row-hover: rgba(5, 150, 105, 0.07);
  --em-line: rgba(5, 150, 105, 0.28); --em-bg: rgba(236, 253, 245, 0.92); --em-text: #047857; --em-solid: #059669; --em-on: #ffffff;
  --mono: "Cascadia Mono", Consolas, "Noto Sans Mono", "Courier New", monospace;
  --thai: "Segoe UI", "Leelawadee UI", "Noto Sans Thai", Tahoma, system-ui, sans-serif;
  color-scheme: light;
}
[data-theme="dark"] {
  --bg: #050b14; --glass: rgba(9, 20, 34, 0.86); --glass-line: rgba(103, 232, 249, 0.12);
  --glass-ring: rgba(0, 0, 0, 0.25); --glass-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #0a1523; --bg-input: #08111d; --line: rgba(56, 189, 248, 0.14); --line-strong: rgba(56, 189, 248, 0.32);
  --text: #dbe7f4; --text-dim: #7f90a8; --title: #ffffff;
  --indigo: #818cf8; --indigo-bg: rgba(129, 140, 248, 0.14); --indigo-line: rgba(129, 140, 248, 0.45);
  --row-hover: rgba(52, 211, 153, 0.07);
  --em-line: rgba(52, 211, 153, 0.28); --em-bg: rgba(52, 211, 153, 0.1); --em-text: #6ee7b7; --em-solid: #059669; --em-on: #ecfdf5;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--thai); font-size: 13px; line-height: 1.5; min-height: 100dvh; display: flex; flex-direction: column; }
.mono { font-family: var(--mono); }
.scene-fallback { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; background: linear-gradient(180deg, #f8fcfe 0%, #eaf7f9 52%, #dff2f4 69.5%, #ffffff 70%, #e7f5f3 71%, #eef8f6 100%); }
.scene-fallback::before { content: ""; position: absolute; left: -40%; right: -40%; top: 70%; height: 60%; background-image: linear-gradient(rgba(14, 116, 144, 0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(14, 116, 144, 0.14) 1px, transparent 1px); background-size: 64px 64px; transform: perspective(360px) rotateX(62deg); transform-origin: 50% 0; }
[data-theme="dark"] .scene-fallback { background: linear-gradient(180deg, #03070f 0%, #06121c 60%, #0d3442 69.6%, #0a2a36 70.2%, #040d16 71%, #03080f 100%); }
.ws { position: relative; z-index: 1; width: 100%; max-width: 1120px; margin: 0 auto; padding: 12px 14px 28px; flex: 1; display: flex; flex-direction: column; gap: 14px; }
.hud { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 8px 14px; border-radius: 18px; background-color: var(--glass); background-image: var(--sheen); border: 1px solid var(--glass-line); box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow); -webkit-backdrop-filter: blur(12px) saturate(140%); backdrop-filter: blur(12px) saturate(140%); }
.hud-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.brand { font-size: 15px; font-weight: 700; color: var(--title); text-decoration: none; }
.nav { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.nav-link { padding: 3px 10px; border-radius: 7px; font-size: 12px; text-decoration: none; color: var(--text-dim); }
.nav-link:hover { background: var(--row-hover); color: var(--text); }
.nav-link.on { background: var(--em-solid); color: var(--em-on); font-weight: 600; }
.hud-right { display: flex; align-items: center; gap: 8px; }
.pill { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; border: 1px solid var(--em-line); border-radius: 999px; background: var(--em-bg); color: var(--em-text); font-size: 11.5px; white-space: nowrap; }
.icon-btn { display: inline-grid; place-items: center; width: 30px; height: 30px; padding: 0; border: 1px solid var(--line); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 14px; cursor: pointer; }
.stage-center {
  flex: 1; display: grid; place-items: center; min-height: 58vh;
  padding: 28px 20px; border-radius: 18px;
  border: 1px solid var(--glass-line); background-color: var(--glass); background-image: var(--sheen);
  box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow);
  text-align: center;
}
.hero-msg {
  margin: 14px 0; font-size: clamp(2.2rem, 6vw, 4.6rem); font-weight: 800;
  color: var(--title); line-height: 1.2; word-break: break-word;
}
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; border: 1px solid var(--em-line); border-radius: 999px; background: var(--em-bg); color: var(--em-text); font-size: 12px; }
.chip.live { border-color: var(--indigo-line); background: var(--indigo-bg); color: var(--indigo); }
.try-bar { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-top: 18px; }
.inp { padding: 5px 11px; border: 1px solid var(--line-strong); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 12.5px; min-width: 240px; }
.btn { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border: 1px solid var(--line-strong); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 12px; cursor: pointer; text-decoration: none; }
.btn.primary { background: var(--em-solid); border-color: var(--em-solid); color: var(--em-on); font-weight: 600; }
"""

THEME_JS = """
const KEY = 'hws.theme';
function initTheme() {
  let t = null; try { t = localStorage.getItem(KEY); } catch {}
  if (t !== 'dark' && t !== 'light') t = 'light';
  document.documentElement.dataset.theme = t;
  const b = document.getElementById('theme-btn'); if (b) b.textContent = t === 'dark' ? '☀' : '☾';
}
function toggleTheme() {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem(KEY, next); } catch {}
  const b = document.getElementById('theme-btn'); if (b) b.textContent = next === 'dark' ? '☀' : '☾';
}
initTheme();
"""


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw_path = self.path.split("?")[0]
        if raw_path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"api-712"}')
            return

        msg = raw_path
        if msg.startswith("/api-712/"):
            msg = msg[len("/api-712/"):]
        elif msg == "/api-712":
            msg = ""
        msg = urllib.parse.unquote(msg).strip("/")
        if not msg:
            msg = "สวัสดี Kubernetes 68130712"

        pod = socket.gethostname()
        node = os.environ.get("NODE_NAME", "k8s-node")

        page = f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>API-712 · {html.escape(msg)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="scene-fallback"></div>
  <div class="ws">
    <header class="hud">
      <div class="hud-left">
        <a class="brand" href="/">iam-712 · Kubernetes Portal</a>
        <nav class="nav">
          <a class="nav-link" href="/">Portal</a>
          <a class="nav-link" href="/research">Research</a>
          <a class="nav-link on" href="/api-712/{urllib.parse.quote(msg)}">API-712</a>
          <a class="nav-link" href="/arch">Architecture (Archify)</a>
          <a class="nav-link" href="http://admin.iam-712.com">Admin</a>
        </nav>
      </div>
      <div class="hud-right">
        <span class="pill mono">Pod: {html.escape(pod)}</span>
        <button id="theme-btn" class="icon-btn" type="button" onclick="toggleTheme()" title="สลับธีม">☾</button>
      </div>
    </header>

    <main class="stage-center">
      <div>
        <div style="display:flex;justify-content:center;gap:6px;flex-wrap:wrap;">
          <span class="chip">Deployment: <b class="mono">api-712</b></span>
          <span class="chip live">Node: <b class="mono">{html.escape(node)}</b></span>
        </div>
        <h1 class="hero-msg">{html.escape(msg)}</h1>
        <p class="mono" style="font-size:12px;opacity:0.75;">Path: /api-712/{html.escape(msg)}</p>
        <form class="try-bar" onsubmit="event.preventDefault(); const v=document.getElementById('m').value.trim(); if(v) location.href='/api-712/'+encodeURIComponent(v);">
          <input id="m" class="inp" type="text" value="{html.escape(msg)}" placeholder="พิมพ์ข้อความเพื่อทดสอบ...">
          <button class="btn primary" type="submit">แสดงข้อความ</button>
        </form>
      </div>
    </main>
  </div>
  <script>{THEME_JS}</script>
</body>
</html>"""
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), ApiHandler).serve_forever()
