#!/usr/bin/env python3
"""SD-U3-2 隔減震原理 —— 示範案例的唯一數值來源。

全篇（gen_figs.py 與 deck.js）的每一個數字都必須 import 自本檔，
改一個常數 → 所有圖與文案一起變。單獨執行會印出完整對帳表。

單位系統：tf（公噸力）、cm、s、g = 981 cm/s²
"""
import math

G = 981.0                      # cm/s²

# ────────────────────────────────────────────────────────────
# 一、示範建築（LRB 與 FPS 共用同一棟）
# ────────────────────────────────────────────────────────────
W      = 12000.0               # 上部結構總重 (tf)
M      = W / G                 # 質量 (tf·s²/cm)
T_FIX  = 0.80                  # 固定基礎（未隔震）基本週期 (s)
K_SUP  = M * (2 * math.pi / T_FIX) ** 2   # 上部結構側向勁度 (tf/cm)

# ────────────────────────────────────────────────────────────
# 二、設計反應譜（等加速度段 + 等速度段，5% 阻尼）
#     S_a(T) = S_DS            T <= T0
#            = S_D1 / T        T >  T0        （S_a 單位：g）
# ────────────────────────────────────────────────────────────
S_DS = 0.80                    # 短週期設計譜加速度係數 (g)
T0   = 0.60                    # 轉角週期 (s)
S_D1 = S_DS * T0               # = 0.48 g·s（等速度段常數）


def Sa(T):
    """5% 阻尼設計譜加速度係數（g）。"""
    return S_DS if T <= T0 else S_D1 / T


def Sd(T, B1=1.0):
    """由譜加速度回推譜位移 (cm)：D = g·S_a·T²/(4π²B₁)。"""
    return Sa(T) * G * T ** 2 / (4 * math.pi ** 2 * B1)


# 阻尼比修正係數（建築物耐震設計規範，表列值 + 線性內插）
XI_TAB = [0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
B1_TAB = [0.80, 1.00, 1.20, 1.50, 1.70, 1.90, 2.00]   # 長週期段（隔震用）
BS_TAB = [0.80, 1.00, 1.30, 1.80, 2.30, 2.70, 3.00]   # 短週期段


def _interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])


def B1(xi):
    return _interp(xi, XI_TAB, B1_TAB)


def BS(xi):
    return _interp(xi, XI_TAB, BS_TAB)


def T_eff(Keff):
    """有效振動週期 (s)：T = 2π√(m/K) = 2π√(W/(gK))。"""
    return 2 * math.pi * math.sqrt(M / Keff)


# ────────────────────────────────────────────────────────────
# 三、LRB 鉛心橡膠支承（雙線性）
# ────────────────────────────────────────────────────────────
class LRB:
    Qd    = 600.0              # 特徵強度（迴圈在 D=0 的截距）tf  = 0.05W
    kd    = 50.0               # 降伏後勁度 tf/cm
    alpha = 0.10               # kd / k0
    k0    = kd / alpha         # 初始（彈性）勁度 = 500 tf/cm
    Fy    = Qd / (1 - alpha)   # 降伏力 tf
    Dy    = Fy / k0            # 降伏位移 cm

    @classmethod
    def F(cls, D):
        """雙線性骨幹曲線的最大回復力 (tf)。"""
        return cls.Qd + cls.kd * D if D > cls.Dy else cls.k0 * D

    @classmethod
    def Keff(cls, D):
        """割線（有效）勁度 tf/cm。"""
        return cls.Qd / D + cls.kd

    @classmethod
    def Wd(cls, D):
        """一圈遲滯迴圈面積 tf·cm —— 平行四邊形，必須扣掉 D_y。"""
        return 4 * cls.Qd * (D - cls.Dy)

    @classmethod
    def xi(cls, D):
        return cls.Wd(D) / (2 * math.pi * cls.Keff(D) * D ** 2)


