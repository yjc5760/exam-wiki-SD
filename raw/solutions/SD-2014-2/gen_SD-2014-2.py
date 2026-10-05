#!/usr/bin/env python3
"""
SD-2014-2 LRB 隔震系統設計位移（等效線性化迭代）— 解題圖解產生腳本

用法：
    python3 gen_SD-2014-2.py [輸出目錄]

本題為純符號題（W、n、k_o、F_y、α 皆未給數值），圖中幾何一律由
SD-2014-2.md §4 的公式算出；為了能畫出形狀，取一組「示意參數」
（ALPHA、MU、BS、B1），改任一參數重跑，圖形會跟著變。

圖 1  雙線性遲滯迴圈：攔「K_eD 誤用初始勁度 k_o」與「A_TD 誤寫成 F_y·D_D 或 4F_y·D_D」
圖 2  阻尼修正後之設計反應譜：攔「B 不分區段一律取 B_1」與「S_aD 誤套 0.4S_DS 下限」
"""
import sys, os

SKILL = os.environ.get("STRUCT_DIAGRAM_SCRIPTS",
    "/root/.claude/skills/synced/6983ec08-a01a-44e4-a131-56c9e592c524_ab4f317b-1625-4c71-b32d-871e33fbc9cc/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SD-2014-2"

# ══════════════════════════════════════════════════════════
# 示意參數（題目為符號題；以下僅決定圖形比例）
# ══════════════════════════════════════════════════════════
ALPHA = 0.10        # 降伏後勁度比 α
MU    = 6.0         # D_D / D_y（設計位移遠大於降伏位移）
# 阻尼修正係數：取 ξ_eD = 20% 之規範表值（見 §4 Step 6 表；2012 年考卷圖二(b) 亦印此值）
BS, B1 = 1.60, 1.50

# ══════════════════════════════════════════════════════════
# 由 §4 公式算出的量（以 D_y、F_y 正規化：D_y = 1, F_y = 1, k_o = 1）
# ══════════════════════════════════════════════════════════
DY   = 1.0
FY   = 1.0
KO   = FY / DY
QD   = FY * (1 - ALPHA)                    # §4 Step 4：Q_d = F_y(1−α)
FMAX = QD + ALPHA * KO * MU                # F(D_D) = Q_d + α k_o D_D
KEFF = FMAX / MU                           # §4 Step 2：割線勁度
ATD  = 4 * QD * (MU - DY)                  # §4 Step 4：單支迴圈面積
XI   = ATD / (2 * 3.141592653589793 * KEFF * MU**2)   # §4 Step 5


def fig1_loop(path):
    YS = 3.2                                # 力軸放大（等向畫布下讓迴圈不扁）
    W, H = 900, 560
    Lm, Rm, Tm, Bm = 80, 250, 30, 60
    xr = (-MU * 1.12, MU * 1.12)
    yr = (-FMAX * YS * 1.12, FMAX * YS * 1.12)
    sx = min((W - Lm - Rm) / (xr[1] - xr[0]), (H - Tm - Bm) / (yr[1] - yr[0]))
    cv = Canvas(W, H, sx=sx, ox=Lm - xr[0] * sx, oy=Bm - yr[0] * sx)
    P = lambda u, f: (u, f * YS)

    # 迴圈頂點：(D,Fmax) →彈性卸載 2F_y→ (D−2D_y, Fmax−2F_y) →降伏後→ (−D,−Fmax) → …
    loop = [P(MU, FMAX), P(MU - 2 * DY, FMAX - 2 * FY), P(-MU, -FMAX),
            P(-MU + 2 * DY, -FMAX + 2 * FY), P(MU, FMAX)]
    cv.polygon(loop[:-1], C["fill_m"])
    # 座標軸
    cv.arrow(P(xr[0], 0), P(xr[1], 0), C["muted"], w=1.6, head=8)
    cv.arrow(P(0, -FMAX * 1.1), P(0, FMAX * 1.12), C["muted"], w=1.6, head=8)
    cv.text(P(xr[1], 0), "u", 15, C["muted"], dx=-6, dy=18, italic=True)
    cv.text(P(0, FMAX * 1.12), "F", 15, C["muted"], dx=14, italic=True)
    # 初始加載 0 → D_y → D_D（骨幹曲線）
    cv.poly([P(0, 0), P(DY, FY), P(MU, FMAX)], C["member2"], 2.2, dash="6 5")
    # 迴圈本體
    cv.poly(loop, C["bmd"], 3.2)
    # 割線勁度
    cv.line(P(-MU, -FMAX), P(MU, FMAX), C["deform"], 2.6)
    # k_o 初始勁度（延伸示意，說明它遠比割線陡）
    cv.line(P(0, 0), P(DY * 1.55, FY * 1.55), C["load"], 2.4, dash="7 5")
    # 標記點
    for p in [(MU, FMAX), (DY, FY), (-MU, -FMAX)]:
        cv.dot(P(*p), 5, C["text"])
    cv.dot(P(0, QD), 5, C["accent"])
    cv.dot(P(0, -QD), 5, C["accent"])

    # 標註
    cv.math(P(0, QD), "Q_{d}", 15, C["accent"], anchor="end", dx=-10, dy=-10, weight="700")
    cv.math(P(0, -QD), "−Q_{d}", 15, C["accent"], anchor="end", dx=-10, dy=14, weight="700")
    cv.math(P(DY, FY), "(D_{y}, F_{y})", 14, C["text"], anchor="start", dx=10, dy=12)
    cv.math(P(MU, FMAX), "(D_{D}, F_{max})", 14, C["text"], anchor="end", dx=-6, dy=-20)
    cv.math(P(DY * 1.55, FY * 1.55), "k_{o}", 16, C["load"], anchor="start", dx=4, dy=-10, weight="700")
    cv.math(P(MU * 0.62, FMAX * 0.62), "K_{eD}/n", 16, C["deform"], anchor="start", dx=12, dy=14, weight="700")
    cv.math(P(-2.5, QD - 2.5 * ALPHA * KO), "αk_{o}", 15, C["bmd"], dy=-18, weight="700")
    cv.math(P(MU - DY, FMAX - FY), "k_{o}（卸載）", 14, C["bmd"], anchor="start", dx=10)
    # 迴圈寬、高尺寸
    cv.dim(P(-MU + 2 * DY, -FMAX - 0.22), P(MU, -FMAX - 0.22), "", off=0)
    cv.math(P(DY, -FMAX - 0.22), "2(D_{D} − D_{y})", 14, C["muted"], dy=18)
    cv.text(P(MU * 0.33, -QD * 0.28), "迴圈面積", 15, C["bmd"], weight="700")
    cv.math(P(MU * 0.33, -QD * 0.28), "A = 4Q_{d}(D_{D}−D_{y})", 15, C["bmd"], dy=24, weight="700")

    # 右側說明欄
    x0 = W - Rm + 22
    cv.text_px(x0, 70, "示意參數", 14, C["text"], "start", weight="700")
    cv.math_px(x0, 98, f"α = {ALPHA:g}", 14, C["muted"], "start")
    cv.math_px(x0, 122, f"D_{{D}}/D_{{y}} = {MU:g}", 14, C["muted"], "start")
    cv.text_px(x0, 162, "由公式算得", 14, C["text"], "start", weight="700")
    cv.math_px(x0, 190, f"K_{{eD}}/(n k_{{o}}) = {KEFF:.3f}", 14, C["deform"], "start")
    cv.math_px(x0, 214, f"ξ_{{eD}} = {XI:.3f}", 14, C["bmd"], "start")
    cv.legend(x0, 260, [(C["load"], "初始勁度（不可用）"),
                        (C["deform"], "割線勁度＝等效勁度"),
                        (C["bmd"], "遲滯迴圈（消能）"),
                        (C["member2"], "初始加載骨幹")], size=12.5, gap=24)
    return compose([cv], title="圖 1　單支 LRB 雙線性遲滯迴圈與等效線性化參數",
                   note="等效勁度＝原點到迴圈頂點的割線斜率；消能面積＝平行四邊形（上下分支垂直間距 2Qd × 水平投影 2(DD − Dy)）",
                   path=path)


def fig2_spectrum(path):
    # 正規化：S_DS = 1，T_0^D = S_D1/S_DS = 1（5% 阻尼轉角週期）
    SDS, T0 = 1.0, 1.0
    SD1 = SDS * T0
    T0D = SD1 * BS / (SDS * B1)              # 阻尼修正後之轉角週期
    TMAX = 4.0
    YS = 2.4

    def sa5(T):                              # 5% 阻尼（隔震規範：長週期無 0.4S_DS 下限）
        if T <= 0.2 * T0: return SDS * (0.4 + 3 * T / T0)
        if T <= T0: return SDS
        return SD1 / T

    def sad(T):                              # 阻尼修正後
        if T <= 0.2 * T0D: return SDS * (0.4 + (1 / BS - 0.4) * 5 * T / T0D)
        if T <= T0D: return SDS / BS
        return SD1 / (B1 * T)

    W, H = 900, 520
    Lm, Rm, Tm, Bm = 80, 40, 30, 70
    sx = min((W - Lm - Rm) / (TMAX * 1.05), (H - Tm - Bm) / (SDS * YS * 1.12))
    cv = Canvas(W, H, sx=sx, ox=Lm, oy=Bm)
    P = lambda t, s: (t, s * YS)
    N = 400
    ts = [TMAX * i / N for i in range(N + 1)]

    # B_S 區與 B_1 區底色
    cv.polygon([P(0, 0), P(T0D, 0), P(T0D, 1.08), P(0, 1.08)], C["fill_s"])
    cv.polygon([P(T0D, 0), P(TMAX, 0), P(TMAX, 1.08), P(T0D, 1.08)], C["fill_c"])
    # 0.4 S_DS 一般建築下限（隔震不適用）
    cv.line(P(T0 / 0.4, 0.4 * SDS), P(TMAX, 0.4 * SDS), C["load"], 2.0, dash="6 5")
    cv.math(P(TMAX, 0.4 * SDS), "0.4S_{DS}", 13.5, C["load"], anchor="end", dy=-12)
    cv.text(P(TMAX, 0.4 * SDS), "一般建築下限（隔震不適用）", 12.5, C["load"], anchor="end", dy=14)
    # 曲線
    cv.poly([P(t, sa5(t)) for t in ts], C["member2"], 2.6)
    cv.poly([P(t, sad(t)) for t in ts], C["deform"], 3.2)
    # 軸
    cv.arrow(P(0, 0), P(TMAX * 1.03, 0), C["muted"], w=1.6, head=8)
    cv.arrow(P(0, 0), P(0, 1.1), C["muted"], w=1.6, head=8)
    cv.text(P(TMAX * 1.03, 0), "T", 15, C["muted"], dx=-4, dy=20, italic=True)
    # 轉角週期刻度
    for t, lab, col in [(T0, "T_{0}^{D}", C["member2"]), (T0D, "T_{0}^{D'}", C["deform"])]:
        cv.line(P(t, 0), P(t, sa5(t) if t == T0 else sad(t)), col, 1.4, dash="3 4")
    cv.math(P(T0, 0), "T_{0}", 14, C["member2"], anchor="end", dx=-2, dy=18)
    cv.math(P(T0D, 0), "T_{0D}", 14, C["deform"], anchor="start", dx=4, dy=18)
    cv.math(P(0, SDS), "S_{DS}", 14, C["muted"], anchor="end", dx=-8)
    cv.math(P(0, SDS / BS), "S_{DS}/B_{S}", 14, C["deform"], anchor="end", dx=-8)
    # 曲線標註
    cv.math(P(2.0, sa5(2.0)), "S_{D1}/T", 14, C["member2"], anchor="start", dx=8, dy=-14)
    cv.text(P(2.0, sa5(2.0)), "（5% 阻尼）", 12.5, C["member2"], anchor="start", dx=70, dy=-14)
    cv.math(P(2.6, sad(2.6)), "S_{D1}/(B_{1}T)", 14, C["deform"], anchor="start", dx=8, dy=24, weight="700")
    # 區段文字
    cv.text(P((0.2 * T0D + T0D) / 2, 1.08), "B = B_{S} 區", 13.5, C["sfd"], dy=-14, weight="700")
    cv.text(P((T0D + TMAX) / 2, 1.08), "B = B_{1} 區（隔震 T_{eD} 通常落在此）", 13.5, C["deform"], dy=-14, weight="700")
    # T_eD 示意
    TE = 2.2 * T0
    cv.line(P(TE, 0), P(TE, sa5(TE)), C["accent"], 2.0)
    cv.dot(P(TE, sad(TE)), 5.5, C["accent"])
    cv.dot(P(TE, sa5(TE)), 5.5, "#FFFFFF", C["accent"], 2.2)
    cv.math(P(TE, 0), "T_{eD}", 14, C["accent"], dy=18, weight="700")
    cv.legend(W - 300, 420, [(C["member2"], "5% 阻尼反應譜 S_{aD}"),
                             (C["deform"], "阻尼修正後 S_{aD}/B")], size=12.5, gap=22)
    return compose([cv], title="圖 2　阻尼修正係數 B 的取用區段（示意：等效阻尼比 20%）",
                   note="阻尼修正後轉角週期 T0D = T0 × BS / B1；等效週期 TeD 大於 T0D 才取 B1，否則取 BS",
                   path=path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1_loop(os.path.join(OUT, f"{TAG}-fig-1-hysteresis.svg"))
    fig2_spectrum(os.path.join(OUT, f"{TAG}-fig-2-spectrum.svg"))
    print(f"K_eff/k_o = {KEFF:.4f}, xi_eD = {XI:.4f}, T0D/T0 = {BS/B1:.4f}")
