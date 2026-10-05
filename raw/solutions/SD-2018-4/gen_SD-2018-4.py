"""SD-2018-4 圖解產生腳本（struct-diagram）。所有數值由題目條件與 §4 公式算出，可重跑。"""
import sys, os, math
SKILL = os.environ.get("STRUCT_DIAGRAM_SCRIPTS",
    "/root/.claude/skills/synced/6983ec08-a01a-44e4-a131-56c9e592c524_ab4f317b-1625-4c71-b32d-871e33fbc9cc/struct-diagram/scripts")
sys.path.insert(0, SKILL)
from structdraw import Canvas, C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figs")

# ── 題目條件（§1）──
D, A, G = 25.0, 0.08, 980.0                 # cm, ×g, cm/s²
SA_C, SA_MAX = 0.48, 0.8                    # Sa = 0.48/T ≤ 0.8
TABLE = [(2, .80), (5, 1.00), (10, 1.25), (20, 1.50), (30, 1.63), (40, 1.70), (50, 1.75)]
# ── §4 Step 2–7 ──
TE = 2*math.pi*math.sqrt(D/(A*G))           # 3.548 s
T_STAR = SA_C/SA_MAX                        # 0.6 s
SA = min(SA_C/TE, SA_MAX)                   # 0.1353
B = G/(4*math.pi**2)*SA*TE**2/D             # 1.691
def xi_of_B(b):
    for (x0, b0), (x1, b1) in zip(TABLE, TABLE[1:]):
        if b0 <= b <= b1: return x0 + (x1-x0)*(b-b0)/(b1-b0)
XI = xi_of_B(B)                             # 38.7 %
MU = math.pi*A*(XI/100)/2                   # 0.0487
DR = A - MU                                 # D/R = 0.0313
R = D/DR                                    # 798 cm

def frame(W, H, L, Rm, T, Bm, xr, yr):
    cv = Canvas(W, H, sx=1, ox=0, oy=0, bg="#FFFFFF")
    fx = lambda x: L + (x-xr[0])/(xr[1]-xr[0])*(W-L-Rm)
    fy = lambda y: Bm + (y-yr[0])/(yr[1]-yr[0])*(H-T-Bm)
    mm = lambda p: (fx(p[0]), fy(p[1]))
    return cv, mm, (lambda p: cv.P(mm(p)))

