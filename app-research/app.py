import html
import json
import os
import socket
import ssl
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

DEFAULT_RESEARCH = {
    "title": "การออกแบบและประเมินระบบแสดงภาพกฎหมายสามมิติเชิงเครือข่ายประสาท (Neural of Law) เพื่อการสำรวจโครงสร้าง ลำดับศักดิ์ และความสัมพันธ์ของกฎหมายไทย กรณีศึกษากฎหมายภาษีอากร",
    "author": "นายมงคล เพชรแสวง (รหัสนักศึกษา 68130712)",
    "course": "วิชาสัมมนาทางวิศวกรรมคอมพิวเตอร์ — มหาวิทยาลัยธุรกิจบัณฑิตย์",
    "keywords": "Neural of Law, 3D Legal Visualization, WebAssembly, WebGL2, Thai Tax Law, Legal Knowledge Graph, RAG Agent",
    "summary": (
        "กฎหมายไทยในปัจจุบันถูกจัดเก็บและเผยแพร่ในรูปแบบเอกสารตัวอักษรเรียงตามมาตรา ทำให้การสืบค้นผ่านเว็บไซต์หน่วยงานภาครัฐแสดงผลเป็นเพียงรายการเอกสารทีละหน้า "
        "ไม่สะท้อนให้เห็นว่ากฎหมายแต่ละฉบับอยู่ระดับใดของลำดับศักดิ์ สังกัดหน่วยงานใด หรือมีความสัมพันธ์เชิงให้อำนาจ แก้ไข ยกเลิก และอ้างอิงต่อกันอย่างไร "
        "งานวิจัยนี้จึงนำเสนอการออกแบบและประเมินระบบ Neural of Law ซึ่งเป็นการแสดงภาพกฎหมายสามมิติเชิงเครือข่ายประสาท โดยใช้กฎหมายภาษีอากรตามประมวลรัษฎากรเป็นกรณีศึกษา\n\n"
        "การวิจัยดำเนินตามแนวทาง Design Science Research (DSR) แบ่งออกเป็น 4 องค์ประกอบหลัก ได้แก่ "
        "1) การเข้ารหัสภาพ (Visual Encoding) และแบบจำลองข้อมูล 7 ระดับ ที่แปลงลำดับศักดิ์ของกฎหมายไทยเป็นความสูงในแกนตั้ง แปลงสังกัดกระทรวงและกรมเป็นการจัดกลุ่มเชิงพื้นที่ "
        "แปลงความสำคัญจากค่า PageRank เป็นขนาดโหนด และแปลงความสัมพันธ์ทางกฎหมาย 11 ชนิดเป็นเส้นเชื่อมที่มีทิศทาง น้ำหนักแบบ noisy-or และความใหม่ของข้อมูล "
        "2) แกนประมวลผลสมรรถนะสูงที่พัฒนาด้วยภาษา Rust คอมไพล์เป็น WebAssembly ทำงานร่วมกับการเรนเดอร์ผ่าน WebGL2 บนเว็บเบราว์เซอร์ทั่วไป "
        "ทำให้สามารถวาดคลังกฎหมายขนาดใหญ่จำนวน 2,372 โหนด และเส้นเชื่อมความสัมพันธ์ 5,867 เส้น ได้อย่างลื่นไหลด้วยคำสั่งวาดเพียง 3 คำสั่ง "
        "3) การประเมินเชิงประจักษ์กับผู้ใช้งาน เพื่อเปรียบเทียบความเร็วและความถูกต้องในการตอบคำถามเชิงโครงสร้างระหว่างระบบภาพสามมิติกับระบบสืบค้นแบบรายการ "
        "และ 4) การออกแบบบรรณารักษ์กฎหมาย (Legal Librarian Agent) ซึ่งเป็นซอฟต์แวร์เอเจนต์แบบค้นก่อนตอบ (Retrieval-First) ที่มีเครื่องมืออ่านคลังข้อมูลอย่างเดียว 3 ชนิด "
        "สามารถตอบคำถามพร้อมอ้างอิงเลขมาตราที่ตรวจสอบย้อนกลับได้ และนำทางมุมกล้องบนหน้าจอสามมิติไปยังโหนดที่เกี่ยวข้องโดยตรง\n\n"
        "ผลลัพธ์จากงานวิจัยนี้แสดงให้เห็นว่าการแปลงโครงสร้างกฎหมายจากตัวอักษรเป็นพื้นที่สามมิติที่มีความหมายทางกฎหมาย ช่วยลดภาระการเปิดเอกสารข้ามไปมา "
        "เพิ่มความเข้าใจภาพรวมลำดับศักดิ์และเครือข่ายการอ้างอิงของกฎหมายภาษีอากรไทยได้อย่างมีประสิทธิภาพ พร้อมเป็นต้นแบบสำหรับขยายผลสู่กฎหมายสาขาอื่นในอนาคต"
    )
}


def load_research_data():
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
                raw = cm.get("data", {}).get("research.json")
                if raw:
                    data = dict(DEFAULT_RESEARCH)
                    data.update(json.loads(raw))
                    return data
        except Exception:
            pass
    return dict(DEFAULT_RESEARCH)


from http.server import BaseHTTPRequestHandler  # noqa

