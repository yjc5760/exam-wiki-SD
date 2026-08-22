#!/usr/bin/env python3
"""
SD-2023-2 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2023-2.py [輸出目錄]      # 預設輸出到 ./figs

圖上每個數值都由頂端常數區的解題結果算出，改數字重跑，圖形跟著變。
"""
import sys, os, math

# 本腳本相依 struct-diagram skill 的 scripts/（可用環境變數覆寫路徑）
_SK = os.environ.get("STRUCT_DIAGRAM_SCRIPTS") or \
      os.path.expanduser("~/.claude/skills/synced/struct-diagram/scripts")
sys.path.insert(0, _SK)

from structdraw import (Canvas, C, FONT, FONT_M, compose, esc,
                        column_shape, beam_shape, member_shape, hermite)
from recipes import plot_function, bar_compare

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"

# ══════════════════════════════════════════════════════════
# lab()：混排標籤。含中文的字串必須走 FONT——FONT_M 這串襯線數學字型
#        沒有 CJK 字，中文會在渲染時整個消失（不是變方框，是不見）。
# ══════════════════════════════════════════════════════════
def _cjk(s):
    return any(ord(ch) > 0x2E80 for ch in str(s))


def lab(cv, x, y, s, size=13, color=C["text"], anchor="middle", weight="700"):
    if _cjk(s):
        cv.text_px(x, y, s, size, color, anchor, weight)
    else:
        cv.math_px(x, y, s, size, color, anchor, weight)


# ══════════════════════════════════════════════════════════
# Ax：資料座標 → Canvas 模型座標（Canvas 為等向縮放，故需自行正規化）
# ══════════════════════════════════════════════════════════
class Ax:
    def __init__(self, cv, xr, yr, box=(0.0, 0.0, 1.0, 0.62)):
        self.cv = cv
        (self.xa, self.xb), (self.ya, self.yb) = xr, yr
        self.bx, self.by, self.bw, self.bh = box

    def X(self, x): return self.bx + (x - self.xa) / (self.xb - self.xa) * self.bw
    def Y(self, y): return self.by + (y - self.ya) / (self.yb - self.ya) * self.bh
    def P(self, x, y): return (self.X(x), self.Y(y))

    def curve(self, xs, ys, color, w=2.8, dash=None):
        self.cv.poly([self.P(x, y) for x, y in zip(xs, ys)], color, w, dash=dash)

    def area(self, xs, ys, fill, ybase=None):
        yb = self.ya if ybase is None else ybase
        pts = [self.P(xs[0], yb)] + [self.P(x, y) for x, y in zip(xs, ys)] + [self.P(xs[-1], yb)]
        self.cv.polygon(pts, fill)

    def vline(self, x, y0, y1, color, w=1.6, dash="5 4"):
        self.cv.line(self.P(x, y0), self.P(x, y1), color, w, dash=dash)

    def hline(self, y, x0, x1, color, w=1.6, dash="5 4"):
        self.cv.line(self.P(x0, y), self.P(x1, y), color, w, dash=dash)

    def frame(self, xticks, yticks, xlabel="", ylabel="",
              xfmt="{:g}", yfmt="{:g}", grid=True, tick_size=12.5, lab_size=14):
        cv = self.cv
        if grid:
            for t in xticks:
                cv.line(self.P(t, self.ya), self.P(t, self.yb), "#E8ECF2", 1.1)
            for t in yticks:
                cv.line(self.P(self.xa, t), self.P(self.xb, t), "#E8ECF2", 1.1)
        cv.line(self.P(self.xa, self.ya), self.P(self.xb, self.ya), C["muted"], 1.8)
        cv.line(self.P(self.xa, self.ya), self.P(self.xa, self.yb), C["muted"], 1.8)
        for t in xticks:
            cv.text_px(cv.X(self.X(t)), cv.Y(self.Y(self.ya)) + 17, xfmt.format(t),
                       tick_size, C["muted"])
        for t in yticks:
            cv.text_px(cv.X(self.X(self.xa)) - 9, cv.Y(self.Y(t)), yfmt.format(t),
                       tick_size, C["muted"], "end")
        if xlabel:
            lab(cv, cv.X(self.X((self.xa + self.xb) / 2)),
                cv.Y(self.Y(self.ya)) + 42, xlabel, lab_size, C["text"])
        if ylabel:
            lab(cv, cv.X(self.X(self.xa)), cv.Y(self.Y(self.yb)) - 24,
                ylabel, lab_size, C["text"])

    def mark(self, x, y, label, color, dx=10, dy=-14, r=5.6, size=13.5, anchor="start"):
        self.cv.dot(self.P(x, y), r, fill=color, stroke="#FFFFFF", w=2.0)
        for j, ln in enumerate(str(label).split("\n")):
            lab(self.cv, self.cv.X(self.X(x)) + dx, self.cv.Y(self.Y(y)) + dy + j * 19,
                ln, size, color, anchor)

    def at(self, x, y, label, color, dx=0, dy=0, size=13, anchor="middle"):
        """在資料座標處放一個標籤（不畫點）"""
        for j, ln in enumerate(str(label).split("\n")):
            lab(self.cv, self.cv.X(self.X(x)) + dx, self.cv.Y(self.Y(y)) + dy + j * 19,
                ln, size, color, anchor)


