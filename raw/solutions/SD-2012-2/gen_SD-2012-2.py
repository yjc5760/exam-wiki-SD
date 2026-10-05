#!/usr/bin/env python3
"""
SD-2012-2 SDOF + 對角斜撐黏滯阻尼器 — 解題圖解產生腳本

用法：
    python3 gen_SD-2012-2.py [輸出目錄]
    （structdraw 位置可用環境變數 STRUCTDRAW 指定 struct-diagram/scripts 路徑）

所有數值由題目給定參數重新計算（與 SD-2012-2.md 步驟一～五逐一對應），
改任何一個參數重跑，四張圖都會跟著變。
"""
import sys, os, math, glob

_cands = [os.environ.get("STRUCTDRAW", "")] + \
    glob.glob("/root/.claude/skills/synced/*/struct-diagram/scripts") + \
    [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools", "struct-diagram", "scripts")]
for _p in _cands:
    if _p and os.path.isfile(os.path.join(_p, "structdraw.py")):
        sys.path.insert(0, _p); break

from structdraw import Canvas, C, FONT_M, compose, column_shape
from recipes import bar_compare

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
TAG = "SD-2012-2"

# ══════════════════════════════════════════════════════════
# 題目給定（SD-2012-2.md「題目敘述」）
# ══════════════════════════════════════════════════════════
K, M, CD, BETA0, G = 8e4, 2000.0, 4e3, 0.05, 9.81
TH = math.radians(30)
B_TABLE = [(5, 1.00, 1.00), (10, 1.33, 1.25), (20, 1.60, 1.50)]   # (β%, Bs, B1)，圖二(b)
SDS, SD1, T_C = 0.20, 0.12, 0.60                                   # 第一題反應譜


def interp(beta_pct, col):
    """圖二(b) 線性內插；col=1 → Bs，col=2 → B1"""
    for a, b in zip(B_TABLE, B_TABLE[1:]):
        if a[0] <= beta_pct <= b[0]:
            return a[col] + (beta_pct - a[0]) / (b[0] - a[0]) * (b[col] - a[col])
    raise ValueError("β 超出表格範圍")


# ── 步驟一 ──
T = 2 * math.pi * math.sqrt(M / K)                     # 0.993 s
OMEGA = 2 * math.pi / T
# ── 步驟二 ──
C_H = CD * math.cos(TH) ** 2                            # 等效水平阻尼係數 3000
D_BETA = math.pi * CD * math.cos(TH) ** 2 / (T * K)     # 0.1186
BETA = BETA0 + D_BETA                                   # 0.1686
# ── 步驟三 ──
B1 = interp(BETA * 100, 2)                              # 1.421
BS = interp(BETA * 100, 1)                              # 1.515（僅供「誤用 Bs」對照）
# ── 步驟四、五 ──
SA5 = SD1 / T                                           # 0.1208
SA_EFF = SA5 / B1                                       # 0.0850
D_MAX = SA_EFF * M * G / K                              # 0.02084 m
D_0 = SA5 * M * G / K                                   # 無阻尼器 0.02962 m
D_BS = SA5 / BS * M * G / K                             # 誤用 Bs


def f2(x): return f"{x:.2f}"


# ══════════════════════════════════════════════════════════
def fig1_geometry():
    """題目重繪＋斜撐運動學：cos²θ 的兩個 cos 各從哪裡來"""
    HH = math.tan(TH)               # 跨度取 1，斜撐 30° → 樓高 tan30°
    PW, PH = 480, 500

    # (a) 題目重繪
    a = Canvas(PW, PH, sx=270, ox=105, oy=215)
    a.panel("(a) 題目重繪：圖二(a)", "單層剪力屋架＋對角斜撐黏滯阻尼器")
    for s, e in (((0, 0), (0, HH)), ((1, HH), (1, 0))):
        a.line(s, e, C["member"], 4.5, cap="butt")
    a.line((-0.04, HH), (1.04, HH), C["member"], 11, cap="butt")
    a.line((0, 0), (1, HH), C["member2"], 2.2)
    # 阻尼器方塊（沿斜撐方向）
    ux, uy = math.cos(TH), math.sin(TH); nx, ny = -uy, ux
    cx, cy = 0.5, HH / 2; hl, hw = 0.11, 0.032
    a.polygon([(cx - hl*ux - hw*nx, cy - hl*uy - hw*ny), (cx + hl*ux - hw*nx, cy + hl*uy - hw*ny),
               (cx + hl*ux + hw*nx, cy + hl*uy + hw*ny), (cx - hl*ux + hw*nx, cy - hl*uy + hw*ny)],
              C["member"])
    a.fixed_support((0, 0), size=17); a.fixed_support((1, 0), size=17)
    a.math((0.5, HH), f"m = {M:.0f} kg", 15, C["text"], dy=-24)
    a.math((0, HH/2), "k", 17, C["text"], "end", dx=-14)
    a.text_px(a.X(cx) + 14, a.Y(cy) + 40, "線性黏滯消能元件", 12.5, C["muted"], "start")
    a.math_px(a.X(cx) + 14, a.Y(cy) + 62, f"c = {CD:.0f} N·s/m", 13, C["muted"], "start")
    a.parts.append(f'<path d="M {a.X(0.22):.1f} {a.Y(0):.1f} A {0.22*a.sx:.1f} {0.22*a.sx:.1f} 0 0 0 '
                   f'{a.X(0.22*math.cos(TH)):.1f} {a.Y(0.22*math.sin(TH)):.1f}" fill="none" '
                   f'stroke="{C["accent"]}" stroke-width="2"/>')
    a.math((0.27, 0.05), "θ = 30°", 14, C["accent"], "start", weight="700")
    a.text_px(PW/2, 410, f"k = 8×10^4 N/m　β = 5%　T = {T:.3f} s", 13, C["muted"])

    # (b) 運動學
    D = 0.26                         # 繪圖放大之側移（純視覺）
    b = Canvas(PW, PH, sx=270, ox=78, oy=185)
    b.panel("(b) 樓層側移 δ 時，阻尼器伸長多少？", "斜撐軸向剛性 → 端點相對位移全由阻尼器吸收")
    for s, e in (((0, 0), (0, HH)), ((1, HH), (1, 0)), ((0, HH), (1, HH)), ((0, 0), (1, HH))):
        b.line(s, e, C["ghost"], 2.6, dash="6 5")
    b.poly(column_shape((0, 0), HH, D, 0.0), C["deform"], 4.2)
    b.poly(column_shape((1, 0), HH, D, 0.0), C["deform"], 4.2)
    b.line((D - 0.04, HH), (1 + D + 0.04, HH), C["deform"], 6, cap="butt")
    b.line((0, 0), (1 + D, HH), C["member2"], 2.0)
    b.fixed_support((0, 0), size=16); b.fixed_support((1, 0), size=16)
    P0 = (1, HH); P1 = (1 + D, HH)
    foot = (1 + D*math.cos(TH)*ux, HH + D*math.cos(TH)*uy)    # δ 在斜撐方向的投影
    b.dim(P0, P1, "δ", off=-58, color=C["deform"], size=17, label_off=-14)
    b.dot(P0, 4, fill=C["muted"]); b.dot(P1, 4.5, fill=C["deform"])
    b.arrow(P0, foot, C["load"], 3.0, 11)
    b.line(foot, P1, C["muted"], 1.4, dash="4 3")
    b.math_px(b.X(P0[0]) - 150, b.Y(HH) - 24, "δ_{r} = δ cosθ", 14.5, C["load"], "start", weight="700")
    b.rect_px(26, 350, PW - 52, 96, "#FFFFFF", 10, C["border"], 1.2)
    b.text_px(44, 372, "① 運動學：δ_{r} = δ cosθ（阻尼器變形）", 13.5, C["text"], "start")
    b.text_px(44, 397, "② 力的投影：F_{h} = F_{d} cosθ（回到水平向）", 13.5, C["text"], "start")
    b.math_px(44, 424, f"⇒ c_{{h}} = c cos^{{2}}θ = {C_H:.0f} N·s/m", 14.5, C["load"], "start", weight="700")
    b.text_px(PW/2, PH - 28, "圖上側移已放大；實際 δ 遠小於樓高", 12, C["muted"])

    compose([a, b], title=f"圖 1　構架幾何與斜撐運動學（θ = {math.degrees(TH):.0f}°）",
            note="提示式中的 δrj 是阻尼器兩端沿軸向的相對位移，不是樓層側移 δ；兩者差一個 cosθ",
            path=f"{OUT}/{TAG}-fig-1-geometry.svg")


# ══════════════════════════════════════════════════════════
def fig2_energy():
    """一個循環：阻尼器消能橢圓（W_V）vs 彈簧最大應變能三角形（W_k）"""
    W_, H_ = 860, 520
    r = C_H * OMEGA / K               # 阻尼力峰值 / kδ（以 kδ 正規化）
    sx = 250
    cv = Canvas(W_, H_, sx=sx, ox=330, oy=150, bg="#FFFFFF")
    cv.text_px(W_/2, 32, "圖 2　穩態簡諧振動一個循環的能量：消能 W_V 與應變能 W_k", 17.5, C["text"], weight="700")
    cv.text_px(W_/2, 57, "橫軸：樓層位移 u/δ　縱軸：水平力 / kδ（比例為真，未放大）", 13, C["muted"])
    cv.arrow((-1.12, 0), (1.18, 0), C["muted"], 1.8, 9)
    cv.math((1.18, 0), "u/δ", 14, C["muted"], "start", dx=8)
    cv.arrow((0, -0.34), (0, 1.1), C["muted"], 1.8, 9)
    cv.math((0, 1.1), "F/(kδ)", 14, C["muted"], dy=-12)
    # 彈簧：F = k u，三角形面積 = W_k
    cv.polygon([(0, 0), (1, 0), (1, 1)], C["fill_c"], C["deform"], 1.2)
    cv.line((-0.32, -0.32), (1.05, 1.05), C["deform"], 2.6)
    cv.math((0.62, 0.30), "W_{k} = kδ^{2}/2", 15, C["deform"], weight="700")
    cv.text((1.05, 1.05), "彈簧 F = ku", 13, C["deform"], "start", dx=8, weight="700")
    # 阻尼器：F = c_h u̇ → 橢圓 (u/δ)^2 + (F/(c_h ω δ))^2 = 1
    pts = [(math.cos(t), r * math.sin(t)) for t in [i * 2 * math.pi / 120 for i in range(121)]]
    cv.polygon(pts, C["fill_t"], C["load"], 2.6)
    cv.dot((0, r), 4.5, fill=C["load"])
    cv.text_px(cv.X(-1.0), cv.Y(r) - 22, f"阻尼力峰值 c_{{h}}ωδ = {r:.3f} kδ", 13, C["load"], "start", weight="700")
    cv.math((-0.55, -0.02), "W_{V}", 15, C["load"], weight="700", dy=12)
    # 右側數值盒
    bx, by = 610, 150
    cv.rect_px(bx, by, 240, 168, "#FFFFFF", 12, C["border"], 1.2)
    cv.math_px(bx+16, by+26, "W_{V} = π c_{h} ω δ^{2}", 14, C["load"], "start")
    cv.math_px(bx+16, by+50, "    = (2π^{2}/T) c δ_{r}^{2}", 14, C["load"], "start")
    cv.math_px(bx+16, by+80, "W_{k} = k δ^{2}/2", 14, C["deform"], "start")
    cv.math_px(bx+16, by+112, f"Δβ = W_{{V}}/(4πW_{{k}}) = {D_BETA*100:.2f}%", 14, C["text"], "start", weight="700")
    cv.math_px(bx+16, by+140, f"β_{{eff}} = 5% + {D_BETA*100:.2f}% = {BETA*100:.2f}%", 14, C["text"], "start", weight="700")
    cv.text_px(W_/2, H_ - 26, f"若 W_k 漏掉 ½（寫成 kδ²），Δβ 會變成 {D_BETA*50:.2f}%，恰好少一半。δ² 在分子分母同時出現，故 Δβ 與振幅無關",
               13, C["muted"])
    cv.save(f"{OUT}/{TAG}-fig-2-energy.svg")


# ══════════════════════════════════════════════════════════
def fig3_spectrum():
    """設計譜折減＋B 值內插：判斷 T 落在哪一段、該用哪一個 B"""
    PW, PH = 520, 440

    # ── (a) 反應譜 ──
    a = Canvas(PW, PH, sx=1, bg=None)
    a.panel("(a) 加速度反應譜係數 S_a", f"5% 阻尼 vs β_{{eff}} = {BETA*100:.1f}%")
    x0p, y0p, wp, hp = 70, 370, 410, 270     # 繪圖區（像素）
    Tmax, Smax = 2.0, 0.24
    X = lambda t: x0p + t / Tmax * wp
    Y = lambda s: y0p - s / Smax * hp
    a.parts.append(f'<line x1="{x0p}" y1="{y0p}" x2="{x0p+wp+6}" y2="{y0p}" stroke="{C["muted"]}" stroke-width="1.6"/>')
    a.parts.append(f'<line x1="{x0p}" y1="{y0p}" x2="{x0p}" y2="{y0p-hp-6}" stroke="{C["muted"]}" stroke-width="1.6"/>')
    for t in (0.5, 1.0, 1.5, 2.0):
        a.text_px(X(t), y0p + 16, f"{t:.1f}", 11.5, C["muted"])
    for s in (0.05, 0.10, 0.15, 0.20):
        a.text_px(x0p - 8, Y(s), f"{s:.2f}", 11.5, C["muted"], "end")
        a.parts.append(f'<line x1="{x0p}" y1="{Y(s):.1f}" x2="{x0p+wp}" y2="{Y(s):.1f}" stroke="{C["border"]}" stroke-width="1"/>')
    a.math_px(x0p + wp - 4, y0p + 34, "T (s)", 13, C["muted"], "end")
    ts = [0.02 + i * (Tmax - 0.02) / 300 for i in range(301)]
    s5 = [min(SDS, SD1 / t) for t in ts]
    se = [min(SDS / BS, SD1 / (B1 * t)) for t in ts]
    path = lambda ss: " ".join(f"{'M' if i==0 else 'L'} {X(t):.1f} {Y(s):.1f}" for i, (t, s) in enumerate(zip(ts, ss)))
    a.parts.append(f'<path d="{path(s5)}" fill="none" stroke="{C["member2"]}" stroke-width="2.6"/>')
    a.parts.append(f'<path d="{path(se)}" fill="none" stroke="{C["load"]}" stroke-width="2.8"/>')
    # 長週期段底色
    a.parts.append(f'<rect x="{X(T_C):.1f}" y="{y0p-hp}" width="{X(Tmax)-X(T_C):.1f}" height="{hp}" fill="{C["fill_s"]}" opacity="0.35"/>')
    a.parts.append(f'<line x1="{X(T_C):.1f}" y1="{y0p}" x2="{X(T_C):.1f}" y2="{y0p-hp}" stroke="{C["sfd"]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    a.text_px(X(T_C) + 8, y0p - hp + 14, "長週期段 → 用 B_1", 12, C["sfd"], "start", weight="700")
    a.text_px(X(0.3), y0p - hp + 14, "短週期段 → B_S", 12, C["muted"])
    # 本題週期
    a.parts.append(f'<line x1="{X(T):.1f}" y1="{y0p}" x2="{X(T):.1f}" y2="{Y(SA5)-14:.1f}" stroke="{C["accent"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    a.dot((X(T), a.h - Y(SA5)), 5, fill=C["member2"])
    a.dot((X(T), a.h - Y(SA_EFF)), 5, fill=C["load"])
    a.math_px(X(T) + 10, Y(SA5) - 12, f"0.12/T = {SA5:.4f}", 12.5, C["member"], "start", weight="700")
    a.math_px(X(T) - 150, Y(SA_EFF) + 30, f"÷ B_{{1}} = {SA_EFF:.4f}", 12.5, C["load"], "start", weight="700")
    a.math_px(X(T), y0p + 34, f"T = {T:.3f}", 12.5, C["accent"], weight="700")
    a.legend(330, 142, [(C["member2"], "5% 阻尼設計譜"), (C["load"], "β_{eff} 折減譜")], 12, 20)

    # ── (b) B 值內插 ──
    b = Canvas(PW, PH, sx=1, bg=None)
    b.panel("(b) 圖二(b) 阻尼修正係數內插", f"β_{{eff}} = {BETA*100:.2f}% 介於 10% 與 20% 之間")
    bx0, by0, bw, bh = 80, 370, 390, 270
    bmax, Bmin, Bmax = 22.0, 0.9, 1.7
    BX = lambda be: bx0 + be / bmax * bw
    BY = lambda v: by0 - (v - Bmin) / (Bmax - Bmin) * bh
    b.parts.append(f'<line x1="{bx0}" y1="{by0}" x2="{bx0+bw+6}" y2="{by0}" stroke="{C["muted"]}" stroke-width="1.6"/>')
    b.parts.append(f'<line x1="{bx0}" y1="{by0}" x2="{bx0}" y2="{by0-bh-6}" stroke="{C["muted"]}" stroke-width="1.6"/>')
    for be in (5, 10, 15, 20):
        b.text_px(BX(be), by0 + 16, f"{be}", 11.5, C["muted"])
    for v in (1.0, 1.2, 1.4, 1.6):
        b.text_px(bx0 - 8, BY(v), f"{v:.1f}", 11.5, C["muted"], "end")
        b.parts.append(f'<line x1="{bx0}" y1="{BY(v):.1f}" x2="{bx0+bw}" y2="{BY(v):.1f}" stroke="{C["border"]}" stroke-width="1"/>')
    b.math_px(bx0 + bw - 4, by0 + 34, "β_{eff} (%)", 13, C["muted"], "end")
    for col, color, wdt in ((1, C["member2"], 2.2), (2, C["load"], 2.8)):
        pp = " ".join(f"{'M' if i==0 else 'L'} {BX(r[0]):.1f} {BY(r[col]):.1f}" for i, r in enumerate(B_TABLE))
        b.parts.append(f'<path d="{pp}" fill="none" stroke="{color}" stroke-width="{wdt}"/>')
        for r_ in B_TABLE:
            b.dot((BX(r_[0]), b.h - BY(r_[col])), 4, fill=color)
    bp = BETA * 100
    b.parts.append(f'<line x1="{BX(bp):.1f}" y1="{by0}" x2="{BX(bp):.1f}" y2="{BY(BS):.1f}" stroke="{C["accent"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    b.parts.append(f'<line x1="{bx0}" y1="{BY(B1):.1f}" x2="{BX(bp):.1f}" y2="{BY(B1):.1f}" stroke="{C["load"]}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    b.dot((BX(bp), b.h - BY(B1)), 5.5, fill="#FFFFFF", stroke=C["load"], w=2.6)
    b.dot((BX(bp), b.h - BY(BS)), 5.0, fill="#FFFFFF", stroke=C["member2"], w=2.4)
    b.math_px(BX(bp) + 10, BY(B1) + 16, f"B_{{1}} = {B1:.3f}", 13, C["load"], "start", weight="700")
    b.text_px(BX(bp) - 10, BY(BS) - 14, f"B_{{S}} = {BS:.3f}（本題不用）", 12, C["muted"], "end")
    b.math_px(BX(bp), by0 + 34, f"{bp:.2f}", 12.5, C["accent"], weight="700")
    b.legend(110, 118, [(C["member2"], "B_S"), (C["load"], "B_1")], 12, 20)

    compose([a, b], title="圖 3　等值線性靜力分析：用有效阻尼比折減設計譜",
            note=f"T = {T:.3f} s 大於 0.6 s，位於長週期段，只能除以 B1；若誤用 BS，位移會低估約 {(1-D_BS/D_MAX)*100:.0f}%",
            path=f"{OUT}/{TAG}-fig-3-spectrum.svg")


# ══════════════════════════════════════════════════════════
def fig4_compare():
    """答案量級：加阻尼器後位移應明顯小於無阻尼器，但不會小到離譜"""
    cases = [
        ("無阻尼器", "β = 5%，Sa = 0.12/T", D_0 * 100, f"δ = {D_0*100:.2f} cm", C["member2"]),
        ("有阻尼器（正解）", f"β_{{eff}} = {BETA*100:.1f}%，÷ B_1 = {B1:.3f}", D_MAX * 100, f"δ = {D_MAX*100:.2f} cm", C["load"]),
        ("誤用 B_S", f"÷ B_S = {BS:.3f}（短週期係數）", D_BS * 100, f"δ = {D_BS*100:.2f} cm", C["muted"]),
    ]
    bar_compare(cases, title="圖 4　樓層最大位移的量級比較",
                sub="長條長度以無阻尼器位移為 100%",
                note=f"加阻尼器位移減少 {(1-D_MAX/D_0)*100:.0f}%；誤用 B_S 只差 {(1-D_BS/D_MAX)*100:.0f}%，量級檢核攔不住，必須回到圖 3 判斷週期段",
                path=f"{OUT}/{TAG}-fig-4-compare.svg")


if __name__ == "__main__":
    print(f"T={T:.4f}  Δβ={D_BETA:.4f}  β_eff={BETA:.4f}  B1={B1:.4f}  BS={BS:.4f}")
    print(f"Sa5={SA5:.4f}  Sa_eff={SA_EFF:.5f}  F={SA_EFF*M*G:.1f} N  δ={D_MAX*100:.3f} cm  δ0={D_0*100:.3f} cm  δBs={D_BS*100:.3f} cm")
    fig1_geometry(); fig2_energy(); fig3_spectrum(); fig4_compare()
    print("done →", OUT)
