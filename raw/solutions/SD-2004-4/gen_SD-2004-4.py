#!/usr/bin/env python3
"""
SD-2004-4 L 形構架：質量矩陣與地震影響向量 — 解題圖解產生腳本

用法：python3 gen_SD-2004-4.py [輸出目錄]

本題 2026-08-22 勘誤的核心是「h1、h2 皆自地面量起」，
fig-1 就是為了把這件事畫死，讓 l_theta 不可能再寫成 h1+h2。
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2004-4"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SD-2004-4.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 幾何：h1、h2 皆為「離地高度」（2026-08-22 由附圖像素判讀更正）
#   附圖中 m1 在 y=378、梁在 y=165、地面在 y=590 → (165+590)/2 = 377.5
#   故 h1/h2 恰為 1/2；此比值由附圖算出，非目測
H1 = (590 - 378) / (590 - 165)       # = 0.499
H2 = 1.00                            # h2 = 柱總高（地面 → 轉角）
X3 = (760 - 440) / (590 - 165)       # x3/h2，依附圖像素比例 = 0.753

# §4 子題(一)：質量矩陣（對角）
M11, M22, M33 = "m_{1}", "m_{2}+m_{3}", "m_{3}"

# §4 子題(二)(三)：影響向量
LX     = ("1", "1", "0")
LTHETA = ("h_{1}", "h_{2}", "x_{3}")     # ← 第二項為 h2，不是 h1+h2

MW = 6.5
TH_DRAW = 0.32          # 繪圖用的單位轉角（純視覺放大）
S_DRAW  = 0.32          # 繪圖用的單位平移


def _frame(cv, color=C["member"], w=MW, dash=None, disp=None):
    """L 形構架本體；disp(x,y) → (dx,dy) 為該點的剛體位移"""
    d = disp or (lambda x, y: (0.0, 0.0))
    T = lambda p: (p[0] + d(*p)[0], p[1] + d(*p)[1])
    cv.poly([T((0, 0)), T((0, H2))], color, w, dash=dash)
    cv.poly([T((0, H2)), T((X3, H2))], color, w, dash=dash)


def _mass_box(cv, q, color):
    cv.rect_px(cv.X(q[0]) - 8, cv.Y(q[1]) - 8, 16, 16, "#FFFFFF",
               rx=2, stroke=color, sw=2.4)


# ══════════════════════════════════════════════════════════
def fig1_geometry():
    """題目重繪 — 唯一目的：把 h1、h2 的量測起點畫死在地面上"""
    cv = Canvas(720, 480, sx=250, ox=320, oy=100, bg="#FFFFFF")

    cv.line((-1.05, 0), (X3 + 0.30, 0), C["muted"], 1.6, dash="7 5")

    _frame(cv)
    cv.fixed_support((0, 0), size=22)

    for p, lab, ax, ay in (((0, H1), "m_{1}", -34, 0),
                           ((0, H2), "m_{2}", -34, -2),
                           ((X3, H2), "m_{3}", 0, -26)):
        _mass_box(cv, p, C["member"])
        cv.math_px(cv.X(p[0]) + ax, cv.Y(p[1]) + ay, lab, 16, C["member"],
                   "start" if ax < 0 else "middle", weight="700")

    cv.arrow((0, H1), (0.32, H1), C["deform"], 3.2, 11)
    cv.math((0.32, H1), "u_{1}", 17, C["deform"], "start", dx=9, weight="700")
    cv.arrow((X3, H2), (X3 + 0.32, H2), C["deform"], 3.2, 11)
    cv.math((X3 + 0.32, H2), "u_{2}", 17, C["deform"], "start", dx=9, weight="700")
    cv.arrow((X3, H2), (X3, H2 - 0.32), C["deform"], 3.2, 11)
    cv.math((X3, H2 - 0.32), "u_{3}", 17, C["deform"], "middle", dy=22, weight="700")

    # ── 關鍵：兩條尺寸線同起於地面 ──
    cv.dim((0, 0), (0, H1), "h_{1}", off=-100, label_off=-16)
    cv.dim((0, 0), (0, H2), "h_{2}", off=-195, label_off=-16)
    cv.dim((0, H2), (X3, H2), "x_{3}", off=-60, label_off=-15)

    cv.dot((0, 0), 5.2, fill=C["accent"], stroke="#FFFFFF", w=2.0)
    cv.line((-1.00, 0), (-0.03, 0), C["accent"], 1.5, dash="4 4")
    cv.text_px(cv.X(-1.00), cv.Y(0) - 16, "兩條尺寸線的共同起點", 13, C["accent"],
               anchor="start", weight="700")

    cv.text_px(360, 450,
               "h1、h2 皆自基礎量起（h2 並非 m1→m2 的段長）；各桿件軸向剛性",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-geometry.svg")


# ══════════════════════════════════════════════════════════
def _panel_rigid(title, sub, mode):
    """mode = 'x'（單位水平平移）或 'theta'（單位順時針轉動）"""
    cv = Canvas(520, 545, sx=180, ox=180, oy=215, bg=C["panel"])
    cv.panel(title, sub)

    cv.line((-0.85, 0), (X3 + 0.85, 0), C["muted"], 1.4, dash="7 5")

    _frame(cv, C["ghost"], 3.0, dash="6 5")
    cv.fixed_support((0, 0), size=20, color=C["ghost"])

    if mode == "x":
        disp = lambda x, y: (S_DRAW, 0.0)
        rows = [("l_{x}(u_{1}) = " + LX[0], "m_1 隨支承右移"),
                ("l_{x}(u_{2}) = " + LX[1], "頂層同步右移"),
                ("l_{x}(u_{3}) = " + LX[2], "水平平移不生垂直位移")]
    else:
        # 順時針轉 theta：dx = +y*theta、dy = -x*theta
        disp = lambda x, y: (y * TH_DRAW, -x * TH_DRAW)
        rows = [("l_{θ}(u_{1}) = " + LTHETA[0], "力臂＝m_1 的離地高度"),
                ("l_{θ}(u_{2}) = " + LTHETA[1], "力臂＝轉角的離地高度"),
                ("l_{θ}(u_{3}) = " + LTHETA[2], "m_3 在中心右方 → 下移")]

    tf = lambda x, y: (x + disp(x, y)[0], y + disp(x, y)[1])
    _frame(cv, C["deform"], MW, disp=disp)
    cv.fixed_support(tf(0, 0), size=20, color=C["deform"])
    for p, lab, ax, ay in (((0, H1), "m_{1}", -32, 2), ((0, H2), "m_{2}", -32, -2),
                           ((X3, H2), "m_{3}", -38, 16)):
        q = tf(*p)
        _mass_box(cv, q, C["deform"])
        cv.math_px(cv.X(q[0]) + ax, cv.Y(q[1]) + ay, lab, 15, C["deform"],
                   "start" if ax < 0 else "middle", weight="700")

    if mode == "x":
        cv.arrow((0, -0.17), (S_DRAW, -0.17), C["load"], 3.4, 11)
        cv.math((S_DRAW / 2, -0.17), "u_{gx} = 1", 15, C["load"], dy=-17, weight="700")
    else:
        cv.moment_arrow((0, -0.16), r=23, ccw=False, color=C["load"], w=2.6,
                        span=250, start=110)
        cv.math((0, -0.16), "θ_{gz} = 1", 15, C["load"], "start", dx=34, weight="700")
        q = tf(X3, H2)
        cv.arrow((X3 + 0.42, H2), (X3 + 0.42, q[1]), C["accent"], 3.0, 10)
        cv.math_px(cv.X(X3 + 0.42) + 10, (cv.Y(H2) + cv.Y(q[1])) / 2,
                   "x_{3}θ", 14, C["accent"], "start", weight="700")

    # 結果列表置於面板下方，與圖形分離，避免標註打架
    cv.line((-0.85, -0.38), (X3 + 0.85, -0.38), C["border"], 1.2)
    y0 = 408
    for i, (expr, why) in enumerate(rows):
        cv.math_px(34, y0 + i * 33, expr, 16, C["accent"], "start", weight="700")
        cv.text_px(196, y0 + i * 33, why, 12.5, C["muted"], anchor="start")
    return cv


def fig2_influence():
    """影響向量 = 支承作單位運動時的剛體位移（不含任何彈性變形）"""
    a = _panel_rigid("(二) 支承單位水平位移", "u_gx = 1", "x")
    b = _panel_rigid("(三) 支承單位順時鐘轉動", "theta_gz = 1", "theta")
    path = f"{OUT}/{TAG}-fig-2-influence.svg"
    compose([a, b],
            title="地震影響向量：兩種支承運動下的剛體位移",
            sub="灰虛線＝原始位置；藍＝剛體位移後（結構本身完全不變形，故與 EI 無關）",
            note="l_theta 的第二項是 h2（轉角的離地高度），不是 h1+h2；u3 向下為正，順時針轉使 m3 下移故取 +x3",
            path=path)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_geometry, fig2_influence):
        print(" ", f())
