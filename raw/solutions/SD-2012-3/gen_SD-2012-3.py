#!/usr/bin/env python3
"""SD-2012-3 圖解產生器 — (一) 強度≠勁度的層間位移角檢核；(二) 扭轉不規則性
兩張圖的數值全部由頂端參數算出（含剛心位置、扭轉勁度、兩端位移比），改參數重跑即更新。
"""
import sys, os
SKILL = os.environ.get("STRUCTDRAW",
    "/root/.claude/skills/synced/ac6f22be-8f8e-4e9a-b5a5-57a76b0ea389_ed8ec2e9-4a34-4076-aef8-82296cfdbb5c/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ══ 圖 1 參數：兩棟「同強度、不同勁度」的結構 ══════════════
H_STORY = 3500.0          # 層高 (mm)
THETA_LIMIT = 0.005       # 規範 2.16.1：層間相對側向位移角上限
D_LIMIT = THETA_LIMIT * H_STORY          # = 17.5 mm
V_STAR = 120.0            # 中小度地震設計地震力 V* (kN)
V_Y = 180.0               # 兩棟的降伏強度相同 (kN)
K_A, K_B = 12.0, 5.0      # 側向勁度 (kN/mm)

D_A, D_B = V_STAR / K_A, V_STAR / K_B
TH_A, TH_B = D_A / H_STORY, D_B / H_STORY

# ══ 圖 2 參數：單層剛性樓板，Y 向構架配置於不同 X ══════════
B, D = 20.0, 12.0                     # 平面尺度 (m)：B 為受力垂直方向的長度
FRAME_X = [0.0, 10.0, 20.0]           # Y 向構架的 X 座標
FRAME_K = [2.0, 1.0, 1.0]             # 各構架的側向勁度（相對值）
X_CM = B / 2                          # 質心（質量均布）
SUM_K = sum(FRAME_K)
X_CR = sum(k * x for k, x in zip(FRAME_K, FRAME_X)) / SUM_K
ECC = X_CM - X_CR                     # 靜態偏心距
J_T = sum(k * (x - X_CR) ** 2 for k, x in zip(FRAME_K, FRAME_X))   # 扭轉勁度
V_UNIT = 1.0                          # 樓層剪力（取 1，位移即 1/k 的倍數）
D_TRANS = V_UNIT / SUM_K
THETA_T = V_UNIT * ECC / J_T
DELTA = [D_TRANS + THETA_T * (x - X_CR) for x in FRAME_X]
D_MAX, D_MIN = max(DELTA[0], DELTA[-1]), min(DELTA[0], DELTA[-1])
D_AVG = (DELTA[0] + DELTA[-1]) / 2
RATIO = D_MAX / D_AVG
ECC_ACC = 0.05 * B                    # 偶然偏心 ±5% 樓面尺度
A_X = min((D_MAX / (1.2 * D_AVG)) ** 2, 3.0)


# ══════════════════════════════════════════════════════════
# 圖 1：強度相同、勁度不同 —— 位移角檢核管的是勁度
# ══════════════════════════════════════════════════════════
def fig1():
    W, HH = 940, 560
    xmax, ymax = max(D_B, D_LIMIT, V_Y / K_B) * 1.16, V_Y * 1.28
    L, R_, T_, B_ = 100, 208, 96, 108
    sy = (HH - T_ - B_) / ymax
    XSC = (W - L - R_) / (sy * xmax)
    cv = Canvas(W, HH, sx=sy, ox=L, oy=B_)
    XM = lambda v: v * XSC

    cv.text_px(W / 2, 34, "圖 1　同樣的強度，不同的勁度：V* 過關不代表位移角過關",
               17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58,
               f"兩棟結構降伏強度同為 {V_Y:.0f} kN，在 V* = {V_STAR:.0f} kN 下都維持線彈性",
               13, C["muted"])
    cv.axes((0, 0), XM(xmax) * 0.99, ymax * 0.99, ("Δ (mm)", "V (kN)"), C["muted"], 1.8)

    # 位移角限值帶
    cv.polygon([(XM(D_LIMIT), 0), (XM(xmax) * 0.99, 0),
                (XM(xmax) * 0.99, ymax * 0.99), (XM(D_LIMIT), ymax * 0.99)],
               "rgba(192,57,43,0.07)", "none")
    cv.line((XM(D_LIMIT), 0), (XM(D_LIMIT), ymax * 0.94), C["load"], 2.4, dash="7 5")
    cv.text_px(cv.X(XM(D_LIMIT)) + 8, cv.Y(ymax * 0.94) - 6,
               f"Δ 上限 = 0.005 × {H_STORY:.0f} = {D_LIMIT:.1f} mm",
               12.5, C["load"], "start", weight="700")
    cv.text_px(cv.X(XM((D_LIMIT + xmax) / 2)), cv.Y(ymax * 0.12), "不合格區",
               13, C["load"], weight="700")

    # 降伏強度線（兩棟相同）
    cv.line((0, V_Y), (XM(xmax) * 0.99, V_Y), C["bmd"], 2.4, dash="5 5")
    cv.math_px(cv.X(XM(xmax) * 0.99) + 10, cv.Y(V_Y),
               f"V_y = {V_Y:.0f} kN（兩棟相同）", 13, C["bmd"], "start", weight="700")
    # V* 水平線
    cv.line((0, V_STAR), (XM(xmax) * 0.99, V_STAR), C["muted"], 1.6, dash="4 4")
    cv.math_px(cv.X(XM(xmax) * 0.99) + 10, cv.Y(V_STAR),
               f"V* = {V_STAR:.0f} kN", 13, C["muted"], "start", weight="700")

    for k, dmax, col, nm in ((K_A, D_A, C["deform"], "A"), (K_B, D_B, C["sfd"], "B")):
        dy = V_Y / k
        cv.poly([(0, 0), (XM(dy), V_Y), (XM(xmax) * 0.99, V_Y)], col, 4.0)
        cv.dot((XM(dmax), V_STAR), 5.8, col)
        ok = dmax <= D_LIMIT
        y0 = cv.Y(V_STAR) + (26 if ok else -64)
        cv.text_px(cv.X(XM(dmax)) + 12, y0,
                   f"結構 {nm}：k = {k:.0f} kN/mm", 12.5, col, "start", weight="700")
        cv.text_px(cv.X(XM(dmax)) + 12, y0 + 20,
                   f"Δ = {dmax:.1f} mm ，θ = 1/{H_STORY/dmax:.0f}", 12, col, "start")
        cv.text_px(cv.X(XM(dmax)) + 12, y0 + 40,
                   ("位移角合格 ✓" if ok else "位移角不合格 ×"), 12.5,
                   C["bmd"] if ok else C["load"], "start", weight="700")
        cv.line((XM(dmax), 0), (XM(dmax), V_STAR), col, 1.3, dash="3 4")

    for v in (0, 60, 120, 180):
        cv.line((-0.012 * XSC * xmax, v), (0.012 * XSC * xmax, v), C["muted"], 1.2)
        cv.text_px(cv.X(0) - 12, cv.Y(v), f"{v}", 11.5, C["muted"], "end")
    for d_ in (0, 10, 20, 30, 40):
        if d_ <= xmax:
            cv.text_px(cv.X(XM(d_)), cv.Y(0) + 20, f"{d_}", 11.5, C["muted"])

    cv.text_px(W / 2, HH - 26,
               "攔錯：以為「V* 保證彈性」就不必再檢核位移。V* 管的是強度（不降伏），"
               "位移角管的是勁度（不過度變形）",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2012-3-fig-1-strength-vs-stiffness.svg")


# ══════════════════════════════════════════════════════════
# 圖 2：扭轉不規則性 —— CM/CR 偏心與兩端位移比
# ══════════════════════════════════════════════════════════
def fig2():
    PW, PH = 640, 430

    # ── 上：平面配置 ───────────────────────────────────────
    def plan():
        Lm, Rm, Tm, Bm = 70, 70, 92, 92
        sx = min((PW - Lm - Rm) / (B + 1.0), (PH - Tm - Bm) / (D + 7.0))
        cv = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm)
        cv.panel("平面配置", f"Y 向構架 {FRAME_K[0]:.0f}k : {FRAME_K[1]:.0f}k : "
                             f"{FRAME_K[2]:.0f}k，剛心被拉向左側")
        cv.poly([(0, 0), (B, 0), (B, D), (0, D), (0, 0)], C["member"], 3.0)
        for x, k in zip(FRAME_X, FRAME_K):
            cv.line((x, 0), (x, D), C["member"], 2.2 + 3.0 * k / max(FRAME_K), cap="butt")
            cv.text_px(cv.X(x), cv.Y(D) + 20, f"{k:.0f}k", 12, C["member"], weight="700")
        cv.dot((X_CR, D / 2), 7.2, C["bmd"])
        cv.dot((X_CM, D / 2), 7.2, C["load"])
        cv.text_px(cv.X(X_CR) - 10, cv.Y(D / 2) - 20, "CR 剛心", 12.5, C["bmd"], "end",
                   weight="700")
        cv.text_px(cv.X(X_CM) + 10, cv.Y(D / 2) - 20, "CM 質心", 12.5, C["load"], "start",
                   weight="700")
        cv.dim((X_CR, D / 2), (X_CM, D / 2), f"e = {ECC:.2f} m", off=40, size=13)
        cv.arrow((X_CM, -4.6), (X_CM, -0.5), C["load"], 3.4, 11)
        cv.text_px(cv.X(X_CM) + 12, cv.Y(-2.8), "V（作用於 CM）", 12.5, C["load"], "start",
                   weight="700")
        cv.moment_arrow((X_CR, D / 2 + 3.2), r=26, ccw=False, color=C["accent"], w=2.6,
                        span=240, start=120)
        cv.text_px(cv.X(X_CR), cv.Y(D / 2 + 3.2) - 42, f"T = V·e",
                   12.5, C["accent"], weight="700")
        cv.text_px(cv.X(B / 2), cv.Y(D + 2.4), f"B = {B:.0f} m", 12, C["dim"])
        return cv

    # ── 下：樓板兩端的位移剖面 ─────────────────────────────
    def profile():
        Lm, Rm, Tm, Bm = 70, 138, 92, 92
        ymax = max(DELTA) * 1.30
        sy = (PH - Tm - Bm) / ymax
        XSC = (PW - Lm - Rm) / (sy * B)
        cv = Canvas(PW, PH, sx=sy, ox=Lm, oy=Bm)
        XM = lambda x: x * XSC
        cv.panel("樓板位移剖面 Δ(x)", "純平移 + 繞 CR 的轉動")
        cv.axes((0, 0), XM(B) * 1.05, ymax * 0.96, ("x (m)", "Δ"), C["muted"], 1.6)

        # 純平移的參考
        cv.line((0, D_TRANS), (XM(B), D_TRANS), C["ghost"], 2.6, dash="7 5")
        cv.text_px(cv.X(XM(B)) + 8, cv.Y(D_TRANS), f"純平移 {D_TRANS:.3f}", 11.8,
                   C["muted"], "start")
        # 實際（平移 + 轉動）
        cv.poly([(XM(0), DELTA[0]), (XM(B), DELTA[-1])], C["deform"], 4.0)
        for x, d in zip(FRAME_X, DELTA):
            cv.dot((XM(x), d), 5.2, C["deform"])
            cv.line((XM(x), 0), (XM(x), d), C["border"], 1.2, dash="3 4")
            cv.text_px(cv.X(XM(x)), cv.Y(0) + 18, f"{x:.0f}", 11.5, C["muted"])
        cv.text_px(cv.X(XM(0)) + 8, cv.Y(DELTA[0]) + 20, f"Δ = {DELTA[0]:.3f}",
                   12, C["deform"], "start", weight="700")
        cv.text_px(cv.X(XM(B)) + 8, cv.Y(DELTA[-1]), f"Δmax = {DELTA[-1]:.3f}",
                   12, C["deform"], "start", weight="700")
        # Δavg 與 1.2Δavg
        for val, lab, col in ((D_AVG, f"Δavg = {D_AVG:.3f}", C["muted"]),
                              (1.2 * D_AVG, f"1.2 Δavg = {1.2*D_AVG:.3f}", C["accent"])):
            cv.line((0, val), (XM(B), val), col, 1.8, dash="5 4")
            cv.text_px(cv.X(XM(B)) + 8, cv.Y(val), lab, 11.8, col, "start",
                       weight="700" if col == C["accent"] else "400")
        cv.dot((XM(B), DELTA[-1]), 6.6, C["accent"])
        cv.text_px(PW / 2, PH - 30,
                   f"Δmax / Δavg = {RATIO:.3f} ＞ 1.2 → 判定為扭轉不規則",
                   12.5, C["accent"], weight="700")
        return cv

    compose([plan(), profile()], cols=2,
            title="圖 2　扭轉不規則性：Δmax ＞ 1.2 Δavg 的來源是 CM 與 CR 的偏心",
            sub=f"平面 {B:.0f} m × {D:.0f} m｜CR = {X_CR:.2f} m、CM = {X_CM:.2f} m、"
                f"e = {ECC:.2f} m｜扭轉勁度 J = Σk(x−x_CR)² = {J_T:.0f}k｜"
                f"偶然偏心 ±0.05B = ±{ECC_ACC:.1f} m｜Ax = {A_X:.2f}（不必大於 3.0）",
            note="攔錯：只寫「靜力法不準」。真正的原因是平移與扭轉振態耦合且頻率接近，"
                 "±5% 偶然偏心與 Ax 都只是靜態補償，取代不了 CQC 對相位差的處理",
            path=f"{OUT}/SD-2012-3-fig-2-torsion-plan.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2()
    print(f"[圖1] Δ限值={D_LIMIT:.1f}mm  A: Δ={D_A:.1f} θ={TH_A:.5f}  "
          f"B: Δ={D_B:.1f} θ={TH_B:.5f}")
    print(f"[圖2] CR={X_CR:.2f} CM={X_CM:.2f} e={ECC:.2f} J={J_T:.1f} "
          f"Δ=({DELTA[0]:.4f},{DELTA[1]:.4f},{DELTA[-1]:.4f}) "
          f"Δmax/Δavg={RATIO:.4f} Ax={A_X:.3f}")
