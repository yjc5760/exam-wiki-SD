#!/usr/bin/env python3
"""
SD-2011-4 隔震規範論述題 — 圖解產生腳本（struct-diagram）

用法：python3 gen_SD-2011-4.py [輸出目錄]

本題為論述題，無數值解。圖中所有曲線、比值皆由下方常數區「算出」，
常數區只放兩類數字：
  (a) 取自本題解析或同卷考題的數值（標明出處）
  (b) 示範用參數（標明「示範」），只決定曲線長相，不作為答案
"""
import sys, os, math
import numpy as np

SKILL = os.environ.get("STRUCTDRAW", os.path.join(os.path.dirname(__file__), "scripts"))
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, FONT_M, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2011-4"

# ══════════════════════════════════════════════════════════
# 常數區
# ══════════════════════════════════════════════════════════
# 圖 1（一）：剪力屋架示範模型（示範參數；只用來說明振態形狀差異）
N_STORY   = 6          # 總樓層數
ISO_LEVEL = 3          # 中間層隔震：隔震層位於第 3 層之上
K_STORY   = 1.0        # 每層勁度（正規化）
K_ISO     = K_STORY / 25   # 隔震層勁度（示範：約為一般樓層 1/25）
M_FLOOR   = 1.0        # 每層質量（正規化）

# 圖 2（三）⑴⑵：遲滯迴圈（位移正規化 D = 1；示範參數）
D_MAX   = 1.0
ISO_Q   = 0.12         # 隔震支承特性強度 Q_d
ISO_KD  = 0.30         # 隔震支承降伏後勁度 K_d
ISO_K1  = 3.0          # 隔震支承初始勁度
DEV_FY  = 0.15         # 位移型元件降伏力
DEV_K   = 1.5          # 位移型元件彈性勁度
VE_K1   = 0.15         # 黏彈性元件儲存勁度 k'
VE_K2   = 0.15         # 黏彈性元件損失勁度 k''
FVD_F0  = 0.15         # 液態黏滯阻尼器在最大速度時的出力
FVD_ALPHA = (1.0, 0.3) # 速度指數 α（線性 / 非線性）

# 圖 3（四）：反應譜取自同一張考卷第一題（SD-2011-1）
SA_PLATEAU = 0.6       # S_aD = 0.6/B_S，0.2 < T ≤ 1.0
T0D        = 1.0       # 轉角週期
def sa(T, B=1.0):
    """同卷第一題之 S_aD；T > 2.5T0 段依規範取 0.4 S_DS（與 0.6/T 在 2.5 s 連續）"""
    if T <= T0D:       return SA_PLATEAU / B
    if T <= 2.5 * T0D: return SA_PLATEAU * T0D / T / B
    return 0.4 * SA_PLATEAU / B
B1_20 = 1.50           # 同卷第一題表：ξ = 20% → B_1 = 1.50
# 解析（四）所述週期範圍：隔震目標 2.0–3.0 s；高聳建築原週期 2–4 s
T_LOW_FIX, T_LOW_ISO   = 0.5, 2.5    # 一般中低層建築（示範取值）
T_TALL_FIX, T_TALL_ISO = 3.0, 4.0    # 高聳建築（示範取值，落在解析所述 2–4 s）

# 圖 4（四）：傾覆檢核（規範豎向分配 F_x ∝ w_x h_x，均勻質量 → 合力高度 2H/3）
HBAR_OVER_H = 2 / 3
CS_LIST = (0.10, 0.15, 0.20)          # 隔震後上部結構設計係數（示範區間）
HB_RANGE = (1.0, 8.0)


# ══════════════════════════════════════════════════════════
# 圖 1　基底隔震 vs 中間層隔震
# ══════════════════════════════════════════════════════════
def shear_mode1(ks, ms):
    """剪力屋架第一振態；ks[i] 為第 i 層（自下而上）勁度。回傳含地面 0 的位移列。"""
    n = len(ks)
    K = np.zeros((n, n))
    for i, k in enumerate(ks):
        K[i, i] += k
        if i > 0:
            K[i-1, i-1] += k; K[i-1, i] -= k; K[i, i-1] -= k
    M = np.diag(ms)
    w2, V = np.linalg.eig(np.linalg.solve(M, K))
    j = np.argmin(w2.real)
    phi = V[:, j].real
    phi = phi / phi[np.argmax(abs(phi))]
    return [0.0] + list(phi), math.sqrt(w2.real[j])


