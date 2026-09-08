#!/usr/bin/env python3
import argparse, html, os, re, shutil, subprocess, sys, glob
from pathlib import Path
import tempfile
import markdown

CSS = r"""
:root{--bg:#efece3;--paper:#fffdf9;--ink:#221f1a;--ink-soft:#544f46;--ink-faint:#8a8275;--accent:#1d6b66;--accent-d:#13524e;--accent2:#a8521d;--line:#e2dccd;
--concept:#e9f3f1;--concept-b:#1d6b66;--summary:#f6f0e2;--quiz:#efeaf4;--quiz-b:#6b4d8f;--note:#fbf1e4;--note-b:#c0732e;--warn:#f9eaea;--warn-b:#b34a3f;
--sidebar:#2a2620;--sidebar-ink:#d9d2c4;--sidebar-dim:#9a9183;--sidebar-active:#7fd8d0;--maxw:51rem;
--serif:"Noto Serif CJK SC","Source Han Serif SC","Songti SC",Georgia,"Times New Roman",serif;
--sans:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC","Hiragino Sans GB",-apple-system,system-ui,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--serif);font-size:18px;line-height:1.9}
#progress{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--accent),var(--accent2));width:0;z-index:200}
#layout{display:flex}
#sidebar{position:fixed;top:0;left:0;width:316px;height:100vh;background:var(--sidebar);color:var(--sidebar-ink);overflow-y:auto;padding:0 0 3rem;z-index:120}
#sidebar .side-head{padding:1.4rem 1.4rem 1rem;border-bottom:1px solid #423c32;position:sticky;top:0;background:var(--sidebar)}
#sidebar .bk{font-family:var(--sans);font-weight:700;font-size:1.02rem;color:#fff;line-height:1.45}
#sidebar .sub{font-family:var(--sans);font-size:.72rem;color:var(--sidebar-dim);margin-top:.35rem;letter-spacing:.06em}
#main{margin-left:316px;flex:1;min-width:0}.wrap{max-width:var(--maxw);margin:0 auto;padding:3.2rem 2.2rem 6rem}
ul.toc{list-style:none;margin:0;padding:.6rem .6rem 0;font-family:var(--sans)}ul.toc li{margin:0}
ul.toc a{color:var(--sidebar-ink);text-decoration:none;display:block;padding:.34rem .7rem;border-radius:7px;font-size:.83rem;line-height:1.4}
ul.toc a:hover{background:#39332b;color:#fff}
li.part{margin-top:1rem}li.part>a{color:var(--sidebar-active);font-weight:700;font-size:.74rem;letter-spacing:.12em;padding-top:.5rem;border-top:1px solid #423c32;border-radius:0}
li.chap{position:relative}li.chap>a{padding-left:1.5rem;font-weight:600;color:#e9e3d6}
li.chap .tw{position:absolute;left:.45rem;top:.46rem;cursor:pointer;color:var(--sidebar-dim);font-size:.7rem;transition:transform .15s;user-select:none;width:1rem;text-align:center}
li.chap.open .tw{transform:rotate(90deg)}
ul.subs{list-style:none;margin:0;padding:0;max-height:0;overflow:hidden;transition:max-height .25s}li.chap.open ul.subs{max-height:60rem}
li.sub>a{padding-left:2.2rem;font-size:.78rem;color:var(--sidebar-dim)}li.sub>a:hover{color:#fff}
ul.toc a.active{background:var(--accent);color:#fff!important}li.sub>a.active{background:var(--accent-d)}
#cover{max-width:var(--maxw);margin:0 auto;min-height:100vh;display:flex;flex-direction:column;padding:3.4rem 2.2rem 2.8rem;text-align:center;border-bottom:1px solid var(--line)}
#cover .imprint{font-family:var(--sans);letter-spacing:.52em;font-size:.86rem;font-weight:700;color:var(--accent);padding-left:.52em}
#cover .imprint-sub{font-family:var(--sans);letter-spacing:.24em;font-size:.62rem;color:var(--ink-faint);margin-top:.62rem;text-transform:uppercase}
#cover .cover-top::after{content:"";display:block;width:42px;height:2px;background:var(--line);margin:1.3rem auto 0}
#cover .cover-center{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center}
#cover h1.booktitle{font-family:var(--sans);font-size:3rem;line-height:1.22;margin:0;font-weight:800}
#cover .rule{width:54px;height:3px;background:var(--accent2);margin:1.75rem auto}
#cover .booksub{font-size:1.06rem;line-height:1.85;color:var(--ink-soft);max-width:31rem}
#cover .cover-foot{font-family:var(--sans);padding-top:1.4rem;border-top:1px solid var(--line)}
#cover .foot-line{font-size:.88rem;color:var(--ink-soft);font-weight:600}#cover .foot-dim{font-size:.76rem;color:var(--ink-faint);line-height:1.9;margin-top:.45rem}
.wrap h1{font-family:var(--sans);font-size:1.05rem;font-weight:800;letter-spacing:.16em;color:var(--accent);margin:4.5rem 0 0;padding:1rem 0 .4rem;border-bottom:2px solid var(--accent)}
.wrap h1 .pnum{display:block;font-size:.72rem;letter-spacing:.2em;color:var(--accent2);margin-bottom:.3rem}
.wrap h2{font-family:var(--sans);font-size:1.72rem;font-weight:800;line-height:1.3;margin:3.2rem 0 1.1rem;padding-top:1rem}
.wrap h3{font-family:var(--sans);font-size:1.22rem;font-weight:700;color:var(--accent-d);margin:2.4rem 0 .8rem}
.wrap h4{font-family:var(--sans);font-size:1.02rem;font-weight:700;margin:1.6rem 0 .5rem}
.wrap p{margin:0 0 1.05rem}.wrap a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(29,107,102,.35)}
.wrap strong{font-weight:700;color:#000}.wrap em{font-style:normal;background:linear-gradient(transparent 62%,#ffe9a8 62%)}
.wrap ul,.wrap ol{margin:0 0 1.15rem;padding-left:1.5rem}.wrap li{margin:.3rem 0}
.wrap blockquote{margin:1.4rem 0;padding:.5rem 1.2rem;border-left:3px solid var(--accent2);color:var(--ink-soft);background:#fbf8f1;font-size:.97rem}
.en{font-family:Georgia,"Times New Roman",serif;font-style:italic;color:var(--accent-d)}
.box{border-radius:12px;padding:1.1rem 1.3rem 1.15rem;margin:1.6rem 0;font-size:.96rem;line-height:1.8;border:1px solid var(--line)}
.box .box-t{font-family:var(--sans);font-weight:800;font-size:.82rem;letter-spacing:.08em;display:flex;align-items:center;gap:.5rem;margin-bottom:.6rem}
.box p:last-child,.box ul:last-child,.box ol:last-child{margin-bottom:0}.box .ic{font-size:1.05rem}
.box.learn{background:var(--concept);border-color:#bfe0db}.box.learn .box-t{color:var(--concept-b)}
.box.concept{background:#fff;border-left:4px solid var(--concept-b)}.box.concept .box-t{color:var(--concept-b)}
.box.summary{background:var(--summary);border-color:#e6d6a8}.box.summary .box-t{color:#9a7321}
.box.quiz{background:var(--quiz);border-color:#d6c9e6}.box.quiz .box-t{color:var(--quiz-b)}
.box.quiz ol{counter-reset:q;list-style:none;padding-left:0}.box.quiz ol li{counter-increment:q;padding-left:2rem;position:relative;margin:.55rem 0}
.box.quiz ol li::before{content:counter(q);position:absolute;left:0;top:.05rem;width:1.4rem;height:1.4rem;background:var(--quiz-b);color:#fff;border-radius:50%;font-family:var(--sans);font-size:.78rem;font-weight:700;display:flex;align-items:center;justify-content:center}
.box.note{background:var(--note);border-color:#ebcfa8}.box.note .box-t{color:var(--note-b)}
.box.warn{background:var(--warn);border-color:#e6c2bc}.box.warn .box-t{color:var(--warn-b)}
.box.who{background:#f3f1ec}.box.who .box-t{color:var(--ink-soft)}
.fig{margin:1.6rem 0;padding:1.2rem 1.3rem;background:#fff;border:1px solid var(--line);border-radius:12px;text-align:center}
.fig .big{font-family:var(--sans);font-size:2.1rem;font-weight:800;color:var(--accent)}.fig .cap{font-family:var(--sans);font-size:.82rem;color:var(--ink-faint);margin-top:.3rem}
figure.diagram{margin:1.9rem 0;padding:1.3rem 1.1rem .9rem;background:var(--paper);border:1px solid var(--line);border-radius:14px;text-align:center;break-inside:avoid}
figure.diagram .d-t{font-family:var(--sans);font-weight:800;font-size:.92rem;color:var(--accent-d);margin-bottom:.9rem}
figure.diagram svg{max-width:100%;height:auto;display:block;margin:0 auto}figure.diagram text{font-family:var(--sans)}
figure.diagram figcaption{font-family:var(--sans);font-size:.82rem;color:var(--ink-soft);margin-top:.85rem;line-height:1.65;max-width:40rem;margin-left:auto;margin-right:auto}
.wrap table{border-collapse:collapse;width:100%;margin:1.5rem 0;font-size:.9rem;font-family:var(--sans)}
.wrap th,.wrap td{border:1px solid var(--line);padding:.55rem .7rem;text-align:left;vertical-align:top}.wrap th{background:#efe9dc}.wrap tr:nth-child(even) td{background:#fbf8f1}
dl.gloss dt{font-family:var(--sans);font-weight:700;color:var(--accent-d);margin-top:1rem}dl.gloss dd{margin:.2rem 0 0;color:var(--ink-soft);font-size:.95rem}
.bookfoot{font-family:var(--sans);font-size:.8rem;color:var(--ink-faint);text-align:center;border-top:1px solid var(--line);margin-top:4rem;padding:2rem;line-height:1.8}
#menu-btn{display:none;position:fixed;top:.7rem;left:.7rem;z-index:140;background:var(--sidebar);color:#fff;border:none;border-radius:9px;width:44px;height:44px;font-size:1.3rem;cursor:pointer}
#overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:110}
@media(max-width:900px){#sidebar{transform:translateX(-100%);transition:transform .25s;width:84vw;max-width:340px}
body.nav-open #sidebar{transform:translateX(0)}body.nav-open #overlay{display:block}#main{margin-left:0}#menu-btn{display:block}
.wrap{padding:3.6rem 1.25rem 5rem}#cover{padding:3rem 1.25rem 2.2rem}#cover h1.booktitle{font-size:2.1rem}body{font-size:17px}}
@page{size:A4;margin:17mm 15mm}
@media print{html,body{background:#fff}body{font-size:11.5pt;line-height:1.62}
#sidebar,#menu-btn,#overlay,#progress{display:none!important}#layout{display:block}#main{margin-left:0}.wrap{max-width:none;margin:0;padding:0}
#cover{border:none;min-height:auto;height:calc(100vh - 1px);padding:6mm 0;break-after:page}#cover h1.booktitle{font-size:32pt}#cover .booksub{font-size:13pt}
.wrap h1{break-before:page}.wrap h2{break-before:page;break-after:avoid}.wrap h2,.wrap h3,.wrap h4{break-after:avoid}
.box,figure.diagram,.fig,table,blockquote{break-inside:avoid}dl.gloss dt{break-after:avoid}dl.gloss dd{break-before:avoid}
p,li{orphans:2;widows:2}.bookfoot{break-before:page;margin-top:2rem}.wrap a{color:var(--accent-d);border:none}.box .box-t .ic{display:none}}
"""
JS = r"""
(function(){
var bar=document.getElementById('progress');
function onScroll(){var h=document.documentElement,st=h.scrollTop||document.body.scrollTop,sh=(h.scrollHeight-h.clientHeight)||1;bar.style.width=(st/sh*100)+'%';}
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
var body=document.body,btn=document.getElementById('menu-btn'),ov=document.getElementById('overlay');
function close(){body.classList.remove('nav-open');}
btn&&btn.addEventListener('click',function(){body.classList.toggle('nav-open');});ov&&ov.addEventListener('click',close);
document.querySelectorAll('li.chap.has-sub .tw').forEach(function(tw){tw.addEventListener('click',function(e){e.stopPropagation();tw.parentElement.classList.toggle('open');});});
document.querySelectorAll('ul.toc a').forEach(function(a){a.addEventListener('click',function(){if(window.innerWidth<=900)close();});});
var links={};document.querySelectorAll('ul.toc a').forEach(function(a){links[a.getAttribute('href').slice(1)]=a;});
var heads=Array.prototype.slice.call(document.querySelectorAll('.wrap h1,.wrap h2,.wrap h3')),current=null;
function spy(){var pos=(document.documentElement.scrollTop||document.body.scrollTop)+120,act=null;
for(var i=0;i<heads.length;i++){if(heads[i].offsetTop<=pos)act=heads[i];else break;}
if(!act||act.id===current)return;current=act.id;for(var k in links)links[k].classList.remove('active');
var a=links[act.id];if(a){a.classList.add('active');var li=a.closest('li.chap');if(li)li.classList.add('open');
var sub=a.closest('li.sub');if(sub){var pc=sub.closest('li.chap');if(pc)pc.classList.add('open');}
var nav=document.getElementById('sidebar'),ar=a.getBoundingClientRect(),nr=nav.getBoundingClientRect();
if(ar.top<nr.top+100)nav.scrollTop-=nr.top+100-ar.top;
else if(ar.bottom>nr.bottom)nav.scrollTop+=ar.bottom-nr.bottom;}}
window.addEventListener('scroll',function(){window.requestAnimationFrame(spy);},{passive:true});spy();
})();
"""

