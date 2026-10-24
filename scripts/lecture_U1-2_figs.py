"""
gen_lecture_SD-U1-2.py — lecture-SD-U1-2.html 的向量圖解產生器
================================================================
所有幾何由公式算出（struct-diagram 鐵則）：改參數重跑，圖跟著變。
輸出：figs/U1-2-fig-*.svg（直接內嵌進 lecture-SD-U1-2.html）

用法：python scripts/lecture_U1-2_figs.py [structdraw 所在目錄] [輸出目錄]
      預設：structdraw 取同目錄的 structdraw.py（struct-diagram skill 的 primitives），輸出到 figs_U1-2/
需求：numpy、scipy
"""
import sys, os, math
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else HERE)
from structdraw import Canvas, C, FONT, FONT_M, esc  # noqa: E402

OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "figs_U1-2")
os.makedirs(OUT, exist_ok=True)

DOT1 = "̇"   # 上一點（速度）
DOT2 = "̈"   # 上兩點（加速度）
UD, UDD = "u" + DOT1, "u" + DOT2
THD, THDD = "θ" + DOT1, "θ" + DOT2


# ───────────────────────────── 共用小工具 ─────────────────────────────
def hcompose(panels, fid, gap=0):
    """寬度可不同的橫向拼接；每格 clipPath（id 帶圖號前綴，避免同頁衝突）"""
    H = max(p.h for p in panels)
    W = sum(p.w for p in panels) + gap * (len(panels) - 1)
    parts, clips, x = [], [], 0
    for i, p in enumerate(panels):
        cid = f"{fid}-clip{i}"
        clips.append(f'<clipPath id="{cid}"><rect width="{p.w}" height="{p.h}"/></clipPath>')
        parts.append(f'<g transform="translate({x},0)" clip-path="url(#{cid})">{"".join(p.parts)}</g>')
        x += p.w + gap
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'role="img"><defs>{"".join(clips)}</defs>{"".join(parts)}</svg>')


# 數學字型：Windows 用 Cambria Math；其他環境退到頁面已載入的 KaTeX_Math（與內文公式同一字型）
FONT_M_PAGE = "'Latin Modern Math','Cambria Math','Times New Roman','KaTeX_Math',serif"


def save(name, svg):
    svg = svg.replace(FONT_M, FONT_M_PAGE)
    # θ 上加點：組合字元在部分襯線字型會失敗，改用「間距型」點號 + dx/dy 疊上去（淨位移為 0）
    svg = svg.replace("θ" + DOT2, 'θ<tspan dx="-0.46em" dy="-0.42em">¨</tspan><tspan dx="0.06em" dy="0.42em">​</tspan>')
    svg = svg.replace("θ" + DOT1, 'θ<tspan dx="-0.40em" dy="-0.42em">˙</tspan><tspan dx="0.10em" dy="0.42em">​</tspan>')
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name)


def spring(cv, p0, p1, n=6, amp=0.13, color=C["bmd"], w=2.2, lead=0.18):
    """彈簧：p0→p1，兩端各留 lead 比例的直線段；鋸齒數 n 固定，拉伸時齒距跟著變"""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    a = lead * L
    pts = [(x0, y0), (x0 + ux * a, y0 + uy * a)]
    seg = (L - 2 * a) / (2 * n)
    for i in range(1, 2 * n):
        s = a + i * seg
        sgn = 1 if i % 2 else -1
        pts.append((x0 + ux * s + nx * amp * sgn, y0 + uy * s + ny * amp * sgn))
    pts += [(x1 - ux * a, y1 - uy * a), (x1, y1)]
    cv.poly(pts, color, w)


def dashpot(cv, p0, p1, color=C["sfd"], w=2.2, hw=0.16):
    """水平阻尼器：p0 端為缸、p1 端為活塞"""
    (x0, y), (x1, _) = p0, p1
    L = x1 - x0
    c0, c1 = x0 + 0.25 * L, x0 + 0.62 * L
    cv.line((x0, y), (c0, y), color, w)
    cv.line((c0, y - hw), (c0, y + hw), color, w)
    cv.line((c0, y - hw), (c1, y - hw), color, w)
    cv.line((c0, y + hw), (c1, y + hw), color, w)
    pis = x0 + 0.48 * L
    cv.line((pis, y - hw * 0.75), (pis, y + hw * 0.75), color, w + 0.6)
    cv.line((pis, y), (x1, y), color, w)


def ground(cv, x0, x1, y, color=C["member2"], n=None, w=2.2):
    cv.line((x0, y), (x1, y), color, w, cap="butt")
    n = n or int((x1 - x0) / 0.25)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        cv.line((x, y), (x - 0.14, y - 0.14), color, 1.3)


def wall_v(cv, x, y0, y1, side=-1, color=C["member2"]):
    """垂直牆；side=-1 斜線在左"""
    cv.line((x, y0), (x, y1), color, 2.4, cap="butt")
    n = int((y1 - y0) / 0.22)
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        cv.line((x, y), (x + side * 0.15, y - 0.15), color, 1.3)


def arc(cv, c, r, a0, a1, color, w=2.0, head=True):
    """圓弧箭頭（數學角，弧度，a0→a1）"""
    n = 30
    pts = [(c[0] + r * math.cos(a0 + (a1 - a0) * i / n), c[1] + r * math.sin(a0 + (a1 - a0) * i / n))
           for i in range(n + 1)]
    cv.poly(pts[:-3] if head else pts, color, w)
    if head:
        cv.arrow(pts[-4], pts[-1], color, w, 8)


def vdim(cv, x, y0, y1, label, color=C["dim"], side=1, size=13.5, math_label=True, tick=0.08):
    """垂直尺寸線（雙箭頭），label 放在 side 側"""
    cv.line((x, y0), (x, y1), color, 1.4)
    for y, s in ((y0, 1), (y1, -1)):
        cv.line((x - tick, y), (x + tick, y), color, 1.4)
    if abs(y1 - y0) * cv.sx > 22:
        cv.arrow((x, (y0 + y1) / 2), (x, y1), color, 1.4, 7)
        cv.arrow((x, (y0 + y1) / 2), (x, y0), color, 1.4, 7)
    f = cv.math if math_label else cv.text
    f((x, (y0 + y1) / 2), label, size, color, "start" if side > 0 else "end", dx=8 * side)


def hdim(cv, y, x0, x1, label, color=C["dim"], above=True, size=13.5, math_label=True, tick=0.08):
    cv.line((x0, y), (x1, y), color, 1.4)
    for x in (x0, x1):
        cv.line((x, y - tick), (x, y + tick), color, 1.4)
    if abs(x1 - x0) * cv.sx > 22:
        cv.arrow(((x0 + x1) / 2, y), (x1, y), color, 1.4, 7)
        cv.arrow(((x0 + x1) / 2, y), (x0, y), color, 1.4, 7)
    f = cv.math if math_label else cv.text
    f(((x0 + x1) / 2, y), label, size, color, dy=-11 if above else 13)


