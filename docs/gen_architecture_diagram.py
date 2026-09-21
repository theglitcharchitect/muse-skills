#!/usr/bin/env python3
"""Generate docs/architecture.svg from code. No image tools, no AI imagery:
rectangles, text, and arrows drawn by this script only."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.svg")

W, H = 860, 520
BG = "#0e1116"
BOX = "#161b22"
EDGE = "#30363d"
TXT = "#e6edf3"
DIM = "#8b949e"
ACC = "#58a6ff"
GRN = "#3fb950"
AMB = "#d29922"

parts = []


def rect(x, y, w, h, fill=BOX, edge=EDGE, rx=8):
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{edge}" stroke-width="1.5"/>')


def text(x, y, s, size=14, fill=TXT, anchor="middle", weight="600"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    parts.append(
        f'<text x="{x}" y="{y}" font-family="system-ui, -apple-system, sans-serif" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}">{s}</text>')


def sub(x, y, s, size=12):
    text(x, y, s, size=size, fill=DIM, weight="400")


def arrow(x1, y1, x2, y2, color=ACC, label=None):
    parts.append(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="1.5" marker-end="url(#ah)"/>')
    if label:
        text((x1 + x2) / 2 + 6, (y1 + y2) / 2 - 6, label, size=11,
             fill=color, anchor="start", weight="400")


parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">')
parts.append(f'<rect width="{W}" height="{H}" fill="{BG}" rx="12"/>')
parts.append(
    '<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" '
    'orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#58a6ff"/></marker></defs>')
text(W / 2, 36, "Muse + Jev: how the pieces fit", size=20)

# Row 1: agent loop
rect(40, 70, 180, 90)
text(130, 100, "Agent")
sub(130, 122, "proposes an action")

rect(340, 70, 180, 90)
text(430, 100, "Usage router")
sub(430, 122, "bin/router.py")
sub(430, 140, "ALLOW / DENY / ESCALATE")

rect(640, 70, 180, 90)
text(730, 100, "Shadow log")
sub(730, 122, "logs/*.jsonl")
sub(730, 140, "every decision recorded")

arrow(220, 115, 340, 115)
arrow(520, 115, 640, 115)

# Row 2: gates
rect(40, 220, 180, 90, edge=AMB)
text(130, 250, "Safety gate", fill=AMB)
sub(130, 272, "bin/safety_gate.py")
sub(130, 290, "pre-tool-call check")

rect(340, 220, 180, 90, edge=AMB)
text(430, 250, "Draft judge", fill=AMB)
sub(430, 272, "bin/judge.py")
sub(430, 290, "score before delivery")

rect(640, 220, 180, 90, edge=GRN)
text(730, 250, "Human", fill=GRN)
sub(730, 272, "authorizes")
sub(730, 290, "irreversible actions")

arrow(130, 160, 130, 220, color=AMB)
arrow(430, 160, 430, 220, color=AMB)
arrow(560, 265, 640, 265, color=GRN)

# Row 3: jev core
rect(190, 370, 480, 100)
text(430, 400, "TypeSafe Jev via Vercel AI Gateway")
sub(430, 422, "typed Choice / Score / Boolean evaluations with probabilities")
sub(430, 440, "bin/jev.py  -  mock gateway in the demo, live with a key")

arrow(130, 310, 300, 400, color=AMB)
arrow(430, 310, 430, 370, color=AMB)
arrow(700, 310, 560, 400, color=GRN)

# caption
text(W / 2, 502, "Jev advises. The human authorizes. Shadow mode first, "
                 "always.", size=12, fill=DIM, weight="400")

parts.append("</svg>")
with open(OUT, "w") as f:
    f.write("\n".join(parts) + "\n")
print("wrote", OUT)
