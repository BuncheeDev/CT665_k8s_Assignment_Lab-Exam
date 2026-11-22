import html
import json
import os
import socket
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

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

DEFAULT_RESEARCH = {
    "title": "การออกแบบและประเมินระบบแสดงภาพกฎหมายสามมิติเชิงเครือข่ายประสาท (Neural of Law) เพื่อการสำรวจโครงสร้าง ลำดับศักดิ์ และความสัมพันธ์ของกฎหมายไทย กรณีศึกษากฎหมายภาษีอากร",
    "author": "นายมงคล เพชรแสวง (รหัสนักศึกษา 68130712)",
    "course": "วิชาสัมมนาทางวิศวกรรมคอมพิวเตอร์ — มหาวิทยาลัยธุรกิจบัณฑิตย์",
    "keywords": "Neural of Law, 3D Legal Visualization, WebAssembly, WebGL2, Thai Tax Law, Legal Knowledge Graph, RAG Agent",
    "summary": "กฎหมายไทยในปัจจุบันถูกจัดเก็บและเผยแพร่ในรูปแบบเอกสารตัวอักษรเรียงตามมาตรา ทำให้การสืบค้นผ่านเว็บไซต์หน่วยงานภาครัฐแสดงผลเป็นเพียงรายการเอกสารทีละหน้า..."
}


def k8s_get_cm():
    token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    if not os.path.exists(token_path):
        return {"portal": dict(DEFAULT_PORTAL), "research": dict(DEFAULT_RESEARCH)}
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
        url = "https://kubernetes.default.svc/api/v1/namespaces/default/configmaps/lab-exam-content"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        ctx = ssl.create_default_context(cafile=ca_path)
        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
            cm = json.loads(resp.read().decode("utf-8"))
            data = cm.get("data", {})
            portal = dict(DEFAULT_PORTAL)
            research = dict(DEFAULT_RESEARCH)
            if data.get("portal.json"):
                portal.update(json.loads(data["portal.json"]))
            if data.get("research.json"):
                research.update(json.loads(data["research.json"]))
            return {"portal": portal, "research": research}
    except Exception:
        return {"portal": dict(DEFAULT_PORTAL), "research": dict(DEFAULT_RESEARCH)}


def k8s_patch_cm(key, value_dict):
    token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    ca_path = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    with open(token_path, "r", encoding="utf-8") as f:
        token = f.read().strip()
    url = "https://kubernetes.default.svc/api/v1/namespaces/default/configmaps/lab-exam-content"
    payload = json.dumps({"data": {key: json.dumps(value_dict, ensure_ascii=False)}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/strategic-merge-patch+json",
        },
    )
    ctx = ssl.create_default_context(cafile=ca_path)
    with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
        return resp.status


