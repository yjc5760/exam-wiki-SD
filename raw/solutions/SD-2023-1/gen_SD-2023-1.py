#!/usr/bin/env python3
"""
SD-2023-1 簡支梁連續體：模態頻率、模態函數與模態載重 — 解題圖解產生腳本
用法：python3 gen_SD-2023-1.py [輸出目錄]

這張圖攔的是「偶數模態為什麼不被激發」——把 n-1 個節點與中點值一起畫出來，
sin(nπ/2) 的 1, 0, -1, 0 就不再需要記憶。
"""
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2023-1"
NMODES = 4

# ══════════════════════════════════════════════════════════
# 解題結果（來自 SD-2023-1.md §4，勿手動改動）
#   beta_n = n*pi/L；omega_n = (n^2 pi^2 / L^2) sqrt(EI/mbar)
#   phi_n(x) = sin(n pi x / L)；M_n = mbar L / 2
#   Q_n(t)  = P(t) phi_n(L/2) = P(t) sin(n pi / 2)
# ══════════════════════════════════════════════════════════
phi   = lambda n, xi: math.sin(n * math.pi * xi)          # xi = x/L
OMG_R = [n ** 2 for n in range(1, NMODES + 1)]            # omega_n / omega_1
QMID  = [round(math.sin(n * math.pi / 2)) for n in range(1, NMODES + 1)]  # 1, 0, -1, 0（整數，避免浮點殘量）
NODES = [[k / n for k in range(1, n)] for n in range(1, NMODES + 1)]  # 內部節點 xi


def _panel(n):
    i = n - 1
    cv = Canvas(840, 250, sx=560, ox=140, oy=100, bg=C["panel"])
    cv.panel("Mode %d：ω_%d = %d ω_1，內部節點 %d 個"
             % (n, n, OMG_R[i], n - 1),
             "φ_%d(L/2) = sin(%dπ/2) = %+.0f　→　Q_%d(t) = %s"
             % (n, n, QMID[i], n,
                ("P(t)" if QMID[i] > 0 else ("-P(t)" if QMID[i] < 0 else "0（不被激發）"))))

    A = 0.075                                   # 繪圖振幅
    cv.line((0, 0), (1, 0), C["ghost"], 2.0, dash="6 5")
    pts = [(xi / 200, 0) for xi in range(0)]
    pts = [(k / 200.0, A * phi(n, k / 200.0)) for k in range(201)]
    cv.poly(pts, C["deform"], 3.6)

    # 支承
    cv.support((0, 0), "pin", 0, 13)
    cv.support((1, 0), "roller", 0, 13)

    # 內部節點（零位移點）——數目應為 n-1，這正是這張圖的檢核價值
    for xi in NODES[i]:
        cv.dot((xi, 0), 5.0, fill="#FFFFFF", stroke=C["accent"], w=2.6)

    # 中點：載重作用位置
    cv.line((0.5, -0.14), (0.5, A + 0.055), C["load"], 1.4, dash="5 4")
    cv.arrow((0.5, A + 0.075), (0.5, A * QMID[i] + 0.018 if QMID[i] else 0.022),
             C["load"], 3.0, 10)
    cv.math_px(cv.X(0.5) + 12, cv.Y(A + 0.075) + 16, "P(t)", 15, C["load"],
               "start", weight="700")
    cv.dot((0.5, A * QMID[i]), 5.6,
           fill=C["load"] if QMID[i] else "#FFFFFF",
           stroke=C["load"], w=2.6)
    cv.math_px(cv.X(0.5) + 13, cv.Y(A * QMID[i]) + (34 if QMID[i] >= 0 else -22),
               "φ_{%d}(L/2) = %+.0f" % (n, QMID[i]), 14,
               C["load"] if QMID[i] else C["accent"], "start", weight="700")
    if QMID[i] == 0:
        cv.text_px(cv.X(0.5) + 13, cv.Y(0) + 42,
                   "中點恰為節點 → 集中力做不了功", 12.5, C["accent"],
                   anchor="start", weight="700")
    return cv


def fig1_modes():
    path = f"{OUT}/{TAG}-fig-1-modes.svg"
    compose([_panel(n) for n in range(1, NMODES + 1)], cols=1,
            title="簡支梁前四個模態：節點數、中點值與模態載重的關係",
            sub="φ_n(x) = sin(nπx/L)；ω_n ∝ n^2；橙圈＝內部節點（零位移點），第 n 模態恰有 n-1 個",
            note="模態載重 Q_n(t) = P(t)·φ_n(L/2) = P(t)·sin(nπ/2)：偶數模態的中點正好是節點，"
                 "故 n = 2, 4, 6… 完全不被激發",
            path=path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("  φ_n(L/2) =", ["%+.0f" % q for q in QMID],
          "  節點數 =", [len(v) for v in NODES])
    print(" ", fig1_modes())
