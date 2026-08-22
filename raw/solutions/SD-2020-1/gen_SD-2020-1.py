#!/usr/bin/env python3
"""
SD-2020-1 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2020-1.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2020-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2020-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目指定要畫的三條曲線
XIS = [0.01, 0.05, 0.20]

# §4(一) 動力放大因子
def D(r, x):
    return 1.0 / math.sqrt((1 - r ** 2) ** 2 + (2 * x * r) ** 2)

# §4(二) 被動傳導率（絕對加速度比）
def TR(r, x):
    return math.sqrt((1 + (2 * x * r) ** 2) /
                     ((1 - r ** 2) ** 2 + (2 * x * r) ** 2))

# §4(二) 相對位移振幅（除以 X_g）——注意分子的 r^2，這是 F_trans 少不得的一項
def U_over_Xg(r, x):
    return r ** 2 / math.sqrt((1 - r ** 2) ** 2 + (2 * x * r) ** 2)

R_ISO = math.sqrt(2.0)          # §4(三)：TR = 1 的共同交點，也是隔震門檻
R_DEMO = 3.0                    # §4(五)：隔震後的典型頻率比
XI_DEMO = 0.05
TR_DEMO = TR(R_DEMO, XI_DEMO)               # = 0.130（原解析誤寫 0.11）
TR_APPROX = math.sqrt(1 + (2 * XI_DEMO * R_DEMO) ** 2) / R_DEMO ** 2   # 大 r 近似 = 0.116

# §4(四) 消能減震：共振點放大倍率
D_RES = [D(1.0, x) for x in XIS]            # 50 / 10 / 2.5

# 相量圖用的示範點（§4(二) 推導的檢核）
R_PH, XI_PH = 2.30, 0.20      # 取題目指定的 ξ = 0.20，三角形比例才看得清楚

# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。
COLS = [C["muted"], C["deform"], C["bmd"]]      # 對應 XIS 的三條曲線


def _panelcanvas(WD, HT, Lm, Rm, Tm, Bm):
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    return Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF"), bw, bh, sx


# ══════════════════════════════════════════════════════════
def fig1_dmf():
    """題目指定的 DMF 曲線（ξ = 0.01 / 0.05 / 0.20）。
    攔錯：共振點 D = 1/(2ξ) 的量級；以及「阻尼在所有 r 都有益」這件事必須從圖上看得出來。"""
    WD, HT = 1010, 592
    cv, bw, bh, sx = _panelcanvas(WD, HT, 100, 268, 96, 100)
    ax = Ax(cv, (0.0, 3.0), (0.0, 10.5), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 2, 4, 6, 8, 10],
             xlabel="r = Ω/ω_{0}", ylabel="DMF  D", xfmt="{:g}")

    rs = [i * 3.0 / 900 for i in range(901)]
    for x, colr in zip(XIS, COLS):
        w = 3.8 if x == XI_DEMO else 2.2
        ax.curve(rs, [min(D(r, x), 10.5) for r in rs], colr, w,
                 dash=None if x == XI_DEMO else "7 5")

    ax.hline(1.0, 0.0, 3.0, C["muted"], 1.4)
    ax.at(0.40, 1.95, "準靜態平台 D ≈ 1", C["accent"], size=13)
    ax.vline(1.0, 0.0, 10.5, C["load"], 1.5)
    ax.at(0.90, 10.75, "r = 1 共振", C["load"], size=13, anchor="end")

    for x, colr in zip(XIS, COLS):
        y = min(D(1.0, x), 10.5)
        cv.dot(ax.P(1.0, y), 5.6, fill=colr, stroke="#FFFFFF", w=2.0)
    ax.at(1.16, 9.7, "ξ = 0.01 → D = %.0f（超出圖框）" % D_RES[0], C["muted"],
          size=12.5, anchor="start")
    ax.at(1.16, 8.5, "ξ = 0.05 → D = %.0f" % D_RES[1], C["deform"], size=12.5, anchor="start")
    ax.at(1.16, 3.3, "ξ = 0.20 → D = %.1f" % D_RES[2], C["bmd"], size=12.5, anchor="start")

    bx = 100 + int(bw * sx) + 24
    cv.rect_px(bx, 92, 232, 168, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 118, "消能減震怎麼看這張圖", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["加消能設備 = 把 ξ 往上推，",
                           "曲線整條被壓下去。",
                           "共振點 D = 1/(2ξ)：",
                           "ξ 由 1% 升到 20%，",
                           "D 由 %.0f 降到 %.1f（%.0f 倍）。" % (D_RES[0], D_RES[2],
                                                            D_RES[0] / D_RES[2])]):
        cv.text_px(bx + 14, 146 + i * 23, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i == 4 else "400")

    cv.rect_px(bx, 278, 232, 142, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 304, "DMF 的關鍵性質", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["分子恆為 1，ξ 只出現在",
                           "分母 → **任何 r 下，ξ 越大",
                           "D 越小**，阻尼永遠有益。",
                           "這一點與 TR 完全不同",
                           "（見 fig-4 對照）。"]):
        cv.text_px(bx + 14, 330 + i * 21, t.replace("**", ""), 12.5, "#9A3412", "start",
                   weight="700" if i in (1, 2) else "400")

    cv.legend(bx + 6, 448, [(C["deform"], "ξ = 0.05"),
                            (C["muted"], "ξ = 0.01"),
                            (C["bmd"], "ξ = 0.20")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 32,
               "DMF 分子是常數 1——阻尼只出現在分母，所以壓低曲線是無條件的。"
               "隔震那條 TR 曲線不是這樣。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-dmf.svg")


# ══════════════════════════════════════════════════════════
def fig2_tr():
    """題目指定的 TR 曲線，並標出 √2 共同交點與 r = 3 的讀值。
    攔錯：(a) 以為 r > 1 就開始隔震（正確門檻是 √2）；
          (b) TR(3, 0.05) 誤讀為 0.11（正確 0.130，近似式才是 0.116）。"""
    WD, HT = 1010, 592
    cv, bw, bh, sx = _panelcanvas(WD, HT, 100, 268, 96, 100)
    ax = Ax(cv, (0.0, 3.0), (0.0, 4.0), (0.0, 0.0, bw, bh))

    # 隔震區底色（分界由 R_ISO 算出，不是畫到那裡剛好好看）
    cv.polygon([ax.P(R_ISO, 0.0), ax.P(3.0, 0.0), ax.P(3.0, 4.0), ax.P(R_ISO, 4.0)],
               "rgba(46,125,111,0.08)")
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], [0, 1, 2, 3, 4],
             xlabel="r = Ω/ω_{0} = T_{structure}/T_{g}", ylabel="TR", xfmt="{:g}")

    rs = [i * 3.0 / 900 for i in range(901)]
    for x, colr in zip(XIS, COLS):
        w = 3.8 if x == XI_DEMO else 2.2
        ax.curve(rs, [min(TR(r, x), 4.0) for r in rs], colr, w,
                 dash=None if x == XI_DEMO else "7 5")

    ax.hline(1.0, 0.0, 3.0, C["muted"], 1.4)
    ax.vline(1.0, 0.0, 4.0, C["load"], 1.5)
    ax.vline(R_ISO, 0.0, 4.0, C["bmd"], 2.2, dash=None)
    ax.at(1.0, 4.18, "r = 1 共振", C["load"], size=13)
    ax.at(R_ISO, 4.18, "r = √2 隔震門檻", C["bmd"], size=13)

    ax.mark(R_ISO, 1.0, "三條曲線共同交點 TR = 1（與 ξ 無關）", C["bmd"],
            dx=13, dy=-14, size=13)
    cv.line(ax.P(R_DEMO, TR_DEMO + 0.03), ax.P(R_DEMO, 0.60), C["accent"], 1.6, dash="4 4")
    cv.dot(ax.P(R_DEMO, TR_DEMO), 5.6, fill=C["accent"], stroke="#FFFFFF", w=2.0)
    ax.at(R_DEMO, 0.78, "r = 3、ξ = 0.05\nTR = %.3f（約 13%%）" % TR_DEMO,
          C["accent"], dx=-8, size=13, anchor="end")

    ax.at(0.55, 3.35, "放大區", C["load"], size=15)
    ax.at(2.30, 3.35, "隔震區  TR ＜ 1", C["bmd"], size=15)
    ax.at(2.30, 2.92, "（此區 ξ 越大 TR 越大）", C["bmd"], size=12.5)

    bx = 100 + int(bw * sx) + 24
    cv.rect_px(bx, 92, 232, 152, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 118, "1 ＜ r ＜ √2 不是隔震", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["相位已反轉，但 TR 仍 ＞ 1；",
                           "r = 1.2、ξ = 0.05 時 TR = %.2f，" % TR(1.2, XI_DEMO),
                           "車體／樓板位移比地面還大。",
                           "真正隔震要 r ＞ √2。"]):
        cv.text_px(bx + 14, 146 + i * 23, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 3 else "400")

    cv.rect_px(bx, 262, 232, 152, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 288, "r = 3 的讀值不是 0.11", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["精確式：TR = %.4f" % TR_DEMO,
                           "大 r 近似：√(1+(2ξr)^{2})/r^{2}",
                           "        = %.4f" % TR_APPROX,
                           "近似值偏低，設計取精確式。"]):
        cv.text_px(bx + 14, 316 + i * 23, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i == 0 else "400")

    cv.legend(bx + 6, 444, [(C["deform"], "ξ = 0.05"),
                            (C["muted"], "ξ = 0.01"),
                            (C["bmd"], "ξ = 0.20")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 32,
               "三條不同阻尼的曲線交會在 r = √2——這是「隔震門檻與阻尼無關」最直接的證據。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-tr.svg")


# ══════════════════════════════════════════════════════════
def fig3_phasor():
    """傳遞力的相量合成：彈簧力與阻尼力相位差 90°，合力 = kU√(1+(2ξr)²)。
    攔錯：F_trans 漏掉 U 分子裡的 r²（除以 m 後湊不出 Ω²X_g，r→0 時發散）；
          以及把絕對加速度振幅寫成 ω_0²X_abs（應為 Ω²X_abs）。"""
    WD, HT = 1010, 470
    cv = Canvas(WD, HT, sx=1, bg="#FFFFFF")
    cv.text_px(WD / 2, 40, "傳遞力 F_{trans} 的相量合成（示範點 r = %.2f、ξ = %.2f）"
               % (R_PH, XI_PH), 17.5, C["text"], weight="700")

    U = U_over_Xg(R_PH, XI_PH)                 # U / X_g
    a = 2 * XI_PH * R_PH                       # cΩ/k = 2ξr
    Ft = U * math.sqrt(1 + a ** 2)             # F_trans / (k X_g)

    ox, oy = 214, 298
    S = 196.0 / math.hypot(1.0, a)             # 讓斜邊固定長度，比例由 a 決定
    px, py = ox + S, oy
    qx, qy = ox + S, oy - S * a

    cv.parts.append(f'<line x1="{ox}" y1="{oy}" x2="{ox + S * 1.22:.1f}" y2="{oy}" '
                    f'stroke="{C["muted"]}" stroke-width="1.3" stroke-dasharray="4 4"/>')
    for x0_, y0_, x1_, y1_, colr, wid in ((ox, oy, px, py, C["deform"], 4.2),
                                          (px, py, qx, qy, C["bmd"], 4.2),
                                          (ox, oy, qx, qy, C["load"], 5.0)):
        ang = math.atan2(y1_ - y0_, x1_ - x0_)
        hl = 13
        bxx, byy = x1_ - hl * math.cos(ang), y1_ - hl * math.sin(ang)
        cv.parts.append(f'<line x1="{x0_:.1f}" y1="{y0_:.1f}" x2="{bxx:.1f}" y2="{byy:.1f}" '
                        f'stroke="{colr}" stroke-width="{wid}" stroke-linecap="round"/>')
        hw = hl * 0.46
        pts = [(x1_, y1_), (bxx - hw * math.sin(ang), byy + hw * math.cos(ang)),
               (bxx + hw * math.sin(ang), byy - hw * math.cos(ang))]
        cv.parts.append(f'<polygon points="{" ".join(f"{p:.1f},{q:.1f}" for p, q in pts)}" '
                        f'fill="{colr}"/>')
    cv.parts.append(f'<polyline points="{px - 17},{py} {px - 17},{py - 17} {px},{py - 17}" '
                    f'fill="none" stroke="{C["muted"]}" stroke-width="1.7"/>')

    cv.math_px(ox + S / 2, oy + 27, "k U", 16, C["deform"], "middle", weight="700")
    cv.math_px(qx + 14, (py + qy) / 2, "c Ω U", 16, C["bmd"], "start", weight="700")
    cv.math_px(ox + S * 0.32, oy - S * a * 0.40 - 17, "F_{trans}", 18, C["load"],
               "middle", weight="700")
    cv.text_px(ox - 4, oy + 64, "彈簧力與阻尼力相位差 90°，取向量和：", 12.5, C["muted"], "start")
    cv.math_px(ox - 4, oy + 90, "c Ω U / (k U) = 2ξr = %.3f" % a, 14, C["muted"],
               "start", weight="700")
    cv.math_px(ox - 4, oy + 116, "F_{trans} = k U √(1 + (2ξr)^{2}) = %.4f · k X_{g}" % Ft,
               14, C["load"], "start", weight="700")

    bx = 494
    cv.rect_px(bx, 74, WD - bx - 34, 186, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 18, 100, "正確的三步", 13.5, "#1D4ED8", "start", weight="700")
    for i_, t in enumerate(["① F_{trans} = k U √(1 + (2ξr)^{2})",
                            "② U = r^{2}X_{g} / √((1−r^{2})^{2} + (2ξr)^{2})",
                            "③ |x''_{abs}| = F_{trans}/m，而 k/m = ω_{0}^{2}、ω_{0}^{2}r^{2} = Ω^{2}",
                            "   → |x''_{abs}| = Ω^{2}X_{g} · TR",
                            "本例：F_{trans}/(kX_{g}) = %.4f，TR = %.4f" % (Ft, TR(R_PH, XI_PH))]):
        cv.text_px(bx + 16, 130 + i_ * 26, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i_ == 4 else "400")

    cv.rect_px(bx, 278, WD - bx - 34, 134, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 18, 304, "兩個必查的檢核點", 13.5, "#9A3412", "start", weight="700")
    for i_, t in enumerate(["F_{trans} 分子必須含 r^{2}（來自 U）。漏掉會得到",
                            "TR/r^{2}，在 r → 0 時發散，明顯不合物理。",
                            "絕對加速度振幅是 Ω^{2}X_{abs}，不是 ω_{0}^{2}X_{abs}——",
                            "反應以激振頻率 Ω 振盪，微分兩次帶出的是 Ω^{2}。"]):
        cv.text_px(bx + 16, 330 + i_ * 21, t, 12, "#9A3412", "start")

    cv.text_px(WD / 2, HT - 24,
               "相量圖只負責「合成」這一步；r^{2} 是從 U 帶進來的——"
               "把這兩件事分開看，就不會把 r^{2} 弄丟或多塞一個。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-phasor.svg")


# ══════════════════════════════════════════════════════════
def fig4_compare():
    """DMF 與 TR 並排：在同一個設計點 r = 3 讀值，阻尼的效果方向相反。
    攔錯：把「阻尼永遠有益」的直覺套到隔震設計上。"""
    PW, PH = 500, 500
    Tm, Bm = 100, 128
    panels = []
    for name, fn, note in (("動力放大因子 DMF", D, "ξ 越大 → 全域皆降"),
                           ("被動傳導率 TR", TR, "ξ 越大 → 隔震區反升")):
        bw = 1.0
        sx = (PW - 88 - 44) / bw
        bh = (PH - Tm - Bm) / sx
        cv = Canvas(PW, PH, sx=sx, ox=88, oy=Bm, bg=None)
        cv.panel(name, note)
        ax = Ax(cv, (0.0, 3.2), (0.0, 3.0), (0.0, 0.0, bw, bh))
        ax.frame([0, 1, 2, 3], [0, 1, 2, 3], xlabel="r", ylabel="", xfmt="{:g}")
        rs = [i_ * 3.2 / 640 for i_ in range(641)]
        for x, colr in zip(XIS, COLS):
            ax.curve(rs, [min(fn(r, x), 3.0) for r in rs], colr,
                     3.4 if x == XI_DEMO else 2.0, dash=None if x == XI_DEMO else "7 5")
        ax.hline(1.0, 0.0, 3.2, C["muted"], 1.3)
        ax.vline(R_DEMO, 0.0, 3.0, C["accent"], 1.8)
        ax.at(R_DEMO, 3.12, "r = 3", C["accent"], size=12.5)
        if fn is TR:
            ax.vline(R_ISO, 0.0, 3.0, C["bmd"], 2.0, dash=None)
            ax.at(R_ISO, 3.12, "隔震門檻", C["bmd"], size=12.5)
        for x, colr in zip(XIS, COLS):
            cv.dot(ax.P(R_DEMO, fn(R_DEMO, x)), 5.0, fill=colr, stroke="#FFFFFF", w=1.8)

        # r = 3 的讀值表（值由 fn 現算，不是寫死）
        vals = [fn(R_DEMO, x) for x in XIS]
        cv.rect_px(88, PH - 108, PW - 88 - 44, 84, "#F5F7FA", 10, C["border"], 1.2)
        cv.text_px(102, PH - 88, "在 r = 3 的讀值", 12.5, C["text"], "start", weight="700")
        for i_, (x, colr, v) in enumerate(zip(XIS, COLS, vals)):
            cv.text_px(102 + i_ * 118, PH - 64, "ξ = %.2f" % x, 12, colr, "start")
            cv.text_px(102 + i_ * 118, PH - 44, "%.4f" % v, 14, colr, "start", weight="700")
        arrow_txt = "↓ 遞減" if vals[-1] < vals[0] else "↑ 遞增"
        cv.text_px(PW - 58, PH - 54, arrow_txt, 14,
                   C["bmd"] if vals[-1] < vals[0] else C["load"], "end", weight="700")
        panels.append(cv)

    dm = [D(R_DEMO, x) for x in XIS]
    tr = [TR(R_DEMO, x) for x in XIS]
    compose(panels, cols=2,
            title="同一個設計點 r = 3，阻尼對兩條曲線的作用方向相反",
            sub="左：DMF 分子恆為 1，阻尼只出現在分母；右：TR 分子另含阻尼項，阻尼力本身也會被傳遞進去",
            note="ξ 由 %.2f 升到 %.2f：DMF 由 %.4f 降到 %.4f（−%.1f%%），"
                 "TR 卻由 %.4f 升到 %.4f（+%.1f%%）——隔震設計不能追求高阻尼。"
                 % (XIS[0], XIS[-1], dm[0], dm[-1], 100 * (1 - dm[-1] / dm[0]),
                    tr[0], tr[-1], 100 * (tr[-1] / tr[0] - 1)),
            path=f"{OUT}/{TAG}-fig-4-compare.svg")
    return f"{OUT}/{TAG}-fig-4-compare.svg"


if __name__ == "__main__":
    print("D(1,ξ):", [round(D(1, x), 3) for x in XIS])
    print("TR(√2,ξ):", [round(TR(R_ISO, x), 6) for x in XIS])
    print(f"TR(3,0.05) = {TR_DEMO:.5f}   大 r 近似 = {TR_APPROX:.5f}")
    print(f"TR(1.2, 0) = {TR(1.2,0.0):.4f}")
    print("r=3 讀值  DMF:", [round(D(3.0, x), 4) for x in XIS],
          "  TR:", [round(TR(3.0, x), 4) for x in XIS])
    print(f"相量示範 r={R_PH} ξ={XI_PH}: U/Xg = {U_over_Xg(R_PH,XI_PH):.4f}  "
          f"F/(kXg) = {U_over_Xg(R_PH,XI_PH)*math.sqrt(1+(2*XI_PH*R_PH)**2):.4f}  "
          f"TR = {TR(R_PH,XI_PH):.4f}")
    for f in (fig1_dmf(), fig2_tr(), fig3_phasor(), fig4_compare()):
        print(f)
