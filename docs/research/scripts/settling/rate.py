#!/usr/bin/env python3
"""Blinded pairwise rating for the settling experiment (spec: 2026-09-05-settling-experiment.md, Q).

    python3 rate.py            serve on http://localhost:8765/

The schedule is derived from manifest.json with a fixed seed: within each brief, across arms only,
every build in exactly three pairs (each arm pair twice, on matched or crossed seeds), left/right
randomised. Only pairs whose two builds exist are served. Judgments append to judgments.jsonl as
{pair, left, right, choice, ms, at}. The page never sees arms; ids are random.
"""
import json, os, random, itertools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
WS = os.environ.get("SETTLING_WS") or os.path.join(REPO, "figma-design-workspace/settling")
MANIFEST = os.path.join(WS, "manifest.json")
JUDGMENTS = os.path.join(WS, "judgments.jsonl")
EVALS = os.path.join(REPO, "evals/evals.json")
PORT = 8765
ARMS = ["none", "v1.1", "v2.0", "v2.1"]


def brief_text(ev):
    if ev == 11:
        return ("Design the page where a regional bus operator's fleet manager compares three tyre suppliers' quotes on the same "
                "criteria — price per axle, lead time, warranty, on-site fitting — and picks one. Single HTML file with realistic data.")
    return next(e["prompt"] for e in json.load(open(EVALS))["evals"] if e["id"] == ev)


def schedule():
    """Deterministic pair list over the whole manifest."""
    cells = json.load(open(MANIFEST))["cells"]
    rng = random.Random(20260905)
    pairs = []
    briefs = sorted({c["brief"] for c in cells}, key=lambda b: min(c["wave"] for c in cells if c["brief"] == b))
    for b in briefs:
        bc = [c for c in cells if c["brief"] == b]
        seeds = sorted({c["seedLabel"] for c in bc})
        by = {(c["arm"], c["seedLabel"]): c for c in bc}
        for a1, a2 in itertools.combinations(ARMS, 2):
            if len(seeds) == 1:
                combos = [(seeds[0], seeds[0])]
            else:
                combos = [("A", "A"), ("B", "B")] if rng.random() < 0.5 else [("A", "B"), ("B", "A")]
            for s1, s2 in combos:
                if (a1, s1) not in by or (a2, s2) not in by:
                    continue
                x, y = by[(a1, s1)], by[(a2, s2)]
                left, right = (x, y) if rng.random() < 0.5 else (y, x)
                pairs.append({"pair": f"{left['id']}-{right['id']}", "brief": b, "eval": x["eval"], "left": left["id"], "right": right["id"]})
    rng.shuffle(pairs)
    return pairs


def built(i):
    return os.path.exists(os.path.join(WS, "builds", i, "index.html")) and os.path.exists(os.path.join(WS, "builds", i, "shot-full.png"))


def judged():
    if not os.path.exists(JUDGMENTS):
        return {}
    out = {}
    for line in open(JUDGMENTS):
        line = line.strip()
        if line:
            j = json.loads(line); out[j["pair"]] = j
    return out


