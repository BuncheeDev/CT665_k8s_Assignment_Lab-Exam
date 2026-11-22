import html
import json
import os
import socket
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_PORTAL = {
    "name_th": "นายมงคล เพชรแสวง",
    "name_en": "Mr. Mongkol Petsawang",
    "student_id": "68130712",
    "short_id": "712",
    "program": "วิศวกรรมศาสตรมหาบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์",
    "university": "วิทยาลัยวิศวกรรมศาสตร์และเทคโนโลยี มหาวิทยาลัยธุรกิจบัณฑิตย์ (DPU)",
    "course": "CT665 คูเบอร์เนเทสและเซิร์ฟเวอร์เลส (Lab Exam)",
    "email": "68130712@dpu.ac.th",
    "bio": "นักศึกษาปริญญาโท สาขาวิชาวิศวกรรมคอมพิวเตอร์ มุ่งเน้นการออกแบบระบบคลาวด์เนทีฟ Kubernetes Microservices และการแสดงผลข้อมูลกฎหมายสามมิติ (Neural of Law)"
}


def load_portal_data():
    token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    if os.path.exists(token_path):
        try:
            with open(token_path, "r", encoding="utf-8") as f:
                token = f.read().strip()
            url = "https://kubernetes.default.svc/api/v1/namespaces/default/configmaps/lab-exam-content"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
            ctx = ssl.create_default_context(cafile=ca_path)
            with urllib.request.urlopen(req, context=ctx, timeout=2) as resp:
                cm = json.loads(resp.read().decode("utf-8"))
                raw = cm.get("data", {}).get("portal.json")
                if raw:
                    data = dict(DEFAULT_PORTAL)
                    data.update(json.loads(raw))
                    return data
        except Exception:
            pass
    return dict(DEFAULT_PORTAL)


