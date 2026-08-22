#!/usr/bin/env python3
"""
SD-2014-1 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2014-1.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2014-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2014-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定
M_KG = 1500.0                      # 各層質量（1F = 2F）
TN   = [0.20, 0.075]               # T_1、T_2（s）
XI   = 0.05
PHI  = [[0.62, 1.00], [-1.62, 1.00]]   # PHI[模態][樓層]，樓層順序 1F、2F
G    = 9.81
MASS = [M_KG, M_KG]
MTOT = sum(MASS)                   # 3000 kg —— 有效質量比的分母是它，不是 M_i


def sa(t):
    """§1 設計反應譜（5% 阻尼，S_a 為 g 的分數）"""
    if t <= 0.12:
        return 0.2 * (0.4 + t / 0.2)
    if t <= 0.6:
        return 0.2
    return 0.12 / t


# §4 題(一)：模態參數（L_i、M_i 皆含質量矩陣）
LI  = [sum(MASS[k] * PHI[j][k] for k in range(2)) for j in range(2)]     # 2430、−930 kg
MI  = [sum(MASS[k] * PHI[j][k] ** 2 for k in range(2)) for j in range(2)]  # 2076.6、5436.6
MEFF = [LI[j] ** 2 / MI[j] for j in range(2)]                            # 2843.5、159.1 kg
RHO = [m / MTOT for m in MEFF]                                           # 94.8%、5.3%
GAM = [LI[j] / MI[j] for j in range(2)]                                  # 1.1703、−0.1711

# §4 前置：反應譜讀值
SA = [sa(TN[0]), sa(TN[1])]                                              # 0.200、0.155

# §4 題(二)：基底剪力（tf）
VB = [MEFF[j] * SA[j] / 1000.0 for j in range(2)]
VB_SRSS = math.hypot(VB[0], VB[1])

# §4 題(三)：屋頂（2F）加速度（m/s²）
ACC = [PHI[j][1] * GAM[j] * SA[j] * G for j in range(2)]
ACC_SRSS = math.hypot(ACC[0], ACC[1])

# §5.1 正交性驗核
ORTHO = sum(MASS[k] * PHI[0][k] * PHI[1][k] for k in range(2))

# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。
MODE_COL = [C["deform"], C["load"]]


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪：兩層剪力樓房，兩層質量相同 → 總質量 2m = 3000 kg。
    攔錯：把有效振態質量比的分母寫成模態廣義質量 M_i（應為全結構總質量）。"""
    WD, HT = 1000, 452
    Lm, Rm, Tm, Bm = 178, 300, 74, 84
    xa, xb, ya, yb = -0.55, 1.60, -0.28, 2.34
    sx = min((WD - Lm - Rm) / (xb - xa), (HT - Tm - Bm) / (yb - ya))
    cv = Canvas(WD, HT, sx=sx, ox=Lm - xa * sx, oy=Bm - ya * sx, bg="#FFFFFF")

    cv.line((-0.55, 0), (1.60, 0), C["member"], 3.4)
    cv._hatch(cv.X(0.5), cv.Y(0.0), 1, 0, 0, 1, 0.92 * sx, C["member"], n=13)
    for xx in (0.0, 1.0):
        cv.line((xx, 0), (xx, 2), C["member"], 4.2, cap="butt")

    for i in range(2):
        y = i + 1
        cv.line((-0.10, y), (1.10, y), C["member"], 9, cap="butt")
        cv.rect_px(cv.X(0.30), cv.Y(y + 0.28), 0.40 * sx, 0.20 * sx,
                   "#DCE4EE", 6, C["member"], 2.2)
        cv.math((0.50, y + 0.18), "m", 17, C["text"], weight="700")
        cv.text_px(cv.X(-0.10) - 12, cv.Y(y), ["1F", "2F"][i], 14, C["muted"], "end",
                   weight="700")
        cv.arrow((1.16, y), (1.48, y), C["deform"], 3.2, 11)
        cv.math((1.48, y), "u_{%d}" % (i + 1), 18, C["deform"], "start", dx=9, weight="700")

    cv.arrow((0.14, -0.19), (0.60, -0.19), C["load"], 3.4, 12)
    cv.math((0.84, -0.19), "ü_{g}(t)", 17, C["load"], "start", dx=4, weight="700")

    bx = WD - Rm + 10
    cv.rect_px(bx, 74, 278, 152, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 100, "分母是「全結構總質量」", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["m = %.0f kg（每層相同）" % M_KG,
                           "M_{total} = 2m = %.0f kg" % MTOT,
                           "ρ_{i} = m_{i}* / M_{total}",
                           "不是 m_{i}* / M_{i} —— 後者會",
                           "讓 Σρ 湊不到 100%。"]):
        cv.text_px(bx + 16, 126 + i * 22, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i == 2 else "400")

    cv.rect_px(bx, 244, 278, 148, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 270, "兩個不同的「模態質量」", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["M_{i} = {φ}^{T}[m]{φ}    廣義質量",
                           "m_{i}* = L_{i}^{2}/M_{i}     有效質量",
                           "L_{i} = {φ}^{T}[m]{1}     激振係數",
                           "三者單位都是 kg，混用是",
                           "本題最常見的失分方式。"]):
        cv.text_px(bx + 14, 296 + i * 21, t, 12, "#9A3412", "start",
                   weight="700" if i == 4 else "400")

    cv.text_px(WD / 2, HT - 30,
               "T_{1} = %.2f s、T_{2} = %.3f s，各模態阻尼比 ξ = %.2f；兩層質量相同、"
               "以水平地表加速度為輸入。" % (TN[0], TN[1], XI), 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


# ══════════════════════════════════════════════════════════
def fig2_modes():
    """兩個振態形狀與有效振態質量比的完整推導鏈。
    攔錯：ρ_i 分母用錯（應為 M_total）；把 Γ_i 與 L_i 混用。"""
    PW, PH = 470, 512
    panels = []
    for j in range(2):
        cv = Canvas(PW, PH, sx=1, bg=None)
        cv.panel("Mode %d" % (j + 1), "T = %.3f s　｜　ξ = %.2f" % (TN[j], XI))
        x0, ytop_, hgt, amp = 158, 96, 196, 62
        peak = max(abs(v) for v in PHI[j])
        u = [0.0] + [PHI[j][k] / peak * amp for k in range(2)]
        ys = [ytop_ + hgt - i * hgt / 2 for i in range(3)]

        cv.parts.append(f'<line x1="{x0}" y1="{ys[0]:.1f}" x2="{x0}" y2="{ys[2]:.1f}" '
                        f'stroke="{C["ghost"]}" stroke-width="2.4" stroke-dasharray="6 5"/>')
        for i in range(3):
            cv.parts.append(f'<line x1="{x0 - 42}" y1="{ys[i]:.1f}" x2="{x0 + 42}" '
                            f'y2="{ys[i]:.1f}" stroke="{C["ghost"]}" stroke-width="1.6"/>')
        cv.text_px(x0 - 92, ys[0], "G", 12, C["muted"], "end")
        pts = " ".join(f"{x0 + u[i]:.1f},{ys[i]:.1f}" for i in range(3))
        cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{MODE_COL[j]}" '
                        f'stroke-width="4.2" stroke-linejoin="round"/>')
        for i in range(1, 3):
            cv.parts.append(f'<circle cx="{x0 + u[i]:.1f}" cy="{ys[i]:.1f}" r="6" '
                            f'fill="{MODE_COL[j]}" stroke="#FFFFFF" stroke-width="2"/>')
            cv.math_px(x0 + u[i], ys[i] - 19, "%.2f" % PHI[j][i - 1], 13,
                       MODE_COL[j], "middle", weight="700")
            cv.text_px(x0 - 92, ys[i], ["1F", "2F"][i - 1], 12, C["muted"], "end")

        # 節點數：第 n 振態應有 n−1 個（由正負號變化算出）
        nodes = sum(1 for i in range(2) if u[i] * u[i + 1] < 0)
        cv.text_px(x0, PH - 176, "節點數 = %d（應為 n−1 = %d）✓" % (nodes, j), 12.5,
                   C["accent"], weight="700")

        # 推導鏈（右半格）
        rx = 268
        cv.rect_px(rx, 104, PW - rx - 22, 188, "#FFFFFF", 10, C["border"], 1.2)
        for i, t in enumerate(["L_{%d} = m Σφ = %.0f kg" % (j + 1, LI[j]),
                               "M_{%d} = m Σφ^{2} = %.1f kg" % (j + 1, MI[j]),
                               "m*_{%d} = L^{2}/M = %.1f kg" % (j + 1, MEFF[j]),
                               "Γ_{%d} = L/M = %.4f" % (j + 1, GAM[j]),
                               "S_{a}(T_{%d}) = %.3f" % (j + 1, SA[j])]):
            cv.text_px(rx + 14, 132 + i * 32, t, 12.5, C["text"], "start")
        cv.rect_px(rx, 306, PW - rx - 22, 52, "#EEF4FF", 10, "#C7D9F5", 1.2)
        cv.text_px(rx + 14, 332, "ρ_{%d} = m*/M_{total} = %.1f%%" % (j + 1, 100 * RHO[j]),
                   13.5, "#1D4ED8", "start", weight="700")

        cv.text_px(PW / 2, PH - 118, "基底剪力貢獻 V_{b,%d} = m*·S_{a} = %.4f tf"
                   % (j + 1, VB[j]), 12.5, C["text"], weight="700")
        cv.text_px(PW / 2, PH - 92, "屋頂加速度貢獻 = φ_{2}·Γ·S_{a}·g = %+.3f m/s^{2}"
                   % ACC[j], 12.5, C["text"], weight="700")
        panels.append(cv)

    compose(panels, cols=2,
            title="兩個振態：有效振態質量比 %.1f%% ／ %.1f%%" % (100 * RHO[0], 100 * RHO[1]),
            sub="Σρ = %.1f%%（規範要求累積 ≥ 90%%，本題僅 Mode 1 即已達標）；"
                "正交性驗核 φ_1 · [m] · φ_2 = %.1f kg，僅 M_1 的 %.2f%% ≈ 0"
                % (100 * sum(RHO), ORTHO, abs(100 * ORTHO / MI[0])),
            note="SRSS 基底剪力 %.3f tf、屋頂加速度 %.2f m/s²——"
                 "兩者都被 Mode 1 主導，與 ρ_1 = %.1f%% 一致。"
                 % (VB_SRSS, ACC_SRSS, 100 * RHO[0]),
            path=f"{OUT}/{TAG}-fig-2-modes.svg")
    return f"{OUT}/{TAG}-fig-2-modes.svg"