# Reuse same HWS tokens
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
  --ring2: #0891b2;
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
  --ring2: #22d3ee; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--thai); font-size: 13px; line-height: 1.5; min-height: 100dvh; }
.mono { font-family: var(--mono); }
.scene-fallback { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; background: linear-gradient(180deg, #f8fcfe 0%, #eaf7f9 52%, #dff2f4 69.5%, #ffffff 70%, #e7f5f3 71%, #eef8f6 100%); }
.scene-fallback::before { content: ""; position: absolute; left: -40%; right: -40%; top: 70%; height: 60%; background-image: linear-gradient(rgba(14, 116, 144, 0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(14, 116, 144, 0.14) 1px, transparent 1px); background-size: 64px 64px; transform: perspective(360px) rotateX(62deg); transform-origin: 50% 0; }
[data-theme="dark"] .scene-fallback { background: linear-gradient(180deg, #03070f 0%, #06121c 60%, #0d3442 69.6%, #0a2a36 70.2%, #040d16 71%, #03080f 100%); }
.ws { position: relative; z-index: 1; max-width: 1120px; margin: 0 auto; padding: 12px 14px 28px; display: flex; flex-direction: column; gap: 12px; }
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
.body-pad { padding: 20px; }
.r-title { margin: 0 0 6px; font-size: 19px; font-weight: 700; color: var(--title); line-height: 1.4; }
.r-meta { margin: 0 0 12px; font-size: 12.5px; color: var(--text-dim); }
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.chip { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; border: 1px solid var(--em-line); border-radius: 999px; background: var(--em-bg); color: var(--em-text); font-size: 12px; }
.chip.live { border-color: var(--indigo-line); background: var(--indigo-bg); color: var(--indigo); }
.summary-card { padding: 16px 18px; border-radius: 12px; border: 1px solid var(--line); background: var(--bg-card); font-size: 14px; line-height: 1.75; white-space: pre-line; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }
.kpi { padding: 12px 14px; border: 1px solid var(--glass-line); border-radius: 14px; background-color: var(--glass); background-image: linear-gradient(90deg, var(--em-solid), var(--ring2)), var(--sheen); background-size: 100% 2px, auto; background-repeat: no-repeat; box-shadow: 0 0 0 1px var(--glass-ring), var(--glass-shadow); }
.kpi-l { font-size: 11.5px; color: var(--text-dim); }
.kpi-v { margin-top: 2px; font-size: 22px; font-weight: 700; color: var(--title); }
.kpi-s { font-size: 11px; color: var(--em-text); }
.btn { display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border: 1px solid var(--line-strong); border-radius: 9px; background: var(--bg-input); color: var(--text); font: inherit; font-size: 12px; cursor: pointer; text-decoration: none; }
.btn.primary { background: var(--em-solid); border-color: var(--em-solid); color: var(--em-on); font-weight: 600; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; padding: 14px 20px; border-top: 1px solid var(--line); background: var(--bg-card); }
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


class ResearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"app-research"}')
            return

        d = load_research_data()
        pod = socket.gethostname()
        node = os.environ.get("NODE_NAME", "k8s-node")
        kw_chips = "".join(f'<span class="chip">{html.escape(k.strip())}</span>' for k in d["keywords"].split(",") if k.strip())
        page = f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Research · {html.escape(d['title'])}</title>
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
          <a class="nav-link on" href="/research">Research</a>
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

    <section class="kpi-grid">
      <div class="kpi"><div class="kpi-l">โหนดกฎหมายในระบบ</div><div class="kpi-v">2,372</div><div class="kpi-s">WebGL2 + WebAssembly</div></div>
      <div class="kpi"><div class="kpi-l">เส้นเชื่อมความสัมพันธ์</div><div class="kpi-v">5,867</div><div class="kpi-s">11 ชนิดความสัมพันธ์</div></div>
      <div class="kpi"><div class="kpi-l">ลำดับศักดิ์กฎหมาย</div><div class="kpi-v">7 ระดับ</div><div class="kpi-s">กรณีศึกษาประมวลรัษฎากร</div></div>
      <div class="kpi"><div class="kpi-l">คำสั่งวาด WebGL2</div><div class="kpi-v">3 Draws</div><div class="kpi-s">Node: {html.escape(node)}</div></div>
    </section>

    <section class="block">
      <div class="block-h">
        <span class="block-t">สรุปงานวิจัยวิชาสัมมนา · Deployment: app-research</span>
        <span class="pill">ความยาว ~300–500 คำ</span>
      </div>
      <div class="body-pad">
        <h1 class="r-title">{html.escape(d['title'])}</h1>
        <p class="r-meta">{html.escape(d['author'])} · {html.escape(d['course'])}</p>
        <div class="chip-row">
          <span class="chip live">Node: <b class="mono">{html.escape(node)}</b></span>
          {kw_chips}
        </div>
        <div class="summary-card">{html.escape(d['summary'])}</div>
      </div>
      <div class="actions">
        <a class="btn primary" href="http://admin.iam-712.com">แก้ไขข้อมูลงานวิจัยผ่าน Admin</a>
        <a class="btn" href="/">กลับหน้า Portal</a>
        <a class="btn" href="/arch">ดูโครงสร้างระบบ (Archify)</a>
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
    HTTPServer(("0.0.0.0", PORT), ResearchHandler).serve_forever()