TAG = "SD-2023-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2023-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定
M_KG = 1.0e4                       # m_1 = m_2（kg）
K1, K2 = 2.0e5, 1.8e5              # 層間勁度（N/m）
F_REF = [1.0, 5.0]                 # Rayleigh 控制點頻率（Hz）
XI_REF = [0.03, 0.05]              # 對應阻尼比

# §4【1】剪力建築勁度矩陣——K11 是 k1+k2，不是 k1
K11, K12, K22 = K1 + K2, -K2, K2

# §4【2】特徵方程（λ = ω²）：由矩陣直接算出，不是抄結果
LAM_SUM = (K11 + K22) / M_KG                                  # = 56
LAM_PROD = (K11 * K22 - K12 ** 2) / M_KG ** 2                 # = 360
_disc = math.sqrt(LAM_SUM ** 2 - 4 * LAM_PROD)
LAM = [(LAM_SUM - _disc) / 2, (LAM_SUM + _disc) / 2]          # 28 ∓ 2√106
WN = [math.sqrt(l) for l in LAM]
FN = [w / (2 * math.pi) for w in WN]

# §4【3】振態向量（以 φ_1i = 1 正規化）：r = (K11 − mλ)/(−K12) = (5±√106)/9
RS = [(K11 - M_KG * l) / (-K12) for l in LAM]

# §4【4】～【6】模態量（一律以精確根計算，驗算才會收斂）
MS = [M_KG * (1 + r ** 2) for r in RS]
KS = [LAM[i] * MS[i] for i in range(2)]
GAM = [M_KG * (1 + RS[i]) / MS[i] for i in range(2)]
MEFF_SUM = sum(GAM[i] ** 2 * MS[i] for i in range(2))          # 應恰為 20000 kg

# §4(二)【2】Rayleigh 阻尼：兩控制點聯立（角頻率，不是 Hz）
W_REF = [2 * math.pi * f for f in F_REF]
BETA = 2 * (XI_REF[1] * W_REF[1] - XI_REF[0] * W_REF[0]) / (W_REF[1] ** 2 - W_REF[0] ** 2)
ALPHA = 2 * XI_REF[0] * W_REF[0] - W_REF[0] ** 2 * BETA


def zeta(w):
    """§4(二)【1】ξ(ω) = α/(2ω) + βω/2"""
    return ALPHA / (2 * w) + BETA * w / 2


XI1 = zeta(WN[0])                       # §4(二)【3】第一振態阻尼比 = 0.05206
W_MIN = math.sqrt(ALPHA / BETA)         # §5 進階：最小阻尼點
F_MIN = W_MIN / (2 * math.pi)
F_GEO = math.sqrt(F_REF[0] * F_REF[1])  # 幾何平均——只在兩控制點 ξ 相等時才等於 F_MIN

# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。
MODE_COL = [C["deform"], C["load"]]


