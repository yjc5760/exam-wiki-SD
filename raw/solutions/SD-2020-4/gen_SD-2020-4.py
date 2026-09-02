#!/usr/bin/env python3
"""SD-2020-4 圖解產生器 — 三水準地震：需求 vs 設計力、V*/V 與 VM/V 隨 R、設計反應譜、韌性額度
圖上每個數字由 R 與規範關係式算出；改 R 重跑，四張圖同時更新。
"""
import sys, os, math
SKILL = os.environ.get("STRUCTDRAW",
    "/root/.claude/skills/synced/ac6f22be-8f8e-4e9a-b5a5-57a76b0ea389_ed8ec2e9-4a34-4076-aef8-82296cfdbb5c/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ── 規範關係（建築物耐震設計規範及解說）────────────────────────
RATIO_D_OVER_SMALL = 3.0      # 一般工址：4.2 = 1.4 × 3
RATIO_M_OVER_D     = 1.5      # SDS = (2/3)SMS  →  SaM = 1.5 SaD
R_MAIN, R_ALT      = 4.8, 2.4


def ra_of(R):
    return 1 + (R - 1) / 1.5


def fu_long(R):
    return ra_of(R)


def fu_mid(R):
    return math.sqrt(2 * ra_of(R) - 1)


def vstar_over_v(R, seg="long"):
    return (fu_long(R) if seg == "long" else fu_mid(R)) / RATIO_D_OVER_SMALL


def vm_over_v(R, seg="long"):
    """VM/V = 1.5 × Fu/FuM；長週期 Fu=Ra、FuM=R → 1+0.5/R"""
    if seg == "long":
        return RATIO_M_OVER_D * ra_of(R) / R
    return RATIO_M_OVER_D * math.sqrt((2 * ra_of(R) - 1) / (2 * R - 1))


# ══════════════════════════════════════════════════════════
# 圖 1：地震需求差很多，設計力卻差不多
# ══════════════════════════════════════════════════════════
def fig1():
    W, HH = 1040, 560
    cv = Canvas(W, HH, sx=1, bg="#FFFFFF")
    cv.text_px(W / 2, 34, "圖 1　三水準地震：需求相差 4.5 倍，設計力卻幾乎一樣",
               17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58,
               f"以 R = {R_MAIN}（特殊抗彎矩構架）、長週期段為例；設計地震力 V 取為 1.00",
               13, C["muted"])

    rows = [
        ("中小度地震", "回歸期約 30 年 ｜ 50 年超越機率約 80%", "小震不壞（結構體保持彈性）",
         1 / RATIO_D_OVER_SMALL, vstar_over_v(R_MAIN), "V*", C["sfd"]),
        ("設計地震", "回歸期 475 年 ｜ 50 年超越機率約 10%", "中震可修（韌性需求 ≤ Ra）",
         1.0, 1.0, "V", C["bmd"]),
        ("最大考量地震", "回歸期 2500 年 ｜ 50 年超越機率約 2%", "大震不倒（韌性可用滿 R）",
         RATIO_M_OVER_D, vm_over_v(R_MAIN), "VM", C["load"]),
    ]
    demand_peak = max(r[3] for r in rows)
    force_peak = max(r[4] for r in rows)
    xd, xf, bw = 372, 700, 250

    cv.text_px(xd + bw / 2, 100, "地震需求（譜加速度 Sa 相對值）", 13.5, C["text"], weight="700")
    cv.text_px(xf + bw / 2, 100, "設計檢核力（相對 V）", 13.5, C["text"], weight="700")

    for i, (name, prob, perf, dem, frc, sym, col) in enumerate(rows):
        y = 152 + i * 116
        cv.text_px(28, y - 12, name, 15, C["text"], "start", weight="700")
        cv.text_px(28, y + 10, prob, 11.8, C["muted"], "start")
        cv.text_px(28, y + 30, perf, 11.8, col, "start", weight="700")
        for x0, val, peak, lab in ((xd, dem, demand_peak, f"{dem:.2f}"),
                                   (xf, frc, force_peak, f"{sym} = {frc:.3f}")):
            cv.rect_px(x0, y - 17, bw, 34, "#EDF1F6", 8)
            cv.rect_px(x0, y - 17, bw * val / peak, 34, col, 8)
            cv.text_px(x0 + bw + 12, y, lab, 13.5, col, "start", weight="700")

    # 對照括號
    cv.text_px(xd + bw / 2, 500, f"最大 / 最小 = {RATIO_M_OVER_D*RATIO_D_OVER_SMALL:.1f} 倍",
               14, C["text"], weight="700")
    fr = [r[4] for r in rows]
    cv.text_px(xf + bw / 2, 500, f"最大 / 最小 = {max(fr)/min(fr):.2f} 倍",
               14, C["text"], weight="700")
    cv.text_px(W / 2, HH - 26,
               f"攔錯：以為 VM > V > V* 恆成立。本例的實際次序是 V* ({vstar_over_v(R_MAIN):.3f}) "
               f"> VM ({vm_over_v(R_MAIN):.3f}) > V (1.000)",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2020-4-fig-1-three-levels.svg")


# ══════════════════════════════════════════════════════════
# 圖 2：V*/V 與 VM/V 隨韌性容量 R 的變化
# ══════════════════════════════════════════════════════════
def fig2():
    W, HH = 940, 570
    R0, R1 = 1.0, 5.2
    ymax = 1.65
    L, R_, T_, B = 96, 218, 100, 104
    sx = (HH - T_ - B) / ymax
    XSC = (W - L - R_) / (sx * (R1 - R0))
    cv = Canvas(W, HH, sx=sx, ox=L, oy=B)
    XM = lambda r: (r - R0) * XSC

    cv.text_px(W / 2, 34, "圖 2　三個檢核力的相對大小隨韌性容量 R 變化", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, "縱軸為與設計地震力 V 的比值（V ≡ 1.00）", 13, C["muted"])

    cv.axes((0, 0), XM(R1) * 0.99, ymax * 0.99, ("R", "V_i/V"), C["muted"], 1.8)

    # V ≡ 1
    cv.line((0, 1.0), (XM(R1) * 0.99, 1.0), C["bmd"], 3.0)
    cv.math_px(cv.X(XM(R1) * 0.99) + 10, cv.Y(1.0), "V = 1.00（基準）", 13.5, C["bmd"],
               "start", weight="700")

    rs = [R0 + i * (R1 - R0) / 400 for i in range(401)]
    curves = [
        ([(XM(r), vstar_over_v(r, "long")) for r in rs], C["sfd"], 4.2, None,
         "V*/V ＝ Fu/3（長週期）"),
        ([(XM(r), vstar_over_v(r, "mid")) for r in rs], C["sfd"], 2.8, "9 6",
         "V*/V（中週期）"),
        ([(XM(r), vm_over_v(r, "long")) for r in rs], C["load"], 4.2, None,
         "VM/V ＝ 1 + 0.5/R（長週期）"),
    ]
    for pts, col, wdt, dsh, _ in curves:
        cv.poly(pts, col, wdt, dash=dsh)

    # 臨界點 R = 4.0（Fu = 3 → V* = V）
    RC = 4.0
    cv.line((XM(RC), 0), (XM(RC), 1.16), C["accent"], 2.0, dash="6 5")
    cv.dot((XM(RC), 1.0), 5.6, C["accent"])
    cv.text_px(cv.X(XM(RC)), cv.Y(1.22), f"R = {RC}", 13, C["accent"], weight="700")
    cv.text_px(cv.X(XM(RC)), cv.Y(1.30), "V* = V 的臨界", 11.8, C["accent"])

    # 主要標記點
    for R in (R_MAIN, R_ALT):
        cv.dot((XM(R), vstar_over_v(R, "long")), 5.2, C["sfd"])
        cv.dot((XM(R), vm_over_v(R, "long")), 5.2, C["load"])
        cv.text_px(cv.X(XM(R)), cv.Y(0) + 42, f"R = {R}", 12.5, C["text"], weight="700")

    for r in (1, 2, 3, 4, 5):
        cv.line((XM(r), -0.018), (XM(r), 0.018), C["muted"], 1.2)
        cv.text_px(cv.X(XM(r)), cv.Y(0) + 22, str(r), 11.5, C["muted"])
    for yv in (0.5, 1.0, 1.5):
        cv.line((-0.02 * XSC, yv), (0.02 * XSC, yv), C["muted"], 1.2)
        cv.text_px(cv.X(0) - 12, cv.Y(yv), f"{yv:.1f}", 11.5, C["muted"], "end")

    # 區域說明
    cv.text_px(cv.X(XM(4.55)), cv.Y(1.30), "V* ＞ V", 13, C["sfd"], weight="700")
    cv.text_px(cv.X(XM(3.4)), cv.Y(0.42), "V* ＜ V", 13, C["sfd"], weight="700")

    cv.legend(cv.X(XM(1.12)), cv.Y(0.42),
              [(c[1], c[4]) for c in curves] + [(C["bmd"], "V（設計地震，基準）")])
    cv.text_px(W / 2, HH - 26,
               "攔錯：直接拿表列的 R 當 Fu。R = 4.8 的 Fu 是 3.53（長週期）或 2.46（中週期），不是 4.8",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2020-4-fig-2-ratio-curve.svg")


# ══════════════════════════════════════════════════════════
# 圖 3：設計反應譜 SaD(T) 的四段式
# ══════════════════════════════════════════════════════════
def fig3():
    W, HH = 940, 540
    XR, ymax = 3.4, 1.32
    L, R_, T_, B = 96, 176, 100, 104
    sx = (HH - T_ - B) / ymax
    XSC = (W - L - R_) / (sx * XR)
    cv = Canvas(W, HH, sx=sx, ox=L, oy=B)
    XM = lambda x: x * XSC

    def sa(x):                       # SaD / SDS，x = T/T0D
        if x < 0.2:
            return 0.4 + 3 * x
        if x <= 1.0:
            return 1.0
        if x <= 2.5:
            return 1.0 / x
        return 0.4

    cv.text_px(W / 2, 34, "圖 3　設計反應譜 SaD(T) 的四段式", 17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, "縱軸為 SaD/SDS，橫軸為 T/T0D；T0D = SD1/SDS（地盤愈軟，T0D 愈大）",
               13, C["muted"])
    cv.axes((0, 0), XM(XR) * 0.99, ymax * 0.82, ("T/T0D", "S_{aD}/S_{DS}"), C["muted"], 1.8)

    xs = [i * XR / 600 for i in range(601)]
    pts = [(XM(x), sa(x)) for x in xs]
    cv.polygon([(0, 0)] + pts + [(XM(XR), 0)], C["fill_m"], "none")
    cv.poly(pts, C["bmd"], 4.2)

    segs = [(0.0, 0.2, "上升段", "S_{DS}(0.4+3T/T0D)"),
            (0.2, 1.0, "等加速度平台", "S_{DS}"),
            (1.0, 2.5, "等速度段", "S_{D1}/T"),
            (2.5, XR, "長週期下限", "0.4S_{DS}")]
    for x0, x1, name, expr in segs:
        if x0 > 0:
            cv.line((XM(x0), 0), (XM(x0), sa(x0) + 0.10), C["border"], 1.6, dash="6 5")
        cv.text_px(cv.X(XM((x0 + x1) / 2)), cv.Y(ymax * 0.96), name, 12.5, C["text"], weight="700")
        cv.math_px(cv.X(XM((x0 + x1) / 2)), cv.Y(ymax * 0.88), expr, 12.5, C["bmd"])

    for xb, lab in ((0.2, "0.2 T0D"), (1.0, "T0D"), (2.5, "2.5 T0D")):
        cv.text_px(cv.X(XM(xb)), cv.Y(0) + 22, lab, 12.5, C["muted"])
    for yv, lab in ((0.4, "0.4"), (1.0, "1.0")):
        cv.line((-0.02 * XSC, yv), (0.02 * XSC, yv), C["muted"], 1.2)
        cv.text_px(cv.X(0) - 12, cv.Y(yv), lab, 11.5, C["muted"], "end")
        cv.line((0, yv), (XM(XR) * 0.99, yv), C["border"], 1.2, dash="4 4")

    # 因子進入點
    cv.rect_px(W - 168, 132, 150, 118, C["panel"], 12, C["border"], 1.2)
    cv.text_px(W - 158, 156, "因子進入點", 12.8, C["text"], "start", weight="700")
    for k, (s_, col) in enumerate([("震區 → SSD, S1D", C["muted"]),
                                   ("地盤 → Fa, Fv", C["muted"]),
                                   ("近斷層 → NA, NV", C["muted"]),
                                   ("週期 → 落在哪段", C["accent"])]):
        cv.text_px(W - 158, 180 + k * 20, s_, 11.5, col, "start")

    cv.text_px(W / 2, HH - 26,
               "攔錯：把譜形背成三段、或把分界寫成固定秒數。分界永遠相對於 T0D = SD1/SDS",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2020-4-fig-3-design-spectrum.svg")


# ══════════════════════════════════════════════════════════
# 圖 4：韌性額度的 2/3 : 1/3 分配
# ══════════════════════════════════════════════════════════
def fig4():
    W, HH = 940, 470
    cv = Canvas(W, HH, sx=1, bg="#FFFFFF")
    R = R_MAIN
    RA = ra_of(R)
    cv.text_px(W / 2, 34, "圖 4　Ra 的 1.5 是「地震水準比」，不是品質變異折扣",
               17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, f"R = {R} → Ra = 1 + (R−1)/1.5 = {RA:.3f}", 13, C["muted"])

    x0, bw, y = 120, 700, 168
    unit = bw / (R - 1)
    # 底線：韌性額度 R − 1
    cv.rect_px(x0, y - 26, bw, 52, "#EDF1F6", 10)
    cv.rect_px(x0, y - 26, unit * (RA - 1), 52, C["bmd"], 10)
    cv.text_px(x0 + unit * (RA - 1) / 2, y, f"設計地震可用 {RA-1:.3f}（= 2/3）",
               13.5, "#FFFFFF", weight="700")
    cv.text_px(x0 + unit * (RA - 1) + (bw - unit * (RA - 1)) / 2, y,
               f"保留 {R - RA:.3f}（= 1/3）", 13.5, C["text"], weight="700")
    cv.text_px(x0 - 14, y, "韌性額度", 13.5, C["text"], "end", weight="700")
    cv.text_px(x0 - 14, y + 20, f"R − 1 = {R-1:.1f}", 12, C["muted"], "end")
    cv.text_px(x0 + bw + 12, y, f"R = {R}", 13.5, C["load"], "start", weight="700")

    # 對應的地震水準
    y2 = 290
    cv.rect_px(x0, y2 - 26, bw, 52, "#EDF1F6", 10)
    cv.rect_px(x0, y2 - 26, bw / RATIO_M_OVER_D, 52, C["sfd"], 10)
    cv.text_px(x0 + bw / RATIO_M_OVER_D / 2, y2, "設計地震 SaD（= 2/3 SaM）",
               13.5, "#FFFFFF", weight="700")
    cv.text_px(x0 + bw / RATIO_M_OVER_D + (bw - bw / RATIO_M_OVER_D) / 2, y2,
               "多出的 1/3", 13.5, C["text"], weight="700")
    cv.text_px(x0 - 14, y2, "地震需求", 13.5, C["text"], "end", weight="700")
    cv.text_px(x0 - 14, y2 + 20, "SaM = 1.5 SaD", 12, C["muted"], "end")
    cv.text_px(x0 + bw + 12, y2, "SaM", 13.5, C["load"], "start", weight="700")

    # 對應箭頭
    for xr in (bw / RATIO_M_OVER_D,):
        cv.parts.append(f'<line x1="{x0+unit*(RA-1):.1f}" y1="{y+28}" '
                        f'x2="{x0+xr:.1f}" y2="{y2-28}" stroke="{C["accent"]}" '
                        f'stroke-width="2" stroke-dasharray="6 5"/>')
    cv.text_px(W / 2, 240, "同一個 2/3 ── 韌性額度的分配比例，就是兩個地震水準的比例",
               13.5, C["accent"], weight="700")

    cv.text_px(W / 2, 366,
               f"若在設計地震就把 R = {R} 用滿，最大考量地震（大 {RATIO_M_OVER_D} 倍）便無韌性餘裕可用",
               13.5, C["text"], weight="700")
    cv.text_px(W / 2, HH - 26,
               "攔錯：把 1.5 說成「考慮施工品質變異的保守係數」。它是設計地震與最大考量地震的譜值比",
               13.5, C["muted"])
    cv.save(f"{OUT}/SD-2020-4-fig-4-ductility-budget.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2(); fig3(); fig4()
    for R in (R_MAIN, 4.0, R_ALT):
        print(f"R={R}: Ra={ra_of(R):.3f} Fu_L={fu_long(R):.3f} Fu_M={fu_mid(R):.3f} "
              f"V*/V(L)={vstar_over_v(R):.3f} V*/V(M)={vstar_over_v(R,'mid'):.3f} "
              f"VM/V(L)={vm_over_v(R):.3f}")
