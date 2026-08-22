#!/usr/bin/env python3
"""
SD-2013-1 解題圖解產生腳本（struct-diagram skill）

用法：  python3 gen_SD-2013-1.py [輸出目錄]      # 預設輸出到 ./figs

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


TAG = "SD-2013-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2013-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# ── 題(一) 隔震：設計反應譜的折減比 ──
# §4 題(一)：S_a 在平台段為定值 S_DS，超過 T_s 後才是 S_D1/T。
#            折減比 = S_a(T_IS)/S_a(T_0) = T_s/T_IS（分子是 T_s，不是 T_0）
TS = 0.5           # 平台段末端 T_s（s）——解析檔採用的示範值
T0 = 0.30          # 固定基礎建築的自然週期（s），落在平台段
T_IS = 3.0         # 隔震後的等效週期（s）
TS_ALT = [0.4, 0.5, 0.6]                       # 換不同 T_s 時折減比會跟著變


def sa_norm(t):
    """正規化設計反應譜（S_DS = 1）：平台段 + 1/T 下降段"""
    return 1.0 if t <= TS else TS / t


RATIO_OK = sa_norm(T_IS) / sa_norm(T0)         # = T_s/T_IS = 1/6
RATIO_BAD = T0 / T_IS                          # 誤用 T_0/T_IS 的結果

# ── 題(二) TMD：2-DOF 頻率反應（Den Hartog 標準式，以複數直接解 2×2）──
MU = 0.02          # 質量比 m_a/m_s（示範值；解析檔要求 μ ≥ 1%）
FT = 1.0           # 調諧比 ω_a/ω_s（完美調諧）
XI_S = 0.01        # 主結構阻尼比
XI_A = 0.06        # TMD 阻尼比（示範值）


def frf(g, mu=MU, ft=FT, xs=XI_S, xa=XI_A):
    """回傳 (|X_s|/x_st, |X_a|/x_st)；令 m_s = ω_s = k_s = 1，外力施於主質量。
    mu = 0 時自動退化為無 TMD 的 SDOF。"""
    ka, ca, cs = mu * ft ** 2, 2 * xa * mu * ft, 2 * xs
    if mu == 0.0:
        return abs(1.0 / complex(1 - g ** 2, cs * g)), 0.0
    z11 = complex(1 + ka - g ** 2, (cs + ca) * g)
    z12 = complex(-ka, -ca * g)
    z22 = complex(ka - mu * g ** 2, ca * g)
    det = z11 * z22 - z12 * z12
    return abs(z22 / det), abs(-z12 / det)


# 反共振谷的真正位置：先找出被劈開的兩個峰，再取兩峰「之間」的極小
# （有阻尼時谷不會恰好落在 g = f，且全域掃描會誤抓到區間邊界）
_gs = [0.70 + i * 0.60 / 6000 for i in range(6001)]
_ys = [frf(g)[0] for g in _gs]
_pk = [i for i in range(1, len(_gs) - 1) if _ys[i] > _ys[i - 1] and _ys[i] > _ys[i + 1]]
assert len(_pk) == 2, f"預期兩個峰，實得 {len(_pk)} 個——調諧比或阻尼比可能不合理"
G_ANTI = min(_gs[_pk[0]:_pk[1]], key=lambda g: frf(g)[0])
G_PEAKS = [_gs[i] for i in _pk]
XS_NO = frf(1.0, mu=0.0)[0]                    # 無 TMD 的共振峰值 = 1/(2ξ_s)
XS_TMD_ANTI = frf(G_ANTI)[0]                   # 加 TMD 後主結構在該頻率的反應
XA_TMD_ANTI = frf(G_ANTI)[1]                   # 同一頻率下 TMD 自身的反應（很大）

# ── 題(四) 對數衰減率 ──
XI_LD = 0.05                                   # 示範阻尼比（RC 結構典型值）
W0_LD = 2 * math.pi                            # ω_0，取 T = 1 s 方便讀圖
WD_LD = W0_LD * math.sqrt(1 - XI_LD ** 2)
TD_LD = 2 * math.pi / WD_LD                    # 有阻尼週期
DELTA = 2 * math.pi * XI_LD / math.sqrt(1 - XI_LD ** 2)
XI_BACK = DELTA / math.sqrt(4 * math.pi ** 2 + DELTA ** 2)      # 反算應回到 XI_LD
XI_APPROX = DELTA / (2 * math.pi)                                # 輕阻尼近似
XI_TABLE = [0.01, 0.05, 0.10, 0.20]


def x_free(t):
    """自由振動（設 t = 0 為第一個峰值，振幅正規化為 1）"""
    return math.exp(-XI_LD * W0_LD * t) * math.cos(WD_LD * t)


# 注意：含中文的字串一律用 text_px / lab()；math_px 的襯線數學字型沒有中文字。


# ══════════════════════════════════════════════════════════
def fig1_spectrum():
    """設計反應譜與隔震折減：分子是 T_s，不是原結構週期 T_0。
    攔錯：把 S_a ∝ 1/T 的下降段關係套到平台段，直接用 T_0/T_IS 相除。"""
    WD, HT = 1010, 560
    Lm, Rm, Tm, Bm = 100, 268, 96, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    TMAX = 4.0
    ax = Ax(cv, (0.0, TMAX), (0.0, 1.20), (0.0, 0.0, bw, bh))
    ax.frame([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
             [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlabel="週期 T  (s)",
             ylabel="S_{a} / S_{DS}", xfmt="{:g}", yfmt="{:.1f}")

    ts = [i * TMAX / 800 for i in range(801)]
    ax.area(ts, [sa_norm(t) for t in ts], C["fill_m"])
    ax.curve(ts, [sa_norm(t) for t in ts], C["bmd"], 3.6)

    ax.vline(TS, 0.0, 1.12, C["muted"], 1.6)
    ax.at(TS, 1.155, "T_{s} = %.1f s（平台段末端）" % TS, C["muted"], size=12.5)
    ax.at(0.26, 0.88, "平台段：S_{a} = S_{DS}", C["accent"], size=12.5)
    ax.at(2.10, 0.42, "下降段：S_{a} = S_{D1}/T", C["accent"], size=12.5)

    for t, colr, name in ((T0, C["deform"], "固定基礎 T_{0}"),
                          (T_IS, C["load"], "隔震後 T_{IS}")):
        ax.vline(t, 0.0, sa_norm(t), colr, 1.8)
        ax.hline(sa_norm(t), 0.0, t, colr, 1.4)
        cv.dot(ax.P(t, sa_norm(t)), 6.0, fill=colr, stroke="#FFFFFF", w=2.0)
    ax.at(T0, sa_norm(T0), "%s = %.2f s\nS_{a} = %.3f" % ("固定基礎 T_{0}", T0, sa_norm(T0)),
          C["deform"], dx=12, dy=-34, size=12.5, anchor="start")
    ax.at(T_IS, sa_norm(T_IS), "隔震後 T_{IS} = %.1f s\nS_{a} = %.4f" % (T_IS, sa_norm(T_IS)),
          C["load"], dx=12, dy=-34, size=12.5, anchor="start")

    # 正確與錯誤的折減比
    ax.at(1.55, 0.86, "折減比 = S_{a}(T_{IS}) / S_{a}(T_{0}) = T_{s}/T_{IS} = %.4f ≈ 1/%.1f"
          % (RATIO_OK, 1 / RATIO_OK), C["bmd"], size=13.5)
    ax.at(1.55, 0.74, "誤用 T_{0}/T_{IS} = %.4f，低估 %.0f%%"
          % (RATIO_BAD, 100 * (1 - RATIO_BAD / RATIO_OK)), C["load"], size=13)

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 92, 236, 158, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 118, "分子是 T_{s}，不是 T_{0}", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["平台段 S_{a} 與週期無關，",
                           "所以 T_{0} 本身不進折減比；",
                           "真正決定分子的是平台段",
                           "末端 T_{s}。兩者數值常接近",
                           "（都在 0.4～0.6 s），但換一",
                           "組譜參數就會露餡。"]):
        cv.text_px(bx + 14, 144 + i * 20, t, 12, "#9A3412", "start")

    cv.rect_px(bx, 268, 236, 152, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 294, "換 T_{s} 折減比就變", 13.5, "#1D4ED8", "start", weight="700")
    for i, tsv in enumerate(TS_ALT):
        cv.text_px(bx + 14, 322 + i * 24,
                   "T_{s} = %.1f s → %.4f ≈ 1/%.1f" % (tsv, tsv / T_IS, T_IS / tsv),
                   12.5, "#1D4ED8", "start", weight="700" if abs(tsv - TS) < 1e-9 else "400")
    cv.text_px(bx + 14, 400, "（T_{IS} = %.1f s 固定）" % T_IS, 12, "#1D4ED8", "start")

    cv.text_px(WD / 2, HT - 32,
               "隔震把週期從平台段推到下降段——折減來自「跨過 T_{s} 之後 S_{a} 才開始隨 1/T 掉」，"
               "這正是分子只能是 T_{s} 的原因。", 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-spectrum.svg")


# ══════════════════════════════════════════════════════════
def fig2_tmd():
    """TMD 的頻率反應：主結構出現反共振谷、TMD 自身反而振幅極大。
    攔錯：把反共振的主體記成 TMD（若 TMD 幾乎不動，就不會有慣性力回饋主結構）。"""
    WD, HT = 1010, 580
    Lm, Rm, Tm, Bm = 100, 272, 96, 104
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    gs = [0.70 + i * 0.60 / 900 for i in range(901)]
    # 圖框上緣由資料決定，不寫死——三條曲線都要完整容納
    YMAX = 20 * math.ceil(max(max(frf(g)[1] for g in gs), XS_NO) / 20)
    ax = Ax(cv, (0.70, 1.30), (0.0, YMAX), (0.0, 0.0, bw, bh))
    ax.frame([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
             [20 * i for i in range(int(YMAX // 20) + 1)],
             xlabel="頻率比 Ω/ω_{s}", ylabel="振幅 / 靜位移", xfmt="{:.1f}", yfmt="{:g}")

    ax.curve(gs, [min(frf(g, mu=0.0)[0], YMAX) for g in gs], C["muted"], 2.4, dash="8 5")
    ax.curve(gs, [min(frf(g)[1], YMAX) for g in gs], C["load"], 2.8, dash="5 4")
    ax.curve(gs, [min(frf(g)[0], YMAX) for g in gs], C["deform"], 3.8)

    ax.vline(G_ANTI, 0.0, YMAX, C["accent"], 1.8)
    cv.dot(ax.P(G_ANTI, frf(G_ANTI)[0]), 6.0, fill=C["deform"], stroke="#FFFFFF", w=2.0)
    cv.dot(ax.P(G_ANTI, min(frf(G_ANTI)[1], YMAX)), 6.0, fill=C["load"],
           stroke="#FFFFFF", w=2.0)

    # 讀值框放在繪圖區內保證空白的右上角（該處三條曲線都已降到很低）
    px0, py0 = cv.X(ax.X(1.045)), 112
    cv.rect_px(px0, py0, 258, 108, "#FFFFFF", 10, C["border"], 1.3)
    cv.text_px(px0 + 14, py0 + 22, "在反共振谷 Ω/ω_{s} = %.3f 上的三個振幅" % G_ANTI, 12.5,
               C["text"], "start", weight="700")
    for i, (colr, name, val) in enumerate([(C["muted"], "主結構（無 TMD）", XS_NO),
                                           (C["deform"], "主結構（有 TMD）", XS_TMD_ANTI),
                                           (C["load"], "TMD 質量塊本身", XA_TMD_ANTI)]):
        yy = py0 + 46 + i * 21
        cv.parts.append(f'<line x1="{px0+14}" y1="{yy}" x2="{px0+32}" y2="{yy}" '
                        f'stroke="{colr}" stroke-width="3.4" stroke-linecap="round"/>')
        cv.text_px(px0 + 40, yy, name, 12, colr, "start")
        cv.text_px(px0 + 244, yy, "%.2f" % val, 12.5, colr, "end", weight="700")
    ax.at(1.30, YMAX * 0.30, "加 TMD 後峰被劈成兩個", C["deform"], size=12.5, anchor="end")

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 92, 240, 176, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 118, "反共振的主體是主結構", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["TMD 被刻意放在共振點上",
                           "大幅擺動（此圖 %.0f 倍靜位移），" % XA_TMD_ANTI,
                           "才有足夠慣性力回饋主結構。",
                           "若 TMD 幾乎不動，就不會產",
                           "生任何反作用力——這也是",
                           "為何 TMD 的行程是設計關鍵。"]):
        cv.text_px(bx + 14, 144 + i * 21, t, 12, "#9A3412", "start",
                   weight="700" if i == 1 else "400")

    cv.rect_px(bx, 286, 240, 134, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 312, "示範參數", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["質量比 μ = %.2f" % MU,
                           "調諧比 ω_{a}/ω_{s} = %.2f" % FT,
                           "主結構 ξ_{s} = %.2f" % XI_S,
                           "TMD ξ_{a} = %.2f" % XI_A]):
        cv.text_px(bx + 14, 338 + i * 21, t, 12, "#1D4ED8", "start")

    cv.legend(bx + 6, 448, [(C["deform"], "主結構（有 TMD）"),
                            (C["muted"], "主結構（無 TMD）"),
                            (C["load"], "TMD 質量塊本身")], size=12.5, gap=23)

    cv.text_px(WD / 2, HT - 32,
               "同一個頻率上，主結構掉到 %.2f、TMD 卻衝到 %.1f——"
               "一條曲線在谷、另一條在峰，反共振的主體是誰就沒有爭議了。"
               % (XS_TMD_ANTI, XA_TMD_ANTI), 13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-tmd.svg")


# ══════════════════════════════════════════════════════════
def fig3_logdec():
    """自由振動衰減與對數衰減率：峰值「比值」的對數，以及輕阻尼近似的適用範圍。
    攔錯：把 δ 當成兩峰值的差或衰減百分比；以及誤以為 δ/2π 在任何阻尼下都夠用。"""
    WD, HT = 1010, 560
    Lm, Rm, Tm, Bm = 100, 274, 96, 100
    bw = 1.0
    sx = (WD - Lm - Rm) / bw
    bh = (HT - Tm - Bm) / sx
    cv = Canvas(WD, HT, sx=sx, ox=Lm, oy=Bm, bg="#FFFFFF")

    NPK = 4
    TMAX = NPK * TD_LD + 0.35
    ax = Ax(cv, (0.0, TMAX), (-1.15, 1.35), (0.0, 0.0, bw, bh))
    ax.frame([0, 1, 2, 3, 4], [-1.0, -0.5, 0.0, 0.5, 1.0],
             xlabel="t  (s)", ylabel="x / x_{1}", xfmt="{:g}", yfmt="{:.1f}")

    ts = [i * TMAX / 1200 for i in range(1201)]
    ax.hline(0.0, 0.0, TMAX, C["muted"], 1.6, dash=None)
    ax.curve(ts, [math.exp(-XI_LD * W0_LD * t) for t in ts], C["ghost"], 2.2, dash="7 5")
    ax.curve(ts, [-math.exp(-XI_LD * W0_LD * t) for t in ts], C["ghost"], 2.2, dash="7 5")
    ax.curve(ts, [x_free(t) for t in ts], C["deform"], 3.6)

    peaks = [(n * TD_LD, x_free(n * TD_LD)) for n in range(NPK + 1)]
    for n, (tp, xp) in enumerate(peaks):
        cv.dot(ax.P(tp, xp), 5.8, fill=C["accent"], stroke="#FFFFFF", w=2.0)
        ax.at(tp, xp, "x_{%d} = %.4f" % (n + 1, xp), C["accent"], dy=-15, size=11.5)

    # 相鄰兩峰之間標一個有阻尼週期
    cv.dim(ax.P(peaks[1][0], -1.05), ax.P(peaks[2][0], -1.05), "T_{d} = %.4f s" % TD_LD,
           off=0, label_off=-15)

    ax.at(TMAX * 0.62, 1.22,
          "δ = ln(x_{n}/x_{n+1}) = %.5f　→　ξ = δ/√(4π^{2}+δ^{2}) = %.5f"
          % (DELTA, XI_BACK), C["text"], size=13.5)

    bx = Lm + int(bw * sx) + 22
    cv.rect_px(bx, 92, 244, 150, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(bx + 16, 118, "δ 是「比值」的對數", 13.5, "#1D4ED8", "start", weight="700")
    for i, t in enumerate(["x_{1}/x_{2} = %.5f" % (peaks[0][1] / peaks[1][1]),
                           "ln(x_{1}/x_{2}) = %.5f" % DELTA,
                           "跨 N 期：(1/N)ln(x_{1}/x_{N+1})",
                           "  = %.5f（完全相同）"
                           % (math.log(peaks[0][1] / peaks[NPK][1]) / NPK),
                           "不是差、也不是衰減百分比。"]):
        cv.text_px(bx + 14, 144 + i * 21, t, 12, "#1D4ED8", "start",
                   weight="700" if i == 4 else "400")

    cv.rect_px(bx, 260, 244, 168, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(bx + 16, 286, "δ/2π 近似的誤差", 13.5, "#9A3412", "start", weight="700")
    cv.text_px(bx + 16, 310, "ξ 真值　δ/2π　誤差", 11.5, "#9A3412", "start", weight="700")
    for i, x_ in enumerate(XI_TABLE):
        d_ = 2 * math.pi * x_ / math.sqrt(1 - x_ ** 2)
        ap = d_ / (2 * math.pi)
        cv.text_px(bx + 16, 332 + i * 21,
                   "%.2f　　　%.4f　　+%.2f%%" % (x_, ap, 100 * (ap / x_ - 1)),
                   11.5, "#9A3412", "start",
                   weight="700" if abs(x_ - XI_LD) < 1e-9 else "400")

    cv.text_px(WD / 2, HT - 32,
               "包絡線是指數衰減，所以相鄰峰值之「比」是定值（與 n 無關）——"
               "取對數才會得到與 ξ 線性相關的量，這就是要取比值而非差值的原因。",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-logdec.svg")


if __name__ == "__main__":
    print(f"[題一] S_a(T0)={sa_norm(T0):.4f}  S_a(T_IS)={sa_norm(T_IS):.4f}  "
          f"折減比={RATIO_OK:.5f}=1/{1/RATIO_OK:.2f}   誤用 T0/T_IS={RATIO_BAD:.4f}"
          f"（低估 {100*(1-RATIO_BAD/RATIO_OK):.0f}%）")
    for tsv in TS_ALT:
        print(f"        T_s={tsv} → 折減比 {tsv/T_IS:.5f} = 1/{T_IS/tsv:.2f}")
    print(f"[題二] 無 TMD 共振峰 = {XS_NO:.3f}（1/(2ξ_s) = {1/(2*XI_S):.1f}）")
    print(f"        Ω/ω_s = 1：主結構 {XS_TMD_ANTI:.4f}  TMD {XA_TMD_ANTI:.3f}"
          f"（1/μ = {1/MU:.1f}）")
    print(f"[題四] ω_d={WD_LD:.5f}  T_d={TD_LD:.5f}  δ={DELTA:.6f}  "
          f"反算 ξ={XI_BACK:.6f}（應={XI_LD}）  δ/2π={XI_APPROX:.6f}")
    for f in (fig1_spectrum(), fig2_tmd(), fig3_logdec()):
        print(f)