def mass_box(cv, x0, y0, w, h, label="m", fill="#E8EDF4", stroke=C["member"], dash=None, sw=2.2):
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    s = " ".join(f"{cv.X(x):.2f},{cv.Y(y):.2f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    cv.parts.append(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} '
                    f'stroke-linejoin="round"/>')
    if label:
        cv.math((x0 + w / 2, y0 + h / 2), label, 17, C["text"])


def title(cv, s, sub=None):
    cv.text_px(cv.w / 2, 26, s, 15, C["text"], weight="700")
    if sub:
        cv.text_px(cv.w / 2, 47, sub, 12, C["muted"])


def frame_bg(cv):
    cv.rect_px(4, 4, cv.w - 8, cv.h - 8, C["panel"], 12, C["border"], 1.1)


# ═══════════════════ 圖 A　§1 牛頓 vs D'Alembert ═══════════════════
def fig_dalembert():
    W, H = 460, 330
    # 左：真實系統
    a = Canvas(W, H, sx=78, ox=40, oy=110)
    frame_bg(a); title(a, "真實系統：合力造成加速度", "位移、速度、加速度皆以向右為正")
    U_DRAW = 0.42                       # 繪圖用位移（示意放大）
    xm0, mw, mh = 2.25, 1.15, 1.05      # 靜平衡時質量左緣、寬、高
    wall_v(a, 0, -0.05, 1.45)
    ground(a, 0, 5.0, -0.05)
    for cx in (xm0 + U_DRAW + 0.25, xm0 + U_DRAW + mw - 0.25):   # 滾輪
        a.circle((cx, 0.045), 0.09, "#FFFFFF", C["member"], 1.8)
    xm = xm0 + U_DRAW
    mass_box(a, xm0, 0.14, mw, mh, None, "none", C["ghost"], "6,4", 1.6)
    mass_box(a, xm, 0.14, mw, mh)
    spring(a, (0, 0.95), (xm, 0.95), n=7, amp=0.11)
    dashpot(a, (0, 0.40), (xm, 0.40))
    a.math((xm / 2, 1.20), "k", 15, C["bmd"])
    a.math((xm / 2, 0.08), "c", 15, C["sfd"])
    a.arrow((xm + mw, 0.67), (xm + mw + 0.85, 0.67), C["load"], 3.0)
    a.math((xm + mw + 0.95, 0.67), "p(t)", 15, C["load"], "start")
    # 位移基準線與 u
    a.line((xm0, 1.30), (xm0, 1.75), C["ghost"], 1.6, "5,4")
    a.line((xm, 1.22), (xm, 1.75), C["deform"], 1.4)
    a.arrow((xm0, 1.62), (xm, 1.62), C["deform"], 2.2, 8)
    a.math((xm0 - 0.06, 1.62), "u(t)", 14, C["deform"], "end")
    a.text_px(W / 2, H - 52, "m" + UDD + " = p(t) − c" + UD + " − ku", 15.5, C["text"], font=FONT_M, italic=True)
    a.text_px(W / 2, H - 28, "彈簧拉、阻尼拖、外力推 → 淨力 = 質量 × 加速度", 12, C["muted"])

    # 右：D'Alembert 自由體
    b = Canvas(W, H, sx=78, ox=40, oy=110)
    frame_bg(b); title(b, "D'Alembert：把 m" + UDD + " 畫成一個力", "四個力在任一瞬間平衡（∑F = 0）")
    bx0 = 2.05
    mass_box(b, bx0, 0.14, mw, mh, None, "#FFFFFF", C["member"], "6,4", 2.0)
    b.math((bx0 + mw / 2, 0.66), "m", 17, C["muted"])
    L0 = bx0
    # 三個阻抗力向左（長度僅示意，同一方向是重點）
    rows = [(1.02, 1.05, C["bmd"], "f_S = ku", "彈簧力"),
            (0.66, 0.80, C["sfd"], "f_D = c" + UD, "阻尼力"),
            (0.30, 1.30, C["accent"], "f_I = m" + UDD, "慣性力（虛構）")]
    for y, ln, col, lab, zh in rows:
        b.arrow((L0, y), (L0 - ln, y), col, 3.0, 10, "7,4" if "I" in lab else None)
        b.math((L0 - ln - 0.08, y + 0.02), lab, 14, col, "end")
    b.arrow((bx0 + mw, 0.66), (bx0 + mw + 0.85, 0.66), C["load"], 3.0)
    b.math((bx0 + mw + 0.95, 0.66), "p(t)", 15, C["load"], "start")
    # 垂直方向（重力與正向力自行抵銷，灰色）
    b.arrow((bx0 + mw / 2, 0.14), (bx0 + mw / 2, -0.38), C["member2"], 1.8, 7)
    b.arrow((bx0 + mw / 2, 1.19), (bx0 + mw / 2, 1.60), C["member2"], 1.8, 7)
    b.math((bx0 + mw / 2 + 0.08, -0.30), "mg", 12.5, C["member2"], "start")
    b.math((bx0 + mw / 2 + 0.08, 1.52), "N", 12.5, C["member2"], "start")
    b.text_px(W / 2, H - 52, "m" + UDD + " + c" + UD + " + ku = p(t)", 15.5, C["text"], font=FONT_M, italic=True)
    b.text_px(W / 2, H - 28, "三個阻抗力同向（都與正方向相反）→ 方程式左邊三項同號", 12, C["accent"])
    save("U1-2-fig-A-dalembert.svg", hcompose([a, b], "fA"))


