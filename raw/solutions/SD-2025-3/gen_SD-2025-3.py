#!/usr/bin/env python3
"""
SD-2025-3 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2025-3.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2025-3"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2025-3.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定
W1, W2, W3 = 14.5, 31.1, 46.2        # ω_1, ω_2, ω_3（rad/s）
ZETA = 0.05                          # ζ_1 = ζ_3（題目給定）

# §5.2 緊湊式：ζ_1 = ζ_3 = ζ 時的解析解（是算式，不是抄來的數字）
A1 = 2 * ZETA / (W1 + W3)                    # §4 Step 3：a_1 = 0.1/60.7
A0 = 2 * ZETA * W1 * W3 / (W1 + W3)          # §4 Step 3：a_0 = 66.99/60.7


def zeta(w):
    """§4 Step 1：Rayleigh 阻尼比 ζ(ω) = a_0/(2ω) + a_1 ω/2"""
    return A0 / (2 * w) + A1 * w / 2


def zeta_m(w):  return A0 / (2 * w)      # 質量比例項（低頻主導）
def zeta_k(w):  return A1 * w / 2        # 剛度比例項（高頻主導）


W_STAR = math.sqrt(A0 / A1)              # §5.1：dζ/dω = 0 → ω* = √(a_0/a_1) = √(ω_1ω_3)
Z2 = zeta(W2)                            # §4 Step 4：ζ_2 ≈ 0.0434
Z_MIN = zeta(W_STAR)                     # 曲線最小值 = √(a_0 a_1)

# 注意：含中文的字串一律用 text_px（FONT 有 CJK fallback）；
#      math_px 用的襯線數學字型沒有中文字，中文會整個消失。


def fig1_rayleigh():
    """Rayleigh 阻尼 U 型曲線，並把兩個分量拆成兩條線。
    攔錯：(a) ζ = a_0/(2ω) + a_1ω/2 的分子分母倒置；(b) 誤以為 ζ_2 應介於 ζ_1、ζ_3 之間。"""
    WD, HT = 1010, 604
    Lm, Rm, Tm, Bm = 96, 274, 104, 104
    bw, bh = 1.0, 0.60
    sx = min((WD - Lm - Rm) / bw, (HT - Tm - Bm) / bh)
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (6.0, 60.0), (0.0, 0.12), (0.0, 0.0, bw, bh))
    ax.frame([10, 20, 30, 40, 50, 60], [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12],
             xlabel="ω  (rad/s)", ylabel="ζ", yfmt="{:.2f}")

    ws = [6.0 + i * (60.0 - 6.0) / 400 for i in range(401)]
    ax.curve(ws, [zeta_m(w) for w in ws], C["load"], 2.2, dash="7 5")
    ax.curve(ws, [zeta_k(w) for w in ws], C["bmd"], 2.2, dash="7 5")
    ax.curve(ws, [zeta(w) for w in ws], C["deform"], 3.8)

    # 弦線與曲線之間的區域——嚴格凸函數在兩個等值點之間必定整段落在弦線下方。
    # 這就是 §5.1 用來取代「ω_2 > ω*」那個非因果推論的論證；弦線本身即 ζ = 5% 水平線。
    _band = [w for w in ws if W1 <= w <= W3]
    cv.polygon([ax.P(W1, ZETA)] + [ax.P(w, zeta(w)) for w in _band] + [ax.P(W3, ZETA)],
               "rgba(180,83,9,0.13)")
    ax.at(26.0, 0.0472, "嚴格凸 → 中間整段更低", C["accent"], size=12.5)

    # 兩個分量直接標在曲線旁（在圖的空白角落，不靠圖例辨識）
    # 放在 41 而不是 45：45 正好壓在 ω_3 = 46.2 的縱向對位線上。
    cv.math_px(cv.X(ax.X(41.0)), cv.Y(ax.Y(zeta_m(41.0))) - 15,
               "a_{0}/(2ω)", 15, C["load"], "middle", weight="700")
    cv.math_px(cv.X(ax.X(11.5)), cv.Y(ax.Y(zeta_k(11.5))) - 15,
               "a_{1}ω/2", 15, C["bmd"], "middle", weight="700")

    # ζ = 5% 基準線
    ax.hline(ZETA, 6.0, 60.0, C["accent"], 1.5, dash="4 5")
    cv.math_px(cv.X(ax.X(37.0)), cv.Y(ax.Y(ZETA)) - 11, "ζ = 5%", 13.5,
               C["accent"], "middle", weight="700")

    # 四條縱向對位線 + 底部標籤
    for w, ytop, lab, col in ((W1, zeta(W1), "ω_{1}", C["deform"]),
                              (W_STAR, Z_MIN, "ω*", C["accent"]),
                              (W2, Z2, "ω_{2}", C["load"]),
                              (W3, zeta(W3), "ω_{3}", C["deform"])):
        ax.vline(w, 0.0, ytop, C["muted"], 1.3)
        cv.math_px(cv.X(ax.X(w)), cv.Y(ax.Y(0.0)) - 13, lab, 14, col, "middle", weight="700")

    ax.mark(W1, zeta(W1), "%.2f%%" % (100 * zeta(W1)), C["deform"], dx=9, dy=-15)
    ax.mark(W3, zeta(W3), "%.2f%%" % (100 * zeta(W3)), C["deform"], dx=-9, dy=-15, anchor="end")
    ax.mark(W2, Z2, "%.2f%%" % (100 * Z2), C["load"], dx=0, dy=21, anchor="middle")
    cv.dot(ax.P(W_STAR, Z_MIN), 6.0, fill=C["accent"], stroke="#FFFFFF", w=2.0)


    # ── 右側說明欄 ──
    bx = Lm + int(bw * sx) + 26
    cv.rect_px(bx, 100, 238, 132, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 126, "由 ζ_{1} = ζ_{3} = 5% 反推兩係數", 13.5, "#1D4ED8", "start", weight="700")
    cv.math_px(bx + 16, 156, "a_{0} = 2ζω_{1}ω_{3}/(ω_{1}+ω_{3}) = %.3f s^{-1}" % A0,
               13, "#1D4ED8", "start", weight="700")
    cv.math_px(bx + 16, 182, "a_{1} = 2ζ/(ω_{1}+ω_{3})", 13, "#1D4ED8", "start",
               weight="700")
    cv.math_px(bx + 16, 206, "     = %.3f × 10^{-3} s" % (A1 * 1e3), 13, "#1D4ED8",
               "start", weight="700")

    cv.rect_px(bx, 250, 238, 184, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 276, "為什麼中間反而最小", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["低頻端：質量項 a_{0}/(2ω) 主導",
                           "高頻端：剛度項 a_{1}ω/2 主導",
                           "兩端釘在 5%，中間必然下凹",
                           "最低點 ω* = √(ω_{1}ω_{3}) = %.1f rad/s" % W_STAR,
                           "ζ_{2} = %.2f%% ＜ ζ_{1} = ζ_{3} = 5%%" % (100 * Z2)]):
        cv.text_px(bx + 16, 304 + i * 26, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 4 else "400")

    cv.legend(bx + 6, 470, [(C["deform"], "總阻尼比 ζ(ω)"),
                            (C["load"], "質量比例項 a_{0}[M]"),
                            (C["bmd"], "剛度比例項 a_{1}[K]")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 32,
               "把 a_{0}[M] 與 a_{1}[K] 拆成兩條線畫出來，「中間頻率阻尼比最小」就不再是需要硬記的結論。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-rayleigh.svg")


# §3.5 L3：ζ(ω) = ζ(ω*²/ω)，即在對數頻率軸上關於 ω* 對稱。
# 這使 ω* 必為幾何平均 √(ω_1ω_3)，而不是算術平均 (ω_1+ω_3)/2。
W_ARITH = (W1 + W3) / 2.0                # 算術平均——常被誤當成最低點
W2_MIRROR = W_STAR ** 2 / W2             # ω_2 的鏡像點，兩者 ζ 必相等


def fig2_logsym():
    """把橫軸換成對數頻率：ζ(ω) 關於 ω* 左右對稱，ω* 因此是幾何平均。
    攔錯：(a) 把 ω* 當成 (ω_1+ω_3)/2；
          (b) 以為「線性軸上看起來偏左」是畫錯，而不是對數對稱的必然結果。"""
    WD, HT = 1010, 566
    Lm, Rm, Tm, Bm = 96, 268, 96, 112
    bw, bh = 1.0, 0.52
    sx = min((WD - Lm - Rm) / bw, (HT - Tm - Bm) / bh)
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    WA, WB = 9.0, 74.0                       # 對數軸兩端，取關於 ω* 對稱的範圍
    lg = math.log10
    ax = Ax(cv, (lg(WA), lg(WB)), (0.030, 0.075), (0.0, 0.0, bw, bh))

    # frame 的刻度標籤是直接格式化資料座標，對數軸不能用；故自行畫刻度。
    ax.frame([], [0.030, 0.040, 0.050, 0.060, 0.070],
             xlabel="ω  (rad/s，對數軸)", ylabel="ζ", yfmt="{:.3f}")
    for wt in (10, 15, 20, 30, 40, 50, 70):
        ax.vline(lg(wt), 0.030, 0.075, "#E8ECF2", 1.1, dash=None)
        cv.text_px(cv.X(ax.X(lg(wt))), cv.Y(ax.Y(0.030)) + 17, "%d" % wt, 12.5, C["muted"])

    ws = [WA * (WB / WA) ** (i / 400) for i in range(401)]
    ax.curve([lg(w) for w in ws], [zeta(w) for w in ws], C["deform"], 3.8)
    ax.hline(ZETA, lg(WA), lg(WB), C["accent"], 1.5, dash="4 5")

    # ω* 的對稱軸：曲線在它左右互為鏡像
    ax.vline(lg(W_STAR), 0.030, 0.075, C["accent"], 2.0, dash=None)
    cv.text_px(cv.X(ax.X(lg(W_STAR))), cv.Y(ax.Y(0.0765)),
               "對稱軸 ω* = √(ω_{1}ω_{3}) = %.2f" % W_STAR, 13, C["accent"], weight="700")

    # 兩組鏡像點：(ω_1, ω_3) 與 (ω_2 的鏡像, ω_2)。等 ζ 用水平連線畫出來。
    # 曲線谷底很平（縱幅 0.045 只佔 336 px），所以谷底附近的每一段文字都
    # 必須各佔一個像素列、且左右錯開，否則一定疊在一起。
    for wl, wr, zv, colr in ((W1, W3, ZETA, C["deform"]),
                             (W2_MIRROR, W2, Z2, C["load"])):
        cv.line(ax.P(lg(wl), zv), ax.P(lg(wr), zv), colr, 1.6, dash="6 4")
        for w in (wl, wr):
            cv.dot(ax.P(lg(w), zv), 5.6, fill=colr, stroke="#FFFFFF", w=2.0)

    # ζ = 5% 的那一組：標籤放在對稱軸左側，避免壓到縱線
    cv.math_px(cv.X(ax.X(lg(W_STAR))) - 14, cv.Y(ax.Y(ZETA)) - 12,
               "ζ_{1} = ζ_{3} = 5%", 12.5, C["deform"], "end", weight="700")
    cv.math_px(cv.X(ax.X(lg(W1))), cv.Y(ax.Y(ZETA)) + 22, "ω_{1} = %.1f" % W1,
               12.5, C["text"], "middle", weight="700")
    cv.math_px(cv.X(ax.X(lg(W3))), cv.Y(ax.Y(ZETA)) + 22, "ω_{3} = %.1f" % W3,
               12.5, C["text"], "middle", weight="700")

    # ζ_2 的那一組：兩個標籤分別向左、向右展開，中間讓給對稱軸
    cv.math_px(cv.X(ax.X(lg(W2_MIRROR))) - 12, cv.Y(ax.Y(Z2)) + 26,
               "ω*^{2}/ω_{2} = %.1f" % W2_MIRROR, 12.5, C["load"], "end", weight="700")
    # 這一段含中文，必須走 text_px；math_px 的襯線數學字型沒有 CJK，
    # 中文不是變方框而是整段消失（本圖第一版就踩到）。
    cv.text_px(cv.X(ax.X(lg(W2))) + 12, cv.Y(ax.Y(Z2)) + 26,
               "ω_{2} = %.1f，與左邊同一個 ζ = %.2f%%" % (W2, 100 * Z2),
               12.5, C["load"], "start", weight="700")

    # 最低點與算術平均各佔一列，兩者不同高才看得出算術平均沒落在對稱軸上
    cv.dot(ax.P(lg(W_STAR), Z_MIN), 6.0, fill=C["accent"], stroke="#FFFFFF", w=2.0)
    cv.text_px(cv.X(ax.X(lg(W_STAR))), cv.Y(ax.Y(Z_MIN)) + 52,
               "最低 ζ = √(a_{0}a_{1}) = %.4f" % Z_MIN, 12.5, C["accent"], weight="700")
    cv.dot(ax.P(lg(W_ARITH), zeta(W_ARITH)), 5.2, fill=C["bmd"], stroke="#FFFFFF", w=1.8)
    cv.line(ax.P(lg(W_ARITH), zeta(W_ARITH)), ax.P(lg(W_ARITH), Z_MIN - 0.0088),
            C["bmd"], 1.2, dash="3 4")
    cv.text_px(cv.X(ax.X(lg(W_ARITH))), cv.Y(ax.Y(Z_MIN)) + 78,
               "算術平均 (ω_{1}+ω_{3})/2 = %.2f，不在對稱軸上" % W_ARITH,
               12.5, C["bmd"], weight="700")

    # ── 右側說明欄 ──
    bx = Lm + int(bw * sx) + 26
    cv.rect_px(bx, 96, 238, 156, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 122, "為什麼是幾何平均", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["把 ω 換成 ω*^{2}/ω 代進",
                           "ζ(ω) = a_{0}/(2ω) + a_{1}ω/2，",
                           "兩項恰好互換 → ζ 不變。",
                           "故 ζ(ω) = ζ(ω*^{2}/ω)，",
                           "對數軸上對稱於 ω*。"]):
        cv.text_px(bx + 16, 148 + i * 22, t, 12.5, "#1D4ED8", "start")

    cv.rect_px(bx, 270, 238, 130, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 296, "兩個平均差多少", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["幾何 √(ω_{1}ω_{3}) = %.2f" % W_STAR,
                           "算術 (ω_{1}+ω_{3})/2 = %.2f" % W_ARITH,
                           "ζ 差 %.5f（%.1f%%）" % (zeta(W_ARITH) - Z_MIN,
                                                  100 * (zeta(W_ARITH) / Z_MIN - 1))]):
        cv.text_px(bx + 16, 322 + i * 24, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 2 else "400")

    cv.text_px(WD / 2, HT - 34,
               "ω_{2} 與 %.1f 的 ζ 完全相同——等 ζ 的兩個頻率互為 ω* 的鏡像，"
               "這正是 ω* 只能是幾何平均的證據。" % W2_MIRROR, 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-logsym.svg")


if __name__ == "__main__":
    print(f"a_0 = {A0:.4f} 1/s   a_1 = {A1:.6e} s   ω* = {W_STAR:.2f}   "
          f"ζ_2 = {Z2:.4f}   ζ_min = {Z_MIN:.4f}")
    print(f"ω_2 鏡像 = {W2_MIRROR:.3f}   ζ(鏡像) = {zeta(W2_MIRROR):.6f} "
          f"（應等於 ζ_2 = {Z2:.6f}）")
    print(f"算術平均 = {W_ARITH:.3f}   ζ = {zeta(W_ARITH):.6f}")
    print(fig1_rayleigh())
    print(fig2_logsym())
