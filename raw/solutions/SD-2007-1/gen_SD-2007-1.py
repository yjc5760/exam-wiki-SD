#!/usr/bin/env python3
"""SD-2007-1 圖解產生器 — 韌性折減：等位移／等能量推導、Fu 週期分段、三層超強折減
圖上每個數字都由頂端的 R、αy 算出；改 R 重跑，三張圖同時更新。
"""
import sys, os, math
SKILL = os.environ.get("STRUCTDRAW",
    "/root/.claude/skills/synced/ac6f22be-8f8e-4e9a-b5a5-57a76b0ea389_ed8ec2e9-4a34-4076-aef8-82296cfdbb5c/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose
from recipes import bar_compare

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ── 示例參數（規範表 1-3 特殊抗彎矩構架；解說 2.9 之 RC 極限強度設計）──
R      = 4.8          # 結構系統韌性容量
ALPHA_Y = 1.5         # 起始降伏地震力放大倍數（RC 極限強度設計）
OVERSTR = 1.4         # 系統超強：首根構件降伏 → 全面塑化

RA      = 1 + (R - 1) / 1.5            # 容許韌性容量 = 3.533
FU_LONG = RA                            # 長週期（等位移）
FU_MID  = math.sqrt(2 * RA - 1)         # 中週期（等能量）
FU_SHORT = 1.0                          # 極短週期（等加速度）


def fu_of(x, ra=RA):
    """Fu 隨 x = T/T0D 的規範分段（式 2-12）"""
    fm, fl = math.sqrt(2 * ra - 1), ra
    if x >= 1.0:
        return fl
    if x >= 0.6:
        return fm + (fl - fm) * (x - 0.6) / 0.4
    if x >= 0.2:
        return fm
    return 1.0 + (fm - 1.0) * x / 0.2


# ══════════════════════════════════════════════════════════
# 圖 1：等位移原則 vs 等能量原則
# ══════════════════════════════════════════════════════════
def fig1():
    PW, PH = 500, 470
    K = 1.0
    UE = 1.0                      # 彈性系統最大位移（正規化）
    VE = K * UE                   # 彈性需求力

    def panel(kind):
        if kind == "disp":
            fu = FU_LONG
            vy = VE / fu
            uy = vy / K
            umax = UE                       # 等位移
        else:
            fu = FU_MID
            vy = VE / fu
            uy = vy / K
            umax = RA * uy                  # 延性需求 = Ra
        xmax = max(UE, umax) * 1.30
        ymax = VE * 1.22
        Lm, Rm, Tm, Bm = 78, 116, 92, 76
        sx = min((PW - Lm - Rm) / xmax, (PH - Tm - Bm) / ymax)
        cv = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm)
        cv.panel("長週期：等位移原則" if kind == "disp" else "中週期：等能量原則",
                 f"Fu = Ra = {fu:.3f}" if kind == "disp"
                 else f"Fu = √(2Ra−1) = {fu:.3f}")
        cv.axes((0, 0), xmax * 0.99, ymax * 0.99, ("u", "V"), C["muted"], 1.6)

        # 彈塑性系統（雙線性）
        if kind == "energy":
            cv.polygon([(0, 0), (uy, vy), (umax, vy), (umax, 0)], C["fill_c"], "none")
        cv.poly([(0, 0), (uy, vy), (umax, vy)], C["deform"], 4.2)
        # 彈性系統
        if kind == "energy":
            cv.polygon([(0, 0), (UE, VE), (UE, 0)], C["fill_t"], "none")
        cv.poly([(0, 0), (UE, VE)], C["load"], 3.2, dash="8 5")

        cv.dot((uy, vy), 5.0, C["deform"])
        cv.dot((UE, VE), 5.0, C["load"])
        cv.dot((umax, vy), 5.0, C["accent"])

        # 標註
        cv.line((0, VE), (UE, VE), C["muted"], 1.2, dash="4 4")
        cv.line((0, vy), (uy, vy), C["muted"], 1.2, dash="4 4")
        cv.math_px(cv.X(0) - 10, cv.Y(VE), "V_e", 14.5, C["load"], "end", weight="700")
        cv.math_px(cv.X(0) - 10, cv.Y(vy), "V_y", 14.5, C["deform"], "end", weight="700")
        cv.line((uy, 0), (uy, vy), C["muted"], 1.2, dash="4 4")
        cv.line((umax, 0), (umax, vy), C["muted"], 1.2, dash="4 4")
        cv.math_px(cv.X(uy), cv.Y(0) + 20, "u_y", 14, C["deform"])
        cv.math_px(cv.X(umax), cv.Y(0) + 20, "u_{max}", 14, C["accent"])
        if kind == "disp":
            cv.double_arrow((uy, VE * 1.10), (UE, VE * 1.10), C["accent"], 2.2, 8)
            cv.text_px(cv.X((uy + UE) / 2), cv.Y(VE * 1.10) - 14,
                       "兩者最大位移相同", 12.5, C["accent"], weight="700")
            note = f"V_e/V_y = μ = Ra = {fu:.3f}"
        else:
            cv.text_px(cv.X(UE * 0.42), cv.Y(VE * 0.62), "彈性三角形", 12, C["load"], weight="700")
            cv.text_px(cv.X(umax * 0.66), cv.Y(vy * 0.42), "彈塑性梯形", 12, C["deform"], weight="700")
            e_el = 0.5 * VE * UE
            e_ip = 0.5 * vy * uy + vy * (umax - uy)
            note = f"面積相等：{e_el:.3f} = {e_ip:.3f}  ✓"
        cv.text_px(PW / 2, PH - 30, note, 13, C["text"], weight="700")
        return cv

    compose([panel("disp"), panel("energy")], cols=2,
            title="圖 1　韌性折減係數 Fu 的兩個力學假設",
            sub=f"以 R = {R}（特殊抗彎矩構架）→ Ra = 1+(R−1)/1.5 = {RA:.3f} 為例",
            note="攔錯：兩個原則的適用週期段搞反。長週期看位移、中週期看面積（能量）",
            path=f"{OUT}/SD-2007-1-fig-1-equal-disp-energy.svg")


