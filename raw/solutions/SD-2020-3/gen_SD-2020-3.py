#!/usr/bin/env python3
"""
SD-2020-3 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2020-3.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2020-3"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2020-3.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 題目給定：五個振態頻率（Hz）與質量正規化振態（列＝樓層 1F→5F，行＝振態）
FHZ = [0.285, 0.831, 1.31, 1.682, 1.919]
XI = 0.03
NSTORY = 5

# 考卷印出值（答案即依此作答）
PHI_P = [[0.160, -0.455, 0.597, 0.549, 0.326],     # 1F
         [0.326, -0.597, 0.170, -0.455, -0.549],   # 2F
         [0.455, -0.326, -0.549, -0.170, 0.597],   # 3F
         [0.549, 0.170, -0.326, 0.597, -0.455],    # 4F
         [0.597, 0.549, 0.455, 0.326, 0.170]]      # 5F

# §5「考卷原表兩處印刷誤植」——更正後的版本
PHI_C = [row[:] for row in PHI_P]
PHI_C[0][0] = 0.170        # 振態1 / 1F：0.160 → 0.170（該行 Σφ² 才等於 1）
PHI_C[4][3] = -0.326       # 振態4 / 5F：+0.326 → −0.326（正交性與節點數才對）


def col(P, i):
    return [P[f][i] for f in range(NSTORY)]


# §1 題目給定：譜位移分段函數（表中的 ω 其實是頻率 f，單位 Hz，不要乘 2π）
def sd(f):
    if f < 0.1:
        return 0.01
    if f <= 0.5:
        return 0.01 + 0.15 * (f - 0.1)
    if f <= 1.5:
        return 0.07
    return 0.105 / f


# §4 Step 1：質量正規化 → M_i* = 1，故 Γ_i = L_i，ρ_i = L_i²/5
NORM_P = [sum(v ** 2 for v in col(PHI_P, i)) for i in range(5)]
NORM_C = [sum(v ** 2 for v in col(PHI_C, i)) for i in range(5)]
L_P = [sum(col(PHI_P, i)) for i in range(5)]
L_C = [sum(col(PHI_C, i)) for i in range(5)]
RHO_P = [l ** 2 / NSTORY for l in L_P]
RHO_C = [l ** 2 / NSTORY for l in L_C]
CUM_P = [sum(RHO_P[:i + 1]) for i in range(5)]
NMODE = next(i + 1 for i in range(5) if CUM_P[i] >= 0.95)     # 累積 ≥ 95% 的最少振態數

# §4 Step 2–3
SD_ = [sd(f) for f in FHZ]
U5 = [L_P[i] * PHI_P[4][i] * SD_[i] for i in range(5)]        # 頂樓各振態位移
U5_SRSS = math.hypot(U5[0], U5[1])                            # §4 Step 4：只採 2 個振態


def sjk(r, xj=XI, xk=XI):
    """§3.5 CQC 相關係數，r = ω_k/ω_j"""
    num = 8 * math.sqrt(xj * xk) * (xj + r * xk) * r ** 1.5
    den = (1 - r ** 2) ** 2 + 4 * xj * xk * r * (1 + r ** 2) + 4 * (xj ** 2 + xk ** 2) * r ** 2
    return num / den


R12 = FHZ[1] / FHZ[0]                                          # = 2.916
S12 = sjk(R12)                                                 # = 0.00249
U5_CQC = math.sqrt(U5[0] ** 2 + 2 * S12 * U5[0] * U5[1] + U5[1] ** 2)

# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。
MC = [C["deform"], C["load"], C["bmd"], C["accent"], C["sfd"]]


# ══════════════════════════════════════════════════════════
def fig1_modes():
    """五個振態形狀，以節點數（零位移點）逐一檢核。
    攔錯：第 n 振態應有 n−1 個節點。振態 4 依考卷印出值只數得到 2 個，
    把 5F 的符號改為負號後恰為 3 個——考卷原表的誤植就是這樣被抓出來的。"""
    PW, PH = 288, 486
    panels = []
    for i in range(5):
        cv = Canvas(PW, PH, sx=1, bg=None)
        cv.panel("振態 %d" % (i + 1), "f = %.3f Hz" % FHZ[i])
        x0, ytop_, hgt, amp = PW / 2, 92, 250, 62
        vp, vc = col(PHI_P, i), col(PHI_C, i)
        ys = [ytop_ + hgt - k * hgt / 5 for k in range(6)]

        cv.parts.append(f'<line x1="{x0}" y1="{ys[0]:.1f}" x2="{x0}" y2="{ys[5]:.1f}" '
                        f'stroke="{C["ghost"]}" stroke-width="2.2" stroke-dasharray="6 5"/>')
        for k in range(6):
            cv.parts.append(f'<line x1="{x0 - 40}" y1="{ys[k]:.1f}" x2="{x0 + 40}" '
                            f'y2="{ys[k]:.1f}" stroke="{C["ghost"]}" stroke-width="1.4"/>')
            cv.text_px(x0 - 78, ys[k], ["G", "1F", "2F", "3F", "4F", "5F"][k],
                       11, C["muted"], "end")

        def draw(vals, color, w, dash=None, dots=True):
            u = [0.0] + [v / 0.597 * amp for v in vals]
            pts = " ".join(f"{x0 + u[k]:.1f},{ys[k]:.1f}" for k in range(6))
            d = f' stroke-dasharray="{dash}"' if dash else ""
            cv.parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                            f'stroke-width="{w}" stroke-linejoin="round"{d}/>')
            if dots:
                for k in range(1, 6):
                    cv.parts.append(f'<circle cx="{x0 + u[k]:.1f}" cy="{ys[k]:.1f}" r="4.6" '
                                    f'fill="{color}" stroke="#FFFFFF" stroke-width="1.6"/>')
            return u

        # 節點數：由相鄰樓層的正負號變化算出（含地面端），不是目測
        def count_nodes(u):
            return sum(1 for k in range(5) if u[k] * u[k + 1] < 0)

        changed = vp != vc
        if changed:
            up = draw(vp, C["muted"], 2.2, dash="7 5", dots=False)
        uc = draw(vc, MC[i], 4.0)

        n_c, n_p = count_nodes(uc), count_nodes(up) if changed else count_nodes(uc)
        if n_p != n_c:            # 振態 4：節點數才是抓到誤植的那道檢核
            cv.text_px(PW / 2, PH - 98, "印出值：節點 %d 個 ×" % n_p, 12.5,
                       C["load"], weight="700")
            cv.text_px(PW / 2, PH - 76, "更正後：節點 %d 個 ✓（= n−1）" % n_c, 12.5,
                       C["accent"], weight="700")
        elif changed:             # 振態 1：Σφ² 才是抓到誤植的那道檢核
            cv.text_px(PW / 2, PH - 98, "印出值：Σφ^{2} = %.4f ×" % NORM_P[i], 12.5,
                       C["load"], weight="700")
            cv.text_px(PW / 2, PH - 76, "更正後：Σφ^{2} = %.4f ✓" % NORM_C[i], 12.5,
                       C["accent"], weight="700")
        else:
            cv.text_px(PW / 2, PH - 98, "節點數 = %d（應為 n−1 = %d）✓" % (n_c, i),
                       12.5, C["accent"], weight="700")
            cv.text_px(PW / 2, PH - 76, "Σφ^{2} = %.4f ✓" % NORM_C[i], 12.5,
                       C["muted"], weight="700")
        cv.text_px(PW / 2, PH - 50, "L = %+.3f" % L_C[i], 12, C["muted"])
        cv.text_px(PW / 2, PH - 28, "有效質量比 %.1f%%" % (100 * RHO_C[i]), 12.5,
                   C["text"], weight="700")
        panels.append(cv)

    compose(panels, cols=5,
            title="五個振態：節點數把考卷原表的兩處誤植揪出來",
            sub="灰虛線＝考卷印出值，實線＝依正交性更正後（振態1/1F 0.160→0.170，"
                "振態4/5F +0.326→−0.326）",
            note="第 n 振態必有 n−1 個節點——振態 4 依印出值只數得到 2 個，改回負號才是 3 個。"
                 "本題只用振態 1、2，答案不受影響。",
            path=f"{OUT}/{TAG}-fig-1-modes.svg")
    return f"{OUT}/{TAG}-fig-1-modes.svg"


# ══════════════════════════════════════════════════════════
def fig2_mass():
    """有效質量比與累積曲線：回答「最少需幾個振態」。
    攔錯：ρ_i 的分母是全結構總質量（此處 = 5，因質量正規化），不是模態質量 M_i*；
    另外，振態 4 依印出值算出 ρ = 14.4% ＞ ρ_2，物理上不可能，是誤植的第二個證據。"""
    WD, HT = 1010, 546
    Lm, Rm, Tm, Bm = 100, 262, 100, 108
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.4, 5.6), (0.0, 1.25), (0.0, 0.0, bw, bh))
    ax.frame([1, 2, 3, 4, 5], [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2],
             xlabel="振態序號", ylabel="有效質量比", xfmt="{:g}", yfmt="{:.0%}")

    hw = 0.30
    for i in range(5):
        for val, colr, off, opa in ((RHO_P[i], MC[i], 0.0, 1.0),):
            cv.polygon([ax.P(i + 1 - hw + off, 0.0), ax.P(i + 1 + hw + off, 0.0),
                        ax.P(i + 1 + hw + off, val), ax.P(i + 1 - hw + off, val)],
                       colr, "#FFFFFF", 1.4)
        ax.at(i + 1, RHO_P[i], "%.2f%%" % (100 * RHO_P[i]), MC[i], dy=-15, size=12.5)

    # 累積曲線與 95% 門檻
    ax.curve([i + 1 for i in range(5)], CUM_P, C["accent"], 3.2)
    for i in range(5):
        cv.dot(ax.P(i + 1, CUM_P[i]), 5.6, fill=C["accent"], stroke="#FFFFFF", w=2.0)
    ax.hline(0.95, 0.4, 5.6, C["load"], 2.0, dash="6 5")
    ax.hline(1.00, 0.4, 5.6, C["muted"], 1.5, dash="4 4")
    ax.at(5.45, 0.905, "95% 門檻", C["load"], size=12.5, anchor="end")
    ax.at(2.0, CUM_P[1], "累積 %.2f%% ≥ 95%%" % (100 * CUM_P[1]), C["accent"],
          dx=14, dy=26, size=13, anchor="start")
    cv.line(ax.P(4.0, 0.155), ax.P(4.0, 0.40), C["load"], 1.6, dash="4 4")
    ax.at(4.0, 0.44, "依印出值 %.2f%% ＞ ρ_{2}\n物理上不可能" % (100 * RHO_P[3]),
          C["load"], dy=0, size=12.5)
    ax.at(5.0, CUM_P[4], "Σρ = %.1f%% ＞ 100%%\n同樣指向誤植" % (100 * CUM_P[4]),
          C["load"], dx=-14, dy=-8, size=12.5, anchor="end")

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 96, 226, 174, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 122, "質量正規化的三個好處", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["Σφ^{2} = 1  →  M_{i}* = 1",
                           "Γ_{i} = L_{i}/M_{i}* = L_{i}",
                           "ρ_{i} = L_{i}^{2}/M_{total} = L_{i}^{2}/5",
                           "先驗算 Σφ^{2} 是否為 1，",
                           "再決定要不要除以 M_{i}*。"]):
        cv.text_px(bx + 14, 150 + i * 23, t, 12.5, "#1D4ED8", "start",
                   weight="700" if i == 2 else "400")

    cv.rect_px(bx, 288, 226, 148, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 314, "答案：採 %d 個振態" % NMODE, 13.5, "#9A3412",
               "start", weight="700")
    for i, t in enumerate(["ρ_{1} = %.2f%%" % (100 * RHO_P[0]),
                           "ρ_{2} = %.2f%%" % (100 * RHO_P[1]),
                           "累積 = %.2f%% ≥ 95%% ✓" % (100 * CUM_P[1]),
                           "振態 3 以上不必納入。"]):
        cv.text_px(bx + 14, 342 + i * 23, t, 12.5, "#9A3412", "start",
                   weight="700" if i == 2 else "400")

    cv.text_px(WD / 2, HT - 32,
               "長條＝各振態有效質量比（依考卷印出值），橘線＝累積值；"
               "累積曲線一跨過 95%，振態數就定下來了。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-mass.svg")


# ══════════════════════════════════════════════════════════
def fig3_sd():
    """譜位移分段曲線與兩個振態頻率的落點。
    攔錯：表中的 ω 其實是 Hz，不要先乘 2π——分段點的連續性就是判別依據。"""
    WD, HT = 1010, 570
    Lm, Rm, Tm, Bm = 100, 268, 92, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (0.0, 2.5), (0.0, 0.09), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.1, 0.5, 1.0, 1.5, 2.0, 2.5], [0, 0.02, 0.04, 0.06, 0.08],
             xlabel="頻率 f  (Hz)", ylabel="譜位移 S_{d}  (m)", xfmt="{:g}", yfmt="{:.2f}")

    fs = [i * 2.5 / 1000 for i in range(1001)]
    ax.area(fs, [sd(f) for f in fs], C["fill_m"])
    ax.curve(fs, [sd(f) for f in fs], C["bmd"], 3.4)

    for fb in (0.1, 0.5, 1.5):
        ax.vline(fb, 0.0, 0.082, C["muted"], 1.4)
        ax.at(fb, 0.086, "f = %g" % fb, C["muted"], size=12)

    for i in (1, 0):
        ax.vline(FHZ[i], 0.0, SD_[i], C["muted"], 1.4)
        ax.hline(SD_[i], 0.0, FHZ[i], C["muted"], 1.3)
    ax.mark(FHZ[0], SD_[0], "振態 1  f = %.3f Hz\nS_{d} = %.5f m" % (FHZ[0], SD_[0]),
            MC[0], dx=13, dy=-34, size=13)
    ax.mark(FHZ[1], SD_[1], "振態 2  f = %.3f Hz\nS_{d} = %.2f m" % (FHZ[1], SD_[1]),
            MC[1], dx=13, dy=-34, size=13)

    # 若誤把表中的 ω 當 rad/s（先乘 2π 再查表）會落到哪裡
    f_wrong = 2 * math.pi * FHZ[0]
    ax.mark(f_wrong, sd(f_wrong), "誤乘 2π：f = %.2f Hz → S_{d} = %.4f m"
            % (f_wrong, sd(f_wrong)), C["load"], dx=-13, dy=22, size=12.5, anchor="end")

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 90, 234, 168, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 116, "表中的 ω 是 Hz，不是 rad/s", 13, "#9A3412",
               "start", weight="700")
    for i, t in enumerate(["判別依據＝分段點必須連續：",
                           "f = 0.5：0.01+0.15(0.4) = %.2f ✓" % sd(0.5),
                           "f = 1.5：0.105/1.5 = %.2f ✓" % sd(1.5),
                           "三段完全接得上 → 直接用",
                           "表格上方的振態頻率代入。"]):
        cv.text_px(bx + 14, 144 + i * 22, t, 12, "#9A3412", "start",
                   weight="700" if i == 3 else "400")

    cv.rect_px(bx, 276, 234, 150, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 302, "頂樓各振態位移", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["u_{5,1} = Γ_{1}φ_{5,1}S_{d1} = %+.5f m" % U5[0],
                           "u_{5,2} = Γ_{2}φ_{5,2}S_{d2} = %+.5f m" % U5[1],
                           "（Γ_{i} = L_{i}，因 M_{i}* = 1）",
                           "SRSS = %.5f m = %.2f cm" % (U5_SRSS, 100 * U5_SRSS)]):
        cv.text_px(bx + 14, 330 + i * 23, t, 12, "#1D4ED8", "start",
                   weight="700" if i == 3 else "400")

    cv.text_px(WD / 2, HT - 30,
               "兩個振態分別落在「線性上升段」與「定值段」——"
               "若誤把 f 乘 2π，兩者都會掉進 0.105/f 的尾段，答案整個變小。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-sd.svg")


# ══════════════════════════════════════════════════════════
def fig4_cqc():
    """CQC 相關係數 S_jk 隨頻率比 r 的變化。
    攔錯：以為 CQC 一定與 SRSS 差很多。r = 2.92 時 S_12 僅 0.0025，
    交叉項只佔平方和的 −0.21%，CQC ≈ SRSS 是算出來的，不是猜的。"""
    WD, HT = 1010, 570
    Lm, Rm, Tm, Bm = 100, 274, 92, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    ax = Ax(cv, (1.0, 4.0), (0.0, 1.05), (0.0, 0.0, bw, bh))
    ax.frame([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0],
             xlabel="頻率比 r = ω_{k}/ω_{j}", ylabel="CQC 相關係數 S_{jk}",
             xfmt="{:.1f}", yfmt="{:.1f}")

    rs = [1.0 + i * 3.0 / 900 for i in range(901)]
    for x_, colr, w, dash in ((0.10, C["muted"], 1.9, "6 5"),
                              (0.05, C["bmd"], 1.9, "6 5"),
                              (XI, C["deform"], 3.8, None)):
        ax.curve(rs, [sjk(r, x_, x_) for r in rs], colr, w, dash=dash)

    # 工程準則 r < 1.1
    cv.polygon([ax.P(1.0, 0.0), ax.P(1.1, 0.0), ax.P(1.1, 1.05), ax.P(1.0, 1.05)],
               "rgba(192,57,43,0.10)")
    ax.at(1.10, 0.62, "r ＜ 1.1：必須用 CQC", C["load"], dx=10, size=13, anchor="start")

    ax.vline(R12, 0.0, S12, C["muted"], 1.5)
    ax.mark(R12, S12, "本題 r = %.3f\nS_{12} = %.5f" % (R12, S12), C["accent"],
            dx=13, dy=-34, size=13)

    bx = Lm + int(bw * sx) + 24
    cv.rect_px(bx, 90, 240, 190, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 116, "SRSS 與 CQC 的差距", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["u_{5,1} = %+.5f m" % U5[0],
                           "u_{5,2} = %+.5f m" % U5[1],
                           "交叉項 2S_{12}u_{1}u_{2} = %.2e m^{2}" % (2 * S12 * U5[0] * U5[1]),
                           "SRSS = %.5f m" % U5_SRSS,
                           "CQC  = %.5f m" % U5_CQC,
                           "差異 %.2f%%（可忽略）" % (100 * (U5_CQC / U5_SRSS - 1))]):
        cv.text_px(bx + 14, 144 + i * 23, t, 12, "#1D4ED8", "start",
                   weight="700" if i >= 3 else "400")

    cv.rect_px(bx, 298, 240, 128, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 324, "r 的方向不要搞反", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["S_{12}：j=1、k=2 → r = f_{2}/f_{1}",
                           "S_{21}：j=2、k=1 → r = f_{1}/f_{2}",
                           "兩者相等（S_{21} = %.5f），" % sjk(1 / R12),
                           "但代錯會算出不同分母。"]):
        cv.text_px(bx + 14, 350 + i * 21, t, 12, "#9A3412", "start")

    cv.legend(bx + 6, 452, [(C["deform"], "ξ = %.2f（本題）" % XI),
                            (C["bmd"], "ξ = 0.05"),
                            (C["muted"], "ξ = 0.10")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 30,
               "S_{jk} 只在 r ≈ 1 附近接近 1；一旦頻率分離，它以 r^{-3/2} 衰減——"
               "本題 r = %.2f，CQC 與 SRSS 的差距只有 %.2f%%。"
               % (R12, 100 * abs(U5_CQC / U5_SRSS - 1)), 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-4-cqc.svg")


if __name__ == "__main__":
    print("Σφ² （印出值）:", [round(v, 4) for v in NORM_P])
    print("Σφ² （更正後）:", [round(v, 4) for v in NORM_C])
    print("L   （印出值）:", [round(v, 4) for v in L_P])
    print("ρ   （印出值）:", [f"{100*v:.2f}%" for v in RHO_P])
    print("ρ   （更正後）:", [f"{100*v:.2f}%" for v in RHO_C])
    print("累積（印出值）:", [f"{100*v:.2f}%" for v in CUM_P], "→ 需", NMODE, "個振態")
    print("S_d:", [round(v, 5) for v in SD_])
    print(f"u_5,1 = {U5[0]:+.5f}  u_5,2 = {U5[1]:+.5f}")
    print(f"r = {R12:.4f}  S_12 = {S12:.6f}  S_21 = {sjk(1/R12):.6f}")
    print(f"SRSS = {U5_SRSS:.5f} m   CQC = {U5_CQC:.5f} m   "
          f"差異 {100*(U5_CQC/U5_SRSS-1):.3f}%")
    for f in (fig1_modes(), fig2_mass(), fig3_sd(), fig4_cqc()):
        print(f)
