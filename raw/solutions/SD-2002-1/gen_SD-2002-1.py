#!/usr/bin/env python3
"""
SD-2002-1 柔性基座 2-DOF（土壤—結構互制）— 解題圖解產生腳本
用法：python3 gen_SD-2002-1.py [輸出目錄]

fig-1 攔的是「柱變形寫成 u2」；fig-2 攔的是「側移／搖擺主導判反」。
兩張圖的所有比例都由 §4 的特徵解算出，改 k_theta 重跑圖形就會跟著變。
"""
import sys, os, math
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2002-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2002-1.md §1 與 §4，勿手動改動）
# ══════════════════════════════════════════════════════════
KTH = 1.2e7                 # kN-m/rad
I1, I2 = 8000.0, 4000.0     # Ton-m^2
M2 = 100.0                  # Ton
L  = 3.0                    # m（旋轉中心 → 樓版）
K  = 3.0e4                  # kN/m（每根柱）

M11 = I1 + I2                       # 12000
M22 = M2                            # 100
K11 = KTH + 2 * K * L ** 2          # 1.254e7
K12 = -2 * K * L                    # -1.8e5
K22 = 2 * K                         # 6.0e4

# 特徵值由上列數字現算（鐵則 2：改輸入，圖就會變）
_a, _b, _c = M11 * M22, -(K11 * M22 + K22 * M11), K11 * K22 - K12 ** 2
_d = math.sqrt(_b * _b - 4 * _a * _c)
LAM = sorted([(-_b - _d) / (2 * _a), (-_b + _d) / (2 * _a)])
OMG = [math.sqrt(v) for v in LAM]                       # 23.36, 33.15
TN  = [2 * math.pi / w for w in OMG]
PHI2 = [-K12 / (K22 - lam * M22) for lam in LAM]        # 33.27, -3.61  (m/rad)
W_TRA = math.sqrt(K22 / M22)        # 24.5  Rayleigh 商界限
W_ROT = math.sqrt(K11 / M11)        # 32.3
RIGID = L                            # 剛體隨動時 u2/θ1 = L = 3 m/rad

# 繪圖幾何（模型單位，柱高 = L 對應 HC）
MW = 7.0
HW, HB = 0.95, 0.30      # 基座半寬、厚
HC = 1.60                # 柱高
CW = 0.60                # 柱間距半寬
SW = 0.72                # 樓版半寬


def _structure(cv, th=0.0, u2=0.0, color=C["member"], w=MW, dash=None):
    """th：基座（＝樓版）轉角，逆時針正；u2：樓版質心水平位移。皆為繪圖量。"""
    c, s = math.cos(th), math.sin(th)
    R = lambda p: (p[0] * c - p[1] * s, p[0] * s + p[1] * c)
    cv.polygon([R((-HW, 0)), R((HW, 0)), R((HW, -HB)), R((-HW, -HB))],
               "rgba(0,0,0,0.05)", color, 2.4 if dash is None else 1.5)
    slab = [(u2 - SW * c, HC - SW * s), (u2 + SW * c, HC + SW * s)]
    for sgn in (-1, 1):
        b = R((sgn * CW, 0))
        t = (u2 + sgn * CW * c, HC + sgn * CW * s)
        cv.line(b, t, color, w * 0.62, dash=dash, cap="butt")
    cv.line(slab[0], slab[1], color, w, dash=dash, cap="butt")
    return R