# ═══════════════════ 圖 B　§2 虛功：剛性桿 ＋ 彈簧 ＋ 質量 ═══════════════════
def fig_virtual_work():
    W, H = 920, 330
    L, A_ = 6.0, 2.4                     # 繪圖用：L、a（比例 a/L = 0.4）
    TH = 0.13                            # 繪圖用 δθ（放大示意；位移採小角度線性化）
    cv = Canvas(W, H, sx=78, ox=50, oy=150)
    frame_bg(cv)
    title(cv, "虛功：只給一個 δθ，所有點的虛位移都由幾何決定", "鉸 A 的反力作用點不動 → 反力不做虛功，自動消失")
    # 地面與鉸
    cv.pin_support((0, 0), 0, 16, C["member"])
    # 彈簧（下端接地）
    yb = -1.25
    ground(cv, A_ - 0.4, A_ + 0.4, yb)
    spring(cv, (A_, yb), (A_, 0), n=5, amp=0.12, lead=0.15)
    cv.math((A_ - 0.24, yb / 2), "k", 15, C["bmd"], "end")
    # 原桿（灰虛線）與虛位移後（藍）
    cv.line((0, 0), (L, 0), C["member"], 6, cap="butt")
    cv.line((0, 0), (L, L * TH), C["deform"], 3, "8,5")
    cv.dot((L, 0), 9, C["member"], "#FFFFFF", 2)
    cv.math((L + 0.05, -0.38), "m", 16, C["text"])
    cv.dot((L, L * TH), 7, "#FFFFFF", C["deform"], 2.2)
    # 虛位移箭頭（長度 = 距離 × δθ，比例為真）
    cv.arrow((A_, 0), (A_, A_ * TH), C["deform"], 2.4, 7)
    cv.math((A_ - 0.1, A_ * TH + 0.32), "δu_{k} = a δθ", 14, C["deform"], "end")
    cv.arrow((L, 0.02), (L, L * TH), C["deform"], 2.4, 8)
    cv.math((L - 0.14, L * TH * 0.5), "δu_{m} = L δθ", 14, C["deform"], "end")
    arc(cv, (0, 0), 1.25, 0.0, TH, C["deform"], 1.8)
    cv.math((1.32, 0.03), "δθ", 14, C["deform"], "start")
    # 作用在桿上的力（在原位置畫）
    cv.arrow((L + 0.85, 0.0), (L + 0.85, 1.2), C["load"], 3, 10)
    cv.math((L + 0.96, 1.05), "p(t)", 15, C["load"], "start")
    cv.arrow((L + 0.85, 0.0), (L + 0.85, -1.0), C["accent"], 2.6, 9, "7,4")
    cv.math((L + 0.96, -0.85), "mL" + THDD, 14, C["accent"], "start")
    cv.text((L + 0.96, -1.17), "慣性力", 11.5, C["accent"], "start")
    cv.line((L, 0), (L + 0.85, 0), C["dim"], 1, "3,3")
    cv.arrow((A_ + 0.35, 0.0), (A_ + 0.35, -0.85), C["bmd"], 2.6, 9)
    cv.math((A_ + 0.48, -0.55), "k aθ", 14, C["bmd"], "start")
    # 尺寸線
    hdim(cv, -1.65, 0, A_, "a", above=False)
    hdim(cv, -1.65, A_, L, "L − a", above=False)
    cv.text((0, 0.45), "A（鉸）", 12.5, C["muted"])
    cv.text((L, 1.25), "B", 12.5, C["muted"])
    # 右側：虛功三項
    x = 710
    cv.rect_px(x - 14, 78, 210, 200, "#FFFFFF", 10, C["border"], 1)
    cv.text_px(x, 100, "力 × 同方向虛位移", 13, C["text"], "start", "700")
    cv.math_px(x, 128, "+p(t) · L δθ", 14.5, C["load"], "start")
    cv.math_px(x, 156, "− kaθ · a δθ", 14.5, C["bmd"], "start")
    cv.math_px(x, 184, "− mL" + THDD + " · L δθ", 14.5, C["accent"], "start")
    cv.line((x, 203), (x + 180, 203), C["border"], 1.2)
    cv.text_px(x, 224, "總和 = 0、消去 δθ：", 12.5, C["muted"], "start")
    cv.math_px(x, 252, "mL^{2}" + THDD + " + ka^{2}θ = p(t)L", 14.5, C["text"], "start", "700")
    save("U1-2-fig-B-virtual-work.svg", cv.svg().replace("<svg ", '<svg role="img" ', 1))