def _ticks(vmax, n=4):
    raw = vmax / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min(s_ for s_ in (1, 2, 2.5, 5, 10) if s_ * mag >= raw) * mag
    k = int(vmax / step)
    return [round(step * i, 6) for i in range(-k, k + 1)]


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪：兩個層間彈簧 k_1、k_2 各自連到哪兩個自由度，一眼看清楚。
    攔錯：K_11 只填 k_1（漏掉 2F 那根彈簧也拉著 1F）——這一格錯，特徵值全錯。"""
    WD, HT = 1010, 486
    Lm, Rm, Tm, Bm = 176, 320, 74, 86
    xa, xb, ya, yb = -0.62, 1.62, -0.28, 2.34
    sx = min((WD - Lm - Rm) / (xb - xa), (HT - Tm - Bm) / (yb - ya))
    cv = Canvas(WD, HT, sx=sx, ox=Lm - xa * sx, oy=Bm - ya * sx, bg="#FFFFFF")

    cv.line((-0.62, 0), (1.62, 0), C["member"], 3.4)
    cv._hatch(cv.X(0.5), cv.Y(0.0), 1, 0, 0, 1, 0.95 * sx, C["member"], n=13)
    for xx in (0.0, 1.0):
        cv.line((xx, 0), (xx, 2), C["member"], 4.2, cap="butt")

    for i in range(2):
        y = i + 1
        cv.line((-0.10, y), (1.10, y), C["member"], 9, cap="butt")
        cv.rect_px(cv.X(0.28), cv.Y(y + 0.28), 0.44 * sx, 0.20 * sx,
                   "#DCE4EE", 6, C["member"], 2.2)
        cv.text_px(cv.X(0.50), cv.Y(y + 0.18), "%.0f kg" % M_KG, 13, C["text"],
                   weight="700")
        cv.text_px(cv.X(-0.10) - 12, cv.Y(y), ["1F", "2F"][i], 14, C["muted"], "end",
                   weight="700")
        cv.arrow((1.16, y), (1.48, y), C["deform"], 3.2, 11)
        cv.math((1.48, y), "u_{%d}" % (i + 1), 18, C["deform"], "start", dx=9, weight="700")
        # 層間勁度標在左側
        kk = [K1, K2][i]
        cv.text_px(cv.X(-0.34), cv.Y(y - 0.5), "k_{%d}" % (i + 1), 16, C["accent"],
                   weight="700")
        cv.text_px(cv.X(-0.34), cv.Y(y - 0.5) + 20, "%.0f" % kk, 11.5, C["accent"])
        cv.line((-0.34, y - 0.90), (-0.34, y - 0.70), C["accent"], 1.4, dash="4 3")
        cv.line((-0.34, y - 0.24), (-0.34, y - 0.10), C["accent"], 1.4, dash="4 3")

    cv.arrow((0.14, -0.19), (0.60, -0.19), C["load"], 3.4, 12)
    cv.math((0.84, -0.19), "ü_{g}(t)", 17, C["load"], "start", dx=4, weight="700")

    bx = WD - Rm + 10
    cv.rect_px(bx, 74, 296, 176, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 100, "K_{11} 為什麼是 k_{1} + k_{2}", 13.5, "#9A3412",
               "start", weight="700")
    for i, t in enumerate(["1F 被兩根彈簧夾住：",
                           "k_{1} 連到地面、k_{2} 連到 2F。",
                           "令 u_{1} = 1、u_{2} = 0，1F 需要",
                           "的力 = k_{1}·1 + k_{2}·1 = K_{11}。",
                           "2F 只有 k_{2} → K_{22} = k_{2}。"]):
        cv.text_px(bx + 14, 128 + i * 22, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 3 else "400")

    cv.rect_px(bx, 268, 296, 128, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 294, "本題的兩個矩陣", 13.5, "#1D4ED8", "start", weight="700")
    mat = [["%.0f" % K11, "%.0f" % K12], ["%.0f" % K12, "%.0f" % K22]]
    cv.text_px(bx + 16, 322, "[M] = diag( %.0f , %.0f )" % (M_KG, M_KG), 12.5,
               "#1D4ED8", "start")
    for i, row in enumerate(mat):
        yy = 348 + i * 22
        cv.text_px(bx + 30, yy, "[", 15, "#1D4ED8", "middle")
        for c, val in enumerate(row):
            cv.text_px(bx + 76 + c * 96, yy, val, 12.5, "#1D4ED8", "middle")
        cv.text_px(bx + 200, yy, "]", 15, "#1D4ED8", "middle")
    cv.text_px(bx + 216, 359, "N/m", 12, "#1D4ED8", "start")

    cv.text_px(WD / 2, HT - 32,
               "k_{1} 跨的是「地面 ↔ 1F」、k_{2} 跨的是「1F ↔ 2F」——"
               "把每根彈簧連到哪兩個自由度標出來，勁度矩陣就不會填錯。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


# ══════════════════════════════════════════════════════════
def fig2_modes():
    """兩個振態形狀與完整模態量鏈，並附有效質量驗算。
    攔錯：節點數（第 n 振態 n−1 個）；以及 Σ Γ_i² M_i* 必須恰等於總質量，
          若用四捨五入後的 r 代入，驗算就收斂不到 20000 kg，反而分不清是捨入還是算錯。"""
    PW, PH = 480, 400
    panels = []
    for j in range(2):
        cv = Canvas(PW, PH, sx=1, bg=None)
        cv.panel("模態 %d" % (j + 1),
                 "ω = %.4f rad/s　｜　f = %.4f Hz" % (WN[j], FN[j]))
        x0, ytop_, hgt, amp = 150, 98, 190, 60
        peak = max(1.0, abs(RS[j]))
        u = [0.0, 1.0 / peak * amp, RS[j] / peak * amp]
        ys = [ytop_ + hgt - i * hgt / 2 for i in range(3)]

        cv.parts.append(f'<line x1="{x0}" y1="{ys[0]:.1f}" x2="{x0}" y2="{ys[2]:.1f}" '
                        f'stroke="{C["ghost"]}" stroke-width="2.4" stroke-dasharray="6 5"/>')
        for i in range(3):
            cv.parts.append(f'<line x1="{x0 - 40}" y1="{ys[i]:.1f}" x2="{x0 + 40}" '
                            f'y2="{ys[i]:.1f}" stroke="{C["ghost"]}" stroke-width="1.6"/>')
            cv.text_px(x0 - 88, ys[i], ["G", "1F", "2F"][i], 12, C["muted"], "end")
        pts = " ".join(f"{x0 + u[i]:.1f},{ys[i]:.1f}" for i in range(3))
        cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{MODE_COL[j]}" '
                        f'stroke-width="4.2" stroke-linejoin="round"/>')
        for i in (1, 2):
            cv.parts.append(f'<circle cx="{x0 + u[i]:.1f}" cy="{ys[i]:.1f}" r="6" '
                            f'fill="{MODE_COL[j]}" stroke="#FFFFFF" stroke-width="2"/>')
            val = 1.0 if i == 1 else RS[j]
            cv.math_px(x0 + u[i], ys[i] - 19, "%.4f" % val, 12.5, MODE_COL[j],
                       "middle", weight="700")

        # 節點（零位移點）：由正負號變化線性內插算出
        nodes = 1 if u[1] * u[2] < 0 else 0
        if nodes:
            yn = ys[1] + (ys[2] - ys[1]) * abs(u[1]) / (abs(u[1]) + abs(u[2]))
            cv.parts.append(f'<circle cx="{x0:.1f}" cy="{yn:.1f}" r="7.5" fill="#FFFFFF" '
                            f'stroke="{C["accent"]}" stroke-width="3"/>')
        cv.text_px(x0, 340, "節點數 = %d（應為 n−1 = %d）✓" % (nodes, j), 12.5,
                   C["accent"], weight="700")

        rx = 256
        cv.rect_px(rx, 106, PW - rx - 20, 196, "#FFFFFF", 10, C["border"], 1.2)
        for i, t in enumerate(["λ_{%d} = ω^{2} = %.4f" % (j + 1, LAM[j]),
                               "r_{%d} = φ_{2}/φ_{1} = %.4f" % (j + 1, RS[j]),
                               "M*_{%d} = m(1+r^{2}) = %.0f kg" % (j + 1, MS[j]),
                               "K*_{%d} = λM* = %s N/m" % (j + 1, format(round(KS[j]), ",")),
                               "Γ_{%d} = m(1+r)/M* = %.4f" % (j + 1, GAM[j])]):
            cv.text_px(rx + 12, 134 + i * 33, t, 12, C["text"], "start")
        cv.rect_px(rx, 316, PW - rx - 20, 50, "#EEF4FF", 10, "#C7D9F5", 1.2)
        cv.text_px(rx + 12, 341, "Γ^{2}M* = %s kg" % format(round(GAM[j] ** 2 * MS[j]), ","),
                   13, "#1D4ED8", "start", weight="700")
        panels.append(cv)

    compose(panels, cols=2,
            title="兩個振態：模態量鏈與有效質量驗算",
            sub="振態向量取精確根 r = (5 ± √106)/9 = %.6f、%.6f" % (RS[0], RS[1]),
            note="有效質量合計 = %s kg，恰等於總質量，殘差為零；"
                 "若改用四捨五入的 r 會得 20,022，就分不清是捨入還是算錯。"
                 % format(round(MEFF_SUM), ","),
            path=f"{OUT}/{TAG}-fig-2-modes.svg")
    return f"{OUT}/{TAG}-fig-2-modes.svg"


# ══════════════════════════════════════════════════════════
def fig3_rayleigh():
    """Rayleigh 阻尼曲線：兩控制點、第一振態落點、最小阻尼點。
    攔錯：(a) 用 Hz 直接代入（曲線會整條位移，ξ_1 完全不對）；
          (b) 以為最小點在兩控制頻率的幾何平均（只有 ξ 相等時才成立）。"""
    WD, HT = 1010, 600
    Lm, Rm, Tm, Bm = 100, 276, 100, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    FMIN, FMAX, ZMAX = 0.30, 6.0, 0.10      # 起點取 0.30 Hz：再低質量項就衝出圖框
    ax = Ax(cv, (FMIN, FMAX), (0.0, ZMAX), (0.0, 0.0, bw, bh))
    ax.frame([1, 2, 3, 4, 5, 6], [0, 0.02, 0.04, 0.06, 0.08, 0.10],
             xlabel="頻率 f  (Hz)", ylabel="阻尼比 ξ", xfmt="{:g}", yfmt="{:.2f}")

    fs = [FMIN + i * (FMAX - FMIN) / 800 for i in range(801)]
    clip = lambda v: min(v, ZMAX)           # 保險：任何曲線都不得超出圖框
    ax.curve(fs, [clip(ALPHA / (2 * (2 * math.pi * f))) for f in fs], C["load"], 2.2, dash="7 5")
    ax.curve(fs, [clip(BETA * (2 * math.pi * f) / 2) for f in fs], C["bmd"], 2.2, dash="7 5")
    ax.curve(fs, [clip(zeta(2 * math.pi * f)) for f in fs], C["deform"], 3.8)

    # 兩個控制點（題目給定）
    for f, z, dxx, dyy, anc in zip(F_REF, XI_REF, (11, 12), (-16, -32), ("start", "start")):
        ax.vline(f, 0.0, z, C["muted"], 1.4)
        txt = ("控制點 %g Hz，ξ = %.2f" % (f, z)) if f == F_REF[0] else \
              ("控制點 %g Hz\nξ = %.2f" % (f, z))
        ax.mark(f, z, txt, C["accent"], dx=dxx, dy=dyy, size=12.5, anchor=anc)

    # 第一振態落點
    ax.vline(FN[0], 0.0, XI1, C["deform"], 1.8)
    cv.dot(ax.P(FN[0], XI1), 5.8, fill=C["deform"], stroke="#FFFFFF", w=2.0)
    cv.line(ax.P(FN[0], XI1 + 0.004), ax.P(0.62, 0.086), C["deform"], 1.5, dash="4 4")
    ax.at(0.66, 0.092, "第一振態 f_{1} = %.4f Hz\nξ_{1} = %.5f（＞ 控制點的 3%%）"
          % (FN[0], XI1), C["deform"], size=12.5, anchor="start")
    # 第二振態（本題未問，僅標點供對照）
    cv.dot(ax.P(FN[1], zeta(WN[1])), 4.6, fill=C["muted"], stroke="#FFFFFF", w=1.8)

    # 最小點 vs 幾何平均
    ax.vline(F_MIN, 0.0, zeta(W_MIN), C["accent"], 1.6)
    cv.dot(ax.P(F_MIN, zeta(W_MIN)), 6.0, fill=C["accent"], stroke="#FFFFFF", w=2.0)
    ax.at(F_MIN, zeta(W_MIN), "最小 %.3f Hz" % F_MIN, C["accent"], dy=22, size=12.5)
    cv.line(ax.P(F_GEO, 0.0), ax.P(F_GEO, 0.056), C["muted"], 1.6, dash="3 4")
    ax.at(F_GEO, 0.060, "幾何平均 %.3f Hz（此處並非最小）" % F_GEO, C["muted"],
          dx=10, size=12, anchor="start")

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 96, 244, 158, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 122, "係數（必用角頻率）", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["ω = 2πf：%.4f、%.4f rad/s" % (W_REF[0], W_REF[1]),
                           "α = π/12 = %.5f  1/s" % ALPHA,
                           "β = 11/(1200π) = %.4e s" % BETA,
                           "若誤用 f 代 ω，α、β 會差",
                           "2π 倍，ξ_{1} 整個跑掉。"]):
        cv.text_px(bx + 14, 148 + i * 22, t, 12, "#1D4ED8", "start",
                   weight="700" if i == 3 else "400")

    cv.rect_px(bx, 272, 244, 150, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 298, "為什麼 ξ_{1} ＞ 3%", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["f_{1} = %.4f Hz ＜ 1 Hz，" % FN[0],
                           "落在曲線的左半支——",
                           "該區由 α/(2ω) 主導，",
                           "頻率越低阻尼比越高。",
                           "故 ξ_{1} = %.2f%% ＞ 3%%。" % (100 * XI1)]):
        cv.text_px(bx + 14, 324 + i * 21, t, 12, "#9A3412", "start",
                   weight="700" if i == 4 else "400")

    cv.legend(bx + 6, 448, [(C["deform"], "總阻尼比 ξ(ω)"),
                            (C["load"], "質量項 α/(2ω)"),
                            (C["bmd"], "剛度項 βω/2")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 32,
               "最小阻尼點落在 %.3f Hz，而不是兩控制頻率的幾何平均 %.3f Hz——"
               "幾何平均只在兩控制點 ξ 相等時才成立。" % (F_MIN, F_GEO), 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-rayleigh.svg")


if __name__ == "__main__":
    print(f"特徵方程 λ² − {LAM_SUM:.0f}λ + {LAM_PROD:.0f} = 0")
    for j in range(2):
        print(f"  模態{j+1}: λ={LAM[j]:.5f}  ω={WN[j]:.5f}  f={FN[j]:.5f}  r={RS[j]:.6f}  "
              f"M*={MS[j]:.1f}  K*={KS[j]:.0f}  Γ={GAM[j]:.5f}")
    print(f"ΣΓ²M* = {MEFF_SUM:.4f} kg（應 = {2*M_KG:.0f}）")
    print(f"α = {ALPHA:.6f}（π/12 = {math.pi/12:.6f}）  β = {BETA:.8f}"
          f"（11/1200π = {11/(1200*math.pi):.8f}）")
    print(f"驗算 ξ(1Hz) = {zeta(W_REF[0]):.6f}  ξ(5Hz) = {zeta(W_REF[1]):.6f}")
    print(f"ξ_1 = {XI1:.6f}   ξ_2 = {zeta(WN[1]):.6f}")
    print(f"f_min = {F_MIN:.4f} Hz   幾何平均 = {F_GEO:.4f} Hz")
    for f in (fig1_frame(), fig2_modes(), fig3_rayleigh()):
        print(f)
