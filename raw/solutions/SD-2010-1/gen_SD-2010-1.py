#!/usr/bin/env python3
"""
SD-2010-1 倒擺穩定性與振動頻率 — 解題圖解產生腳本
用法：python3 gen_SD-2010-1.py [輸出目錄]

fig-1 攔的是「兩個力臂互換」；fig-2 攔的是「穩定條件的方向寫反」。
"""
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2010-1"

# ══════════════════════════════════════════════════════════
# 解題結果（來自 SD-2010-1.md §4，勿手動改動）
#   V(θ) = mgL cosθ + (1/2) k (L sinθ)^2
#   k_eff = kL^2 - mgL；穩定 ⇔ k > mg/L
#   EOM  : mL^2 θ¨ + (kL^2 - mgL) θ = 0
#   ω    = sqrt(k/m - g/L)
# 以無因次參數 r = kL/(mg) 表示：V/(mgL) = cosθ + (r/2) sin^2 θ
#   k_eff/(mgL) = r - 1；ω^2 /(g/L) = r - 1
# ══════════════════════════════════════════════════════════
R_CASES = [1.60, 1.00, 0.55]        # r = kL/(mg)：穩定 / 臨界 / 不穩定
V_OF = lambda th, r: math.cos(th) + 0.5 * r * math.sin(th) ** 2   # V/(mgL)
KEFF = lambda r: r - 1.0                                          # k_eff/(mgL)
OMG2 = lambda r: r - 1.0                                          # ω^2/(g/L)