def _building(cv, x0, iso_after, phi, title, sub, notes, ncol):
    """iso_after：隔震層位於第幾個樓板之上（0 = 基底）。"""
    cv.panel(title, sub)
    H_ST, Wd = 46, 120
    g = 120                          # 地面像素 y（由底起算，數學座標）
    total = N_STORY + 1              # 含隔震層
    # 樓層高程（隔震層以薄層表示）
    levels, y = [g], g
    for s in range(total):
        y += 26 if s == iso_after else H_ST
        levels.append(y)
    cv.line((x0 - 30, g), (x0 + Wd + 30, g), C["member"], 2.4)
    for k in range(7):
        xx = x0 - 26 + k * 28
        cv.line((xx, g), (xx - 10, g - 12), C["member"], 1.4)
    # 未變形輪廓（灰）
    cv.poly([(x0, g), (x0, levels[-1]), (x0 + Wd, levels[-1]), (x0 + Wd, g)], C["ghost"], 2.2, dash="6 5")
    # 變形後：phi 長度 = total+1（含地面）
    amp = 70
    xs = [x0 + amp * p for p in phi]
    for i in range(total):
        y0, y1 = levels[i], levels[i+1]
        is_iso = (i == iso_after)
        col = C["accent"] if is_iso else C["deform"]
        if is_iso:
            cv.polygon([(xs[i], y0), (xs[i] + Wd, y0), (xs[i+1] + Wd, y1), (xs[i+1], y1)],
                       "rgba(180,83,9,0.16)", C["accent"], 1.6)
            for b in range(4):
                bx0 = xs[i] + 14 + b * 30; bx1 = xs[i+1] + 14 + b * 30
                cv.line((bx0, y0 + 3), (bx1 + 6, y1 - 3), C["accent"], 2)
                cv.line((bx0 + 6, y0 + 3), (bx1, y1 - 3), C["accent"], 2)
        else:
            cv.line((xs[i], y0), (xs[i+1], y1), col, 3.2)
            cv.line((xs[i] + Wd, y0), (xs[i+1] + Wd, y1), col, 3.2)
        cv.line((xs[i+1], y1), (xs[i+1] + Wd, y1), C["member"], 3.0)
    # 標籤
    cv.text_px(cv.X(x0 + Wd + 52 + amp), cv.Y((levels[iso_after] + levels[iso_after+1]) / 2),
               "隔震層", 13, C["accent"], "start", weight="700")
    ycol = cv.h - 92
    for i, (t, c) in enumerate(notes):
        cv.text_px(cv.w / 2, ycol + i * 21, t, 12.8, c)


def fig1_story():
    PW, PH = 400, 560
    # 基底隔震：第 0 層為隔震層
    ks_b = [K_ISO] + [K_STORY] * N_STORY
    phi_b, _ = shear_mode1(ks_b, [M_FLOOR] * (N_STORY + 1))
    ks_m = [K_STORY] * ISO_LEVEL + [K_ISO] + [K_STORY] * (N_STORY - ISO_LEVEL)
    phi_m, _ = shear_mode1(ks_m, [M_FLOOR] * (N_STORY + 1))
    drift_b = phi_b[1] - phi_b[0]
    sub_m = phi_m[ISO_LEVEL]          # 隔震層底（下部結構頂）位移

    a = Canvas(PW, PH)
    _building(a, 95, 0, phi_b, "基底隔震（規範第九章對象）", "隔震層以下 ＝ 剛性基礎",
              [("下部 ＝ 地面，無動力反應", C["muted"]),
               (f"隔震層變形占頂層位移 {drift_b/phi_b[-1]*100:.0f}%", C["accent"]),
               ("上部結構近似剛體平移", C["deform"])], 0)
    b = Canvas(PW, PH)
    _building(b, 95, ISO_LEVEL, phi_m, "中間層隔震", "隔震層以下 ＝ 有柔性、有質量的下部結構",
              [("下部結構本身也在振動、承受慣性力", C["load"]),
               (f"下部結構頂已位移 {sub_m/phi_m[-1]*100:.0f}% 頂層值", C["load"]),
               ("規範「下部固定」假設不成立", C["load"])], 0)
    path = f"{OUT}/{TAG}-fig-1-story.svg"
    compose([a, b], title="圖 1　基底隔震與中間層隔震的第一振態（剪力屋架特徵分析）",
            sub=f"示範模型：{N_STORY} 層＋隔震層，各層質量相同；隔震層勁度 ＝ 一般樓層 1/{round(K_STORY/K_ISO)}",
            note="藍＝結構樓層變形，橙＝隔震層，灰虛線＝未變形位置。振態由特徵值分析算出，非手繪。",
            path=path)
    return path