CSS = """
:root {
  --bg: #e6f4f6; --glass: rgba(255, 255, 255, 0.84); --glass-strong: rgba(255, 255, 255, 0.94); --glass-line: rgba(255, 255, 255, 0.95);
  --glass-ring: rgba(8, 145, 178, 0.16); --glass-shadow: 0 10px 30px rgba(15, 76, 92, 0.1), 0 1px 2px rgba(15, 76, 92, 0.06);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #fafdfe; --bg-input: #ffffff; --line: rgba(15, 60, 80, 0.1); --line-strong: rgba(5, 150, 105, 0.32);
  --text: #15303a; --text-dim: #587080; --title: #0a2430;
  --danger: #dc2626; --indigo: #4f46e5; --indigo-bg: #eef2ff; --indigo-line: rgba(79, 70, 229, 0.4);
  --row-hover: rgba(5, 150, 105, 0.07);
  --em-line: rgba(5, 150, 105, 0.28); --em-bg: rgba(236, 253, 245, 0.92); --em-text: #047857; --em-solid: #059669; --em-on: #ffffff;
  --shadow: 0 10px 26px rgba(15, 60, 80, 0.14);
  --mono: "Cascadia Mono", Consolas, "Noto Sans Mono", "Courier New", monospace;
  --thai: "Segoe UI", "Leelawadee UI", "Noto Sans Thai", Tahoma, system-ui, sans-serif;
  color-scheme: light;
}
[data-theme="dark"] {
  --bg: #050b14; --glass: rgba(9, 20, 34, 0.86); --glass-strong: rgba(10, 22, 38, 0.95); --glass-line: rgba(103, 232, 249, 0.12);
  --glass-ring: rgba(0, 0, 0, 0.25); --glass-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  --sheen: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0) 40%);
  --bg-card: #0a1523; --bg-input: #08111d; --line: rgba(56, 189, 248, 0.14); --line-strong: rgba(56, 189, 248, 0.32);
  --text: #dbe7f4; --text-dim: #7f90a8; --title: #ffffff;
  --danger: #f87171; --indigo: #818cf8; --indigo-bg: rgba(129, 140, 248, 0.14); --indigo-line: rgba(129, 140, 248, 0.45);
  --row-hover: rgba(52, 211, 153, 0.07);
  --em-line: rgba(52, 211, 153, 0.28); --em-bg: rgba(52, 211, 153, 0.1); --em-text: #6ee7b7; --em-solid: #059669; --em-on: #ecfdf5;
  --shadow: 0 10px 28px rgba(0, 0, 0, 0.45); color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--thai); font-size: 13px; line-height: 1.5; min-height: 100dvh; }
.mono { font-family: var(--mono); }
.scene-fallback { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; background: linear-gradient(180deg, #f8fcfe 0%, #eaf7f9 52%, #dff2f4 69.5%, #ffffff 70%, #e7f5f3 71%, #eef8f6 100%); }
.scene-fallback::before { content: ""; position: absolute; left: -40%; right: -40%; top: 70%; height: 60%; background-image: linear-gradient(rgba(14, 116, 144, 0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(14, 116, 144, 0.14) 1px, transparent 1px); background-size: 64px 64px; transform: perspective(360px) rotateX(62deg); transform-origin: 50% 0; }
[data-theme="dark"] .scene-fallback { background: linear-gradient(180deg, #03070f 0%, #06121c 60%, #0d3442 69.6%, #0a2a36 70.2%, #040d16 71%, #03080f 100%); }
.ws { position: relative; z-index: 1; max-width: 1020px; margin: 0 auto; padding: 12px 14px 40px; display: flex; flex-direction: column; gap: 12px; }
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
.block { overflow: hidden; border: 1px solid var(--glass-line); border-radius: 16px; background-color: var(--glass); background-image: var(--sheen); box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow); }
.block-h { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; padding: 9px 14px; border-bottom: 1px solid var(--line); background: var(--em-bg); }
.block-t { font-size: 13px; font-weight: 700; color: var(--em-text); }
.selector-bar { display: flex; flex-wrap: wrap; gap: 10px; padding: 16px 20px; align-items: center; }
.tab-btn { padding: 8px 16px; border: 1px solid var(--line-strong); border-radius: 10px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
.tab-btn:hover { background: var(--em-bg); }
.tab-btn.on { background: var(--em-solid); border-color: var(--em-solid); color: var(--em-on); }
.form-pad { padding: 18px 20px; }
.field { display: grid; grid-template-columns: 140px 1fr; align-items: start; gap: 10px; margin-bottom: 12px; }
.field-l { text-align: right; font-size: 12.5px; color: var(--text-dim); padding-top: 6px; }
.inp, .ta { width: 100%; padding: 6px 10px; border: 1px solid var(--line-strong); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 12.5px; outline: none; }
.ta { min-height: 210px; line-height: 1.65; resize: vertical; }
.inp:focus, .ta:focus { border-color: var(--em-solid); box-shadow: 0 0 0 2px var(--em-bg); }
.btn { display: inline-flex; align-items: center; gap: 5px; padding: 5px 14px; border: 1px solid var(--line-strong); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 12.5px; cursor: pointer; text-decoration: none; }
.btn.primary { background: var(--em-solid); border-color: var(--em-solid); color: var(--em-on); font-weight: 600; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; padding-top: 8px; border-top: 1px solid var(--line); }
.fchip { position: fixed; right: 16px; bottom: 24px; z-index: 90; width: min(380px, calc(100vw - 24px)); min-height: 46px; display: none; align-items: center; gap: 8px; padding: 8px 14px; border: 1px solid var(--em-line); border-left: 4px solid var(--em-solid); border-radius: 12px; background: var(--glass-strong); box-shadow: var(--shadow); -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); font-size: 12.5px; }
.fchip.err { border-left-color: var(--danger); }
@media (max-width: 700px) { .field { grid-template-columns: 1fr; } .field-l { text-align: left; padding-top: 0; } }
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


class AdminHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"admin-712"}')
            return

        data = k8s_get_cm()
        p = data["portal"]
        r = data["research"]
        pod = socket.gethostname()
        node = os.environ.get("NODE_NAME", "k8s-node")

        page = f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Admin 712 · จัดการข้อมูล Portal & Research</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="scene-fallback"></div>
  <div class="ws">
    <header class="hud">
      <div class="hud-left">
        <a class="brand" href="/">admin.iam-712 · Control Panel</a>
        <nav class="nav">
          <a class="nav-link on" href="/">Admin Home</a>
          <a class="nav-link" href="http://www.iam-712.com/">Portal</a>
          <a class="nav-link" href="http://www.iam-712.com/research">Research</a>
          <a class="nav-link" href="http://www.iam-712.com/arch">Architecture (Archify)</a>
        </nav>
      </div>
      <div class="hud-right">
        <span class="pill mono">Pod: {html.escape(pod)} ({html.escape(node)})</span>
        <button id="theme-btn" class="icon-btn" type="button" onclick="toggleTheme()" title="สลับธีม">☾</button>
      </div>
    </header>

    <section class="block">
      <div class="block-h">
        <span class="block-t">เลือกส่วนที่ต้องการแก้ไขข้อมูล · Deployment: admin-712</span>
        <span class="pill">ConfigMap: lab-exam-content</span>
      </div>
      <div class="selector-bar">
        <button id="btn-portal" class="tab-btn on" type="button" onclick="selectTab('portal')">แก้ไขข้อมูล Portal (portal-712)</button>
        <button id="btn-research" class="tab-btn" type="button" onclick="selectTab('research')">แก้ไขข้อมูลงานวิจัย (app-research)</button>
      </div>
    </section>

    <section id="panel-portal" class="block">
      <div class="block-h">
        <span class="block-t">แก้ไขข้อมูลนักศึกษา (portal-712)</span>
        <a class="btn" href="http://www.iam-712.com/" target="_blank">เปิดดูหน้า Portal ↗</a>
      </div>
      <form class="form-pad" onsubmit="savePortal(event)">
        <div class="field"><label class="field-l">ชื่อ-นามสกุล (ไทย)</label><input id="p_name_th" class="inp" value="{html.escape(p['name_th'])}" required></div>
        <div class="field"><label class="field-l">ชื่อ-นามสกุล (EN)</label><input id="p_name_en" class="inp" value="{html.escape(p['name_en'])}" required></div>
        <div class="field"><label class="field-l">รหัสนักศึกษา</label><input id="p_student_id" class="inp mono" value="{html.escape(p['student_id'])}" required></div>
        <div class="field"><label class="field-l">อีเมล</label><input id="p_email" class="inp mono" value="{html.escape(p['email'])}"></div>
        <div class="field"><label class="field-l">หลักสูตร</label><input id="p_program" class="inp" value="{html.escape(p['program'])}"></div>
        <div class="field"><label class="field-l">สถาบัน</label><input id="p_university" class="inp" value="{html.escape(p['university'])}"></div>
        <div class="field"><label class="field-l">รายวิชา</label><input id="p_course" class="inp" value="{html.escape(p['course'])}"></div>
        <div class="field"><label class="field-l">คำแนะนำตัว</label><textarea id="p_bio" class="ta" style="min-height:90px;">{html.escape(p['bio'])}</textarea></div>
        <div class="actions">
          <button class="btn primary" type="submit">บันทึกข้อมูล Portal</button>
        </div>
      </form>
    </section>

    <section id="panel-research" class="block" style="display:none;">
      <div class="block-h">
        <span class="block-t">แก้ไขข้อมูลสรุปงานวิจัย (app-research)</span>
        <a class="btn" href="http://www.iam-712.com/research" target="_blank">เปิดดูหน้า Research ↗</a>
      </div>
      <form class="form-pad" onsubmit="saveResearch(event)">
        <div class="field"><label class="field-l">ชื่องานวิจัย</label><input id="r_title" class="inp" value="{html.escape(r['title'])}" required></div>
        <div class="field"><label class="field-l">ผู้วิจัย</label><input id="r_author" class="inp" value="{html.escape(r['author'])}" required></div>
        <div class="field"><label class="field-l">รายวิชา / สัมมนา</label><input id="r_course" class="inp" value="{html.escape(r['course'])}"></div>
        <div class="field"><label class="field-l">คำสำคัญ (Keywords)</label><input id="r_keywords" class="inp" value="{html.escape(r['keywords'])}"></div>
        <div class="field"><label class="field-l">สรุปงานวิจัย (300-500 คำ)</label><textarea id="r_summary" class="ta" required>{html.escape(r['summary'])}</textarea></div>
        <div class="actions">
          <button class="btn primary" type="submit">บันทึกข้อมูลงานวิจัย</button>
        </div>
      </form>
    </section>
  </div>

  <div id="toast" class="fchip"></div>

  <script>
    {THEME_JS}
    function selectTab(tab) {{
      document.getElementById('panel-portal').style.display = tab === 'portal' ? 'block' : 'none';
      document.getElementById('panel-research').style.display = tab === 'research' ? 'block' : 'none';
      document.getElementById('btn-portal').classList.toggle('on', tab === 'portal');
      document.getElementById('btn-research').classList.toggle('on', tab === 'research');
    }}
    function showToast(msg, isErr) {{
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.className = isErr ? 'fchip err' : 'fchip';
      t.style.display = 'flex';
      setTimeout(() => {{ t.style.display = 'none'; }}, 3500);
    }}
    async function savePortal(e) {{
      e.preventDefault();
      const payload = {{
        name_th: document.getElementById('p_name_th').value,
        name_en: document.getElementById('p_name_en').value,
        student_id: document.getElementById('p_student_id').value,
        short_id: document.getElementById('p_student_id').value.slice(-3),
        email: document.getElementById('p_email').value,
        program: document.getElementById('p_program').value,
        university: document.getElementById('p_university').value,
        course: document.getElementById('p_course').value,
        bio: document.getElementById('p_bio').value
      }};
      const res = await fetch('/api/save/portal', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(payload) }});
      if (res.ok) showToast('บันทึกข้อมูล Portal ลง Kubernetes ConfigMap เรียบร้อยแล้ว');
      else showToast('บันทึกข้อมูล Portal ไม่สำเร็จ', true);
    }}
    async function saveResearch(e) {{
      e.preventDefault();
      const payload = {{
        title: document.getElementById('r_title').value,
        author: document.getElementById('r_author').value,
        course: document.getElementById('r_course').value,
        keywords: document.getElementById('r_keywords').value,
        summary: document.getElementById('r_summary').value
      }};
      const res = await fetch('/api/save/research', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(payload) }});
      if (res.ok) showToast('บันทึกข้อมูลงานวิจัยลง Kubernetes ConfigMap เรียบร้อยแล้ว');
      else showToast('บันทึกข้อมูลงานวิจัยไม่สำเร็จ', true);
    }}
  </script>
</body>
</html>"""
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw)
            if self.path == "/api/save/portal":
                k8s_patch_cm("portal.json", payload)
            elif self.path == "/api/save/research":
                k8s_patch_cm("research.json", payload)
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), AdminHandler).serve_forever()
