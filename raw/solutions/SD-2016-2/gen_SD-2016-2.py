#!/usr/bin/env python3
"""
SD-2016-2 兩支剛性梁 2-DOF 系統 — 解題圖解產生腳本

用法：python3 gen_SD-2016-2.py [輸出目錄]

2026-08-22 勘誤：上梁右端 B 是「一點兩簧」（天花板簧＋聯接簧）。
fig-1 逐點清點彈簧、fig-2 逐格算力矩、fig-3 畫出真正的振態比，
三張圖各自獨立地讓「漏一根簧」現形。
"""
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2016-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2016-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §4(一) 質量矩陣：M = (m l^2 / 3) I
# §4(二) 勁度矩陣（以 k l^2 為單位）
K11 = 9 / 4        # = 1/4（中點簧）+ 1（B 端天花板簧）+ 1（聯接簧）
K22 = 5 / 4        # = 1/4（中點簧）+ 1（聯接簧）
K12 = -1.0         # 聯接簧的耦合項

# §4(三) 特徵值：det([K]-w^2[M])=0，令 lam = w^2 m /(3k)
#   → 16 lam^2 - 56 lam + 29 = 0 → lam = (7 -+ 2 sqrt5)/4
_disc = math.sqrt((K11 + K22) ** 2 - 4 * (K11 * K22 - K12 ** 2))
LAM = [((K11 + K22) - _disc) / 2, ((K11 + K22) + _disc) / 2]      # 0.63197, 2.86803
OMG = [math.sqrt(3 * l) for l in LAM]                             # w / sqrt(k/m)
PHI = [K11 - l for l in LAM]                                      # phi2/phi1 = 9/4 - lam
#   PHI = [1.618034, -0.618034] = 黃金比例 (1±sqrt5)/2

# 聯接簧的變形量（伸長為正）= (phi2 - phi1) * l
SPRING_DEF = [p - 1.0 for p in PHI]                               # +0.618 l, -1.618 l

MW = 8.0
LB = 1.10          # 梁長（模型單位）
GAPX = 0.10        # B 與 C 的水平間距（僅為畫圖易讀）
CEIL = 1.05        # 天花板高度
Y1 = 0.60          # 上梁平衡位置
Y2 = 0.00          # 下梁平衡位置


def _spring(cv, p0, p1, color=C["muted"], n=6, amp=0.030, w=1.8):
    """鋸齒彈簧"""
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    seg = L / (n + 1)
    pts = [p0, (x0 + ux * seg * .5, y0 + uy * seg * .5)]
    for i in range(n):
        s = 1 if i % 2 == 0 else -1
        pts.append((x0 + ux * seg * (i + 1) + nx * amp * s,
                    y0 + uy * seg * (i + 1) + ny * amp * s))
    pts += [(x1 - ux * seg * .5, y1 - uy * seg * .5), p1]
    cv.poly(pts, color, w)


def _ceil_mount(cv, x, y=CEIL, color=C["muted"]):
    cv.line((x - .09, y), (x + .09, y), color, 1.8)
    for i in range(5):
        cv.line((x - .08 + i * .04, y), (x - .11 + i * .04, y + .045), color, 1.3)


def _layout(t1=0.0, t2=0.0):
    """回傳幾何點位。t1/t2 為兩梁的轉角（繪圖用位移量，正 = 端點向下）"""
    A = (0.0, Y1)
    B = (LB, Y1 - t1)
    Bmid = (LB / 2, Y1 - t1 / 2)
    C_ = (LB + GAPX, Y2 - t2)
    D = (LB + GAPX + LB, Y2)
    Cmid = (LB + GAPX + LB / 2, Y2 - t2 / 2)
    return A, B, Bmid, C_, D, Cmid


def _draw_system(cv, t1=0.0, t2=0.0, colA=C["member"], colB=C["member"],
                 ghost=False, spring_hl=None, w=MW):
    A, B, Bmid, C_, D, Cmid = _layout(t1, t2)
    sc = C["ghost"] if ghost else C["muted"]
    hl = spring_hl or ()

    _ceil_mount(cv, Bmid[0]); _ceil_mount(cv, B[0]); _ceil_mount(cv, Cmid[0])
    _spring(cv, (Bmid[0], CEIL), Bmid, C["accent"] if 1 in hl else sc)
    _spring(cv, (B[0], CEIL), B, C["accent"] if 2 in hl else sc, n=8)
    _spring(cv, B, C_, C["accent"] if 3 in hl else sc, n=5)
    _spring(cv, (Cmid[0], CEIL), Cmid, C["accent"] if 4 in hl else sc, n=12)

    cv.poly([A, B], colA, w)
    cv.poly([C_, D], colB, w)
    cv.support(A, "pin", 90, 15, colA)
    cv.support(D, "pin", -90, 15, colB)
    return A, B, Bmid, C_, D, Cmid


