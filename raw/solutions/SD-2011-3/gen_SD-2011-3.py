#!/usr/bin/env python3
"""
SD-2011-3 電梯懸吊系統：等速基礎運動 → Ramp 激振 — 解題圖解產生腳本
用法：python3 gen_SD-2011-3.py [輸出目錄]

fig-1 攔的是「重力重複計入」與「彈簧變形只寫 u」；
fig-2 攔的是「以為 u(t) = vt、沒有振盪」。
"""
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2011-3"

# ══════════════════════════════════════════════════════════
# 解題結果（來自 SD-2011-3.md §4，勿手動改動）
#   靜平衡  ：k·δst = mg
#   彈簧變形：Δ(t) = δst + (vt − u)
#   EOM     ：m ü + k u = k v t
#   解      ：u(t) = v t − (v/ω0) sin(ω0 t)，ω0 = sqrt(k/m)
#   速度    ：u̇ = v[1 − cos(ω0 t)]  ∈ [0, 2v]
#   加速度  ：ü = v ω0 sin(ω0 t)
# 以無因次時間 τ = ω0 t、無因次位移 U = u ω0 / v 表示：
#   U(τ) = τ − sin τ；  U'(τ) = 1 − cos τ ∈ [0, 2]
# ══════════════════════════════════════════════════════════
U_OF  = lambda tau: tau - math.sin(tau)          # u·ω0/v
UD_OF = lambda tau: 1 - math.cos(tau)            # u̇/v
TAU_MAX = 4 * math.pi
AMP = 1.0        # 自由振盪振幅 v/ω0 → 無因次為 1


