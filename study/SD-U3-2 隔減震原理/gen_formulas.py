#!/usr/bin/env python3
"""SD-U3-2 觀念講義 —— 公式 PNG 渲染（matplotlib mathtext）

踩過的坑：
  * mathtext 只支援 LaTeX 子集：\\frac \\sqrt ^ _ \\sum \\left \\right 希臘字母
    \\leq \\geq \\times \\cdot \\quad；**不支援** \\le \\ge \\tfrac \\text \\begin。
  * `$...$` 內絕對不能放中文 —— cm 字型無 CJK 字面。
    中文一律寫在 deck.js 的 label / note / insights。
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import json, os, re                       # noqa: E402

OUT_DIR = "formula_imgs"
os.makedirs(OUT_DIR, exist_ok=True)

NAVY = "#1B2A41"
DPI, FONTSIZE = 400, 30
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["text.color"] = NAVY

FORMULAS = {
    # ── 反應譜與阻尼折減 ───────────────────────────────
    "f_sa":    r"$S_a(T) = S_{DS} \;\; (T \leq T_0) \quad ; \quad "
               r"S_a(T) = \frac{S_{D1}}{T} \;\; (T > T_0)$",
    "f_sd":    r"$D = \frac{g}{4\pi^2} S_a T^2 \quad \Rightarrow \quad "
               r"D \propto T \;\; \mathrm{(velocity \; branch)}$",
    "f_b1":    r"$S_{a,eff} = \frac{S_a(T_{eff}, 5\%)}{B_1} \quad , \quad "
               r"D = \frac{g}{4\pi^2} \cdot \frac{S_a(T_{eff}, 5\%) \, T_{eff}^2}{B_1}$",
    "f_series": r"$\frac{1}{k_{eq}} = \frac{1}{k_{sup}} + \frac{1}{k_b} "
                r"\quad , \quad k_b \ll k_{sup} \; \Rightarrow \; k_{eq} \approx k_b$",
    # ── 等效線性化三式 ─────────────────────────────────
    "f_keff":  r"$K_{eff} = \frac{F(D)}{D} \qquad "
               r"\mathrm{(secant, \; through \; the \; origin)}$",
    "f_teff":  r"$T_{eff} = 2\pi \sqrt{\frac{m}{K_{eff}}} "
               r"= 2\pi \sqrt{\frac{W}{g \, K_{eff}}}$",
    "f_xieq":  r"$\xi_{eq} = \frac{W_D}{4\pi W_S} "
               r"= \frac{W_D}{2\pi K_{eff} D^2}$",
    "f_ws":    r"$W_S = \frac{1}{2} K_{eff} D^2 \qquad "
               r"\mathrm{(system \; stiffness, \; not \; k_d)}$",
    # ── LRB 雙線性 ─────────────────────────────────────
    "f_lrb_k": r"$K_{eff} = \frac{Q_d}{D} + k_d \quad , \quad "
               r"\alpha = \frac{k_d}{k_0}$",
    "f_lrb_q": r"$Q_d = F_y (1 - \alpha) \quad , \quad "
               r"D_y = \frac{F_y}{k_0} = \frac{Q_d}{k_0 (1 - \alpha)}$",
    "f_lrb_w": r"$W_D = 4 Q_d (D - D_y) \qquad "
               r"\mathrm{(subtract \; D_y \, !)}$",
    "f_lrb_f": r"$F(D) = Q_d + k_d D \qquad (D > D_y)$",
    # ── FPS 摩擦單擺 ───────────────────────────────────
    "f_fps_t": r"$T = 2\pi \sqrt{\frac{R}{g}} \qquad "
               r"\mathrm{(independent \; of \; W)}$",
    "f_fps_k": r"$K_{eff} = \frac{W}{R} + \frac{\mu W}{D}$",
    "f_fps_w": r"$W_D = 4 \mu W D \qquad (D_y \approx 0)$",
    "f_fps_a": r"$A = \frac{F_{max}}{W} = \frac{D}{R} + \mu \quad , \quad "
               r"\xi_{eq} = \frac{2\mu}{\pi A}$",
    # ── 設計量 ─────────────────────────────────────────
    "f_v":     r"$V_b = K_{eff} \, D = W \cdot \frac{S_a(T_{eff},5\%)}{B_1}$",
    "f_dtm":   r"$D_{TM} = D \left[ 1 + y \, \frac{12 e}{b^2 + d^2} \right]$",
    "f_conv":  r"$\frac{|D_{i+1} - D_i|}{D_i} < 5\% \quad \Rightarrow \quad "
               r"\mathrm{converged}$",
    # ── 速度型阻尼器 ───────────────────────────────────
    "f_fvd":   r"$F_d = C \, |\dot{u}|^{\,\beta} \mathrm{sgn}(\dot{u}) "
               r"\qquad (\beta = 1 : \; F_d = C \dot{u})$",
    "f_dxi":   r"$\Delta \xi = \frac{\pi C \cos^2\theta}{T \, k}$",
    "f_cos2":  r"$c_{eq} = C \cos^2\theta \qquad "
               r"\mathrm{(force \; once, \; displacement \; once)}$",
    "f_phase": r"$F_{max} \neq k u_0 + C \omega u_0 \quad ; \quad "
               r"F_{max} = k u_0 \sqrt{1 + (2\xi_d)^2}$",
    # ── 位移型阻尼器 ───────────────────────────────────
    "f_brb_k": r"$k_{tot} = k + k_{brb} \quad \Rightarrow \quad "
               r"T_{new} = T \sqrt{\frac{k}{k_{tot}}} < T$",
    "f_brb_n": r"$V_{new} = W \cdot \frac{S_a(T_{new}, 5\%)}{B_1} "
               r"\quad \mathrm{vs} \quad V = W S_a(T, 5\%)$",
    # ── TMD ────────────────────────────────────────────
    "f_tmd_m": r"$\mu = \frac{m_d}{M} \quad , \quad "
               r"f = \frac{\omega_d}{\omega_n}$",
    "f_tmd_f": r"$f_{opt} = \frac{1}{1 + \mu} \quad \Rightarrow \quad "
               r"T_d = T_n (1 + \mu)$",
    "f_tmd_x": r"$\xi_{opt} = \sqrt{\frac{3\mu}{8(1 + \mu)}}$",
    "f_tmd_p": r"$\left| \frac{X_1}{X_{st}} \right|_{peak} "
               r"= \sqrt{1 + \frac{2}{\mu}}$",
}

CJK = re.compile(r"[　-〿一-鿿＀-￯]")
bad = {k: v for k, v in FORMULAS.items() if CJK.search(v)}
if bad:
    raise SystemExit(f"CJK leaked into mathtext: {list(bad)}")
for k, v in FORMULAS.items():
    if re.search(r"\\le[^qf]|\\ge[^q]|\\tfrac|\\text", v):
        raise SystemExit(f"unsupported macro in {k}: {v}")

manifest, errors = {}, []
for fid, latex in FORMULAS.items():
    fig = plt.figure(figsize=(0.1, 0.1), dpi=DPI)
    try:
        fig.text(0, 0, latex, fontsize=FONTSIZE, color=NAVY)
        path = os.path.join(OUT_DIR, f"{fid}.png")
        fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight",
                    pad_inches=0.08)
        plt.close(fig)
        from PIL import Image
        w, h = Image.open(path).size
        manifest[fid] = {"file": path, "ar": w / h}
    except Exception as e:
        errors.append((fid, str(e)))
        plt.close(fig)

with open("formula_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Rendered {len(manifest)} formulas, {len(errors)} errors")
for fid, err in errors:
    print("ERROR", fid, err)