# ════ 圖 2：FPS 遲滯迴圈 ════
def fig_hysteresis():
    W, H = 760, 560
    ymax = A*1.35
    cv, m, P = frame(W, H, 80, 170, 80, 60, (-D*1.25, D*1.25), (-ymax, ymax))
    cv.text_px(W/2, 34, "圖 2　FPS 力–位移遲滯迴圈（設計位移 D 時）", 17, C["text"], weight="700")
    loop = [(-D, -DR-MU), (-D, -DR+MU), (D, DR+MU), (D, DR-MU), (-D, -DR-MU)]
    cv.polygon([m(p) for p in loop], C["fill_m"], C["bmd"], 2.6)
    cv.arrow(m((-D*1.22, 0)), m((D*1.22, 0)), C["muted"], 1.8, 9)
    cv.arrow(m((0, -ymax*0.98)), m((0, ymax*0.98)), C["muted"], 1.8, 9)
    x, y = P((D*1.22, 0)); cv.math_px(x+8, y, "u", 15, C["muted"], "start")
    x, y = P((0, ymax*0.98)); cv.text_px(x-10, y, "F/W", 14, C["muted"], "end", italic=True)
    # 單擺勁度線（無摩擦）
    cv.line(m((-D*1.1, -DR*1.1)), m((D*1.1, DR*1.1)), C["ghost"], 2, dash="6 5")
    # 割線勁度 K_eff
    cv.line(m((0, 0)), m((D, A)), C["deform"], 2.4, dash="8 5")
    x, y = P((D*0.45, A*0.45)); cv.math_px(x-10, y-14, "K_{eff}", 14, C["deform"], "end", weight="700")
    # 摩擦截距 μ
    x0, y0 = P((0, MU)); cv.dot(m((0, MU)), 5, fill=C["load"])
    cv.math_px(x0-10, y0-12, f"μ = {MU:.4f}", 13.5, C["load"], "end", weight="700")
    # 峰值點
    xp, yp = P((D, A)); cv.dot(m((D, A)), 5.5, fill=C["accent"])
    cv.math_px(xp+32, yp-4, f"A = D/R + μ = {A:.3f}", 14, C["accent"], "start", weight="700")
    # D/R 與 μ 分解（在 u=D 右側）
    xb = xp + 22
    _, y_dr = P((D, DR)); _, y0b = P((D, 0))
    cv.parts.append(f'<line x1="{xb}" y1="{y0b}" x2="{xb}" y2="{y_dr}" stroke="{C["member2"]}" stroke-width="5"/>')
    cv.parts.append(f'<line x1="{xb}" y1="{y_dr}" x2="{xb}" y2="{yp}" stroke="{C["load"]}" stroke-width="5"/>')
    cv.math_px(xb+10, (y0b+y_dr)/2, f"D/R = {DR:.4f}", 13, C["member2"], "start", weight="700")
    cv.math_px(xb+10, (y_dr+yp)/2+6, "μ", 13, C["load"], "start", weight="700")
    # D 標示
    xd, yd = P((D, 0)); cv.text_px(xd+8, yd+40, f"D = {D:g} cm", 13, C["text"], "start", weight="700")
    xd, yd = P((-D, 0)); cv.text_px(xd-8, yd+18, "−D", 13, C["text"], "end")
    # 斜率標示
    x, y = P((-D*0.55, -DR*0.55-MU))
    cv.text_px(x, y+26, f"斜率 1/R（R = {R/100:.2f} m）", 13, C["bmd"], weight="700")
    # 面積
    x, y = P((-D*0.5, 0.0)); cv.text_px(x, y-24, "面積 = 4μWD", 13, C["bmd"], weight="700")
    cv.text_px(W/2, H-22, f"迴圈頂點即最大傳遞力 W(D/R+μ)；割線 K_{{eff}} = W(1/R+μ/D) 決定 T_e = {TE:.3f} s", 13, C["muted"])
    cv.save(os.path.join(OUT, "SD-2018-4-fig-2-hysteresis.svg"))

# ════ 圖 3：設計反應譜 ════
def fig_spectrum():
    W, H = 760, 460
    cv, m, P = frame(W, H, 80, 60, 80, 70, (0, 4.5), (0, 0.95))
    cv.text_px(W/2, 34, "圖 3　設計譜加速度係數與等效週期位置", 17, C["text"], weight="700")
    cv.arrow(m((0, 0)), m((4.5, 0)), C["muted"], 1.8, 9)
    cv.arrow(m((0, 0)), m((0, 0.95)), C["muted"], 1.8, 9)
    for t in range(0, 5):
        x, y = P((t, 0)); cv.text_px(x, y+18, f"{t}", 12, C["muted"])
    for s in (0.2, 0.4, 0.6, 0.8):
        x, y = P((0, s)); cv.text_px(x-8, y, f"{s:.1f}", 12, C["muted"], "end")
    x, y = P((4.5, 0)); cv.text_px(x+6, y-16, "T (s)", 13, C["muted"], "end", italic=True)
    x, y = P((0, 0.95)); cv.math_px(x+10, y+4, "S_{a}", 14, C["muted"], "start")
    pts = [(0, SA_MAX), (T_STAR, SA_MAX)] + [(T_STAR + i*(4.4-T_STAR)/120, SA_C/(T_STAR + i*(4.4-T_STAR)/120)) for i in range(121)]
    cv.poly([m(p) for p in pts], C["bmd"], 3)
    # 轉折點
    x, y = P((T_STAR, SA_MAX)); cv.dot(m((T_STAR, SA_MAX)), 5, fill=C["bmd"])
    cv.text_px(x+10, y-12, f"T* = 0.48/0.8 = {T_STAR:.1f} s", 13, C["bmd"], "start", weight="700")
    # Te
    xt, yt = P((TE, SA))
    cv.line(m((TE, 0)), m((TE, SA)), C["accent"], 1.6, dash="5 4")
    cv.line(m((0, SA)), m((TE, SA)), C["accent"], 1.6, dash="5 4")
    cv.dot(m((TE, SA)), 6, fill=C["accent"])
    cv.text_px(xt, P((TE, 0))[1]+44, f"T_e = {TE:.3f} s", 13.5, C["accent"], weight="700")
    cv.text_px(xt+10, yt-16, f"S_a = 0.48/T_e = {SA:.4f}", 13.5, C["accent"], "start", weight="700")
    # 誤用 0.8
    cv.line(m((T_STAR, SA_MAX)), m((4.4, SA_MAX)), C["load"], 1.6, dash="3 5")
    x, y = P((4.4, SA_MAX)); cv.text_px(x, y-12, f"誤用 S_a = 0.8（高估約 {SA_MAX/SA:.1f} 倍）", 13, C["load"], "end")
    cv.save(os.path.join(OUT, "SD-2018-4-fig-3-spectrum.svg"))
    return SA_MAX/SA