PAGE = r"""<!doctype html><meta charset=utf-8><title>settling — pairwise</title>
<style>
body{margin:0;font:14px/1.45 system-ui;color:#222;background:#f4f4f4}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:10px 16px;z-index:5;display:flex;gap:16px;align-items:baseline}
header b{font-size:15px} header .brief{flex:1;color:#333} header .n{color:#777;white-space:nowrap}
main{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.side{background:#fff;border:1px solid #ccc;display:flex;flex-direction:column;height:calc(100vh - 150px)}
.side .bar{display:flex;justify-content:space-between;align-items:center;padding:6px 10px;border-bottom:1px solid #e5e5e5;font-weight:600}
.side .bar a{font-weight:400;color:#06c}
.shot{flex:1;overflow:auto;background:#eee} .shot img{width:100%;display:block}
footer{position:sticky;bottom:0;background:#fff;border-top:1px solid #ddd;padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:center}
button{font:inherit;padding:10px 22px;border:1px solid #888;background:#fff;border-radius:4px;cursor:pointer}
button.pick{font-weight:700} button:disabled{opacity:.4;cursor:default}
.q{font-weight:600;margin-right:8px}
.done{padding:60px;text-align:center;font-size:18px}
</style>
<header><b>Which would you be more likely to deliver to a client?</b><span class=brief id=brief></span><span class=n id=n></span></header>
<main>
 <section class=side><div class=bar><span>Left</span><a id=la target=_blank href="#">open live page ↗</a></div><div class=shot id=ls><img id=li alt=""></div></section>
 <section class=side><div class=bar><span>Right</span><a id=ra target=_blank href="#">open live page ↗</a></div><div class=shot id=rs><img id=ri alt=""></div></section>
</main>
<footer><span class=q>Scroll both to the bottom, then choose:</span><button class=pick id=bl disabled>← Left (1)</button><button class=pick id=br disabled>Right (2) →</button><button id=skip>skip for now</button></footer>
<script>
let queue=[], cur=null, t0=0, seenL=false, seenR=false;
async function load(){ const r=await fetch('/api/state'); const s=await r.json(); queue=s.pending; document.getElementById('n').textContent=`${s.done} judged · ${s.pending.length} pending · ${s.unbuilt} not yet built`; next(); }
function next(){ cur=queue.shift(); seenL=seenR=false; upd();
  if(!cur){ document.querySelector('main').innerHTML='<div class=done>Nothing pending. Come back when the next wave lands.</div>'; document.querySelector('footer').style.display='none'; return; }
  document.getElementById('brief').textContent=cur.briefText; t0=Date.now();
  document.getElementById('li').src=`/builds/${cur.left}/shot-full.png`; document.getElementById('ri').src=`/builds/${cur.right}/shot-full.png`;
  document.getElementById('la').href=`/builds/${cur.left}/index.html`; document.getElementById('ra').href=`/builds/${cur.right}/index.html`;
  document.getElementById('ls').scrollTop=0; document.getElementById('rs').scrollTop=0; }
function upd(){ const ok=seenL&&seenR; document.getElementById('bl').disabled=!ok; document.getElementById('br').disabled=!ok; }
function watch(id,set){ const el=document.getElementById(id); el.addEventListener('scroll',()=>{ if(el.scrollTop+el.clientHeight>=el.scrollHeight-40){ set(); upd(); } }); }
watch('ls',()=>seenL=true); watch('rs',()=>seenR=true);
document.getElementById('li').addEventListener('load',()=>{ const el=document.getElementById('ls'); if(el.scrollHeight<=el.clientHeight+40){seenL=true;upd();} });
document.getElementById('ri').addEventListener('load',()=>{ const el=document.getElementById('rs'); if(el.scrollHeight<=el.clientHeight+40){seenR=true;upd();} });
async function judge(choice){ if(!cur) return; await fetch('/api/judge',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({pair:cur.pair,left:cur.left,right:cur.right,choice,ms:Date.now()-t0,at:new Date().toISOString()})}); load(); }
document.getElementById('bl').onclick=()=>judge('left'); document.getElementById('br').onclick=()=>judge('right'); document.getElementById('skip').onclick=()=>next();
document.addEventListener('keydown',e=>{ if(e.key==='1'&&!document.getElementById('bl').disabled) judge('left'); if(e.key==='2'&&!document.getElementById('br').disabled) judge('right'); });
load();
</script>"""


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WS, **k)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = PAGE.encode(); self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if self.path == "/api/state":
            done = judged(); pend = []; unbuilt = 0
            for p in schedule():
                if p["pair"] in done:
                    continue
                if built(p["left"]) and built(p["right"]):
                    pend.append({**p, "briefText": brief_text(p["eval"])})
                else:
                    unbuilt += 1
            body = json.dumps({"done": len(done), "pending": pend, "unbuilt": unbuilt}).encode()
            self.send_response(200); self.send_header("content-type", "application/json"); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        if self.path.startswith("/builds/") and (self.path.endswith("DESIGN.md") or self.path.endswith("/")):
            self.send_response(403); self.end_headers(); return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/judge":
            n = int(self.headers.get("content-length", 0)); j = json.loads(self.rfile.read(n))
            with open(JUDGMENTS, "a") as f:
                f.write(json.dumps(j) + "\n")
            self.send_response(204); self.end_headers(); return
        self.send_response(404); self.end_headers()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "schedule":
        for p in schedule():
            print(p["brief"], p["left"], p["right"])
        sys.exit()
    print(f"settling rating → http://localhost:{PORT}/   (judgments → {JUDGMENTS})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
