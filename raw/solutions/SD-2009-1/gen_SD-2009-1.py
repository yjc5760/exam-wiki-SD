#!/usr/bin/env python3
"""
SD-2009-1 廣義座標法（懸臂柱）— 解題圖解產生腳本
用法：python3 gen_SD-2009-1.py [輸出目錄]

fig-1 攔的是「k* 誤用 Ψ' 而非 Ψ''」；fig-2 攔的是「以為 m* = m̄L、p* = p̄L」。
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose
from recipes import plot_function, bar_compare

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2009-1"

# ══════════════════════════════════════════════════════════
# 解題結果（來自 SD-2009-1.md §4，勿手動改動）
#   Psi(x)   = (x/L)^2 (3/2 - x/2L) = x^2(3L-x)/(2L^3)
#   Psi'(x)  = 3x/L^2 - 3x^2/(2L^3)
#   Psi''(x) = 3(L-x)/L^3
#   m* = 33 mbar L /140 = 0.2357 mbar L
#   k* = 3EI/L^3
#   p* = 3 pbar L / 8 = 0.375 pbar L
# ══════════════════════════════════════════════════════════
PSI   = lambda xi: xi ** 2 * (1.5 - xi / 2)          # xi = x/L；Psi(1) = 1
DPSI  = lambda xi: 3 * xi - 1.5 * xi ** 2            # L·Psi'
DDPSI = lambda xi: 3 * (1 - xi)                      # L^2·Psi''

M_STAR = 33 / 140          # m* / (mbar L)   = 0.23571
K_STAR = 3.0               # k* / (EI/L^3)
P_STAR = 3 / 8             # p* / (pbar L)   = 0.375
OMEGA  = (K_STAR / M_STAR) ** 0.5      # omega1 * sqrt(mbar L^4/EI) = 3.5675
OMEGA_EXACT = 3.5160       # 精確一階頻率係數（Euler-Bernoulli 懸臂梁）

XS = [k / 100.0 for k in range(101)]


def _panel(title, sub, ys, color, note_pts):
    cv = Canvas(360, 430, sx=230, ox=56, oy=92, bg=C["panel"])
    cv.panel(title, sub)
    ymax = max(abs(min(ys)), abs(max(ys)))
    sc = 0.90 / ymax                            # 讓最大值畫到 0.90（模型單位）
    cv.axes((0, 0), lx=1.06, ly=1.06, labels=("", "ξ = x/L"))
    cv.line((0, 0), (0, 1), C["ghost"], 1.6, dash="5 4")
    pts = [(y * sc, xi) for xi, y in zip(XS, ys)]      # 垂直擺放：xi 為縱軸
    cv.polygon([(0, 0)] + pts + [(0, 1)], C["fill_m"], color, 3.0)
    for xi, txt, dxp, dyp in note_pts:
        i = min(range(len(XS)), key=lambda k: abs(XS[k] - xi))
        cv.dot((ys[i] * sc, xi), 5.0, fill="#FFFFFF", stroke=color, w=2.6)
        cv.math_px(cv.X(ys[i] * sc) + dxp, cv.Y(xi) + dyp, txt, 14, color,
                   "start", weight="700")
    return cv


def fig1_shape():
    """形函數與其一、二階導數：k* 由曲率（Ψ''）決定，不是斜率"""
    a = _panel("Ψ(ξ)　→ 決定 m* 與 p*", "端點正規化 Ψ(1) = 1",
               [PSI(x) for x in XS], C["deform"],
               [(1.0, "= 1", 8, 20), (0.0, "= 0", 8, -8)])
    b = _panel("L·Ψ'(ξ)　→ 不用於 k*", "固定端 Ψ'(0) = 0",
               [DPSI(x) for x in XS], C["muted"],
               [(0.0, "= 0", 8, -8), (1.0, "= 1.5/L", 8, 20)])
    c = _panel("L²·Ψ''(ξ)　→ 決定 k*", "自由端彎矩為零：Ψ''(1) = 0",
               [DDPSI(x) for x in XS], C["bmd"],
               [(0.0, "= 3/L^{2}", -8, -20), (1.0, "= 0", 8, 18)])
    path = f"{OUT}/{TAG}-fig-1-shape.svg"
    compose([a, b, c], cols=3,
            title="形函數三聯圖：哪一階導數決定哪一個廣義量",
            sub="m* = ∫ m̄Ψ² dx　｜　p* = ∫ p̄Ψ dx　｜　k* = ∫ EI(Ψ'')² dx（是二階導數，不是一階）",
            note="Ψ''(1) = 0 對應自由端彎矩為零、Ψ'(0) = 0 對應固定端無轉角——"
                 "這兩個邊界條件同時成立，才證明所取形函數合法",
            path=path)
    return path


def fig2_magnitude():
    """量級比較：廣義量與「總量」的差距是加權積分的結果，不是打折"""
    path = f"{OUT}/{TAG}-fig-2-magnitude.svg"
    bar_compare(
        [("分布質量總和", "m̄L（若整柱剛體平移）", 1.0, "1.000 m̄L", C["ghost"]),
         ("廣義質量 m*", "∫ m̄Ψ² dx = 33m̄L/140", M_STAR, "%.4f m̄L" % M_STAR, C["deform"]),
         ("分布荷重總和", "p̄L（合力）", 1.0, "1.000 p̄L", C["ghost"]),
         ("廣義荷重 p*", "∫ p̄Ψ dx = 3p̄L/8", P_STAR, "%.4f p̄L" % P_STAR, C["load"])],
        title="廣義量 vs. 總量：兩者不是同一件事",
        sub="長條長度以各自的「總量」為 100%%；Rayleigh 頻率 √(k*/m*) = %.4f√(EI/m̄L⁴)，較精確值 %.4f 高估 %.1f%%"
            % (OMEGA, OMEGA_EXACT, (OMEGA / OMEGA_EXACT - 1) * 100),
        note="只有 Ψ ≡ 1（剛體平移）時才會 m* = m̄L、p* = p̄L；Ψ(L) = 1 只是端點正規化，與積分值無關",
        path=path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("  m* = %.5f m̄L　k* = %.1f EI/L^3　p* = %.5f p̄L　ω = %.4f (精確 %.4f)"
          % (M_STAR, K_STAR, P_STAR, OMEGA, OMEGA_EXACT))
    for f in (fig1_shape, fig2_magnitude):
        print(" ", f())
