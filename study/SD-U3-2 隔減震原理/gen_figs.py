#!/usr/bin/env python3
"""SD-U3-2 隔減震原理 —— 向量圖產生腳本（14 張）。

圖上每一個數字都 import 自 case.py，不得手打。
驗證：python3 <struct-diagram>/scripts/render.py . --scale=2.0
"""
import math
from plotkit import Plot, canvas, compose, C, sampled, badge
import case as K

P = "sd32-fig-"
LRB, FPS, TMD, FVD, BRB = K.LRB, K.FPS, K.TMD, K.FVD, K.BRB
R_L, R_F, FIX = K.LRB_R, K.FPS_R, K.FIX

NAVY, ORANGE, BLUE, RED, GREEN, PURPLE = (C["text"], C["accent"], C["deform"],
                                          C["load"], C["bmd"], C["sfd"])

def f1(x): return f"{x:.1f}"
def f2(x): return f"{x:.2f}"
def pct(x): return f"{x*100:.1f}%"


# ══════════════════════════════════════════════════════════════════
# 圖 1　反應譜上的兩個旋鈕
# ══════════════════════════════════════════════════════════════════
def fig1():
    cv = canvas(1020, 560)
    pl = Plot(cv, 96, 108, 690, 340, (0, 4.0), (0, 0.9))
    pl.frame(xticks=[0, 0.6, 1, 2, 3, 4], yticks=[0, 0.2, 0.4, 0.6, 0.8],
             xlabel="有效振動週期 T (s)", ylabel="設計譜加速度 Sa (g)",
             xfmt="{:g}", yfmt="{:.1f}")

    pl.curve(sampled(K.Sa, 0.02, 4.0), NAVY, 2.8)
    b1 = R_L["B1"]
    pl.curve(sampled(lambda t: K.Sa(t) / b1, 0.02, 4.0), GREEN, 2.4, dash="7 5")

    Tf, Saf = FIX["T"], FIX["Sa"]
    Ti = R_L["Teff"]
    Sai, Sae = K.Sa(Ti), K.Sa(Ti) / b1

    pl.arrow((Tf, Saf), (Ti, Sai), ORANGE, 3.0, 11)
    pl.arrow((Ti, Sai), (Ti, Sae), GREEN, 3.0, 11)
    pl.dot((Tf, Saf), 6.2, RED)
    pl.dot((Ti, Sai), 5.4, ORANGE)
    pl.dot((Ti, Sae), 6.2, GREEN)

    pl.tag((Tf, Saf), "固定基礎 T = 0.80 s", 13.5, RED, dx=-14, dy=-12,
           anchor="end")
    pl.tag((Tf, Saf), "Sa = 0.600 g ⇒ V/W = 60%", 12.5, C["muted"],
           dx=-14, dy=8, anchor="end", weight="400")
    pl.tag(((Tf + Ti) / 2, 0.80), "旋鈕①　延長週期", 14.5, ORANGE)
    pl.tag(((Tf + Ti) / 2, 0.80), "沿 5% 譜把工作點往右搬", 12.5, C["muted"],
           dy=20, weight="400")
    pl.tag((Ti, (Sai + Sae) / 2), "旋鈕②", 14.5, GREEN, dx=-12, anchor="end")
    pl.tag((Ti, (Sai + Sae) / 2), "阻尼 ÷ B1", 12.5, C["muted"],
           dx=-12, dy=19, anchor="end", weight="400")
    pl.tag((Ti, Sae), f"隔震後 T = {f2(Ti)} s、ξ = {pct(R_L['xi'])}", 13.5,
           GREEN, dx=16, dy=-4, anchor="start")
    pl.tag((Ti, Sae), f"Sa,eff = {Sae:.3f} g ⇒ V/W = {pct(R_L['VW'])}", 12.5,
           C["muted"], dx=16, dy=16, anchor="start", weight="400")

    cv.legend(812, 268, [(NAVY, "設計譜 ξ = 5%"),
                         (GREEN, f"折減譜 ÷ B1 = {f2(b1)}")])
    badge(cv, 806, 320, 202, 150,
          ["V 由 7,200 tf",
           f"降到 {R_L['V']:,.0f} tf",
           f"只剩 {R_L['V']/FIX['V']*100:.0f}%",
           f"（{FIX['V']/R_L['V']:.1f} 倍）"],
          title="力降了多少", title_color=NAVY, size=13, lh=21)

    cv.text_px(510, 40, "隔震不是「把結構做強」，是把工作點搬到譜上力比較小的地方",
               17.5, NAVY, weight="700")
    cv.text_px(510, 66, "同一棟 12,000 tf 的八層建築、同一張設計譜，只是換了兩個旋鈕",
               13, C["muted"])
    cv.text_px(510, 532,
               "攔錯：把隔震說成「加阻尼」。阻尼只提供圖上那段垂直的折減，水平那段才是隔震的本體。",
               13.5, C["muted"])
    cv.save(P + "1-two-knobs.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 2　力與位移的矛盾
# ══════════════════════════════════════════════════════════════════
def fig2():
    b1 = R_L["B1"]
    Tf, Ti = FIX["T"], R_L["Teff"]

    a = canvas(510, 430)
    a.panel("加速度（力）：週期愈長愈小", "Sa 在等速度段與 T 成反比")
    pa = Plot(a, 78, 112, 388, 212, (0, 4.0), (0, 0.9))
    pa.frame(xticks=[0, 1, 2, 3, 4], yticks=[0, 0.2, 0.4, 0.6, 0.8],
             xlabel="T (s)", ylabel="Sa (g)", yfmt="{:.1f}")
    pa.curve(sampled(K.Sa, 0.02, 4.0), NAVY, 2.6)
    pa.dot((Tf, FIX["Sa"]), 5.4, RED)
    pa.dot((Ti, K.Sa(Ti)), 5.4, ORANGE)
    pa.arrow((Tf, FIX["Sa"]), (Ti, K.Sa(Ti)), ORANGE, 2.6, 10)
    pa.tag((Tf, FIX["Sa"]), "0.600 g", 12.5, RED, dx=8, dy=-12, anchor="start")
    pa.tag((Ti, K.Sa(Ti)), f"{K.Sa(Ti):.3f} g", 12.5, ORANGE, dx=10, dy=-10,
           anchor="start")
    a.text_px(255, 396, f"週期 {Ti/Tf:.1f} 倍　⇒　力降為 {K.Sa(Ti)/FIX['Sa']:.2f} 倍",
              13.5, GREEN, weight="700")

    b = canvas(510, 430)
    b.panel("位移：週期愈長愈大（這就是代價）", "等速度段 D 與 T 成正比")
    pb = Plot(b, 78, 112, 388, 212, (0, 4.0), (0, 40))
    pb.frame(xticks=[0, 1, 2, 3, 4], yticks=[0, 10, 20, 30, 40],
             xlabel="T (s)", ylabel="譜位移 D (cm)")
    pb.curve(sampled(lambda t: K.Sd(t), 0.02, 4.0), NAVY, 2.6)
    pb.curve(sampled(lambda t: K.Sd(t, b1), 0.02, 4.0), GREEN, 2.4, dash="7 5")
    D5 = K.Sd(Ti)
    pb.dot((Tf, FIX["D"]), 5.4, RED)
    pb.dot((Ti, D5), 5.4, ORANGE)
    pb.dot((Ti, R_L["D"]), 5.6, GREEN)
    pb.arrow((Tf, FIX["D"]), (Ti, D5), ORANGE, 2.6, 10)
    pb.arrow((Ti, D5), (Ti, R_L["D"]), GREEN, 2.8, 10)
    pb.tag((Tf, FIX["D"]), f"{f1(FIX['D'])} cm", 12.5, RED, dx=8, dy=12,
           anchor="start")
    pb.tag((Ti, D5), f"{f1(D5)} cm（若只有 5%）", 12.5, ORANGE, dx=-12, dy=-12,
           anchor="end")
    pb.tag((Ti, R_L["D"]), f"{f1(R_L['D'])} cm", 13, GREEN, dx=12, dy=4,
           anchor="start")
    b.text_px(255, 396, f"阻尼 ξ = {pct(R_L['xi'])} 把位移收回 "
                        f"{(1-R_L['D']/D5)*100:.0f}%", 13.5, GREEN, weight="700")

    compose([a, b],
            title="延長週期一定要付位移的代價；阻尼是唯一能把代價收回來的東西",
            sub=f"同一棟建築、同一張譜：力從 {FIX['Sa']:.3f} g → {K.Sa(Ti):.3f} g，"
                f"但位移從 {f1(FIX['D'])} cm → {f1(D5)} cm，"
                f"必須再靠阻尼壓回 {f1(R_L['D'])} cm",
            note="攔錯：只講「隔震降低地震力」而不檢核隔震層位移。位移不夠就會撞擊隔震溝、拉斷管線。",
            path=P + "2-force-disp-tradeoff.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 3　串聯彈簧與剛體平移
# ══════════════════════════════════════════════════════════════════
def fig3():
    a = canvas(500, 460)
    a.panel("力學模型：兩根彈簧串聯", "同一個力走過兩根彈簧，位移相加")
    # 上部結構（方塊）
    a.rect_px(150, 96, 200, 112, "#EDF1F6", 10, C["border"], 1.4)
    a.text_px(250, 140, "上部結構", 15, NAVY, weight="700")
    a.math_px(250, 166, f"k_{{sup}} = {K.K_SUP:.0f}", 14, NAVY)
    a.text_px(250, 188, "tf/cm", 12, C["muted"])
    # 隔震層彈簧
    xs, y0, y1 = 250, 208, 300
    zig = [(xs, y0)]
    for i in range(1, 9):
        zig.append((xs + (26 if i % 2 else -26), y0 + i * (y1 - y0) / 9))
    zig.append((xs, y1))
    a.poly([(x, a.h - y) for x, y in zig], BLUE, 3.0)
    a.text_px(320, 244, "隔震層", 14.5, BLUE, "start", weight="700")
    a.math_px(320, 268, f"k_b = {R_L['Keff']:.1f}", 13.5, BLUE, "start")
    # 基礎
    a.rect_px(120, 300, 260, 18, C["ghost"], 4)
    a._hatch(250, 318, 1, 0, 1, 0, 260, C["member"], 9, 1.4)
    a.text_px(250, 344, "基礎／地盤", 12.5, C["muted"])

    badge(a, 44, 366, 412, 78,
          [f"1/k_{{eq}} = 1/{K.K_SUP:.0f} + 1/{R_L['Keff']:.1f}"
           f"　⇒　k_{{eq}} = {K.K_SERIES:.1f} tf/cm",
           f"最軟的那根主宰：k_{{eq}} 只比 k_b 小 "
           f"{(1-K.K_SERIES/R_L['Keff'])*100:.0f}%"],
          title="串聯，不是並聯", title_color=BLUE, size=13, lh=22)

    b = canvas(500, 460)
    b.panel("後果：第一振態幾乎是剛體平移", "所以可以用單自由度等值靜力法")
    # 兩棟對照的振態
    for k, (ox, lab, col, top, curved) in enumerate(
            [(96, "固定基礎", C["muted"], 0.0, True),
             (300, "基礎隔震", BLUE, 0.0, False)]):
        base_y, H = 330, 200
        b.line((ox, b.h - base_y), (ox, b.h - (base_y - H)), C["ghost"], 2.2,
               dash="5 5")
        pts = []
        for i in range(31):
            t = i / 30
            u = 62 * (t ** 1.7) if curved else 62 * (0.12 + 0.88 * t ** 0.12)
            pts.append((ox + u, b.h - (base_y - H * t)))
        b.poly(pts, col, 4.2)
        for t in (0.25, 0.5, 0.75, 1.0):
            u = 62 * (t ** 1.7) if curved else 62 * (0.12 + 0.88 * t ** 0.12)
            b.line((ox, b.h - (base_y - H * t)), (ox + u, b.h - (base_y - H * t)),
                   C["ghost"], 1.4)
            b.dot((ox + u, b.h - (base_y - H * t)), 3.6, col)
        b.text_px(ox + 30, base_y + 24, lab, 13.5, col, weight="700")
        if not curved:
            b.rect_px(ox - 6, base_y - 8, 80, 12, "rgba(29,78,216,0.18)", 3)
    b.text_px(250, base_y + 52 if False else 382,
              "隔震後層間變位集中在隔震層，上部各層幾乎同步移動",
              13, C["muted"])
    badge(b, 44, 398, 412, 46,
          ["有效模態質量超過 95%，高振態貢獻可忽略"],
          size=13, color=C["muted"])

    compose([a, b],
            title="隔震層與上部結構是串聯：最軟的彈簧主宰全局",
            sub=f"k_b/k_sup = {R_L['Keff']/K.K_SUP:.3f}，隔震層軟了快 10 倍，"
                f"所以整體週期由它決定",
            note=f"誠實的但書：把上部結構當剛體算得 T = {f2(R_L['Teff'])} s，"
                 f"真正串聯算是 {f2(K.T_SERIES)} s，低估約 {K.SERIES_ERR*100:.0f}%——"
                 f"偏不保守於位移，初步設計可接受，細部設計要回到多自由度分析。",
            path=P + "3-series-spring.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 4　LRB 雙線性遲滯迴圈
# ══════════════════════════════════════════════════════════════════
def fig4():
    D = R_L["D"]
    Qd, kd, k0, Dy = LRB.Qd, LRB.kd, LRB.k0, LRB.Dy
    Fm = Qd + kd * D
    Fy = LRB.Fy
    loop = [(D, Fm), (D - 2 * Dy, Fm - 2 * Fy), (-D, -Fm),
            (-D + 2 * Dy, -Fm + 2 * Fy), (D, Fm)]

    cv = canvas(1020, 600)
    pl = Plot(cv, 110, 118, 640, 374, (-26, 26), (-2100, 2100))
    pl.frame(xticks=[-20, -10, 0, 10, 20], yticks=[-2000, -1000, 0, 1000, 2000],
             xlabel="隔震層位移 D (cm)", ylabel="回復力 F (tf)")
    pl.area(loop, "rgba(29,78,216,0.18)", BLUE, 2.6)

    # 骨幹線與割線
    pl.seg((-26, -Qd - kd * 26), (26, Qd + kd * 26), C["muted"], 1.6, dash="6 5")
    pl.seg((0, 0), (D, Fm), RED, 2.6)
    pl.seg((0, 0), (Dy, k0 * Dy), GREEN, 2.4)
    pl.dot((D, Fm), 6, BLUE)
    pl.dot((Dy, Fy), 5, GREEN)

    # 標註
    pl.hline(Qd, ORANGE, 1.6, "5 5", x=0)
    pl.seg((-7.5, 0), (-7.5, Qd), ORANGE, 2.4)
    pl.tag((-7.5, Qd / 2), f"Qd = {Qd:.0f} tf", 13, ORANGE, dx=-10, anchor="end")
    pl.tag((-7.5, Qd / 2), "特徵強度", 12, C["muted"], dx=-10, dy=18,
           anchor="end", weight="400")
    pl.tag((D, Fm), f"D = {f1(D)} cm", 13, BLUE, dx=2, dy=-30, anchor="end")
    pl.tag((D, Fm), f"F = {Fm:,.0f} tf", 13, BLUE, dx=2, dy=-12, anchor="end")
    pl.tag((D * 0.40, Qd * 0.40 + kd * D * 0.40), f"割線 Keff = {R_L['Keff']:.1f} tf/cm",
           12.5, RED, dx=8, dy=30, anchor="start")
    pl.tag((-16.5, -Qd - kd * 16.5), "骨幹線斜率 = kd = 50 tf/cm", 12.5,
           C["muted"], dx=6, dy=26, anchor="start", weight="400")
    pl.tag((Dy, Fy), f"Dy = {Dy:.2f} cm", 12.5, GREEN, dx=-8, dy=-30,
           anchor="end")
    pl.tag((Dy, Fy), "（沿 k0 = 500 卸載）", 12, C["muted"], dx=-8, dy=-12,
           anchor="end", weight="400")
    pl.tag((-1.5, -880), "迴圈面積 = Wd", 14, BLUE, anchor="start")
    pl.tag((-1.5, -880), f"= 4Qd(D − Dy) = {LRB.Wd(D):,.0f} tf·cm", 12.5,
           C["muted"], dy=20, anchor="start", weight="400")

    badge(cv, 780, 126, 224, 200,
          [f"k0 = {k0:.0f} tf/cm（初始）",
           f"kd = {kd:.0f} tf/cm（降伏後）",
           f"α = kd/k0 = {LRB.alpha}",
           f"Fy = Qd/(1−α) = {Fy:.0f} tf",
           f"Dy = Fy/k0 = {Dy:.2f} cm",
           f"Keff = Qd/D + kd",
           f"　　 = {R_L['Keff']:.1f} tf/cm"],
          title="鉛心橡膠的四個常數", title_color=BLUE, size=12.5, lh=20)
    badge(cv, 780, 344, 224, 170,
          ["迴圈是平行四邊形，不是",
           "矩形：右上角要沿 k0 卸載",
           f"2Dy = {2*Dy:.2f} cm 才回到",
           "另一條骨幹線。",
           "漏掉這段，Wd 會高估",
           f"{Dy/(D-Dy)*100:.0f}%。"],
          title="為什麼要扣 Dy", title_color=RED, size=12.5, lh=20)

    cv.text_px(510, 42, "LRB 的一切都寫在這個迴圈裡：割線給勁度，面積給阻尼",
               17.5, NAVY, weight="700")
    cv.text_px(510, 68, f"示範建築 W = 12,000 tf，鉛心特徵強度取 0.05W", 13,
               C["muted"])
    cv.text_px(510, 572,
               "攔錯：把 Keff 取成 k0 或 kd。等效線性化一定是「過原點到最大位移」的割線。",
               13.5, C["muted"])
    cv.save(P + "4-bilinear-loop.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 5　割線 vs 切線
# ══════════════════════════════════════════════════════════════════
def fig5():
    D = R_L["D"]
    Qd, kd, k0 = LRB.Qd, LRB.kd, LRB.k0
    Fm = Qd + kd * D
    T_sec, T_kd, T_k0 = R_L["Teff"], K.T_eff(kd), K.T_eff(k0)

    panels = []
    for lab, k, col, Tv, ok in [
            ("【正解】割線勁度 Keff = F(D)/D", R_L["Keff"], GREEN, T_sec, True),
            ("【錯誤】取降伏後切線 kd", kd, RED, T_kd, False),
            ("【錯誤】取初始勁度 k0", k0, PURPLE, T_k0, False)]:
        cv = canvas(340, 430)
        cv.panel(lab, f"k = {k:.1f} tf/cm")
        pl = Plot(cv, 66, 148, 236, 178, (0, 24), (0, 2200))
        pl.frame(xticks=[0, 10, 20], yticks=[0, 1000, 2000],
                 xlabel="D (cm)", ylabel="F (tf)")
        pl.curve([(0, 0), (LRB.Dy, k0 * LRB.Dy), (24, Qd + kd * 24)], NAVY, 2.4)
        pl.seg((0, 0), (min(24, 2200 / k), min(24 * k, 2200)), col, 2.8)
        pl.dot((D, Fm), 5.4, BLUE)
        cv.text_px(170, 358, f"T = 2π√(m/k) = {f2(Tv)} s", 14,
                   col, weight="700")
        cv.text_px(170, 383,
                   "與正解一致" if ok else f"偏差 {abs(Tv/T_sec-1)*100:.0f}%",
                   12.5, C["muted"])
        cv.text_px(170, 407,
                   "面積與割線同時對帳" if ok else
                   ("週期過長、位移高估" if k < R_L["Keff"] else "週期過短、力被高估"),
                   12.5, C["muted"])
        panels.append(cv)

    compose(panels,
            title="等效線性化只有一種勁度可以用：過原點的割線",
            sub=f"三種取法算出來的週期分別是 {f2(T_sec)} / {f2(T_kd)} / {f2(T_k0)} 秒，"
                f"差距最大到 {T_k0/T_sec:.0%} 以上",
            note="判斷法：割線必須通過「原點」與「本輪迭代的最大位移點」兩點，"
                 "少任何一點都不是 Keff。",
            path=P + "5-secant-vs-tangent.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 6　FPS 摩擦單擺幾何
# ══════════════════════════════════════════════════════════════════
def fig6():
    Rr, mu, D = FPS.R, FPS.mu, R_F["D"]
    Fr, Ff = K.W * D / Rr, mu * K.W

    a = canvas(520, 470)
    a.panel("倒單擺幾何", "滑動面是半徑 R 的球面")
    cx, cy, sc = 260, 92, 1.28          # 圓心像素、每 cm 幾像素（示意縮放）
    rr = 210.0
    pts = []
    for i in range(121):
        th = math.radians(-58 + 116 * i / 120)
        pts.append((cx + rr * math.sin(th), a.h - (cy + rr * math.cos(th))))
    a.poly(pts, C["member"], 3.4)
    a.dot((cx, a.h - cy), 4.4, C["muted"])
    ang = math.radians(20)
    sx_, sy_ = cx + rr * math.sin(ang), cy + rr * math.cos(ang)
    a.line((cx, a.h - cy), (sx_, a.h - sy_), C["dim"], 1.6, dash="5 5")
    a.line((cx, a.h - cy), (cx, a.h - (cy + rr)), C["dim"], 1.6, dash="5 5")
    a.math_px(cx + 44, cy + 104, "R", 15, C["dim"])
    # 滑塊（騎在弧線上）＋ 垂直投影，讓 D 看得出是水平偏移
    a.rect_px(sx_ - 32, sy_ - 34, 64, 32, "#EDF1F6", 6, C["border"], 1.4)
    a.arrow((sx_, a.h - (sy_ - 40)), (sx_, a.h - (sy_ - 104)), RED, 3.0, 10)
    a.math_px(sx_ + 12, sy_ - 92, "W", 15, RED, "start")
    a.line((sx_, a.h - sy_), (sx_, a.h - (cy + rr + 10)), C["dim"], 1.4,
           dash="5 5")
    a.line((cx, a.h - (cy + rr + 10)), (sx_, a.h - (cy + rr + 10)), ORANGE, 2.6)
    a.text_px((cx + sx_) / 2, cy + rr + 34, f"D = {f1(D)} cm", 13, ORANGE,
              weight="700")
    a.arrow((sx_ - 32, a.h - (sy_ - 18)), (sx_ - 100, a.h - (sy_ - 18)),
            BLUE, 2.8, 10)
    a.text_px(sx_ - 104, sy_ - 18, f"W·D/R = {Fr:,.0f} tf", 12.5, BLUE, "end",
              weight="700")
    a.text_px(260, 400, "重力提供回復力，摩擦提供消能", 13.5, NAVY, weight="700")
    a.text_px(260, 424, "兩件事由同一片滑動面同時做完", 12.5, C["muted"])

    b = canvas(520, 470)
    b.panel("週期與重量完全無關", "這是 FPS 最反直覺、也最常被考的性質")
    for i, (wlab, col, yy) in enumerate([("W = 6,000 tf", C["muted"], 150),
                                         ("W = 12,000 tf", NAVY, 235),
                                         ("W = 24,000 tf", BLUE, 320)]):
        b.rect_px(70, yy - 26, 150 + i * 26, 52, "#EDF1F6", 8, C["border"], 1.2)
        b.text_px(80, yy, wlab, 13.5, col, "start", weight="700")
        b.arrow((250 + i * 26, b.h - yy), (346, b.h - yy), C["dim"], 2.2, 9)
        b.text_px(430, yy, f"T = {FPS.T_pendulum:.3f} s", 14.5, ORANGE,
                  weight="700")
    badge(b, 56, 356, 408, 92,
          ["T = 2π√(m/k)，而 k = W/R = mg/R",
           "⇒ T = 2π√(mR/mg) = 2π√(R/g)，m 被約掉了",
           f"R = {Rr:.0f} cm ⇒ T = {FPS.T_pendulum:.3f} s"],
          title="為什麼可以約掉", title_color=NAVY, size=12.5, lh=21)

    compose([a, b],
            title="FPS：回復力來自幾何（W·D/R），阻尼來自摩擦（μW）",
            sub=f"本案例 R = {Rr:.0f} cm、μ = {mu}，定案位移 D = {f1(D)} cm 時"
                f"回復力 {Fr:,.0f} tf ＋ 摩擦力 {Ff:,.0f} tf = {Fr+Ff:,.0f} tf",
            note=f"注意：純單擺週期 {FPS.T_pendulum:.2f} s 與 W 無關，"
                 f"但加了摩擦項之後的「有效週期」{f2(R_F['Teff'])} s 會隨位移 D 改變——"
                 f"這兩個週期不是同一個東西。",
            path=P + "6-fps-geometry.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 7　兩種遲滯迴圈對照
# ══════════════════════════════════════════════════════════════════
def fig7():
    DL, DF = R_L["D"], R_F["D"]
    Qf = FPS.mu * K.W

    a = canvas(510, 450)
    a.panel("LRB：有明顯的降伏轉角",
            f"Q = Qd = {LRB.Qd:.0f} tf，Dy = {LRB.Dy:.2f} cm，卸載斜率 k0 = 500")
    pa = Plot(a, 76, 132, 386, 220, (-24, 24), (-1900, 1900))
    pa.frame(xticks=[-20, 0, 20], yticks=[-1500, 0, 1500],
             xlabel="D (cm)", ylabel="F (tf)")
    Fm = LRB.Qd + LRB.kd * DL
    Fy = LRB.Fy
    pa.area([(DL, Fm), (DL - 2 * LRB.Dy, Fm - 2 * Fy), (-DL, -Fm),
             (-DL + 2 * LRB.Dy, -Fm + 2 * Fy)], "rgba(29,78,216,0.18)", BLUE, 2.4)
    a.text_px(255, 394, f"Wd = 4Qd(D − Dy) = {LRB.Wd(DL):,.0f} tf·cm", 13.5,
              BLUE, weight="700")
    a.text_px(255, 420, f"ξeq = {pct(R_L['xi'])}", 13, C["muted"])

    b = canvas(510, 450)
    b.panel("FPS：四個角幾乎是直角",
            f"Q = μW = {Qf:.0f} tf，Dy ≈ 0，滑動後斜率 W/R = {K.W/FPS.R:.1f}")
    pb = Plot(b, 76, 132, 386, 220, (-24, 24), (-1900, 1900))
    pb.frame(xticks=[-20, 0, 20], yticks=[-1500, 0, 1500],
             xlabel="D (cm)", ylabel="F (tf)")
    kf = K.W / FPS.R
    pb.area([(DF, kf * DF + Qf), (-DF, -kf * DF + Qf), (-DF, -kf * DF - Qf),
             (DF, kf * DF - Qf)], "rgba(180,83,9,0.18)", ORANGE, 2.4)
    b.text_px(255, 394, f"Wd = 4μW·D = {FPS.Wd(DF):,.0f} tf·cm", 13.5, ORANGE,
              weight="700")
    b.text_px(255, 420, f"ξeq = 2μ/(πA) = {pct(R_F['xi'])}", 13, C["muted"])

    compose([a, b],
            title="其實是同一條公式：Wd = 4Q(D − Dy)，差別只在 Q 是誰、Dy 大不大",
            sub="LRB 的 Q 是鉛心的特徵強度、Dy 約 1.3 cm 不可忽略；"
                "FPS 的 Q 是摩擦力 μW、起滑位移趨近於零，公式才退化成 4μWD",
            note=f"分母一律用「系統」的割線勁度：ξ = Wd/(2π·Keff·D²)。"
                 f"用單顆支承的勁度、或用 kd 當分母，都會算錯阻尼比。",
            path=P + "7-loop-compare.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 8　迭代收斂（蛛網圖）
# ══════════════════════════════════════════════════════════════════
def fig8():
    def Dnext(D):
        Ke = LRB.Keff(D)
        Te = K.T_eff(Ke)
        return K.Sa(Te) * K.G * Te ** 2 / (4 * math.pi ** 2 * K.B1(LRB.xi(D)))

    cv = canvas(1020, 560)
    pl = Plot(cv, 100, 112, 600, 340, (14, 22), (14, 22))
    pl.frame(xticks=[14, 16, 18, 20, 22], yticks=[14, 16, 18, 20, 22],
             xlabel="本輪代入的位移 D (cm)",
             ylabel="算出來的新位移 D_{new} (cm)")
    pl.curve([(14, 14), (22, 22)], C["muted"], 1.8, dash="6 5")
    pl.tag((21.0, 21.0), "45° 線：代入 = 算出", 12.5, C["muted"], dx=-8, dy=18,
           anchor="end", weight="400")
    pl.curve(sampled(Dnext, 14, 22, 120), NAVY, 2.8)

    # 蛛網
    for i, r in enumerate(K.LRB_IT):
        pl.seg((r["D"], r["D"]), (r["D"], r["Dnew"]), ORANGE, 2.4)
        pl.arrow((r["D"], r["Dnew"]), (r["Dnew"], r["Dnew"]), ORANGE, 2.4, 9)
        pl.dot((r["D"], r["Dnew"]), 5.4, ORANGE)
        pl.tag((r["D"], r["Dnew"]), f"第 {i+1} 輪", 12.5, ORANGE,
               dx=12, dy=-8, anchor="start")
    pl.dot((R_L["D"], R_L["D"]), 6.6, GREEN)
    pl.tag((R_L["D"], R_L["D"]), f"定案 D = {f1(R_L['D'])} cm", 13.5, GREEN,
           dx=-16, dy=34, anchor="end")

    rows = [f"第 {r['n']} 輪　{f1(r['D'])} → {f1(r['Dnew'])} cm"
            f"　誤差 {r['err']*100:.1f}%" for r in K.LRB_IT]
    badge(cv, 392, 300, 296, 40 + 20 * (len(rows) + 1),
          rows + ["收斂判準：誤差小於 5%"],
          fill="#FFFFFF", size=12.8, lh=20, color=C["muted"],
          title="迭代表格", title_color=ORANGE)

    badge(cv, 730, 120, 276, 178,
          ["Keff 是 D 的函數 ⇒ T 也是",
           "T 變 ⇒ Sa 變 ⇒ D 變",
           "ξ 變 ⇒ B1 變 ⇒ D 又變",
           "",
           "所以只能猜一個 D 進去，",
           "看吐出來的 D 對不對得上。"],
          title="為什麼一定要迭代", title_color=NAVY, size=12.8, lh=20)
    badge(cv, 730, 318, 276, 164,
          ["曲線比 45° 線平緩 ⇒ 收斂",
           "每輪誤差約縮小 3 倍",
           f"兩輪就進 5%（{K.LRB_IT[-1]['err']*100:.1f}%）",
           "",
           "考場上寫兩輪並註明",
           "收斂判準，就是完整答案。"],
          title="收斂速度", title_color=GREEN, size=12.8, lh=20)

    cv.text_px(510, 40, "迭代在做什麼：找「代進去的位移」與「算出來的位移」相等的那一點",
               17.5, NAVY, weight="700")
    cv.text_px(510, 66, "橘色折線就是考卷上那張迭代表格的幾何版本", 13, C["muted"])
    cv.text_px(510, 532,
               "攔錯：只算一輪就把 D 當答案。第一輪的 20 cm 與定案差 "
               f"{abs(20-R_L['D'])/R_L['D']*100:.0f}%，位移檢核會整個失真。",
               13.5, C["muted"])
    cv.save(P + "8-iteration.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 9　阻尼折減係數 B1 的內插
# ══════════════════════════════════════════════════════════════════
def fig9():
    cv = canvas(1020, 540)
    pl = Plot(cv, 100, 112, 640, 326, (0, 0.52), (0.6, 3.1))
    pl.frame(xticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5],
             yticks=[1.0, 1.5, 2.0, 2.5, 3.0],
             xlabel="等效阻尼比 ξeq", ylabel="阻尼比修正係數 B",
             xfmt="{:.0%}", yfmt="{:.1f}")
    pl.curve(list(zip(K.XI_TAB, K.B1_TAB)), GREEN, 2.8)
    pl.curve(list(zip(K.XI_TAB, K.BS_TAB)), PURPLE, 2.4, dash="7 5")
    for x, y in zip(K.XI_TAB, K.B1_TAB):
        pl.dot((x, y), 4.0, GREEN)

    for xi, b, col, nm, dx, dy, anc in [
            (R_L["xi"], R_L["B1"], BLUE, "LRB", -14, 26, "end"),
            (R_F["xi"], R_F["B1"], ORANGE, "FPS", 14, -14, "start")]:
        pl.vline(xi, col, 1.6, "5 5", y=b)
        pl.seg((0, b), (xi, b), col, 1.6, dash="5 5")
        pl.dot((xi, b), 6.0, col)
        pl.tag((xi, b), f"{nm}　ξ = {pct(xi)} ⇒ B1 = {b:.3f}", 13, col,
               dx=dx, dy=dy, anchor=anc)

    cv.legend(770, 140, [(GREEN, "B1（長週期段）"),
                         (PURPLE, "BS（短週期段）")])
    badge(cv, 762, 186, 244, 152,
          ["隔震後 T 落在 2～4 s，",
           "屬於長週期段，一律查 B1。",
           "",
           "查成 BS 會把力低估：",
           f"ξ = {pct(R_L['xi'])} 時 BS = "
           f"{K.BS(R_L['xi']):.2f}，",
           f"比 B1 大 {(K.BS(R_L['xi'])/R_L['B1']-1)*100:.0f}%。"],
          title="為什麼查 B1 不是 BS", title_color=RED, size=12.5, lh=20)
    badge(cv, 762, 352, 244, 100,
          [f"20% → 1.50",
           f"30% → 1.70",
           f"{pct(R_L['xi'])} → 1.50 + 0.20 × "
           f"{(R_L['xi']-0.20)/0.10:.3f}"],
          title="線性內插怎麼做", title_color=NAVY, size=12.5, lh=20)

    cv.text_px(510, 40, "阻尼比不是 5% 時，力與位移要「同時」除以 B1",
               17.5, NAVY, weight="700")
    cv.text_px(510, 66, "表列值之間一律線性內插，不可四捨五入到最近的表列阻尼比",
               13, C["muted"])
    cv.text_px(510, 508,
               "攔錯：只把力折減、忘了位移也要折減（或反過來）。兩者來自同一張譜，必須一致。",
               13.5, C["muted"])
    cv.save(P + "9-b1-interp.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 10　LRB 與 FPS 四項指標對照
# ══════════════════════════════════════════════════════════════════
def fig10():
    metrics = [
        ("有效週期 Teff", R_L["Teff"], R_F["Teff"], "s", "{:.2f}"),
        ("設計位移 D", R_L["D"], R_F["D"], "cm", "{:.1f}"),
        ("等效阻尼比 ξeq", R_L["xi"] * 100, R_F["xi"] * 100, "%", "{:.1f}"),
        ("基底剪力比 V/W", R_L["VW"] * 100, R_F["VW"] * 100, "%", "{:.2f}"),
    ]
    cv = canvas(1020, 520)
    cv.text_px(510, 40, "同一棟建築、同一張譜：LRB 與 FPS 各自付出什麼、換到什麼",
               17.5, NAVY, weight="700")
    cv.text_px(510, 66, "力幾乎打平，差別在位移與阻尼的來源", 13, C["muted"])
    x0, bw = 330, 420
    for i, (name, a, b, unit, fmt) in enumerate(metrics):
        y = 130 + i * 92
        peak = max(a, b) * 1.18
        cv.text_px(66, y + 4, name, 14.5, NAVY, "start", weight="700")
        for j, (v, col, nm) in enumerate([(a, BLUE, "LRB"), (b, ORANGE, "FPS")]):
            yy = y - 18 + j * 34
            cv.rect_px(x0, yy - 13, bw, 26, "#EDF1F6", 6)
            cv.rect_px(x0, yy - 13, bw * v / peak, 26, col, 6)
            cv.text_px(x0 - 10, yy, nm, 12.5, col, "end", weight="700")
            cv.text_px(x0 + bw * v / peak + 12, yy, fmt.format(v) + " " + unit,
                       13, col, "start", weight="700")
        cv.line((60, cv.h - (y - 46)), (960, cv.h - (y - 46)), C["border"], 1)

    badge(cv, 60, 470, 900, 40,
          ["FPS 位移較小、阻尼較高（摩擦），但摩擦係數對溫度與速度敏感；"
           "LRB 阻尼較穩定，代價是位移大 3 cm、支承要做得更大。"],
          size=13, color=C["muted"])
    cv.save(P + "10-lrb-vs-fps.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 11　速度型阻尼器的 90° 相位差
# ══════════════════════════════════════════════════════════════════
def fig11():
    cv = canvas(1020, 560)
    pl = Plot(cv, 96, 130, 700, 320, (0, 2.0), (-1.35, 1.35))
    pl.frame(xticks=[0, 0.5, 1.0, 1.5, 2.0], yticks=[-1, 0, 1],
             xlabel="時間 t / T（一個週期）", ylabel="正規化幅值",
             xfmt="{:g}", yfmt="{:g}")
    # 全部以「彈性力峰值 = 1」正規化：阻尼力峰值即 2ξd，合力為兩者的向量和
    r = 2 * FVD.dxi                      # cω/k = 2ξd = 0.30
    amp = math.sqrt(1 + r ** 2)
    ph = math.atan(r)
    pl.curve(sampled(lambda t: math.sin(2 * math.pi * t), 0, 2.0), BLUE, 2.8)
    pl.curve(sampled(lambda t: r * math.cos(2 * math.pi * t), 0, 2.0), RED, 2.6,
             dash="8 5")
    pl.curve(sampled(lambda t: amp * math.sin(2 * math.pi * t + ph), 0, 2.0),
             GREEN, 2.4, dash="2 5")
    for t in (0.25, 0.75):
        pl.vline(t, C["border"], 1.4, "4 4")
        pl.dot((t, math.sin(2 * math.pi * t)), 5.2, BLUE)
        pl.dot((t, r * math.cos(2 * math.pi * t)), 5.2, RED)
    pl.tag((0.25, 1.0), "位移（彈性力）最大", 12.5, BLUE, dy=-16)
    pl.tag((0.25, 0.0), "此刻阻尼力恰為 0", 12.5, RED, dx=10, dy=-10,
           anchor="start")
    pl.tag((0.0, r), f"阻尼力峰值 = 2ξd = {r:.2f}", 12.5, RED, dx=8, dy=-12,
           anchor="start")
    pl.tag((1.25 - ph / (2 * math.pi), amp), f"合力峰值 = {amp:.3f}", 12.5,
           GREEN, dy=-14)

    cv.legend(822, 160, [(BLUE, "位移 u(t)（＝彈性力）"),
                         (RED, "阻尼力 C·u̇"),
                         (GREEN, "合力")])
    badge(cv, 816, 236, 192, 118,
          [f"直接相加：1 + {r:.2f} = {1+r:.2f}",
           f"實際峰值：√(1+{r:.2f}²) = {amp:.3f}",
           f"高估 {(1+r)/amp-1:.0%}"],
          title="為什麼不能相加", title_color=RED, size=12.5, lh=21)
    badge(cv, 816, 366, 192, 116,
          ["最大位移", "最大速度（剪力）", "最大加速度",
           "三者各檢核一次取包絡"],
          title="三個設計狀態", title_color=GREEN, size=12.5, lh=20)

    cv.text_px(510, 42, "速度型阻尼器與彈性力差 90°：不能把兩個峰值直接相加",
               17.5, NAVY, weight="700")
    cv.text_px(510, 68, "這也是 FVD 「只加阻尼、不加勁度」的物理根據——它在最大位移時完全不出力",
               13, C["muted"])
    cv.text_px(510, 508,
               f"斜撐角 θ = {FVD.theta:.0f}° 時有效阻尼要乘 cos²θ = {FVD.cos2:.2f}"
               f"（力投影一次、位移投影一次），"
               f"本案例 C = {FVD.C:.1f} tf·s/cm 才換到 Δξ = {FVD.dxi:.0%}。",
               13.5, C["muted"])
    cv.save(P + "11-fvd-phase.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 12　BRB 左移 vs FVD 下移
# ══════════════════════════════════════════════════════════════════
def fig12():
    a = canvas(510, 470)
    a.panel("速度型 FVD：垂直往下", "週期不變，Sa 乾淨地被 B1 折減")
    pa = Plot(a, 74, 142, 392, 226, (0, 1.6), (0, 0.95))
    pa.frame(xticks=[0, 0.4, 0.8, 1.2, 1.6], yticks=[0, 0.3, 0.6, 0.9],
             xlabel="T (s)", ylabel="Sa (g)", xfmt="{:g}", yfmt="{:.1f}")
    pa.curve(sampled(K.Sa, 0.05, 1.6), NAVY, 2.4)
    pa.curve(sampled(lambda t: K.Sa(t) / FVD.B1v, 0.05, 1.6), GREEN, 2.2,
             dash="7 5")
    pa.dot((K.T_FIX, FIX["Sa"]), 5.4, RED)
    pa.dot((FVD.T, FVD.Sa_), 5.6, GREEN)
    pa.arrow((K.T_FIX, FIX["Sa"]), (FVD.T, FVD.Sa_), GREEN, 2.8, 10)
    pa.tag((FVD.T, FVD.Sa_), f"{FVD.Sa_:.3f} g", 12.5, GREEN, dx=10, dy=4,
           anchor="start")
    a.text_px(255, 404, f"力 {FVD.V/FIX['V']-1:+.0%}　位移 "
                        f"{FVD.D/FIX['D']-1:+.0%}", 14, GREEN, weight="700")
    a.text_px(255, 430, f"V = {FVD.V:,.0f} tf、D = {f1(FVD.D)} cm", 12.5,
              C["muted"])

    b = canvas(510, 470)
    b.panel("位移型 BRB：先往左、再往下", "加勁度使 T 縮短，Sa 反而先變大")
    pb = Plot(b, 74, 142, 392, 226, (0, 1.6), (0, 0.95))
    pb.frame(xticks=[0, 0.4, 0.8, 1.2, 1.6], yticks=[0, 0.3, 0.6, 0.9],
             xlabel="T (s)", ylabel="Sa (g)", xfmt="{:g}", yfmt="{:.1f}")
    pb.curve(sampled(K.Sa, 0.05, 1.6), NAVY, 2.4)
    pb.curve(sampled(lambda t: K.Sa(t) / BRB.B1v, 0.05, 1.6), PURPLE, 2.2,
             dash="7 5")
    pb.dot((K.T_FIX, FIX["Sa"]), 5.4, RED)
    pb.arrow((K.T_FIX, FIX["Sa"]), (BRB.T, K.Sa(BRB.T)), RED, 2.8, 10)
    pb.dot((BRB.T, K.Sa(BRB.T)), 5.4, RED)
    pb.arrow((BRB.T, K.Sa(BRB.T)), (BRB.T, BRB.Sa_), PURPLE, 2.8, 10)
    pb.dot((BRB.T, BRB.Sa_), 5.6, PURPLE)
    pb.tag((BRB.T, K.Sa(BRB.T)), f"{K.Sa(BRB.T):.3f} g", 12.5, RED, dx=-10,
           dy=-10, anchor="end")
    pb.tag((BRB.T, BRB.Sa_), f"{BRB.Sa_:.3f} g", 12.5, PURPLE, dx=10, dy=6,
           anchor="start")
    b.text_px(255, 404, f"力 {BRB.V/FIX['V']-1:+.0%}　位移 "
                        f"{BRB.D/FIX['D']-1:+.0%}", 14, PURPLE, weight="700")
    b.text_px(255, 430, f"V = {BRB.V:,.0f} tf、D = {f1(BRB.D)} cm", 12.5,
              C["muted"])

    compose([a, b],
            title="加了阻尼器不等於力一定變小：先看它有沒有同時改變勁度",
            sub=f"同一棟建築加 {BRB.ratio:.0%} 勁度的 BRB，週期由 {K.T_FIX} s "
                f"縮到 {f2(BRB.T)} s，5% 譜加速度反而由 {FIX['Sa']:.3f} g "
                f"漲到 {K.Sa(BRB.T):.3f} g",
            note=f"淨效益：FVD 力少 {1-FVD.V/FIX['V']:.0%}、位移少 "
                 f"{1-FVD.D/FIX['D']:.0%}；BRB 力只少 {1-BRB.V/FIX['V']:.0%}、"
                 f"位移卻少 {1-BRB.D/FIX['D']:.0%}。要控制變形選 BRB，"
                 f"要降低構件力選 FVD。",
            path=P + "12-brb-vs-fvd.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 13　TMD 的雙峰與最佳調頻
# ══════════════════════════════════════════════════════════════════
def fig13():
    cv = canvas(1020, 560)
    pl = Plot(cv, 98, 116, 660, 330, (0.7, 1.3), (0, 14))
    pl.frame(xticks=[0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
             yticks=[0, 4, 8, 12],
             xlabel="激振頻率比 β = ω / ω_{n}",
             ylabel="位移動力放大率 |X1 / Xst|",
             xfmt="{:.1f}", yfmt="{:g}")

    bs = [0.7 + 0.6 * i / 600 for i in range(601)]
    # 無 TMD 的主結構（ξ = 2%）
    pl.curve_clip([(b, 1 / math.sqrt((1 - b ** 2) ** 2 + (2 * 0.02 * b) ** 2))
                   for b in bs], RED, 2.2, dash="8 4")
    for xid, col, w, dash in [(0.004, C["muted"], 2.0, "4 5"),
                              (0.40, PURPLE, 2.0, "2 5"),
                              (TMD.xi_opt, GREEN, 3.2, None)]:
        pl.curve_clip([(b, K.tmd_response(b, xid=xid)) for b in bs], col, w, dash)

    # 調頻點的反力抵消（無阻尼 TMD 在 β = f_opt 處 X1 → 0）
    f = TMD.f_opt
    pl.vline(f, C["border"], 1.4, "4 4")
    pl.dot((f, K.tmd_response(f, xid=0.004)), 5.6, ORANGE)
    pl.tag((f, 0), "調頻點 β = f_{opt}", 13, ORANGE, dx=-10, dy=-56,
           anchor="end")
    pl.tag((f, 0), "無阻尼時 X1 → 0（反力完全抵消）", 12, C["muted"],
           dx=-10, dy=-36, anchor="end", weight="400")
    # 等高雙峰
    for bpk in (0.9277, 1.0426):
        pl.dot((bpk, TMD.Rpeak), 5.2, GREEN)
    pl.tag((0.9277, TMD.Rpeak), "雙峰等高", 13, GREEN, dx=-14, dy=-26,
           anchor="end")
    pl.tag((1.0426, TMD.Rpeak), f"高度 √(1+2/μ) = {TMD.Rpeak:.1f}", 13, GREEN,
           dx=14, dy=-26, anchor="start")

    cv.legend(784, 132, [(RED, "無 TMD（ξ = 2%）"),
                         (C["muted"], "TMD 阻尼趨近於零"),
                         (GREEN, f"最佳阻尼 ξd = {TMD.xi_opt:.1%}"),
                         (PURPLE, "TMD 阻尼過大（鎖死）")])
    badge(cv, 778, 220, 230, 136,
          [f"μ = md/M = {TMD.mu}",
           f"f_{{opt}} = 1/(1+μ) = {TMD.f_opt:.4f}",
           f"Td = {TMD.Td:.3f} s、md 重 {TMD.Wd_:.0f} tf",
           f"ξ_{{opt}} = √(3μ/8(1+μ)) = {TMD.xi_opt:.1%}"],
          title="Den Hartog 最佳解", title_color=GREEN, size=12.5, lh=21)
    badge(cv, 778, 372, 230, 110,
          [f"雙峰高度 = √(1+2/μ) = {TMD.Rpeak:.1f}",
           f"折算等效阻尼僅約 {TMD.xi_eq:.1%}",
           f"質量塊行程約主結構的 {TMD.stroke:.1f} 倍"],
          title="量級感", title_color=RED, size=12.5, lh=21)

    cv.text_px(510, 40, "TMD 的兩件事：調頻點反力抵消，再用阻尼把分裂出的雙峰壓到等高",
               17.5, NAVY, weight="700")
    cv.text_px(510, 66,
               "阻尼為零時抵消最乾淨，卻換來兩個無窮大的新共振峰；最佳阻尼是拿深谷去換低峰",
               13, C["muted"])
    cv.text_px(510, 522,
               f"攔錯：以為 TMD 對地震也像對風一樣有效。3% 質量比只折算到約 "
               f"{TMD.xi_eq:.0%} 等效阻尼，遠不如隔震的 {pct(R_L['xi'])}，"
               f"且寬頻地震波不一定落在調頻點上。",
               13.5, C["muted"])
    cv.save(P + "13-tmd-peaks.svg")


# ══════════════════════════════════════════════════════════════════
# 圖 14　五個方案的「力—位移」取捨地圖 ＋ 三把量級尺
# ══════════════════════════════════════════════════════════════════
def fig14():
    a = canvas(560, 520)
    a.panel("取捨地圖：往左下走才是真的變好", "橫軸位移、縱軸力，同一棟建築五個方案")
    pa = Plot(a, 86, 118, 424, 306, (0, 22), (0, 0.68))
    pa.frame(xticks=[0, 5, 10, 15, 20], yticks=[0, 0.2, 0.4, 0.6],
             xlabel="位移需求 (cm)", ylabel="V / W", yfmt="{:.1f}")
    pts = [("未處理", FIX["D"], FIX["Sa"], RED, 10, -10, "start"),
           ("FVD", FVD.D, FVD.V / K.W, GREEN, 10, -10, "start"),
           ("BRB", BRB.D, BRB.V / K.W, PURPLE, -10, -10, "end"),
           ("LRB 隔震", R_L["D"], R_L["VW"], BLUE, 8, -14, "end"),
           ("FPS 隔震", R_F["D"], R_F["VW"], ORANGE, -8, 20, "end")]
    for nm, d, v, col, dx, dy, anc in pts:
        pa.dot((d, v), 6.4, col)
        pa.tag((d, v), nm, 12.5, col, dx=dx, dy=dy, anchor=anc)
    a.text_px(280, 462, "隔震把「力」打到另一個量級；消能主要在收位移", 13,
              C["muted"])
    a.text_px(280, 486, "BRB 位移最小但力幾乎沒降；FVD 兩者都改善但幅度有限",
              12.5, C["muted"])

    b = canvas(560, 520)
    b.panel("三把量級尺：算完先量一次", "落在灰帶內才合理")
    bands = [("有效週期 Teff", 2.0, 4.0, 0.0, 5.0, "s",
              [("LRB", R_L["Teff"], BLUE), ("FPS", R_F["Teff"], ORANGE)]),
             ("隔震層設計位移 D", 15.0, 40.0, 0.0, 50.0, "cm",
              [("LRB", R_L["D"], BLUE), ("FPS", R_F["D"], ORANGE)]),
             ("等效阻尼比 ξeq", 0.10, 0.30, 0.0, 0.45, "",
              [("LRB", R_L["xi"], BLUE), ("FPS", R_F["xi"], ORANGE)])]
    for i, (nm, lo, hi, a0, a1, unit, marks) in enumerate(bands):
        y = 158 + i * 112
        b.text_px(48, y - 58, nm, 14, NAVY, "start", weight="700")
        x0, bw = 48, 464
        b.rect_px(x0, y, bw, 26, "#EDF1F6", 6)
        b.rect_px(x0 + bw * (lo - a0) / (a1 - a0), y,
                  bw * (hi - lo) / (a1 - a0), 26, "rgba(46,125,111,0.20)", 6)
        fmt = (lambda v: f"{v:.0%}") if unit == "" else (lambda v: f"{v:g}")
        b.text_px(x0 + bw * (lo - a0) / (a1 - a0), y + 42, fmt(lo), 12,
                  C["muted"])
        b.text_px(x0 + bw * (hi - a0) / (a1 - a0), y + 42,
                  fmt(hi) + ("" if unit == "" else f" {unit}"), 12, C["muted"])
        for j, (mn, mv, col) in enumerate(marks):
            X = x0 + bw * (mv - a0) / (a1 - a0)
            b.line((X, b.h - y), (X, b.h - (y + 26)), col, 3.4)
            val = f"{mv:.0%}" if unit == "" else f"{mv:.2f}"
            b.text_px(X, y - 34 + j * 20, f"{mn} {val}", 12, col,
                      weight="700")
    b.text_px(280, 486, "超出灰帶不代表一定錯，但一定要說得出理由", 12.5,
              C["muted"])

    compose([a, b],
            title="收尾：先看取捨地圖選對工具，再用三把尺檢查數量級",
            sub="所有座標值都由 case.py 的同一組常數算出，改一個參數整張圖跟著動",
            note="T 小於 1.2 s 表示隔震層太硬、大於 6 s 多半算錯；"
                 "D 只有 5 cm 表示根本沒隔震到，超過 1 m 是公式代錯。",
            path=P + "14-scheme-map.svg")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8,
              fig9, fig10, fig11, fig12, fig13, fig14):
        f()
        print("ok", f.__name__)