# ══════════════════════════════════════════════════════════
# 圖 2　遲滯迴圈對比
# ══════════════════════════════════════════════════════════
N_T = 720
TT = np.linspace(0, 2 * math.pi, N_T + 1)


def bilinear_loop(k1, kd, q):
    """雙線性模型的穩態迴圈（u = D sinωt，走兩圈取第二圈）"""
    fy = q * k1 / (k1 - kd) if k1 > kd else q
    uy = fy / k1
    u_hist = D_MAX * np.sin(np.concatenate([TT, TT[1:] + 2 * math.pi]))
    f, fp, up = [], 0.0, 0.0
    for u in u_hist:
        ft = fp + k1 * (u - up)
        hi = kd * u + q; lo = kd * u - q
        ft = min(max(ft, lo), hi)
        f.append(ft); fp, up = ft, u
    n = len(TT)
    return u_hist[-n:], np.array(f[-n:])


def epp_loop(k, fy):
    u_hist = D_MAX * np.sin(np.concatenate([TT, TT[1:] + 2 * math.pi]))
    f, fp, up = [], 0.0, 0.0
    for u in u_hist:
        ft = min(max(fp + k * (u - up), -fy), fy)
        f.append(ft); fp, up = ft, u
    n = len(TT)
    return u_hist[-n:], np.array(f[-n:])


def keff_beta(u, f):
    """規範定義：K_eff = (|F+|+|F-|)/(|Δ+|+|Δ-|)，β = E_loop/(2π K_eff D²)"""
    keff = (f[np.argmax(u)] - f[np.argmin(u)]) / (u.max() - u.min())
    E = abs(np.trapezoid(f, u)) if hasattr(np, "trapezoid") else abs(np.trapz(f, u))
    return keff, E / (2 * math.pi * keff * D_MAX ** 2), E


def _loop_panel(title, sub, curves, keff_lines, info, PW=440, PH=520):
    cv = Canvas(PW, PH)
    cv.panel(title, sub)
    cx, cy, sx, sy = PW / 2, 290, 150, 215     # 原點像素（數學座標 y 由底起算）、比例
    P = lambda u, f: (cx + u * sx, cy + f * sy)
    cv.line(P(-1.2, 0), P(1.2, 0), C["dim"], 1.2)
    cv.line(P(0, -0.62), P(0, 0.62), C["dim"], 1.2)
    cv.math(P(1.2, 0), "u", 14, C["muted"], "start", dx=6)
    cv.math(P(0, 0.62), "F", 14, C["muted"], dy=-10)
    for xv in (-1, 1):
        cv.line(P(xv, -0.03), P(xv, 0.03), C["dim"], 1.2)
    cv.math(P(1, 0), "D", 13, C["muted"], dx=8, dy=14)
    for (u, f, col, w, dash) in curves:
        cv.poly([P(a, b) for a, b in zip(u, f)], col, w, dash=dash)
    for (k, col, lab, dy) in keff_lines:
        cv.line(P(-1.1, -1.1 * k), P(1.1, 1.1 * k), col, 1.6, dash="5 4")
        cv.math(P(1.1, 1.1 * k), lab, 13, col, "start", dx=4, dy=dy, weight="700")
    for i, (t, col, is_math) in enumerate(info):
        y = PH - 84 + i * 22
        (cv.math_px if is_math else cv.text_px)(PW / 2, y, t, 13, col, weight="700")
    return cv


