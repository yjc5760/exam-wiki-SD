# -*- coding: utf-8 -*-
"""SD-2023-4 圖解產生器（struct-diagram）。可重跑：python gen_SD-2023-4.py
所有數值皆由下方常數區（題目給定 / §4 公式）算出，改常數即改圖。"""
import os, sys, math
SKILL = os.environ.get("STRUCTDRAW", os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "struct-diagram", "scripts"))
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose

PI = math.pi
# ── 題目給定（§1）──
M, K = 1.0, 16 * PI**2            # kg, N/m
WN = math.sqrt(K / M)             # ω_n = 4π rad/s
OMEGAS = (2 * PI, 4 * PI)         # rad/s
RHOS = (0.01, 0.02)               # m
# ── 三種消能器的力半幅（§1 附圖）──
DEV = {
    "a": dict(shape="ellipse", F=lambda r, w: 5 * r * w,  name="圖a 線性黏滯", col=C["deform"]),
    "b": dict(shape="ellipse", F=lambda r, w: 20 * PI * r, name="圖b 速率無關（遲滯型）", col=C["bmd"]),
    "c": dict(shape="rect",    F=lambda r, w: 0.4 * PI,   name="圖c 摩擦（矩形）", col=C["accent"]),
}

def W_D(d, r, w):
    F = DEV[d]["F"](r, w)
    return PI * r * F if DEV[d]["shape"] == "ellipse" else 4 * r * F

def U_max(r):
    return 0.5 * K * r * r

def xi(d, r, w):        # §4 正解：ξ = (ω_n/ω)·W_D/(4πU_{max})
    return (WN / w) * W_D(d, r, w) / (4 * PI * U_max(r))

def xi_simple(d, r, w): # 原解答的簡化式（僅 ω = ω_n 時成立）
    return W_D(d, r, w) / (4 * PI * U_max(r))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
TAG = "SD-2023-4"

# ═════════ 圖 1：三種遲滯迴圈（題目重繪＋與彈簧儲能比較）═════════
def fig1(r=0.01, w=2 * PI):
    panels = []
    kr = K * r                                   # 彈簧在 ρ 時的力，作為力軸單位
    for d in "abc":
        PW, PH = 340, 430
        s = 112                                  # 1 個無因次單位 = 112 px
        cv = Canvas(PW, PH, sx=s, ox=PW / 2, oy=PH - 70 - 1.3 * s)
        cv.panel(DEV[d]["name"])
        col = DEV[d]["col"]
        f = DEV[d]["F"](r, w) / kr               # 力半幅 / kρ
        # U_max 三角形（彈簧）
        cv.polygon([(0, 0), (1, 0), (1, 1)], C["fill_t"])
        cv.line((-1.15, -1.15), (1.15, 1.15), C["load"], 1.6, dash="6 4")
        # 遲滯迴圈
        if DEV[d]["shape"] == "ellipse":
            pts = [(math.cos(t), f * math.sin(t)) for t in [2 * PI * i / 120 for i in range(121)]]
        else:
            pts = [(-1, -f), (1, -f), (1, f), (-1, f), (-1, -f)]
        cv.polygon(pts, col, op=0.22); cv.poly(pts, col, 2.6)
        cv.axes((-1.3, 0), 2.6, 0, ("x", ""), C["muted"]); cv.line((0, -1.25), (0, 1.25), C["muted"], 1.4)
        cv.math((1, 0), "ρ", 14, C["text"], dy=14); cv.math((-1, 0), "−ρ", 14, C["text"], dy=14)
        lab = {"a": "5ρω", "b": "20πρ", "c": "0.4π"}[d]
        cv.math((0, f), lab, 14, col, "end", dx=-6, dy=-11, weight="700")
        cv.math((1, 1), "kρ", 13, C["load"], "start", dx=6)
        wd = W_D(d, r, w); u = U_max(r)
        cv.text_px(PW / 2, PH - 50, f"W_{{D}} = {wd*1e3:.2f} mJ ，U_{{max}} = {u*1e3:.2f} mJ", 12.5, C["text"])
        cv.text_px(PW / 2, PH - 25, f"ξ_{{eq}} = {100*xi(d, r, w):.1f}%", 13.5, col, weight="700")
        panels.append(cv)
    return compose(panels,
        title="圖 1　三種遲滯迴圈與彈簧儲能（ρ = 0.01 m，ω = 2π rad/s，力軸以 kρ 正規化）",
        sub="色塊＝每循環消散能量；紅色三角形＝主彈簧最大儲能（彈簧線 F = kx 下方面積），兩者相比即得阻尼比",
        note="橢圓面積 = π·半軸·半軸；矩形面積 = 全寬 × 全高 = 4·ρ·力半幅",
        path=os.path.join(OUT, f"{TAG}-fig-1-loops.svg"))

