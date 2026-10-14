#!/usr/bin/env python3
r"""build_scroll.py — render THE_DELIBERATE_LINE_PUBLIC.md as a single self-contained scroll page,
with the three figures placed inline at the sections they belong to and revealed as you scroll.

Noah, 2026-09-20: "there was some graphs/visuals that tracked with the paper as you scrolled through
… I don't think it was finished either." It wasn't built. This builds it — the paper read top to
bottom, the figure for each idea arriving where the idea does. Dark to match the figures (which are
rendered on ink), one portable file (images base64-embedded, so it opens anywhere with nothing to
fetch). A FIRST version to steer the look on, not a finished aesthetic.

    python build_scroll.py   ->   deliberate_line.html

No third-party libraries — a focused Markdown converter for exactly the constructs this paper uses
(headings, bold/italic, inline + fenced code, tables, lists, blockquote-italic notes, rules).
"""
from __future__ import annotations

import base64
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(HERE, "THE_DELIBERATE_LINE_PUBLIC.md")
FIGDIR = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "deliberate_line.html")

# a figure is dropped in BEFORE the paragraph whose text contains the anchor phrase (first match)
FIGURES = [
    ("out of sample", "deliberate_line_full.png",
     "The whole argument in one image — the migrating seat (1300–2026) with the within-society "
     "extraction wedge, the S&P deliberate line, and the flip from taking to receiving. Every "
     "fitted number is printed on the figure so it checks against the text."),
    ("Correlate today's deviation", "deliberate_line.png",
     "The S&P 500 in log-space against one straight line — and the deviation from it predicting the "
     "next year's return, in-sample and out."),
    ("watch the seat itself migrate", "migrating_seat.png",
     "The seat of global value, hand to hand, on measured output back to the 1300s: Italian "
     "city-states → the Dutch Republic → Britain → the United States — the S&P line the latest turn."),
]


def _b64_img(name: str) -> str | None:
    p = os.path.join(FIGDIR, name)
    if not os.path.isfile(p):
        return None
    with open(p, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    # inline code first so its contents are not further formatted
    codes: list[str] = []
    def _stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)
    s = re.sub(r"`([^`]+)`", _stash, s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    # bold may contain nested italic (e.g. **…the *rate* stepped…**) and may close against an
    # adjacent italic-close as *** — split *** into (italic-close *)(strong-close \x02) first, then
    # match bold non-greedily accepting either close, so the inner *word* survives for the em pass.
    s = re.sub(r"\*\*\*", "*\x02", s)
    s = re.sub(r"\*\*(.+?)(?:\*\*|\x02)", lambda m: "<strong>%s</strong>" % m.group(1), s)
    s = s.replace("\x02", "**")
    s = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % html.escape(codes[int(m.group(1))], quote=False), s)
    return s


def convert(md: str) -> list[str]:
    lines = md.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []

    def flush_para():
        if para:
            text = " ".join(x.strip() for x in para).strip()
            if text:
                cls = ' class="note"' if text.startswith("*(") or text.startswith("<em>(") else ""
                out.append("<p%s>%s</p>" % (cls, _inline(text)))
            para.clear()

    while i < n:
        line = lines[i]
        st = line.strip()
        # figure anchors — inject before the paragraph that carries the phrase
        for phrase, fig, cap in list(FIGURES):
            if phrase in line:
                data = _b64_img(fig)
                if data:
                    flush_para()
                    out.append(
                        '<figure class="fig"><img loading="lazy" src="%s" alt="%s">'
                        '<figcaption>%s</figcaption></figure>' % (data, html.escape(fig), _inline(cap)))
                FIGURES.remove((phrase, fig, cap))
                break
        if st.startswith("```"):
            flush_para()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(buf), quote=False))
            i += 1
            continue
        if st.startswith("|") and i + 1 < n and set(lines[i + 1].strip()) <= set("|-: "):
            flush_para()
            header = [c.strip() for c in st.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join("<th>%s</th>" % _inline(c) for c in header)
            body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in r) for r in rows)
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, body))
            continue
        if not st:
            flush_para()
            i += 1
            continue
        if st == "---":
            flush_para()
            out.append("<hr>")
            i += 1
            continue
        m = re.match(r"(#{1,3})\s+(.*)", st)
        if m:
            flush_para()
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, _inline(m.group(2)), lvl))
            i += 1
            continue
        if st.startswith("- "):
            flush_para()
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append("<li>%s</li>" % _inline(lines[i].strip()[2:]))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue
        para.append(line)
        i += 1
    flush_para()
    return out


