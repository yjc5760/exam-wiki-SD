# -*- coding: utf-8 -*-
"""lecture-SD-U1-1.html 的公式驅動 SVG 產生器（2026-10-24）。所有座標由公式計算；python lecture_U1_1_figs.py figs.json 輸出各圖 SVG 字串。"""
import math, json

def f(v): return f"{v:.1f}"
def poly(pts): return " ".join(f"{f(x)},{f(y)}" for x, y in pts)

GREEN, ORANGE, RED, BLUE, PURPLE, GREY = "#2e7d32", "#ef6c00", "#c62828", "#1565c0", "#6a1b9a", "#546e7a"

def marker(id_, color):
    return (f'<marker id="{id_}" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">'
            f'<path d="M0,0 L9,4.5 L0,9 z" fill="{color}"/></marker>')

def T(x, y, s, size=12.5, color="#37474f", anchor="start", bold=False, extra=""):
    b = ' font-weight="bold"' if bold else ""
    return f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{b}{extra}>{s}</text>'

def L(x1, y1, x2, y2, color="#90a4ae", w=1.5, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{color}" stroke-width="{w}"{d}{extra}/>'

def svg(w, h, body, label):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">\n' + "\n".join(body) + "\n</svg>"

def ground(x1, x2, y):
    out = [L(x1, y, x2, y, "#455a64", 3)]
    x = x1 + 4
    while x < x2:
        out.append(L(x, y, x - 9, y + 10, "#90a4ae", 1.2))
        x += 12
    return out

# ------------------------------------------------------------------ A. column stiffness
def fig_column():
    b = [f'<defs>{marker("mkA-r", RED)}{marker("mkA-p", PURPLE)}</defs>']
    b.append(L(450, 14, 450, 352, "#cfd8dc", 2, "6 5"))
    H, D = 210, 52                      # column height px, drawn Δ px
    yb, yt = 300, 300 - H
    panels = [
        dict(x0=95, title="兩端固接（樓版剛性、柱底固接）", tc="#0d47a1", col=BLUE,
             shape=lambda z: 3*z*z - 2*z**3, Mb=6, Mt=-6, k="k = 12EI / h³", pinned=False),
        dict(x0=545, title="柱底固接、柱頂鉸接（可自由轉動）", tc="#e65100", col=ORANGE,
             shape=lambda z: (3*z*z - z**3)/2, Mb=3, Mt=0, k="k = 3EI / h³", pinned=True),
    ]
    for p in panels:
        x0, col = p["x0"], p["col"]
        cx = x0 + 225 - 90
        b.append(T(x0 + 130, 34, p["title"], 15.5, p["tc"], "middle", True))
        b += ground(x0 + 5, x0 + 115, yb)
        b.append(L(x0 + 60, yb, x0 + 60, yt, "#b0bec5", 1.6, "5 4"))           # undeformed
        pts = [(x0 + 60 + D*p["shape"](i/40), yb - H*i/40) for i in range(41)]
        b.append(f'<polyline fill="none" stroke="{col}" stroke-width="3.6" points="{poly(pts)}"/>')
        # beam (rigid, translates by Δ, no rotation)
        bx = x0 + 60 + D
        b.append(f'<rect x="{f(bx-55)}" y="{f(yt-12)}" width="110" height="12" fill="#546e7a" rx="2"/>')
        if p["pinned"]:
            b.append(f'<circle cx="{f(bx)}" cy="{f(yt+4)}" r="6.5" fill="#fff" stroke="{col}" stroke-width="3"/>')
            b.append(T(bx + 12, yt + 24, "鉸：M = 0", 12, col))
        else:
            mid = pts[20]
            b.append(f'<circle cx="{f(mid[0])}" cy="{f(mid[1])}" r="5" fill="{col}"/>')
            b.append(T(mid[0] + 10, mid[1] + 4, "反曲點 h/2（M = 0）", 12, col))
        # F and Δ
        b.append(f'<path d="M{f(bx-110)} {f(yt-6)} h46" stroke="{RED}" stroke-width="3" marker-end="url(#mkA-r)"/>')
        b.append(T(bx - 122, yt - 1, "F", 14, RED, bold=True))
        yd = yt - 24
        b.append(L(x0 + 60, yd - 6, x0 + 60, yd + 6, PURPLE, 1.4))
        b.append(L(bx, yd - 6, bx, yd + 6, PURPLE, 1.4))
        b.append(L(x0 + 60, yd, bx, yd, PURPLE, 1.4))
        b.append(T((x0 + 60 + bx)/2, yd - 5, "Δ", 13, PURPLE, "middle", True))
        # moment diagram (linear), axis at mx
        mx, sc = x0 + 300, 9.5           # 1 unit (EIΔ/h²) = 9.5 px
        b.append(T(mx, yt - 34, "彎矩圖 M", 12.5, GREY, "middle", True))
        b.append(L(mx, yb, mx, yt, "#78909c", 1.6))
        mpts = [(mx + sc*(p["Mb"] + (p["Mt"] - p["Mb"])*i/20), yb - H*i/20) for i in range(21)]
        b.append(f'<polygon points="{poly([(mx, yb)] + mpts + [(mx, yt)])}" fill="{col}" fill-opacity="0.16" stroke="{col}" stroke-width="2"/>')
        b.append(T(mx + sc*p["Mb"]/2, yb + 17, f'{p["Mb"]}EIΔ/h²', 12, col, "middle", True))
        if p["Mt"]:
            b.append(T(mx + sc*p["Mt"]/2, yt - 8, f'{abs(p["Mt"])}EIΔ/h²', 12, col, "middle", True))
        else:
            b.append(T(mx + 6, yt + 4, "0", 12, col, bold=True))
        # result
        b.append(T(x0 + 175, 334, p["k"], 17, p["tc"], "middle", True))
        if p["pinned"]:
            b.append(T(x0 + 175, 354, "V = (3 + 0)EIΔ/h² ÷ h = 3EIΔ/h³", 12.5, GREY, "middle"))
        else:
            b.append(T(x0 + 175, 354, "V = (6 + 6)EIΔ/h² ÷ h = 12EIΔ/h³", 12.5, GREY, "middle"))
    b.append(f'<rect x="90" y="370" width="720" height="28" rx="7" fill="#e3f2fd" stroke="#90caf9"/>')
    b.append(T(450, 389, "柱剪力 V = (M頂 + M底) / h：兩端各貢獻 6 → 12；鉸接端貢獻 0、固接端只剩 3 → k 差 4 倍、T 差 2 倍", 13, "#0d47a1", "middle"))
    return svg(900, 404, b, "柱側向勁度：兩端固接與一端鉸接的變形與彎矩圖")

# ------------------------------------------------------------------ B. log decrement
def fig_logdec():
    xi = 0.03481; u0 = 12.0
    w = 2*math.pi; wd = w*math.sqrt(1 - xi*xi); TD = 2*math.pi/wd
    X0, X1, Y0 = 70, 820, 165            # plot origin (t=0,u=0)
    sx = (X1 - X0)/(4.4*TD); sy = 9.6   # px per mm
    u = lambda t: math.exp(-xi*w*t)*(u0*math.cos(wd*t) + xi*w*u0/wd*math.sin(wd*t))
    b = [f'<defs>{marker("mkB-p", PURPLE)}</defs>']
    # grid + ticks
    for mm in (-10, -5, 5, 10):
        y = Y0 - mm*sy
        b.append(L(X0, y, X1 + 20, y, "#eceff1", 1))
        b.append(T(X0 - 8, y + 4, f"{mm}", 11, "#78909c", "end"))
    b.append(L(X0, Y0, X1 + 25, Y0, "#90a4ae", 1.6)); b.append(L(X0, 30, X0, 300, "#90a4ae", 1.6))
    b.append(T(X1 + 30, Y0 + 4, "t", 13, GREY)); b.append(T(X0 - 8, 26, "u (mm)", 12, GREY, "end"))
    # peak line u0 e^{-ξωt} (true locus of peaks for release from rest)
    env = [(X0 + sx*t, Y0 - sy*u0*math.exp(-xi*w*t)) for t in [i*4.4*TD/120 for i in range(121)]]
    envn = [(x, 2*Y0 - y) for x, y in env]
    b.append(f'<polyline fill="none" stroke="#ef9a9a" stroke-width="1.8" stroke-dasharray="7 5" points="{poly(env)}"/>')
    b.append(f'<polyline fill="none" stroke="#ef9a9a" stroke-width="1.8" stroke-dasharray="7 5" points="{poly(envn)}"/>')
    b.append(T(420, 266, "峰值連線 ±u₀·e^(−ξωt)", 12.5, RED))
    curve = [(X0 + sx*t, Y0 - sy*u(t)) for t in [i*4.4*TD/600 for i in range(601)]]
    b.append(f'<polyline fill="none" stroke="{BLUE}" stroke-width="2.6" points="{poly(curve)}"/>')
    # peaks at t = n·T_D exactly (velocity zero)
    for n in range(5):
        t = n*TD; up = u0*math.exp(-xi*w*t); x = X0 + sx*t; y = Y0 - sy*up
        main = n in (0, 4)
        b.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{5 if main else 3.8}" fill="{GREEN if main else "#78909c"}"/>')
        if main:
            b.append(L(x, y, x, Y0, GREEN, 2))
        lab = f"u{'₁₂₃₄₅'[n]} = {up:.2f}" if not main else ("第 1 峰 u₁ = 12.0 mm" if n == 0 else "第 5 峰 u₅ = 5.0 mm")
        b.append(T(x + (8 if n == 0 else 0), y - 10, lab, 12 if not main else 12.5, GREEN if main else "#607d8b",
                   "start" if n == 0 else "middle", main))
    # T_D marker between peak 1 and 2 at bottom
    yT = Y0 + sy*u0*0.98 + 14
    xa, xb = X0, X0 + sx*TD
    b.append(L(xa, yT, xb, yT, "#455a64", 1.3)); b.append(L(xa, yT - 5, xa, yT + 5, "#455a64", 1.3)); b.append(L(xb, yT - 5, xb, yT + 5, "#455a64", 1.3))
    b.append(T((xa + xb)/2, yT + 15, "T_D（峰到峰）", 12, "#455a64", "middle"))
    # n = 4 bracket
    yb = 318
    xe = X0 + sx*4*TD
    b.append(L(X0, yb, xe, yb, PURPLE, 1.8)); b.append(L(X0, yb - 6, X0, yb + 6, PURPLE, 1.8)); b.append(L(xe, yb - 6, xe, yb + 6, PURPLE, 1.8))
    for n in range(1, 4):
        xx = X0 + sx*n*TD; b.append(L(xx, yb - 4, xx, yb + 4, "#ce93d8", 1.4))
    for n in range(4):
        b.append(T(X0 + sx*(n + 0.5)*TD, yb + 17, f"{n+1}", 12, PURPLE, "middle", True))
    b.append(T((X0 + xe)/2, yb - 8, "n = 4 個間隔（5 個峰）", 12.5, PURPLE, "middle", True))
    # ratio box
    b.append(f'<rect x="640" y="24" width="230" height="70" rx="8" fill="#f3e5f5" stroke="#ce93d8"/>')
    b.append(T(755, 44, "相鄰峰比值固定", 12.5, PURPLE, "middle", True))
    b.append(T(755, 64, "12.00 / 9.64 = 9.64 / 7.75 = … = 1.245", 11.5, "#4a148c", "middle"))
    b.append(T(755, 83, "= e^δ，δ = 0.2189 → ξ = 3.48%", 11.5, "#4a148c", "middle"))
    return svg(900, 345, b, "對數衰減率：第1峰到第5峰的自由振動衰減")

# ------------------------------------------------------------------ C. Rayleigh damping curve
def fig_rayleigh():
    w1, w2, w3, xi = 14.5, 31.1, 46.2, 0.05
    a0 = 2*xi*w1*w3/(w1 + w3); a1 = 2*xi/(w1 + w3)
    xs = lambda w: lambda_ if False else None
    X0, X1, Y0, Y1 = 80, 800, 300, 40
    WMAX, XMAX = 60.0, 0.12
    px = lambda w: X0 + (X1 - X0)*w/WMAX
    py = lambda z: Y0 - (Y0 - Y1)*min(z, XMAX + 0.02)/XMAX
    b = []
    # shade region between anchors
    b.append(f'<rect x="{f(px(w1))}" y="{Y1}" width="{f(px(w3)-px(w1))}" height="{Y0-Y1}" fill="#ede7f6" opacity="0.6"/>')
    b.append(T((px(w1) + px(w3))/2, Y1 + 16, "錨定點之間：ξ &lt; 5%（低估）", 12, PURPLE, "middle", True))
    b.append(T((px(w3) + X1)/2 + 4, Y1 + 16, "錨定點外：高估", 12, RED, "middle", True))
    for p in range(2, 13, 2):
        y = py(p/100)
        b.append(L(X0, y, X1, y, "#eceff1", 1))
        b.append(T(X0 - 8, y + 4, f"{p}%", 11, "#78909c", "end"))
    for wv in range(0, 61, 10):
        x = px(wv); b.append(L(x, Y0, x, Y0 + 5, "#90a4ae", 1)); b.append(T(x, Y0 + 18, str(wv), 11, "#78909c", "middle"))
    b.append(L(X0, Y0, X1, Y0, "#90a4ae", 1.6)); b.append(L(X0, Y1 - 8, X0, Y0, "#90a4ae", 1.6))
    b.append(L(X0, py(xi), X1, py(xi), "#b0bec5", 1.4, "5 4"))
    b.append(T((X0 + X1)/2, Y0 + 40, "圓頻率 ω (rad/s)", 13, GREY, "middle"))
    b.append(T(X0 - 44, (Y0 + Y1)/2, "ξ", 15, GREY, "middle", True))
    ws = [3 + i*(WMAX - 3)/300 for i in range(301)]
    m_pts = [(px(w), py(a0/(2*w))) for w in ws if a0/(2*w) <= XMAX + 0.005]
    k_pts = [(px(w), py(a1*w/2)) for w in ws]
    t_pts = [(px(w), py(a0/(2*w) + a1*w/2)) for w in ws if a0/(2*w) + a1*w/2 <= XMAX + 0.005]
    b.append(f'<polyline fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="7 4" points="{poly(m_pts)}"/>')
    b.append(f'<polyline fill="none" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="7 4" points="{poly(k_pts)}"/>')
    b.append(f'<polyline fill="none" stroke="{BLUE}" stroke-width="3.4" points="{poly(t_pts)}"/>')
    b.append(T(px(5.6) + 6, py(0.098), "質量項 a₀/(2ω)", 12.5, GREEN, bold=True))
    b.append(T(px(52), py(a1*52/2) + 22, "勁度項 a₁ω/2", 12.5, ORANGE, "middle", True))
    b.append(T(px(54), py(a0/108 + a1*27) - 12, "總和 ξ(ω)", 13.5, BLUE, "middle", True))
    wstar = math.sqrt(a0/a1); xmin = math.sqrt(a0*a1)
    xi2 = a0/(2*w2) + a1*w2/2
    for wv, z, c, lab, dx, dy, anc in [
        (w1, xi, RED, f"ω₁ = {w1}：錨定 5%", 6, -12, "start"),
        (w3, xi, RED, f"ω₃ = {w3}：錨定 5%", -6, -12, "end"),
        (w2, xi2, PURPLE, f"ω₂ = {w2} → {xi2*100:.2f}%", 8, 22, "start"),
        (wstar, xmin, "#37474f", f"最低點 ω* = √(ω₁ω₃) = {wstar:.1f}，ξmin = √(a₀a₁) = {xmin*100:.2f}%", 0, 0, "middle")]:
        b.append(f'<circle cx="{f(px(wv))}" cy="{f(py(z))}" r="{6 if c != "#37474f" else 4.5}" fill="{c}"/>')
        if c in (PURPLE, "#37474f"):
            b.append(L(px(wv), py(z), px(wv), Y0, c, 1, "3 3"))
        if c == "#37474f":
            b.append(T(px(wv) + 10, Y0 - 12, lab, 12, c, "middle"))
        else:
            b.append(T(px(wv) + dx, py(z) + dy, lab, 12, c, anc, True))
    b.append(f'<rect x="575" y="232" width="215" height="52" rx="7" fill="#fff" stroke="#cfd8dc"/>')
    b.append(T(682, 252, f"a₀ = {a0:.3f} s⁻¹", 12, "#37474f", "middle"))
    b.append(T(682, 272, f"a₁ = {a1*1000:.3f}×10⁻³ s", 12, "#37474f", "middle"))
    return svg(820, 360, b, "Rayleigh 阻尼比與頻率的關係"), dict(a0=a0, a1=a1, xi2=xi2, wstar=wstar, xmin=xmin)

# ------------------------------------------------------------------ D. DMF & TR (linear)
def dmf(r, z): return 1/math.sqrt((1 - r*r)**2 + (2*z*r)**2)
def tr(r, z): return math.sqrt(1 + (2*z*r)**2)*dmf(r, z)

def peak(fn, z):
    best = (0, 0)
    for i in range(1, 40000):
        r = i*2e-4*0 + i/20000*2
        v = fn(r, z)
        if v > best[1]: best = (r, v)
    return best

def fig_dmf_tr():
    zs = [(0.05, RED), (0.10, ORANGE), (0.20, GREEN)]
    b = []
    YMAX = 11
    res = {}
    for k, (title, fn, tc, x0) in enumerate([("DMF：外力直接打在結構上（消能減震的舞台）", dmf, "#0d47a1", 60),
                                                ("TR：地基在動（基礎隔震的舞台）", tr, "#b71c1c", 510)]):
        X0, X1, Y0, Y1 = x0, x0 + 330, 300, 70
        px = lambda r: X0 + (X1 - X0)*r/4
        py = lambda v: Y0 - (Y0 - Y1)*min(v, YMAX)/YMAX
        b.append(T(x0 + 165, 34, title, 15, tc, "middle", True))
        for v in (1, 2.5, 5, 10):
            b.append(L(X0, py(v), X1, py(v), "#eceff1", 1))
            b.append(T(X0 - 7, py(v) + 4, f"{v:g}", 11, "#78909c", "end"))
        for r in (1, 2, 3, 4):
            b.append(L(px(r), Y0, px(r), Y0 + 5, "#90a4ae")); b.append(T(px(r), Y0 + 18, str(r), 11, "#78909c", "middle"))
        b.append(T(px(0), Y0 + 18, "0", 11, "#78909c", "middle"))
        b.append(L(X0, Y0, X1 + 8, Y0, "#90a4ae", 1.6)); b.append(L(X0, Y1 - 14, X0, Y0, "#90a4ae", 1.6))
        b.append(T(X1 + 12, Y0 + 4, "r = Ω/ω", 12, GREY))
        b.append(T(X0 + 4, Y1 - 18, "DMF" if fn is dmf else "TR", 12.5, GREY, bold=True))
        if fn is tr:
            rs2 = math.sqrt(2)
            b.append(f'<rect x="{f(px(rs2))}" y="{f(py(1))}" width="{f(X1-px(rs2))}" height="{f(Y0-py(1))}" fill="#c8e6c9" opacity="0.7"/>')
            b.append(L(px(rs2), Y1 - 10, px(rs2), Y0, PURPLE, 2, "6 4"))
            b.append(T(px(rs2) + 6, Y1 + 2, "r = √2：三線交於 (√2, 1)", 12, PURPLE, bold=True))
            b.append(T(px(2.9), py(1) - 8, "↓ 隔震有效區 TR &lt; 1", 12, "#1b5e20", "middle", True))
        b.append(L(X0, py(1), X1, py(1), "#b0bec5", 1.2, "4 4"))
        for z, c in zs:
            pts = []
            n = 800
            for i in range(n + 1):
                r = 4*i/n
                pts.append((px(r), py(fn(r, z))))
            b.append(f'<polyline fill="none" stroke="{c}" stroke-width="2.6" points="{poly(pts)}"/>')
            rp, vp = peak(fn, z)
            res[(fn.__name__, z)] = (rp, vp)
        if fn is tr:
            b.append(f'<circle cx="{f(px(math.sqrt(2)))}" cy="{f(py(1))}" r="5" fill="{PURPLE}"/>')
        # legend with exact peaks
        lx, ly = X0 + 175, Y1 + 22 + (36 if fn is tr else 0)
        for i, (z, c) in enumerate(zs):
            rp, vp = res[(fn.__name__, z)]
            b.append(L(lx, ly + i*21 - 4, lx + 24, ly + i*21 - 4, c, 3))
            b.append(T(lx + 30, ly + i*21, f"ξ = {z:.2f}　峰 {vp:.2f}（r = {rp:.3f}）", 11.5, c))
        if fn is dmf:
            b.append(T(lx + 2, ly + 66, "峰值 = 1/(2ξ√(1−ξ²)) ≈ 1/(2ξ)", 11.5, GREY))
            b.append(T(px(0.06), py(1) - 26, "r≪1 → 1", 11.5, GREY))
            b.append(T(px(3.98), py(1) - 8, "r≫1：→ 1/r²（三線重合）", 11.5, GREY, "end"))
        else:
            b.append(T(lx + 2, ly + 66, "TR 峰略高於 1/(2ξ)（分子 &gt; 1）", 11.5, GREY))
        # bottom box
        bc = ("#e3f2fd", "#90caf9", "#0d47a1") if fn is dmf else ("#ffebee", "#ef9a9a", "#b71c1c")
        b.append(f'<rect x="{X0}" y="330" width="{X1-X0}" height="50" rx="9" fill="{bc[0]}" stroke="{bc[1]}"/>')
        if fn is dmf:
            b.append(T((X0 + X1)/2, 351, "消能減震＝沿「ξ 方向」把共振峰往下壓", 13.5, bc[2], "middle"))
            b.append(T((X0 + X1)/2, 371, "全頻段阻尼越大越好，r 越大三線越靠攏", 12.5, "#37474f", "middle"))
        else:
            b.append(T((X0 + X1)/2, 351, "基礎隔震＝沿「r 方向」把結構推到 r &gt; √2", 13.5, bc[2], "middle"))
            vals = " / ".join(f"{tr(4, z):.3f}" for z, _ in zs)
            b.append(T((X0 + X1)/2, 371, f"r = 4 時 TR = {vals}（阻尼越大反而越高）", 12.5, "#37474f", "middle"))
    return svg(900, 392, b, "動力放大因子 DMF 與傳遞率 TR 對頻率比的曲線"), res

# ------------------------------------------------------------------ E/F. mode shapes
def mode_panel(x0, width, title, color, phi, omega_txt, foot, story_h, base_y, scale_px, node_note=True):
    b = []
    n = len(phi)
    ax = x0 + width*0.64
    b.append(T(x0 + width/2, 26, title, 14, color, "middle", True))
    b.append(T(x0 + width/2, 45, omega_txt, 12.5, color, "middle"))
    b += ground(ax - 70, ax + 70, base_y)
    ys = [base_y - story_h*(i + 1) for i in range(n)]
    b.append(L(ax, base_y, ax, ys[-1] - 12, "#b0bec5", 1.6, "5 4"))
    mx = max(abs(v) for v in phi); s = scale_px/mx
    pts = [(ax, base_y)] + [(ax + s*v, y) for v, y in zip(phi, ys)]
    for y in ys:
        b.append(L(x0 + 8, y, x0 + width - 8, y, "#eceff1", 1))
    b.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{poly(pts)}"/>')
    nodes = []
    prev = (0.0, base_y)
    for v, y in zip(phi, ys):
        if prev[0]*v < 0:
            t = prev[0]/(prev[0] - v)
            yn = prev[1] + (y - prev[1])*t
            hz = (base_y - yn)/story_h
            nodes.append(hz)
            b.append(f'<circle cx="{f(ax)}" cy="{f(yn)}" r="5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
            if v < 0:
                b.append(T(ax + 9, yn - 5, f"節點 {hz:.2f}h", 11.5, PURPLE))
            else:
                b.append(T(ax - 9, yn - 5, f"節點 {hz:.2f}h", 11.5, PURPLE, "end"))
        prev = (v, y)
    for i, (v, y) in enumerate(zip(phi, ys)):
        X = ax + s*v
        b.append(f'<rect x="{f(X-9)}" y="{f(y-9)}" width="18" height="18" rx="3" fill="{color}"/>')
        b.append(L(ax, y, X, y, color, 1.2, "3 3"))
        b.append(T(x0 + 8, y + 4, f"{i+1}F", 12, "#455a64", bold=True))
        b.append(T(x0 + 32, y + 4, f"φ = {v:+.3f}".replace("-", "−"), 11.5, color, bold=(v < 0)))
    for j, line in enumerate(foot):
        b.append(T(x0 + width/2, base_y + 26 + j*18, line, 12, color, "middle", j == 0))
    return b, nodes

def fig_modes2():
    lam = [2 - math.sqrt(2), 2 + math.sqrt(2)]
    phis = [[1, 3 - l] for l in lam]
    b = [L(440, 20, 440, 300, "#cfd8dc", 2, "6 5")]
    allnodes = []
    meta = [("第一振態", GREEN, ["兩層同向、0 個節點 → 基底剪力最大", "有效質量 85.4%，主宰地震反應"]),
            ("第二振態", RED, ["兩層反向、1 個節點 → 層間變形大", "有效質量 14.6%，影響高樓層加速度"])]
    for i, (lab, c, foot) in enumerate(meta):
        part, nodes = mode_panel(i*440, 440, lab, c, phis[i], f"ω{'₁₂'[i]} = {math.sqrt(lam[i]):.4f} √(k/m)", foot, 85, 240, 120)
        b += part; allnodes.append(nodes)
    b.append(T(440, 322, "比例尺：每個振態以最大分量 = 120 px 繪製；折線＝剪力建築（質量集中在樓版，柱段內位移線性變化）", 11.5, GREY, "middle"))
    return svg(880, 332, b, "二自由度剪力建築振態"), allnodes

def fig_modes3():
    import numpy as np
    K = np.array([[2, -1, 0], [-1, 2, -1], [0, -1, 1]], float)
    lam, V = np.linalg.eigh(K)
    phis = [list(V[:, i]/V[0, i]) for i in range(3)]
    colors = [GREEN, ORANGE, RED]; names = ["第一振態", "第二振態", "第三振態"]
    meff = []
    for p in phis:
        p = np.array(p); M = p @ p; G = p.sum()/M; meff.append(G*G*M/3)
    b = [L(300, 20, 300, 330, "#cfd8dc", 1.6, "6 5"), L(600, 20, 600, 330, "#cfd8dc", 1.6, "6 5")]
    allnodes = []
    for i in range(3):
        part, nodes = mode_panel(i*300, 300, names[i], colors[i], phis[i], f"ω{'₁₂₃'[i]} = {math.sqrt(lam[i]):.4f} √(k/m)",
                                 [f"有效質量 {meff[i]*100:.1f}%　{i} 個節點"], 68, 290, 74)
        b += part; allnodes.append(nodes)
    b.append(f'<rect x="34" y="338" width="832" height="30" rx="7" fill="#ede7f6" stroke="#b39ddb"/>')
    b.append(T(450, 358, "同樣五個數字 0.445 / 0.802 / 1.247 / 1.802 / 2.247 在三個振態間輪替出現 —— 均勻剪力建築的特徵，可用來檢查有沒有算錯", 12, "#4527a0", "middle"))
    return svg(900, 374, b, "三自由度均勻剪力建築振態"), dict(lam=list(lam), phis=phis, meff=meff, nodes=allnodes)

# ------------------------------------------------------------------ N1. hysteresis W_D vs W_S
def fig_hyst():
    xi = 0.10
    X0, Y0, S = 250, 185, 130          # origin; u0 -> 130 px, k*u0 -> 130 px
    b = [f'<defs>{marker("mkN1", GREY)}</defs>']
    b.append(L(X0 - 175, Y0, X0 + 175, Y0, "#90a4ae", 1.6)); b.append(L(X0, Y0 + 165, X0, Y0 - 165, "#90a4ae", 1.6))
    b.append(T(X0 + 180, Y0 + 4, "u", 13, GREY)); b.append(T(X0 + 6, Y0 - 155, "F", 13, GREY))
    # W_S triangle
    b.append(f'<polygon points="{poly([(X0, Y0), (X0+S, Y0), (X0+S, Y0-S)])}" fill="#bbdefb" stroke="{BLUE}" stroke-width="1.2" opacity="0.9"/>')
    b.append(L(X0 - S - 15, Y0 + S + 15, X0 + S + 15, Y0 - S - 15, BLUE, 2, "6 4"))
    b.append(T(X0 + S + 18, Y0 - S - 14, "彈簧 F = k·u", 12.5, BLUE, bold=True))
    b.append(T(X0 + S*0.66, Y0 - 12, "W_S = ½ k u₀²", 12.5, "#0d47a1", "middle", True))
    # total force ellipse at resonance: F = k u + c u̇ ; u=u0 sinθ, c ω u0 = 2ξ k u0
    pts = []
    for i in range(241):
        th = 2*math.pi*i/240
        u = math.sin(th); F = u + 2*xi*math.cos(th)
        pts.append((X0 + S*u, Y0 - S*F))
    b.append(f'<polygon points="{poly(pts)}" fill="#ef9a9a" fill-opacity="0.45" stroke="{RED}" stroke-width="2.6"/>')
    b.append(T(X0 - S - 10, Y0 + S - 30, "W_D ＝ 迴圈面積", 12.5, RED, "end", True))
    b.append(T(X0 - S - 10, Y0 + S - 12, "＝ π c ω u₀²", 12.5, RED, "end"))
    hh = 2*xi*S
    b.append(L(X0 - 8, Y0 - hh, X0 + 8, Y0 - hh, RED, 1.4)); b.append(L(X0 - 8, Y0 + hh, X0 + 8, Y0 + hh, RED, 1.4))
    b.append(T(X0 - 12, Y0 - hh - 4, "c ω u₀", 11.5, RED, "end"))
    b.append(L(X0 + S, Y0 + 6, X0 + S, Y0 + 16, "#455a64", 1.2)); b.append(T(X0 + S, Y0 + 30, "u₀", 12, "#455a64", "middle"))
    # right-hand derivation
    x = 470
    rows = [("同一振幅 u₀、在共振 ω = ω₀ 時：", "#37474f", True),
            ("W_D = π c ω u₀² = π (2ξmω₀) ω₀ u₀² = 2π ξ k u₀²", "#b71c1c", False),
            ("W_S = ½ k u₀²", "#0d47a1", False),
            ("⇒ W_D / W_S = 4π ξ", "#4a148c", True),
            ("⇒ ξ_eq = W_D / (4π W_S)", "#4a148c", True),
            ("本圖依 ξ = 0.10 精確繪製：", "#37474f", True),
            ("紅色橢圓面積 / 藍色三角形 = 4π(0.10) = 1.257", "#37474f", False),
            ("（橢圓上下半寬 = c ω u₀ = 2ξ·k u₀ = 0.2 k u₀）", "#607d8b", False),
            ("換成摩擦、BRB、鉛心橡膠：迴圈形狀不同，", "#37474f", False),
            ("定義完全一樣 — 量面積、除以 4π W_S。", "#37474f", False)]
    y = 58
    for s, c, bold in rows:
        b.append(T(x, y, s, 13 if bold else 12.5, c, bold=bold)); y += 26 if s.startswith("⇒") or bold else 24
    return svg(900, 360, b, "黏滯阻尼遲滯迴圈與等效阻尼比定義")

# ------------------------------------------------------------------ N2. critical damping comparison
def fig_crit():
    w = 2*math.pi
    def u(t, z):
        if z < 1:
            wd = w*math.sqrt(1 - z*z)
            return math.exp(-z*w*t)*(math.cos(wd*t) + z*w/wd*math.sin(wd*t))
        if z == 1:
            return (1 + w*t)*math.exp(-w*t)
        s1 = -w*(z - math.sqrt(z*z - 1)); s2 = -w*(z + math.sqrt(z*z - 1))
        return (s2*math.exp(s1*t) - s1*math.exp(s2*t))/(s2 - s1)
    TM = 2.5
    X0, X1, Y0 = 70, 800, 175; SY = 120
    px = lambda t: X0 + (X1 - X0)*t/TM; py = lambda v: Y0 - SY*v
    b = []
    b.append(f'<rect x="{X0}" y="{f(py(0.05))}" width="{X1-X0}" height="{f(2*SY*0.05)}" fill="#e8f5e9"/>')
    b.append(T(X1 - 4, py(0.05) - 4, "±5% 帶", 11, "#2e7d32", "end"))
    for v in (-1, -0.5, 0.5, 1):
        b.append(L(X0, py(v), X1, py(v), "#eceff1", 1)); b.append(T(X0 - 8, py(v) + 4, f"{v:g}", 11, "#78909c", "end"))
    for t in (0.5, 1, 1.5, 2, 2.5):
        b.append(L(px(t), py(-1.12), px(t), py(-1.12) + 5, "#90a4ae")); b.append(T(px(t), py(-1.12) + 18, f"{t:g}T", 11, "#78909c", "middle"))
    b.append(L(X0, Y0, X1 + 10, Y0, "#90a4ae", 1.6)); b.append(L(X0, py(1.15), X0, py(-1.12), "#90a4ae", 1.6)); b.append(L(X0, py(-1.12), X1, py(-1.12), "#cfd8dc", 1))
    b.append(T(X0 - 8, py(1.18), "u/u₀", 12, GREY, "end"))
    cases = [(0.0, "#90a4ae", "ξ = 0：永遠等幅"), (0.1, BLUE, "ξ = 0.1 欠阻尼：越過零點來回"),
             (1.0, GREEN, "ξ = 1 臨界：最快回到平衡、不越過"), (2.0, ORANGE, "ξ = 2 過阻尼：不越過，但更慢")]
    settle = {}
    for z, c, lab in cases:
        pts = [(px(TM*i/500), py(u(TM*i/500, z))) for i in range(501)]
        dash = ' stroke-dasharray="5 4"' if z == 0 else ""
        b.append(f'<polyline fill="none" stroke="{c}" stroke-width="{3.2 if z == 1 else 2.2}"{dash} points="{poly(pts)}"/>')
        # settling time to stay within 5%
        ts = None
        last_out = 0
        for i in range(1, 20001):
            t = 8*i/20000
            if abs(u(t, z)) > 0.05: last_out = t
        settle[z] = last_out
    for z, c in ((1.0, GREEN), (2.0, ORANGE)):
        t = settle[z]
        b.append(f'<circle cx="{f(px(t))}" cy="{f(py(0.05))}" r="5" fill="{c}"/>')
        b.append(L(px(t), py(0.05), px(t), Y0 + 22, c, 1.2, "3 3"))
        b.append(T(px(t), Y0 + 36, f"{t:.2f}T", 12, c, "middle", True))
    ly = 356
    for i, (z, c, lab) in enumerate(cases):
        xx = X0 + 30 + (i % 2)*370; yy = ly + (i//2)*22
        b.append(L(xx, yy - 4, xx + 26, yy - 4, c, 3)); b.append(T(xx + 32, yy, lab, 12.5, c, bold=(z == 1)))
    b.append(T(440, 410, f"進入 ±5% 帶後不再離開的時間：ξ = 1 只要 {settle[1.0]:.2f}T；ξ = 2 要 {settle[2.0]:.2f}T；ξ = 0.1 要 {settle[0.1]:.2f}T", 12.5, "#37474f", "middle", True))
    return svg(880, 420, b, "不同阻尼比的自由振動比較"), settle

# ------------------------------------------------------------------ N3. code formula shape vs sine
def fig_beam():
    X0, X1, Y0, A = 90, 790, 70, 150
    fs = lambda s: 16/5*(s**4 - 2*s**3 + s)
    gs = lambda s: math.sin(math.pi*s)
    b = []
    b.append(L(X0, Y0, X1, Y0, "#455a64", 4))
    b.append(f'<polygon points="{poly([(X0,Y0+2),(X0-12,Y0+20),(X0+12,Y0+20)])}" fill="#fff" stroke="#455a64" stroke-width="2"/>')
    b.append(f'<polygon points="{poly([(X1,Y0+2),(X1-12,Y0+20),(X1+12,Y0+20)])}" fill="#fff" stroke="#455a64" stroke-width="2"/>')
    b.append(f'<circle cx="{X1}" cy="{Y0+26}" r="4" fill="#fff" stroke="#455a64" stroke-width="1.5"/>')
    for i in range(11):
        x = X0 + (X1 - X0)*i/10
        b.append(f'<path d="M{f(x)} {Y0-34} v26" stroke="#78909c" stroke-width="1.4"/>')
        b.append(f'<path d="M{f(x-4)} {Y0-14} l4 7 l4 -7" fill="none" stroke="#78909c" stroke-width="1.4"/>')
    b.append(L(X0, Y0 - 34, X1, Y0 - 34, "#78909c", 1.4))
    b.append(T((X0 + X1)/2, Y0 - 40, "單位靜載重 w 當側力施加", 12.5, GREY, "middle"))
    ss = [i/200 for i in range(201)]
    P1 = [(X0 + (X1 - X0)*s, Y0 + A*fs(s)) for s in ss]
    P2 = [(X0 + (X1 - X0)*s, Y0 + A*gs(s)) for s in ss]
    b.append(f'<polyline fill="none" stroke="{BLUE}" stroke-width="5" opacity="0.55" points="{poly(P1)}"/>')
    b.append(f'<polyline fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="7 4" points="{poly(P2)}"/>')
    b.append(L(X0 + 250, Y0 + 186, X0 + 280, Y0 + 186, BLUE, 5, extra=' opacity="0.55"'))
    b.append(T(X0 + 288, Y0 + 190, "規範 u(x)：靜載重撓度（正規化）", 12.5, BLUE, bold=True))
    b.append(L(X0 + 250, Y0 + 208, X0 + 280, Y0 + 208, RED, 2, "7 4"))
    b.append(T(X0 + 288, Y0 + 212, "精確第一振態 sin(πx/L)", 12.5, RED, bold=True))
    # difference x50
    Yd = 330; G = 200
    diffs = [fs(s) - gs(s) for s in ss]
    dmax = max(diffs, key=abs); smax = ss[diffs.index(dmax)]
    b.append(L(X0, Yd, X1, Yd, "#90a4ae", 1.2))
    D = [(X0 + (X1 - X0)*s, Yd - A*G*d/10) for s, d in zip(ss, diffs)]
    b.append(f'<polyline fill="none" stroke="{PURPLE}" stroke-width="2.2" points="{poly(D)}"/>')
    b.append(T(X0 - 8, Yd + 4, "差值", 11.5, PURPLE, "end", True))
    b.append(T(X0 - 8, Yd + 18, "×20", 11.5, PURPLE, "end"))
    xm = X0 + (X1 - X0)*smax
    b.append(f'<circle cx="{f(xm)}" cy="{f(Yd - A*G*dmax/10)}" r="4" fill="{PURPLE}"/>')
    b.append(T(xm + 8, Yd - A*G*dmax/10 - 6, f"最大差 {abs(dmax)*100:.2f}%（x = {smax:.2f}L）", 12, PURPLE, bold=True))
    b.append(T((X0 + X1)/2, 372, "兩條曲線肉眼無法分辨 → Rayleigh 商只高估 ω 0.07%（T 低估 0.07%）", 13, "#37474f", "middle", True))
    return svg(880, 384, b, "簡支梁靜載重撓度與正弦振態比較"), dict(dmax=dmax, smax=smax)

if __name__ == "__main__":
    out = {}
    out["column"] = fig_column()
    out["logdec"] = fig_logdec()
    out["rayleigh"], r1 = fig_rayleigh()
    out["dmftr"], r2 = fig_dmf_tr()
    out["modes2"], r3 = fig_modes2()
    out["modes3"], r4 = fig_modes3()
    out["hyst"] = fig_hyst()
    out["crit"], r5 = fig_crit()
    out["beam"], r6 = fig_beam()
    import sys; json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "figs.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(r1); print({str(k): (round(v[0], 3), round(v[1], 3)) for k, v in r2.items()}); print(r3); print(r4); print(r5); print(r6)
