#!/usr/bin/env python3
"""
SD-2017-2 三自由度門形構架 — 解題圖解產生腳本

用法：python3 gen_SD-2017-2.py [輸出目錄]

2026-08-22 勘誤：附圖的 v2、v3 弧形箭頭為「順時針正」，
此慣例下 K12 = K13 = -6EI1/h^2（原解寫成 +）。
fig-1 把三個單位位移狀態逐格畫出、fig-2 用實際變形形狀反查符號，
兩張圖都能獨立戳破符號寫反。
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, compose, column_shape, beam_shape

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2017-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2017-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §4 Step 4 全域勁度矩陣（v1 向右正；v2、v3 順時針 CW 正）
K11 = "24EI_{1}/h^{3}"
K12 = "-6EI_{1}/h^{2}"      # ← CW 正 → 負號（原解誤為 +）
K22 = "4EI_{1}/h + 4EI_{2}/l"
K23 = "2EI_{2}/l"

# §5.1 靜態凝縮：v2 = v3 = c/(A+B)·v1 > 0（節點順時針轉）
#   c = 6EI1/h^2、A = 4EI1/h + 4EI2/l、B = 2EI2/l
#   k_eff = 24EI1/h^3 - 72E^2I1^2 /[h^4 (4EI1/h + 6EI2/l)]
#   極限：EI2→∞ → 24EI1/h^3；EI2→0 → 6EI1/h^3
K_EFF_RIGID = 24.0          # 剛性梁（剪力構架）
K_EFF_FREE  = 6.0           # 無梁束制（兩根懸臂柱 = 2 × 3EI/h^3）

# 繪圖用（純視覺，不影響上列任何物理量）
# 取一組具體的梁柱勁度比來畫變形形狀：rho = (EI2/l)/(EI1/h)
RHO   = 1.0
# theta_cw / (v1/h) = 6 / (4 + 6*rho)  ← 由 §5.1 的 v2 = c/(A+B) v1 化為無因次
TH_OVER_D = 6.0 / (4.0 + 6.0 * RHO)     # = 0.6
D_DRAW  = 0.20                          # 繪圖側移量（模型單位，h = 1）
TH_CW   = TH_OVER_D * D_DRAW            # 順時針正
TH_CCW  = -TH_CW                        # column_shape / beam_shape 吃逆時針正

MW = 6.5
LSPAN = 1.35        # 跨度 l / 柱高 h（繪圖比例，依附圖）


def _frame(cv, color=C["member"], w=MW, dash=None):
    for s, e in (((0, 0), (0, 1)), ((0, 1), (LSPAN, 1)), ((LSPAN, 1), (LSPAN, 0))):
        cv.line(s, e, color, w, dash=dash, cap="butt")


def _ghost(cv):
    _frame(cv, C["ghost"], 3.0, dash="6 5")


# ══════════════════════════════════════════════════════════
def _unit_panel(idx):
    """idx = 1,2,3 → v1=1（側移）／v2=1（右節點 CW）／v3=1（左節點 CW）"""
    cv = Canvas(560, 470, sx=250, ox=115, oy=115, bg=C["panel"])
    titles = {1: "狀態 1：v1 = 1（側移），轉角鎖住",
              2: "狀態 2：v2 = 1（右節點 CW）",
              3: "狀態 3：v3 = 1（左節點 CW）"}
    subs = {1: "K11 = 24EI1/h^3　K21 = K31 = -6EI1/h^2",
            2: "K22 = 4EI1/h + 4EI2/l　K12 = -6EI1/h^2",
            3: "K33 = 4EI1/h + 4EI2/l　K13 = -6EI1/h^2"}
    cv.panel(titles[idx], subs[idx])
    _ghost(cv)
    cv.fixed_support((0, 0), size=19); cv.fixed_support((LSPAN, 0), size=19)

    D = 0.22
    T = 0.26                       # 繪圖用單位轉角（順時針正）
    if idx == 1:
        dl = dr = D; tl = tr = 0.0
    elif idx == 2:
        dl = dr = 0.0; tl, tr = 0.0, T
    else:
        dl = dr = 0.0; tl, tr = T, 0.0

    # column_shape 吃逆時針正 → 取負
    cv.poly(column_shape((0, 0), 1.0, dl, -tl), C["deform"], 5.0)
    cv.poly(column_shape((LSPAN, 0), 1.0, dr, -tr), C["deform"], 5.0)
    cv.poly(beam_shape((dl, 1), LSPAN, -tl, -tr), C["deform"], 5.0)

    # 標示施加的單位位移
    if idx == 1:
        cv.arrow((LSPAN + 0.06, 1), (LSPAN + 0.34, 1), C["load"], 3.4, 11)
        cv.math((LSPAN + 0.34, 1), "v_{1}=1", 16, C["load"], "start", dx=9, weight="700")
    else:
        p = (LSPAN, 1) if idx == 2 else (0, 1)
        cv.moment_arrow(p, r=27, ccw=False, color=C["load"], w=2.8, span=235, start=205)
        cv.math_px(cv.X(p[0]) + (30 if idx == 2 else -84), cv.Y(p[1]) - 34,
                   "v_{%d}=1" % idx, 16, C["load"], "start", weight="700")

    # 為維持該狀態所需外加的「節點力矩」方向（＝勁度矩陣的耦合項）
    if idx == 1:
        for p in ((0, 1), (LSPAN, 1)):
            cv.moment_arrow(p, r=20, ccw=True, color=C["accent"], w=2.4,
                            span=230, start=25)
        cv.text_px(280, 396, "須外加「逆時針」力矩才能鎖住轉角",
                   13, C["accent"], weight="700")
        cv.text_px(280, 418, "→ 在 CW 正慣例下記為負值",
                   13, C["accent"], weight="700")
    return cv


def fig1_unit_states():
    """勁度矩陣三行的物理意義；狀態 1 直接讀出 K12、K13 的符號"""
    path = f"{OUT}/{TAG}-fig-1-unit-states.svg"
    compose([_unit_panel(1), _unit_panel(2), _unit_panel(3)], cols=3,
            title="勁度矩陣的三個單位位移狀態（灰虛線＝原始位置）",
            sub="符號慣例：v1 向右為正；v2、v3 依附圖弧形箭頭取「順時針（CW）為正」",
            note="狀態 1 是判斷符號的關鍵：柱頂右移且不許轉動時，柱端彎矩為逆時針 6EI1/h^2，"
                 "在 CW 正慣例下記為 -6EI1/h^2",
            path=path)
    return path


# ══════════════════════════════════════════════════════════
def fig2_deflected():
    """實際側移變形：節點順時針轉、柱呈雙曲率 → 靜態凝縮的 v2 必為正"""
    cv = Canvas(880, 500, sx=290, ox=175, oy=125, bg="#FFFFFF")
    _ghost(cv)
    cv.fixed_support((0, 0), size=21); cv.fixed_support((LSPAN, 0), size=21)

    cv.poly(column_shape((0, 0), 1.0, D_DRAW, TH_CCW), C["deform"], 5.6)
    cv.poly(column_shape((LSPAN, 0), 1.0, D_DRAW, TH_CCW), C["deform"], 5.6)
    cv.poly(beam_shape((D_DRAW, 1), LSPAN, TH_CCW, TH_CCW), C["deform"], 5.6)

    cv.arrow((LSPAN + 0.06, 1), (LSPAN + 0.36, 1), C["load"], 3.6, 12)
    cv.math((LSPAN + 0.36, 1), "v_{1}", 18, C["load"], "start", dx=10, weight="700")

    for p, lab, dx in (((D_DRAW, 1), "v_{3}", -96), ((LSPAN + D_DRAW, 1), "v_{2}", 34)):
        cv.moment_arrow(p, r=26, ccw=False, color=C["accent"], w=2.8, span=235, start=205)
        cv.math_px(cv.X(p[0]) + dx, cv.Y(1) - 40, lab + " > 0", 16, C["accent"],
                   "start", weight="700")

    # 柱的反曲點：純側移＋端點轉角的三次形狀，位置由 TH_OVER_D 算出
    # w(xi) = D(3xi^2-2xi^3) + theta_cw*h*(xi^3 - xi^2)  → w''=0
    #   6D(1-2xi) + TH_CW*(6xi-2) = 0
    a = TH_CW
    xi_inf = (6 * D_DRAW - 2 * a) / (12 * D_DRAW - 6 * a)
    u_inf = D_DRAW * (3 * xi_inf ** 2 - 2 * xi_inf ** 3) + a * (xi_inf ** 3 - xi_inf ** 2)
    for x0 in (0.0, LSPAN):
        cv.dot((x0 + u_inf, xi_inf), 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.8)
    cv.math_px(cv.X(LSPAN + u_inf) + 16, cv.Y(xi_inf),
               "反曲點 ξ = %.3f" % xi_inf, 14, C["accent"], "start", weight="700")

    cv.text_px(440, 452,
               "門形構架向右側移時，兩個節點都是「順時針」轉；"
               "若靜態凝縮解出 v2 為負，代表符號慣例某處寫反了",
               13.5, C["muted"])
    cv.text_px(440, 474,
               "本圖取 (EI2/l)/(EI1/h) = %.1f，故 v2/(v1/h) = 6/(4+6ρ) = %.3f（由 §5.1 公式算出）"
               % (RHO, TH_OVER_D), 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-deflected.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(f"  θ_cw/(v1/h) = {TH_OVER_D:.4f}   k_eff 極限 = {K_EFF_FREE:g}~{K_EFF_RIGID:g} EI1/h^3")
    for f in (fig1_unit_states, fig2_deflected):
        print(" ", f())