def find_browser(explicit=None):
    requested = explicit or os.environ.get("CHROME_PATH")
    candidates = [requested] if requested else [
        "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    if not requested:
        for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            if os.environ.get(key):
                candidates.append(str(Path(os.environ[key]) / "Google/Chrome/Application/chrome.exe"))
                candidates.append(str(Path(os.environ[key]) / "Microsoft/Edge/Application/msedge.exe"))
    for candidate in candidates:
        resolved = shutil.which(candidate) or os.path.expanduser(candidate)
        if Path(resolved).is_file() and os.access(resolved, os.X_OK): return resolved
    sys.exit("找不到 Chrome/Chromium；请安装浏览器或用 --chrome 指定可执行文件。HTML 已保存。")


def build(a):
    files = sorted(glob.glob(os.path.join(a.chapters, "*.md")))
    if not files: sys.exit("no .md in " + a.chapters)
    parts, toc, sec = [], [], 0
    for f in files:
        h = markdown.markdown(Path(f).read_text(encoding="utf-8"), extensions=["extra", "sane_lists", "md_in_html"])
        def repl(m):
            nonlocal sec; sec += 1
            lvl, inner = m.group(1), m.group(2)
            text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip(); sid = f"sec{sec}"
            if lvl == "1":
                pn = re.match(r"(.+?)[｜|](.+)", text)
                if pn:
                    inner = f'<span class="pnum">{html.escape(pn.group(1).strip())}</span>{html.escape(pn.group(2).strip())}'; text = pn.group(2).strip()
                toc.append(("part", sid, text))
            else: toc.append(("chap" if lvl == "2" else "sub", sid, text))
            return f'<h{lvl} id="{sid}">{inner}</h{lvl}>'
        parts.append(f"<!-- {os.path.basename(f)} -->\n" + re.sub(r"<h([123])>(.*?)</h\1>", repl, h, flags=re.S) + "\n")
    items, i = [], 0
    while i < len(toc):
        kind, sid, text = toc[i]
        if kind == "part": items.append(f'<li class="part"><a href="#{sid}">{html.escape(text)}</a></li>'); i += 1
        elif kind == "chap":
            subs, j = [], i + 1
            while j < len(toc) and toc[j][0] == "sub":
                subs.append(f'<li class="sub"><a href="#{toc[j][1]}">{html.escape(toc[j][2])}</a></li>'); j += 1
            items.append(f'<li class="chap has-sub"><span class="tw">▸</span><a href="#{sid}">{html.escape(text)}</a><ul class="subs">{"".join(subs)}</ul></li>' if subs
                         else f'<li class="chap"><a href="#{sid}">{html.escape(text)}</a></li>'); i = j
        else: i += 1
    cl = [l.strip() for l in a.cover_lines.split("|") if l.strip()]
    foot = (f'<div class="foot-line">{html.escape(cl[0])}</div>' + ('<div class="foot-dim">' + "<br>".join(html.escape(l) for l in cl[1:]) + '</div>' if len(cl) > 1 else "")) if cl else ""
    doc = f"""<!DOCTYPE html><html lang="{html.escape(a.lang, quote=True)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(a.title)}{(' · ' + html.escape(a.subtitle)) if a.subtitle else ''}</title><style>{CSS}</style></head>
<body><div id="progress"></div><button id="menu-btn" aria-label="目录">☰</button><div id="overlay"></div>
<div id="layout"><nav id="sidebar"><div class="side-head"><div class="bk">{html.escape(a.title)}</div><div class="sub">{html.escape(a.sidebar_sub or a.subtitle)}</div></div>
<ul class="toc">{chr(10).join(items)}</ul></nav>
<div id="main"><section id="cover"><div class="cover-top"><div class="imprint">{html.escape(a.imprint)}</div><div class="imprint-sub">{html.escape(a.imprint_sub)}</div></div>
<div class="cover-center"><h1 class="booktitle">{html.escape(a.title)}</h1><div class="rule"></div><p class="booksub">{html.escape(a.subtitle)}</p></div>
<div class="cover-foot">{foot}</div></section>
<div class="wrap">{''.join(parts)}<div class="bookfoot">{html.escape(a.footer)}</div></div></div></div>
<script>{JS}</script></body></html>"""
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(doc, encoding="utf-8"); print(f"wrote {a.output} ({len(files)} files, {sec} headings)")
    if a.pdf:
        chrome = find_browser(a.chrome)
        pdf = os.path.splitext(a.output)[0] + ".pdf"
        with tempfile.TemporaryDirectory(prefix="ebook-chrome-") as profile:
            temporary_pdf = Path(profile) / "book.pdf"
            command = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                       "--user-data-dir=" + profile, "--no-pdf-header-footer", "--virtual-time-budget=10000",
                       "--print-to-pdf=" + str(temporary_pdf), Path(a.output).resolve().as_uri()]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                sys.exit("PDF 渲染失败；HTML 已保存。" + str(exc))
            if not temporary_pdf.is_file() or temporary_pdf.stat().st_size == 0:
                sys.exit("浏览器未生成 PDF；HTML 已保存。")
            shutil.copyfile(temporary_pdf, pdf)
        print("wrote", pdf)
        if shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", "-singlefile", pdf, os.path.splitext(a.output)[0] + "-cover"], check=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("chapters"); ap.add_argument("-o", "--output", default="book.html")
    ap.add_argument("--title", required=True); ap.add_argument("--subtitle", default=""); ap.add_argument("--sidebar-sub", default="")
    ap.add_argument("--imprint", default=""); ap.add_argument("--imprint-sub", default=""); ap.add_argument("--cover-lines", default="")
    ap.add_argument("--footer", default=""); ap.add_argument("--lang", default="zh-CN"); ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--chrome", help="Chrome/Chromium 可执行文件路径，也可设置 CHROME_PATH")
    build(ap.parse_args())