# ═══════════════════ 圖 C　§3.1 倒擺：幾何 ＋ 位能曲線 ═══════════════════
def fig_inverted_pendulum():
    # 左：幾何
    TH = math.radians(24)                # 繪圖用傾角
    L = 3.0
    a = Canvas(400, 380, sx=62, ox=120, oy=100)
    frame_bg(a); title(a, "倒擺：傾斜 θ 時誰在推、誰在拉", "θ 向右為正；彈簧在 θ = 0 時無伸縮")
    a.pin_support((0, 0), 0, 15, C["member"])
    Ax, Ay = L * math.sin(TH), L * math.cos(TH)
    a.line((0, 0), (0, L), C["ghost"], 3, "7,5")
    a.line((0, 0), (Ax, Ay), C["member"], 5, cap="butt")
    a.dot((Ax, Ay), 10, C["member"], "#FFFFFF", 2)
    a.math((Ax + 0.32, Ay - 0.32), "m", 16, C["text"])
    # 彈簧：右牆，自然長 S0
    S0 = 2.6
    wall_v(a, S0, L - 0.45, L + 0.45, side=1)
    spring(a, (Ax, Ay), (S0, Ay), n=6, amp=0.11, lead=0.12)
    a.math(((Ax + S0) / 2, Ay + 0.32), "k", 14, C["bmd"])
    # 力
    a.arrow((Ax, Ay), (Ax, Ay - 0.95), C["load"], 2.8, 9)
    a.math((Ax + 0.12, Ay - 0.78), "mg", 14, C["load"], "start")
    a.arrow((Ax, Ay - 0.02), (Ax - 0.9, Ay - 0.02), C["bmd"], 2.8, 9)
    a.math((Ax - 0.48, Ay + 0.24), "kL sinθ", 13.5, C["bmd"])
    # 尺寸
    hdim(a, L + 0.30, 0, Ax, "L sinθ", above=True, size=13)
    a.line((0, L), (0, L + 0.38), C["dim"], 1, "3,3")
    vdim(a, -0.38, Ay, L, "", side=-1)
    a.math((-0.48, L + 0.18), "L(1−cosθ)", 12.5, C["dim"], "end")
    a.line((-0.5, Ay), (Ax - 0.15, Ay), C["dim"], 1, "3,3")
    arc(a, (0, 0), 0.9, math.pi / 2, math.pi / 2 - TH, C["deform"], 1.8)
    a.math((0.18, 1.05), "θ", 14, C["deform"], "start")
    a.math((Ax / 2 + 0.2, Ay / 2), "L", 14, C["muted"], "start")
    a.text((-0.35, 0.05), "B（鉸）", 12, C["muted"], "end")
    a.text_px(200, 314, "傾倒力矩 mg · L sinθ ≈ mgL · θ", 12.5, C["load"])
    a.text_px(200, 336, "回復力矩 kL sinθ · L cosθ ≈ kL^{2} · θ", 12.5, C["bmd"])
    a.text_px(200, 362, "兩者都 ∝ θ → 重力是一根「負彈簧」", 13, C["text"], weight="700")

    # 右：位能曲線（精確式），ν = V/(mgL)，κ = kL/(mg)
    b = Canvas(520, 380, sx=1, ox=0, oy=0)
    frame_bg(b); title(b, "位能曲線：勁度 = 平衡點的曲率", "實線：精確 V(θ)；虛線：小角度二次近似")
    X0, X1, Y0, Y1 = 62, 500, 66, 290            # 繪圖區（像素）
    TMAX, VMIN, VMAX = 0.9, -0.45, 0.45
    px = lambda t: X0 + (t + TMAX) / (2 * TMAX) * (X1 - X0)
    py = lambda v: Y1 - (v - VMIN) / (VMAX - VMIN) * (Y1 - Y0)
    b.parts.append(f'<rect x="{X0}" y="{Y0}" width="{X1-X0}" height="{Y1-Y0}" fill="#FFFFFF" stroke="{C["border"]}"/>')
    for t in (-0.8, -0.4, 0, 0.4, 0.8):
        b.parts.append(f'<line x1="{px(t):.1f}" y1="{Y0}" x2="{px(t):.1f}" y2="{Y1}" stroke="#EEF1F5"/>')
        b.text_px(px(t), Y1 + 14, f"{t:+.1f}".replace("+0.0", "0"), 11, C["muted"])
    for v in (-0.4, -0.2, 0, 0.2, 0.4):
        b.parts.append(f'<line x1="{X0}" y1="{py(v):.1f}" x2="{X1}" y2="{py(v):.1f}" stroke="#EEF1F5"/>')
        b.text_px(X0 - 6, py(v), f"{v:+.1f}".replace("+0.0", "0"), 11, C["muted"], "end")
    b.parts.append(f'<clipPath id="fC-plot"><rect x="{X0}" y="{Y0}" width="{X1-X0}" height="{Y1-Y0}"/></clipPath><g clip-path="url(#fC-plot)">')
    b.parts.append(f'<line x1="{X0}" y1="{py(0):.1f}" x2="{X1}" y2="{py(0):.1f}" stroke="{C["member2"]}" stroke-width="1.2"/>')
    b.parts.append(f'<line x1="{px(0):.1f}" y1="{Y0}" x2="{px(0):.1f}" y2="{Y1}" stroke="{C["member2"]}" stroke-width="1.2"/>')
    b.text_px(X1 - 6, Y1 - 10, "θ（rad）", 12, C["muted"], "end")
    b.text_px(X0 + 8, Y0 + 12, "縱軸：[V(θ) − V(0)] / mgL", 11, C["muted"], "start")
    cases = [(2.0, C["bmd"], "kL/mg = 2：谷底 → 穩定"),
             (1.0, C["accent"], "kL/mg = 1：臨界（實為 −θ^{4}/8）"),
             (0.5, C["load"], "kL/mg = 0.5：山頂 → 不穩定")]
    ts = np.linspace(-TMAX, TMAX, 181)
    clip = lambda v: max(VMIN, min(VMAX, v))
    for kap, col, lab in cases:
        ex = [(px(t), py(math.cos(t) - 1 + 0.5 * kap * math.sin(t) ** 2)) for t in ts]
        ap = [(px(t), py(0.5 * (kap - 1) * t * t)) for t in ts]
        b.parts.append('<polyline fill="none" stroke="%s" stroke-width="2.6" points="%s"/>' %
                       (col, " ".join(f"{x:.1f},{y:.1f}" for x, y in ex)))
        b.parts.append('<polyline fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="6,4" opacity="0.8" points="%s"/>' %
                       (col, " ".join(f"{x:.1f},{y:.1f}" for x, y in ap)))
    b.parts.append("</g>")
    b.parts.append(f'<circle cx="{px(0):.1f}" cy="{py(0):.1f}" r="4.5" fill="{C["member"]}"/>')
    lx, ly = px(0) - 128, py(-0.215)
    b.rect_px(lx - 8, ly - 13, 268, 70, "#FFFFFF", 6, C["border"], 1)
    for i, (kap, col, lab) in enumerate(cases):
        b.parts.append(f'<line x1="{lx}" y1="{ly+i*22}" x2="{lx+22}" y2="{ly+i*22}" stroke="{col}" stroke-width="3"/>')
        b.text_px(lx + 28, ly + i * 22, lab, 11.5, col, "start", "700")
    b.text_px(260, 324, "k_{eff} = ∂^{2}V/∂θ^{2}|_{0} = kL^{2} − mgL", 13, C["text"], weight="700", font=FONT_M, italic=True)
    b.text_px(260, 352, "彈簧給正曲率、重力給負曲率；兩者相等時二次項消失", 12, C["muted"])
    save("U1-2-fig-C-inverted-pendulum.svg", hcompose([a, b], "fC"))


# ═══════════════════ 圖 D　§4.1 從靜平衡位置量 ═══════════════════
def fig_static_eq():
    W, H = 920, 420
    cv = Canvas(W, H, sx=70, ox=80, oy=40)
    frame_bg(cv)
    title(cv, "三個狀態、兩條基準線：重力被吸收進 δ_{st}", "y 從彈簧自然長度量；u 從靜平衡位置量（皆向下為正）")
    TOP, L0, MH, MW = 4.5, 1.6, 0.6, 0.95
    DST, U = 0.65, 0.48                  # 繪圖用 δst、u（示意比例）
    F0 = 0.55                            # 繪圖用：mg 的箭頭長；彈簧力箭頭長 = F0 × 伸長量/δst（比例為真）
    cols = [(0.7, 0.0, "① 自然長度", None),
            (4.5, DST, "② 靜平衡", "kδ_{st} = mg"),
            (8.3, DST + U, "③ 運動中某瞬間", "k(δ_{st}+u) − mg = ku")]
    for x, ext, lab, eq in cols:
        cv.line((x - 0.8, TOP), (x + 0.8, TOP), C["member2"], 2.4, cap="butt")
        for i in range(8):
            xx = x - 0.8 + i * 0.22
            cv.line((xx, TOP), (xx + 0.15, TOP + 0.15), C["member2"], 1.3)
        yb = TOP - L0 - ext
        spring(cv, (x, TOP), (x, yb), n=6, amp=0.14, lead=0.12)
        mass_box(cv, x - MW / 2, yb - MH, MW, MH, dash="6,4" if ext == 0 else None)
        cv.text((x, 0.18), lab, 13.5, C["text"], weight="700")
    # 兩條基準線
    y_nat, y_eq = TOP - L0, TOP - L0 - DST
    cv.line((-0.4, y_nat), (9.9, y_nat), C["ghost"], 1.4, "6,4")
    cv.line((3.2, y_eq), (9.9, y_eq), C["deform"], 1.4, "6,4")
    cv.text((1.6, y_nat + 0.2), "自然長度端點（y = 0）", 11.5, C["muted"], "start")
    cv.text((3.2, y_eq + 0.2), "靜平衡位置（u = 0）", 11.5, C["deform"], "start")
    vdim(cv, 5.75, y_eq, y_nat, "δ_{st} = mg/k", C["accent"], side=1, size=13)
    vdim(cv, 9.8, y_eq - U, y_eq, "u(t)", C["deform"], side=1, size=14)
    vdim(cv, 7.45, y_eq - U, y_nat, "", C["muted"])
    cv.math((7.35, y_eq - U - 0.18), "y = δ_{st} + u", 12.5, C["muted"], "end")
    # 力（作用在質量上，箭頭長度與力成正比）
    for x, ext, lab, eq in cols[1:]:
        yb = TOP - L0 - ext
        cx, cy = x + 0.72, yb - MH / 2
        cv.arrow((cx, cy), (cx, cy + F0 * ext / DST), C["bmd"], 2.4, 8)
        cv.arrow((cx + 0.3, cy), (cx + 0.3, cy - F0), C["load"], 2.4, 8)
        cv.math((cx + 0.42, cy - F0 + 0.1), "mg", 12.5, C["load"], "start")
        cv.math((cx + 0.12, cy + F0 * ext / DST - 0.02), "kδ_{st}" if ext == DST else "k(δ_{st}+u)", 12, C["bmd"], "start")
        cv.math((x, 0.58), eq, 13.5, C["text"])
    cv.text((0.7, 0.58), "（虛線質量：托住不放，彈簧未受力）", 11.5, C["muted"])
    save("U1-2-fig-D-static-eq.svg", cv.svg().replace("<svg ", '<svg role="img" ', 1))