def fig2_loops():
    u0, f0 = bilinear_loop(ISO_K1, ISO_KD, ISO_Q)
    k0, b0, E0 = keff_beta(u0, f0)
    T_iso = 1.0                                   # 以原隔震系統週期正規化

    # (a) + 位移型元件
    ud, fd = epp_loop(DEV_K, DEV_FY)
    fa = f0 + fd
    ka, ba, _ = keff_beta(u0, fa)
    Ta = T_iso * math.sqrt(k0 / ka)

    # (b) + 黏彈性元件：F = k'u + (k''/ω) u̇；u = D sinθ → u̇/ω = D cosθ
    uv = D_MAX * np.sin(TT); fv = VE_K1 * uv + VE_K2 * D_MAX * np.cos(TT)
    fb = f0 + VE_K1 * u0 + VE_K2 * D_MAX * np.cos(TT)
    kb, bb, _ = keff_beta(u0, fb)
    Tb = T_iso * math.sqrt(k0 / kb)

    # (c) FVD：F = F0·sgn(u̇)|u̇/u̇max|^α，u̇ ∝ cosθ
    c_curves = []
    for al, col, w in ((FVD_ALPHA[0], C["sfd"], 3.0), (FVD_ALPHA[1], C["sfd"], 2.0)):
        v = np.cos(TT)
        ff = FVD_F0 * np.sign(v) * np.abs(v) ** al
        c_curves.append((u0, ff, col, w, None if al == 1 else "6 4"))
    f_at_D = c_curves[0][1][np.argmax(u0)]
    E_fvd = abs(np.trapezoid(c_curves[0][1], u0))
    fc = f0 + c_curves[0][1]
    kc, bc, _ = keff_beta(u0, fc)
    xi_fvd = E_fvd / (4 * math.pi * 0.5 * k0 * D_MAX ** 2)

    base = (u0, f0, C["ghost"], 2.4, "6 4")
    pa = _loop_panel("(a) 加位移型元件（降伏型）", "元件提供勁度 → 迴圈變陡",
                     [base, (ud, fd, C["member2"], 1.6, "3 3"), (u0, fa, C["load"], 3.0, None)],
                     [(k0, C["muted"], "K_{0}", 12), (ka, C["load"], "K_{eff}", -10)],
                     [(f"K_{{eff}} 增為 {ka/k0:.2f} 倍 → T_{{eff}} 縮為 {Ta:.2f} 倍", C["load"], False),
                      (f"ξ_{{eff}}：{b0*100:.0f}% → {ba*100:.0f}%", C["load"], False),
                      ("與原設計週期、地震力牴觸", C["load"], False)])
    pb = _loop_panel("(b) 加黏彈性元件", "儲存勁度 k′ 同樣抬高勁度",
                     [base, (uv, fv, C["member2"], 1.6, "3 3"), (u0, fb, C["load"], 3.0, None)],
                     [(k0, C["muted"], "K_{0}", 12), (kb, C["load"], "K_{eff}", -10)],
                     [(f"K_{{eff}} 增為 {kb/k0:.2f} 倍 → T_{{eff}} 縮為 {Tb:.2f} 倍", C["load"], False),
                      (f"ξ_{{eff}}：{b0*100:.0f}% → {bb*100:.0f}%", C["load"], False),
                      ("k′、k″ 又隨頻率與溫度變動", C["load"], False)])
    pc = _loop_panel("(c) 液態黏滯阻尼器 FVD 單獨", "u = ±D 時 F = 0 → 不提供勁度",
                     [(u0, c_curves[0][1], C["sfd"], 3.0, None), c_curves[1]],
                     [],
                     [(f"F(u = D) = {abs(f_at_D):.2f} → k_{{FVD}} = 0，應變能權重 = 0", C["sfd"], False),
                      ("但迴圈面積 W_{D} 大於 0：消能真實存在", C["sfd"], False),
                      (f"須改用 ξ = W_{{D}}/(4π E_{{S}})，本例 +{xi_fvd*100:.0f}%", C["sfd"], False)])
    pc.legend(30, 78, [(C["sfd"], "α = 1（橢圓）")], 12)
    pc.parts.append(f'<line x1="30" y1="98" x2="52" y2="98" stroke="{C["sfd"]}" '
                    f'stroke-width="2" stroke-dasharray="6 4"/>')
    pc.text_px(60, 98, "α = 0.3（虛線，近矩形）", 12, C["muted"], "start")
    path = f"{OUT}/{TAG}-fig-2-loops.svg"
    compose([pa, pb, pc],
            title="圖 2　補充消能元件的遲滯迴圈：誰改了勁度、誰只加了消能",
            sub="灰虛線＝原隔震支承（雙線性）；紅實線＝支承＋元件合成；K_eff、ξ_eff 依規範割線定義由迴圈數值積分算出（示範參數）",
            note="判讀：迴圈「轉陡」＝改週期，即第 1 小題的牴觸；迴圈「變胖但不轉」＝只加阻尼，即第 2 小題的 FVD。",
            path=path)
    return path