# ══════════════════════════════════════════════════════════
def fig3_spectrum():
    """三段式設計反應譜與兩個週期的落點。
    攔錯：T_2 = 0.075 s 落在「上升段」，必須代公式得 0.155，不可直接用平台值 0.2。"""
    WD, HT = 1010, 578
    Lm, Rm, Tm, Bm = 96, 268, 92, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 1.5), (0.0, 0.26), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.12, 0.3, 0.6, 0.9, 1.2, 1.5], [0, 0.05, 0.10, 0.15, 0.20, 0.25],
             xlabel="T  (s)", ylabel="S_{a}  (g 的分數)", xfmt="{:g}", yfmt="{:.2f}")

    ts = [i * 1.5 / 600 for i in range(601)]
    ax.area(ts, [sa(t) for t in ts], C["fill_m"])
    ax.curve(ts, [sa(t) for t in ts], C["bmd"], 3.4)

    # 分段界線（0.12 與 0.6）——由 sa() 的分段點決定，不是畫到那裡剛好好看
    for tb in (0.12, 0.6):
        ax.vline(tb, 0.0, 0.24, C["muted"], 1.5)
        ax.at(tb, 0.245, "T = %g" % tb, C["muted"], size=12)
    ax.at(0.055, 0.225, "上升段", C["accent"], size=13)
    ax.at(0.44, 0.238, "平台段", C["accent"], size=13)
    ax.at(1.05, 0.225, "雙曲線段 0.12/T", C["accent"], size=13)

    for j in (1, 0):
        ax.vline(TN[j], 0.0, SA[j], C["muted"], 1.4)
        ax.hline(SA[j], 0.0, TN[j], C["muted"], 1.3)
    ax.mark(TN[1], SA[1], "T_{2} = %.3f s\nS_{a} = %.3f" % (TN[1], SA[1]),
            MODE_COL[1], dx=14, dy=30, size=13)
    ax.mark(TN[0], SA[0], "T_{1} = %.2f s\nS_{a} = %.3f" % (TN[0], SA[0]),
            MODE_COL[0], dx=14, dy=-40, size=13)

    # 誤用平台值的落點
    ax.mark(TN[1], 0.2, "誤用平台值 0.2", C["load"], dx=-13, dy=-15, size=12.5, anchor="end")
    cv.line(ax.P(TN[1], SA[1]), ax.P(TN[1], 0.2), C["load"], 2.0, dash="4 4")

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 88, 232, 190, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 114, "T_{2} 在哪一段？", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["T_{2} = %.3f ≤ 0.12 → 上升段" % TN[1],
                           "S_{a} = 0.2(0.4 + T/0.2)",
                           "    = 0.2 × 0.775 = %.3f" % SA[1],
                           "誤用 0.2 會把 Mode 2 的",
                           "基底剪力高估 %.0f%%。" % (100 * (0.2 / SA[1] - 1)),
                           "所幸 ρ_{2} 僅 %.1f%%，SRSS" % (100 * RHO[1]),
                           "結果幾乎不變。"]):
        cv.text_px(bx + 14, 142 + i * 21, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 2 else "400")

    cv.rect_px(bx, 296, 232, 128, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 322, "分段點連續性檢核", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["T = 0.12：0.2(0.4+0.6) = %.2f ✓" % sa(0.12),
                           "T = 0.60：0.12/0.6 = %.2f ✓" % sa(0.60),
                           "三段接得上 → 讀法正確。"]):
        cv.text_px(bx + 14, 350 + i * 22, t, 12, "#1D4ED8", "start",
                   weight="700" if i == 2 else "400")

    cv.text_px(WD / 2, HT - 30,
               "第二模態週期短，落在譜的上升段而不是平台——"
               "把兩個週期畫在同一條譜上，這件事就無法被忽略。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-spectrum.svg")


if __name__ == "__main__":
    for j in range(2):
        print(f"Mode {j+1}: L={LI[j]:.1f} kg  M={MI[j]:.1f} kg  m*={MEFF[j]:.1f} kg  "
              f"ρ={100*RHO[j]:.1f}%  Γ={GAM[j]:.4f}  S_a={SA[j]:.3f}  "
              f"V_b={VB[j]:.5f} tf  a_roof={ACC[j]:+.3f} m/s²")
    print(f"Σρ = {100*sum(RHO):.1f}%   正交性 = {ORTHO:.2f}")
    print(f"V_b SRSS = {VB_SRSS:.4f} tf   屋頂加速度 SRSS = {ACC_SRSS:.3f} m/s²")
    for f in (fig1_frame(), fig2_modes(), fig3_spectrum()):
        print(f)
