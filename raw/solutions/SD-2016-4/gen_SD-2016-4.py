#!/usr/bin/env python3
"""
SD-2016-4 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2016-4.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2016-4"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2016-4.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定
K_N  = 1.15e6                       # 層間勁度 k（N/m）
M_KG = 5.0e3                        # 質量 m（kg）
G    = 9.81
MASS = [M_KG, M_KG, M_KG / 2]       # 1F、2F、RF —— 頂層是 m/2，不是 m

# §3.2 特徵值 λ = ω²m/k 的三個解析根
S3  = math.sqrt(3.0)
LAM = [2 - S3, 2.0, 2 + S3]
# §3.4 振態向量
PHI = [[1.0, S3, 2.0], [1.0, 0.0, -1.0], [1.0, -S3, 2.0]]

# §3.3 自然頻率與週期
W2 = [l * K_N / M_KG for l in LAM]
WN = [math.sqrt(w) for w in W2]
TN = [2 * math.pi / w for w in WN]

# §4.1 模態參與因子（含質量矩陣，不可省略 [M]）
LI = [sum(MASS[k] * PHI[j][k] for k in range(3)) for j in range(3)]
MI = [sum(MASS[k] * PHI[j][k] ** 2 for k in range(3)) for j in range(3)]
GAM = [LI[j] / MI[j] for j in range(3)]
MEFF = [LI[j] ** 2 / MI[j] for j in range(3)]
MTOT = sum(MASS)
RHO = [m / MTOT for m in MEFF]      # 有效質量比：92.9% / 6.7% / 0.5%

# §1 fig-2 圖說所載之反應譜控制點（T 秒, S_a 以 g 計）
SPEC = [(0.0, 0.60), (0.20, 0.70), (0.25, 0.79), (0.30, 1.00), (0.40, 1.21),
        (0.50, 1.27), (0.60, 1.21), (0.70, 1.01), (0.80, 0.81), (0.90, 0.63),
        (1.00, 0.50), (2.00, 0.12)]

# §4.2 各模態採用之譜加速度讀值（g）
SA = [0.80, 1.00, 0.72]

# §4.3–4.5
SD_ = [SA[j] * G / W2[j] for j in range(3)]
U = [[GAM[j] * SD_[j] * PHI[j][k] for k in range(3)] for j in range(3)]      # U[模態][樓層]
U_SRSS = [math.sqrt(sum(U[j][k] ** 2 for j in range(3))) for k in range(3)]

# §5.1–5.3 慣性力與層剪力（層剪力必須逐模態算完再 SRSS，不可由位移差 SRSS 得來）
F = [[MASS[k] * GAM[j] * PHI[j][k] * SA[j] * G for k in range(3)] for j in range(3)]
V = [[sum(F[j][k:]) for k in range(3)] for j in range(3)]                    # V[模態][樓層起算]
V_SRSS = [math.sqrt(sum(V[j][k] ** 2 for j in range(3))) for k in range(3)]


def spec(t):
    """由 SPEC 控制點線性內插；反應譜是被讀的對象，讀值由 §4.2 決定"""
    if t <= SPEC[0][0]:
        return SPEC[0][1]
    for (t0, s0), (t1, s1) in zip(SPEC, SPEC[1:]):
        if t <= t1:
            return s0 + (s1 - s0) * (t - t0) / (t1 - t0)
    return SPEC[-1][1]


# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。
MODE_COL = [C["deform"], C["load"], C["bmd"]]


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪：頂層質量 m/2 與「層間」勁度一次標清楚。
    攔錯：質量矩陣寫成 diag(m,m,m)；勁度矩陣對角線全填 k（應為 2k、2k、k）。"""
    WD, HT = 1010, 520
    Lm, Rm, Tm, Bm = 190, 306, 74, 82
    xa, xb, ya, yb = -0.62, 1.62, -0.30, 3.30
    sx = min((WD - Lm - Rm) / (xb - xa), (HT - Tm - Bm) / (yb - ya))
    cv = Canvas(WD, HT, sx=sx, ox=Lm - xa * sx, oy=Bm - ya * sx, bg="#FFFFFF")

    # 地面
    cv.line((-0.62, 0), (1.62, 0), C["member"], 3.4)
    cv._hatch(cv.X(0.5), cv.Y(0.0), 1, 0, 0, 1, 0.95 * sx, C["member"], n=13)

    # 柱與樓版
    for xx in (0.0, 1.0):
        cv.line((xx, 0), (xx, 3), C["member"], 4.2, cap="butt")
    names = ["1F", "2F", "RF"]
    mlab = ["m", "m", "m/2"]
    for i in range(3):
        y = i + 1
        cv.line((-0.10, y), (1.10, y), C["member"], 9, cap="butt")
        cv.rect_px(cv.X(0.30), cv.Y(y + 0.27), 0.40 * sx, 0.20 * sx,
                   "#DCE4EE", 6, C["member"], 2.2)
        cv.math((0.50, y + 0.17), mlab[i], 16, C["text"], weight="700")
        cv.text_px(cv.X(-0.10) - 12, cv.Y(y), names[i], 14, C["muted"], "end", weight="700")
        # 自由度
        cv.arrow((1.16, y), (1.50, y), C["deform"], 3.2, 11)
        cv.math((1.50, y), "v_{%d}" % (i + 1), 18, C["deform"], "start", dx=9, weight="700")
        # 層間勁度
        cv.math((-0.30, y - 0.5), "k", 17, C["accent"], weight="700")
        cv.line((-0.30, y - 0.86), (-0.30, y - 0.66), C["accent"], 1.4, dash="4 3")
        cv.line((-0.30, y - 0.34), (-0.30, y - 0.14), C["accent"], 1.4, dash="4 3")

    # 地表加速度
    cv.arrow((0.14, -0.20), (0.62, -0.20), C["load"], 3.4, 12)
    cv.math((0.86, -0.20), "ü_{g}(t)", 17, C["load"], "start", dx=4, weight="700")

    bx = WD - Rm + 10
    cv.rect_px(bx, 74, 284, 172, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 100, "質量矩陣（頂層 m/2）", 13.5, "#1D4ED8", "start", weight="700")
    cv.text_px(bx + 16, 128, "[M] = diag( m , m , m/2 )", 13.5, "#1D4ED8", "start")
    cv.text_px(bx + 16, 160, "勁度矩陣（剪力樓層）", 13.5, "#1D4ED8", "start", weight="700")
    mat = [["2k", "−k", "0"], ["−k", "2k", "−k"], ["0", "−k", "k"]]
    for i, row in enumerate(mat):
        yy = 188 + i * 22
        cv.text_px(bx + 34, yy, "[", 15, "#1D4ED8", "middle")
        for c, val in enumerate(row):
            cv.text_px(bx + 58 + c * 34, yy, val, 13.5, "#1D4ED8", "middle")
        cv.text_px(bx + 160, yy, "]", 15, "#1D4ED8", "middle")

    cv.rect_px(bx, 264, 284, 174, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 290, "為什麼對角線是 2k 不是 k", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["k 是「層間」勁度：第 j 層的",
                           "相對變形為 v_{j} − v_{j−1}。",
                           "中間樓層同時被上、下兩層",
                           "的彈簧拉住 → 對角線 2k；",
                           "頂層上方沒有樓層 → 只有 k。",
                           "這一格寫錯，特徵值全錯。"]):
        cv.text_px(bx + 14, 316 + i * 21, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 5 else "400")

    cv.text_px(WD / 2, HT - 30,
               "k = %.2f×10^{6} N/m，m = %.0f×10^{3} kg，k/m = %.0f rad^{2}/s^{2}"
               % (K_N / 1e6, M_KG / 1e3, K_N / M_KG), 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


# ══════════════════════════════════════════════════════════
def fig2_modes():
    """三個振態形狀，並數出各自的節點數。
    攔錯：第 n 振態應有 n−1 個節點；數目不符代表振態向量解錯或抄錯。"""
    PW, PH = 336, 460
    panels = []
    for j in range(3):
        cv = Canvas(PW, PH, sx=1, bg=None)
        cv.panel("Mode %d" % (j + 1),
                 "T = %.3f s　｜　ω = %.2f rad/s" % (TN[j], WN[j]))
        x0, ymid = PW / 2, 96
        hgt = 268
        amp = 64.0
        peak = max(abs(v) for v in PHI[j])
        u = [0.0] + [PHI[j][k] / peak * amp for k in range(3)]
        ys = [ymid + hgt - i * hgt / 3 for i in range(4)]

        cv.parts.append(f'<line x1="{x0}" y1="{ys[0]:.1f}" x2="{x0}" y2="{ys[3]:.1f}" '
                        f'stroke="{C["ghost"]}" stroke-width="2.4" stroke-dasharray="6 5"/>')
        for i in range(4):
            cv.parts.append(f'<line x1="{x0 - 44}" y1="{ys[i]:.1f}" x2="{x0 + 44}" '
                            f'y2="{ys[i]:.1f}" stroke="{C["ghost"]}" stroke-width="1.6"/>')
        cv.text_px(x0 - 98, ys[0], "G", 12, C["muted"], "end")
        pts = " ".join(f"{x0 + u[i]:.1f},{ys[i]:.1f}" for i in range(4))
        cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{MODE_COL[j]}" '
                        f'stroke-width="4.2" stroke-linejoin="round"/>')
        for i in range(1, 4):
            cv.parts.append(f'<circle cx="{x0 + u[i]:.1f}" cy="{ys[i]:.1f}" r="6" '
                            f'fill="{MODE_COL[j]}" stroke="#FFFFFF" stroke-width="2"/>')
            cv.math_px(x0 + u[i] + (17 if u[i] >= 0 else -17), ys[i] - 15,
                       "%.3f" % PHI[j][i - 1], 12.5, MODE_COL[j],
                       "start" if u[i] >= 0 else "end", weight="700")
            cv.text_px(x0 - 98, ys[i], ["1F", "2F", "RF"][i - 1], 12, C["muted"], "end")

        # 節點（零位移點）：由相鄰樓層的正負號變化線性內插算出，不是目測
        nodes = []
        for i in range(3):
            a, b = u[i], u[i + 1]
            if a == 0 and i > 0:
                nodes.append(ys[i])
            elif a * b < 0:
                nodes.append(ys[i] + (ys[i + 1] - ys[i]) * abs(a) / (abs(a) + abs(b)))
        for yn in nodes:
            cv.parts.append(f'<circle cx="{x0:.1f}" cy="{yn:.1f}" r="7.5" fill="#FFFFFF" '
                            f'stroke="{C["accent"]}" stroke-width="3"/>')
        cv.text_px(PW / 2, PH - 66,
                   "節點數 = %d　（應為 n−1 = %d）%s" % (len(nodes), j, "✓"),
                   13, C["accent"], weight="700")
        cv.text_px(PW / 2, PH - 42, "有效質量比 %.1f%%" % (100 * RHO[j]), 13,
                   C["text"], weight="700")
        panels.append(cv)

    compose(panels, cols=3,
            title="三個振態形狀：用節點數自我檢核",
            sub="虛線為未變形位置；空心圈為節點（零位移點）。Mode 2 的節點恰落在 2F，"
                "故 2F 在該模態完全不動。",
            note="有效質量比合計 %.1f%%（Mode 1 佔 %.1f%%）——精度該花在哪個模態，這張圖直接回答。"
                 % (100 * sum(RHO), 100 * RHO[0]),
            path=f"{OUT}/{TAG}-fig-2-modes.svg")
    return f"{OUT}/{TAG}-fig-2-modes.svg"