# ══════════════════════════════════════════════════════════
# 圖 3　反應譜週期移位
# ══════════════════════════════════════════════════════════
def fig3_spectrum():
    W, H = 900, 540
    cv = Canvas(W, H, bg="#FFFFFF")
    L, R, B, T = 90, 260, 80, 60
    tmax, smax = 4.5, 0.7
    X = lambda t: L + t / tmax * (W - L - R)
    Y = lambda s: B + s / smax * (H - B - T)
    cv.text_px(W / 2, 30, "圖 3　隔震的效益來自週期移位：低矮建築移得遠，高聳建築幾乎移不動",
               17, C["text"], weight="700")
    # 軸
    cv.line((X(0), Y(0)), (X(tmax), Y(0)), C["member"], 1.6)
    cv.line((X(0), Y(0)), (X(0), Y(smax)), C["member"], 1.6)
    for t in range(0, 5):
        cv.line((X(t), Y(0)), (X(t), Y(0) - 6), C["member"], 1.4)
        cv.text_px(cv.X(X(t)), cv.Y(Y(0)) + 18, str(t), 12.5, C["muted"])
    for s in (0.2, 0.4, 0.6):
        cv.line((X(0), Y(s)), (X(0) - 6, Y(s)), C["member"], 1.4)
        cv.text_px(cv.X(X(0)) - 10, cv.Y(Y(s)), f"{s:.1f}", 12.5, C["muted"], "end")
        cv.line((X(0), Y(s)), (X(tmax), Y(s)), C["border"], 1)
    cv.math_px(cv.X(X(tmax / 2)), cv.Y(Y(0)) + 36, "T (s)", 14, C["muted"])
    cv.math_px(cv.X(X(0)) - 52, cv.Y(Y(smax)) - 2, "S_{aD}", 15, C["muted"])
    ts = np.linspace(0.2, tmax, 300)
    cv.poly([(X(t), Y(sa(t))) for t in ts], C["member"], 3)
    cv.poly([(X(t), Y(sa(t, B1_20))) for t in ts if t > T0D], C["member2"], 2.4, dash="7 5")
    cv.text_px(cv.X(X(4.45)), cv.Y(Y(sa(4.4))) - 14, "ξ = 5%", 12.5, C["member"], "end", weight="700")
    cv.text_px(cv.X(X(4.45)), cv.Y(Y(sa(4.4, B1_20))) + 16, "ξ = 20%（÷B_{1}）", 12.5, C["member2"], "end")

    def shift(t0, t1, col, name, dy):
        s0, s1 = sa(t0), sa(t1, B1_20)
        cv.dot((X(t0), Y(s0)), 6.5, fill=col)
        cv.dot((X(t1), Y(s1)), 6.5, fill="#FFFFFF", stroke=col, w=3)
        cv.arrow((X(t0) + 8, Y(s0) + dy), (X(t1) - 8, Y(s1) + dy), col, 2.6, 11)
        return s0, s1

    s0, s1 = shift(T_LOW_FIX, T_LOW_ISO, C["deform"], "低矮", 14)
    t0, t1 = shift(T_TALL_FIX, T_TALL_ISO, C["load"], "高聳", 16)
    # 右側說明欄
    x = W - R + 20
    cv.rect_px(x, 92, 236, 150, "#EEF4FF", 12, "#C7D9F5", 1.2)
    cv.text_px(x + 14, 116, "一般中低層建築", 14, C["deform"], "start", weight="700")
    cv.math_px(x + 14, 144, f"T: {T_LOW_FIX} → {T_LOW_ISO} s", 13.5, C["deform"], "start")
    cv.math_px(x + 14, 170, f"S_{{aD}}: {s0:.2f} → {s1:.2f}", 13.5, C["deform"], "start")
    cv.text_px(x + 14, 200, f"地震力剩 {s1/s0*100:.0f}%", 15, C["deform"], "start", weight="700")
    cv.text_px(x + 14, 224, "（主要靠週期移位）", 12.5, C["muted"], "start")
    cv.rect_px(x, 262, 236, 150, "#FFF6F1", 12, "#F0C9B8", 1.2)
    cv.text_px(x + 14, 286, "高聳細長建築", 14, C["load"], "start", weight="700")
    cv.math_px(x + 14, 314, f"T: {T_TALL_FIX} → {T_TALL_ISO} s", 13.5, C["load"], "start")
    cv.math_px(x + 14, 340, f"S_{{aD}}: {t0:.2f} → {t1:.2f}", 13.5, C["load"], "start")
    cv.text_px(x + 14, 370, f"地震力剩 {t1/t0*100:.0f}%", 15, C["load"], "start", weight="700")
    cv.text_px(x + 14, 394, "（只剩阻尼的 1/B_{1} 折減）", 12.5, C["muted"], "start")
    cv.dot((X(0.2) + 4, Y(0.12)), 6, fill=C["muted"])
    cv.text_px(cv.X(X(0.2)) + 16, cv.Y(Y(0.12)), "隔震前", 12.5, C["muted"], "start")
    cv.dot((X(0.2) + 4, Y(0.07)), 6, fill="#FFFFFF", stroke=C["muted"], w=2.6)
    cv.text_px(cv.X(X(0.2)) + 16, cv.Y(Y(0.07)), "隔震後（ξ = 20%）", 12.5, C["muted"], "start")
    cv.text_px(W / 2, H - 22,
               "反應譜取同卷第一題（S_{aD} = 0.6／0.6/T），T 超過 2.5 s 依規範取 0.4S_{DS}；週期為示範值，落在解析（四）所述範圍",
               12.5, C["muted"])
    path = f"{OUT}/{TAG}-fig-3-spectrum.svg"
    cv.save(path)
    return path


