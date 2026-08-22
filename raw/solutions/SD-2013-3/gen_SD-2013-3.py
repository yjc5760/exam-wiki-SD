#!/usr/bin/env python3
"""
SD-2013-3 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2013-3.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2013-3"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2013-3.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §4 Step 1：形函數 = 均佈靜載重下懸臂梁撓度（省略常數 w/24EI），L = 1
#            φ(ξ) = 6ξ² − 4ξ³ + ξ⁴
# §4 Step 2–4：三個積分（以 L = 1 表示）
NUM     = 144 / 5              # ∫EI[φ'']² dx  = 144EI L⁵/5
DEN_M   = 104 / 45             # ∫m φ²   dx    = 104 m L⁹/45
PHI_HALF = 17 / 16             # φ(L/2) = 17L⁴/16
DEN_W   = PHI_HALF ** 2        # (W/g)[φ(L/2)]² 的係數 = 289/256
assert abs(DEN_W - 289 / 256) < 1e-12

# §4 極限驗核：兩端極限的 Rayleigh 值與精確值
W2_RAY_BEAM  = NUM / DEN_M                       # W → 0：12.46 EI/(mL⁴)
LAM1         = 1.8751040687119611                # 懸臂梁第一振態特徵值 λ_1
W2_EXA_BEAM  = LAM1 ** 4                         # 精確：12.36 EI/(mL⁴)
W2_RAY_MASS  = NUM / DEN_W                       # mL → 0：25.51 EIg/(WL³)
W2_EXA_MASS  = 3.0 / 0.5 ** 3                    # 精確：k = 3EI/(L/2)³ → 24 EIg/(WL³)


def phi(xi):
    """形函數（未正規化）"""
    return 6 * xi ** 2 - 4 * xi ** 3 + xi ** 4


def phi_hat(xi):
    """正規化為自由端 = 1（φ(1) = 3）"""
    return phi(xi) / phi(1.0)


SIG = ((math.cosh(LAM1) + math.cos(LAM1)) / (math.sinh(LAM1) + math.sin(LAM1)))


def psi(xi):
    """懸臂梁精確第一振態"""
    a = LAM1 * xi
    return (math.cosh(a) - math.cos(a)) - SIG * (math.sinh(a) - math.sin(a))


def psi_hat(xi):
    return psi(xi) / psi(1.0)


# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。


# ══════════════════════════════════════════════════════════
def fig1_beam():
    """題目重繪：把「分佈質量」與「集中重量 W」分開標清楚。
    攔錯：把 W 當成質量直接代入（應為 W/g）；把集中質量誤放在自由端。"""
    WD, HT = 1000, 384
    Lm, Rm, Tm, Bm = 112, 244, 112, 142
    xa, xb, ya, yb = -0.06, 1.06, -0.02, 0.26
    sx = min((WD - Lm - Rm) / (xb - xa), (HT - Tm - Bm) / (yb - ya))
    cv = Canvas(WD, HT, sx=sx, ox=Lm - xa * sx, oy=Bm - ya * sx, bg="#FFFFFF")

    # 梁與固定端
    cv.line((0, 0), (1, 0), C["member"], 9, cap="butt")
    cv.fixed_support((0, 0), ang=90, size=34)

    # 中點集中重量 W（質量 = W/g）
    bw_, bh_ = 0.13, 0.115
    cv.rect_px(cv.X(0.5 - bw_ / 2), cv.Y(bh_ + 0.028), bw_ * sx, bh_ * sx,
               "#F3D9D2", 6, C["load"], 2.6)
    cv.line((0.5, 0.028), (0.5, 0.0), C["load"], 2.6)
    cv.math((0.5, bh_ / 2 + 0.028), "W", 20, C["load"], weight="700")
    cv.text_px(cv.X(0.5), cv.Y(bh_ + 0.028) - 16, "重量（質量 = W/g）", 13, C["load"],
               weight="700")

    # 分佈質量與 EI
    cv.text_px(cv.X(0.80), cv.Y(0.0) + 30, "均佈質量 m（每單位長度）、EI 均勻",
               13.5, C["muted"], "middle")

    # 尺寸
    cv.dim((0, 0), (0.5, 0), "L/2", off=66, label_off=16)
    cv.dim((0.5, 0), (1, 0), "L/2", off=66, label_off=16)

    # 邊界條件
    cv.dot((0, 0), 5.4, fill=C["member"])
    cv.dot((1, 0), 5.4, fill=C["member"])
    cv.text_px(cv.X(0.0), cv.Y(0.0) - 74, "固定端", 13, C["text"], weight="700")
    cv.math_px(cv.X(0.0), cv.Y(0.0) - 54, "φ(0) = φ'(0) = 0", 13, C["text"])
    cv.text_px(cv.X(1.0), cv.Y(0.0) - 74, "自由端", 13, C["text"], weight="700")
    cv.math_px(cv.X(1.0), cv.Y(0.0) - 54, "M = V = 0", 13, C["text"])

    bx = WD - Rm + 10
    cv.rect_px(bx, 78, 218, 190, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 104, "動能分母有兩項", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["分佈質量：∫m φ^{2} dx",
                           "集中質量：(W/g)[φ(L/2)]^{2}",
                           "漏掉第二項是本題最常見",
                           "的失分點；把 W 直接當質量",
                           "用（忘了除以 g）是第二常見。",
                           "φ(L/2) = %d/%d 決定第二項的" % (17, 16),
                           "權重，位置錯 → 權重全錯。"]):
        cv.text_px(bx + 14, 132 + i * 22, t, 12.5, "#9A3412", "start",
                   weight="700" if i < 2 else "400")

    cv.text_px(WD / 2, HT - 30,
               "集中重量在 L/2 而不是自由端——這決定了它在 Rayleigh 商裡的權重只有 φ(L/2)^{2}，"
               "不是 φ(L)^{2}。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-beam.svg")


# ══════════════════════════════════════════════════════════
def fig2_shape():
    """形函數與精確第一振態對照，並標出 φ(L/2) 這個決定集中質量權重的點。
    攔錯：選了不滿足幾何邊界條件的形函數；或誤讀 φ(L/2) 的值。"""
    WD, HT = 1010, 578
    Lm, Rm, Tm, Bm = 96, 262, 92, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 1.0), (0.0, 1.08), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.25, 0.5, 0.75, 1.0], [0, 0.25, 0.5, 0.75, 1.0],
             xlabel="ξ = x/L", ylabel="正規化撓度  φ(ξ)/φ(L)", xfmt="{:.2f}", yfmt="{:.2f}")

    xs = [i / 300 for i in range(301)]
    ax.curve(xs, [psi_hat(x) for x in xs], C["muted"], 2.6, dash="7 5")
    ax.curve(xs, [phi_hat(x) for x in xs], C["deform"], 3.8)

    ax.vline(0.5, 0.0, phi_hat(0.5), C["accent"], 1.5)
    ax.hline(phi_hat(0.5), 0.0, 0.5, C["accent"], 1.5)
    ax.mark(0.5, phi_hat(0.5),
            "φ(L/2)/φ(L) = %.4f\n( φ(L/2) = 17L^{4}/16 )" % phi_hat(0.5),
            C["accent"], dx=-14, dy=-34, size=13, anchor="end")
    ax.at(0.545, 0.055, "集中重量 W 所在位置", C["accent"], size=12.5, anchor="start")

    cv.legend(cv.X(ax.X(0.045)), cv.Y(ax.Y(0.99)),
              [(C["deform"], "UDL 靜力撓度形函數（本題採用）"),
               (C["muted"], "精確第一振態（λ_{1} = 1.8751）")], size=12.5, gap=22)

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 90, 226, 172, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 116, "四個邊界條件全部滿足", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["φ(0) = 0                幾何 ✓",
                           "φ'(0) = 0               幾何 ✓",
                           "φ''(L) = 12(L−L)^{2} = 0   力學 ✓",
                           "φ'''(L) = −24(L−L) = 0     力學 ✓",
                           "幾何 BC 是必要條件，",
                           "力學 BC 滿足則精度更高。"]):
        cv.text_px(bx + 14, 142 + i * 21, t, 11.5, "#1D4ED8", "start")

    cv.rect_px(bx, 280, 226, 148, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 306, "兩條線幾乎重合的後果", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["分佈質量主導時，Rayleigh",
                           "誤差僅 %.1f%%（見 fig-3）；" % (100 * (W2_RAY_BEAM / W2_EXA_BEAM - 1)),
                           "但集中質量主導時，真實",
                           "振態會偏離 UDL 曲線，",
                           "誤差擴大到 %.1f%%。" % (100 * (W2_RAY_MASS / W2_EXA_MASS - 1))]):
        cv.text_px(bx + 14, 332 + i * 21, t, 12, "#9A3412", "start")

    cv.text_px(WD / 2, HT - 30,
               "形函數不必是真的振態，但必須滿足幾何邊界條件——"
               "兩條線的貼合程度，直接就是 Rayleigh 誤差的大小。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-shape.svg")


# ══════════════════════════════════════════════════════════
def fig3_bounds():
    """兩個極限的上界驗核：Rayleigh 值必定落在精確值的右側。
    攔錯：算出的 ω 低於精確值卻沒察覺（Rayleigh 商不可能給下界）。"""
    WD, HT = 1010, 452
    cv = Canvas(WD, HT, sx=1, bg="#FFFFFF")
    cv.text_px(WD / 2, 40, "Rayleigh 商是上界：ω_{Rayleigh} ≥ ω_{exact}", 17.5,
               C["text"], weight="700")
    cv.text_px(WD / 2, 66, "橫軸為「相對精確值的比值」，兩列各自以自己的精確值為 1.00", 13,
               C["muted"])

    rows = [("極限 W → 0（純分佈質量）",
             "ω^{2} = 144EI/5L^{3} ÷ 104mL/45",
             W2_RAY_BEAM, W2_EXA_BEAM, "EI/(mL^{4})"),
            ("極限 mL → 0（純集中質量 W）",
             "ω^{2} = 144EI/5L^{3} ÷ 289W/256g",
             W2_RAY_MASS, W2_EXA_MASS, "EIg/(WL^{3})")]

    x0, x1 = 372, 902                    # 軸的像素範圍
    va, vb = 0.955, 1.095                # 比值範圍
    def PX(v): return x0 + (v - va) / (vb - va) * (x1 - x0)

    for i, (name, expr, ray, exa, unit) in enumerate(rows):
        y = 150 + i * 152
        cv.text_px(58, y - 26, name, 14, C["text"], "start", weight="700")
        cv.text_px(58, y + 2, expr, 12.5, C["muted"], "start")
        cv.text_px(58, y + 26, "誤差 +%.2f%%（偏高＝上界）" % (100 * (ray / exa - 1)),
                   12.5, C["accent"], "start", weight="700")

        # 「不可能區」：比值 ＜ 1
        cv.rect_px(PX(va), y - 30, PX(1.0) - PX(va), 60, "#FBEAE6", 6)
        cv.line_px = None
        cv.parts.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" '
                        f'stroke="{C["muted"]}" stroke-width="2"/>')
        for v in (0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.08):
            cv.parts.append(f'<line x1="{PX(v):.1f}" y1="{y-6}" x2="{PX(v):.1f}" y2="{y+6}" '
                            f'stroke="{C["muted"]}" stroke-width="1.4"/>')
            cv.text_px(PX(v), y + 24, "%.2f" % v, 11.5, C["muted"])

        cv.parts.append(f'<line x1="{PX(1.0):.1f}" y1="{y-34}" x2="{PX(1.0):.1f}" y2="{y+12}" '
                        f'stroke="{C["bmd"]}" stroke-width="2.4"/>')
        cv.text_px(PX(1.0), y - 46, "精確 %.2f" % exa, 13, C["bmd"], weight="700")
        cv.math_px(PX(1.0), y - 66, unit, 12, C["bmd"])

        cv.parts.append(f'<circle cx="{PX(ray / exa):.1f}" cy="{y}" r="8" fill="{C["load"]}" '
                        f'stroke="#FFFFFF" stroke-width="2.4"/>')
        cv.text_px(PX(ray / exa), y + 46, "Rayleigh %.2f" % ray, 13, C["load"], weight="700")

        cv.text_px(PX(0.9775), y - 16, "Rayleigh 不可能落在此側", 12, "#B5504A")

    cv.text_px(WD / 2, HT - 38,
               "假設形函數＝對系統多加了約束，等效勁度只會變大，故頻率必定偏高。",
               13.5, C["muted"])
    cv.text_px(WD / 2, HT - 16,
               "分佈質量主導時 UDL 形函數幾乎就是真實振態（+%.2f%%）；"
               "集中質量主導時偏離變大（+%.2f%%）。"
               % (100 * (W2_RAY_BEAM / W2_EXA_BEAM - 1), 100 * (W2_RAY_MASS / W2_EXA_MASS - 1)),
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-bounds.svg")


if __name__ == "__main__":
    print(f"φ(L/2) = {PHI_HALF}  φ(L) = {phi(1.0)}  φ(L/2)/φ(L) = {phi_hat(0.5):.5f}")
    print(f"ψ_exact(0.5)/ψ(1) = {psi_hat(0.5):.5f}")
    print(f"W→0 : Rayleigh {W2_RAY_BEAM:.4f} vs 精確 {W2_EXA_BEAM:.4f}  "
          f"(+{100*(W2_RAY_BEAM/W2_EXA_BEAM-1):.2f}%)")
    print(f"mL→0: Rayleigh {W2_RAY_MASS:.4f} vs 精確 {W2_EXA_MASS:.4f}  "
          f"(+{100*(W2_RAY_MASS/W2_EXA_MASS-1):.2f}%)")
    for f in (fig1_beam(), fig2_shape(), fig3_bounds()):
        print(f)