CSS = """
:root{--ink:#0d0f13;--paper:#e8e4d8;--gold:#d9a441;--take:#c0503f;--give:#5b9279;--mute:#8a8577}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--ink);color:var(--paper);
 font:18px/1.7 Georgia,'Iowan Old Style',serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:7vh 24px 18vh}
h1{font-size:2.5rem;line-height:1.12;margin:.2em 0 .1em;letter-spacing:-.01em}
h2{font-size:1.5rem;margin:2.4em 0 .5em;color:#fff;border-top:1px solid #23262d;padding-top:1.2em}
h3{font-size:1.15rem;color:var(--mute);font-weight:400;font-style:italic;margin:.2em 0 1.4em}
p{margin:0 0 1.1em}
p.note{color:var(--mute);font-size:.94rem}
a{color:var(--gold);text-decoration:none;border-bottom:1px solid #4a4331}
a:hover{border-color:var(--gold)}
strong{color:#fff}
em{color:#d8d2c4}
code{font-family:'SF Mono',Consolas,monospace;font-size:.86em;background:#181b21;color:var(--gold);padding:.08em .35em;border-radius:3px}
pre{background:#15181e;border:1px solid #23262d;border-radius:8px;padding:16px 18px;overflow:auto;margin:1.3em 0}
pre code{background:none;color:#cfc9ba;font-size:.82rem;line-height:1.55;padding:0}
table{width:100%;border-collapse:collapse;margin:1.4em 0;font-size:.9rem}
th,td{text-align:left;padding:.5em .7em;border-bottom:1px solid #23262d;vertical-align:top}
th{color:var(--gold);font-family:Georgia,serif;font-weight:400;border-bottom-color:#3a3428}
hr{border:none;border-top:1px solid #23262d;margin:2.6em 0}
ul{padding-left:1.2em}
li{margin:.35em 0}
figure.fig{margin:2.4em -8vw;opacity:0;transform:translateY(24px);transition:opacity .8s ease,transform .8s ease}
figure.fig.in{opacity:1;transform:none}
figure.fig img{width:100%;height:auto;border-radius:10px;border:1px solid #23262d;
 box-shadow:0 14px 50px rgba(0,0,0,.5);background:var(--ink)}
figcaption{color:var(--mute);font-size:.82rem;font-style:italic;margin-top:.7em;padding:0 8vw;text-align:center}
@media(max-width:820px){figure.fig{margin-left:0;margin-right:0}figcaption{padding:0}}
@media(max-width:560px){body{font-size:16px}h1{font-size:1.9rem}.wrap{padding:6vh 18px 14vh}}
.rule{height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.5;margin:1.6em 0}
"""

JS = """
const io=new IntersectionObserver((es)=>{for(const e of es){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}},{threshold:.15});
document.querySelectorAll('figure.fig').forEach(f=>io.observe(f));
"""


def build() -> str:
    with open(PAPER, encoding="utf-8") as fh:
        md = fh.read()
    body = "\n".join(convert(md))
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>The Deliberate Line</title><style>%s</style></head>"
        "<body><main class=wrap>%s</main><script>%s</script></body></html>"
        % (CSS, body, JS)
    )


if __name__ == "__main__":
    htmlout = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(htmlout)
    size_kb = os.path.getsize(OUT) // 1024
    print("wrote", OUT, "(%d KB, self-contained)" % size_kb)