# ══════════════════════════════════════════════════════════
# 圖 4　傾覆與支承拉力
# ══════════════════════════════════════════════════════════
def fig4_overturn():
    PW, PH = 470, 500
    # (a) 自由體圖
    a = Canvas(PW, PH)
    a.panel("(a) 隔震層以上自由體", "規範豎向分配 F_x ∝ w_x h_x，均勻質量")
    bx0, bw, by0, bh = 150, 110, 170, 250
    a.polygon([(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh)],
              "#E9EDF3", C["member"], 2.4)
    nfl = 8
    for i in range(1, nfl):
        a.line((bx0, by0 + bh * i / nfl), (bx0 + bw, by0 + bh * i / nfl), C["member2"], 1)
    for i in range(1, nfl + 1):                      # 倒三角形慣性力
        hy = by0 + bh * i / nfl
        ln = 70 * i / nfl
        a.arrow((bx0 - 12 - ln, hy), (bx0 - 12, hy), C["load"], 1.8, 7)
    hbar = by0 + HBAR_OVER_H * bh
    a.line((bx0 - 10, hbar), (bx0 + bw + 70, hbar), C["accent"], 1.4, dash="5 4")
    a.text_px(a.X(bx0 + bw + 8), a.Y(hbar) - 14, "合力 V 作用高度", 12.5, C["accent"], "start", weight="700")
    a.math_px(a.X(bx0 + bw + 8), a.Y(hbar) + 12, "h_{V} = 2H/3", 13.5, C["accent"], "start", weight="700")
    a.arrow((bx0 + bw / 2, by0 + bh / 2), (bx0 + bw / 2, by0 + bh / 2 - 60), C["member"], 3, 11)
    a.math((bx0 + bw / 2, by0 + bh / 2 - 60), "W", 15, C["member"], dx=14, dy=4, weight="700")
    # 支承與反力
    for x, lab, col, up in ((bx0 + 8, "T（拉）", C["tension"], False), (bx0 + bw - 8, "C（壓）", C["compr"], True)):
        a.rect_px(a.X(x) - 9, a.Y(by0) , 18, 14, "#D6DBE3", 2, C["member"], 1.2)
        if up:
            a.arrow((x, by0 - 62), (x, by0 - 18), col, 3, 11)
        else:
            a.arrow((x, by0 - 18), (x, by0 - 62), col, 3, 11)
        a.text_px(a.X(x), a.Y(by0 - 76), lab, 13, col, weight="700")
    a.arrow((bx0 - 6, by0 - 8), (bx0 - 62, by0 - 8), C["member"], 2.6, 10)
    a.math((bx0 - 62, by0 - 8), "V", 14, C["member"], "end", dx=-6, weight="700")
    a.dim((bx0, by0 - 100), (bx0 + bw, by0 - 100), "B", off=0, label_off=14)
    a.dim((bx0 + bw + 40, by0), (bx0 + bw + 40, by0 + bh), "H", off=70, label_off=14)
    a.text_px(PW / 2, PH - 30, "支承出現拉力條件：V·h_{V} &gt; W·B/2", 14.5, C["text"], weight="700")

    # (b) 比值曲線
    b = Canvas(PW, PH)
    b.panel("(b) 傾覆比 V·h_{V} / (W·B/2) = C_{s}·(4/3)·H/B", "大於 1 → 受拉側支承淨拉力")
    L, R, Bm, T = 70, 30, 110, 90
    hmin, hmax = HB_RANGE; rmax = 1.8
    X = lambda r: L + (r - hmin) / (hmax - hmin) * (PW - L - R)
    Y = lambda v: Bm + v / rmax * (PH - Bm - T)
    b.polygon([(X(hmin), Y(1)), (X(hmax), Y(1)), (X(hmax), Y(rmax)), (X(hmin), Y(rmax))],
              C["fill_t"], "none")
    b.line((X(hmin), Y(0)), (X(hmax), Y(0)), C["member"], 1.4)
    b.line((X(hmin), Y(0)), (X(hmin), Y(rmax)), C["member"], 1.4)
    b.line((X(hmin), Y(1)), (X(hmax), Y(1)), C["load"], 1.8, dash="6 4")
    b.text_px(b.X(X(hmin)) + 8, b.Y(Y(rmax)) + 14, "支承受拉區", 12.5, C["load"], "start", weight="700")
    for h in range(int(hmin), int(hmax) + 1):
        b.text_px(b.X(X(h)), b.Y(Y(0)) + 16, str(h), 12, C["muted"])
    for v in (0.5, 1.0, 1.5):
        b.text_px(b.X(X(hmin)) - 8, b.Y(Y(v)), f"{v:.1f}", 12, C["muted"], "end")
    b.math_px(b.X(X((hmin + hmax) / 2)), b.Y(Y(0)) + 40, "H/B", 14, C["muted"])
    cols = (C["deform"], C["bmd"], C["sfd"])
    for cs, col in zip(CS_LIST, cols):
        k = cs * 2 * HBAR_OVER_H         # 比值 = C_s·2h̄/B = C_s·(4/3)·(H/B)
        pts = [(X(r), Y(min(k * r, rmax))) for r in np.linspace(hmin, hmax, 60) if k * r <= rmax]
        b.poly(pts, col, 2.8)
        r1 = 1 / k
        if hmin <= r1 <= hmax:
            b.dot((X(r1), Y(1)), 5, fill="#FFFFFF", stroke=col, w=2.4)
            b.math_px(b.X(X(r1)) + 4, b.Y(Y(1)) + 18, f"{r1:.1f}", 12, col, "start", weight="700")
        lx, ly = pts[-1]
        b.math_px(b.X(lx) - 4, b.Y(ly) - 12, f"C_{{s}} = {cs:.2f}", 12.5, col, "end", weight="700")
    r_lo, r_hi = 1 / (max(CS_LIST) * 2 * HBAR_OVER_H), 1 / (min(CS_LIST) * 2 * HBAR_OVER_H)
    b.text_px(PW / 2, PH - 44, f"比值不必「遠大於 1」；H/B 約 {r_lo:.1f}–{r_hi:.1f} 即越線", 13, C["text"], weight="700")
    b.text_px(PW / 2, PH - 22, "（○ 為各 C_s 開始出現拉力的 H/B）", 12, C["muted"])
    path = f"{OUT}/{TAG}-fig-4-overturn.svg"
    compose([a, b], title="圖 4　高聳細長建築的傾覆：地震力合力作用在 2H/3 高度，不在 H",
            sub="剛體上部結構對受壓側支承取矩；W 為隔震層以上重量，Cs 為隔震後上部結構設計係數（示範區間）",
            note="橡膠支承抗拉能力遠低於抗壓；一旦淨拉力出現，支承即有拉裂或拔離的風險。",
            path=path)
    return path


if __name__ == "__main__":
    for f in (fig1_story, fig2_loops, fig3_spectrum, fig4_overturn):
        print(f())