# ══════════════════════════════════════════════════════════
# 圖 2：Fu 隨週期的規範分段
# ══════════════════════════════════════════════════════════
def fig2():
    W, HH = 940, 560
    XR, ymax = 1.55, RA * 1.22
    L, R_, T_, B = 96, 210, 100, 108
    sx = (HH - T_ - B) / ymax
    XSC = (W - L - R_) / (sx * XR)          # 橫軸壓縮比（讓等向 sx 也能撐滿寬度）
    cv = Canvas(W, HH, sx=sx, ox=L, oy=B)
    XM = lambda x: x * XSC                   # T/T0D → 模型座標

    cv.text_px(W / 2, 34, "圖 2　Fu 隨結構週期的規範分段（式 2-12）", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, f"R = {R} → Ra = {RA:.3f}；橫軸為 T / T0D，T0D = SD1/SDS",
               13, C["muted"])

    cv.axes((0, 0), XM(XR) * 0.99, ymax * 0.99, ("T/T0D", "F_u"), C["muted"], 1.8)

    zones = [(0.0, 0.2, "內插", C["muted"]),
             (0.2, 0.6, "等能量 √(2Ra−1)", C["bmd"]),
             (0.6, 1.0, "線性內插", C["muted"]),
             (1.0, XR, "等位移 Ra", C["load"])]
    for x0, x1, lab, col in zones:
        if x0 > 0:
            cv.line((XM(x0), 0), (XM(x0), ymax * 0.90), C["border"], 1.6, dash="6 5")
        cv.text_px(cv.X(XM((x0 + x1) / 2)), cv.Y(ymax * 0.955), lab, 12.5, col, weight="700")
    cv.text_px(cv.X(XM(0.1)), cv.Y(ymax * 0.86), "等加速度區", 11.5, C["muted"])

    for xb, lab in ((0.2, "0.2 T0D"), (0.6, "0.6 T0D"), (1.0, "T0D")):
        cv.text_px(cv.X(XM(xb)), cv.Y(0) + 22, lab, 12.5, C["muted"])

    xs = [i * XR / 400 for i in range(401)]
    R2 = 2.4
    RA2 = 1 + (R2 - 1) / 1.5
    cv.poly([(XM(x), fu_of(x, RA2)) for x in xs], C["member2"], 3.0, dash="9 6")
    cv.poly([(XM(x), fu_of(x)) for x in xs], C["deform"], 4.4)

    for yv, lab, col in ((RA, f"Ra = {RA:.3f}", C["load"]),
                         (FU_MID, f"√(2Ra−1) = {FU_MID:.3f}", C["bmd"]),
                         (1.0, "Fu = 1.0（不折減）", C["muted"])):
        cv.line((0, yv), (XM(XR) * 0.99, yv), col, 1.4, dash="5 5")
        cv.math_px(cv.X(XM(XR) * 0.99) + 10, cv.Y(yv), lab, 13.5, col, "start", weight="700")

    for pt, col in (((1.0, RA), C["load"]), ((0.6, FU_MID), C["bmd"]),
                    ((0.2, FU_MID), C["bmd"]), ((0.0, 1.0), C["muted"])):
        cv.dot((XM(pt[0]), pt[1]), 5.4, col)

    for yv in range(0, int(ymax) + 1):
        cv.line((-0.02 * XSC, yv), (0.02 * XSC, yv), C["muted"], 1.2)
        cv.text_px(cv.X(0) - 12, cv.Y(yv), str(yv), 11.5, C["muted"], "end")

    cv.legend(cv.X(XM(0.66)), cv.Y(0.52),
              [(C["deform"], f"R = {R}（Ra = {RA:.2f}）"),
               (C["member2"], f"R = {R2}（Ra = {RA2:.2f}）")])
    cv.text_px(W / 2, HH - 26,
               "攔錯：以為短週期也能照 √(2Ra−1) 折減。T → 0 是等加速度區，Fu → 1.0，韌性完全幫不上忙",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2007-1-fig-2-fu-spectrum.svg")


# ══════════════════════════════════════════════════════════
# 圖 3：從設計地震力到彈性需求的三層放大
# ══════════════════════════════════════════════════════════
def fig3():
    V = 1.0
    PY = ALPHA_Y * V
    PU = OVERSTR * ALPHA_Y * V
    VE = FU_LONG * PU
    cases = [
        ("設計地震力 V", "設計斷面用",
         V, "V", C["member2"]),
        ("起始降伏側力 Py", "首根構件降伏",
         PY, f"P_y = α_yV = {PY:.2f}V", C["sfd"]),
        ("極限側力 Pu", "全面塑化",
         PU, f"P_u = 1.4α_yV = {PU:.2f}V", C["bmd"]),
        ("彈性地震力需求 Ve", "不許降伏時所需",
         VE, f"V_e = F_u·P_u = {VE:.2f}V", C["load"]),
    ]
    bar_compare(cases,
                title="圖 3　設計地震力與彈性需求之間的三層放大",
                sub=f"αy = {ALPHA_Y}（RC 極限強度設計）、1.4（系統超強）、Fu = Ra = {FU_LONG:.3f}（長週期）",
                note=f"攔錯：把 1.4 當載重因子、把 αy 當 ≤1 的折減。三者相乘 = {VE:.2f}，即規範式分母 1.4αyFu",
                path=f"{OUT}/SD-2007-1-fig-3-force-chain.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2(); fig3()
    print(f"R={R} Ra={RA:.4f} Fu_long={FU_LONG:.4f} Fu_mid={FU_MID:.4f} "
          f"Ve/V={FU_LONG*OVERSTR*ALPHA_Y:.3f}")
