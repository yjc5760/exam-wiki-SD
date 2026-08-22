#!/usr/bin/env python3
"""
SD-2006-1 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2006-1.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2006-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2006-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# 子題(一) 為純符號題，圖上的具體數字僅為「示範參數」，
# 用來把符號解畫成看得見的曲線；改這幾個值，三張圖會全部跟著變。
W0 = 6.0           # ω_0（rad/s）示範值
XI = 0.12          # ξ 示範值（欠阻尼）
D0 = 2.0           # 初始位移 d
V0 = 1.5           # 初始速度 v
# 取 d 大、v 小的組合，是為了讓「漏掉 −ξω_0 項」的誤差（大小恰為 ξω_0·d）
# 在圖上一眼可辨；換成別組參數圖形會變，但結論不變。
MASS = 1.0         # m

WD_ = W0 * math.sqrt(1 - XI ** 2)          # §4 Step 1：ω_d = ω_0√(1−ξ²)
A_COEF = D0                                # §4 Step 4：A = d
B_COEF = (V0 + XI * W0 * D0) / WD_         # §4 Step 4：B = (v + ξω_0 d)/ω_d
# §4 Step 6：sin 項係數，關鍵在 ω_d² + ξ²ω_0² = ω_0²
SIN_COEF = (V0 * XI * W0 + D0 * W0 ** 2) / WD_


def x_h(t):
    """§4 Step 5：齊次解（自由振動）"""
    return math.exp(-XI * W0 * t) * (A_COEF * math.cos(WD_ * t) + B_COEF * math.sin(WD_ * t))


def v_h(t):
    """§4 Step 6：正確的速度歷時"""
    return math.exp(-XI * W0 * t) * (V0 * math.cos(WD_ * t) - SIN_COEF * math.sin(WD_ * t))


def v_h_wrong(t):
    """陷阱④：只微分三角函數、漏掉 e^{-ξω_0 t} 帶出的 −ξω_0 項"""
    return math.exp(-XI * W0 * t) * WD_ * (-A_COEF * math.sin(WD_ * t)
                                           + B_COEF * math.cos(WD_ * t))


def env(t):
    """包絡線 ±√(A²+B²)·e^{-ξω_0 t}"""
    return math.hypot(A_COEF, B_COEF) * math.exp(-XI * W0 * t)


def h_imp(tau, t):
    """L3：脈衝反應函數 h(t−τ) = e^{-ξω_0(t−τ)}sin[ω_d(t−τ)]/(mω_d)"""
    s = t - tau
    return 0.0 if s < 0 else math.exp(-XI * W0 * s) * math.sin(WD_ * s) / (MASS * WD_)


def p_load(t):
    """示範外力 p(t)：一段任意波形，用來展示 Duhamel 是「切片＋疊加」"""
    return 0.0 if t < 0 else 6.0 * math.exp(-0.9 * t) * math.sin(2.2 * t) ** 2


def x_duhamel(t, n=900, tmax=None):
    """§4 Step 3：Duhamel 積分（梯形法數值積分）"""
    tm = t if tmax is None else min(t, tmax)
    if tm <= 0:
        return 0.0
    h = tm / n
    s = 0.5 * (p_load(0.0) * h_imp(0.0, t) + p_load(tm) * h_imp(tm, t))
    for i in range(1, n):
        tau = i * h
        s += p_load(tau) * h_imp(tau, t)
    return s * h


# 子題(二)：三種振動源（振幅量級與識別阻尼比區間，取自 §4 子題(二) 的表與內文）
SOURCES = [("微動",   1e-5, 1e-3, 0.01, 0.02, C["deform"]),
           ("激振器", 1e-3, 1e-1, 0.015, 0.035, C["bmd"]),
           ("地震",   1e-1, 1.0,  0.05, 0.10, C["load"])]

def _ticks(vmax, n=4):
    """由資料範圍算出對稱的整齊刻度（不寫死）"""
    raw = vmax / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min(s_ for s_ in (1, 2, 2.5, 5, 10) if s_ * mag >= raw) * mag
    k = int(vmax / step)
    return [round(step * i, 6) for i in range(-k, k + 1)]


# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。


# ══════════════════════════════════════════════════════════
def fig1_duhamel():
    """Duhamel 積分的物理內容：外力切成脈衝、每個脈衝各自產生衰減正弦、全部疊加。
    攔錯：把積分核當成 p(t) 本身；以及不知道為何微分時上限項會消失
          （h(0) = sin(0)/(mω_d) = 0，圖上最右端那條剛生成的響應振幅正好是零）。"""
    PW, PH = 960, 288
    Lm, Rm, Tm, Bm = 96, 60, 70, 96
    TMAX = 3.2
    T_NOW = 2.4
    bw = 1.0
    sx = (PW - Lm - Rm) / bw
    bh = (PH - Tm - Bm) / sx
    ts = [i * TMAX / 600 for i in range(601)]

    # ── 上格：外力 p(τ) 與被切出的幾個脈衝 ──
    top = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    top.panel("① 外力 p(τ) 切成一連串脈衝", None)
    a1 = Ax(top, (0.0, TMAX), (0.0, 6.6), (0.0, 0.0, bw, bh))
    a1.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 2, 4, 6], xlabel="", ylabel="p", xfmt="{:g}")
    a1.area(ts, [p_load(t) for t in ts], C["fill_t"])
    a1.curve(ts, [p_load(t) for t in ts], C["load"], 3.0)
    TAUS = [0.35, 0.85, 1.35, 1.85, T_NOW]
    for tau in TAUS:
        a1.vline(tau, 0.0, p_load(tau), C["accent"], 2.0, dash=None)
        top.dot(a1.P(tau, p_load(tau)), 5.0, fill=C["accent"], stroke="#FFFFFF", w=1.8)
    a1.at(TAUS[0], 6.9, "p(τ)dτ", C["accent"], size=12.5)

    # ── 下格：各脈衝的響應 h(t−τ) 與其疊加 ──
    # 每條虛線就是 p(τ_i)·Δτ·h(t−τ_i)，五條之和即為積分的粗略近似，
    # 與精確的 Duhamel 積分（實線）畫在一起，才看得出「疊加」是真的。
    DTAU = TAUS[1] - TAUS[0]
    contribs = [[p_load(tau) * DTAU * h_imp(tau, t) for t in ts] for tau in TAUS]
    approx = [sum(c[i] for c in contribs) for i in range(len(ts))]
    exact = [x_duhamel(t) for t in ts]
    ylim = max(max(abs(v) for v in exact),
               max(abs(v) for row in contribs for v in row)) * 1.35

    bot = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    bot.panel("② 每個脈衝的響應相加 = x_p(t)", None)
    a2 = Ax(bot, (0.0, TMAX), (-ylim, ylim), (0.0, 0.0, bw, bh))
    a2.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], _ticks(ylim),
             xlabel="t  (s)", ylabel="x", xfmt="{:g}", yfmt="{:g}")
    a2.hline(0.0, 0.0, TMAX, C["muted"], 1.6, dash=None)
    for c in contribs:
        a2.curve(ts, c, C["accent"], 1.6, dash="6 4")
    a2.curve(ts, approx, C["muted"], 2.2, dash="2 4")
    a2.curve(ts, exact, C["deform"], 3.6)
    a2.vline(T_NOW, -ylim, ylim, C["muted"], 1.5)
    a2.at(T_NOW, ylim * 0.86, "觀察時刻 t", C["muted"], size=12.5, dx=-9, anchor="end")
    a2.at(T_NOW, -ylim * 0.62, "此處剛生成的脈衝\n響應振幅 = 0", C["accent"], size=12, dx=10,
          anchor="start")
    for i_, (colr, txt) in enumerate([(C["accent"], "單一脈衝 p(τ)Δτ·h(t−τ)"),
                                      (C["muted"], "五個脈衝之和（Δτ = %.1f s）" % DTAU),
                                      (C["deform"], "Duhamel 積分（精確）")]):
        xx = Lm + 10 + i_ * 236
        bot.parts.append(f'<line x1="{xx}" y1="{PH-22}" x2="{xx+20}" y2="{PH-22}" '
                         f'stroke="{colr}" stroke-width="3.6" stroke-linecap="round"/>')
        bot.text_px(xx + 27, PH - 22, txt, 11.5, C["muted"], "start")

    compose([top, bot], cols=1,
            title="Duhamel 積分 = 脈衝反應函數的卷積",
            sub="示範參數 ω_0 = %.1f rad/s、ξ = %.2f、m = %.0f（改這幾個值整張圖會跟著變）"
                % (W0, XI, MASS),
            note="最右端那條剛生成的響應，振幅恰為零——h(0) = sin(0)/(mω_d) = 0。"
                 "這正是速度式用萊布尼茲法則微分時，積分上限那一項會消失的原因。",
            path=f"{OUT}/{TAG}-fig-1-duhamel.svg")
    return f"{OUT}/{TAG}-fig-1-duhamel.svg"


# ══════════════════════════════════════════════════════════
def fig2_velocity():
    """齊次解的位移與速度歷時，並把「漏掉衰減指數微分項」的錯誤曲線畫在同一張。
    攔錯：陷阱④——微分 e^{-ξω_0 t}[…] 時只動三角函數、漏掉 −ξω_0 那一項。"""
    PW, PH = 960, 268
    Lm, Rm, Tm, Bm = 100, 262, 72, 66
    TMAX = 3.4
    bw = 1.0
    sx = (PW - Lm - Rm) / bw
    bh = (PH - Tm - Bm) / sx
    ts = [i * TMAX / 900 for i in range(901)]

    # ── 上格：位移 ──
    top = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    top.panel("位移 x_h(t)", None)
    ymax = env(0.0) * 1.15
    a1 = Ax(top, (0.0, TMAX), (-ymax, ymax), (0.0, 0.0, bw, bh))
    a1.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], _ticks(ymax),
             xlabel="", ylabel="x", xfmt="{:g}", yfmt="{:g}")
    a1.hline(0.0, 0.0, TMAX, C["muted"], 1.6, dash=None)
    a1.curve(ts, [env(t) for t in ts], C["ghost"], 2.0, dash="7 5")
    a1.curve(ts, [-env(t) for t in ts], C["ghost"], 2.0, dash="7 5")
    a1.curve(ts, [x_h(t) for t in ts], C["deform"], 3.6)
    a1.mark(0.0, D0, "x(0) = d = %.1f" % D0, C["accent"], dx=12, dy=-14, size=12.5)
    a1.at(2.45, ymax * 0.70, "包絡線：指數衰減", C["ghost"], size=12.5)

    # ── 下格：速度（正確 vs 漏項） ──
    bot = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm, bg=None)
    bot.panel("速度歷時：正確式 vs 漏掉衰減指數的微分項", None)
    vmax = max(abs(v_h(t)) for t in ts) * 1.18
    a2 = Ax(bot, (0.0, TMAX), (-vmax, vmax), (0.0, 0.0, bw, bh))
    a2.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], _ticks(vmax),
             xlabel="t  (s)", ylabel="速度", xfmt="{:g}", yfmt="{:g}")
    a2.hline(0.0, 0.0, TMAX, C["muted"], 1.6, dash=None)
    a2.curve(ts, [v_h_wrong(t) for t in ts], C["load"], 2.4, dash="8 5")
    a2.curve(ts, [v_h(t) for t in ts], C["deform"], 3.6)
    cv_ = bot
    cv_.dot(a2.P(0.0, V0), 5.8, fill=C["deform"], stroke="#FFFFFF", w=2.0)
    cv_.dot(a2.P(0.0, v_h_wrong(0.0)), 5.8, fill=C["load"], stroke="#FFFFFF", w=2.0)
    a2.at(0.07, vmax * 0.80, "正確式：t = 0 給出 v = %.1f ✓" % V0, C["deform"],
          size=12.5, anchor="start")
    a2.at(0.07, vmax * 0.66, "漏項式：t = 0 給出 Bω_{d} = %.2f ×" % v_h_wrong(0.0),
          C["load"], size=12.5, anchor="start")
    a2.at(0.07, vmax * 0.52, "兩者相差恰為 ξω_{0}d = %.2f" % (XI * W0 * D0),
          C["accent"], size=12.5, anchor="start")

    bx = PW - Rm + 14
    for cv in (top, bot):
        cv.rect_px(bx, 60, Rm - 34, PH - 108, "#FFFFFF", 10, C["border"], 1.2)
    top.text_px(bx + 14, 86, "係數由初始條件定", 13, C["text"], "start", weight="700")
    for i, t in enumerate(["A = d = %.2f" % A_COEF,
                           "B = (v + ξω_{0}d)/ω_{d}",
                           "  = %.4f" % B_COEF,
                           "ω_{d} = ω_{0}√(1−ξ^{2})",
                           "  = %.4f rad/s" % WD_]):
        top.text_px(bx + 14, 110 + i * 21, t, 12, C["text"], "start")
    bot.text_px(bx + 14, 86, "漏掉的是哪一項", 13, "#9A3412", "start", weight="700")
    for i, t in enumerate(["正確 sin 係數：",
                           "(vξω_{0} + dω_{0}^{2})/ω_{d} = %.3f" % SIN_COEF,
                           "漏項式的 cos 係數變成",
                           "Bω_{d} = %.3f ≠ v = %.1f" % (B_COEF * WD_, V0),
                           "t = 0 一代就露餡。"]):
        bot.text_px(bx + 14, 110 + i * 21, t, 12, "#9A3412", "start",
                    weight="700" if i == 4 else "400")

    compose([top, bot], cols=1,
            title="齊次解的位移與速度：t = 0 反代就能抓出漏項",
            sub="示範參數 ω_0 = %.1f rad/s、ξ = %.2f、d = %.1f、v = %.1f" % (W0, XI, D0, V0),
            note="漏掉 e 的微分項後，t = 0 的速度變成 Bω_d = %.3f，"
                 "與題目給的 v = %.1f 對不上——這是最省事的自我檢核。"
                 % (B_COEF * WD_, V0),
            path=f"{OUT}/{TAG}-fig-2-velocity.svg")
    return f"{OUT}/{TAG}-fig-2-velocity.svg"


# ══════════════════════════════════════════════════════════
def fig3_identification():
    """三種振動源的振幅量級與識別阻尼比：把「為何地震識別值最大」畫成一條趨勢。
    攔錯：把三者的週期／阻尼比大小關係記反（微動最小、地震最大）。"""
    WD, HT = 1010, 520
    Lm, Rm, Tm, Bm = 108, 258, 100, 108
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    # 橫軸為 log10(振幅 g)
    ax = Ax(cv, (-5.5, 0.5), (0.0, 0.135), (0.0, 0.0, bw, bh))
    # x 軸自行標「10 的次方」，故 frame 不再重複畫一次數字刻度
    ax.frame([], [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12],
             xlabel="振動振幅（g，對數軸）", ylabel="識別阻尼比 ξ", yfmt="{:.2f}")
    for t in (-5, -4, -3, -2, -1, 0):
        cv.line(ax.P(t, 0.0), ax.P(t, 0.135), "#E8ECF2", 1.1)
        ax.at(t, 0.0, "10^{%d}" % t, C["muted"], dy=17, size=12)

    for name, a0, a1_, z0, z1, colr in SOURCES:
        x0, x1 = math.log10(a0), math.log10(a1_)
        cv.polygon([ax.P(x0, z0), ax.P(x1, z0), ax.P(x1, z1), ax.P(x0, z1)],
                   "rgba(0,0,0,0.05)", colr, 2.4)
        ax.at((x0 + x1) / 2, z1, "%s　ξ ≈ %.0f%%～%.0f%%" % (name, 100 * z0, 100 * z1),
              colr, dy=-14, size=13.5)

    # 趨勢箭頭（放在最上方，避開三個區塊）
    cv.arrow(ax.P(-4.8, 0.124), ax.P(-0.5, 0.124), C["accent"], 3.0, 12)
    ax.at(-2.7, 0.124, "振幅越大 → 非線性消能越顯著 → 識別阻尼比越高", C["accent"],
          dy=-15, size=13)

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 96, 226, 152, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 122, "識別值的大小關係", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["ξ_{微動} ＜ ξ_{激振器} ＜ ξ_{地震}",
                           "T_{微動} ≈ T_{激振器} ＜ T_{地震}",
                           "前者：非線性消能隨振幅增加",
                           "後者：開裂使等效勁度下降，",
                           "週期延長（Period Elongation）"]):
        cv.text_px(bx + 14, 148 + i * 21, t, 12, "#1D4ED8", "start",
                   weight="700" if i < 2 else "400")

    cv.rect_px(bx, 266, 226, 154, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 292, "頻率內涵決定量測方式", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["微動：寬頻白噪音 → 需長",
                           "  時間紀錄以求統計收斂",
                           "激振器：窄頻掃頻 → 逐頻",
                           "  等穩態，可直接量 FRF",
                           "地震：寬頻短脈衝、非平穩",
                           "  → 紀錄短，需大地震"]):
        cv.text_px(bx + 14, 318 + i * 18, t, 11.5, "#9A3412", "start")

    cv.text_px(WD / 2, HT - 32,
               "三個區塊沿對數振幅軸階梯上升——這張圖說明的是「為什麼」有大小關係，"
               "而不只是把結論背下來。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-identification.svg")


if __name__ == "__main__":
    print(f"ω_d = {WD_:.5f}   A = {A_COEF}   B = {B_COEF:.5f}   sin係數 = {SIN_COEF:.5f}")
    print(f"x_h(0) = {x_h(0):.5f}（應 = d = {D0}）   v_h(0) = {v_h(0):.5f}（應 = v = {V0}）")
    print(f"漏項式 v(0) = {v_h_wrong(0):.5f}（= Bω_d，與 v 差 {abs(v_h_wrong(0)-V0):.3f}）")
    num = (x_h(0.4 + 1e-6) - x_h(0.4 - 1e-6)) / 2e-6
    print(f"數值微分檢核 @t=0.4：{num:.6f} vs 正確式 {v_h(0.4):.6f}")
    print(f"h(0) = {h_imp(1.0, 1.0):.6f}（積分上限項，應為 0）")
    for f in (fig1_duhamel(), fig2_velocity(), fig3_identification()):
        print(f)