# ────────────────────────────────────────────────────────────
# 四、FPS 摩擦單擺支承
# ────────────────────────────────────────────────────────────
class FPS:
    R  = 220.0                 # 曲率半徑 cm
    mu = 0.06                  # 摩擦係數

    T_pendulum = 2 * math.pi * math.sqrt(R / G)   # 與重量完全無關

    @classmethod
    def F(cls, D):
        return W * D / cls.R + cls.mu * W

    @classmethod
    def Keff(cls, D):
        return W / cls.R + cls.mu * W / D

    @classmethod
    def Wd(cls, D):
        """矩形迴圈面積 tf·cm。"""
        return 4 * cls.mu * W * D

    @classmethod
    def A(cls, D):
        """最大傳遞力比 F/W。"""
        return D / cls.R + cls.mu

    @classmethod
    def xi(cls, D):
        """= 2μ/(π·A)，由 Wd/(2πKeffD²) 化簡而得。"""
        return 2 * cls.mu / (math.pi * cls.A(D))


# ────────────────────────────────────────────────────────────
# 五、通用迭代（等效線性化 → 反應譜 → 新位移）
# ────────────────────────────────────────────────────────────
def iterate(dev, D0=20.0, tol=0.05, nmax=12):
    """回傳每一輪的紀錄 list[dict]，欄位與考場手算的表格一致。"""
    rows, D = [], D0
    for k in range(1, nmax + 1):
        Ke  = dev.Keff(D)
        Te  = T_eff(Ke)
        wd  = dev.Wd(D)
        xi  = dev.xi(D)
        b1  = B1(xi)
        sa  = Sa(Te)
        Dn  = sa * G * Te ** 2 / (4 * math.pi ** 2 * b1)
        err = abs(Dn - D) / D
        rows.append(dict(n=k, D=D, Keff=Ke, Teff=Te, Wd=wd, xi=xi,
                         B1=b1, Sa=sa, Dnew=Dn, err=err))
        D = Dn
        if err < tol:
            break
    return rows


def converge(dev, D0=20.0, tol=1e-6):
    """跑到數值收斂，供圖上標「定案值」。"""
    rows = iterate(dev, D0, tol=tol, nmax=200)
    r = rows[-1]
    D = r["Dnew"]
    return dict(D=D, Keff=dev.Keff(D), Teff=T_eff(dev.Keff(D)),
                xi=dev.xi(D), B1=B1(dev.xi(D)), Wd=dev.Wd(D),
                V=dev.Keff(D) * D, VW=dev.Keff(D) * D / W)


LRB_IT, FPS_IT = iterate(LRB), iterate(FPS)
LRB_R, FPS_R = converge(LRB), converge(FPS)

# 未隔震的彈性需求（同一棟建築、同一張反應譜）
FIX = dict(T=T_FIX, Sa=Sa(T_FIX), V=Sa(T_FIX) * W, D=Sd(T_FIX))

# 串聯彈簧：上部結構不是真的剛體
K_SERIES = 1 / (1 / K_SUP + 1 / LRB_R["Keff"])
T_SERIES = T_eff(K_SERIES)
SERIES_ERR = (T_SERIES - LRB_R["Teff"]) / LRB_R["Teff"]

# ────────────────────────────────────────────────────────────
# 六、消能減震（同一棟建築，未隔震）
# ────────────────────────────────────────────────────────────
class FVD:                      # 速度型：加阻尼、不加勁度
    theta = 30.0                # 斜撐與水平夾角（度）
    dxi   = 0.15                # 目標附加阻尼比
    cos2  = math.cos(math.radians(theta)) ** 2
    C     = dxi * T_FIX * K_SUP / (math.pi * cos2)   # 阻尼係數 tf·s/cm
    xi    = 0.05 + dxi
    B1v   = B1(xi)
    T     = T_FIX               # 週期完全不變
    Sa_   = Sa(T_FIX) / B1v
    V     = Sa_ * W
    D     = Sd(T_FIX, B1v)


class BRB:                      # 位移型：同時加勁度與阻尼
    ratio = 0.50                # 附加勁度 / 原結構勁度
    K     = K_SUP * (1 + ratio)
    T     = T_eff(K)
    xi    = 0.15
    B1v   = B1(xi)
    Sa_   = Sa(T) / B1v
    V     = Sa_ * W
    D     = Sd(T, B1v)


