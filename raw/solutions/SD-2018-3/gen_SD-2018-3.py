#!/usr/bin/env python3
"""SD-2018-3 圖解產生器 — 規範豎向分配 vs 動力學豎向分配

振態、有效質量、側力分布與層間位移全部由 5 層剪力屋架的廣義特徵值問題
(K − ω²M)φ = 0 實際解出，非描摹。改任一 K/M 參數重跑，三張圖同時更新。

本檔的計算同時是解析 §4.4／§4.5 的依據：
  軟層（1F, k=0.4k）→ 第一振態有效質量反而升到 95.5%（假設 A 更成立），
                        但 φ1 偏離直線達 0.321（假設 B 嚴重失效）
  質量不規則（1F, m=3m）→ 第二振態有效質量由 8.7% 升到 16.3%（假設 A 失效），
                        φ1 偏離直線僅 0.177（假設 B 影響小）
兩種不規則各打破一個假設，這正是規範兩者都要求做動力分析的理由。
"""
import sys, os, math
import numpy as np
SKILL = os.environ.get("STRUCTDRAW",
    "/root/.claude/skills/synced/ac6f22be-8f8e-4e9a-b5a5-57a76b0ea389_ed8ec2e9-4a34-4076-aef8-82296cfdbb5c/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C, compose

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# ── 模型：5 層剪力屋架（無因次）────────────────────────────
N, HS = 5, 3.5
HT = N * HS
K_SOFT, SOFT_STORY = 0.40, 1        # 底層挑空：k1 = 0.40k < 0.70 門檻
M_HEAVY, HEAVY_FLOOR = 3.0, 1       # 底層重物：m1 = 3m > 1.5 門檻
HZ = [HS * (i + 1) for i in range(N)]
LIN = [HZ[i] / HT for i in range(N)]      # 規範隱含的線性振型


def build_K(ks):
    K = np.zeros((N, N))
    for i in range(N):
        K[i, i] += ks[i]
        if i > 0:
            K[i - 1, i - 1] += ks[i]
            K[i, i - 1] -= ks[i]
            K[i - 1, i] -= ks[i]
    return K


def modal(ks, ms):
    """廣義特徵值問題：先對稱化 A = M^(-1/2) K M^(-1/2)，避免 inv(M)K 非對稱"""
    K = build_K(ks)
    ms = np.asarray(ms, float)
    Mh = np.diag(1.0 / np.sqrt(ms))
    A = Mh @ K @ Mh
    w2, v = np.linalg.eigh((A + A.T) / 2)
    phi = Mh @ v
    i = np.argsort(w2)
    w2, phi = w2[i], phi[:, i]
    one, G, Me = np.ones(N), [], []
    for r in range(N):
        p = phi[:, r] / phi[-1, r]          # 頂層正規化為 1
        phi[:, r] = p
        L = p @ (np.diag(ms) @ one)
        M = p @ (np.diag(ms) @ p)
        G.append(L / M)
        Me.append(L * L / M)
    return np.sqrt(w2), phi, np.array(G), np.array(Me) / ms.sum()


ks_reg, ms_reg = [1.0] * N, [1.0] * N
ks_soft = ks_reg[:]; ks_soft[SOFT_STORY - 1] = K_SOFT
ms_mass = ms_reg[:]; ms_mass[HEAVY_FLOOR - 1] = M_HEAVY
ks_soft3 = ks_reg[:]; ks_soft3[2] = K_SOFT

CASES = [
    ("regular", "規則結構", ks_reg, ms_reg),
    ("soft", f"軟層（{SOFT_STORY}F，k = {K_SOFT}k）", ks_soft, ms_reg),
    ("mass", f"質量不規則（{HEAVY_FLOOR}F，m = {M_HEAVY:.0f}m）", ks_reg, ms_mass),
    ("soft3", "軟層（3F，k = 0.4k）", ks_soft3, ms_reg),
]
SOL = {k: modal(ks, ms) for k, _, ks, ms in CASES}
NAME = {k: n for k, n, _, _ in CASES}
KS = {k: ks for k, _, ks, _ in CASES}
MS = {k: ms for k, _, _, ms in CASES}


def sa(T, t0d=0.6):
    """示範用設計反應譜 SaD/SDS（四段式）"""
    x = T / t0d
    if x < 0.2:
        return 0.4 + 3 * x
    if x <= 1.0:
        return 1.0
    if x <= 2.5:
        return 1.0 / x
    return 0.4


def code_forces(key):
    ms = MS[key]
    wh = np.array([ms[i] * HZ[i] for i in range(N)])
    return wh / wh.sum()                       # 基底剪力正規化為 1


def modal_forces(key):
    w, phi, G, Me = SOL[key]
    ms = MS[key]
    f = np.zeros((N, N))
    for r in range(N):
        Tr = 2 * math.pi / w[r]
        for i in range(N):
            f[i, r] = G[r] * sa(Tr) * ms[i] * phi[i, r]
    F = np.sqrt((f ** 2).sum(axis=1))
    return F / F.sum()                          # 同基底剪力下比形狀


def drifts(key, F):
    """由側力分布算層間位移（Δi = Vi / ki）"""
    ks = KS[key]
    V = [sum(F[j] for j in range(i, N)) for i in range(N)]
    return np.array([V[i] / ks[i] for i in range(N)])


# ══════════════════════════════════════════════════════════
# 圖 1：第一振態形狀 — 兩種不規則各打破一個假設
# ══════════════════════════════════════════════════════════
def fig1():
    PW, PH = 366, 520

    def panel(key):
        w, phi, G, Me = SOL[key]
        p1 = phi[:, 0]
        dev = [abs(p1[i] - LIN[i]) for i in range(N)]
        j = int(np.argmax(dev))
        xmax, ymax = 1.34, HT * 1.10
        Lm, Rm, Tm, Bm = 76, 84, 96, 92
        sx = (PH - Tm - Bm) / ymax
        XSC = (PW - Lm - Rm) / (sx * xmax)      # 橫軸拉伸，讓振型差異看得見
        XM = lambda v: v * XSC
        cv = Canvas(PW, PH, sx=sx, ox=Lm, oy=Bm)
        cv.panel(NAME[key], f"第一振態有效質量 {Me[0]*100:.1f}%　｜　第二振態 {Me[1]*100:.1f}%")
        cv.line((0, 0), (0, HT * 1.04), C["muted"], 1.6)
        cv.poly([(0, 0)] + [(XM(LIN[i]), HZ[i]) for i in range(N)], C["ghost"], 3.4, dash="7 5")
        cv.poly([(0, 0)] + [(XM(p1[i]), HZ[i]) for i in range(N)], C["deform"], 4.4)
        for i in range(N):
            cv.dot((XM(p1[i]), HZ[i]), 4.4, C["deform"])
            cv.text_px(cv.X(0) - 10, cv.Y(HZ[i]), f"{i+1}F", 11, C["muted"], "end")
        cv.dot((XM(p1[j]), HZ[j]), 6.8, C["accent"])
        cv.double_arrow((XM(LIN[j]), HZ[j]), (XM(p1[j]), HZ[j]), C["accent"], 2.2, 8)
        cv.text_px(cv.X(XM(max(p1[j], LIN[j]))) + 8, cv.Y(HZ[j]) - 16,
                   f"偏離 {dev[j]:.3f}", 11.2, C["accent"], "start", weight="700")
        verdict = {
            "regular": ("兩個假設都成立", C["bmd"]),
            "soft": ("假設 B 失效（振型不再是直線）", C["accent"]),
            "mass": ("假設 A 失效（二振態 8.7%→16.3%）", C["accent"]),
        }[key]
        cv.text_px(PW / 2, PH - 52, verdict[0], 12.2, verdict[1], weight="700")
        cv.text_px(PW / 2, PH - 30, f"max|φ1 − h/H| = {max(dev):.3f}", 12, C["text"])
        return cv

    compose([panel("regular"), panel("soft"), panel("mass")], cols=3,
            title="圖 1　兩種不規則，各打破規範的一個假設",
            sub="灰虛線＝規範隱含的線性振型 φ ∝ h；藍實線＝廣義特徵值問題解出的真實第一振態",
            note="攔錯：以為公式裡的 wi 已處理掉質量不規則。wi 修正了質量，卻沒有修正振型；"
                 "也別以為不規則一定使第一振態有效質量下降——軟層反而上升",
            path=f"{OUT}/SD-2018-3-fig-1-mode-shapes.svg")


# ══════════════════════════════════════════════════════════
# 圖 2：軟層結構的側力分布與層間位移
# ══════════════════════════════════════════════════════════
def fig2():
    key = "soft"
    Fc, Fd = code_forces(key), modal_forces(key)
    # 傾覆彎矩分布 M(z) = Σ_{hi>z} Fi (hi − z)
    zs = [j * HT / 100 for j in range(101)]
    Mc = np.array([sum(Fc[i] * (HZ[i] - z) for i in range(N) if HZ[i] > z) for z in zs])
    Md = np.array([sum(Fd[i] * (HZ[i] - z) for i in range(N) if HZ[i] > z) for z in zs])

    PW, PH = 500, 540

    def panel_force():
        xmax = max(Fc.max(), Fd.max()) * 1.60
        ymax = HT * 1.10
        Lm, Rm, Tm, Bm = 82, 152, 96, 108
        sy = (PH - Tm - Bm) / ymax
        XSC = (PW - Lm - Rm) / (sy * xmax)
        cv = Canvas(PW, PH, sx=sy, ox=Lm, oy=Bm)
        XM = lambda v: v * XSC
        cv.panel("側力分布 Fi", "基底剪力已正規化為相同，比較的是形狀")
        cv.line((0, 0), (0, HT * 1.04), C["muted"], 1.6)
        for vals, col, dsh in ((Fc, C["load"], None), (Fd, C["sfd"], "8 5")):
            cv.poly([(XM(vals[i]), HZ[i]) for i in range(N)], col, 3.6, dash=dsh)
            for i in range(N):
                cv.dot((XM(vals[i]), HZ[i]), 4.8, col)
        for i in range(N):
            cv.text_px(cv.X(0) - 10, cv.Y(HZ[i]), f"{i+1}F", 11, C["muted"], "end")
            d = (Fd[i] - Fc[i]) / Fc[i] * 100
            cv.text_px(cv.X(XM(max(Fc[i], Fd[i]))) + 12, cv.Y(HZ[i]) + (16 if i == 0 else 0),
                       f"{d:+.0f}%", 12,
                       C["accent"] if abs(d) >= 20 else C["muted"], "start", weight="700")
        cv.line((0, HZ[0]), (XM(xmax) * 0.98, HZ[0]), C["accent"], 1.4, dash="6 5")
        cv.text_px(cv.X(XM(xmax * 0.46)), cv.Y(HZ[0] - HS * 0.55),
                   f"{SOFT_STORY}F 軟層", 11.5, C["accent"], weight="700")
        cv.legend(18, PH - 76, [(C["load"], "規範 F ∝ w·h"), (C["sfd"], "振態疊加 SRSS")])
        cv.text_px(PW / 2, PH - 26,
                   f"規範把 1F 的力少算一半、5F 多算 {abs((Fd[-1]-Fc[-1])/Fc[-1]*100):.0f}%",
                   12, C["text"], weight="700")
        return cv

    def panel_moment():
        xmax = max(Mc.max(), Md.max()) * 1.42
        ymax = HT * 1.10
        Lm, Rm, Tm, Bm = 82, 152, 96, 108
        sy = (PH - Tm - Bm) / ymax
        XSC = (PW - Lm - Rm) / (sy * xmax)
        cv = Canvas(PW, PH, sx=sy, ox=Lm, oy=Bm)
        XM = lambda v: v * XSC
        cv.panel("傾覆彎矩 M(z)", "力放得愈高，傾覆彎矩愈大")
        cv.line((0, 0), (0, HT * 1.04), C["muted"], 1.6)
        cv.poly([(XM(Mc[k]), zs[k]) for k in range(len(zs))], C["load"], 3.6)
        cv.poly([(XM(Md[k]), zs[k]) for k in range(len(zs))], C["sfd"], 3.6, dash="8 5")
        for i in range(N):
            cv.text_px(cv.X(0) - 10, cv.Y(HZ[i]), f"{i+1}F", 11, C["muted"], "end")
        cv.dot((XM(Mc[0]), 0), 5.2, C["load"])
        cv.dot((XM(Md[0]), 0), 5.2, C["sfd"])
        cv.text_px(cv.X(XM(Mc[0])) + 12, cv.Y(0) - 12, f"規範 {Mc[0]:.2f}",
                   12, C["load"], "start", weight="700")
        cv.text_px(cv.X(XM(Md[0])) + 12, cv.Y(0) + 10, f"動力 {Md[0]:.2f}",
                   12, C["sfd"], "start", weight="700")
        cv.text_px(PW / 2, PH - 26,
                   f"基底傾覆彎矩差 {(Md[0]-Mc[0])/Mc[0]*100:+.0f}%（同一個基底剪力）",
                   12, C["text"], weight="700")
        return cv

    compose([panel_force(), panel_moment()], cols=2,
            title=f"圖 2　軟層結構（{SOFT_STORY}F，k = {K_SOFT}k）：規範分配 vs 振態疊加",
            sub="規範把力按 w·h 攤成倒三角；真實第一振態卻幾乎是「軟層以上剛體平移」",
            note="攔錯：以為兩法只差基底剪力大小。基底剪力相同時，錯的是力的「分布」——"
                 "各層構材內力與傾覆彎矩全都跟著錯，Ft 加在頂部完全補不到 1F",
            path=f"{OUT}/SD-2018-3-fig-2-code-vs-modal.svg")


# ══════════════════════════════════════════════════════════
# 圖 3：有效振態質量分布
# ══════════════════════════════════════════════════════════
def fig3():
    W, HH = 1000, 620
    cv = Canvas(W, HH, sx=1, bg="#FFFFFF")
    cv.text_px(W / 2, 34, "圖 3　有效振態質量：不規則不必然使第一振態失去主導",
               17.5, C["text"], weight="700")
    cv.text_px(W / 2, 58, "各振態有效質量佔總質量的百分比（由特徵值問題算出，總和 100%）",
               13, C["muted"])
    x0, bw = 268, 560
    cols = [C["deform"], C["sfd"], C["bmd"], C["accent"], C["member2"]]
    order = ["regular", "soft", "mass", "soft3"]
    base = SOL["regular"][3][0]
    for j, key in enumerate(order):
        Me = SOL[key][3]
        y = 132 + j * 84
        cv.text_px(24, y - 10, NAME[key], 13.5, C["text"], "start", weight="700")
        d = (Me[0] - base) * 100
        cv.text_px(24, y + 12,
                   f"第一振態 {Me[0]*100:.1f}%" + ("" if key == "regular" else f"（{d:+.1f} pt）"),
                   11.8, C["accent"] if abs(d) > 2 else C["muted"], "start", weight="700")
        acc = 0.0
        for r in range(N):
            wd = bw * Me[r]
            if wd > 0.6:
                cv.rect_px(x0 + bw * acc, y - 19, wd, 38, cols[r], 6)
                if Me[r] > 0.055:
                    cv.text_px(x0 + bw * acc + wd / 2, y, f"{Me[r]*100:.0f}%",
                               12.5, "#FFFFFF", weight="700")
            acc += Me[r]
        acc2, need = 0.0, N
        for r in range(N):
            acc2 += Me[r]
            if acc2 >= 0.90:
                need = r + 1
                break
        cv.text_px(x0 + bw + 14, y, f"達 90% 需 {need} 個振態", 12.5,
                   C["accent"] if need > 1 else C["muted"], "start", weight="700")
    cv.parts.append(f'<line x1="{x0+bw*0.9:.1f}" y1="{106}" x2="{x0+bw*0.9:.1f}" '
                    f'y2="{132+3*84+26}" stroke="{C["text"]}" stroke-width="2" '
                    f'stroke-dasharray="5 4"/>')
    cv.text_px(x0 + bw * 0.9, 96, "規範門檻 90%", 12, C["text"], weight="700")
    cv.legend(x0, HH - 168, [(cols[r], f"振態 {r+1}") for r in range(N)], gap=19)
    cv.text_px(W / 2, HH - 24,
               "攔錯：把「不規則 → 第一振態有效質量下降」當成通則。軟層在底層時反而上升到 95.5%，"
               "失效的是振型形狀而不是振態主導性",
               13, C["muted"])
    cv.save(f"{OUT}/SD-2018-3-fig-3-modal-mass.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1(); fig2(); fig3()
    for key, name, _, _ in CASES:
        w, phi, G, Me = SOL[key]
        dev = max(abs(phi[i, 0] - LIN[i]) for i in range(N))
        print(f"{name:26s} Meff=[{' '.join(f'{x*100:5.1f}' for x in Me)}]  "
              f"max|phi1-lin|={dev:.3f}")