# ═══════════════════ 圖 E　§4.2 絕對 vs 相對座標 ═══════════════════
def fig_base_excitation():
    W, H = 460, 390
    HH, B, UG, U = 2.3, 2.3, 0.95, 0.55          # 繪圖用：柱高、跨度、u_g、u
    shape = lambda xi, u: u * (3 * xi ** 2 - 2 * xi ** 3)   # 底固接、頂只能平移（剛性梁）：v(0)=v'(0)=v'(1)=0

    def frame(cv, base_x, u, col):
        for cx in (base_x, base_x + B):
            pts = [(cx + shape(i / 40, u), HH * i / 40) for i in range(41)]
            cv.poly(pts, col, 3.6)
        cv.line((base_x + u, HH), (base_x + B + u, HH), col, 5, cap="butt")
        mass_box(cv, base_x + u + 0.35, HH + 0.04, B - 0.7, 0.40)

    # 左：絕對座標
    a = Canvas(W, H, sx=58, ox=64, oy=104)
    frame_bg(a); title(a, "絕對座標：三個位移混在一起", "u^{t} 從固定參考點量")
    a.line((0, -0.5), (0, HH + 1.0), C["member"], 1.6, "4,4")
    a.text((-0.12, 0.9), "固定參考", 11.5, C["muted"], "end")
    for cx in (0, B):                                        # 原位置
        a.line((cx, 0), (cx, HH), C["ghost"], 2, "6,4")
    ground(a, UG - 0.45, UG + B + 0.45, 0, C["accent"])
    frame(a, UG, U, C["deform"])
    hdim(a, -0.35, 0, UG, "u_{g}", C["accent"], above=False)
    a.line((UG, -0.45), (UG, HH + 0.62), C["accent"], 1, "3,3")
    a.line((UG + U, HH + 0.45), (UG + U, HH + 0.95), C["dim"], 1, "3,3")
    hdim(a, HH + 0.88, 0, UG + U, "u^{t} = u_{g} + u", C["text"], above=True, size=13)
    hdim(a, HH + 0.58, UG, UG + U, "u", C["deform"], above=False, size=13)
    a.arrow((UG + B * 0.55, -0.62), (UG + B * 0.55 + 0.7, -0.62), C["accent"], 2.2, 8)
    a.math((UG + B * 0.55 + 0.8, -0.62), "ü_{g}".replace("ü", UDD), 13, C["accent"], "start")
    a.text_px(W / 2, H - 44, "m ü^{t} + c(u̇^{t} − u̇_{g}) + k(u^{t} − u_{g}) = 0".replace("ü", UDD).replace("u̇", UD),
              14, C["text"], font=FONT_M, italic=True)
    a.text_px(W / 2, H - 20, "彈簧與阻尼只「看得到」相對量 u = u^{t} − u_{g}", 12, C["muted"])

    # 右：相對座標（固定基礎 ＋ 等效力）
    b = Canvas(W, H, sx=58, ox=64, oy=104)
    frame_bg(b); title(b, "相對座標：固定基礎 ＋ 等效力", "結構變形一模一樣，只是觀察者跟著地面走")
    for cx in (0, B):
        b.line((cx, 0), (cx, HH), C["ghost"], 2, "6,4")
    ground(b, -0.45, B + 0.45, 0)
    frame(b, 0, U, C["deform"])
    b.line((U, HH + 0.45), (U, HH + 0.75), C["dim"], 1, "3,3")
    b.line((0, HH + 0.05), (0, HH + 0.75), C["dim"], 1, "3,3")
    hdim(b, HH + 0.68, 0, U, "u", C["deform"], above=True, size=14)
    b.arrow((U + B - 0.35, HH + 0.24), (U + B + 0.85, HH + 0.24), C["load"], 3, 10, "8,4")
    b.math((U + B + 0.25, HH + 0.62), "p_{eff} = −m ü_{g}".replace("ü", UDD), 13.5, C["load"])
    b.text((U + B + 0.2, HH - 0.15), "箭頭畫正向；", 10.5, C["muted"], "start")
    b.text((U + B + 0.2, HH - 0.45), "地面向右加速時", 10.5, C["muted"], "start")
    b.text((U + B + 0.2, HH - 0.75), "實際向左", 10.5, C["muted"], "start")
    b.text_px(W / 2, H - 44, ("m" + UDD + " + c" + UD + " + ku = −m" + UDD + "_{g}"), 14, C["text"], font=FONT_M, italic=True)
    b.text_px(W / 2, H - 20, "u 就是柱的變形 → 直接決定內力與層間變位", 12, C["muted"])
    save("U1-2-fig-E-base-excitation.svg", hcompose([a, b], "fE"))