# ══════════════════════════════════════════════════════════
def fig1_dof():
    """自由度與柱變形：Δ = u2 - L·θ1（不是 u2）"""
    cv = Canvas(900, 520, sx=130, ox=330, oy=175, bg="#FFFFFF")
    TH, U2 = 0.15, 0.66

    cv.line((-1.90, 0), (3.10, 0), C["muted"], 1.4, dash="7 5")
    _structure(cv, 0, 0, C["ghost"], 3.0, dash="6 5")
    _structure(cv, TH, U2, C["deform"])

    cv.moment_arrow((0, -HB / 2), r=30, ccw=True, color=C["bmd"], w=2.6,
                    span=250, start=110)
    cv.dot((0, -HB / 2), 5.0, fill=C["bmd"])
    cv.math_px(cv.X(0) - 52, cv.Y(-HB / 2) + 46, "k_{θ}", 17, C["bmd"],
               "start", weight="700")
    cv.text_px(cv.X(0) + 6, cv.Y(-HB / 2) + 48, "旋轉中心（基座質心）",
               12.5, C["muted"], anchor="start")
    cv.math_px(cv.X(-HW) - 12, cv.Y(0) - 30, "θ_{1}", 17, C["deform"],
               "end", weight="700")

    rig = HC * TH                       # 剛體隨動量（＝ L·θ1 的繪圖對應）
    cv.arrow((0, HC + 0.30), (rig, HC + 0.30), C["accent"], 2.8, 10)
    cv.line((rig, HC), (rig, HC + 0.46), C["accent"], 1.3, dash="4 4")
    cv.arrow((rig, HC + 0.30), (U2, HC + 0.30), C["bmd"], 2.8, 10)
    cv.line((0, HC), (0, HC + 0.46), C["ghost"], 1.3, dash="4 4")
    cv.math_px(cv.X(rig / 2) - 6, cv.Y(HC + 0.30) + 20, "Lθ_{1}", 15, C["accent"], "end", weight="700")
    cv.math_px(cv.X((rig + U2) / 2), cv.Y(HC + 0.30) - 20,
               "Δ = u_{2} - Lθ_{1}", 15, C["bmd"], weight="700")
    cv.arrow((0, HC - 0.34), (U2, HC - 0.34), C["load"], 3.2, 11)
    cv.math_px(cv.X(U2 / 2), cv.Y(HC - 0.34) + 18, "u_{2}", 16, C["load"], weight="700")

    cv.dim((-HW - 0.28, 0), (-HW - 0.28, HC), "L", off=0, label_off=-17)
    cv.math_px(cv.X(-HW + 0.20), cv.Y(-HB / 2), "I_{1}", 16, C["muted"],
               "start", weight="700")
    cv.math_px(cv.X(U2 + SW) + 14, cv.Y(HC) - 4, "M_{2}, I_{2}", 16, C["muted"], "start", weight="700")
    cv.math_px(cv.X(-CW) - 10, cv.Y(HC / 2), "k", 16, C["muted"], "end", weight="700")
    cv.math_px(cv.X(CW) + 10, cv.Y(HC / 2), "k", 16, C["muted"], "start", weight="700")

    cv.text_px(450, 476,
               "軸向剛性柱 → 樓版轉角 = 基座轉角，故 I2 併入 M11 = I1 + I2 = %.0f Ton-m^2"
               % M11, 13, C["muted"])
    cv.text_px(450, 498,
               "柱真正的變形只有 Δ 這一段；寫成 u2 會漏掉整個剛體隨動量，K11 也就跟著錯",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-dof.svg")


# ══════════════════════════════════════════════════════════
TH_M = 0.070        # 兩格共用的基座轉角（繪圖量）


def _mode_panel(i):
    cv = Canvas(600, 470, sx=125, ox=215, oy=150, bg=C["panel"])
    cv.panel("Mode %d：ω = %.1f rad/s，T = %.3f s" % (i + 1, OMG[i], TN[i]),
             "θ1 = 1 rad 時 u2 = %+.2f m" % PHI2[i])

    rig = HC * TH_M                       # 對應 L·θ1
    u2 = PHI2[i] / RIGID * rig            # ← 比例完全由特徵向量決定

    cv.line((-1.70, 0), (2.90, 0), C["muted"], 1.3, dash="7 5")
    _structure(cv, 0, 0, C["ghost"], 3.0, dash="6 5")
    _structure(cv, TH_M, u2, C["deform"])

    cv.line((rig, HC - 0.55), (rig, HC + 0.30), C["accent"], 1.7, dash="5 4")
    cv.math_px(cv.X(rig) + 8, cv.Y(HC + 0.30) + 4, "剛體隨動位置 Lθ_{1}", 12.5,
               C["accent"], "start", weight="700")

    # 判準：樓版位移與剛體隨動量的比值 r = u2/(L θ1)
    r = PHI2[i] / RIGID
    tag = ("側移（柱剪切）主導：同向且遠超剛體值" if r > 1 else
           "基座搖擺主導：樓版與剛體隨動反向")
    cv.text_px(300, 424, "u2/(L·θ1) = %+.2f　（柱變形 Δ = u2 - L·θ1 = %+.2f m/rad）"
               % (r, PHI2[i] - RIGID), 13.5, C["muted"])
    cv.text_px(300, 446, "→ " + tag, 14, C["accent"], weight="700")
    return cv


def fig2_modes():
    path = f"{OUT}/{TAG}-fig-2-modes.svg"
    compose([_mode_panel(0), _mode_panel(1)],
            title="兩個振態：以「剛體隨動量 L·θ1 = 3 m/rad」為判準",
            sub="Rayleigh 商界限 √(K22/M22) = %.1f 與 √(K11/M11) = %.1f 恰落在 ω1 = %.1f 與 ω2 = %.1f 之間"
                % (W_TRA, W_ROT, OMG[0], OMG[1]),
            note="兩格用同一個 θ1；u2 的長度比 = 特徵向量比，故「哪個模態柱變形大」是看出來的，不是說出來的",
            path=path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("  λ = %.1f, %.1f   ω = %.3f, %.3f   φ2 = %.2f, %.2f"
          % (LAM[0], LAM[1], OMG[0], OMG[1], PHI2[0], PHI2[1]))
    print("  交錯界限：%.2f < %.2f < %.2f < %.2f"
          % (OMG[0], W_TRA, W_ROT, OMG[1]))
    for f in (fig1_dof, fig2_modes):
        print(" ", f())
