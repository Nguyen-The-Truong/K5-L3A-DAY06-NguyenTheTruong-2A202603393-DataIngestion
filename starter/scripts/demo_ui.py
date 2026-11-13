"""Local web UI for the retrieval demo (standard library only, no extra install).

  cd starter
  python -X utf8 scripts/demo_ui.py          # then open http://127.0.0.1:8000
Needs the index built by `python -X utf8 -m src.run`. Binds to localhost only.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.embeddings import MyEmbedder  # noqa: E402
from src.run import CHROMA_DIR, CONFIG, MODEL  # noqa: E402
from src.store import ChromaStore  # noqa: E402

PORT = 8000
EMB = MyEmbedder(MODEL)
STORE = ChromaStore(CHROMA_DIR, EMB.dimensions)
if STORE.count("B") == 0:
    raise SystemExit("Index is empty. Run `python -X utf8 -m src.run` first.")

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Retrieval Demo</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--text:#1d2530;--muted:#667085;--line:#e1e5ea;--accent:#2457c5;--hit:#e8f0ff}
@media(prefers-color-scheme:dark){:root{--bg:#14171c;--card:#1d222a;--text:#e8ecf1;--muted:#98a2b3;--line:#2d343e;--accent:#7aa2ff;--hit:#222c42}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 48px}h1{font-size:20px;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 18px}form{display:grid;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.row{display:flex;gap:10px;flex-wrap:wrap}label{font-size:12px;color:var(--muted);display:grid;gap:3px}
input,select,button{font:inherit;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--text)}
input[type=text]{width:100%}button{background:var(--accent);color:#fff;border:0;cursor:pointer;padding:9px 18px}
#note{color:var(--muted);font-size:13px;margin:10px 2px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:10px}
.meta{display:flex;gap:8px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin-bottom:6px}.tag{background:var(--hit);color:var(--accent);padding:1px 8px;border-radius:99px}
.txt{white-space:pre-wrap;word-break:break-word}
</style></head><body><main>
<h1>Data ingestion retrieval demo</h1>
<p class="sub">Principles of Data Science (OpenStax), chapters 2-3. Top-3 chunks per strategy; embedding intfloat/multilingual-e5-small, Chroma, cosine.</p>
<form id="f"><label>Question<input type="text" id="q" placeholder="e.g. What is stratified sampling?" required></label>
<div class="row"><label>Strategy<select id="s"><option value="A">A: fixed 500/50</option><option value="B">B: paragraph</option><option value="C" selected>C: paragraph + filter</option></select></label>
<label>Section filter (C only)<select id="sec"><option value="">none</option></select></label>
<label>Chapter filter (C only)<select id="ch"><option value="">none</option><option>2</option><option>3</option></select></label>
<label>&nbsp;<button>Search</button></label></div></form>
<div id="note"></div><div id="out"></div></main>
<script>
const secs=["2.0","2.1","2.2","2.3","2.4","2.5","3.0","3.1","3.2","3.3","3.4","3.5"];
const sec=document.getElementById("sec");secs.forEach(s=>{const o=document.createElement("option");o.textContent=s;sec.appendChild(o)});
document.getElementById("f").addEventListener("submit",async e=>{e.preventDefault();
const p=new URLSearchParams({q:q.value,strategy:s.value,section:sec.value,chapter:ch.value});
const note=document.getElementById("note"),out=document.getElementById("out");note.textContent="Searching...";out.textContent="";
try{const r=await fetch("/search?"+p);const d=await r.json();if(d.error)throw new Error(d.error);
note.textContent="Strategy "+d.strategy+" | filter: "+(d.filter?JSON.stringify(d.filter):"none")+(d.ignored?" (A and B ignore filters)":"");
d.hits.forEach((h,i)=>{const c=document.createElement("div");c.className="card";
const m=document.createElement("div");m.className="meta";
[["#"+(i+1)],["score "+h.score.toFixed(3)],["page "+h.page],["section "+h.section+" "+h.section_title],[h.chunk_id]].forEach((t,j)=>{const sp=document.createElement("span");sp.textContent=t[0];if(j<3)sp.className="tag";m.appendChild(sp)});
const t=document.createElement("div");t.className="txt";t.textContent=h.text;c.append(m,t);out.appendChild(c)})}
catch(err){note.textContent="Error: "+err.message}});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        if url.path == "/":
            return self._send(200, PAGE, "text/html")
        if url.path != "/search":
            return self._send(404, "not found", "text/plain")
        qs = parse_qs(url.query)
        get = lambda k: (qs.get(k, [""])[0]).strip()  # noqa: E731
        try:
            question, strategy = get("q"), get("strategy") or "C"
            if not question or strategy not in CONFIG:
                raise ValueError("need a question and strategy A, B or C")
            flt = {}
            if get("section"):
                flt["section"] = get("section")
            if get("chapter"):
                flt["chapter"] = int(get("chapter"))
            cfg = CONFIG[strategy]
            use = flt if (cfg["filter"] and flt) else None
            hits = STORE.search(cfg["collection"], EMB.embed_query(question), 3, use)
            body = {"strategy": strategy, "filter": use, "ignored": bool(flt and not cfg["filter"]),
                    "hits": [{"score": h["score"], "page": h["metadata"]["page"],
                              "section": h["metadata"]["section"], "section_title": h["metadata"]["section_title"],
                              "chunk_id": h["chunk_id"], "text": h["text"]} for h in hits]}
            self._send(200, json.dumps(body), "application/json")
        except Exception as exc:  # report to the page instead of failing silently
            self._send(400, json.dumps({"error": str(exc)}), "application/json")

    def log_message(self, *args):  # keep the console quiet
        pass


if __name__ == "__main__":
    print(f"Open http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