# ═══════════════════ 圖 F　§4.3 L 形構架影響向量（SD-2004-4） ═══════════════════
def fig_influence():
    h1, h2, x3 = 1.0, 1.0, 1.4           # 繪圖用幾何（比例示意，結論與數值無關）
    W, H = 306, 380
    pts0 = {"O": (0, 0), "1": (0, h1), "2": (0, h1 + h2), "3": (x3, h1 + h2)}

    def base(cv, mp, col, w=4, ghost=False):
        c = C["ghost"] if ghost else col
        d = "6,4" if ghost else None
        cv.line(mp["O"], mp["2"], c, 2.4 if ghost else w, d, cap="butt")
        cv.line(mp["2"], mp["3"], c, 2.4 if ghost else w, d, cap="butt")
        if not ghost:
            for k in ("1", "2", "3"):
                cv.dot(mp[k], 7, C["member"], "#FFFFFF", 1.8)

    def mk(t, s):
        cv = Canvas(W, H, sx=84, ox=80, oy=100)
        frame_bg(cv); title(cv, t, s)
        return cv

    # (1) 模型與自由度
    a = mk("① 模型與自由度", "軸向剛性：3 個質量、3 個自由度")
    a.fixed_support((0, 0), 0, 16, C["member"])
    base(a, pts0, C["member"])
    for k, lab, dx in (("1", "m_1", -0.16), ("2", "m_2", -0.16)):
        a.math((pts0[k][0] + dx, pts0[k][1] + 0.16), lab, 14, C["text"], "end")
    a.math((x3 + 0.02, h1 + h2 + 0.24), "m_3", 14, C["text"])
    a.arrow(pts0["1"], (0.5, h1), C["deform"], 2.6, 8); a.math((0.56, h1), "u_1", 14, C["deform"], "start")
    a.arrow((0.0, h1 + h2 + 0.17), (0.5, h1 + h2 + 0.17), C["deform"], 2.6, 8); a.math((0.56, h1 + h2 + 0.17), "u_2", 14, C["deform"], "start")
    a.arrow(pts0["3"], (x3, h1 + h2 - 0.5), C["deform"], 2.6, 8); a.math((x3 + 0.08, h1 + h2 - 0.42), "u_3↓", 14, C["deform"], "start")
    vdim(a, -0.42, 0, h1, "h_1", side=-1); vdim(a, -0.42, h1, h1 + h2, "h_2", side=-1)
    hdim(a, h1 + h2 + 0.52, 0, x3, "x_3", above=True)
    a.text_px(W / 2, H - 50, "m_{3} 水平位移 ≡ u_{2}（梁不可伸縮）", 12, C["accent"], weight="700")
    a.text_px(W / 2, H - 28, "u_{3} 定義：向下為正", 12, C["muted"])

    # (2) 支承水平剛體平移 1
    S = 0.42                              # 繪圖時「1 單位」的長度
    b = mk("② 支承平移 1", "整體剛體平移，不變形")
    ground(b, -0.45, 0.45 + S, 0)
    base(b, pts0, None, ghost=True)
    mp = {k: (x + S, y) for k, (x, y) in pts0.items()}
    base(b, mp, C["deform"])
    for k, yoff in (("1", 0), ("2", 0)):
        b.arrow(pts0[k], (pts0[k][0] + S, pts0[k][1]), C["load"], 2.6, 8)
    b.math((S + 0.12, h1 - 0.2), "ι_1 = 1", 13.5, C["load"], "start")
    b.math((S + 0.12, h1 + h2 - 0.2), "ι_2 = 1", 13.5, C["load"], "start")
    b.arrow((0, -0.25), (S, -0.25), C["accent"], 2.6, 8)
    b.math((S + 0.1, -0.25), "u_{g} = 1", 12.5, C["accent"], "start")
    b.math((x3 + S / 2, h1 + h2 + 0.30), "ι_3 = 0", 14, C["load"], weight="700")
    b.text((x3 + S / 2, h1 + h2 - 0.30), "m₃ 只平移、不下沉".replace("m₃", "m3"), 11, C["muted"])
    b.text_px(W / 2, H - 50, "{ι_{x}} = {1, 1, 0}^{T}", 13.5, C["text"], weight="700", font=FONT_M)
    b.text_px(W / 2, H - 28, "垂直自由度不被水平地震激發", 12, C["muted"])

    # (3) 支承順時鐘剛體轉動 θ
    TH = 0.24                             # 繪圖用 θ（放大示意；採小角度線性化）
    c = mk("③ 支承順時鐘轉 θ", "Δx = y_{0}θ、Δy = −x_{0}θ（比例為真）")
    rot = lambda p: (p[0] + p[1] * TH, p[1] - p[0] * TH)
    gl, gr = rot((-0.45, 0)), rot((0.45, 0))
    ground(c, -0.45, 0.45, 0, C["ghost"])
    c.line(gl, gr, C["accent"], 3, cap="butt")
    base(c, pts0, None, ghost=True)
    mp = {k: rot(p) for k, p in pts0.items()}
    base(c, mp, C["deform"])
    c.arrow(pts0["1"], (h1 * TH, h1), C["load"], 2.6, 7)
    c.math((-0.1, h1), "h_1θ", 13.5, C["load"], "end")
    c.arrow(pts0["2"], ((h1 + h2) * TH, h1 + h2), C["load"], 2.6, 7)
    c.math((0.02, h1 + h2 + 0.2), "(h_1+h_2)θ", 13, C["load"], "start")
    c.arrow(pts0["3"], (x3, h1 + h2 - x3 * TH), C["load"], 2.8, 8)
    c.math((x3 - 0.05, h1 + h2 - x3 * TH - 0.24), "x_3θ", 13.5, C["load"], "end", weight="700")
    c.text((x3 + 0.02, h1 + h2 - x3 * TH - 0.24), "（向下）", 11.5, C["load"], "start")
    arc(c, (0, 0), 0.62, math.pi / 2, math.pi / 2 - TH, C["accent"], 2)
    c.math((0.30, 0.5), "θ", 13, C["accent"], "start")
    c.text_px(W / 2, H - 50, "{ι_{θ}} = {h_{1}, h_{1}+h_{2}, x_{3}}^{T}", 13.5, C["text"], weight="700", font=FONT_M)
    c.text_px(W / 2, H - 28, "單位：長度（每弧度）", 12, C["muted"])
    save("U1-2-fig-F-influence.svg", hcompose([a, b, c], "fF"))


# ═══════════════════ 圖 G　§6 廣義單自由度：懸臂梁 ψ(x) ═══════════════════
def cantilever_mode(n=1):
    roots = [brentq(lambda b: math.cos(b) * math.cosh(b) + 1, lo, hi) for lo, hi in ((1, 3), (4, 5.5), (7, 8.5))]
    b = roots[n - 1]
    s = (math.cosh(b) + math.cos(b)) / (math.sinh(b) + math.sin(b))
    f = lambda x: math.cosh(b * x) - math.cos(b * x) - s * (math.sinh(b * x) - math.sin(b * x))
    return b, f