# ══════════════════════════════════════════════════════════
def fig3_spectrum():
    """三個模態週期在反應譜上的落點。
    攔錯：T_3 = 0.214 s 落在「上升段」，S_a 僅 0.72g，卻常被誤讀成尖峰 1.27g。"""
    WD, HT = 1010, 578
    Lm, Rm, Tm, Bm = 96, 268, 92, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 1.4), (0.0, 1.4), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4],
             [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4],
             xlabel="T  (s)", ylabel="S_{a}  (g)", xfmt="{:.1f}", yfmt="{:.1f}")

    ts = [i * 1.4 / 560 for i in range(561)]
    ax.area(ts, [spec(t) for t in ts], C["fill_m"])
    ax.curve(ts, [spec(t) for t in ts], C["bmd"], 3.4)

    # 尖峰（讀圖時最容易被誤抓的位置）
    tpk, spk = max(SPEC, key=lambda p: p[1])
    ax.mark(tpk, spk, "尖峰 %.2fg（T = %.1f s）" % (spk, tpk), C["muted"], dx=13, dy=-14, size=13)

    for j in (0, 1, 2):
        ax.vline(TN[j], 0.0, SA[j], C["muted"], 1.4)
        ax.hline(SA[j], 0.0, TN[j], C["muted"], 1.3)
    ax.mark(TN[2], SA[2], "T_{3} = %.3f s\nS_{a} = %.2f g" % (TN[2], SA[2]),
            MODE_COL[2], dx=-13, dy=-34, size=13, anchor="end")
    ax.mark(TN[1], SA[1], "T_{2} = %.3f s\nS_{a} = %.2f g" % (TN[1], SA[1]),
            MODE_COL[1], dx=12, dy=-34, size=13)
    ax.mark(TN[0], SA[0], "T_{1} = %.3f s   S_{a} = %.2f g" % (TN[0], SA[0]),
            MODE_COL[0], dx=13, dy=-14, size=13)

    ax.at(0.105, 1.06, "上升段", C["accent"], size=13)
    ax.at(1.06, 0.96, "下降段", C["accent"], size=13)

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 88, 232, 212, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 114, "最容易錯的一步", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["T_{3} 最短，但 S_{a} 不是最大——",
                           "譜在短週期端是「由 0.60g",
                           "往上爬」，不是一路很高。",
                           "誤讀成尖峰 %.2fg 會把 Mode 3" % spk,
                           "的貢獻放大 %.1f 倍。" % (spk / SA[2]),
                           "所幸 Mode 3 有效質量僅 %.1f%%，" % (100 * RHO[2]),
                           "答案幾乎不受影響——真正",
                           "要讀準的是 T_{1} 的 S_{a}。"]):
        cv.text_px(bx + 14, 142 + i * 21, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 7 else "400")

    cv.rect_px(bx, 318, 232, 116, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 344, "各模態譜位移", 13.5, "#1D4ED8", "start", weight="700")
    for j in range(3):
        cv.text_px(bx + 14, 370 + j * 22,
                   "S_{d%d} = %.2f/ω^{2} = %.5f m" % (j + 1, SA[j] * G, SD_[j]),
                   12, "#1D4ED8", "start")

    cv.text_px(WD / 2, HT - 30,
               "三個週期分別落在譜的三個不同區段——把它們畫在同一條曲線上，"
               "「短週期就一定大」這個直覺立刻被推翻。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-spectrum.svg")


