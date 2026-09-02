#!/usr/bin/env python3
"""SD-2025-1 圖解產生器 — 等效靜力法：樓層力分配、剪力/傾覆彎矩、等效高度
所有數值由本檔頂端的題目條件算出，不得手填。改任一輸入重跑，圖形自動跟著變。
"""
import sys, os
SKILL = os.environ.get("STRUCTDRAW",
    "/root/.claude/skills/synced/ac6f22be-8f8e-4e9a-b5a5-57a76b0ea389_ed8ec2e9-4a34-4076-aef8-82296cfdbb5c/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose
from recipes import bar_compare

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ── L1：題目直接給定（SD-2025-1 §1）──────────────────────────
I, S_aD, ALPHA_Y, FU = 1.25, 0.6, 1.4, 2.0
W_TOT, N, HS = 160.0, 8, 3.5
T = 0.8

# ── 由 §4 解出（此處重算，圖上數字即這些變數）────────────────
H   = N * HS                                   # 28 m
w   = [W_TOT / N] * N                          # 每層 20 kN
h   = [HS * (i + 1) for i in range(N)]         # 3.5, 7.0, ... 28.0
V0  = I * S_aD / (1.4 * ALPHA_Y * FU) * W_TOT  # 30.612 kN
FT  = 0.07 * T * V0 if T > 0.7 else 0.0        # 1.714 kN
FT_CAP = 0.25 * V0
assert FT <= FT_CAP
VP  = V0 - FT                                  # 28.898 kN
SWH = sum(wi * hi for wi, hi in zip(w, h))     # 2520 kN·m
SWH2 = sum(wi * hi * hi for wi, hi in zip(w, h))  # 49980 kN·m^2
F   = [wi * hi / SWH * VP for wi, hi in zip(w, h)]
F_TOP_TOTAL = F[-1] + FT
M0  = sum(f * hi for f, hi in zip(F, h)) + FT * H
HEQ = M0 / V0
HEQ_DISCRETE = SWH2 / SWH                      # 不含 Ft 的離散等效高度


def story_shear(z):
    """z 高度處的樓層剪力 = 其上所有水平力之和"""
    return sum(f for f, hi in zip(F, h) if hi > z + 1e-9) + (FT if H > z + 1e-9 else 0.0)


def overturning(z):
    """z 高度處的傾覆彎矩"""
    return (sum(f * (hi - z) for f, hi in zip(F, h) if hi > z + 1e-9)
            + (FT * (H - z) if H > z + 1e-9 else 0.0))


# ══════════════════════════════════════════════════════════
# 圖 1：樓層水平力分配（含頂部集中力 Ft）
# ══════════════════════════════════════════════════════════
def fig1():
    W, HH = 900, 800
    BW = 8.0                                  # 構架繪圖寬度（模型單位）
    ARR_MAX, ARR_MIN = 5.4, 1.3               # 箭頭長度範圍（模型單位）
    xmin, xmax = -(ARR_MAX + 1.6), BW
    L, R, TT, B = 158, 262, 100, 104
    sx = min((W - L - R) / (xmax - xmin), (HH - TT - B) / H)
    cv = Canvas(W, HH, sx=sx, ox=L - xmin * sx, oy=B)

    cv.text_px(W / 2, 34, "圖 1　設計水平力的豎向分配", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, "頂部集中力 Ft 先扣除，剩下的 V′ 才按 w·h 加權分配", 13, C["muted"])

    # 構架
    for xc in (0.0, BW):
        cv.line((xc, 0), (xc, H), C["member"], 3.4, cap="butt")
        cv.fixed_support((xc, 0), 0, 20, C["member"])
    for hi in h:
        cv.line((0, hi), (BW, hi), C["member"], 3.4, cap="butt")

    fmax = F_TOP_TOTAL
    for i, (f, hi) in enumerate(zip(F, h)):
        ln = ARR_MIN + (ARR_MAX - ARR_MIN) * f / fmax
        cv.arrow((-ln, hi), (0, hi), C["load"], 3.0, 10)
        cv.dot((0, hi), 4.2, C["member"])
        cv.math_px(cv.X(BW) + 16, cv.Y(hi) - 9,
                   f"F_{{{i+1}}} = {f:.3f} kN", 14.5, C["load"], "start", weight="700")
        cv.text_px(cv.X(BW) + 16, cv.Y(hi) + 11,
                   f"h = {hi:.1f} m ，w·h = {w[i]*hi:.0f}", 11.8, C["muted"], "start")

    # 頂部集中力 Ft：接在 F8 箭頭尾端，視覺上顯示「頂層總力 = F8 + Ft」
    ln8 = ARR_MIN + (ARR_MAX - ARR_MIN) * F[-1] / fmax
    ln_t = (ARR_MAX - ARR_MIN) * FT / fmax
    cv.arrow((-(ln8 + ln_t), H), (-ln8, H), C["accent"], 3.0, 10)
    cv.math_px(L - 12, cv.Y(H) - 10, f"F_t = {FT:.3f} kN", 14.5, C["accent"], "end", weight="700")
    cv.text_px(L - 12, cv.Y(H) + 11, f"= 0.07 × {T} × V0", 11.8, C["accent"], "end")
    cv.text_px(cv.X(BW) + 16, cv.Y(H) + 30,
               f"頂層合力 F8 + Ft = {F_TOP_TOTAL:.3f} kN", 12.6, C["accent"], "start", weight="700")

    # 尺寸
    cv.dim((BW, 0), (BW, HS), f"{HS} m", off=-44, size=13)
    cv.math_px(L - 12, cv.Y(H * 0.52), f"H = {H:.0f} m", 14, C["dim"], "end")
    cv.text_px(L - 12, cv.Y(H * 0.52) + 18, "（8 層 × 3.5 m）", 11.5, C["dim"], "end")

    # 基底剪力
    cv.arrow((0.4, -1.5), (4.2, -1.5), C["sfd"], 3.4, 11)
    cv.math_px(cv.X(4.4), cv.Y(-1.5), f"V0 = {V0:.2f} kN", 15, C["sfd"], "start", weight="700")

    # 檢核方塊
    bx, by, bw_, bh_ = 22, HH - 236, 246, 158
    cv.rect_px(bx, by, bw_, bh_, C["panel"], 12, C["border"], 1.2)
    cv.text_px(bx + 14, by + 26, "驗算", 13.5, C["text"], "start", weight="700")
    lines = [
        (f"ΣF = {sum(F):.3f} = V′  ✓", C["load"]),
        (f"V′ = V0 − Ft = {V0:.3f} − {FT:.3f}", C["muted"]),
        (f"Σ w·h = {SWH:.0f} kN·m", C["muted"]),
        (f"Ft ≤ 0.25 V0 = {FT_CAP:.2f}  ✓", C["accent"]),
        ("Ft 不進入 Σ w·h 的分配", C["accent"]),
    ]
    for k, (s_, col) in enumerate(lines):
        cv.text_px(bx + 14, by + 54 + k * 21, s_, 12.6, col, "start")

    cv.text_px(W / 2, HH - 26,
               "攔錯：T = 0.8 s > 0.7 s 必須計 Ft；且 Ft 是先扣除、不進入 Σ w·h 分配",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2025-1-fig-1-force-dist.svg")


# ══════════════════════════════════════════════════════════
# 圖 2：樓層剪力圖與傾覆彎矩圖
# ══════════════════════════════════════════════════════════
def fig2():
    PW, PH = 430, 640
    L, R, TT, B = 92, 116, 92, 78
    sy = (PH - TT - B) / H
    VU = (PW - L - R) / max(V0, 1e-9) / sy          # 模型單位 / kN
    MU = (PW - L - R) / max(M0, 1e-9) / sy          # 模型單位 / (kN·m)

    def panel(kind):
        unit = VU if kind == "V" else MU
        col = C["sfd"] if kind == "V" else C["bmd"]
        fillc = C["fill_s"] if kind == "V" else C["fill_m"]
        cv = Canvas(PW, PH, sx=sy, ox=L, oy=B)
        cv.panel("樓層剪力 V(z)" if kind == "V" else "傾覆彎矩 M(z)",
                 "上方各力之和" if kind == "V" else "上方各力對該高度取矩")
        # 縱軸
        cv.line((0, 0), (0, H + 1.2), C["muted"], 1.6)
        cv.math_px(cv.X(0), cv.Y(H + 1.2) - 14, "z", 14, C["muted"])
        for hi in [0] + h:
            cv.line((-0.28, hi), (0.28, hi), C["muted"], 1.2)
            cv.text_px(cv.X(0) - 12, cv.Y(hi), f"{hi:.1f}", 11, C["muted"], "end")

        # 曲線：在每個樓層高度上下取值（剪力為階梯，彎矩為折線）
        pts = []
        zs = []
        for k in range(N, -1, -1):
            z_hi = h[k - 1] if k > 0 else 0.0
            zs.append(z_hi)
        zs = sorted(set([0.0] + h))
        if kind == "V":
            poly = [(0.0, H)]
            for z in sorted(zs, reverse=True):
                vv = story_shear(z - 1e-6) if z > 0 else story_shear(-1e-6)
                poly.append((story_shear(z + 1e-6) * unit, z))
                poly.append((vv * unit, z))
            poly.append((0.0, 0.0))
            cv.polygon(poly, fillc, col, 2.4)
            for z in sorted(zs, reverse=True):
                v = story_shear(z - 1e-6)
                if z == 0:
                    continue
                cv.text_px(cv.X(v * unit) + 8, cv.Y(z) + 10, f"{v:.2f}", 11.5, col, "start")
            cv.math_px(cv.X(V0 * unit) + 10, cv.Y(0) + 30,
                       f"V0 = {V0:.2f} kN", 14.5, col, "end", weight="700")
            cv.dot((V0 * unit, 0), 5.0, col)
        else:
            zz = [j * H / 200 for j in range(201)]
            pts = [(overturning(z) * unit, z) for z in zz]
            cv.polygon([(0, H)] + pts + [(0, 0)], fillc, col, 2.4)
            cv.math_px(cv.X(M0 * unit) + 10, cv.Y(0) + 30,
                       f"M0 = {M0:.1f} kN·m", 14.5, col, "end", weight="700")
            cv.dot((M0 * unit, 0), 5.0, col)
            # 等效高度
            cv.line((0, HEQ), (M0 * unit * 0.92, HEQ), C["accent"], 2.0, dash="7 5")
            cv.arrow((M0 * unit * 0.55, HEQ), (M0 * unit * 0.20, HEQ), C["accent"], 2.6, 9)
            cv.math_px(cv.X(M0 * unit * 0.58), cv.Y(HEQ) - 12,
                       f"h_eq = M0/V0 = {HEQ:.2f} m", 13, C["accent"], "start",
                       weight="700")
            # Ft 的貢獻
            cv.math_px(cv.X(0) + 14, cv.Y(H * 0.90),
                       f"其中 Ft·H = {FT*H:.1f} kN·m", 12.5, C["accent"], "start")
        return cv

    svg = compose([panel("V"), panel("M")], cols=2,
                  title="圖 2　樓層剪力與傾覆彎矩沿高度的分布",
                  sub=f"基底 V0 = {V0:.2f} kN、M0 = {M0:.1f} kN·m",
                  note=f"攔錯：M0 必須含 Ft·H = {FT*H:.1f} kN·m 這一項，漏掉會少算 {FT*H/M0*100:.1f}%",
                  path=f"{OUT}/SD-2025-1-fig-2-shear-moment.svg")
    return svg


# ══════════════════════════════════════════════════════════
# 圖 3：等效高度的三種來源
# ══════════════════════════════════════════════════════════
def fig3():
    cases = [
        ("連續倒三角形（理論）", "質量連續分布",
         2 * H / 3, f"2H/3 = {2*H/3:.2f} m = 0.667H", C["member2"]),
        ("8 層離散樓層（不含 Ft）", "集中質量抬高合力點",
         HEQ_DISCRETE, f"Σwh^{{2}}/Σwh = {HEQ_DISCRETE:.2f} m = {HEQ_DISCRETE/H:.3f}H", C["deform"]),
        ("本題（含 Ft）", "Ft 再抬一次",
         HEQ, f"M0/V0 = {HEQ:.2f} m = {HEQ/H:.3f}H", C["accent"]),
    ]
    bar_compare(cases,
                title="圖 3　等效高度 h_{eq} 的三個來源",
                sub="0.725H 不是全由 Ft 造成——離散化本身已貢獻 0.708H",
                note=f"攔錯：把「不是 2H/3」全歸因於 Ft。Ft 只再加 {HEQ/H - HEQ_DISCRETE/H:.3f}H",
                path=f"{OUT}/SD-2025-1-fig-3-heq-compare.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2(); fig3()
    print(f"V0={V0:.4f} Ft={FT:.4f} V'={VP:.4f} M0={M0:.3f} heq={HEQ:.3f} ({HEQ/H:.4f}H)")
    print("figs ->", OUT)