def fig_generalized():
    psi = lambda x: 1 - math.cos(math.pi * x / 2)
    b1, phi = cantilever_mode(1)
    phiL = phi(1.0)
    stat = lambda x: (x ** 4 - 4 * x ** 3 + 6 * x ** 2) / 3          # 均布載重靜撓度（端點=1）
    I1 = quad(psi, 0, 1)[0]                     # = 1 − 2/π
    I2 = quad(lambda x: psi(x) ** 2, 0, 1)[0]  # = 3/2 − 4/π
    assert abs(I1 - (1 - 2 / math.pi)) < 1e-12 and abs(I2 - (1.5 - 4 / math.pi)) < 1e-12

    # 左：梁與三種形狀
    a = Canvas(440, 360, sx=300, ox=50, oy=225)
    frame_bg(a); title(a, "猜一個形狀 ψ(x)：三種選法幾乎重疊", "端點正規化為 1；繪圖撓度放大")
    A = 0.28                                         # 繪圖振幅（端點）
    a.fixed_support((0, 0), 90, 18, C["member"])
    a.line((0, 0), (1, 0), C["ghost"], 2.4, "6,4")
    xs = np.linspace(0, 1, 81)
    a.poly([(x, -A * stat(x)) for x in xs], C["accent"], 2.2, "3,3")
    a.poly([(x, -A * phi(x) / phiL) for x in xs], C["bmd"], 2.4, "8,4")
    a.poly([(x, -A * psi(x)) for x in xs], C["deform"], 3.2)
    a.udl((0, 0.02), (1, 0.02), 0.11, 10, C["load"], 1.8)
    a.math((0.5, 0.20), "p_0(t)（均布）", 13.5, C["load"])
    a.math((1.02, -A), "ψ(L) = 1", 13, C["deform"], "start")
    a.math((1.02, 0.0), "x = L", 12, C["muted"], "start")
    items = [(C["deform"], "1 − cos(πx/2L)　ω 係數 3.664"),
             (C["accent"], "均布載重靜撓度　ω 係數 3.530"),
             (C["bmd"], f"精確第一振態　ω 係數 {b1**2:.3f}")]
    for i, (col, lab) in enumerate(items):
        y = 270 + i * 22
        a.parts.append(f'<line x1="40" y1="{y}" x2="66" y2="{y}" stroke="{col}" stroke-width="3"/>')
        a.text_px(74, y, lab, 12, C["text"], "start")

    # 右：被積函數 ψ 與 ψ^{2}（面積 = 廣義量）
    b = Canvas(480, 360, sx=1, ox=0, oy=0)
    frame_bg(b); title(b, "面積就是廣義量（÷ m̄L 或 ÷ p_{0}L）", "ψ 一次方 → p*、L*；ψ 平方 → m*")
    X0, X1, Y0, Y1 = 60, 450, 80, 290
    px = lambda x: X0 + x * (X1 - X0)
    py = lambda v: Y1 - v * (Y1 - Y0)
    b.parts.append(f'<rect x="{X0}" y="{Y0}" width="{X1-X0}" height="{Y1-Y0}" fill="#FFFFFF" stroke="{C["member2"]}" stroke-dasharray="5,4"/>')
    up = [(px(x), py(psi(x))) for x in xs]
    up2 = [(px(x), py(psi(x) ** 2)) for x in xs]
    poly = lambda pts, fill, op: b.parts.append(
        f'<polygon fill="{fill}" opacity="{op}" points="{X0},{Y1} ' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f' {X1},{Y1}"/>')
    poly(up, C["deform"], 0.16)
    poly(up2, C["deform"], 0.22)
    b.parts.append('<polyline fill="none" stroke="%s" stroke-width="2.6" points="%s"/>' % (C["deform"], " ".join(f"{x:.1f},{y:.1f}" for x, y in up)))
    b.parts.append('<polyline fill="none" stroke="%s" stroke-width="2" stroke-dasharray="7,4" points="%s"/>' % (C["deform"], " ".join(f"{x:.1f},{y:.1f}" for x, y in up2)))
    for v in (0, 0.5, 1):
        b.text_px(X0 - 6, py(v), f"{v:g}", 11, C["muted"], "end")
    for x in (0, 0.5, 1):
        b.text_px(px(x), Y1 + 14, ["0", "L/2", "L"][int(x * 2)], 11, C["muted"])
    b.text_px(px(0.86), py(0.88) - 4, "ψ", 15, C["deform"], weight="700", font=FONT_M, italic=True)
    b.text_px(px(0.95), py(0.55), "ψ^{2}", 15, C["deform"], weight="700", font=FONT_M, italic=True)
    lx, ly = X0 + 14, Y0 + 20
    b.rect_px(lx - 6, ly - 12, 226, 110, "#FFFFFF", 6, C["border"], 1)
    b.rect_px(lx, ly - 7, 16, 14, C["deform"], 2); b.parts[-1] = b.parts[-1].replace("/>", ' opacity="0.16"/>')
    b.rect_px(lx + 6, ly - 7, 10, 14, C["deform"], 0); b.parts[-1] = b.parts[-1].replace("/>", ' opacity="0.38"/>')
    b.text_px(lx + 24, ly, f"淺＋深 = ∫ψ dx = {I1:.4f}L", 12, C["text"], "start", "700")
    b.text_px(lx + 24, ly + 17, "→ p* = 0.3634 p_{0}L，L* = 0.3634 m̄L", 11, C["muted"], "start")
    b.rect_px(lx, ly + 36, 16, 14, C["deform"], 2); b.parts[-1] = b.parts[-1].replace("/>", ' opacity="0.38"/>')
    b.text_px(lx + 24, ly + 43, f"深色 = ∫ψ^{{2}} dx = {I2:.4f}L", 12, C["text"], "start", "700")
    b.text_px(lx + 24, ly + 60, "→ m* = 0.2268 m̄L", 11, C["muted"], "start")
    b.text_px(lx, ly + 82, "虛線框 = 1 × L（相當於總荷重 p_{0}L）", 10.5, C["member2"], "start")
    b.text_px(240, 322, "靠近固端 ψ ≈ 0：那裡的荷重與質量「使不上力」", 12, C["accent"], weight="700")
    b.text_px(240, 342, f"所以 p* &lt; p_{0}L、m* &lt; m̄L；Γ = L*/m* = {I1/I2:.3f}", 12, C["muted"])
    save("U1-2-fig-G-generalized.svg", hcompose([a, b], "fG"))


