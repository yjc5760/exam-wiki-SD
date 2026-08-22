#!/usr/bin/env python3
"""
SD-2021-2 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2021-2.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2021-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2021-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定
W0   = 10.0          # ω_0 自然角頻率（rad/s）
X1CM = 2.4           # ω̄ = 0.1 rad/s（準靜態）之穩態位移（cm）
X2CM = 20.0          # ω̄ = 10  rad/s（共振）之穩態位移（cm）
MASS = 1.0e4         # m（kg）
P0   = 1.0e5         # p_0 = 10^2 kN（N）
TD   = 0.1           # t_d 載重持續時間（s）

# §4(一) 準靜態 → 共振：ξ 由兩個振幅之比反推（是算式，不是抄數字）
XI   = X1CM / (2 * X2CM)                     # = 2.4/(2×20) = 0.06

# §4(二) Step 1、2
K    = MASS * W0 ** 2                        # k = mω_0² = 1e6 N/m
T0   = 2 * math.pi / W0                      # T = 0.6283 s
XST  = P0 / K                                # x_st = 0.1 m
OMG  = math.pi / TD                          # Ω = π/t_d = 10π rad/s（不是 1/t_d）
R    = OMG / W0                              # r = π
GAM  = TD / T0                               # t_d/T = 0.1592


def x_forced(t):
    """§4(二) Step 4：強迫相（無阻尼，靜止起始）之封閉解 = Duhamel 積分結果"""
    return XST / (1 - R ** 2) * (math.sin(OMG * t) - R * math.sin(W0 * t))


def v_forced(t):
    return XST / (1 - R ** 2) * (OMG * math.cos(OMG * t) - R * W0 * math.cos(W0 * t))


XTD  = x_forced(TD)                          # §4(二) Step 4：x(t_d) = 0.02980 m
VTD  = v_forced(TD)                          # ẋ(t_d) = 0.5456 m/s
XMAX = math.hypot(XTD, VTD / W0)             # §4(二) Step 5：自由相振幅 = 0.06217 m
RD   = XMAX / XST                            # 動力放大 R_d = 0.622


def x_free(t):
    """§4(二) Step 5：自由振動相，以強迫相端點值為初始條件"""
    tau = t - TD
    return XTD * math.cos(W0 * tau) + (VTD / W0) * math.sin(W0 * tau)


def daf(r, xi):
    """穩態動力放大係數 D(r, ξ)"""
    return 1.0 / math.sqrt((1 - r ** 2) ** 2 + (2 * xi * r) ** 2)


def srs_halfsine(gamma, n=600):
    """半正弦脈衝之震動反應譜（無阻尼）：給 γ = t_d/T，回傳 (R_d, 最大值是否在自由相)。
    完全由數值積分／封閉解算出，不是查表描摹——這正是鐵則 2。"""
    w0, T = 2 * math.pi, 1.0
    td = gamma * T
    om = math.pi / td
    r = om / w0                       # = 1/(2γ)
    if abs(1 - r * r) < 1e-9:         # r → 1 之極限式
        def xx(t): return 0.5 * (math.sin(w0 * t) - w0 * t * math.cos(w0 * t))
        def vv(t): return 0.5 * w0 * w0 * t * math.sin(w0 * t)
    else:
        def xx(t): return (math.sin(om * t) - r * math.sin(w0 * t)) / (1 - r * r)
        def vv(t): return (om * math.cos(om * t) - r * w0 * math.cos(w0 * t)) / (1 - r * r)
    peak_f = max(abs(xx(td * i / n)) for i in range(n + 1))
    peak_r = math.hypot(xx(td), vv(td) / w0)
    return (max(peak_f, peak_r), peak_r >= peak_f)


# 注意：含中文的字串一律用 text_px（FONT 有 CJK fallback）；
#      math_px 的襯線數學字型沒有中文字，中文會整個消失。


# ══════════════════════════════════════════════════════════
def fig1_daf():
    """穩態動力放大係數 D(r)：把「準靜態」與「共振」兩個讀值放在同一條曲線上。
    攔錯：r_1 = 0.01 也去套完整公式（其實 D ≈ 1，直接讀靜位移）；r = 1 時誤用一般式。"""
    WD, HT = 1010, 592
    Lm, Rm, Tm, Bm = 96, 268, 96, 100
    bw, bh = 1.0, 0.60
    sx = min((WD - Lm - Rm) / bw, (HT - Tm - Bm) / bh)
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 3.0), (0.0, 10.0), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 2, 4, 6, 8, 10],
             xlabel="r = ω̄/ω_{0}", ylabel="D", xfmt="{:g}")

    rs = [i * 3.0 / 600 for i in range(601)]
    for xi, col, w, dash in ((0.02, C["muted"], 1.8, "6 5"),
                             (0.20, C["bmd"], 1.8, "6 5"),
                             (XI, C["deform"], 3.8, None)):
        ax.curve(rs, [min(daf(r, xi), 10.0) for r in rs], col, w, dash=dash)

    # 兩個題目讀值
    ax.vline(1.0, 0.0, daf(1.0, XI), C["load"], 1.5)
    ax.hline(daf(1.0, XI), 0.0, 1.0, C["load"], 1.5)
    ax.mark(1.0, daf(1.0, XI), "D = 1/(2ξ) = %.2f" % daf(1.0, XI), C["load"], dx=14, dy=-6)
    ax.mark(0.01, daf(0.01, XI), "D ≈ 1", C["accent"], dx=12, dy=-16)

    ax.at(0.30, 0.62, "準靜態區（D 為平台）", C["accent"], size=13, anchor="start")
    ax.at(1.0, 0.30, "共振", C["load"], size=13)

    bx = Lm + int(bw * sx) + 26
    cv.rect_px(bx, 92, 232, 178, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 118, "兩個讀值就夠解出 ξ", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["r_{1} = 0.1/10 = 0.01 → D ≈ 1",
                           "∴ p_{0}/k = X_{1} = 2.4 cm",
                           "r_{2} = 10/10 = 1 → D = 1/(2ξ)",
                           "X_{2}/X_{1} = 20/2.4 = %.3f" % (X2CM / X1CM),
                           "ξ = 2.4/(2×20) = %.2f" % XI]):
        cv.text_px(bx + 16, 146 + i * 26, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i == 4 else "400")

    cv.rect_px(bx, 288, 232, 128, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 314, "為什麼不必解聯立", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["兩個未知數 p_{0}/k 與 ξ，",
                           "但 r_{1} 落在 D ≈ 1 的平台上，",
                           "第一式直接把 p_{0}/k 讀出來，",
                           "第二式只剩 ξ 一個未知數。"]):
        cv.text_px(bx + 16, 340 + i * 22, t, 12.5, "#9A3412", "start")

    cv.legend(bx + 6, 442, [(C["deform"], "ξ = %.2f（本題）" % XI),
                            (C["muted"], "ξ = 0.02"),
                            (C["bmd"], "ξ = 0.20")], size=12.5, gap=23)
    cv.text_px(bx + 6, 516, "ξ = 0.02 之尖峰已被切至 D = 10", 12, C["muted"], "start")

    cv.text_px(WD / 2, HT - 32,
               "低頻端 D 是一段平台、共振點 D 只由阻尼決定——這兩件事讓題目給的兩個振幅剛好夠用。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-daf.svg")


# ══════════════════════════════════════════════════════════
def fig2_pulse():
    """半正弦脈衝的載重圖與位移時程（強迫相 ＋ 自由相）。
    攔錯：以為最大位移一定發生在載重作用期間。"""
    PW, PH = 980, 292
    Lm, Rm, Tm, Bm = 100, 74, 74, 62
    TEND = 0.72
    bw = 1.0
    sx = (PW - Lm - Rm) / bw
    bh = (PH - Tm - Bm) / sx                 # 直接指定繪圖區高度，不受等向縮放牽制

    # ── 上格：載重 ──
    top = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    top.panel("載重 p(t)", None)
    axp = Ax(top, (0.0, TEND), (0.0, 118.0), (0.0, 0.0, bw, bh))
    axp.frame([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], [0, 50, 100],
              xlabel="", ylabel="p  (kN)", xfmt="{:g}")
    ts = [TD * i / 200 for i in range(201)]
    ps = [P0 / 1e3 * math.sin(math.pi * t / TD) for t in ts]
    axp.area(ts, ps, C["fill_t"])
    axp.curve(ts, ps, C["load"], 3.0)
    axp.curve([TD, TEND], [0.0, 0.0], C["load"], 3.0)
    axp.vline(TD, 0.0, 118.0, C["muted"], 1.4)
    axp.at(TD / 2, P0 / 1e3, "p_{0} = 100 kN", C["load"], dy=-14)
    axp.at(TD, 112.0, "t_{d} = %.1f s" % TD, C["muted"], dx=9, dy=0, anchor="start")
    axp.at(0.44, 62.0, "p(t) = p_{0} sin(πt/t_{d})", C["load"], size=15)
    axp.at(0.44, 30.0, "Ω = π/t_{d} = 10π rad/s   (不是 1/t_{d})", C["load"], size=13.5)

    # ── 下格：位移 ──
    bot = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    bot.panel("位移 x(t)", None)
    axx = Ax(bot, (0.0, TEND), (-8.4, 8.4), (0.0, 0.0, bw, bh))
    axx.frame([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], [-8, -4, 0, 4, 8],
              xlabel="t  (s)", ylabel="x  (cm)", xfmt="{:g}")
    axx.hline(0.0, 0.0, TEND, C["muted"], 1.6, dash=None)

    tf = [TD * i / 200 for i in range(201)]
    axx.curve(tf, [100 * x_forced(t) for t in tf], C["deform"], 3.8)
    tv = [TD + (TEND - TD) * i / 400 for i in range(401)]
    axx.curve(tv, [100 * x_free(t) for t in tv], C["deform"], 3.8, dash="9 5")
    axx.hline(100 * XMAX, TD, TEND, C["accent"], 1.5)
    axx.hline(-100 * XMAX, TD, TEND, C["accent"], 1.5)
    axx.vline(TD, -8.4, 8.4, C["muted"], 1.4)

    axx.mark(TD, 100 * XTD, "x(t_{d}) = %.2f cm" % (100 * XTD), C["deform"],
             dx=-11, dy=-15, anchor="end")
    phi = math.atan2(XTD, VTD / W0)          # 自由相第一個波峰：由相位角算出，非目測
    t_pk = TD + (math.pi / 2 - phi) / W0
    axx.mark(t_pk, 100 * XMAX, "x_{max} = %.2f cm" % (100 * XMAX), C["accent"], dx=13, dy=-13)

    axx.at(0.048, -7.2, "強迫相", C["muted"], size=13)
    axx.at(0.55, 7.3, "自由振動相（載重已結束）", C["muted"], size=13)

    # compose() 的 title/sub/note 走 esc()，不解析上下標，故此處用純文字寫法
    compose([top, bot], cols=1,
            title="半正弦脈衝：載重結束後才出現最大位移",
            sub="t_d/T = %.3f ＜ 0.5，故最大值落在自由振動相；R_d = x_max/x_st = %.3f" % (GAM, RD),
            note="強迫相在 t_d 之前沒有極值，端點值 %.2f cm 只是自由相的初始條件；"
                 "真正的最大值 %.2f cm 由 x(t_d) 與速度 v(t_d) 合成。" % (100 * XTD, 100 * XMAX),
            path=f"{OUT}/{TAG}-fig-2-pulse.svg")
    return f"{OUT}/{TAG}-fig-2-pulse.svg"


# ══════════════════════════════════════════════════════════
def fig3_srs():
    """半正弦脈衝震動反應譜 R_d(t_d/T)：三個最常記錯的點一次標清楚。
    攔錯：以為 R_d ＜ 1 的門檻在 0.4、尖峰在 0.5、長持續時間趨近 2。"""
    WD, HT = 1010, 596
    Lm, Rm, Tm, Bm = 96, 250, 100, 100
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 3.0), (0.0, 2.0), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 0.5, 1.0, 1.5, 2.0],
             xlabel="t_{d}/T", ylabel="R_{d} = x_{max}/x_{st}", xfmt="{:g}", yfmt="{:.1f}")

    gs = [0.02 + i * (3.0 - 0.02) / 500 for i in range(501)]
    rd = [srs_halfsine(g)[0] for g in gs]
    ax.area(gs, rd, C["fill_c"])
    ax.curve(gs, rd, C["deform"], 3.6)
    ax.hline(1.0, 0.0, 3.0, C["muted"], 1.4)

    # 三個關鍵座標全部由 srs_halfsine() 掃描算出，不是查表抄的
    g_peak = max(gs, key=lambda g: srs_halfsine(g)[0])
    rd_peak = srs_halfsine(g_peak)[0]
    g_one = min((g for g in gs if srs_halfsine(g)[0] >= 1.0), default=0.0)
    g_switch = min((g for g in gs if not srs_halfsine(g)[1]), default=0.0)

    for g, txt, col, dx, dy, an in (
            (GAM,      "本題 t_d/T = %.3f\nR_d = %.3f" % (GAM, RD), C["load"],   -11, -30, "end"),
            (g_one,    "R_d = 1 的分界\nt_d/T = %.2f" % g_one,      C["accent"],  14,   24, "start"),
            (g_peak,   "全域尖峰\nR_d = %.3f  (t_d/T = %.2f)" % (rd_peak, g_peak),
                                                                    C["bmd"],     13,  -30, "start"),
            (g_switch, "最大值由自由相\n移交強迫相 %.2f" % g_switch, C["muted"],  -13, -44, "end")):
        y = srs_halfsine(g)[0]
        ax.vline(g, 0.0, y, C["muted"], 1.3)
        ax.mark(g, y, txt, col, dx=dx, dy=dy, anchor=an, size=13)

    ax.at(2.15, 1.62, "長持續時間 → 準靜態，R_d → 1", C["muted"], size=13)

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 96, 214, 216, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 122, "三個常被記錯的點", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["R_{d} ＜ 1 的門檻是 %.2f，" % g_one,
                           "不是 0.4。",
                           "尖峰 %.2f 出現在 %.2f，" % (rd_peak, g_peak),
                           "不是 0.5（那裡是 π/2）。",
                           "t_{d}/T ≫ 1 時 R_{d} → 1，",
                           "不是 2——那是突加定值",
                           "載重（step load）的結果。"]):
        cv.text_px(bx + 16, 150 + i * 22, t, 12.5, "#9A3412", "start")

    cv.rect_px(bx, 330, 214, 96, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 356, "本題落在放大 ＜ 1 區", 13, "#1D4ED8", "start", weight="700")
    cv.text_px(bx + 16, 382, "x_{max} = %.3f × 10 cm" % RD, 12.5, "#1D4ED8", "start")
    cv.text_px(bx + 16, 405, "     = %.2f cm" % (100 * XMAX), 12.5, "#1D4ED8",
               "start", weight="700")

    cv.text_px(WD / 2, HT - 32,
               "整條曲線由本腳本的 SRS 函式逐點算出：若把尖峰記成 0.5，圖上尖峰的位置立刻對不上。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-srs.svg")


if __name__ == "__main__":
    print(f"ξ = {XI}  k = {K:.3g} N/m  T = {T0:.4f} s  x_st = {XST} m  r = {R:.4f}  "
          f"t_d/T = {GAM:.4f}")
    print(f"x(t_d) = {XTD:.5f} m   ẋ(t_d) = {VTD:.5f} m/s   x_max = {XMAX:.5f} m   R_d = {RD:.4f}")
    for g in (0.10, 0.159, 0.28, 0.40, 0.50, 0.75, 0.81, 1.00, 2.00):
        r, freephase = srs_halfsine(g)
        print(f"  t_d/T = {g:5.3f} → R_d = {r:.4f}  ({'自由相' if freephase else '強迫相'})")
    for f in (fig1_daf(), fig2_pulse(), fig3_srs()):
        print(f)