# ══════════════════════════════════════════════════════════
def fig1_model():
    """題目重繪：逐點清點彈簧 — 全系統 4 根，B 點掛 2 根"""
    cv = Canvas(880, 510, sx=290, ox=100, oy=150, bg="#FFFFFF")
    A, B, Bmid, C_, D, Cmid = _draw_system(cv)

    for p, lab, dx, dy in ((A, "A", -20, -16), (B, "B", 14, -20),
                           (C_, "C", -20, 20), (D, "D", 20, -16)):
        cv.dot(p, 5.0)
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, lab, 16, C["text"], weight="700")

    for i, (x, y) in enumerate(((Bmid[0], (CEIL + Bmid[1]) / 2),
                                (B[0], (CEIL + B[1]) / 2),
                                ((B[0] + C_[0]) / 2, (B[1] + C_[1]) / 2),
                                (Cmid[0], (CEIL + Cmid[1]) / 2)), start=1):
        cv.math_px(cv.X(x) + 13, cv.Y(y), "k", 16, C["muted"], "start", weight="700")
        cv.text_px(cv.X(x) - 13, cv.Y(y), f"({i})", 12.5, C["accent"], anchor="end")

    cv.dim(A, Bmid, "l/2", off=44, label_off=15)
    cv.dim(Bmid, B, "l/2", off=44, label_off=15)
    cv.dim(C_, Cmid, "l/2", off=44, label_off=15)
    cv.dim(Cmid, D, "l/2", off=44, label_off=15)
    cv.text_px(cv.X(LB / 2), cv.Y(Y1) + 80, "上梁　總質量 = m", 13.5, C["muted"])
    cv.text_px(cv.X(LB + GAPX + LB / 2), cv.Y(Y2) + 80, "下梁　總質量 = m", 13.5, C["muted"])

    # 把「B 點兩根簧」圈出來
    cv.circle(B, 0.115, "none", C["accent"], 2.4, dash="5 4")
    cv.text_px(cv.X(B[0]) + 34, cv.Y(B[1]) - 62,
               "B 點掛兩根簧：(2) 對天花板、(3) 對下梁", 13, C["accent"],
               anchor="start", weight="700")

    cv.text_px(440, 486,
               "全系統共 4 根彈簧：(1)(2)(4) 為天花板簧、(3) 為聯接簧；漏掉 (2) 會使 K11 由 9kl^2/4 誤為 5kl^2/4",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-model.svg")


# ══════════════════════════════════════════════════════════
def _unit_panel(which):
    """單位轉角狀態圖：which = 1 → theta1=1；which = 2 → theta2=1"""
    T = 0.20
    t1, t2 = (T, 0.0) if which == 1 else (0.0, T)
    cv = Canvas(900, 330, sx=150, ox=62, oy=68, bg=C["panel"])
    cv.panel(f"施加 θ_{which} = 1，另一者鎖住", None)

    _draw_system(cv, 0, 0, C["ghost"], C["ghost"], ghost=True, w=3.0)
    A, B, Bmid, C_, D, Cmid = _draw_system(
        cv, t1, t2, C["deform"], C["deform"],
        spring_hl=(1, 2, 3) if which == 1 else (3, 4))

    def force(p, up, lab, col=C["load"]):
        d = 0.20 if up else -0.20
        cv.arrow((p[0], p[1]), (p[0], p[1] + d), col, 3.0, 10)
        cv.math_px(cv.X(p[0]) + 12, cv.Y(p[1] + d) + (-8 if up else 8),
                   lab, 14, col, "start", weight="700")

    if which == 1:
        force(Bmid, True, "k(l/2)")
        force(B, True, "kl")                       # ← B 端天花板簧
        force(C_, False, "kl")                     # 聯接簧對 C 的反作用（向下）
        rows = [("中點簧 (1)", "k(l/2)·(l/2) = kl^{2}/4"),
                ("B 端天花板簧 (2)", "k(l)·(l) = kl^{2}"),
                ("聯接簧 (3)", "k(l)·(l) = kl^{2}"),
                ("K_{11} 合計", "9kl^{2}/4"),
                ("K_{21}（對 D）", "-kl^{2}")]
    else:
        force(Cmid, True, "k(l/2)")
        force(C_, True, "kl")
        force(B, False, "kl")
        rows = [("中點簧 (4)", "k(l/2)·(l/2) = kl^{2}/4"),
                ("聯接簧 (3)", "k(l)·(l) = kl^{2}"),
                ("下梁無其他簧", "—"),
                ("K_{22} 合計", "5kl^{2}/4"),
                ("K_{12}（對 A）", "-kl^{2}")]

    y0 = 90
    cv.line((2.60, -0.30), (2.60, 1.10), C["border"], 1.2)
    for i, (a, b) in enumerate(rows):
        hi = a.startswith("K_")
        col = C["accent"] if hi else C["muted"]
        cv.text_px(480, y0 + i * 34, a.replace("_{11}", "11").replace("_{21}", "21")
                   .replace("_{22}", "22").replace("_{12}", "12"),
                   13.5, col, anchor="start", weight="700" if hi else "400")
        cv.math_px(650, y0 + i * 34, b, 15, col, "start", weight="700" if hi else "400")
    return cv


def fig2_unit_states():
    """勁度矩陣每一行的物理意義：單位轉角下各簧力對支點的力矩"""
    path = f"{OUT}/{TAG}-fig-2-unit-states.svg"
    compose([_unit_panel(1), _unit_panel(2)], cols=1,
            title="勁度矩陣的兩個單位轉角狀態（橙色＝該狀態下被拉伸／壓縮的彈簧）",
            sub="力矩 = 彈簧力 × 力臂 = k(rθ)·r = k r^2 θ，故力臂平方是旋轉自由度的特徵",
            note="上梁三根簧、下梁兩根簧，這個不對稱正是 K11 ≠ K22 的原因；非對角項為負，因聯接簧「推」另一梁朝正向轉",
            path=path)
    return path


# ══════════════════════════════════════════════════════════
def _mode_panel(i):
    A_ = 0.20                                   # 繪圖用振幅（θ1 對應的端點位移）
    t1 = A_
    t2 = A_ * PHI[i]
    cv = Canvas(880, 400, sx=200, ox=92, oy=95, bg=C["panel"])
    ratio = f"{PHI[i]:+.3f}"
    cv.panel(f"Mode {i+1}：ω = {OMG[i]:.3f}·√(k/m)",
             f"θ1 : θ2 = 1 : {ratio}　（λ = {LAM[i]:.4f}）")

    _draw_system(cv, 0, 0, C["ghost"], C["ghost"], ghost=True, w=3.0)
    A, B, Bmid, C_, D, Cmid = _draw_system(cv, t1, t2, C["deform"],
                                           C["deform"], spring_hl=(3,))

    # 聯接簧的變形量（由振態算出，不是目測）
    d = SPRING_DEF[i]
    txt = ("伸長 %.3f l" % d) if d > 0 else ("壓縮 %.3f l" % abs(d))
    cv.text_px(cv.X((B[0] + C_[0]) / 2) + 26, cv.Y((B[1] + C_[1]) / 2),
               txt, 13.5, C["accent"], anchor="start", weight="700")

    cv.math_px(cv.X(0.06), cv.Y(Y1) - 30, "θ_{1} = 1", 15, C["deform"],
               "start", weight="700")
    yl = Y2 - t2 - 0.30
    cv.math_px(cv.X(LB + GAPX + 0.72), cv.Y(yl), "θ_{2} = %+.3f" % PHI[i],
               15, C["deform"], "start", weight="700")
    return cv


def fig3_modes():
    """振態形狀：兩梁的轉角比由特徵向量算出，不是畫成好看的 ±1"""
    path = f"{OUT}/{TAG}-fig-3-modes.svg"
    compose([_mode_panel(0), _mode_panel(1)], cols=1,
            title="兩個振態的實際形狀（比值由特徵向量算出）",
            sub="灰虛線＝平衡位置；正交性檢查：1×1 + (%.3f)×(%.3f) = %.3f"
                % (PHI[0], PHI[1], 1 + PHI[0] * PHI[1]),
            note="振態不是 {1, 1} 與 {1, -1}——那是「上梁少一根簧」時才會出現的對稱解；"
                 "此處為黃金比例 (1±√5)/2，ω2/ω1 = %.2f 而非 3" % (OMG[1] / OMG[0]),
            path=path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(f"  λ = {LAM[0]:.5f}, {LAM[1]:.5f}   ω/√(k/m) = {OMG[0]:.5f}, {OMG[1]:.5f}")
    print(f"  φ2/φ1 = {PHI[0]:.5f}, {PHI[1]:.5f}   正交性 = {1+PHI[0]*PHI[1]:.2e}")
    for f in (fig1_model, fig2_unit_states, fig3_modes):
        print(" ", f())