# ═══════════════════ 圖 H　§6.3 軸壓下沉：幾何勁度 ═══════════════════
def fig_geometric():
    L, Q = 3.4, 1.15                     # 繪圖用：柱長、頂端側移（放大）
    psi = lambda xi: 1 - math.cos(math.pi * xi / 2)
    dpsi = lambda xi: math.pi / 2 * math.sin(math.pi * xi / 2)       # dψ/dξ
    # 不可伸長：沿弧長 s 積分，x = Qψ(s/L)，dy = sqrt(1 − (dx/ds)²) ds
    n = 200
    pts, y = [(0.0, 0.0)], 0.0
    for i in range(1, n + 1):
        s0, s1 = (i - 1) / n, i / n
        sm = (s0 + s1) / 2
        slope = Q / L * dpsi(sm)
        y += L / n * math.sqrt(1 - slope ** 2)
        pts.append((Q * psi(s1), y))
    drop_exact = L - y
    drop_lin = 0.5 * (Q ** 2 / L) * (math.pi ** 2 / 8)              # ½ q²∫ψ'²dx，∫ψ'²dx = π²/(8L)
    W, H = 920, 380
    cv = Canvas(W, H, sx=64, ox=170, oy=46)
    frame_bg(cv)
    title(cv, "柱彎曲時頂端會下沉：軸壓 N 隨之做正功", "柱長不變（不可伸長），水平投影變短")
    cv.fixed_support((0, 0), 0, 16, C["member"])
    cv.line((0, 0), (0, L), C["ghost"], 3, "7,5")
    cv.poly(pts, C["deform"], 4)
    xt, yt = pts[-1]
    cv.line((-0.5, L), (xt + 0.6, L), C["ghost"], 1.3, "4,3")
    cv.line((xt - 0.2, yt), (xt + 0.6, yt), C["ghost"], 1.3, "4,3")
    vdim(cv, xt + 0.45, yt, L, "Δ", C["accent"], side=1, size=15)
    hdim(cv, L + 1.05, 0, xt, "q", C["deform"], above=True, size=14)
    cv.text((xt + 0.1, L + 1.05), "頂端側移", 11.5, C["deform"], "start")
    for xx in (0.0, xt):
        cv.line((xx, L + 1.05), (xx, L + 0.05 if xx == 0 else yt + 0.08), C["dim"], 1, "3,3")
    cv.arrow((xt, yt + 0.9), (xt, yt + 0.12), C["load"], 3.2, 11)
    cv.math((xt - 0.12, yt + 0.62), "N", 16, C["load"], "end", weight="700")
    cv.math((0.62, L * 0.36), "ψ = 1 − cos(πx/2L)", 13, C["deform"], "start")
    # 右側說明
    x = 470
    cv.rect_px(x - 16, 74, 446, 292, "#FFFFFF", 10, C["border"], 1)
    rows = [("下沉量（小變形）", C["text"], True),
            ("Δ = ½ q^{2} ∫ (ψ′)^{2} dx", C["accent"], False),
            ("軸壓做的功 = 損失的位能", C["text"], True),
            ("N·Δ = ½ (N∫(ψ′)^{2}dx) q^{2} = ½ k_{G} q^{2}", C["load"], False),
            ("所以有效勁度要扣掉它", C["text"], True),
            ("k* = k_{e} − k_{G}", C["text"], False),
            ("軸壓 N 一定是「扣」，寫成加號 = 壓越大越硬（荒謬）", C["comp"] if "comp" in C else C["load"], True),
            (f"本圖驗證：q/L = {Q/L:.3f} 時，", C["muted"], True),
            (f"Δ/L 線性化 = {drop_lin/L:.4f}，弧長積分 = {drop_exact/L:.4f}", C["muted"], True)]
    yy = 104
    for s, col, zh in rows:
        if zh:
            cv.text_px(x, yy, s, 12.5, col, "start", "700" if col == C["text"] else "400")
        else:
            cv.text_px(x + 12, yy, s, 15, col, "start", "700", font=FONT_M, italic=True)
        yy += 30 if not zh else 27
    save("U1-2-fig-H-geometric.svg", cv.svg().replace("<svg ", '<svg role="img" ', 1))
    return drop_lin / L, drop_exact / L


# ═══════════════════ 圖 I　§7 三種邊界的振態函數 ═══════════════════
def fig_modes():
    def ff_mode(n):
        roots = [brentq(lambda b: math.cos(b) * math.cosh(b) - 1, lo, hi) for lo, hi in ((4, 5.5), (7, 8.5))]
        b = roots[n - 1]
        s = (math.cosh(b) - math.cos(b)) / (math.sinh(b) - math.sin(b))
        return b, lambda x: math.cosh(b * x) - math.cos(b * x) - s * (math.sinh(b * x) - math.sin(b * x))

    cases = [("簡支 – 簡支", [(math.pi, lambda x: math.sin(math.pi * x)), (2 * math.pi, lambda x: math.sin(2 * math.pi * x))], ("pin", "roller")),
             ("固定 – 自由（懸臂）", [cantilever_mode(1), cantilever_mode(2)], ("fixed", None)),
             ("固定 – 固定", [ff_mode(1), ff_mode(2)], ("fixed", "fixed"))]
    W, H = 306, 300
    xs = np.linspace(0, 1, 161)
    panels = []
    for name, modes, (sl, sr) in cases:
        cv = Canvas(W, H, sx=230, ox=38, oy=150)
        frame_bg(cv); title(cv, name)
        cv.line((0, 0), (1, 0), C["member"], 3.5, cap="butt")
        if sl == "fixed": cv.fixed_support((0, 0), 90, 14, C["member"])
        else: cv.support((0, 0), sl, 0, 12, C["member"])
        if sr == "fixed": cv.fixed_support((1, 0), -90, 14, C["member"])
        elif sr: cv.support((1, 0), sr, 0, 12, C["member"])
        for (b, f), col, dash, A in zip(modes, (C["deform"], C["sfd"]), (None, "7,4"), (0.22, 0.22)):
            m = max(abs(f(x)) for x in xs)
            cv.poly([(x, A * f(x) / m) for x in xs], col, 2.8 if dash is None else 2.0, dash)
        b1 = modes[0][0]
        b2 = modes[1][0]
        cv.text_px(W / 2, 222, f"第一振態 β_{1}L = {b1:.4f}", 12.5, C["deform"], weight="700")
        cv.text_px(W / 2, 244, f"ω_{1} = {b1**2:.3f}·√(EI/m̄L^{4})", 12.5, C["text"])
        cv.text_px(W / 2, 270, f"第二振態（虛線）β_{2}L = {b2:.3f}", 11.5, C["sfd"])
        panels.append(cv)
    save("U1-2-fig-I-modes.svg", hcompose(panels, "fI"))


if __name__ == "__main__":
    fig_dalembert()
    fig_virtual_work()
    fig_inverted_pendulum()
    fig_static_eq()
    fig_base_excitation()
    fig_influence()
    fig_generalized()
    print("geometric drop (lin, exact):", fig_geometric())
    fig_modes()