# ══════════════════════════════════════════════════════════
def fig1_fbd():
    """自由體圖：彈簧（水平力）與重力（鉛垂力）各自的力臂完全不同"""
    cv = Canvas(880, 520, sx=215, ox=250, oy=88, bg="#FFFFFF")
    TH = 0.42                       # 繪圖用傾角（放大以看清力臂）
    L = 1.30
    A = (L * math.sin(TH), L * math.cos(TH))     # 質量端

    # 鉛垂參考線與原始位置
    cv.line((0, 0), (0, L + 0.22), C["ghost"], 2.0, dash="6 5")
    cv.line((0, 0), A, C["member"], 7.0, cap="butt")
    cv.pin_support((0, 0), 0, 17)
    cv.dot((0, 0), 5.0)
    cv.text_px(cv.X(0) + 16, cv.Y(0) - 12, "B", 16, C["text"], weight="700")
    cv.circle(A, 0.11, "#FFFFFF", C["member"], 3.0)
    cv.math_px(cv.X(A[0]), cv.Y(A[1]), "m", 17, C["member"], weight="700")
    cv.text_px(cv.X(A[0]) + 30, cv.Y(A[1]) - 22, "A", 16, C["text"], weight="700")
    cv.dim((0, 0), A, "L", off=-40, label_off=-14)
    cv.math_px(cv.X(0) + 14, cv.Y(L * 0.86), "θ", 17, C["muted"], "start", weight="700")

    # 彈簧力（水平）與其力臂 = A 點的鉛垂高度 L cosθ
    cv.arrow(A, (A[0] - 0.55, A[1]), C["tension"], 3.4, 12)
    cv.math_px(cv.X(A[0] - 0.55) - 10, cv.Y(A[1]) - 16,
               "F_{s} = k L sinθ", 15, C["tension"], "end", weight="700")
    cv.line((A[0] - 0.62, A[1]), (A[0] - 0.62, 0), C["tension"], 1.3, dash="4 4")
    cv.line((0, 0), (A[0] - 0.62, 0), C["tension"], 1.3, dash="4 4")
    cv.dim((A[0] - 0.62, 0), (A[0] - 0.62, A[1]), "L cosθ", off=-52, label_off=-14)
    cv.text_px(cv.X(A[0] - 0.62) - 66, cv.Y(A[1] / 2) + 20, "彈簧力的力臂",
               12.5, C["tension"], weight="700")

    # 重力（鉛垂）與其力臂 = A 點的水平偏距 L sinθ
    cv.arrow(A, (A[0], A[1] - 0.55), C["load"], 3.4, 12)
    cv.math_px(cv.X(A[0]) + 12, cv.Y(A[1] - 0.55), "W = mg", 15, C["load"],
               "start", weight="700")
    cv.line((A[0], A[1] + 0.05), (A[0], L + 0.16), C["load"], 1.3, dash="4 4")
    cv.line((0, L + 0.02), (0, L + 0.16), C["ghost"], 1.3, dash="4 4")
    cv.dim((0, L + 0.12), (A[0], L + 0.12), "L sinθ", off=-28, label_off=-14)
    cv.text_px(cv.X(A[0] / 2), cv.Y(L + 0.12) - 66, "重力的力臂",
               12.5, C["load"], weight="700")

    # 對 B 取力矩
    cv.text_px(700, 190, "對 B 取力矩（小角度）", 14, C["text"], weight="700")
    for i, (t, col) in enumerate([
            ("恢復：F_s · L cosθ  →  k L² θ", C["tension"]),
            ("傾覆：W · L sinθ    →  m g L θ", C["load"]),
            ("m L² θ'' + (k L² − m g L) θ = 0", C["bmd"]),
            ("穩定 ⇔ k L² > m g L ⇔ k > mg/L", C["accent"])]):
        cv.text_px(700, 224 + i * 32, t, 13.5, col,
                   weight="700" if i >= 2 else "400")

    cv.text_px(440, 492,
               "兩個力臂不可互換：彈簧是水平力 → 力臂取鉛垂高度；重力是鉛垂力 → 力臂取水平偏距",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-fbd.svg")


# ══════════════════════════════════════════════════════════
def fig2_stability():
    """位能曲線：θ=0 是谷還是峰，由 r = kL/(mg) 是否大於 1 決定"""
    HGT = 520
    cv = Canvas(1020, HGT, sx=1.0, ox=0, oy=0, bg="#FFFFFF")
    # 本圖為函數圖：採「模型座標、y 向上」，1 模型單位 = 1 像素
    PXY = lambda py: HGT - py            # 像素 y → 模型 y（供 text_px 對位用）

    X0, YB, W, H = 110, 120, 610, 300    # 左緣、基線（模型 y）、寬、高
    th_max = 1.25
    ths = [th_max * (k / 200.0 * 2 - 1) for k in range(201)]
    vals = [[V_OF(t, r) for t in ths] for r in R_CASES]
    lo = min(min(v) for v in vals); hi = max(max(v) for v in vals)
    sx = W / (2 * th_max)
    sy = H / (hi - lo)
    PX = lambda th: X0 + (th + th_max) * sx
    PY = lambda v: YB + (v - lo) * sy     # 模型 y，向上為正

    cv.line((X0, YB), (X0 + W, YB), C["muted"], 1.6)
    cv.line((PX(0), YB - 14), (PX(0), YB + H + 18), C["muted"], 1.6)
    cv.text_px(PX(0), PXY(YB) + 26, "θ = 0", 13, C["muted"])
    cv.text_px(X0 + W, PXY(YB) + 26, "θ", 15, C["muted"])
    cv.text_px(X0 - 8, PXY(YB + H + 18) - 6, "V / (mgL)", 13, C["muted"], anchor="start")

    cols = [C["deform"], C["accent"], C["load"]]
    for r, ys, col in zip(R_CASES, vals, cols):
        cv.poly([(PX(t), PY(v)) for t, v in zip(ths, ys)], col, 3.2)
        cv.dot((PX(0), PY(ys[100])), 5.4, fill="#FFFFFF", stroke=col, w=2.6)

    # 圖例：三條曲線在 θ=0 附近的曲率決定一切
    for i, (r, col) in enumerate(zip(R_CASES, cols)):
        y = 400 - i * 46                                   # 模型 y
        state = ("穩定：θ=0 為谷" if r > 1 else
                 ("臨界：曲線在原點變平" if abs(r - 1) < 1e-9 else "不穩定：θ=0 為峰"))
        cv.line((748, y), (784, y), col, 4.2)
        cv.text_px(794, PXY(y), "r = kL/(mg) = %.2f" % r, 13.5, col,
                   anchor="start", weight="700")
        cv.text_px(794, PXY(y) + 17, state, 12, C["muted"], anchor="start")
        cv.text_px(794, PXY(y) + 33,
                   "k_eff/(mgL) = %+.2f" % KEFF(r), 11.5, C["muted"], anchor="start")

    cv.text_px(510, 476,
               "θ = 0 恆為平衡點，但只有 ∂²V/∂θ² = kL² − mgL > 0（即 r > 1）時才是「谷」——這就是穩定條件",
               13.5, C["muted"])
    cv.text_px(510, 498,
               "r = 1 時曲線在原點變平，ω → 0，即分岔（bifurcation）臨界狀態；r 小於 1 時 ω² 為負，無實數頻率",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-stability.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for r in R_CASES:
        print("  r = %.2f → k_eff/(mgL) = %+.2f, ω²/(g/L) = %+.2f"
              % (r, KEFF(r), OMG2(r)))
    for f in (fig1_fbd, fig2_stability):
        print(" ", f())