# ════ 圖 4：ξe–B 插值 ════
def fig_xi_b():
    W, H = 760, 480
    cv, m, P = frame(W, H, 80, 60, 80, 70, (0, 55), (0.7, 1.85))
    cv.text_px(W/2, 34, "圖 4　由 B 反查等效阻尼比（線性內插）", 17, C["text"], weight="700")
    cv.arrow(m((0, 0.7)), m((55, 0.7)), C["muted"], 1.8, 9)
    cv.arrow(m((0, 0.7)), m((0, 1.85)), C["muted"], 1.8, 9)
    for xx in range(0, 51, 10):
        x, y = P((xx, 0.7)); cv.text_px(x, y+18, f"{xx}", 12, C["muted"])
    for b in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
        x, y = P((0, b)); cv.text_px(x-8, y, f"{b:.1f}", 12, C["muted"], "end")
    x, y = P((55, 0.7)); cv.text_px(x+6, y-16, "ξe (%)", 13, C["muted"], "end", italic=True)
    x, y = P((0, 1.85)); cv.math_px(x+10, y+4, "B", 14, C["muted"], "start")
    cv.poly([m(p) for p in TABLE], C["bmd"], 2.6)
    for p in TABLE:
        cv.dot(m(p), 4.5, fill=C["bmd"])
    for p in TABLE[4:6]:
        x, y = P(p); cv.text_px(x, y+(18 if p[0] == 30 else -14), f"({p[0]}%, {p[1]:.2f})", 12, C["bmd"], weight="700")
    # B 橫線 → ξ
    xq, yq = P((XI, B))
    cv.line(m((0, B)), m((XI, B)), C["accent"], 1.6, dash="5 4")
    cv.line(m((XI, 0.7)), m((XI, B)), C["accent"], 1.6, dash="5 4")
    cv.dot(m((XI, B)), 6, fill=C["accent"])
    x, y = P((0, B)); cv.text_px(x+8, y-12, f"B = {B:.3f}", 13.5, C["accent"], "start", weight="700")
    x, y = P((XI, 0.7)); cv.text_px(x-8, y-14, f"ξe = {XI:.1f}%", 13.5, C["accent"], "end", weight="700")
    cv.text_px(W/2, H-22, f"取最近值 40% 會使 μ 偏大約 {(0.40/(XI/100)-1)*100:.0f}%；B 落在 1.63–1.70 之間就要內插", 13, C["muted"])
    cv.save(os.path.join(OUT, "SD-2018-4-fig-4-xi-b.svg"))

if __name__ == "__main__":
    print(f"Te={TE:.4f} Sa={SA:.4f} B={B:.4f} xi={XI:.2f}% mu={MU:.5f} D/R={DR:.5f} R={R:.1f}cm")
    fig_hysteresis(); r = fig_spectrum(); fig_xi_b()
    print("Sa高估倍數", r)