# ══════════════════════════════════════════════════════════
def fig1_model():
    """系統圖與靜平衡消去：彈簧變形是「上端減下端」，不是 u"""
    def spring(cv, x, y0, y1, color, n=9, amp=0.10):
        pts = [(x, y0)]
        seg = (y1 - y0) / (n + 1)
        pts.append((x, y0 + seg * 0.5))
        for i in range(n):
            pts.append((x + amp * (1 if i % 2 == 0 else -1), y0 + seg * (i + 1)))
        pts += [(x, y1 - seg * 0.5), (x, y1)]
        cv.poly(pts, color, 2.0)

    cv = Canvas(880, 500, sx=125, ox=250, oy=118, bg="#FFFFFF")

    # ── 左：t = 0（靜平衡）──
    cv.line((-0.85, 2.10), (0.85, 2.10), C["muted"], 2.0)
    for i in range(6):
        cv.line((-0.72 + i * 0.28, 2.10), (-0.86 + i * 0.28, 2.24), C["muted"], 1.4)
    spring(cv, 0, 2.10, 1.05, C["muted"])
    cv.rect_px(cv.X(0) - 34, cv.Y(1.05) - 4, 68, 46, "#FFFFFF", rx=4,
               stroke=C["member"], sw=3.0)
    cv.math_px(cv.X(0), cv.Y(1.05) + 19, "m", 18, C["member"], weight="700")
    cv.math_px(cv.X(0) + 46, cv.Y(1.58), "k", 17, C["muted"], "start", weight="700")
    cv.arrow((0, 0.72), (0, 0.30), C["load"], 3.0, 10)
    cv.math_px(cv.X(0) + 10, cv.Y(0.50), "mg", 15, C["load"], "start", weight="700")
    cv.text_px(cv.X(0), cv.Y(0.22), "t = 0：靜平衡", 14, C["text"], weight="700")
    cv.text_px(cv.X(0), cv.Y(-0.00), "k·δst = mg", 13.5, C["accent"], weight="700")

    # ── 右：t > 0（上端已上升 vt，質塊上升 u）──
    XR = 2.45
    cv.line((XR - 0.85, 2.10), (XR + 0.85, 2.10), C["ghost"], 2.0, dash="5 4")
    cv.line((XR - 0.85, 2.55), (XR + 0.85, 2.55), C["muted"], 2.0)
    for i in range(6):
        cv.line((XR - 0.72 + i * 0.28, 2.55), (XR - 0.86 + i * 0.28, 2.69), C["muted"], 1.4)
    cv.arrow((XR - 0.62, 2.10), (XR - 0.62, 2.55), C["load"], 3.0, 10)
    cv.math_px(cv.X(XR - 0.62) - 10, cv.Y(2.33), "v t", 15, C["load"], "end", weight="700")

    spring(cv, XR, 2.55, 1.42, C["deform"])
    cv.line((XR - 0.85, 1.05), (XR + 0.85, 1.05), C["ghost"], 1.4, dash="5 4")
    cv.rect_px(cv.X(XR) - 34, cv.Y(1.42) - 4, 68, 46, "#FFFFFF", rx=4,
               stroke=C["deform"], sw=3.0)
    cv.math_px(cv.X(XR), cv.Y(1.42) + 19, "m", 18, C["deform"], weight="700")
    cv.arrow((XR + 0.62, 1.05), (XR + 0.62, 1.42), C["deform"], 3.0, 10)
    cv.math_px(cv.X(XR + 0.62) + 10, cv.Y(1.24), "u", 16, C["deform"], "start", weight="700")

    cv.text_px(cv.X(XR), cv.Y(0.22), "t > 0：上端上升 v t、電梯上升 u", 14,
               C["text"], weight="700")
    cv.text_px(cv.X(XR), cv.Y(-0.00), "彈簧變形 Δ = δst + (v t − u)", 13.5,
               C["accent"], weight="700")

    # 消去說明
    cv.text_px(440, 424,
               "m ü = k[δst + (v t − u)] − mg　→　靜態項 k·δst − mg = 0 自動對消",
               14, C["bmd"], weight="700")
    cv.text_px(440, 452, "→　m ü + k u = k v t（Ramp 型激振）", 15, C["bmd"], weight="700")
    cv.text_px(440, 480,
               "座標 u 自靜平衡位置量起，故 mg 不可再出現在方程式右端；"
               "彈簧變形也不是 u，而是「上端位移 − 下端位移」",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-model.svg")


# ══════════════════════════════════════════════════════════
def fig2_response():
    """響應時程：u(t) 繞著 vt 振盪；速度在 0 與 2v 之間，平均為 v"""
    HGT = 520
    cv = Canvas(940, HGT, sx=1.0, ox=0, oy=0, bg="#FFFFFF")
    PXY = lambda py: HGT - py

    X0, W = 105, 620
    sx = W / TAU_MAX
    taus = [TAU_MAX * k / 400.0 for k in range(401)]

    # ── 上：位移 ──
    YB1, H1 = 296, 178
    umax = U_OF(TAU_MAX)
    sy1 = H1 / umax
    cv.line((X0, YB1), (X0 + W, YB1), C["muted"], 1.5)
    cv.line((X0, YB1 - 8), (X0, YB1 + H1 + 14), C["muted"], 1.5)
    cv.poly([(X0 + t * sx, YB1 + t * sy1) for t in taus], C["ghost"], 2.6, dash="7 5")
    cv.poly([(X0 + t * sx, YB1 + U_OF(t) * sy1) for t in taus], C["deform"], 3.2)
    cv.text_px(X0 - 6, PXY(YB1 + H1 + 20), "u * omega0 / v", 13, C["muted"], anchor="start")
    cv.text_px(X0 + W - 4, PXY(YB1) + 22, "tau = omega0 · t", 13, C["muted"], anchor="end")
    # 標出「穩態跟隨」與「自由振盪」兩項
    tp = 3 * math.pi / 2
    cv.line((X0 + tp * sx, YB1 + tp * sy1), (X0 + tp * sx, YB1 + U_OF(tp) * sy1),
            C["accent"], 2.4)
    cv.text_px(X0 + tp * sx + 10, PXY(YB1 + (tp + U_OF(tp)) / 2 * sy1),
               "自由振盪 −(v/ω0)·sin(ω0 t)", 12.5, C["accent"], anchor="start", weight="700")
    cv.text_px(X0 + 0.72 * W, PXY(YB1 + 0.72 * TAU_MAX * sy1) + 26,
               "穩態跟隨 vt", 12.5, C["muted"], anchor="start")
    cv.text_px(X0 + W / 2, PXY(YB1 + H1 + 20), "位移 u(t) = vt − (v/ω0)·sin(ω0 t)",
               14, C["text"], weight="700")

    # ── 下：速度 ──
    YB2, H2 = 96, 130
    sy2 = H2 / 2.0
    cv.line((X0, YB2), (X0 + W, YB2), C["muted"], 1.5)
    cv.line((X0, YB2 - 8), (X0, YB2 + H2 + 14), C["muted"], 1.5)
    for lv, lab, col in ((0.0, "0", C["muted"]), (1.0, "v（平均）", C["accent"]),
                         (2.0, "2v（最大）", C["load"])):
        cv.line((X0, YB2 + lv * sy2), (X0 + W, YB2 + lv * sy2), col, 1.3, dash="5 4")
        cv.text_px(X0 - 8, PXY(YB2 + lv * sy2), lab, 12, col, anchor="end", weight="700")
    cv.poly([(X0 + t * sx, YB2 + UD_OF(t) * sy2) for t in taus], C["bmd"], 3.2)
    cv.text_px(X0 + W / 2, PXY(YB2 + H2 + 20),
               "速度 du/dt = v[1 − cos(ω0 t)]，在 0 與 2v 之間振盪", 14, C["text"], weight="700")

    cv.text_px(470, 474,
               "起動瞬間支承速度由 0 突跳至 v，此不連續必然激發振幅 v/ω0 = v√(m/k) 的自由振動",
               13.5, C["muted"])
    cv.text_px(470, 496,
               "若答案只寫 u(t) = vt（無振盪項），代表初速度條件漏掉了特解貢獻的 v",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-response.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("  U'(τ) 範圍 = [%.2f, %.2f]（應為 0~2）"
          % (min(UD_OF(TAU_MAX * k / 400) for k in range(401)),
             max(UD_OF(TAU_MAX * k / 400) for k in range(401))))
    for f in (fig1_model, fig2_response):
        print(" ", f())