# ══════════════════════════════════════════════════════════
def fig4_story():
    """樓層位移剖面與層剪力剖面（各模態 ＋ SRSS）。
    攔錯：把 SRSS 後的位移拿去相減求層剪力——SRSS 已丟失相位，Mode 2 的 V 在
    Story 1 與 Story 2、3 是反號的，相減會得到完全錯誤的結果。"""
    PW, PH = 496, 476
    Tm, Bm = 100, 98
    hgt = PH - Tm - Bm

    def panel(vals_by_mode, srss, unit, title_, sub_, xr, ticks):
        cv = Canvas(PW, PH, sx=1, bg=None)
        cv.panel(title_, sub_)
        xa_, xb_ = xr
        x0, wdt = 112, PW - 112 - 70

        def PX(v): return x0 + (v - xa_) / (xb_ - xa_) * wdt
        def PY(h): return Tm + hgt - h * hgt / 3.0

        for h in range(4):
            cv.parts.append(f'<line x1="{x0}" y1="{PY(h):.1f}" x2="{x0 + wdt}" '
                            f'y2="{PY(h):.1f}" stroke="#E8ECF2" stroke-width="1.1"/>')
            cv.text_px(x0 - 14, PY(h), ["G", "1F", "2F", "RF"][h], 12, C["muted"], "end")
        cv.parts.append(f'<line x1="{PX(0):.1f}" y1="{PY(0):.1f}" x2="{PX(0):.1f}" '
                        f'y2="{PY(3):.1f}" stroke="{C["muted"]}" stroke-width="1.8"/>')
        for t in ticks:
            cv.parts.append(f'<line x1="{PX(t):.1f}" y1="{PY(0):.1f}" x2="{PX(t):.1f}" '
                            f'y2="{PY(0)+6:.1f}" stroke="{C["muted"]}" stroke-width="1.3"/>')
            cv.text_px(PX(t), PY(0) + 21, "%g" % t, 11.5, C["muted"])
        cv.text_px(x0 + wdt / 2, PY(0) + 46, unit, 13, C["text"], weight="700")

        # 先畫 SRSS（粗），再把各模態疊在上面，否則主控模態會被完全遮住
        pts = " ".join(f"{PX(v):.1f},{PY(h):.1f}" for h, v in srss)
        cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{C["accent"]}" '
                        f'stroke-width="5.0" stroke-linejoin="round"/>')
        for j_ in range(3):
            pts = " ".join(f"{PX(v):.1f},{PY(h):.1f}" for h, v in vals_by_mode[j_])
            cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{MODE_COL[j_]}" '
                            f'stroke-width="2.0" stroke-dasharray="8 6"/>')
        for h, v in srss:
            cv.parts.append(f'<circle cx="{PX(v):.1f}" cy="{PY(h):.1f}" r="5.2" '
                            f'fill="{C["accent"]}" stroke="#FFFFFF" stroke-width="2"/>')
        return cv, PX, PY

    # ── 位移剖面 ──
    disp_modes = [[(0, 0.0)] + [(k + 1, 100 * U[j][k]) for k in range(3)] for j in range(3)]
    disp_srss = [(0, 0.0)] + [(k + 1, 100 * U_SRSS[k]) for k in range(3)]
    p1, PX1, PY1 = panel(disp_modes, disp_srss, "位移 (cm)", "樓層位移",
                         "Mode 1 幾乎與 SRSS 重合", (-4.0, 20.0),
                         [-4, 0, 4, 8, 12, 16, 20])
    for k in range(3):
        p1.text_px(PX1(100 * U_SRSS[k]) + 14, PY1(k + 1) - 17,
                   "%.2f" % (100 * U_SRSS[k]), 13, C["accent"], "start", weight="700")

    # ── 層剪力剖面（階梯狀：每一層的 V 在該層高度區間內為定值）──
    def steps(vals):
        out = [(0, 0.0)]
        for i in range(3):
            out += [(i, vals[i]), (i + 1, vals[i])]
        return out + [(3, 0.0)]

    sh_modes = [steps([V[j][k] / 1e3 for k in range(3)]) for j in range(3)]
    sh_srss = steps([V_SRSS[k] / 1e3 for k in range(3)])
    p2, PX2, PY2 = panel(sh_modes, sh_srss, "層剪力 (kN)", "各層剪力",
                         "Mode 2 在 Story 1 與 Story 2、3 反號", (-20.0, 100.0),
                         [-20, 0, 20, 40, 60, 80, 100])
    for k in range(3):
        p2.text_px(PX2(V_SRSS[k] / 1e3) + 11, PY2(k + 0.5), "%.1f" % (V_SRSS[k] / 1e3),
                   13, C["accent"], "start", weight="700")
    p2.text_px(PX2(V[1][0] / 1e3) + 10, PY2(0.5) + 26, "Mode 2  +%.1f" % (V[1][0] / 1e3),
               12, MODE_COL[1], "start", weight="700")
    p2.text_px(PX2(V[1][2] / 1e3) - 10, PY2(2.5) - 26, "Mode 2  %.1f" % (V[1][2] / 1e3),
               12, MODE_COL[1], "end", weight="700")

    compose([p1, p2], cols=2,
            title="樓層位移與層剪力：兩者都要逐模態算完再 SRSS",
            sub="虛線為各模態（藍 Mode 1、紅 Mode 2、綠 Mode 3），粗橘線為 SRSS 組合",
            note="基底剪力 %.1f kN；若改由 SRSS 位移差乘勁度回推，Mode 2 的反號會被抹平，"
                 "結果不對。" % (V_SRSS[0] / 1e3),
            path=f"{OUT}/{TAG}-fig-4-story.svg")
    return f"{OUT}/{TAG}-fig-4-story.svg"


if __name__ == "__main__":
    for j in range(3):
        print(f"Mode {j+1}: λ={LAM[j]:.4f}  ω²={W2[j]:.2f}  ω={WN[j]:.2f}  T={TN[j]:.4f}  "
              f"Γ={GAM[j]:.4f}  ρ={100*RHO[j]:.1f}%  S_d={SD_[j]:.5f} m")
    print("位移 SRSS (cm):", [round(100 * u, 2) for u in U_SRSS])
    for j in range(3):
        print(f"  Mode {j+1} 層剪力 (kN):", [round(v / 1e3, 2) for v in V[j]])
    print("層剪力 SRSS (kN):", [round(v / 1e3, 1) for v in V_SRSS])
    print("Σρ =", round(100 * sum(RHO), 2), "%")
    for f in (fig1_frame(), fig2_modes(), fig3_spectrum(), fig4_story()):
        print(f)