HWS_CSS = """
:root {
  --bg: #e6f4f6;
  --glass: rgba(255, 255, 255, 0.84);
  --glass-strong: rgba(255, 255, 255, 0.94);
  --glass-line: rgba(255, 255, 255, 0.95);
  --glass-ring: rgba(8, 145, 178, 0.16);
  --glass-shadow: 0 10px 30px rgba(15, 76, 92, 0.1), 0 1px 2px rgba(15, 76, 92, 0.06);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #fafdfe;
  --bg-head: #eefaf5;
  --bg-input: #ffffff;
  --line: rgba(15, 60, 80, 0.1);
  --line-strong: rgba(5, 150, 105, 0.32);
  --text: #15303a;
  --text-dim: #587080;
  --title: #0a2430;
  --nil: #c3d3da;
  --danger: #dc2626;  --danger-bg: #fef2f2;  --danger-line: rgba(220, 38, 38, 0.34);
  --amber: #b45309;   --amber-bg: #fffbeb;   --amber-line: rgba(217, 119, 6, 0.4);
  --indigo: #4f46e5;  --indigo-bg: #eef2ff;  --indigo-line: rgba(79, 70, 229, 0.4);
  --ok: #059669;
  --row-hover: rgba(5, 150, 105, 0.07);
  --row-odd: rgba(15, 60, 80, 0.028);
  --em-line: rgba(5, 150, 105, 0.28);
  --em-bg: rgba(236, 253, 245, 0.92);
  --em-text: #047857;
  --em-solid: #059669;
  --em-on: #ffffff;
  --shadow: 0 10px 26px rgba(15, 60, 80, 0.14);
  --ring1: #059669; --ring2: #0891b2; --ring3: #4f46e5; --ring4: #2563eb;
  --mono: "Cascadia Mono", Consolas, "Noto Sans Mono", "Courier New", monospace;
  --thai: "Segoe UI", "Leelawadee UI", "Noto Sans Thai", Tahoma, system-ui, sans-serif;
  color-scheme: light;
}
[data-theme="dark"] {
  --bg: #050b14;
  --glass: rgba(9, 20, 34, 0.86);
  --glass-strong: rgba(10, 22, 38, 0.95);
  --glass-line: rgba(103, 232, 249, 0.12);
  --glass-ring: rgba(0, 0, 0, 0.25);
  --glass-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #0a1523;
  --bg-head: #0f1d2e;
  --bg-input: #08111d;
  --line: rgba(56, 189, 248, 0.14);
  --line-strong: rgba(56, 189, 248, 0.32);
  --text: #dbe7f4;
  --text-dim: #7f90a8;
  --title: #ffffff;
  --nil: #2c3a52;
  --danger: #f87171;  --danger-bg: rgba(248, 113, 113, 0.12);  --danger-line: rgba(248, 113, 113, 0.42);
  --amber: #fcd34d;   --amber-bg: rgba(251, 191, 36, 0.12);    --amber-line: rgba(251, 191, 36, 0.42);
  --indigo: #818cf8;  --indigo-bg: rgba(129, 140, 248, 0.14);  --indigo-line: rgba(129, 140, 248, 0.45);
  --ok: #34d399;
  --row-hover: rgba(52, 211, 153, 0.07);
  --row-odd: rgba(148, 163, 184, 0.035);
  --em-line: rgba(52, 211, 153, 0.28);
  --em-bg: rgba(52, 211, 153, 0.1);
  --em-text: #6ee7b7;
  --em-solid: #059669;
  --em-on: #ecfdf5;
  --shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
  --ring1: #34d399; --ring2: #22d3ee; --ring3: #818cf8; --ring4: #60a5fa;
  color-scheme: dark;
}
* { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: var(--line-strong) transparent; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: var(--thai); font-size: 13px; line-height: 1.5;
  -webkit-font-smoothing: antialiased; min-height: 100dvh;
}
.mono { font-family: var(--mono); }
.muted { color: var(--text-dim); }
.scene-fallback {
  position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none;
  background: linear-gradient(180deg, #f8fcfe 0%, #eaf7f9 52%, #dff2f4 69.5%, #ffffff 70%, #e7f5f3 71%, #eef8f6 100%);
}
.scene-fallback::before {
  content: ""; position: absolute; left: -40%; right: -40%; top: 70%; height: 60%;
  background-image: linear-gradient(rgba(14, 116, 144, 0.14) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(14, 116, 144, 0.14) 1px, transparent 1px);
  background-size: 64px 64px;
  transform: perspective(360px) rotateX(62deg);
  transform-origin: 50% 0;
}
[data-theme="dark"] .scene-fallback {
  background: linear-gradient(180deg, #03070f 0%, #06121c 60%, #0d3442 69.6%, #0a2a36 70.2%, #040d16 71%, #03080f 100%);
}
.ws { position: relative; z-index: 1; max-width: 1120px; margin: 0 auto; padding: 12px 14px 28px; display: flex; flex-direction: column; gap: 12px; }
.hud {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
  padding: 8px 14px; border-radius: 18px;
  background-color: var(--glass); background-image: var(--sheen);
  border: 1px solid var(--glass-line);
  box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow);
  -webkit-backdrop-filter: blur(12px) saturate(140%); backdrop-filter: blur(12px) saturate(140%);
}
.hud-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.brand { font-size: 15px; font-weight: 700; color: var(--title); text-decoration: none; }
.nav { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.nav-link {
  padding: 3px 10px; border-radius: 7px; font-size: 12px; text-decoration: none;
  color: var(--text-dim); border: 1px solid transparent;
}
.nav-link:hover { background: var(--row-hover); color: var(--text); }
.nav-link.on { background: var(--em-solid); color: var(--em-on); font-weight: 600; }
.hud-right { display: flex; align-items: center; gap: 8px; }
.pill {
  display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px;
  border: 1px solid var(--em-line); border-radius: 999px;
  background: var(--em-bg); color: var(--em-text); font-size: 11.5px; white-space: nowrap;
}
.btn {
  display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px;
  border: 1px solid var(--line-strong); border-radius: 9px;
  background: var(--bg-input); color: var(--text);
  font: inherit; font-size: 12px; cursor: pointer; text-decoration: none; white-space: nowrap;
}
.btn:hover { background: var(--em-bg); border-color: var(--em-line); }
.btn.primary { background: var(--em-solid); border-color: var(--em-solid); color: var(--em-on); font-weight: 600; }
.btn.primary:hover { filter: brightness(1.08); background: var(--em-solid); }
.icon-btn {
  display: inline-grid; place-items: center; width: 30px; height: 30px; padding: 0;
  border: 1px solid var(--line); border-radius: 9px; background: var(--bg-input);
  color: var(--text); font: inherit; font-size: 14px; cursor: pointer;
}
.icon-btn:hover { background: var(--row-hover); }
.block {
  overflow: hidden; border: 1px solid var(--glass-line); border-radius: 16px;
  background-color: var(--glass); background-image: var(--sheen);
  box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow);
}
.block-h {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
  padding: 9px 14px; border-bottom: 1px solid var(--line); background: var(--em-bg);
}
.block-t { font-size: 13px; font-weight: 700; color: var(--em-text); }
.profile-grid {
  display: grid; grid-template-columns: 220px 1fr; gap: 20px; padding: 20px; align-items: center;
}
.avatar-wrap {
  width: 210px; height: 210px; border-radius: 16px; overflow: hidden;
  border: 2px solid var(--em-line); box-shadow: var(--glass-shadow); margin: 0 auto;
}
.avatar-wrap img { width: 100%; height: 100%; object-fit: cover; display: block; }
.title-lg { margin: 0 0 4px; font-size: 22px; font-weight: 700; color: var(--title); }
.subtitle { margin: 0 0 12px; font-size: 13px; color: var(--text-dim); }
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.chip {
  display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px;
  border: 1px solid var(--em-line); border-radius: 999px;
  background: var(--em-bg); color: var(--em-text); font-size: 12px;
}
.chip.live { border-color: var(--indigo-line); background: var(--indigo-bg); color: var(--indigo); }
.bio-box {
  padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line);
  background: var(--bg-card); font-size: 13px; line-height: 1.65;
}
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }
.kpi {
  padding: 12px 14px; overflow: hidden; border: 1px solid var(--glass-line); border-radius: 14px;
  background-color: var(--glass);
  background-image: linear-gradient(90deg, var(--em-solid), var(--ring2)), var(--sheen);
  background-size: 100% 2px, auto; background-repeat: no-repeat;
  box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow);
}
.kpi-l { font-size: 11.5px; color: var(--text-dim); }
.kpi-v { margin-top: 3px; font-size: 18px; font-weight: 700; color: var(--title); }
.kpi-s { margin-top: 2px; font-size: 11px; color: var(--em-text); }
.actions { display: flex; flex-wrap: wrap; gap: 8px; padding: 14px 20px; border-top: 1px solid var(--line); background: var(--bg-card); }
@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; text-align: center; }
  .chip-row { justify-content: center; }
}
"""

