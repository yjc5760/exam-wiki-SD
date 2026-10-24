# -*- coding: utf-8 -*-
"""
build_figs_SD-U2-2.py — 產生 lecture-SD-U2-2.html 的全部向量圖（SVG）
所有幾何座標由下列數值計算而來，不手打：
  * 反應譜四段式（台灣規範，T0D = S1D/SDS）
  * Fu 依週期分段（規範式 2-12；SD-2007-1 解析）
  * (SaD/Fu)m 修正式（規範 2.2；SD-2020-4 解析）
  * SD-2025-1 等效靜力法全部數字
  * 弱層判定：該層「強度/設計層剪力」比 < 上層比值 80%（規範表 1-1 第 5 項）
用法：python build_figs_SD-U2-2.py  → 回傳 dict{name: svg_string}，或直接 import FIGS
"""
import math

# ---------- 共用工具 ----------
INK = "#263238"; MUT = "#546e7a"; GRID = "#cfd8dc"; AX = "#455a64"
BLUE = "#1565c0"; BLUE_D = "#0d47a1"; BLUE_L = "#e3f2fd"; BLUE_M = "#90caf9"
RED = "#c62828"; RED_D = "#b71c1c"; RED_L = "#ffebee"; RED_M = "#ef9a9a"
GRN = "#2e7d32"; GRN_D = "#1b5e20"; GRN_L = "#e8f5e9"; GRN_M = "#a5d6a7"
ORG = "#ef6c00"; ORG_D = "#e65100"; ORG_L = "#fff3e0"; ORG_M = "#ffcc80"
PUR = "#6a1b9a"; PUR_L = "#f3e5f5"; PUR_M = "#ce93d8"
GRY_L = "#eceff1"; GRY_M = "#b0bec5"


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if abs(x - round(x)) > 1e-9 else str(int(round(x)))


