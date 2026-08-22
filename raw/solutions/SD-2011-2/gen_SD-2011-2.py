#!/usr/bin/env python3
"""
SD-2011-2 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2011-2.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2011-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2011-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# 「解題步驟／前置」：空間波長 L 與車速 v 化為時間激振頻率
#     ω_f = 2πv/L，β = ω_f/ω_0 = (2πv/L)·√(m/k)
# 「步驟二」：共振車速 v_res = (L/2π)√(k/m) = L·f_0 = L/T_0
# 「步驟三」：無阻尼穩態絕對位移 u'_p = u_g0/(1−β²)·sin(ω_f t)
#            → 傳導率 TR = 1/|1−β²|
BETA_ISO = math.sqrt(2.0)        # §解題關鍵觀念 3：隔振門檻（不是 β = 1）
BETA_MYTH = 1.2                  # 常見誤區的示範點
TR_MYTH = 1.0 / abs(1 - BETA_MYTH ** 2)      # = 2.27，β 已 ＞ 1 卻仍放大 2 倍以上


def tr(beta, xi):
    """有阻尼傳導率（位移基礎激振）"""
    return math.sqrt((1 + (2 * xi * beta) ** 2) /
                     ((1 - beta ** 2) ** 2 + (2 * xi * beta) ** 2))


# 繪圖用的路面幾何（純視覺，不影響上列任何物理量）
LAM, AMP = 1.0, 0.085            # 一個波長 = 1 模型單位；振幅 = u_g0
XC, RW = 2.00, 0.13              # 車輪中心 x、輪半徑


def road(x):
    return AMP * math.sin(2 * math.pi * x / LAM)


# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。


def spring(cv, p0, p1, coils=6, amp=0.055, color=C["member"], w=2.6):
    """鋸齒彈簧（p0 → p1 任意方向）"""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    Lm = math.hypot(dx, dy) or 1.0
    ux, uy = dx / Lm, dy / Lm
    nx, ny = -uy, ux
    lead = Lm * 0.16
    pts = [(x0, y0), (x0 + ux * lead, y0 + uy * lead)]
    seg = (Lm - 2 * lead) / (2 * coils)
    for i in range(2 * coils):
        t = lead + seg * (i + 0.5)
        s = amp if i % 2 == 0 else -amp
        pts.append((x0 + ux * t + nx * s, y0 + uy * t + ny * s))
    pts += [(x1 - ux * lead, y1 - uy * lead), (x1, y1)]
    cv.poly(pts, color, w)


def dashpot(cv, p0, p1, color=C["member"], w=2.6, hw=0.055, hh=0.075):
    """阻尼器（僅供鉛垂方向使用）：p0 為下端（缸體側），p1 為上端（活塞桿側）"""
    (x0, y0), (x1, y1) = p0, p1
    ym = (y0 + y1) / 2
    cv.line((x0, y0), (x0, ym - hh), color, w)
    cv.poly([(x0 - hw, ym + hh), (x0 - hw, ym - hh),
             (x0 + hw, ym - hh), (x0 + hw, ym + hh)], color, w)
    cv.line((x1, y1), (x1, ym + hh * 0.25), color, w)
    cv.line((x0 - hw * 0.78, ym + hh * 0.25), (x0 + hw * 0.78, ym + hh * 0.25), color, w + 0.6)


# ══════════════════════════════════════════════════════════
def fig1_car():
    """題目重繪：把「空間的路面輪廓」與「時間的基礎激振」畫在同一張圖上。
    攔錯：漏掉 x = v t 這步代換，導致激振頻率寫成 v/L 或 1/L 之類。"""
    WD, HT = 1060, 476
    Lm, Rm, Tm, Bm = 78, 238, 68, 86
    xa, xb, ya, yb = -0.12, 3.45, -0.26, 1.20
    sx = min((WD - Lm - Rm) / (xb - xa), (HT - Tm - Bm) / (yb - ya))
    cv = Canvas(WD, HT, sx=sx, ox=Lm - xa * sx, oy=Bm - ya * sx, bg="#FFFFFF")

    # ── 路面 ──
    xs = [xa + i * (xb - xa) / 500 for i in range(501)]
    cv.polygon([(xa, ya)] + [(x, road(x)) for x in xs] + [(xb, ya)], "#EDF1F6")
    cv.poly([(x, road(x)) for x in xs], C["member"], 3.2)
    cv.line((xa, 0), (xb, 0), C["ghost"], 1.4, dash="6 5")

    # ── 車體（質塊）＋ 懸吊 ──
    yc = road(XC) + RW                       # 輪心高度（隨路面幾何算出）
    ybot, ytop = yc + 0.49, yc + 0.79        # 車體下緣、上緣
    cv.line((XC - 0.36, yc), (XC + 0.36, yc), C["member"], 3.4)
    spring(cv, (XC - 0.30, yc), (XC - 0.30, ybot), coils=5, amp=0.062)
    dashpot(cv, (XC + 0.30, yc), (XC + 0.30, ybot), hw=0.062, hh=0.088)
    cv.circle((XC, yc), RW, fill="#FFFFFF", stroke=C["member"], w=3.0)
    cv.dot((XC, yc), 4.6, fill=C["member"])
    cv.rect_px(cv.X(XC - 0.46), cv.Y(ytop), 0.92 * sx, (ytop - ybot) * sx,
               "#DCE4EE", 8, C["member"], 2.6)
    cv.math((XC, (ybot + ytop) / 2), "m", 22, C["text"], weight="700")
    cv.math((XC - 0.30, (yc + ybot) / 2), "k", 18, C["text"], "end", dx=-14)
    cv.math((XC + 0.30, (yc + ybot) / 2), "c", 18, C["text"], "start", dx=16)

    # 絕對位移 u^t（沿用題圖記號）
    cv.arrow((XC + 0.62, ytop - 0.04), (XC + 0.62, ytop + 0.26), C["deform"], 3.0, 10)
    cv.math((XC + 0.62, ytop + 0.26), "u^{t}", 20, C["deform"], "start", dx=10, weight="700")

    # 車速
    cv.arrow((XC - 0.95, ytop + 0.13), (XC - 0.40, ytop + 0.13), C["load"], 3.4, 12)
    cv.math((XC - 0.68, ytop + 0.13), "v", 20, C["load"], dy=-18, weight="700")
    cv.text((XC - 0.68, ytop + 0.13), "等速", 13, C["load"], dy=17)

    # 波長 L 與振幅 u_g0（幾何量由 LAM、AMP 決定，改參數圖就跟著變）
    cv.dim((0.25, AMP + 0.30), (1.25, AMP + 0.30), "L", off=0, label_off=-16)
    for x in (0.25, 1.25):
        cv.line((x, road(x)), (x, AMP + 0.30), C["dim"], 1.0, dash="3 3")
    cv.line((0.75, road(0.75)), (0.55, road(0.75)), C["dim"], 1.0, dash="3 3")
    cv.dim((0.75, road(0.75)), (0.75, 0.0), "u_{g0}", off=-30, label_off=-17)

    # x = v t 座標軸
    cv.arrow((0.10, -0.20), (1.05, -0.20), C["muted"], 2.0, 9)
    cv.math((1.05, -0.20), "x = v t", 15, C["muted"], "start", dx=10, weight="700")

    # ── 右側說明 ──
    bx = WD - Rm + 10
    cv.rect_px(bx, 62, 216, 142, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 88, "空間 → 時間的代換", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["u_{g}(x) = u_{g0} sin(2πx/L)",
                           "代入 x = v t：",
                           "u_{g}(t) = u_{g0} sin(ω_{f} t)",
                           "ω_{f} = 2πv/L"]):
        cv.text_px(bx + 16, 114 + i * 24, t, 13, "#1D4ED8", "start",
                   weight="700" if i == 3 else "400")

    cv.rect_px(bx, 222, 216, 190, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 248, "兩組座標不要混用", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["絕對位移 u^{t}：車體對地面",
                           "相對位移 z = u^{t} − u_{g}：",
                           "懸吊行程，決定彈簧力",
                           "相對座標下的運動方程式",
                           "m z'' + c z' + k z",
                           "    = m u_{g0} ω_{f}^{2} sin(ω_{f} t)",
                           "共振車速 v_{res} = L / T_{0}"]):
        cv.text_px(bx + 14, 274 + i * 22, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 6 else "400")

    cv.text_px(WD / 2, HT - 28,
               "路面凹凸是「空間」的量，結構承受的卻是「時間」的激振——"
               "本題所有後續推導都掛在 ω_f = 2πv/L 這一步上。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-car.svg")


# ══════════════════════════════════════════════════════════
def fig2_transmissibility():
    """傳導率 TR–β 曲線：把「隔振從哪裡開始」畫成一條線。
    攔錯：以為 β ＞ 1（車速超過共振車速）就開始隔振——正確門檻是 β ＞ √2。"""
    WD, HT = 1010, 596
    Lm, Rm, Tm, Bm = 96, 254, 96, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 3.0), (0.0, 4.0), (0.0, 0.0, bw, bh))

    # 放大區／隔振區底色（分界由 BETA_ISO 決定，不是畫到那裡剛好好看）
    cv.polygon([ax.P(BETA_ISO, 0.0), ax.P(3.0, 0.0), ax.P(3.0, 4.0), ax.P(BETA_ISO, 4.0)],
               "rgba(46,125,111,0.08)")
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 1, 2, 3, 4],
             xlabel="β = ω_{f}/ω_{0} = 2πv/(L ω_{0})", ylabel="TR = u^{t}/u_{g0}",
             xfmt="{:g}")

    bs = [i * 3.0 / 900 for i in range(901)]
    for xi, col, w, dash in ((0.25, C["bmd"], 1.9, "6 5"),
                             (0.50, C["muted"], 1.9, "6 5"),
                             (0.0, C["deform"], 3.8, None)):
        ax.curve(bs, [min(tr(b, xi) if xi else 1.0 / abs(1 - b ** 2 or 1e-9), 4.0)
                      for b in bs], col, w, dash=dash)

    ax.hline(1.0, 0.0, 3.0, C["muted"], 1.5)
    ax.vline(1.0, 0.0, 4.0, C["load"], 1.6)
    ax.vline(BETA_ISO, 0.0, 4.0, C["bmd"], 2.0, dash=None)

    ax.at(1.0, 4.18, "β = 1  共振", C["load"], size=13.5)
    ax.at(BETA_ISO, 4.18, "β = √2  隔振門檻", C["bmd"], size=13.5)
    ax.mark(BETA_ISO, 1.0, "TR = 1（與 ξ 無關的共同交點）", C["bmd"], dx=13, dy=-14, size=13)
    ax.mark(BETA_MYTH, min(TR_MYTH, 4.0), "β = %.1f 仍放大 %.2f 倍" % (BETA_MYTH, TR_MYTH),
            C["accent"], dx=13, dy=-13, size=13)

    ax.at(0.50, 3.30, "放大區", C["load"], size=15)
    ax.at(2.45, 2.60, "隔振區  TR ＜ 1", C["bmd"], size=15)
    ax.at(2.45, 2.15, "（阻尼越大反而越差）", C["bmd"], size=12.5)

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 96, 218, 202, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 122, "1 ＜ β ＜ √2 是什麼？", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["相位已反轉（u^{t} 與 u_{g} 反相），",
                           "但 TR = 1/(β^{2}−1) 仍 ＞ 1，",
                           "車體位移比路面起伏還大。",
                           "β = 1.2 → TR = %.2f" % TR_MYTH,
                           "真正隔振要 v ＞ √2 · v_{res}"]):
        cv.text_px(bx + 14, 150 + i * 24, t, 12.5, "#9A3412", "start",
                   weight="700" if i >= 3 else "400")

    cv.rect_px(bx, 316, 218, 104, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 342, "為什麼 β=√2 是交點", 13, "#1D4ED8", "start", weight="700")
    cv.text_px(bx + 14, 368, "代 β^{2} = 2 進有阻尼式，", 12.5, "#1D4ED8", "start")
    cv.text_px(bx + 14, 390, "分子分母同為 1+(2ξβ)^{2}，", 12.5, "#1D4ED8", "start")
    cv.text_px(bx + 14, 410, "故 TR ≡ 1。", 12.5, "#1D4ED8", "start", weight="700")

    cv.legend(bx + 6, 442, [(C["deform"], "ξ = 0（本題）"),
                            (C["bmd"], "ξ = 0.25"),
                            (C["muted"], "ξ = 0.50")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 30,
               "三條不同阻尼的曲線交會在 β = √2 這一點——這是「隔振門檻與阻尼無關」最直接的證據。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-transmissibility.svg")


if __name__ == "__main__":
    print(f"β_iso = {BETA_ISO:.4f}   TR(β=1.2) = {TR_MYTH:.3f}   "
          f"TR(√2, ξ=0.25) = {tr(BETA_ISO, 0.25):.4f}   TR(√2, ξ=0.5) = {tr(BETA_ISO, 0.5):.4f}")
    print(fig1_car())
    print(fig2_transmissibility())