# ═════════ 圖 3：ξ_{eq} 對 ω/ω_n ═════════
def fig2():
    W, H = 860, 520
    L, R, T, B = 86, 210, 84, 70
    r0, r1, ymax = 0.4, 1.25, 1.2
    gx = lambda r: L + (r - r0) / (r1 - r0) * (W - L - R)
    gy = lambda y: B + y / ymax * (H - T - B)
    cv = Canvas(W, H, sx=1, bg="#FFFFFF")
    cv.text_px(W / 2, 30, "圖 3　等值阻尼比 ξ_{eq} 隨頻率比 ω/ω_n 的變化", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 55, "ω_n = √(k/m) = 4π rad/s；題目的兩個頻率正好是 ω/ω_n = 0.5 與 1.0", 13, C["muted"])
    # 格線與軸
    for k in range(0, 13, 2):
        y = k / 10
        cv.line((gx(r0), gy(y)), (gx(r1), gy(y)), C["border"], 1)
        cv.text_px(gx(r0) - 10, H - gy(y), f"{int(100*y)}%", 12, C["muted"], "end")
    for rr in (0.4, 0.5, 0.6, 0.8, 1.0, 1.2):
        cv.text_px(gx(rr), H - B + 20, f"{rr:g}", 12, C["muted"])
    cv.line((gx(r0), gy(0)), (gx(r1), gy(0)), C["muted"], 1.6)
    cv.line((gx(r0), gy(0)), (gx(r0), gy(ymax)), C["muted"], 1.6)
    cv.math_px(gx(r1) + 8, H - B, "ω/ω_n", 14, C["muted"], "start")
    for rr in (0.5, 1.0):
        cv.line((gx(rr), gy(0)), (gx(rr), gy(ymax)), C["dim"], 1.2, dash="4 4")
    cv.line((gx(r0), gy(1)), (gx(r1), gy(1)), C["load"], 1.6, dash="8 5")
    cv.text_px(gx(r1) - 6, H - gy(1) - 12, "ξ = 100%（臨界阻尼）", 12, C["load"], "end")
    rs = [r0 + (r1 - r0) * i / 200 for i in range(201)]
    def curve(fn, col, w=2.8, dash=None):
        pts = [(gx(r), gy(min(fn(r), ymax))) for r in rs if fn(r) <= ymax]
        cv.poly(pts, col, w, dash)
    series = [
        ("a", 0.01, C["deform"], None, "圖a（任一 ρ）"),
        ("b", 0.01, C["bmd"], None, "圖b（任一 ρ）"),
        ("c", 0.01, C["accent"], None, "圖c，ρ = 0.01"),
        ("c", 0.02, C["accent"], "9 5", "圖c，ρ = 0.02（虛線）"),
    ]
    # 原解答誤用的簡化式（圖a）
    curve(lambda r: xi_simple("a", 0.01, r * WN), C["ghost"], 2.4, "3 5")
    for d, rho, col, dash, _ in series:
        curve(lambda r, d=d, rho=rho: xi(d, rho, r * WN), col, 2.8, dash)
        for w in OMEGAS:
            cv.dot((gx(w / WN), gy(xi(d, rho, w))), 5.2, col)
    leg = [(c_, l_) for _, _, c_, _, l_ in series] + [(C["ghost"], "原解答圖a（點線）")]
    cv.legend(W - R + 22, T + 40, leg, 12.5, 26)
    cv.text_px(W / 2, H - 22, "圖a 為水平線：真正的黏滯阻尼比 c/(2mω_n) 不隨外力頻率改變；圖b、圖c 的 W_D 與 ω 無關，故 ξ_{eq} 與 ω 成反比", 12.5, C["muted"])
    cv.save(os.path.join(OUT, f"{TAG}-fig-3-xi-freq.svg"))
    return cv

