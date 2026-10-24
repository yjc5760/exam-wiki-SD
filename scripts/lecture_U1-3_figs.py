# -*- coding: utf-8 -*-
"""
lecture-SD-U1-3.html 向量圖產生器
所有曲線由講義內文的公式直接計算（不手描），重跑即可重現。
用法：python lecture_U1-3_figs.py  → 輸出 figs_U1-3/*.svg（每張圖一個檔）
"""
import math, os, json
import numpy as np

C = dict(red="#c62828", ora="#ef6c00", blu="#1565c0", grn="#2e7d32", pur="#6a1b9a",
         ink="#263238", ink2="#37474f", mut="#78909c", axis="#455a64", grid="#eceff1",
         ref="#b0bec5", gry="#90a4ae")

def f(v, n=1):
    return f"{v:.{n}f}"

def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    P = np.array(pts); d = b - a; n = np.hypot(*d)
    dist = np.abs(d[0] * (P[:, 1] - a[1]) - d[1] * (P[:, 0] - a[0])) / n if n > 0 else np.hypot(*(P - a).T)
    i = int(np.argmax(dist))
    if dist[i] > eps:
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]

class Ax:
    def __init__(s, x0, y0, w, h, xr, yr, cid):
        s.x0, s.y0, s.w, s.h, s.xr, s.yr, s.cid = x0, y0, w, h, xr, yr, cid
    def X(s, v): return s.x0 + (v - s.xr[0]) / (s.xr[1] - s.xr[0]) * s.w
    def Y(s, v): return s.y0 + s.h - (v - s.yr[0]) / (s.yr[1] - s.yr[0]) * s.h
    def path(s, xs, ys):
        segs, cur = [], []
        for x, y in zip(xs, ys):
            if np.isfinite(y):
                yy = min(max(s.Y(y), s.y0 - 40), s.y0 + s.h + 40)
                cur.append((s.X(x), yy))
            elif cur:
                segs.append(cur); cur = []
        if cur: segs.append(cur)
        out = []
        for sg in segs:
            sg = rdp(sg, 0.12)
            out.append("M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in sg))
        return " ".join(out)
    def clip(s):
        return (f'<clipPath id="{s.cid}"><rect x="{s.x0}" y="{s.y0}" width="{s.w}" '
                f'height="{s.h}"/></clipPath>')
    def frame(s, xticks, yticks, xlab, ylab, xfmt=None, yfmt=None, grid=True):
        o = []
        if grid:
            for v in yticks:
                o.append(f'<line x1="{s.x0}" y1="{s.Y(v):.1f}" x2="{s.x0+s.w}" y2="{s.Y(v):.1f}" stroke="{C["grid"]}"/>')
        for v in xticks:
            o.append(f'<line x1="{s.X(v):.1f}" y1="{s.y0+s.h}" x2="{s.X(v):.1f}" y2="{s.y0+s.h+5}" stroke="{C["axis"]}"/>')
            lab = xfmt(v) if xfmt else f"{v:g}"
            o.append(f'<text x="{s.X(v):.1f}" y="{s.y0+s.h+19}" text-anchor="middle" font-size="11.5" fill="{C["mut"]}">{lab}</text>')
        for v in yticks:
            o.append(f'<line x1="{s.x0-5}" y1="{s.Y(v):.1f}" x2="{s.x0}" y2="{s.Y(v):.1f}" stroke="{C["axis"]}"/>')
            lab = yfmt(v) if yfmt else f"{v:g}"
            o.append(f'<text x="{s.x0-8}" y="{s.Y(v)+4:.1f}" text-anchor="end" font-size="11.5" fill="{C["mut"]}">{lab}</text>')
        o.append(f'<line x1="{s.x0}" y1="{s.y0+s.h}" x2="{s.x0+s.w}" y2="{s.y0+s.h}" stroke="{C["axis"]}" stroke-width="1.5"/>')
        o.append(f'<line x1="{s.x0}" y1="{s.y0}" x2="{s.x0}" y2="{s.y0+s.h}" stroke="{C["axis"]}" stroke-width="1.5"/>')
        o.append(f'<text x="{s.x0+s.w/2:.0f}" y="{s.y0+s.h+40}" text-anchor="middle" font-size="13" fill="{C["ink2"]}">{xlab}</text>')
        yc = s.y0 + s.h / 2
        o.append(f'<text x="{s.x0-46}" y="{yc:.0f}" text-anchor="middle" font-size="13" fill="{C["ink2"]}" transform="rotate(-90 {s.x0-46} {yc:.0f})">{ylab}</text>')
        return "\n".join(o)
    def curve(s, xs, ys, col, sw=2.2, dash=None, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<path d="{s.path(xs, ys)}" fill="none" stroke="{col}" stroke-width="{sw}"'
                f'{d} stroke-linejoin="round" opacity="{op}" clip-path="url(#{s.cid})"/>')
    def dot(s, x, y, col, r=4.5, hollow=False):
        if hollow:
            return f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="{r}" fill="#fff" stroke="{col}" stroke-width="2"/>'
        return f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="1.5"/>'
    def hline(s, y, col=None, dash="4,4", x1=None, x2=None, sw=1):
        col = col or C["ref"]
        a = s.X(x1) if x1 is not None else s.x0
        b = s.X(x2) if x2 is not None else s.x0 + s.w
        return f'<line x1="{a:.1f}" y1="{s.Y(y):.1f}" x2="{b:.1f}" y2="{s.Y(y):.1f}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="{sw}"/>'
    def vline(s, x, col=None, dash="4,4", y1=None, y2=None, sw=1):
        col = col or C["ref"]
        a = s.Y(y1) if y1 is not None else s.y0 + s.h
        b = s.Y(y2) if y2 is not None else s.y0
        return f'<line x1="{s.X(x):.1f}" y1="{a:.1f}" x2="{s.X(x):.1f}" y2="{b:.1f}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="{sw}"/>'
    def band(s, xa, xb, col, op=0.08):
        return (f'<rect x="{s.X(xa):.1f}" y="{s.y0}" width="{s.X(xb)-s.X(xa):.1f}" height="{s.h}" '
                f'fill="{col}" opacity="{op}"/>')

def T(x, y, txt, size=12, col=None, anchor="start", bold=False, extra=""):
    col = col or C["ink2"]
    b = ' font-weight="bold"' if bold else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" fill="{col}"{b}{extra}>{txt}</text>'

def sub(s):  # 下標
    return f'<tspan baseline-shift="sub" font-size="75%">{s}</tspan>'
def sup(s):
    return f'<tspan baseline-shift="super" font-size="70%">{s}</tspan>'

def box(x, y, w, h, fill, stroke, rx=9):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'

def legend_line(x, y, col, label, dash=None, sw=3):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x}" y1="{y}" x2="{x+34}" y2="{y}" stroke="{col}" stroke-width="{sw}"{d}/>'
            + T(x + 44, y + 4.5, label, 13, C["ink2"]))

def svg(w, h, body, defs=""):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>')

ARROW = ('<marker id="{id}" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto">'
         '<path d="M0,0 L9,4.5 L0,9 z" fill="{c}"/></marker>')

OUT = {}
CHECK = {}