# ────────────────────────────────────────────────────────────
# 七、TMD 調頻質量阻尼器（Den Hartog 最佳解）
# ────────────────────────────────────────────────────────────
class TMD:
    mu    = 0.03
    md    = mu * M
    Wd_   = mu * W              # 質量塊重量 tf
    f_opt = 1 / (1 + mu)
    Td    = T_FIX / f_opt
    xi_opt = math.sqrt(3 * mu / (8 * (1 + mu)))
    Rpeak = math.sqrt(1 + 2 / mu)       # 最佳化後的最大動力放大倍數
    xi_eq = 1 / (2 * Rpeak)             # 折算成等效黏滯阻尼比
    stroke = 1 / (2 * xi_opt)           # 質量塊行程 / 主結構位移


def tmd_response(beta, mu=TMD.mu, f=TMD.f_opt, xid=TMD.xi_opt):
    """Den Hartog 無阻尼主結構 + TMD 的位移動力放大率 |X1/Xst|。

    ζ 以 TMD 自身的自然頻率定義（c/(2 m_d ω_d)），與 f_opt、ξ_opt 的推導一致。
    """
    b2, f2 = beta ** 2, f ** 2
    two = (2 * xid * beta) ** 2
    num = math.sqrt(two + (b2 - f2) ** 2)
    den = math.sqrt(two * (b2 - 1 + mu * b2) ** 2
                    + ((b2 - 1) * (b2 - f2) - mu * f2 * b2) ** 2)
    return num / den