# ═════════ 圖 2：12 組結果（正解 vs 原解答）═════════
def fig3():
    rows = [(d, w, r) for d in "abc" for w in OMEGAS for r in RHOS]
    W, rowh = 960, 34
    T, B = 112, 70
    H = T + rowh * len(rows) + 3 * 14 + B
    x0, x1, vmax = 290, W - 150, 1.1
    gx = lambda v: x0 + v / vmax * (x1 - x0)
    cv = Canvas(W, H, sx=1, bg="#FFFFFF")
    cv.text_px(W / 2, 30, "圖 2　12 組等值阻尼比：正解與原解答", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 55, "實心長條＝正解 (ω_n/ω)·W_D/(4πU_{max})；空心框＝原解答 W_D/(4πU_{max})", 13, C["muted"])
    for k in range(0, 12, 2):
        v = k / 10; x = gx(v)
        cv.parts.append(f'<line x1="{x}" y1="{T-14}" x2="{x}" y2="{H-B+6}" stroke="{C["border"]}" stroke-width="1"/>')
        cv.text_px(x, T - 26, f"{int(100*v)}%", 12, C["muted"])
    xc = gx(1.0)
    cv.parts.append(f'<line x1="{xc}" y1="{T-14}" x2="{xc}" y2="{H-B+6}" stroke="{C["load"]}" stroke-width="1.6" stroke-dasharray="7 5"/>')
    cv.text_px(xc, H - B + 22, "臨界阻尼", 12, C["load"])
    y = T
    for i, (d, w, r) in enumerate(rows):
        if i and rows[i - 1][0] != d: y += 14
        col = DEV[d]["col"]
        v, v0 = xi(d, r, w), xi_simple(d, r, w)
        if i % 4 == 0: cv.text_px(24, y + rowh * 2 - rowh / 2, DEV[d]["name"], 13.5, col, "start", weight="700")
        cv.text_px(x0 - 12, y + rowh / 2, f"ω = {w/PI:g}π, ρ = {r:g}", 12.5, C["text"], "end")
        cv.rect_px(x0, y + 7, gx(v) - x0, rowh - 14, col, 4)
        cv.rect_px(x0, y + 7, gx(v0) - x0, rowh - 14, "none", 4, C["text"], 1.4)
        tag = f"{100*v:.3g}%" + ("" if abs(v - v0) < 1e-9 else f"（原 {100*v0:.3g}%）")
        cv.text_px(max(gx(v), gx(v0)) + 8, y + rowh / 2, tag, 12.5, C["load"] if abs(v - v0) > 1e-9 else C["text"], "start",
                   weight="700" if abs(v - v0) > 1e-9 else "400")
        y += rowh
    cv.text_px(W / 2, H - 24, "ω = 4π（= ω_n）時兩式相同；ω = 2π 時原解答全部低估一半，圖c 小振幅實際已達臨界阻尼", 12.5, C["muted"])
    cv.save(os.path.join(OUT, f"{TAG}-fig-2-xi-compare.svg"))
    return cv

if __name__ == "__main__":
    fig1(); fig2(); fig3()
    for d in "abc":
        print(d, [f"{100*xi(d, r, w):.2f}" for w in OMEGAS for r in RHOS])