# ---------------------------------------------------------------- 0 全景（SD-2016-4 實際數值）
def fig_overview():
    lam = [2 - math.sqrt(3), 2.0, 2 + math.sqrt(3)]
    phis = [[1, math.sqrt(3), 2], [1, 0, -1], [1, -math.sqrt(3), 2]]
    mvec = [1, 1, 0.5]
    om = [math.sqrt(230 * l) for l in lam]
    G, Ms = [], []
    for p in phis:
        L = sum(m * q for m, q in zip(mvec, p)); M = sum(m * q * q for m, q in zip(mvec, p))
        G.append(L / M); Ms.append(L * L / M / sum(mvec))
    CHECK["overview"] = dict(omega=[round(x, 2) for x in om], Gamma=[round(x, 3) for x in G],
                             Mstar_ratio=[round(x, 4) for x in Ms], sum=round(sum(Ms), 6))
    o = []
    o.append(T(215, 30, "物理座標 {u}：三條方程互相牽扯", 15, C["red"], "middle", True))
    o.append(T(690, 30, "模態座標 {q}：三個獨立的 SDOF", 15, C["grn"], "middle", True))
    o.append('<line x1="440" y1="44" x2="440" y2="370" stroke="#cfd8dc" stroke-dasharray="6,5" stroke-width="2"/>')
    # 左：三層剪力屋架
    gx, gy, hs = 120, 300, 70
    o.append(f'<line x1="{gx-30}" y1="{gy}" x2="{gx+230}" y2="{gy}" stroke="{C["axis"]}" stroke-width="3"/>')
    for i in range(14):
        xx = gx - 26 + i * 18
        o.append(f'<line x1="{xx}" y1="{gy}" x2="{xx-9}" y2="{gy+9}" stroke="{C["axis"]}"/>')
    labels = ["m", "m", "m/2"]
    for j in range(3):
        yb, yt = gy - j * hs, gy - (j + 1) * hs
        for cx in (gx + 40, gx + 160):
            o.append(f'<line x1="{cx}" y1="{yb}" x2="{cx}" y2="{yt+12}" stroke="{C["axis"]}" stroke-width="3"/>')
        o.append(box(gx + 20, yt - 2, 160, 24, "#ffcdd2", "#c62828", 5))
        o.append(T(gx + 100, yt + 15, f"m{sub(j+1)} = {labels[j]}", 12.5, "#b71c1c", "middle"))
        o.append(T(gx + 172, (yb + yt) / 2 + 12, f"k{sub(j+1)} = k", 12, C["mut"]))
        o.append(T(gx - 40, yt + 15, f"u{sub(j+1)}", 13, C["ink2"], "end"))
    # 牽扯箭頭
    for j in range(2):
        y1, y2 = gy - (j + 1) * hs + 22, gy - (j + 2) * hs + 22
        o.append(f'<path d="M{gx+5},{y1-4} C{gx-22},{y1-20} {gx-22},{y2+20} {gx+5},{y2+4}" fill="none" '
                 f'stroke="{C["red"]}" stroke-width="1.6" marker-start="url(#ovA)" marker-end="url(#ovA)"/>')
    o.append(T(215, 330, "[M]{ü} + [K]{u} = −[M]{ι}ü" + sub("g"), 13.5, C["ink"], "middle"))
    o.append(T(215, 350, "[K] 有非對角項（−k）→ 改一層，三層都動", 12, C["mut"], "middle"))
    o.append(T(215, 372, "解不開：一動全動", 13.5, C["red"], "middle", True))
    # 中間換座標箭頭
    o.append(f'<path d="M400,190 L470,190" stroke="{C["pur"]}" stroke-width="3" marker-end="url(#ovB)"/>')
    o.append(T(437, 166, "{u} = [Φ]{q}", 12.5, C["pur"], "middle", True))
    # 右：三個模態小圖
    cols = [C["grn"], C["ora"], C["red"]]
    for n in range(3):
        cx = 545 + n * 140
        o.append(box(cx - 62, 50, 124, 196, "#f1f8e9" if n == 0 else "#fff", "#c5e1a5" if n == 0 else "#e0e0e0", 8))
        o.append(T(cx, 70, f"Mode {n+1}", 13, cols[n], "middle", True))
        by, sh, sc = 222, 42, 17
        o.append(f'<line x1="{cx-40}" y1="{by}" x2="{cx+40}" y2="{by}" stroke="{C["axis"]}" stroke-width="2"/>')
        o.append(f'<line x1="{cx}" y1="{by}" x2="{cx}" y2="{by-3*sh}" stroke="{C["ref"]}" stroke-dasharray="3,3"/>')
        pts = [(cx, by)] + [(cx + sc * phis[n][j], by - (j + 1) * sh) for j in range(3)]
        o.append('<polyline fill="none" stroke="{}" stroke-width="2.4" points="{}"/>'.format(
            cols[n], " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)))
        for (a, b) in pts[1:]:
            o.append(f'<rect x="{a-11:.1f}" y="{b-3.5:.1f}" width="22" height="7" rx="2" fill="{cols[n]}"/>')
        o.append(T(cx, 238 + 0, "", 1))
    # 右下方程
    for n in range(3):
        cx = 545 + n * 140
        o.append(T(cx, 262, f"ω{sub(n+1)} = {om[n]:.2f} rad/s", 11.5, C["ink2"], "middle"))
        o.append(T(cx, 280, f"Γ{sub(n+1)} = {G[n]:.3f}", 11.5, C["ink2"], "middle"))
        o.append(T(cx, 298, f"M{sub(n+1)}*/M = {Ms[n]*100:.1f}%", 11.5, cols[n], "middle", True))
    o.append(T(685, 326, "q̈" + sub("n") + " + 2ξ" + sub("n") + "ω" + sub("n") + "q̇" + sub("n") + " + ω" + sub("n") + sup("2") + "q" + sub("n") + " = −Γ" + sub("n") + "ü" + sub("g"), 13.5, C["ink"], "middle"))
    o.append(T(685, 348, "每一條都跟 §1 的 SDOF 方程一模一樣", 12, C["mut"], "middle"))
    o.append(T(685, 372, "解得開：各自查反應譜，再用 SRSS／CQC 裝回去", 13.5, C["grn"], "middle", True))
    defs = ARROW.format(id="ovA", c=C["red"]) + ARROW.format(id="ovB", c=C["pur"])
    OUT["00_overview"] = svg(900, 386, "\n".join(o), defs)

# ---------------------------------------------------------------- 1 D–r
def fig_D():
    ax = Ax(70, 22, 540, 280, (0, 3), (0, 6), "cD")
    r = np.linspace(0, 3, 1501)
    D = lambda r, x: 1 / np.sqrt((1 - r * r) ** 2 + (2 * x * r) ** 2)
    xis = [(0.05, C["red"]), (0.10, C["ora"]), (0.20, C["blu"]), (0.50, C["grn"])]
    o = [ax.band(0, 0.6, C["blu"], 0.06), ax.band(0.8, 1.2, C["pur"], 0.07), ax.band(1.6, 3, C["ora"], 0.06)]
    o.append(T(ax.X(0.3), 40, "勁度控制", 12, C["blu"], "middle", True))
    o.append(T(ax.X(0.3), 56, "D ≈ 1", 11.5, C["blu"], "middle"))
    o.append(T(ax.X(1.0) + 30, ax.Y(4.3), "阻尼控制", 12, C["pur"], "start", True))
    o.append(T(ax.X(2.3), 40, "質量控制", 12, C["ora"], "middle", True))
    o.append(T(ax.X(2.3), 56, "D ≈ 1/(r²−1)", 11.5, C["ora"], "middle"))
    o.append(ax.frame([0, 0.5, 1, 1.5, 2, 2.5, 3], [0, 1, 2, 3, 4, 5, 6], "頻率比 r = Ω / ω", "放大係數 D"))
    o.append(ax.hline(1)); o.append(ax.vline(1))
    rr = np.linspace(1.35, 3, 200)
    o.append(ax.curve(rr, 1 / (rr * rr - 1), C["axis"], 1.3, "2,3", 0.8))
    pk = []
    for x, col in xis:
        o.append(ax.curve(r, D(r, x), col))
        rp = math.sqrt(1 - 2 * x * x); Dm = 1 / (2 * x * math.sqrt(1 - x * x)); pk.append((x, rp, Dm))
        if Dm < 6:
            o.append(ax.dot(rp, Dm, col))
    o.append(f'<line x1="{ax.X(1):.1f}" y1="{ax.Y(5.55):.1f}" x2="{ax.X(1):.1f}" y2="{ax.Y(5.95):.1f}" stroke="{C["red"]}" stroke-width="2" marker-end="url(#dA)"/>')
    o.append(T(ax.X(1) + 12, ax.Y(5.7), "ξ=0.05 峰值 10.0 ↑（超出圖框）", 11.5, C["red"], "start"))
    o.append(ax.clip())
    # legend
    lx = 640
    o.append(box(lx, 22, 268, 150, "#fafafa", "#cfd8dc"))
    o.append(T(lx + 16, 44, "ξ", 12, C["mut"])); o.append(T(lx + 112, 44, "r" + sub("peak"), 12, C["mut"])); o.append(T(lx + 190, 44, "D" + sub("max"), 12, C["mut"]))
    for i, (x, rp, Dm) in enumerate(pk):
        y = 68 + i * 28
        col = xis[i][1]
        o.append(f'<line x1="{lx+16}" y1="{y-4}" x2="{lx+44}" y2="{y-4}" stroke="{col}" stroke-width="3"/>')
        o.append(T(lx + 52, y, f"{x:.2f}", 12.5, C["ink2"]))
        o.append(T(lx + 112, y, f"{rp:.3f}", 12.5, C["ink2"]))
        o.append(T(lx + 190, y, f"{Dm:.2f}", 12.5, col, bold=True))
    o.append(box(lx, 186, 268, 116, "#fff8e1", "#ffe082"))
    o.append(T(lx + 16, 210, "峰值不在 r = 1，而在", 12.5, "#e65100", bold=True))
    o.append(T(lx + 16, 234, "r" + sub("peak") + " = √(1 − 2ξ²)", 13, C["ink"]))
    o.append(T(lx + 16, 258, "D" + sub("max") + " = 1 / [2ξ√(1 − ξ²)] ≈ 1/(2ξ)", 13, C["ink"]))
    o.append(T(lx + 16, 284, "ξ ≤ 0.2 時差 < 4%，考場用 1/(2ξ)", 11.5, C["mut"]))
    CHECK["D"] = [dict(xi=x, r_peak=round(rp, 4), Dmax=round(Dm, 3)) for x, rp, Dm in pk]
    OUT["01_D"] = svg(920, 350, "\n".join(o), ARROW.format(id="dA", c=C["red"]))

# ---------------------------------------------------------------- 2 TR
def fig_TR():
    ax = Ax(70, 22, 540, 280, (0, 4), (0, 4), "cTR")
    r = np.linspace(0, 4, 2001)
    TR = lambda r, x: np.sqrt((1 + (2 * x * r) ** 2) / ((1 - r * r) ** 2 + (2 * x * r) ** 2))
    s2 = math.sqrt(2)
    o = [ax.band(s2, 4, C["grn"], 0.07)]
    o.append(ax.frame([0, 1, s2, 2, 3, 4], [0, 1, 2, 3, 4], "頻率比 r = Ω / ω", "傳遞率 T" + sub("R"),
                      xfmt=lambda v: "√2" if abs(v - s2) < 1e-9 else f"{v:g}"))
    o.append(ax.hline(1)); o.append(ax.vline(s2, C["grn"], "6,4", sw=1.8))
    o.append(T(ax.X(s2) + 12, 44, "r &gt; √2 才叫隔振（T" + sub("R") + " &lt; 1）", 13, C["grn"], bold=True))
    o.append(T(ax.X(s2) + 12, 64, "此區阻尼越大，T" + sub("R") + " 反而越大", 12, C["grn"]))
    rr = np.where(np.abs(r - 1) < 1e-3, np.nan, r)
    o.append(ax.curve(rr, np.abs(1 / (1 - rr * rr)), C["axis"], 1.4, "5,4", 0.9))
    for x, col in [(0.05, C["red"]), (0.20, C["blu"]), (0.50, C["grn"])]:
        o.append(ax.curve(r, TR(r, x), col))
    o.append(ax.dot(s2, 1, C["ink"], 5.5))
    o.append(T(ax.X(s2) - 8, ax.Y(1) + 20, "(√2, 1)", 12, C["ink"], "end", True))
    # SD-2009-2 範例
    re = math.sqrt(11); tr = 1 / (re * re - 1)
    o.append(ax.dot(re, tr, C["pur"], 5))
    o.append(f'<line x1="{ax.X(re):.1f}" y1="{ax.Y(tr)-6:.1f}" x2="{ax.X(re):.1f}" y2="{ax.Y(0.62):.1f}" stroke="{C["pur"]}" stroke-width="1"/>')
    o.append(T(ax.X(re), ax.Y(0.62) - 22, "SD-2009-2 範例", 11.5, C["pur"], "middle", True))
    o.append(T(ax.X(re), ax.Y(0.62) - 6, f"r = {re:.3f} → T" + sub("R") + f" = {tr:.2f}", 11.5, C["pur"], "middle"))
    o.append(ax.clip())
    lx = 640
    o.append(box(lx, 22, 268, 128, "#fafafa", "#cfd8dc"))
    o.append(legend_line(lx + 16, 46, C["axis"], "ξ = 0（|1/(1−r²)|）", "5,4", 2))
    o.append(legend_line(lx + 16, 72, C["red"], "ξ = 0.05"))
    o.append(legend_line(lx + 16, 98, C["blu"], "ξ = 0.20"))
    o.append(legend_line(lx + 16, 124, C["grn"], "ξ = 0.50"))
    o.append(box(lx, 164, 268, 138, "#fff3e0", "#ffcc80"))
    o.append(T(lx + 16, 188, "為何所有曲線都過 (√2, 1)？", 13, "#e65100", bold=True))
    o.append(T(lx + 16, 212, "代 r² = 2：", 12.5, C["ink2"]))
    o.append(T(lx + 16, 234, "分母 (1−2)² + (2ξr)² = 1 + (2ξr)²", 12.5, C["ink2"]))
    o.append(T(lx + 16, 256, "＝ 分子 1 + (2ξr)²", 12.5, C["ink2"]))
    o.append(T(lx + 16, 282, "→ T" + sub("R") + " ≡ 1，與 ξ 無關", 13, "#e65100", bold=True))
    CHECK["TR"] = dict(example_r=round(re, 4), example_TR=round(tr, 4),
                       TR_at_sqrt2=[round(float(TR(s2, x)), 6) for x in (0.05, 0.2, 0.5)])
    OUT["02_TR"] = svg(920, 350, "\n".join(o))

# ---------------------------------------------------------------- SRS 數值
def srs(shape, tdT):
    w = 2 * math.pi; td = tdT
    tend = td + 1.2
    n = max(4000, int(tend / min(td, 1) * 1500))
    t = np.linspace(0, tend, n); dt = t[1] - t[0]
    if shape == "rect": p = np.where(t <= td, 1.0, 0.0)
    elif shape == "sine": p = np.where(t <= td, np.sin(np.pi * np.minimum(t, td) / td), 0.0)
    else: p = np.where(t <= td, 1 - np.abs(2 * t / td - 1), 0.0)
    c, s = math.cos(w * dt), math.sin(w * dt)
    u = v = umax = 0.0
    for i in range(n - 1):  # 分段線性外力之精確遞迴（無阻尼，k = 1）
        p0, sl = p[i], (p[i + 1] - p[i]) / dt
        a, b = u - p0, (v - sl) / w
        u = a * c + b * s + p0 + sl * dt
        v = -a * w * s + b * w * c + sl
        if abs(u) > umax: umax = abs(u)
    return umax

def fig_SRS():
    ax = Ax(70, 22, 560, 290, (0, 2), (0, 2.2), "cS")
    xs = np.concatenate([np.linspace(0.005, 0.5, 60), np.linspace(0.51, 2.0, 75)])
    data = {sh: [srs(sh, x) for x in xs] for sh in ("rect", "sine", "tri")}
    from scipy.optimize import minimize_scalar
    pk_s = minimize_scalar(lambda x: -srs("sine", x), bounds=(0.7, 0.9), method="bounded", options={"xatol": 1e-3})
    pk_t = minimize_scalar(lambda x: -srs("tri", x), bounds=(0.8, 1.0), method="bounded", options={"xatol": 1e-3})
    exB = 0.03 / (2 * math.pi / math.sqrt(200 / (100 / 981)))
    RB = srs("sine", exB)
    o = [ax.band(0, 0.25, C["blu"], 0.07)]
    o.append(T(ax.X(0.125), 40, "衝量區", 12.5, C["blu"], "middle", True))
    o.append(T(ax.X(0.125), 56, "t" + sub("d") + "/T &lt; 0.25", 11, C["blu"], "middle"))
    o.append(ax.frame([0, 0.25, 0.5, 1, 1.5, 2], [0, 0.5, 1, 1.5, 2], "t" + sub("d") + " / T（脈衝時距 ÷ 結構週期）", "R = u" + sub("max") + " / u" + sub("st")))
    # 衝量漸近線
    z = np.linspace(0, 0.36, 30)
    o.append(ax.curve(z, 2 * math.pi * z, C["red"], 1.2, "2,3"))
    o.append(ax.curve(z, 4 * z, C["blu"], 1.2, "2,3"))
    o.append(ax.curve(z, math.pi * z, C["grn"], 1.2, "2,3"))
    for sh, col in (("rect", C["red"]), ("sine", C["blu"]), ("tri", C["grn"])):
        o.append(ax.curve(xs, data[sh], col, 2.4))
    o.append(ax.dot(0.5, 2.0, C["red"])); o.append(T(ax.X(0.5) + 8, ax.Y(2.0) - 9, "2.00（t" + sub("d") + "/T ≥ 0.5 恆為 2）", 12, C["red"]))
    o.append(ax.dot(pk_s.x, -pk_s.fun, C["blu"])); o.append(T(ax.X(pk_s.x) + 8, ax.Y(-pk_s.fun) - 9, f"{-pk_s.fun:.2f} @ {pk_s.x:.2f}", 12, C["blu"]))
    o.append(ax.dot(pk_t.x, -pk_t.fun, C["grn"])); o.append(T(ax.X(pk_t.x) + 8, ax.Y(-pk_t.fun) - 9, f"{-pk_t.fun:.2f} @ {pk_t.x:.2f}", 12, C["grn"]))
    o.append(ax.vline(exB, C["ora"], "3,3", 0, RB, 1.3)); o.append(ax.hline(RB, C["ora"], "3,3", 0, exB, 1.3))
    o.append(ax.dot(exB, RB, C["ora"], 5.5))
    o.append(f'<line x1="{ax.X(exB)+5:.1f}" y1="{ax.Y(RB)+4:.1f}" x2="{ax.X(0.3):.1f}" y2="{ax.Y(0.5):.1f}" stroke="{C["ora"]}"/>')
    o.append(T(ax.X(0.3) + 4, ax.Y(0.5) + 14, f"範例 B：t" + sub("d") + f"/T = {exB:.3f} → R = {RB:.3f}", 12, C["ora"], bold=True))
    o.append(ax.clip())
    lx = 660
    o.append(box(lx, 22, 248, 104, "#fafafa", "#cfd8dc"))
    o.append(legend_line(lx + 16, 46, C["red"], "矩形脈衝"))
    o.append(legend_line(lx + 16, 72, C["blu"], "半正弦脈衝"))
    o.append(legend_line(lx + 16, 98, C["grn"], "對稱三角脈衝"))
    o.append(box(lx, 138, 248, 112, "#e3f2fd", "#90caf9"))
    o.append(T(lx + 16, 160, "虛線 = 衝量近似 R ≈ ω·Î/(k·u" + sub("st") + ")", 12.5, C["blu"], bold=True))
    o.append(T(lx + 16, 184, "矩形：R → 2π (t" + sub("d") + "/T)", 12.5, C["ink2"]))
    o.append(T(lx + 16, 206, "半正弦：R → 4 (t" + sub("d") + "/T)", 12.5, C["ink2"]))
    o.append(T(lx + 16, 228, "三角：R → π (t" + sub("d") + "/T)", 12.5, C["ink2"]))
    o.append(box(lx, 262, 248, 70, "#fff3e0", "#ffcc80"))
    o.append(T(lx + 16, 285, "右端：準靜態", 12.5, "#e65100", bold=True))
    o.append(T(lx + 16, 308, "緩加緩卸 → R → 1；矩形恆為 2", 12, C["ink2"]))
    o.append(T(lx + 16, 325, "（突加、突卸各踢一下）", 11.5, C["mut"]))
    CHECK["SRS"] = dict(halfsine_peak=[round(pk_s.x, 3), round(-pk_s.fun, 4)], tri_peak=[round(pk_t.x, 3), round(-pk_t.fun, 4)],
                        exampleB=[round(exB, 4), round(RB, 4)])
    OUT["03_SRS"] = svg(920, 360, "\n".join(o))

# ---------------------------------------------------------------- NEW 自由衰減
def fig_decay():
    xi = 0.25 / 6.0  # 以 δ = 0.2625 反推的 ξ
    delta = 0.25 * math.log(12.0 / 4.2)
    xi = delta / math.sqrt(4 * math.pi ** 2 + delta ** 2)
    ax = Ax(70, 20, 600, 240, (0, 4.6), (-13.5, 13.5), "cDec")
    w = 2 * math.pi / math.sqrt(1 - xi * xi)  # 令 T_d = 1
    wd = 2 * math.pi
    t = np.linspace(0, 4.6, 1200)
    env = 12.0 * np.exp(-xi * w * t)
    u = env * np.cos(wd * t)  # 峰值在 t = n·T_d（近似；ξ 小時誤差可忽略）
    o = [ax.frame([0, 1, 2, 3, 4], [-12, -6, 0, 6, 12], "時間 t / T" + sub("d"), "u（mm）", grid=True)]
    o.append(ax.hline(0, C["ref"], "none"))
    o.append(ax.curve(t, env, C["ora"], 1.5, "6,4")); o.append(ax.curve(t, -env, C["ora"], 1.5, "6,4"))
    o.append(ax.curve(t, u, C["blu"], 2.2))
    peaks = [12.0 * math.exp(-delta * n) for n in range(5)]
    for n, pv in enumerate(peaks):
        o.append(ax.dot(n, pv, C["red"] if n in (0, 4) else C["blu"], 5 if n in (0, 4) else 4))
        o.append(T(ax.X(n) + (8 if n else 8), ax.Y(pv) - 9, f"u{sub(n+1)} = {pv:.2f}" if n not in (0, 4) else f"u{sub(n+1)} = {pv:.1f}", 12,
                   C["red"] if n in (0, 4) else C["blu"], bold=n in (0, 4)))
    # 括號：4 個週期
    yb = ax.Y(-12.6)
    o.append(f'<path d="M{ax.X(0):.1f},{yb-6:.1f} L{ax.X(0):.1f},{yb:.1f} L{ax.X(4):.1f},{yb:.1f} L{ax.X(4):.1f},{yb-6:.1f}" fill="none" stroke="{C["red"]}" stroke-width="1.4"/>')
    o.append(T(ax.X(2), yb - 6, "跨 4 個週期（n = 4）", 12, C["red"], "middle", True))
    o.append(T(ax.X(3.6), ax.Y(9.6), "包絡線 12·e" + sup("−ξωt"), 12, C["ora"], "middle"))
    o.append(ax.clip())
    lx = 700
    o.append(box(lx, 20, 208, 240, "#f3e5f5", "#ce93d8"))
    o.append(T(lx + 14, 44, "從圖讀 ξ", 13, C["pur"], bold=True))
    o.append(T(lx + 14, 70, "每一週期振幅乘 e" + sup("−δ"), 12.5, C["ink2"]))
    o.append(T(lx + 14, 94, f"e" + sup("−δ") + f" = {math.exp(-delta):.3f}（剩 {math.exp(-delta)*100:.0f}%）", 12.5, C["ink2"]))
    o.append(T(lx + 14, 122, "δ = ¼ ln(12.0 / 4.2)", 12.5, C["ink"]))
    o.append(T(lx + 14, 144, f"  = {delta:.4f}", 12.5, C["ink"]))
    o.append(T(lx + 14, 172, f"ξ ≈ δ / 2π = {delta/(2*math.pi):.4f}", 12.5, C["pur"], bold=True))
    o.append(T(lx + 14, 196, f"精確 ξ = {xi:.4f}", 12.5, C["ink2"]))
    o.append(T(lx + 14, 224, "用 n 個週期取平均：", 11.5, C["mut"]))
    o.append(T(lx + 14, 242, "讀數誤差被 n 稀釋", 11.5, C["mut"]))
    CHECK["decay"] = dict(delta=round(delta, 5), xi_exact=round(xi, 5), peaks=[round(p, 3) for p in peaks])
    OUT["N1_decay"] = svg(920, 310, "\n".join(o))

# ---------------------------------------------------------------- NEW 範例 B 時間歷時
def fig_exB():
    W, k, p0, td = 100.0, 200.0, 20.0, 0.03
    m = W / 981; w = math.sqrt(k / m); ust = p0 / k; Om = math.pi / td; r = Om / w
    A = ust / (1 - r * r)
    ud = A * (math.sin(Om * td) - r * math.sin(w * td))
    vd = A * Om * (math.cos(Om * td) - math.cos(w * td))
    umax = math.sqrt(ud ** 2 + (vd / w) ** 2)
    tstar = td + math.atan2(vd / w, ud) / w
    phat = 2 * p0 * td / math.pi; uimp = phat / (m * w)
    t = np.linspace(0, 0.24, 1500)
    u = np.where(t <= td, A * (np.sin(Om * t) - r * np.sin(w * t)),
                 ud * np.cos(w * (t - td)) + vd / w * np.sin(w * (t - td)))
    # 上：外力
    axp = Ax(80, 20, 600, 60, (0, 0.24), (0, 24), "cBp")
    axu = Ax(80, 104, 600, 210, (0, 0.24), (-0.11, 0.13), "cBu")
    o = [axu.band(0, td, C["ora"], 0.10), axp.band(0, td, C["ora"], 0.10)]
    tp = np.linspace(0, td, 100)
    o.append(f'<path d="{axp.path(np.r_[0, tp, td, 0.24], np.r_[0, p0*np.sin(np.pi*tp/td), 0, 0])}" fill="#ffe0b2" stroke="{C["ora"]}" stroke-width="2"/>')
    o.append(f'<line x1="{axp.x0}" y1="{axp.Y(0)}" x2="{axp.x0+axp.w}" y2="{axp.Y(0)}" stroke="{C["axis"]}"/>')
    o.append(T(axp.x0 - 8, axp.Y(20) + 4, "p₀ = 20 tf", 11.5, C["ora"], "end"))
    o.append(T(axp.X(td) + 8, axp.Y(12), "p(t) = p₀ sin(πt/t" + sub("d") + ")，t" + sub("d") + " = 0.03 s", 12, C["ora"]))
    o.append(axu.frame([0, 0.03, 0.05, 0.1, 0.15, 0.2], [-0.1, -0.05, 0, 0.05, 0.1], "時間 t（s）", "u（cm）",
                       xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}"))
    o.append(axu.hline(0, C["ref"], "none"))
    o.append(axu.hline(ust, C["gry"], "2,3")); o.append(T(axu.X(0.085), axu.Y(ust) - 6, f"u" + sub("st") + f" = p₀/k = {ust:.3f}（R = 1）", 11.5, C["mut"], "start"))
    o.append(axu.hline(uimp, C["pur"], "6,4")); o.append(T(axu.X(0.085), axu.Y(uimp) + 15, f"衝量近似 {uimp:.4f}（+{(uimp/umax-1)*100:.1f}%）", 11.5, C["pur"], "start"))
    o.append(axu.curve(t, u, C["blu"], 2.4))
    o.append(axu.dot(td, ud, C["ora"], 5))
    o.append(T(axu.X(td) + 6, axu.Y(ud) + 18, f"t" + sub("d") + f"：u" + sub("d") + f" = {ud:.4f}", 12, C["ora"], bold=True))
    o.append(axu.dot(tstar, umax, C["red"], 5.5))
    o.append(T(axu.X(tstar) - 4, axu.Y(0.118), f"u" + sub("max") + f" = {umax:.4f} cm（t = {tstar:.4f} s）", 12.5, C["red"], "middle", True))
    o.append(T(axu.X(td / 2), axu.Y(-0.095), "強迫", 11.5, C["ora"], "middle", True))
    o.append(T(axu.X(0.13), axu.Y(-0.095), "自由振動階段：峰值在這裡", 12, C["blu"], "middle", True))
    o.append(axu.clip())
    lx = 710
    o.append(box(lx, 20, 198, 294, "#e3f2fd", "#90caf9"))
    o.append(T(lx + 14, 44, "這張圖要看三件事", 13, "#0d47a1", bold=True))
    o.append(T(lx + 14, 72, "① 強迫段很短（橙色）", 12.5, C["ink2"]))
    o.append(T(lx + 28, 92, f"t" + sub("d") + f"/T = {td/(2*math.pi/w):.3f}", 12, C["mut"]))
    o.append(T(lx + 14, 122, "② 峰值落在自由振動段", 12.5, C["ink2"]))
    o.append(T(lx + 28, 142, f"只算到 t" + sub("d") + f" 低估 {(1-ud/umax)*100:.0f}%", 12, C["mut"]))
    o.append(T(lx + 14, 172, "③ 衝量線略高於峰值", 12.5, C["ink2"]))
    o.append(T(lx + 28, 192, "衝量法恆為上界（保守）", 12, C["mut"]))
    o.append(T(lx + 14, 226, "自由段振幅：", 12.5, C["ink2"]))
    o.append(T(lx + 14, 248, "√(u" + sub("d") + "² + (u̇" + sub("d") + "/ω)²)", 12.5, C["ink"]))
    o.append(T(lx + 14, 276, f"ω = {w:.2f} rad/s", 12, C["mut"]))
    o.append(T(lx + 14, 296, f"u̇" + sub("d") + f" = {vd:.3f} cm/s", 12, C["mut"]))
    CHECK["exB"] = dict(omega=round(w, 3), r=round(r, 4), ud=round(ud, 5), vd=round(vd, 4), umax=round(umax, 5),
                        tstar=round(tstar, 4), uimp=round(uimp, 5))
    OUT["N2_exB"] = svg(920, 360, "\n".join(o))

# ---------------------------------------------------------------- 6 振態形狀（SD-2016-4）
def fig_modes():
    s3 = math.sqrt(3)
    phis = [[1, s3, 2], [1, 0, -1], [1, -s3, 2]]
    vals = [["1", "√3", "2"], ["1", "0", "−1"], ["1", "−√3", "2"]]
    lam = ["2 − √3", "2", "2 + √3"]; om = [7.85, 21.45, 29.30]; T_ = [0.800, 0.293, 0.214]
    cols = [C["grn"], C["ora"], C["red"]]
    o = [box(40, 10, 840, 30, "#eceff1", "#eceff1", 8),
         T(460, 30, "第 n 振態有 n − 1 個節點；頻率越高，相鄰樓層越常反向（層間變形越大）", 13, C["ink2"], "middle")]
    gy, hs, sc = 300, 72, 52
    for n in range(3):
        cx = 160 + n * 300
        col = cols[n]
        o.append(f'<line x1="{cx-120}" y1="{gy}" x2="{cx+120}" y2="{gy}" stroke="{C["axis"]}" stroke-width="3"/>')
        for i in range(13):
            xx = cx - 116 + i * 20
            o.append(f'<line x1="{xx}" y1="{gy}" x2="{xx-9}" y2="{gy+9}" stroke="{C["axis"]}"/>')
        o.append(f'<line x1="{cx}" y1="{gy}" x2="{cx}" y2="{gy-3*hs-10}" stroke="{C["ref"]}" stroke-dasharray="4,4"/>')
        for j in range(3):
            o.append(T(cx - 118, gy - (j + 1) * hs + 4, f"{j+1}F", 11, C["mut"]))
        pts = [(cx, gy)] + [(cx + sc * phis[n][j], gy - (j + 1) * hs) for j in range(3)]
        # 正負區塊著色
        poly = [(cx, gy)] + pts[1:] + [(cx, pts[-1][1])]
        o.append('<polygon points="{}" fill="{}" opacity="0.10"/>'.format(" ".join(f"{a:.1f},{b:.1f}" for a, b in poly), col))
        o.append('<polyline fill="none" stroke="{}" stroke-width="3" stroke-linejoin="round" points="{}"/>'.format(
            col, " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)))
        for j, (a, b) in enumerate(pts[1:]):
            o.append(f'<rect x="{a-26:.1f}" y="{b-5:.1f}" width="52" height="10" rx="3" fill="{col}"/>')
            if phis[n][j] != 0:
                o.append(f'<line x1="{cx}" y1="{b-14:.1f}" x2="{a:.1f}" y2="{b-14:.1f}" stroke="{col}" stroke-width="1.2" marker-end="url(#mA{n})"/>')
            lx = a + (32 if phis[n][j] >= 0 else -32)
            o.append(T(lx, b + 5, vals[n][j], 13, col, "start" if phis[n][j] >= 0 else "end", True))
        # 節點
        for j in range(3):
            y0, y1 = (0 if j == 0 else phis[n][j - 1]), phis[n][j]
            h0 = j
            if y0 * y1 < 0:
                fr = y0 / (y0 - y1); hz = h0 + fr
                yy = gy - hz * hs
                o.append(f'<circle cx="{cx}" cy="{yy:.1f}" r="6" fill="#fff" stroke="{col}" stroke-width="2.2"/>')
                o.append(T(cx + 10, yy + 4, f"節點 h = {hz:.2f}h", 11, col))
            if y1 == 0:
                yy = gy - (j + 1) * hs
                o.append(f'<circle cx="{cx}" cy="{yy:.1f}" r="7.5" fill="#fff" stroke="{col}" stroke-width="2.2"/>')
                o.append(T(cx + 34, yy - 10, "節點恰在 2F", 11, col))
        o.append(T(cx, 330, f"Mode {n+1}　λ = {lam[n]}", 14, col, "middle", True))
        o.append(T(cx, 350, f"ω = {om[n]:.2f} rad/s　T = {T_[n]:.3f} s", 12, C["ink2"], "middle"))
        o.append(T(cx, 368, f"{n} 個節點｜變號 {n} 次", 12, col, "middle"))
    defs = "".join(ARROW.format(id=f"mA{n}", c=c) for n, c in enumerate(cols))
    OUT["06_modes"] = svg(920, 378, "\n".join(o), defs)

# ---------------------------------------------------------------- 8 設計反應譜（SD-2014-1 參數）
def fig_spec():
    SDS, SD1 = 0.2, 0.12; T0 = SD1 / SDS
    def Sa(T):
        T = np.asarray(T, float)
        return np.where(T <= 0.2 * T0, SDS * (0.4 + 3 * T / T0),
               np.where(T <= T0, SDS, np.where(T <= 2.5 * T0, SD1 / np.maximum(T, 1e-9), 0.4 * SDS)))
    ax = Ax(70, 22, 600, 270, (0, 2.0), (0, 0.32), "cSp")
    Ts = np.linspace(0, 2.0, 2001)
    o = [ax.band(0, 0.2 * T0, C["red"], 0.07), ax.band(0.2 * T0, T0, C["grn"], 0.07),
         ax.band(T0, 2.5 * T0, C["blu"], 0.07), ax.band(2.5 * T0, 2.0, C["gry"], 0.08)]
    o.append(ax.frame([0, 0.12, 0.6, 1.0, 1.5, 2.0], [0, 0.08, 0.2], "週期 T（s）", "S" + sub("a") + "（g）",
                      xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}"))
    o.append(T(ax.X(0.06), ax.y0 + ax.h + 34, "0.2T₀", 10.5, C["red"], "middle"))
    o.append(T(ax.X(0.6), ax.y0 + ax.h + 34, "T₀ = S" + sub("D1") + "/S" + sub("DS"), 10.5, C["grn"], "middle"))
    o.append(T(ax.X(1.5), ax.y0 + ax.h + 34, "2.5T₀", 10.5, C["blu"], "middle"))
    for v in (0.12, 0.6, 1.5):
        o.append(ax.vline(v, C["gry"], "3,3"))
    o.append(ax.curve(Ts, Sa(Ts), "#0d47a1", 2.8))
    o.append(T(ax.X(0.36), ax.Y(0.225), "平台段 S" + sub("a") + " = S" + sub("DS") + " = 0.2", 12, C["grn"], "middle", True))
    o.append(T(ax.X(1.05), ax.Y(0.050), "S" + sub("a") + " = S" + sub("D1") + "/T = 0.12/T", 12, C["blu"], "middle", True))
    o.append(T(ax.X(1.05), ax.Y(0.050) + 18, "S" + sub("a") + " ∝ 1/T，S" + sub("d") + " ∝ T", 11.5, C["blu"], "middle"))
    o.append(T(ax.X(1.75), ax.Y(0.050), "下限 0.4S" + sub("DS"), 11.5, C["axis"], "middle", True))
    o.append(T(ax.X(1.75), ax.Y(0.050) + 18, "= 0.08（T ≥ 2.5T₀）", 11, C["axis"], "middle"))
    o.append(ax.dot(0.2, 0.2, "#0d47a1", 5.5))
    o.append(T(ax.X(0.2) + 4, ax.Y(0.2) + 22, "T₁ = 0.20 → 0.2", 11.5, "#0d47a1", "start", True))
    o.append(ax.clip())
    # 放大插圖 0–0.3 s
    ix = Ax(ax.X(0.86) + 46, ax.Y(0.312) + 24, ax.X(1.98) - ax.X(0.86) - 60, 76, (0, 0.3), (0.06, 0.22), "cSpI")
    o.append(f'<rect x="{ix.x0-46:.1f}" y="{ix.y0-24:.1f}" width="{ix.w+60:.1f}" height="{ix.h+56:.1f}" rx="8" fill="#fff" stroke="#cfd8dc"/>')
    o.append(T(ix.x0 - 38, ix.y0 - 8, "放大 0 ~ 0.3 s：高振態多落在上升段", 11.5, C["red"], bold=True))
    o.append(ix.band(0, 0.12, C["red"], 0.07))
    o.append(ix.frame([0, 0.075, 0.12, 0.2, 0.3], [0.08, 0.155, 0.2], "", "", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=True))
    tt = np.linspace(0, 0.3, 400)
    o.append(ix.curve(tt, Sa(tt), "#0d47a1", 2.4))
    o.append(ix.vline(0.075, C["ora"], "3,3", 0.06, 0.2))
    o.append(ix.dot(0.075, 0.2, C["red"], 5, hollow=True))
    o.append(T(ix.X(0.075) - 10, ix.Y(0.2) + 4, "✗ 0.2", 11.5, C["red"], "end", True))
    o.append(ix.dot(0.075, float(Sa(0.075)), C["ora"], 5.5))
    o.append(T(ix.X(0.075) + 8, ix.Y(0.155) + 16, "T₂ = 0.075 → 0.155 ✔", 11.5, C["ora"], "start", True))
    o.append(ix.dot(0.2, 0.2, "#0d47a1", 4.5))
    o.append(ix.clip())
    lx = 700
    o.append(box(lx, 22, 208, 132, "#fff3e0", "#ffcc80"))
    o.append(T(lx + 14, 46, "兩個對立的直覺", 13, "#e65100", bold=True))
    o.append(T(lx + 14, 72, "T 變長 → S" + sub("a") + " 下降", 12.5, C["ink2"]))
    o.append(T(lx + 14, 92, "（地震「力」變小）", 12, C["mut"]))
    o.append(T(lx + 14, 118, "但 S" + sub("d") + " = S" + sub("a") + "·g·T²/4π² 上升", 12.5, C["red"]))
    o.append(T(lx + 14, 138, "（地震「位移」變大）", 12, C["mut"]))
    o.append(box(lx, 166, 208, 126, "#e8f5e9", "#a5d6a7"))
    o.append(T(lx + 14, 190, "隔震的全部道理", 13, C["grn"], bold=True))
    o.append(T(lx + 14, 216, "在 S" + sub("D1") + "/T 段把 T 拉長 n 倍：", 12, C["ink2"]))
    o.append(T(lx + 14, 238, "力 → 1/n 倍", 12.5, C["ink2"]))
    o.append(T(lx + 14, 260, "位移 → n 倍 → 要留隔震縫", 12.5, C["ink2"]))
    o.append(T(lx + 14, 282, "（超過 2.5T₀ 後力不再下降）", 11, C["mut"]))
    CHECK["spec"] = dict(T0=T0, Sa_T2=float(Sa(0.075)), Sa_T1=float(Sa(0.2)), cont_at_2p5T0=[float(SD1 / 1.5), 0.4 * SDS])
    OUT["08_spec"] = svg(920, 352, "\n".join(o))

# ---------------------------------------------------------------- 9 SRSS（只改數字）— 在 build 腳本中以字串替換處理

# ---------------------------------------------------------------- 10 CQC ρ
def fig_rho():
    from scipy.optimize import brentq
    rho = lambda b, x: 8 * x * x * (1 + b) * b ** 1.5 / ((1 - b * b) ** 2 + 4 * x * x * b * (1 + b) ** 2)
    ax = Ax(70, 22, 560, 280, (1.0, 3.0), (0, 1.0), "cR")
    b = np.linspace(1.0, 3.0, 2001)
    o = [ax.band(1.0, 1.1, C["red"], 0.09)]
    o.append(T(ax.X(1.05), ax.y0 - 6, "差 10%", 10.5, C["red"], "middle", True))
    o.append(ax.frame([1.0, 1.1, 1.5, 2.0, 2.5, 3.0], [0, 0.1, 0.25, 0.5, 0.75, 1.0], "頻率比 β = ω" + sub("k") + " / ω" + sub("j") + "（≥ 1；ρ(β) = ρ(1/β)）", "相關係數 ρ" + sub("jk"),
                       xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}"))
    o.append(ax.hline(0.1, C["ora"], "6,4", sw=1.4))
    cr = {}
    for x, col in [(0.02, C["red"]), (0.05, C["blu"]), (0.10, C["grn"])]:
        o.append(ax.curve(b, rho(b, x), col, 2.4))
        bc = brentq(lambda q: rho(q, x) - 0.1, 1.0001, 5); cr[x] = bc
        o.append(ax.dot(bc, 0.1, col, 4.5))
        o.append(T(ax.X(bc) + 6, ax.Y(0.1) - 7, f"{bc:.2f}", 11.5, col, bold=True))
    # 範例 D
    rD = rho(1.1, 0.05)
    o.append(ax.dot(1.1, rD, C["ora"], 6))
    o.append(T(ax.X(1.1) + 10, ax.Y(rD) - 2, f"範例 D：β = 1.10, ξ = 5% → ρ = {rD:.3f}", 12, C["ora"], bold=True))
    # 範例 C
    rC = rho(0.831 / 0.285, 0.03)
    o.append(ax.dot(0.831 / 0.285, rC, C["pur"], 5.5))
    o.append(T(ax.X(0.831 / 0.285) + 4, ax.Y(0.17), "範例 C（ξ = 3%）", 11.5, C["pur"], "end", True))
    o.append(T(ax.X(0.831 / 0.285) + 4, ax.Y(0.17) + 15, f"β = 2.92 → ρ = {rC:.4f}", 11, C["pur"], "end"))
    o.append(f'<line x1="{ax.X(2.916):.1f}" y1="{ax.Y(0.17)+20:.1f}" x2="{ax.X(2.916):.1f}" y2="{ax.Y(rC)-7:.1f}" stroke="{C["pur"]}"/>')
    o.append(ax.clip())
    lx = 660
    o.append(box(lx, 22, 248, 104, "#fafafa", "#cfd8dc"))
    o.append(legend_line(lx + 16, 46, C["red"], "ξ = 2%（鋼結構）"))
    o.append(legend_line(lx + 16, 72, C["blu"], "ξ = 5%（RC，規範值）"))
    o.append(legend_line(lx + 16, 98, C["grn"], "ξ = 10%（含消能）"))
    o.append(box(lx, 138, 248, 112, "#fff3e0", "#ffcc80"))
    o.append(T(lx + 16, 162, "ρ 跌破 0.1 的頻率比", 13, "#e65100", bold=True))
    for i, x in enumerate((0.02, 0.05, 0.10)):
        o.append(T(lx + 16, 188 + i * 22, f"ξ = {x*100:.0f}%　→　β = {cr[x]:.2f}", 12.5, C["ink2"]))
    o.append(box(lx, 262, 248, 62, "#e8f5e9", "#a5d6a7"))
    o.append(T(lx + 16, 286, "阻尼越大，過渡帶越寬", 12.5, C["grn"], bold=True))
    o.append(T(lx + 16, 308, "→ 需要用 CQC 的範圍越大", 12, C["ink2"]))
    CHECK["rho"] = dict(cross=dict((str(k), round(v, 4)) for k, v in cr.items()), exD=round(rD, 4), exC=round(rC, 5))
    OUT["10_rho"] = svg(920, 360, "\n".join(o))

# ---------------------------------------------------------------- 11 Rayleigh 阻尼（SD-2025-3）
def fig_rayleigh():
    w1, w2, w3, xi = 14.5, 31.1, 46.2, 0.05
    a1 = 2 * xi / (w1 + w3); a0 = 2 * xi * w1 * w3 / (w1 + w3)
    xn = lambda w: a0 / (2 * w) + a1 * w / 2
    ws = math.sqrt(a0 / a1); xmin = math.sqrt(a0 * a1)
    ax = Ax(70, 22, 580, 280, (0, 70), (0, 0.12), "cRy")
    w = np.linspace(0.5, 70, 1500)
    o = [ax.band(w1, w3, C["ora"], 0.07)]
    o.append(ax.frame([0, w1, ws, w2, w3, 60, 70], [0, 0.02, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12], "ω（rad/s）", "ξ" + sub("n") + "（阻尼比）",
                       xfmt=lambda v: f"{v:.1f}" if v % 1 else f"{v:g}", yfmt=lambda v: f"{v:g}"))
    o.append(ax.hline(0.05, C["grn"], "6,4", sw=1.5))
    o.append(T(ax.X(70) - 2, ax.Y(0.05) + 16, "ξ = 5%", 12, C["grn"], "end", True))
    o.append(ax.curve(w, a0 / (2 * w), C["blu"], 1.8, "6,4"))
    o.append(ax.curve(w, a1 * w / 2, C["red"], 1.8, "6,4"))
    o.append(ax.curve(w, xn(w), C["pur"], 3))
    o.append(T(ax.X(6.5), ax.Y(0.112), "質量項 a₀/(2ω)", 12, C["blu"], "start", True))
    o.append(T(ax.X(56), ax.Y(0.030), "勁度項 a₁ω/2", 12, C["red"], "middle", True))
    o.append(T(ax.X(63), ax.Y(xn(63)) - 10, "總和（U 形）", 12.5, C["pur"], "middle", True))
    for ww, col in ((w1, C["grn"]), (w3, C["grn"])):
        o.append(ax.vline(ww, col, "3,3", 0, 0.05)); o.append(ax.dot(ww, 0.05, col, 5.5))
    o.append(ax.vline(w2, C["ora"], "3,3", 0, xn(w2)))
    o.append(ax.dot(w2, xn(w2), C["ora"], 6))
    o.append(T(ax.X(w2) + 8, ax.Y(xn(w2)) + 18, f"ξ₂ = {xn(w2)*100:.2f}% &lt; 5%", 12.5, C["ora"], "start", True))
    o.append(ax.dot(ws, xmin, C["pur"], 5, hollow=True))
    o.append(T(ax.X(ws) - 6, ax.Y(xmin) + 20, f"最低 {xmin*100:.2f}%", 11.5, C["pur"], "end"))
    o.append(T(ax.X((w1 + w3) / 2), ax.Y(0.002) - 4, "ω₁ ~ ω₃ 之間：ξ &lt; 5%", 11.5, C["ora"], "middle"))
    o.append(T(ax.X(58), ax.Y(0.085), "ω &gt; ω₃：ξ 急升", 11.5, C["red"], "middle"))
    o.append(T(ax.X(58), ax.Y(0.085) + 15, "高頻反應被過度壓抑", 11, C["red"], "middle"))
    o.append(ax.clip())
    lx = 680
    o.append(box(lx, 22, 228, 150, "#f3e5f5", "#ce93d8"))
    o.append(T(lx + 14, 46, "SD-2025-3 數值", 13, C["pur"], bold=True))
    o.append(T(lx + 14, 72, f"a₀ = {a0:.3f} s⁻¹", 12.5, C["ink2"]))
    o.append(T(lx + 14, 94, f"a₁ = {a1*1000:.3f}×10⁻³ s", 12.5, C["ink2"]))
    o.append(T(lx + 14, 120, f"ω* = √(a₀/a₁) = {ws:.1f} rad/s", 12.5, C["ink"]))
    o.append(T(lx + 14, 142, f"　 = √(ω₁ω₃)（ξ₁ = ξ₃ 時）", 12, C["mut"]))
    o.append(T(lx + 14, 164, f"ξ" + sub("min") + f" = √(a₀a₁) = {xmin:.4f}", 12.5, C["ink"]))
    o.append(box(lx, 184, 228, 118, "#fff3e0", "#ffcc80"))
    o.append(T(lx + 14, 208, "讀圖口訣", 13, "#e65100", bold=True))
    o.append(T(lx + 14, 232, "指定兩點 → 中間必低", 12.5, C["ink2"]))
    o.append(T(lx + 14, 254, "兩點之外 → 必高", 12.5, C["ink2"]))
    o.append(T(lx + 14, 280, "所以 ω₁、ω₃ 要框住", 12, C["mut"]))
    o.append(T(lx + 14, 296, "所有重要模態", 12, C["mut"]))
    CHECK["rayleigh"] = dict(a0=round(a0, 5), a1=round(a1, 7), xi1=round(xn(w1), 6), xi2=round(xn(w2), 5), xi3=round(xn(w3), 6),
                             wstar=round(ws, 3), ximin=round(xmin, 5))
    OUT["11_rayleigh"] = svg(920, 360, "\n".join(o))

# ---------------------------------------------------------------- 12 決策流程（重排）
def fig_flow():
    A = 'marker-end="url(#fA)"'
    L = lambda pts: '<polyline fill="none" stroke="#546e7a" stroke-width="2" points="{}" {}/>'.format(
        " ".join(f"{a},{b}" for a, b in pts), A)
    Ln = lambda pts: '<polyline fill="none" stroke="#546e7a" stroke-width="2" points="{}"/>'.format(" ".join(f"{a},{b}" for a, b in pts))
    def dia(cx, cy, hw, hh, t1, t2=None):
        s = f'<polygon points="{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}" fill="#fff3e0" stroke="#ef6c00" stroke-width="1.8"/>'
        if t2:
            s += T(cx, cy - 4, t1, 13, "#e65100", "middle") + T(cx, cy + 15, t2, 11.5, "#795548", "middle")
        else:
            s += T(cx, cy + 5, t1, 13, "#e65100", "middle")
        return s
    o = []
    o.append(box(350, 12, 200, 36, "#eceff1", "#90a4ae", 8)); o.append(T(450, 35, "讀題", 14, C["ink2"], "middle", True))
    o.append(L([(450, 48), (450, 72)]))
    o.append(dia(450, 116, 200, 42, "結構是連續體（梁／橋墩）", "還是集中質量？"))
    o.append(L([(250, 116), (135, 116), (135, 184)])); o.append(T(200, 108, "連續體", 12, C["red"], "middle"))
    o.append(box(20, 188, 230, 116, "#f3e5f5", "#ce93d8", 8))
    o.append(T(135, 210, "§7 Rayleigh / Ritz", 13, "#4a148c", "middle", True))
    o.append(T(135, 232, "猜 ψ(x)，只須滿足幾何 BC", 11.5, C["ink2"], "middle"))
    o.append(T(135, 252, "m* = ∫m̄ψ²dx + Σm" + sub("i") + "ψ" + sub("i") + "²", 11.5, C["ink2"], "middle"))
    o.append(T(135, 272, "k* = ∫EI(ψ″)²dx − N∫(ψ′)²dx", 11.5, C["ink2"], "middle"))
    o.append(T(135, 294, "ω² = k*/m*（上界）", 12, "#4a148c", "middle", True))
    o.append(L([(450, 158), (450, 184)])); o.append(T(462, 176, "集中質量", 12, C["grn"]))
    o.append(dia(450, 228, 170, 42, "獨立自由度有幾個？", "（先做靜態凝縮 §2.6）"))
    # 1 個 → 正下方
    o.append(L([(450, 270), (450, 342)])); o.append(T(462, 296, "1 個", 12, C["blu"], bold=True))
    # §7 化約後匯入
    o.append(L([(135, 304), (135, 322), (444, 322)])); o.append(T(290, 316, "化約成 SDOF 後回主線", 11, C["mut"], "middle"))
    # N 個 → 右欄
    o.append(L([(620, 228), (765, 228), (765, 290)])); o.append(T(690, 220, "N 個", 12, C["red"], "middle", True))
    # SDOF 欄
    o.append(box(300, 346, 300, 32, "#e3f2fd", "#64b5f6", 6)); o.append(T(450, 367, "§1 SDOF：外力是哪一種？", 13, "#0d47a1", "middle", True))
    o.append(Ln([(450, 378), (450, 392)])); o.append(Ln([(113, 392), (505, 392)]))
    sub3 = [("無外力（自由振動）", ["ω = √(k/m)，T = 2π√(m/k)", "ω" + sub("d") + " = ω√(1−ξ²)", "δ = ln(u" + sub("i") + "/u" + sub("i+1") + ") ≈ 2πξ"]),
            ("諧和／基礎激振", ["r = Ω/ω（外 ÷ 己）", "D = 1/√[(1−r²)² + (2ξr)²]", "隔振要 r &gt; √2"]),
            ("任意／衝擊", ["t" + sub("d") + "/T &lt; 0.25 → 衝量近似", "分段外力 → 兩階段法", "其餘 → Duhamel 積分"])]
    for i, (h, lines) in enumerate(sub3):
        x = 20 + i * 196; cx = x + 93
        o.append(L([(cx, 392), (cx, 406)]))
        o.append(box(x, 410, 186, 100, "#e8f5e9", "#a5d6a7", 7))
        o.append(T(cx, 432, h, 12.5, "#1b5e20", "middle", True))
        for k_, ln in enumerate(lines):
            o.append(T(cx, 456 + k_ * 20, ln, 11.3, C["ink2"], "middle"))
    o.append(box(20, 530, 578, 92, "#fff8e1", "#ffe082", 8))
    o.append(T(36, 554, "SDOF 三個出口都附免費驗算（§1）", 12.5, "#e65100", bold=True))
    o.append(T(36, 578, "• 任何非共振衝擊 R ≤ 2（突加定力恰為 2）　• 共振峰 D" + sub("max") + " ≈ 1/(2ξ)", 12, C["ink2"]))
    o.append(T(36, 600, "• T" + sub("R") + " &lt; 1 必須 r &gt; √2　• Rayleigh 法頻率只會偏高（上界）", 12, C["ink2"]))
    # MDOF 欄
    o.append(box(640, 294, 250, 78, "#e3f2fd", "#64b5f6", 8))
    o.append(T(765, 316, "§2 特徵值問題", 13, "#0d47a1", "middle", True))
    o.append(T(765, 338, "det([K] − ω²[M]) = 0（先非因次化）", 11.3, C["ink2"], "middle"))
    o.append(T(765, 358, "→ ω" + sub("n") + "、{φ}" + sub("n") + "（數節點檢查）", 11.3, C["ink2"], "middle"))
    o.append(L([(765, 372), (765, 394)]))
    o.append(dia(765, 434, 125, 38, "題目要什麼？", "只要 ω" + sub("n") + "、φ" + sub("n") + " → 到此結束"))
    o.append(L([(765, 472), (765, 498)])); o.append(T(777, 490, "要地震反應", 12, C["grn"]))
    o.append(box(640, 502, 250, 32, "#f3e5f5", "#ce93d8", 6))
    o.append(T(765, 523, "§3 解耦 → §4 算 Γ" + sub("n") + "、M" + sub("n") + "*", 12.5, "#4a148c", "middle", True))
    o.append(L([(765, 534), (765, 554)]))
    o.append(box(640, 558, 250, 52, "#e3f2fd", "#64b5f6", 6))
    o.append(T(765, 579, "§5 查 S" + sub("a") + "(T" + sub("n") + ")（高振態多在上升段）", 12, "#0d47a1", "middle", True))
    o.append(T(765, 599, "R" + sub("n") + " = Γ" + sub("n") + "{φ}" + sub("n") + "·S" + sub("d") + "　V" + sub("b,n") + " = M" + sub("n") + "*S" + sub("a"), 11.5, C["ink2"], "middle"))
    o.append(L([(765, 610), (765, 632)]))
    o.append(dia(765, 668, 125, 36, "累積 ΣM" + sub("n") + "* ≥ 90%？"))
    o.append(Ln([(640, 668), (618, 668), (618, 584)])); o.append(L([(618, 584), (636, 584)]))
    o.append(T(612, 640, "否：加模態", 11.5, C["red"], "end", True))
    o.append(L([(765, 704), (765, 730)])); o.append(T(777, 722, "是", 12, C["grn"], bold=True))
    o.append(dia(765, 768, 125, 38, "相鄰頻率相差 &gt; 10%？", "（β &gt; 1.1）"))
    o.append(L([(765, 806), (765, 834)])); o.append(T(777, 826, "是", 12, C["grn"], bold=True))
    o.append(Ln([(640, 768), (500, 768)])); o.append(L([(500, 768), (500, 834)])); o.append(T(570, 760, "否", 12, C["red"], "middle", True))
    o.append(box(665, 838, 200, 50, "#e8f5e9", "#a5d6a7", 7))
    o.append(T(765, 858, "SRSS", 13, C["grn"], "middle", True)); o.append(T(765, 878, "R = √ΣR" + sub("n") + "²", 11.5, "#33691e", "middle"))
    o.append(box(400, 838, 200, 50, "#ffebee", "#ef9a9a", 7))
    o.append(T(500, 858, "CQC（算 ρ" + sub("jk") + "）", 13, C["red"], "middle", True)); o.append(T(500, 878, "R" + sub("n") + " 帶正負號代入", 11.5, "#b71c1c", "middle"))
    OUT["12_flow"] = svg(900, 900, "\n".join(o), '<marker id="fA" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#546e7a"/></marker>')

# ---------------------------------------------------------------- NEW Rayleigh 假設形狀
def fig_shapes():
    bL, sg = 1.875104069, 0.734095514
    x = np.linspace(0, 1, 400)
    ex = (np.cosh(bL * x) - np.cos(bL * x) - sg * (np.sinh(bL * x) - np.sin(bL * x))); ex = ex / ex[-1]
    cosS = 1 - np.cos(np.pi * x / 2)
    uni = (6 * x ** 2 - 4 * x ** 3 + x ** 4) / 3
    tip = (3 * x ** 2 - x ** 3) / 2
    from scipy.integrate import quad
    def coef(psi, d2):
        return math.sqrt(quad(lambda s: d2(s) ** 2, 0, 1)[0] / quad(lambda s: psi(s) ** 2, 0, 1)[0])
    cs = {"cos": coef(lambda s: 1 - math.cos(math.pi * s / 2), lambda s: (math.pi / 2) ** 2 * math.cos(math.pi * s / 2)),
          "tip": coef(lambda s: (3 * s * s - s ** 3) / 2, lambda s: 3 * (1 - s)),
          "uni": coef(lambda s: (6 * s * s - 4 * s ** 3 + s ** 4) / 3, lambda s: 4 * (1 - s) ** 2)}
    exact = bL ** 2
    # 左：懸臂柱（x 向上，位移向右）
    gx, gy, Hh, Ww = 90, 330, 290, 210
    o = []
    o.append(f'<rect x="{gx-40}" y="{gy}" width="110" height="14" fill="#cfd8dc"/>')
    for i in range(7):
        o.append(f'<line x1="{gx-36+i*16}" y1="{gy+14}" x2="{gx-44+i*16}" y2="{gy+24}" stroke="{C["axis"]}"/>')
    o.append(f'<line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy-Hh-10}" stroke="{C["ref"]}" stroke-dasharray="4,4"/>')
    def P(y):
        return " ".join(f"{gx+Ww*v:.1f},{gy-Hh*s:.1f}" for s, v in zip(x, y))
    o.append(f'<polyline fill="none" stroke="{C["ink"]}" stroke-width="5" opacity="0.25" points="{P(ex)}"/>')
    o.append(f'<polyline fill="none" stroke="{C["ora"]}" stroke-width="2.2" points="{P(cosS)}"/>')
    o.append(f'<polyline fill="none" stroke="{C["grn"]}" stroke-width="2.2" stroke-dasharray="7,4" points="{P(tip)}"/>')
    o.append(f'<polyline fill="none" stroke="{C["blu"]}" stroke-width="2.2" stroke-dasharray="2,3" points="{P(uni)}"/>')
    o.append(T(gx + Ww + 6, gy - Hh + 4, "ψ(L) = 1", 12, C["ink2"]))
    o.append(T(gx - 8, gy - Hh, "x = L", 11.5, C["mut"], "end")); o.append(T(gx - 8, gy - 4, "x = 0", 11.5, C["mut"], "end"))
    o.append(T(gx + 14, gy - 14, "ψ(0) = 0、ψ′(0) = 0（幾何 BC 必滿足）", 11, C["mut"]))
    # 放大差異（右下小圖）：ψ − 精確
    ax = Ax(400, 40, 220, 120, (0, 1), (-0.06, 0.06), "cSh")
    o.append(T(400, 28, "形狀誤差 ψ(x) − φ" + sub("精確") + "(x)（放大）", 12, C["ink2"], bold=True))
    o.append(ax.frame([0, 0.5, 1], [-0.05, 0, 0.05], "x / L", "", yfmt=lambda v: f"{v:+.2f}" if v else "0"))
    o.append(ax.hline(0, C["ink"], "none", sw=1.2))
    o.append(ax.curve(x, cosS - ex, C["ora"], 2)); o.append(ax.curve(x, tip - ex, C["grn"], 2, "7,4")); o.append(ax.curve(x, uni - ex, C["blu"], 2, "2,3"))
    o.append(ax.clip())
    # 數軸：頻率係數
    ny = 292; nx0, nx1 = 400, 640; v0, v1 = 3.50, 3.70
    NX = lambda v: nx0 + (v - v0) / (v1 - v0) * (nx1 - nx0)
    o.append(T(400, 220, "ω₁ 的係數（× √(EI/m̄L⁴)）", 12, C["ink2"], bold=True))
    o.append(f'<line x1="{nx0}" y1="{ny}" x2="{nx1}" y2="{ny}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    for v in (3.50, 3.55, 3.60, 3.65, 3.70):
        o.append(f'<line x1="{NX(v):.1f}" y1="{ny}" x2="{NX(v):.1f}" y2="{ny+5}" stroke="{C["axis"]}"/>')
        o.append(T(NX(v), ny + 19, f"{v:.2f}", 10.5, C["mut"], "middle"))
    o.append(f'<line x1="{NX(exact):.1f}" y1="{ny-30}" x2="{NX(exact):.1f}" y2="{ny}" stroke="{C["ink"]}" stroke-width="2"/>')
    o.append(T(NX(exact), ny - 36, f"精確 {exact:.3f}", 11, C["ink"], "middle", True))
    for key, col, dy in (("uni", C["blu"], -14), ("tip", C["grn"], -14), ("cos", C["ora"], -14)):
        o.append(f'<circle cx="{NX(cs[key]):.1f}" cy="{ny}" r="5.5" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
    o.append(T(NX(cs["uni"]) + 4, ny + 36, f"{cs['uni']:.3f}", 11, C["blu"], "start", True))
    o.append(T(NX(cs["tip"]), ny - 12, f"{cs['tip']:.3f}", 11, C["grn"], "middle", True))
    o.append(T(NX(cs["cos"]), ny - 12, f"{cs['cos']:.3f}", 11, C["ora"], "middle", True))
    o.append(T(520, ny + 56, "全部落在精確值右邊 → 上界定理", 12, C["red"], "middle", True))
    # 圖例
    lx = 670
    o.append(box(lx, 22, 238, 300, "#fafafa", "#cfd8dc"))
    o.append(f'<line x1="{lx+14}" y1="{48}" x2="{lx+48}" y2="{48}" stroke="{C["ink"]}" stroke-width="5" opacity="0.25"/>')
    o.append(T(lx + 56, 52, "精確第一振態", 12.5, C["ink2"], bold=True))
    o.append(T(lx + 56, 70, f"誤差 0（{exact:.3f}）", 11.5, C["mut"]))
    items = [(C["ora"], None, "1 − cos(πx/2L)", "cos", "講義範例"),
             (C["grn"], "7,4", "3Lx² − x³", "tip", "頂端集中力的靜變形"),
             (C["blu"], "2,3", "6L²x² − 4Lx³ + x⁴", "uni", "均布側力（自重）靜變形")]
    for i, (col, dash, nm, key, note) in enumerate(items):
        y = 106 + i * 66
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o.append(f'<line x1="{lx+14}" y1="{y-4}" x2="{lx+48}" y2="{y-4}" stroke="{col}" stroke-width="2.6"{d}/>')
        o.append(T(lx + 56, y, nm, 12.5, col, bold=True))
        o.append(T(lx + 56, y + 18, note, 11.5, C["mut"]))
        o.append(T(lx + 56, y + 36, f"{cs[key]:.3f}（+{(cs[key]/exact-1)*100:.1f}%）", 12, C["ink2"]))
    o.append(T(lx + 14, 312, "越像真實振態 → 上界越緊", 12, C["red"], bold=True))
    CHECK["shapes"] = dict(exact=round(exact, 4), **{k: round(v, 4) for k, v in cs.items()},
                           err={k: round((v / exact - 1) * 100, 2) for k, v in cs.items()})
    OUT["N3_shapes"] = svg(920, 372, "\n".join(o))

if __name__ == "__main__":
    for fn in (fig_overview, fig_D, fig_TR, fig_SRS, fig_decay, fig_exB, fig_modes, fig_spec, fig_rho, fig_rayleigh, fig_flow, fig_shapes):
        fn()
    os.makedirs("figs_U1-3", exist_ok=True)
    for k, v in OUT.items():
        open(f"figs_U1-3/{k}.svg", "w", encoding="utf-8").write(v)
    json.dump(CHECK, open("figs_U1-3/check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(CHECK, ensure_ascii=False, indent=1))