THEME_JS = """
const KEY = 'hws.theme';
function initTheme() {
  let t = null;
  try { t = localStorage.getItem(KEY); } catch {}
  if (t !== 'dark' && t !== 'light') t = 'light';
  document.documentElement.dataset.theme = t;
  updateThemeBtn(t);
}
function toggleTheme() {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem(KEY, next); } catch {}
  updateThemeBtn(next);
}
function updateThemeBtn(t) {
  const b = document.getElementById('theme-btn');
  if (b) b.textContent = t === 'dark' ? '☀' : '☾';
}
initTheme();
"""


class PortalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"portal-712"}')
            return

        if path == "/avatar.jpg":
            img_path = os.path.join(BASE_DIR, "avatar.jpg")
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        if path == "/arch":
            arch_path = os.path.join(BASE_DIR, "architecture.html")
            if os.path.exists(arch_path):
                with open(arch_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        d = load_portal_data()
        pod = socket.gethostname()
        node = os.environ.get("NODE_NAME", "k8s-node")
        page = f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Portal {html.escape(d['short_id'])} · {html.escape(d['name_th'])}</title>
  <style>{HWS_CSS}</style>
</head>
<body>
  <div class="scene-fallback"></div>
  <div class="ws">
    <header class="hud">
      <div class="hud-left">
        <a class="brand" href="/">iam-712 · Kubernetes Portal</a>
        <nav class="nav">
          <a class="nav-link on" href="/">Portal</a>
          <a class="nav-link" href="/research">Research</a>
          <a class="nav-link" href="/api-712/CT665%20Lab%20Exam%2068130712">API-712</a>
          <a class="nav-link" href="/arch">Architecture (Archify)</a>
          <a class="nav-link" href="http://admin.iam-712.com">Admin</a>
        </nav>
      </div>
      <div class="hud-right">
        <span class="pill mono">Pod: {html.escape(pod)}</span>
        <button id="theme-btn" class="icon-btn" type="button" onclick="toggleTheme()" title="สลับธีม">☾</button>
      </div>
    </header>

    <section class="block">
      <div class="block-h">
        <span class="block-t">ข้อมูลนักศึกษา · Deployment: portal-712</span>
        <span class="pill">รหัส {html.escape(d['student_id'])}</span>
      </div>
      <div class="profile-grid">
        <div class="avatar-wrap">
          <img src="/avatar.jpg" alt="Student Photo">
        </div>
        <div>
          <h1 class="title-lg">{html.escape(d['name_th'])}</h1>
          <p class="subtitle">{html.escape(d['name_en'])} · <span class="mono">{html.escape(d['email'])}</span></p>
          <div class="chip-row">
            <span class="chip">รหัสนักศึกษา: <b class="mono">{html.escape(d['student_id'])}</b></span>
            <span class="chip live">Node: <b class="mono">{html.escape(node)}</b></span>
            <span class="chip">{html.escape(d['course'])}</span>
          </div>
          <div class="bio-box">
            <div><strong>หลักสูตร:</strong> {html.escape(d['program'])}</div>
            <div><strong>สถาบัน:</strong> {html.escape(d['university'])}</div>
            <div style="margin-top:6px;">{html.escape(d['bio'])}</div>
          </div>
        </div>
      </div>
      <div class="actions">
        <a class="btn primary" href="/research">อ่านสรุปงานวิจัย (app-research)</a>
        <a class="btn" href="/api-712/Hello%20Kubernetes%2068130712">ทดสอบ API-712</a>
        <a class="btn" href="/arch">ดูโครงสร้างระบบ (Archify)</a>
        <a class="btn" href="http://admin.iam-712.com">เปิดหน้า Admin แก้ไขข้อมูล</a>
      </div>
    </section>

    <section class="kpi-grid">
      <div class="kpi">
        <div class="kpi-l">Deployment</div>
        <div class="kpi-v mono">portal-712</div>
        <div class="kpi-s">www.iam-712.com / www.id-712.com</div>
      </div>
      <div class="kpi">
        <div class="kpi-l">Kubernetes Node</div>
        <div class="kpi-v mono">{html.escape(node)}</div>
        <div class="kpi-s">3-Node Cluster (minikube + m02 + m03)</div>
      </div>
      <div class="kpi">
        <div class="kpi-l">Shared State</div>
        <div class="kpi-v mono">ConfigMap</div>
        <div class="kpi-s">lab-exam-content (Real-time Sync)</div>
      </div>
    </section>
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
    HTTPServer(("0.0.0.0", PORT), PortalHandler).serve_forever()