def T(x, y, s, size=12, anchor="start", fill=INK, weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text x="{f(x)}" y="{f(y)}"{a} font-size="{size}"{w} fill="{fill}"{extra}>{s}</text>'


def L(x1, y1, x2, y2, stroke=AX, w=1.5, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}{extra}/>')


def R(x, y, w, h, fill, stroke=None, rx=6, sw=1.2, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{s}{extra}/>'


def PL(pts, stroke, w=2.5, fill="none", dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    return f'<polyline fill="{fill}" stroke="{stroke}" stroke-width="{w}"{d} points="{p}"{extra}/>'


def PG(pts, fill, stroke="none", w=1, opacity=None):
    o = f' opacity="{opacity}"' if opacity is not None else ""
    p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{o}/>'


def C(x, y, r, fill, stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{fill}"{s}/>'


def marker(mid, color, size=8):
    return (f'<marker id="{mid}" markerWidth="{size}" markerHeight="{size}" refX="{size-1}" '
            f'refY="{size/2}" orient="auto" markerUnits="userSpaceOnUse">'
            f'<path d="M0,0 L{size},{size/2} L0,{size} z" fill="{color}"/></marker>')


def arrow(x1, y1, x2, y2, mid, stroke, w=2):
    return L(x1, y1, x2, y2, stroke, w, extra=f' marker-end="url(#{mid})"')


def svg(w, h, body, label):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{label}">\n' + "\n".join(body) + "\n</svg>")


# ---------- 規範數學 ----------
def Ra_of(R):
    return 1 + (R - 1) / 1.5


def Fu_of(t, Ra):
    """t = T/T0D；規範式 2-12 分段"""
    a = math.sqrt(2 * Ra - 1)
    if t >= 1.0:
        return Ra
    if t >= 0.6:
        return a + (Ra - a) * (t - 0.6) / 0.4
    if t >= 0.2:
        return a
    return a + (a - 1) * (t - 0.2) / 0.2


def Sa_of(t, SDS=1.0):
    """t = T/T0D；S1D = SDS·T0D → S1D/T = SDS/t"""
    if t < 0.2:
        return SDS * (0.4 + 3 * t)
    if t < 1.0:
        return SDS
    if t < 2.5:
        return SDS / t
    return 0.4 * SDS


def m_mod(x):
    if x <= 0.3:
        return x
    if x < 0.8:
        return 0.52 * x + 0.144
    return 0.70 * x


# ---------- SD-2025-1 數字 ----------
N = 8; H1 = 3.5; WI = 20.0; TT = 0.8; I_ = 1.25; SAD = 0.6; FU = 2.0; AY = 1.4
W = N * WI
V0 = I_ * SAD / (1.4 * AY * FU) * W
FT = 0.07 * TT * V0 if TT > 0.7 else 0.0
VP = V0 - FT
SWH = sum(WI * H1 * i for i in range(1, N + 1))
FI = [WI * H1 * i / SWH * VP for i in range(1, N + 1)]
VS = [FT + sum(FI[j] for j in range(i, N)) for i in range(N)]  # 第 i+1 層層剪力
M0 = sum(FI[i] * H1 * (i + 1) for i in range(N)) + FT * H1 * N
HEQ = M0 / V0


# ============================================================
# FIG 0　§0 兩條鏈 ＋ SD-2025-1 數字瀑布
# ============================================================
def fig0():
    b = [f"<defs>{marker('a0r', RED)}{marker('a0g', GRN)}</defs>"]
    b.append(L(460, 14, 460, 352, GRY_M, 2, "7,5"))
    b.append(T(228, 32, "需求側：地震要多少（越乘越大）", 16, "middle", RED, "bold"))
    b.append(T(692, 32, "供給側：結構肯壞多少（越除越小）", 16, "middle", GRN, "bold"))
    left = [("震區係數 SS、S1（危害度分析）", False),
            ("× 場址放大 Fa、Fv（地盤軟硬）", False),
            ("＝ 最大考量地震 SMS、SM1（約 2500 年）", False),
            ("× 2/3（＝÷1.5）→ 設計地震 SDS、S1D（475 年）", True),
            ("代入週期 T → 四段譜 → SaD", False),
            ("× W（地震時跟著晃的重量）→ 彈性需求 Ve", False)]
    right = [("結構系統韌性容量 R（規範表列）", False),
             ("Ra = 1 + (R−1)/1.5（同一個 1.5）", True),
             ("依週期取 Fu：Ra／√(2Ra−1)／內插（§3.2）", False),
             ("÷ αy（起始降伏超強：設計→首根降伏）", False),
             ("÷ 1.4（系統超強：首根降伏→全面塑化）", False),
             ("× I（用途係數：你要多安全）→ 設計力 V", False)]
    for col, items, fill, fill2, st, tx, mid in ((70, left, RED_L, "#ef9a9a", RED, RED_D, "a0r"),
                                                  (534, right, GRN_L, GRN_M, GRN, GRN_D, "a0g")):
        for k, (s, hi) in enumerate(items):
            y = 48 + k * 46
            b.append(R(col, y, 316, 32, fill2 if hi else fill, st))
            b.append(T(col + 158, y + 21, s, 12.5, "middle", tx, "bold" if hi else None))
            if k < len(items) - 1:
                b.append(arrow(col + 158, y + 32, col + 158, y + 45, mid, st, 1.8))
    b.append(T(460, 340, "左右兩個 1.5 是同一件事：設計地震只准用掉「最大考量地震韌性額度」的 2/3（§2.2、§3.3）",
               12.5, "middle", PUR, "bold"))
    # ---- 數字瀑布（SD-2025-1）----
    y0 = 372
    b.append(R(20, y0, 880, 230, "#fafcfd", GRY_M, 10))
    b.append(T(36, y0 + 24, "以 SD-2025-1 走一遍：W = 160 kN、SaD = 0.6、I = 1.25、Fu = 2、αy = 1.4（長度依實際 kN 比例）",
               12.5, "start", INK, "bold"))
    Ve = SAD * W
    steps = [("SaD·W　彈性需求 Ve", Ve, RED, None),
             ("× I = 1.25", Ve * I_, RED, None),
             ("÷ Fu = 2　（允許降伏）", Ve * I_ / FU, GRN, None),
             ("÷ αy = 1.4　（起始降伏超強）", Ve * I_ / FU / AY, GRN, None),
             ("÷ 1.4　（系統超強）→ V", V0, BLUE, None)]
    x0 = 250; sc = 4.6  # px/kN
    for k, (lab, val, col, _) in enumerate(steps):
        y = y0 + 44 + k * 36
        b.append(T(x0 - 10, y + 16, lab, 12, "end", INK))
        b.append(R(x0, y + 2, val * sc, 22, col, None, 3, extra=' opacity="0.85"'))
        b.append(T(x0 + val * sc + 8, y + 18, f"{val:.2f} kN", 12, "start", col, "bold"))
    b.append(T(880, y0 + 214, f"V / Ve = {V0/Ve:.3f}　→　Ve 約為 V 的 {Ve/V0:.2f} 倍（含 I 則 {Ve*I_/V0:.2f} 倍 = 1.4·αy·Fu = {1.4*AY*FU:.2f}）",
               12, "end", MUT))
    return svg(920, 612, b, "耐震規範需求鏈與供給鏈，及 SD-2025-1 數字瀑布")


# ============================================================
# FIG 1　§1 三水準
# ============================================================
def fig1():
    b = []
    P = lambda TR: 1 - (1 - 1 / TR) ** 50
    cards = [
        (20, "中小度地震", GRN_L, "#66bb6a", GRN_D, GRN,
         "50 年超越機率約 80%", "回歸期約 30 年（常常遇到）", "譜值 ≈ SaD / 3（臺北盆地 /2.5）",
         "小震不壞", "立即使用（IO）", "結構保持在彈性限度內", "非結構構件不得損壞",
         "V* = (I·Fu / 4.2αy)(SaD/Fu)m W", "另檢核層間位移角（§5.1）"),
        (320, "設計地震", ORG_L, "#ffa726", ORG_D, ORG,
         "50 年超越機率 10%", "回歸期 475 年（設計主軸）", "譜值 SaD",
         "中震可修", "生命安全（LS）", "可降伏，韌性需求 ≤ Ra", "損壞可修，不危及人命",
         "V = (I / 1.4αy)(SaD/Fu)m W", "§0 那條主式"),
        (620, "最大考量地震", RED_L, "#ef5350", RED_D, RED,
         "50 年超越機率 2%", "回歸期約 2500 年（罕見）", "譜值 SaM ≈ 1.5 SaD",
         "大震不倒", "防止崩塌（CP）", "韌性可用滿至 R", "可不堪修復，但必須站著",
         "VM = (I / 1.4αy)(SaM/FuM)m W", "FuM 以 R（非 Ra）計；另檢核弱層（§5.2）"),
    ]
    for (x, ttl, bg, bd, c1, c2, p1, p2, p3, goal, perf, d1, d2, eq, note) in cards:
        cx = x + 140
        b.append(R(x, 22, 280, 262, bg, bd, 10, 1.8))
        b.append(T(cx, 50, ttl, 16, "middle", c1, "bold"))
        b.append(T(cx, 74, p1, 12.5, "middle", c2))
        b.append(T(cx, 94, p2, 12.5, "middle", c2))
        b.append(T(cx, 114, p3, 12, "middle", MUT))
        b.append(L(x + 25, 126, x + 255, 126, bd, 1))
        b.append(T(cx, 150, goal, 14.5, "middle", c1, "bold"))
        b.append(T(cx, 172, "性能目標：" + perf, 12.5, "middle", INK))
        b.append(T(cx, 194, d1, 12, "middle", MUT))
        b.append(T(cx, 214, d2, 12, "middle", MUT))
        b.append(L(x + 25, 228, x + 255, 228, bd, 1))
        b.append(T(cx, 252, eq, 12.5, "middle", c1, "bold"))
        b.append(T(cx, 272, note, 11, "middle", c2))
    # 回歸期 ↔ 機率 驗算列
    b.append(R(20, 296, 880, 50, GRY_L, GRY_M, 7))
    vals = "　｜　".join(f"T_R = {tr} 年 → P50 = 1−(1−1/{tr})^50 = {P(tr)*100:.1f}%" for tr in (30, 475, 2475))
    b.append(T(460, 316, vals, 11.5, "middle", INK))
    b.append(T(460, 336, "三者「同時」都要滿足，由控制者決定設計 —— 不一定是中間那個（§1.2）", 12.5, "middle", INK, "bold"))
    return svg(920, 356, b, "三水準耐震設計：中小度地震、設計地震、最大考量地震")


# ============================================================
# FIG 1b　§1.2 V*/V 與 VM/V 隨 R 變化
# ============================================================
def fig1b():
    b = []
    X0, X1, Y0, Y1 = 80, 600, 290, 30
    rmin, rmax, ymin, ymax = 1.0, 5.0, 0.0, 1.6
    X = lambda r: X0 + (r - rmin) / (rmax - rmin) * (X1 - X0)
    Y = lambda v: Y0 - (v - ymin) / (ymax - ymin) * (Y0 - Y1)
    for v in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6):
        b.append(L(X0, Y(v), X1, Y(v), GRID if v != 1.0 else AX, 1 if v != 1.0 else 1.6,
                   "3,3" if v != 1.0 else "6,4"))
        b.append(T(X0 - 6, Y(v) + 4, f"{v:.1f}", 11, "end", MUT))
    for r in (1, 2, 3, 4, 5):
        b.append(L(X(r), Y0, X(r), Y0 + 5, AX, 1.2))
        b.append(T(X(r), Y0 + 19, f"{r}", 11, "middle", MUT))
    b.append(L(X0, Y0, X1, Y0, AX)); b.append(L(X0, Y0, X0, Y1 - 8, AX))
    b.append(T((X0 + X1) / 2, Y0 + 38, "結構系統韌性容量 R", 12.5, "middle", INK))
    b.append(T(26, (Y0 + Y1) / 2, "與設計地震力 V 之比", 12.5, "middle", INK,
               extra=f' transform="rotate(-90 26 {(Y0+Y1)/2})"'))
    rs = [rmin + k * 0.02 for k in range(201)]
    def curves(fn):
        return [(X(r), Y(fn(r))) for r in rs]
    vs_long = lambda r: Ra_of(r) / 3
    vs_mid = lambda r: math.sqrt(2 * Ra_of(r) - 1) / 3
    vm_long = lambda r: 1.5 * Ra_of(r) / r
    vm_mid = lambda r: 1.5 * math.sqrt(2 * Ra_of(r) - 1) / math.sqrt(2 * r - 1)
    b.append(PL(curves(vs_long), RED, 3))
    b.append(PL(curves(vs_mid), RED, 2.2, dash="7,4"))
    b.append(PL(curves(vm_long), PUR, 3))
    b.append(PL(curves(vm_mid), PUR, 2.2, dash="7,4"))
    # 交點 R=4
    b.append(C(X(4), Y(1.0), 5, "#fff", RED, 2.5))
    b.append(T(X(4) - 8, Y(1.0) - 10, "R = 4：Fu = 3，V* = V", 11.5, "end", RED, "bold"))
    # R=4.8 標記
    for fn, col, dy in ((vs_long, RED, -10), (vs_mid, RED, 16), (vm_long, PUR, -10), (vm_mid, PUR, -10)):
        b.append(C(X(4.8), Y(fn(4.8)), 4, col))
    b.append(L(X(4.8), Y0, X(4.8), Y1, GRY_M, 1, "3,3"))
    b.append(T(X(4.8), Y1 - 6, "R = 4.8", 11, "middle", MUT))
    b.append(T(X(4.8) + 8, Y(vs_long(4.8)) - 5, f"{vs_long(4.8):.2f}", 11, "start", RED, "bold"))
    b.append(T(X(4.8) + 8, Y(vs_mid(4.8)) + 15, f"{vs_mid(4.8):.2f}", 11, "start", RED))
    b.append(T(X(4.8) + 8, Y(vm_long(4.8)) + 15, f"{vm_long(4.8):.2f}", 11, "start", PUR, "bold"))
    b.append(T(X(4.8) + 8, Y(vm_mid(4.8)) - 5, f"{vm_mid(4.8):.2f}", 11, "start", PUR))
    # 圖例
    lx = 622
    b.append(R(lx, 30, 286, 260, "#fafcfd", GRY_M, 8))
    rows = [(RED, None, "V*/V = Fu/3　長週期（Fu = Ra）"),
            (RED, "7,4", "V*/V = Fu/3　中週期（Fu = √(2Ra−1)）"),
            (PUR, None, "VM/V = 1.5Fu/FuM = 1 + 0.5/R　長週期"),
            (PUR, "7,4", "VM/V　中週期（FuM = √(2R−1)）")]
    for k, (col, dash, s) in enumerate(rows):
        y = 54 + k * 26
        b.append(L(lx + 14, y - 4, lx + 44, y - 4, col, 3 if not dash else 2.2, dash))
        b.append(T(lx + 52, y, s, 11.5, "start", INK))
    b.append(T(lx + 14, 172, "讀圖：", 12, "start", INK, "bold"))
    b.append(T(lx + 14, 192, "• 紅實線過 1.0 → 長週期高韌性建築", 11.5, "start", INK))
    b.append(T(lx + 26, 210, "由「中小度地震」控制", 11.5, "start", RED, "bold"))
    b.append(T(lx + 14, 230, "• 中週期 Fu 小，紅虛線永遠 < 1", 11.5, "start", INK))
    b.append(T(lx + 14, 250, "• VM 只比 V 大 10%～50%", 11.5, "start", INK))
    b.append(T(lx + 14, 270, "　→「地震越大設計力越大」不可靠", 11.5, "start", MUT))
    return svg(920, 340, b, "V*/V 與 VM/V 隨韌性容量 R 的變化")


# ============================================================
# FIG 2　§2.3 四段譜（精確），含交點證明與「縮短週期」陷阱
# ============================================================
def fig2():
    b = [f"<defs>{marker('a2', ORG_D)}</defs>"]
    X0, X1, Y0, Y1 = 80, 650, 290, 40
    tmax = 3.2
    X = lambda t: X0 + t / tmax * (X1 - X0)
    Y = lambda s: Y0 - s / 1.15 * (Y0 - Y1)
    # 分區底色
    zones = [(0, 0.2, BLUE_L, "上升段"), (0.2, 1.0, GRN_L, "平台段 SDS"),
             (1.0, 2.5, ORG_L, "下降段 S1D/T"), (2.5, tmax, PUR_L, "下限 0.4SDS")]
    zc = [BLUE_D, GRN, ORG_D, PUR]
    for (a, c, col, lab), tc in zip(zones, zc):
        b.append(R(X(a), Y1, X(c) - X(a), Y0 - Y1, col, None, 0, extra=' opacity="0.7"'))
        if a > 0:
            b.append(T((X(a) + X(c)) / 2, Y1 + 16, lab, 12, "middle", tc, "bold"))
    b.append(T(X(0.1), Y1 - 6, "上升", 11, "middle", BLUE_D, "bold"))
    # 軸
    b.append(L(X0, Y0, X1 + 6, Y0, AX)); b.append(L(X0, Y0, X0, Y1 - 10, AX))
    for s, lab, col in ((1.0, "SDS", INK), (0.4, "0.4SDS", ORG_D)):
        b.append(L(X0, Y(s), X1, Y(s), GRID if s == 1 else ORG, 1, "4,4"))
        b.append(T(X0 - 6, Y(s) + 4, lab, 11.5, "end", col))
    b.append(T(X0 - 6, Y0 + 4, "0", 11, "end", MUT))
    for t, lab in ((0.2, "0.2T0D"), (0.6, "0.6T0D"), (1.0, "T0D"), (2.0, "2T0D"), (2.5, "2.5T0D"), (3.0, "3T0D")):
        b.append(L(X(t), Y0, X(t), Y0 + 5, AX, 1.2))
        b.append(T(X(t), Y0 + 19, lab, 10.5, "middle", MUT))
    b.append(T((X0 + X1) / 2, Y0 + 40, "結構基本週期 T（以 T0D = S1D/SDS 為單位）", 12.5, "middle", INK))
    b.append(T(28, (Y0 + Y1) / 2, "SaD", 13, "middle", INK, extra=f' transform="rotate(-90 28 {(Y0+Y1)/2})"'))
    # S1D/T 雙曲線延伸（虛線）：左側證明交點，右側「若不截斷」
    hyp_l = [(X(t), Y(1 / t)) for t in [0.87 + k * 0.01 for k in range(14)]]
    b.append(PL(hyp_l, ORG, 1.6, dash="4,3"))
    hyp_r = [(X(t), Y(1 / t)) for t in [2.5 + k * 0.02 for k in range(36)]]
    b.append(PL(hyp_r, "#90a4ae", 1.8, dash="5,4"))
    b.append(T(X(2.95), Y(1 / 2.95) + 18, "若不設下限：S1D/T 續降", 11, "middle", "#78909c"))
    # 主曲線
    ts = [k * 0.005 for k in range(int(tmax / 0.005) + 1)]
    b.append(PL([(X(t), Y(Sa_of(t))) for t in ts], BLUE_D, 3.2))
    # 交界點
    for t in (0.2, 1.0, 2.5):
        b.append(C(X(t), Y(Sa_of(t) if t != 2.5 else 0.4), 4.5, "#fff", BLUE_D, 2.2))
    b.append(C(X0, Y(0.4), 4.5, ORG, None))
    b.append(T(X(0.26), Y(1.0) + 20, "S1D/T 正好在 T0D 交平台", 11, "start", ORG_D))
    # 縮短週期陷阱
    tA, tB = 1.8, 1.25
    b.append(arrow(X(tA), Y(1 / tA) - 12, X(tB) + 6, Y(1 / tB) - 14, "a2", ORG_D, 2))
    b.append(T(X(1.55), Y(1 / 1.55) - 30, "加勁度 → T 縮短 → Sa 變大", 11.5, "middle", ORG_D, "bold"))
    # 右側說明框
    bx = 670
    b.append(R(bx, 40, 238, 122, ORG_L, ORG_M, 8))
    b.append(T(bx + 14, 62, "0.4 從哪來？", 12.5, "start", ORG_D, "bold"))
    b.append(T(bx + 14, 84, "T = 2.5T0D 時：", 11.5, "start", INK))
    b.append(T(bx + 14, 104, "S1D/(2.5T0D) = SDS/2.5", 11.5, "start", INK))
    b.append(T(bx + 14, 124, "= 0.4 SDS", 11.5, "start", INK))
    b.append(T(bx + 14, 148, "0.4 = 1/2.5，不是憑空訂的", 11.5, "start", ORG_D, "bold"))
    b.append(R(bx, 172, 238, 118, BLUE_L, BLUE_M, 8))
    b.append(T(bx + 14, 194, "上升段的 0.4 是同一個", 12.5, "start", BLUE_D, "bold"))
    b.append(T(bx + 14, 216, "T → 0：Sa → 0.4SDS", 11.5, "start", INK))
    b.append(T(bx + 14, 234, "（剛體，等於地表加速度）", 11, "start", MUT))
    b.append(T(bx + 14, 256, "T = 0.2T0D：0.4 + 3×0.2 = 1.0", 11.5, "start", INK))
    b.append(T(bx + 14, 276, "→ 剛好接上平台段 ✔", 11.5, "start", MUT))
    return svg(920, 344, b, "台灣規範設計反應譜四段式")


# ============================================================
# FIG 3　§3.2 等位移 vs 等能量（A1 = A2）
# ============================================================
def fig3():
    b = [f"<defs>{marker('a3', GRN)}</defs>"]
    b.append(L(460, 20, 460, 360, GRY_M, 2, "7,5"))
    b.append(T(230, 30, "長週期：等位移法則（μ = 2）", 15.5, "middle", BLUE, "bold"))
    b.append(T(690, 30, "中週期：等能量法則（μ = 2）", 15.5, "middle", RED, "bold"))
    # 共同比例：Ve = 2.0 單位（左），uy 單位
    def panel(ox, ux, vy):
        return (lambda u: ox + u * ux), (lambda v: 270 - v * vy)
    # 左：uy=1, Vy=1, Ve=2, ue=um=2
    Xl, Yl = panel(70, 120, 92)
    b.append(L(Xl(0), Yl(0), Xl(2.75), Yl(0), AX)); b.append(L(Xl(0), Yl(0), Xl(0), Yl(2.25), AX))
    b.append(T(Xl(2.75), Yl(0) - 7, "u", 13, "end", INK, "bold"))
    b.append(T(Xl(0) + 8, Yl(2.25) + 6, "V", 13, "start", INK, "bold"))
    b.append(L(Xl(0), Yl(0), Xl(2), Yl(2), "#90a4ae", 2, "5,4"))
    b.append(C(Xl(2), Yl(2), 4, "#90a4ae"))
    b.append(T(Xl(2) + 8, Yl(2) + 4, "彈性 (ue, Ve)", 11.5, "start", "#607d8b"))
    b.append(PL([(Xl(0), Yl(0)), (Xl(1), Yl(1)), (Xl(2), Yl(1))], BLUE, 3))
    b.append(C(Xl(1), Yl(1), 4, BLUE)); b.append(C(Xl(2), Yl(1), 4.5, BLUE))
    for u in (1, 2):
        b.append(L(Xl(u), Yl(0), Xl(u), Yl(1 if u == 1 else 2), "#bdbdbd", 1, "3,3"))
    b.append(L(Xl(0), Yl(1), Xl(1), Yl(1), "#bdbdbd", 1, "3,3"))
    b.append(L(Xl(0), Yl(2), Xl(2), Yl(2), "#bdbdbd", 1, "3,3"))
    b.append(T(Xl(1), Yl(0) + 16, "uy", 11.5, "middle", MUT))
    b.append(T(Xl(2), Yl(0) + 16, "um = ue = 2uy", 11.5, "middle", BLUE, "bold"))
    b.append(T(Xl(0) - 6, Yl(1) + 4, "Vy", 11.5, "end", BLUE))
    b.append(T(Xl(0) - 6, Yl(2) + 4, "Ve", 11.5, "end", "#607d8b"))
    b.append(arrow(Xl(2) + 14, Yl(2) + 8, Xl(2) + 14, Yl(1) - 4, "a3", GRN, 2))
    b.append(T(Xl(2) + 22, Yl(1.6), "位移不變", 11.5, "start", GRN))
    b.append(T(Xl(2) + 22, Yl(1.6) + 17, "力小 2 倍", 11.5, "start", GRN, "bold"))
    b.append(R(80, 300, 340, 52, BLUE_L, BLUE_M, 7))
    b.append(T(250, 321, "假設 um = ue（位移被地表鎖住）", 12.5, "middle", BLUE_D))
    b.append(T(250, 342, "Fu = Ve/Vy = ue/uy = μ ⇒ Fu = Ra", 13, "middle", BLUE_D, "bold"))
    # 右：uy=1, Vy=1, Fu=√3, ue=√3, um=2
    s3 = math.sqrt(3)
    Xr, Yr = panel(510, 120, 92)
    b.append(L(Xr(0), Yr(0), Xr(2.95), Yr(0), AX)); b.append(L(Xr(0), Yr(0), Xr(0), Yr(2.25), AX))
    b.append(T(Xr(2.95), Yr(0) - 7, "u", 13, "end", INK, "bold"))
    b.append(T(Xr(0) + 8, Yr(2.25) + 6, "V", 13, "start", INK, "bold"))
    # 共同面積（淺灰）
    b.append(PG([(Xr(0), Yr(0)), (Xr(1), Yr(1)), (Xr(s3), Yr(1)), (Xr(s3), Yr(0))], "#eceff1"))
    # A1：彈性三角形高出 Vy 的部分
    b.append(PG([(Xr(1), Yr(1)), (Xr(s3), Yr(s3)), (Xr(s3), Yr(1))], "#90caf9", BLUE, 1.2, 0.85))
    # A2：彈塑性多出的矩形
    b.append(PG([(Xr(s3), Yr(1)), (Xr(2), Yr(1)), (Xr(2), Yr(0)), (Xr(s3), Yr(0))], "#ef9a9a", RED, 1.2, 0.85))
    b.append(L(Xr(0), Yr(0), Xr(s3), Yr(s3), "#90a4ae", 2, "5,4"))
    b.append(C(Xr(s3), Yr(s3), 4, "#90a4ae"))
    b.append(PL([(Xr(0), Yr(0)), (Xr(1), Yr(1)), (Xr(2), Yr(1))], RED, 3))
    b.append(C(Xr(1), Yr(1), 4, RED)); b.append(C(Xr(2), Yr(1), 4.5, RED))
    b.append(L(Xr(1), Yr(0), Xr(1), Yr(1), "#bdbdbd", 1, "3,3"))
    b.append(L(Xr(0), Yr(s3), Xr(s3), Yr(s3), "#bdbdbd", 1, "3,3"))
    b.append(T(Xr(1), Yr(0) + 16, "uy", 11.5, "middle", MUT))
    b.append(T(Xr(s3) - 4, Yr(0) + 16, "ue", 11.5, "end", "#607d8b"))
    b.append(T(Xr(2) + 4, Yr(0) + 16, "um = 2uy", 11.5, "start", RED, "bold"))
    b.append(T(Xr(0) - 6, Yr(1) + 4, "Vy", 11.5, "end", RED))
    b.append(T(Xr(0) - 6, Yr(s3) + 4, "Ve", 11.5, "end", "#607d8b"))
    b.append(T(Xr(1.48), Yr(1.28), "A1", 12, "middle", BLUE_D, "bold"))
    b.append(T(Xr(1.866), Yr(0.5) + 4, "A2", 12, "middle", RED_D, "bold"))
    b.append(T(Xr(2.08), Yr(1.92), "A1 = ½(√3−1)² = 0.268", 11.5, "start", BLUE_D))
    b.append(T(Xr(2.08), Yr(1.92) + 18, "A2 = 1×(2−√3) = 0.268", 11.5, "start", RED_D))
    b.append(T(Xr(2.08), Yr(1.92) + 38, "A1 = A2 ⇔ 總面積相等", 12, "start", INK, "bold"))
    b.append(T(Xr(2.08), Yr(1.92) + 58, "um > ue：位移「跑掉」", 11.5, "start", RED))
    b.append(R(500, 300, 390, 52, RED_L, RED_M, 7))
    b.append(T(695, 321, "½Ve·ue = Vy(um − uy/2) ⇒ ½Fu² = μ − ½", 12.5, "middle", RED_D))
    b.append(T(695, 342, f"Fu = √(2μ−1) = √3 = {s3:.3f} ⇒ Fu = √(2Ra−1)", 13, "middle", RED_D, "bold"))
    return svg(920, 362, b, "等位移法則與等能量法則的力-位移圖")


# ============================================================
# FIG 3b　§3.2 Fu 隨週期（規範式 2-12）
# ============================================================
def fig3b():
    b = []
    X0, X1, Y0, Y1 = 80, 640, 280, 40
    tmax, ymax = 1.6, 4.0
    X = lambda t: X0 + t / tmax * (X1 - X0)
    Y = lambda v: Y0 - v / ymax * (Y0 - Y1)
    zones = [(0, 0.2, BLUE_L, "等加速度", BLUE_D), (0.2, 0.6, RED_L, "等能量", RED),
             (0.6, 1.0, GRY_L, "線性內插", MUT), (1.0, tmax, GRN_L, "等位移", GRN)]
    for a, c, col, lab, tc in zones:
        b.append(R(X(a), Y1, X(c) - X(a), Y0 - Y1, col, None, 0, extra=' opacity="0.75"'))
        b.append(T((X(a) + X(c)) / 2, Y0 - 10, lab, 12, "middle", tc, "bold"))
    b.append(L(X0, Y0, X1 + 6, Y0, AX)); b.append(L(X0, Y0, X0, Y1 - 10, AX))
    for v in (1, 2, 3, 4):
        b.append(L(X0, Y(v), X1, Y(v), GRID, 1, "3,3"))
        b.append(T(X0 - 6, Y(v) + 4, str(v), 11, "end", MUT))
    for t, lab in ((0, "0"), (0.2, "0.2T0D"), (0.6, "0.6T0D"), (1.0, "T0D"), (1.4, "1.4T0D")):
        b.append(L(X(t), Y0, X(t), Y0 + 5, AX, 1.2))
        b.append(T(X(t), Y0 + 19, lab, 10.5, "middle", MUT))
    b.append(T((X0 + X1) / 2, Y0 + 40, "結構基本週期 T", 12.5, "middle", INK))
    b.append(T(30, (Y0 + Y1) / 2, "韌性折減係數 Fu", 12.5, "middle", INK, extra=f' transform="rotate(-90 30 {(Y0+Y1)/2})"'))
    ts = [k * 0.005 for k in range(int(tmax / 0.005) + 1)]
    for Rv, col, dash in ((4.8, BLUE_D, None), (2.4, ORG_D, "7,4")):
        ra = Ra_of(Rv); a = math.sqrt(2 * ra - 1)
        b.append(PL([(X(t), Y(Fu_of(t, ra))) for t in ts], col, 3 if not dash else 2.4, dash=dash))
        b.append(T(X(1.42), Y(ra) - 8, f"R = {Rv}：Fu = Ra = {ra:.3f}", 11.5, "middle", col, "bold"))
        b.append(T(X(0.4), Y(a) - 8, f"√(2Ra−1) = {a:.3f}", 11.5, "middle", col))
        for t in (0.2, 0.6, 1.0):
            b.append(C(X(t), Y(Fu_of(t, ra)), 3.8, "#fff", col, 2))
    b.append(C(X(0), Y(1), 4.5, INK))
    b.append(T(X(0) + 8, Y(1) + 16, "T→0：Fu = 1（剛體隨地面，韌性用不上）", 11, "start", INK))
    bx = 660
    b.append(R(bx, 40, 248, 240, "#fafcfd", GRY_M, 8))
    rows = [("規範式 2-12（t = T/T0D）", INK, "bold"),
            ("t ≥ 1.0：Fu = Ra", GRN, None),
            ("0.6 ≤ t < 1.0：", MUT, None),
            ("　√(2Ra−1) + (Ra−√(2Ra−1))·(t−0.6)/0.4", MUT, None),
            ("0.2 ≤ t < 0.6：Fu = √(2Ra−1)", RED, None),
            ("t < 0.2：", BLUE_D, None),
            ("　√(2Ra−1) + (√(2Ra−1)−1)·(t−0.2)/0.2", BLUE_D, None),
            ("", INK, None),
            ("「中週期」是 0.2～0.6 T0D，", INK, "bold"),
            ("不是固定秒數 —— 換到軟弱地盤", INK, None),
            ("T0D 變大，同一棟樓會掉回中週期", INK, None)]
    for k, (s, col, wt) in enumerate(rows):
        b.append(T(bx + 12, 62 + k * 20, s, 11 if k in (3, 6) else 11.5, "start", col, wt))
    return svg(920, 334, b, "韌性折減係數 Fu 隨週期的規範分段")


# ============================================================
# FIG 3c　§3.4 (SaD/Fu)m 修正
# ============================================================
def fig3c():
    b = []
    X0, X1, Y0, Y1 = 80, 520, 290, 40
    xm = 1.2
    X = lambda x: X0 + x / xm * (X1 - X0)
    Y = lambda y: Y0 - y / xm * (Y0 - Y1)
    b.append(R(X(0.3), Y1, X(0.8) - X(0.3), Y0 - Y1, ORG_L, None, 0))
    b.append(R(X(0.8), Y1, X(xm) - X(0.8), Y0 - Y1, RED_L, None, 0))
    b.append(L(X0, Y0, X1 + 6, Y0, AX)); b.append(L(X0, Y0, X0, Y1 - 10, AX))
    for v in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2):
        b.append(L(X0, Y(v), X1, Y(v), GRID, 1, "3,3"))
        b.append(T(X0 - 6, Y(v) + 4, f"{v:.1f}", 11, "end", MUT))
        b.append(T(X(v), Y0 + 18, f"{v:.1f}", 11, "middle", MUT))
    b.append(T((X0 + X1) / 2, Y0 + 38, "SaD / Fu（修正前）", 12.5, "middle", INK))
    b.append(T(30, (Y0 + Y1) / 2, "(SaD / Fu)m", 12.5, "middle", INK, extra=f' transform="rotate(-90 30 {(Y0+Y1)/2})"'))
    b.append(L(X(0), Y(0), X(xm), Y(xm), "#90a4ae", 1.6, "6,4"))
    b.append(T(X(0.47), Y(0.56), "1 : 1（不修正）", 11, "end", "#78909c"))
    xs = [k * 0.004 for k in range(301)]
    b.append(PL([(X(x), Y(m_mod(x))) for x in xs], BLUE_D, 3.2))
    for x in (0.3, 0.8):
        b.append(C(X(x), Y(m_mod(x)), 4.5, "#fff", BLUE_D, 2.2))
        b.append(T(X(x) + 8, Y(m_mod(x)) + 18, f"({x}, {m_mod(x):.2f})", 11, "start", BLUE_D, "bold"))
    b.append(T(X(0.15), Y1 + 18, "≤ 0.3", 11.5, "middle", INK, "bold"))
    b.append(T(X(0.55), Y1 + 18, "0.52x + 0.144", 11.5, "middle", ORG_D, "bold"))
    b.append(T(X(1.0), Y1 + 18, "0.70x", 11.5, "middle", RED, "bold"))
    b.append(T(X(1.0), Y(0.70) + 26, "最多折掉 30%", 11.5, "middle", RED))
    bx = 545
    b.append(R(bx, 40, 363, 250, "#fafcfd", GRY_M, 8))
    rows = [("下標 m 是「修正值」，不是取大值、也不是短週期規定", INK, "bold", 12),
            ("", INK, None, 11),
            ("SaD/Fu 大 → 結構被要求進入較深的非彈性", INK, None, 11.5),
            ("→ 遲滯消能使等效阻尼比 > 5%", INK, None, 11.5),
            ("→ 在 5% 阻尼譜上再打折", INK, None, 11.5),
            ("", INK, None, 11),
            ("兩個分界點皆連續：0.3 → 0.30、0.8 → 0.56", MUT, None, 11.5),
            ("", INK, None, 11),
            ("V、V*、VM 三式都套同一個修正", PUR, "bold", 11.5),
            ("→ V*/V = Fu/3 不受影響（引數相同）", PUR, None, 11.5),
            ("→ VM/V 會受影響（引數 SaM/FuM 不同）", PUR, None, 11.5),
            ("", INK, None, 11),
            ("SD-2025-1：0.6/2 = 0.30 → 剛好落在第一段", BLUE_D, None, 11.5)]
    for k, (s, col, wt, sz) in enumerate(rows):
        b.append(T(bx + 14, 64 + k * 17.5, s, sz, "start", col, wt))
    return svg(920, 344, b, "(SaD/Fu)m 修正式")


# ============================================================
# FIG 4　§4 SD-2025-1 側力分配與層剪力（真實數字）
# ============================================================
def fig4():
    b = [f"<defs>{marker('a4b', BLUE)}{marker('a4o', ORG_D)}</defs>"]
    gy = 360; sh = 36  # 每層像素
    yF = lambda i: gy - i * sh  # 第 i 層樓板 (i=1..8)
    bx0, bx1 = 110, 210
    # 構架
    b.append(L(bx0 - 30, gy, bx1 + 30, gy, AX, 4))
    for k in range(9):
        b.append(L(bx0 - 30 + k * 20, gy, bx0 - 40 + k * 20, gy + 10, AX, 1))
    b.append(L(bx0, gy, bx0, yF(8), "#90a4ae", 2)); b.append(L(bx1, gy, bx1, yF(8), "#90a4ae", 2))
    for i in range(1, 9):
        b.append(L(bx0, yF(i), bx1, yF(i), "#607d8b", 3))
        b.append(T(bx0 - 8, yF(i) + 4, f"{i}F", 11, "end", MUT))
        b.append(T(bx0 - 40, yF(i) + 4, f"{H1*i:g}", 10.5, "end", "#90a4ae"))
    b.append(T(bx0 - 40, gy - 4 - 8 * sh - 14, "h (m)", 10.5, "end", "#90a4ae"))
    b.append(T((bx0 + bx1) / 2, gy + 28, "w = 20 kN/層，h = 3.5 m/層", 11.5, "middle", INK))
    # 力箭頭：往左打在構架左側（箭頭指向構架）
    sc = 13.0  # px per kN
    for i in range(1, 9):
        Fi = FI[i - 1]
        xs = bx1 + 6 + Fi * sc
        b.append(L(xs, yF(i), bx1 + 6, yF(i), BLUE, 2.6, extra=' marker-end="url(#a4b)"'))
        b.append(T(xs + 6, yF(i) + 4, f"{Fi:.3f}", 11, "start", BLUE))
    xs = bx1 + 6 + (FI[7] + FT) * sc
    b.append(L(xs, yF(8) - 13, bx1 + 6, yF(8) - 13, ORG_D, 3, extra=' marker-end="url(#a4o)"'))
    b.append(T(xs + 6, yF(8) - 9, f"Ft = {FT:.3f}", 11.5, "start", ORG_D, "bold"))
    b.append(T(bx1 + 6, yF(8) - 46, "側力 Fi（kN）＝ i/36 × (V − Ft)", 12, "start", BLUE_D, "bold"))
    b.append(T(bx1 + 6, yF(8) - 30, "箭頭長度依 kN 比例", 11, "start", MUT))
    # 層剪力圖
    S0 = 470; sv = 7.4  # px/kN
    b.append(L(S0, gy, S0, yF(8) - 18, AX, 1.5))
    b.append(L(S0, gy, S0 + 34 * sv, gy, AX, 1.5))
    for v in (0, 10, 20, 30):
        b.append(L(S0 + v * sv, gy, S0 + v * sv, gy + 5, AX, 1.2))
        b.append(T(S0 + v * sv, gy + 18, str(v), 11, "middle", MUT))
    b.append(T(S0 + 17 * sv, gy + 36, "層剪力 Vi（kN）", 12, "middle", INK))
    pts = []
    for i in range(8, 0, -1):
        top, bot = yF(i), yF(i - 1)
        pts += [(S0 + VS[i - 1] * sv, top), (S0 + VS[i - 1] * sv, bot)]
    poly = [(S0, yF(8))] + pts + [(S0, gy)]
    b.append(PG(poly, RED_L, RED, 1.5))
    for i in range(1, 9):
        ym = (yF(i) + yF(i - 1)) / 2
        b.append(T(S0 + VS[i - 1] * sv + 6, ym + 4, f"{VS[i-1]:.2f}", 11, "start", RED_D, "bold" if i == 1 else None))
    b.append(T(S0 + 2, yF(8) - 26, "Vi = Ft + Σ(j≥i) Fj　（由上往下累加）", 12, "start", RED_D, "bold"))
    # 右側檢核
    bx = 742
    b.append(R(bx, 64, 166, 296, ORG_L, ORG_M, 8))
    rows = [("SD-2025-1 數字", ORG_D, "bold"),
            (f"V0 = {V0:.2f} kN", INK, None),
            (f"Ft = 0.07TV0 = {FT:.3f}", INK, None),
            (f"V0 − Ft = {VP:.2f}", INK, None),
            (f"ΣFi + Ft = {sum(FI)+FT:.2f} ✔", GRN, "bold"),
            ("", INK, None),
            (f"M0 = {M0:.1f} kN·m", INK, "bold"),
            (f"h_eq = M0/V0 = {HEQ:.1f} m", INK, None),
            (f"　　= {HEQ/(N*H1):.3f} H", INK, None),
            ("", INK, None),
            ("力：上大下小", BLUE_D, "bold"),
            ("剪力：上小下大", RED_D, "bold"),
            ("底層剪力 = V0", RED_D, None)]
    for k, (s, col, wt) in enumerate(rows):
        b.append(T(bx + 12, 88 + k * 21, s, 11.5, "start", col, wt))
    return svg(920, 410, b, "SD-2025-1 側力豎向分配與層剪力")


# ============================================================
# FIG 5　§5.2 跳層斷面：需求/供給 ＋ 強度需求比與 80% 判定
# ============================================================
WEAK_N = 12
DEM = [1 - (i - 1) * i / (WEAK_N * (WEAK_N + 1)) for i in range(1, WEAK_N + 1)]
SUP = [1.30] * 4 + [0.88] * 4 + [0.58] * 4
RAT = [s / d for s, d in zip(SUP, DEM)]
FLAG = [i < WEAK_N - 1 and RAT[i] < 0.8 * RAT[i + 1] for i in range(WEAK_N)]
SUP_G = [1.18 * d + 0.06 for d in DEM]  # 漸進縮減示意
RAT_G = [s / d for s, d in zip(SUP_G, DEM)]


def fig5():
    b = []
    # 左：剪力剖面
    X0, X1, Y0 = 70, 400, 330
    sh = 22.5
    yS = lambda i: Y0 - i * sh  # 第 i 層頂
    X = lambda v: X0 + v / 1.4 * (X1 - X0)
    b.append(L(X0, Y0, X1 + 6, Y0, AX)); b.append(L(X0, Y0, X0, yS(12) - 10, AX))
    for v in (0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4):
        b.append(L(X(v), Y0, X(v), Y0 + 5, AX, 1.2))
        b.append(T(X(v), Y0 + 18, f"{v:.1f}", 10.5, "middle", MUT))
    b.append(T((X0 + X1) / 2, Y0 + 36, "層剪力（以 1F 需求 = 1）", 12, "middle", INK))
    for i in range(1, 13):
        b.append(T(X0 - 6, (yS(i) + yS(i - 1)) / 2 + 4, f"{i}F", 10.5, "end", MUT))
        b.append(L(X0, yS(i), X1, yS(i), "#eceff1", 1))
    def step(vals, col, w, dash=None):
        pts = []
        for i in range(12):
            pts += [(X(vals[i]), yS(i)), (X(vals[i]), yS(i + 1))]
        return PL(pts, col, w, dash=dash)
    b.append(step(SUP_G, GRN, 2, "6,4"))
    b.append(step(DEM, RED, 2.6))
    b.append(step(SUP, BLUE, 2.8))
    b.append(T(X(DEM[6]) - 6, yS(6) + 14, "需求", 11.5, "end", RED, "bold"))
    b.append(T(X(SUP[0]) + 4, yS(2), "供給", 11.5, "start", BLUE, "bold"))
    b.append(T(X(SUP_G[9]) + 6, yS(10) + 4, "漸進縮減", 11, "start", GRN))
    b.append(T(X0, 22, "① 層剪力需求 vs 極限層剪力強度", 13, "start", INK, "bold"))
    # 右：比值長條
    P0, P1 = 520, 760
    Xr = lambda r: P0 + r / 4.0 * (P1 - P0)
    b.append(T(P0 - 40, 22, "② 強度 / 需求 比值 ri 與 80% 判定", 13, "start", INK, "bold"))
    b.append(L(P0, Y0, P1 + 6, Y0, AX)); b.append(L(P0, Y0, P0, yS(12) - 10, AX))
    for v in (1, 2, 3, 4):
        b.append(L(Xr(v), Y0, Xr(v), yS(12), GRID, 1, "3,3"))
        b.append(T(Xr(v), Y0 + 18, str(v), 10.5, "middle", MUT))
    b.append(L(Xr(1), Y0, Xr(1), yS(12), AX, 1.4, "6,3"))
    b.append(T((P0 + P1) / 2, Y0 + 36, "ri = 該層強度 ÷ 該層設計層剪力", 12, "middle", INK))
    for i in range(12):
        yc = (yS(i) + yS(i + 1)) / 2
        col = RED if FLAG[i] else (ORG if i in (4, 8) else BLUE)
        b.append(R(P0, yc - 7, Xr(min(RAT[i], 4.0)) - P0, 14, col, None, 2, extra=' opacity="0.85"'))
        b.append(T(P0 - 6, yc + 4, f"{i+1}F", 10.5, "end", MUT))
        lab = f"{RAT[i]:.2f}"
        if i < 11:
            lab += f"　r{i+1}/r{i+2} = {RAT[i]/RAT[i+1]:.2f}"
        b.append(T(max(Xr(min(RAT[i], 4.0)), Xr(RAT_G[i])) + 8, yc + 4, lab, 10.5, "start",
                   RED if FLAG[i] else INK, "bold" if FLAG[i] else None))
        b.append(C(Xr(RAT_G[i]), yc, 3, GRN))
    # 圖例
    ly = 384
    b.append(R(20, ly, 880, 72, "#fafcfd", GRY_M, 8))
    b.append(R(36, ly + 14, 14, 12, RED, None, 2)); b.append(T(56, ly + 25, "ri < 0.8·r(i+1)：判定為弱層（規範表 1-1 立面不規則第 5 項）", 11.5, "start", RED, "bold"))
    b.append(R(36, ly + 36, 14, 12, ORG, None, 2)); b.append(T(56, ly + 47, "ri 鋸齒低點（5F、9F）：VM 下最先降伏、非線性變形最先集中處（9F 同時被判弱層）", 11.5, "start", ORG_D))
    b.append(C(43, ly + 62, 4, GRN)); b.append(T(56, ly + 66, f"漸進縮減（綠虛線）：ri 全部落在 {min(RAT_G):.2f}～{max(RAT_G):.2f}，相鄰比 ≥ {min(RAT_G[i]/RAT_G[i+1] for i in range(11)):.2f}，無弱層", 11.5, "start", GRN))
    return svg(920, 466, b, "12 層跳層斷面：需求與供給剖面、強度需求比與弱層判定")


# ============================================================
# FIG 6　§7 決策流程（沿用版面，修正內容）
# ============================================================
def fig6(orig_svg):
    s = orig_svg
    s = s.replace("1.5 → 韌性只認 2/3（§3.3）", "1.5 → SaM/SaD，與 2/3 同源（§3.3）")
    s = s.replace("Fu → 等位移／等能量（§3.2）", "Fu → 等位移／等能量／內插（§3.2）")
    s = s.replace("倒三角合力在 2/3 H，加 Ft 略高", "離散樓層 ≈0.71H，加 Ft 再高一點")
    s = s.replace("③ 點出現行規範版本的差異（如 Ft 已淡出）", "③ 點出規範版本差異（如 Ft、中小度地震回歸期）")
    s = s.replace('<svg viewBox="0 0 920 660" xmlns="http://www.w3.org/2000/svg">',
                  '<svg viewBox="0 0 920 660" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SD-U2-2 解題決策流程">')
    return s


FIG_FUNCS = dict(fig0=fig0, fig1=fig1, fig1b=fig1b, fig2=fig2, fig3=fig3, fig3b=fig3b,
                 fig3c=fig3c, fig4=fig4, fig5=fig5)

if __name__ == "__main__":
    print(f"V0={V0:.4f} Ft={FT:.4f} M0={M0:.2f} heq={HEQ:.3f} ({HEQ/28:.4f}H)")
    print("Fi", [round(x, 3) for x in FI]); print("Vi", [round(x, 3) for x in VS])
    print("ratios", [round(x, 3) for x in RAT]); print("flags", FLAG)
    print("grad", [round(x, 3) for x in RAT_G])