if __name__ == "__main__":
    p = print
    p("=" * 74)
    p(f"示範建築  W = {W:,.0f} tf   m = {M:.3f} tf·s²/cm   "
      f"T_fix = {T_FIX} s   k_sup = {K_SUP:.1f} tf/cm")
    p(f"設計譜    S_DS = {S_DS} g   T0 = {T0} s   S_D1 = {S_D1} g·s")
    p(f"未隔震彈性需求  S_a = {FIX['Sa']:.3f} g   V = {FIX['V']:,.0f} tf "
      f"(V/W = {FIX['Sa']*100:.1f}%)   D = {FIX['D']:.2f} cm")
    p("=" * 74)

    p(f"\n【LRB】Qd = {LRB.Qd} tf (={LRB.Qd/W*100:.0f}%W)  k0 = {LRB.k0} "
      f"kd = {LRB.kd} tf/cm  α = {LRB.alpha}  Fy = {LRB.Fy:.1f} tf  "
      f"Dy = {LRB.Dy:.3f} cm")
    p(f"{'輪':>2} {'D':>7} {'Keff':>8} {'Teff':>7} {'Wd':>10} {'ξ':>7} "
      f"{'B1':>6} {'Sa':>7} {'Dnew':>7} {'誤差':>7}")
    for r in LRB_IT:
        p(f"{r['n']:>2} {r['D']:>7.2f} {r['Keff']:>8.2f} {r['Teff']:>7.3f} "
          f"{r['Wd']:>10,.0f} {r['xi']*100:>6.1f}% {r['B1']:>6.3f} "
          f"{r['Sa']:>7.4f} {r['Dnew']:>7.2f} {r['err']*100:>6.2f}%")
    p(f"定案 D = {LRB_R['D']:.2f} cm  Keff = {LRB_R['Keff']:.2f} tf/cm  "
      f"Teff = {LRB_R['Teff']:.3f} s  ξ = {LRB_R['xi']*100:.1f}%  "
      f"B1 = {LRB_R['B1']:.3f}  V = {LRB_R['V']:,.0f} tf "
      f"(V/W = {LRB_R['VW']*100:.2f}%)")
    p(f"  降幅：V 由 {FIX['V']:,.0f} → {LRB_R['V']:,.0f} tf，"
      f"剩 {LRB_R['V']/FIX['V']*100:.1f}%（{FIX['V']/LRB_R['V']:.2f} 倍）")

    p(f"\n【FPS】R = {FPS.R} cm  μ = {FPS.mu}  "
      f"單擺週期 T = 2π√(R/g) = {FPS.T_pendulum:.3f} s（與 W 無關）")
    p(f"{'輪':>2} {'D':>7} {'Keff':>8} {'Teff':>7} {'Wd':>10} {'ξ':>7} "
      f"{'B1':>6} {'Sa':>7} {'Dnew':>7} {'誤差':>7}")
    for r in FPS_IT:
        p(f"{r['n']:>2} {r['D']:>7.2f} {r['Keff']:>8.2f} {r['Teff']:>7.3f} "
          f"{r['Wd']:>10,.0f} {r['xi']*100:>6.1f}% {r['B1']:>6.3f} "
          f"{r['Sa']:>7.4f} {r['Dnew']:>7.2f} {r['err']*100:>6.2f}%")
    p(f"定案 D = {FPS_R['D']:.2f} cm  Keff = {FPS_R['Keff']:.2f} tf/cm  "
      f"Teff = {FPS_R['Teff']:.3f} s  ξ = {FPS_R['xi']*100:.1f}%  "
      f"A = D/R+μ = {FPS.A(FPS_R['D']):.4f}  V = {FPS_R['V']:,.0f} tf "
      f"(V/W = {FPS_R['VW']*100:.2f}%)")

    p(f"\n【串聯彈簧】k_b = {LRB_R['Keff']:.2f}  k_sup = {K_SUP:.1f}  "
      f"k_eq = {K_SERIES:.2f} tf/cm  →  T = {T_SERIES:.3f} s "
      f"（比剛體假設長 {SERIES_ERR*100:.1f}%）  k_b/k_sup = "
      f"{LRB_R['Keff']/K_SUP:.3f}")

    p(f"\n【FVD 速度型】θ = {FVD.theta}°  cos²θ = {FVD.cos2:.3f}  "
      f"C = {FVD.C:.2f} tf·s/cm  Δξ = {FVD.dxi*100:.0f}%  ξ = {FVD.xi*100:.0f}%"
      f"  B1 = {FVD.B1v:.2f}")
    p(f"   T 不變 = {FVD.T} s   Sa {FIX['Sa']:.3f} → {FVD.Sa_:.3f} g   "
      f"V = {FVD.V:,.0f} tf ({FVD.V/FIX['V']*100:.0f}%)   "
      f"D {FIX['D']:.2f} → {FVD.D:.2f} cm ({FVD.D/FIX['D']*100:.0f}%)")

    p(f"\n【BRB 位移型】附加勁度 {BRB.ratio:.0%}k  K = {BRB.K:.1f} tf/cm  "
      f"T {T_FIX} → {BRB.T:.3f} s（左移）  ξ = {BRB.xi*100:.0f}%  "
      f"B1 = {BRB.B1v:.2f}")
    p(f"   Sa(5%) {FIX['Sa']:.3f} → {Sa(BRB.T):.3f} g（反而變大）  "
      f"折減後 {BRB.Sa_:.3f} g   V = {BRB.V:,.0f} tf "
      f"({BRB.V/FIX['V']*100:.0f}%)   D {FIX['D']:.2f} → {BRB.D:.2f} cm "
      f"({BRB.D/FIX['D']*100:.0f}%)")

    p(f"\n【TMD】μ = {TMD.mu}  m_d = {TMD.md:.3f} tf·s²/cm（重 {TMD.Wd_:.0f} tf）"
      f"  f_opt = {TMD.f_opt:.4f}  T_d = {TMD.Td:.3f} s")
    p(f"   ξ_opt = {TMD.xi_opt*100:.2f}%  最佳雙峰放大率 = {TMD.Rpeak:.2f}  "
      f"等效阻尼比 ≈ {TMD.xi_eq*100:.2f}%  質量塊行程 ≈ 主結構的 "
      f"{TMD.stroke:.1f} 倍")

    p(f"\n【B1 表】" + "  ".join(f"{x*100:.0f}%:{b:.1f}"
                                for x, b in zip(XI_TAB, B1_TAB)))
    p(f"  內插：ξ = {LRB_R['xi']*100:.1f}% → B1 = {LRB_R['B1']:.3f}；"
      f"ξ = {FPS_R['xi']*100:.1f}% → B1 = {FPS_R['B1']:.3f}")
    p("=" * 74)
