# -*- coding: utf-8 -*-
"""
build_figs_SD-U3-2.py — 產生 study/lecture-SD-U3-2.html 的全部向量圖（15 張 SVG）
所有幾何座標由公式／數值計算而來，不手打：
  * 反應譜 S_a=0.48/T<=0.8、S_d=S_a g T^2/4pi^2（§0）
  * 5 層剪力屋架特徵向量（固定基礎 vs k_b=k/30 隔震）（§1.2）
  * 串聯彈簧 k_eq/k_b=1/(1+k_b/k)（§1.1）
  * 遲滯迴圈頂點（橢圓／矩形／雙線性），面積以鞋帶公式驗算（§2.2、§3.1）
  * B_1 表內插與三個範例工作點（§2.4）；範例 B 迭代映射與固定點（§3.2）
  * FPS 單擺幾何與力三角形（§3.3）；SD-2018-4 R=D/(A-mu)（§3.4）
  * 雙線性遲滯逐步計算 vs FVD F=c*udot 的相位（§4.1）；cos^2(theta)（§4.2）
  * Den Hartog 主質量振幅解析式（mu=5%）（§4.5）；D_TM 扭轉放大（§5.1）
用法：python scripts/build_figs_SD-U3-2.py study/lecture-SD-U3-2.html
      → 以 data-fig 屬性就地替換頁面中對應的 <svg>（需 numpy、scipy）
"""
"""Tiny SVG builder: every coordinate comes from data/formulas."""
import re, html, sys, pathlib
import numpy as np

C = dict(red='#c62828', green='#2e7d32', blue='#1565c0', orange='#ef6c00', purple='#6a1b9a',
         teal='#00838f', ink='#263238', mut='#607d8b', grid='#e6ebee', axis='#78909c',
         red2='#ffebee', green2='#e8f5e9', blue2='#e3f2fd', orange2='#fff3e0', purple2='#f3e5f5',
         teal2='#e0f2f1', gray2='#eceff1')


def esc(s):
    return html.escape(s, quote=False)


def rich(s):
    """'K_{eff}' / 'T^2' -> tspans with sub/superscript."""
    out = []
    i = 0
    pat = re.compile(r'([_^])(\{([^}]*)\}|(.))')
    pos = 0
    for m in pat.finditer(s):
        out.append(esc(s[pos:m.start()]))
        body = m.group(3) if m.group(3) is not None else m.group(4)
        shift = 'sub' if m.group(1) == '_' else 'super'
        out.append(f'<tspan baseline-shift="{shift}" font-size="72%">{esc(body)}</tspan>')
        pos = m.end()
    out.append(esc(s[pos:]))
    return ''.join(out)


class Fig:
    def __init__(self, fid, w, h, title=None):
        self.id, self.w, self.h = fid, w, h
        self.el = []
        self.title = title

    def add(self, s):
        self.el.append(s)

    # ---- primitives
    def line(self, x1, y1, x2, y2, c=C['ink'], w=1.5, dash=None, arrow=None, start_arrow=None, op=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        a = f' marker-end="url(#{self.id}-a-{arrow})"' if arrow else ''
        sa = f' marker-start="url(#{self.id}-s-{start_arrow})"' if start_arrow else ''
        o = f' opacity="{op}"' if op else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d}{a}{sa}{o}/>')

    def path(self, d, c=C['ink'], w=1.5, fill='none', dash=None, arrow=None, op=None, extra=''):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        a = f' marker-end="url(#{self.id}-a-{arrow})"' if arrow else ''
        o = f' fill-opacity="{op}"' if op is not None else ''
        self.add(f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}"{ds}{a}{o} stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def poly(self, pts, c=C['ink'], w=1.5, fill='none', dash=None, close=False, arrow=None, op=None, extra=''):
        d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + (' Z' if close else '')
        self.path(d, c, w, fill, dash, arrow, op, extra)

    def rect(self, x, y, w, h, c=C['ink'], fill='#fff', rx=8, sw=1.5, dash=None, op=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        o = f' fill-opacity="{op}"' if op is not None else ''
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{c}" stroke-width="{sw}"{ds}{o}/>')

    def circle(self, x, y, r=4.5, fill=C['ink'], c='#fff', sw=1.5):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=13, c=C['ink'], anchor='start', weight='normal', italic=False, halo=False, rot=None):
        st = ' font-style="italic"' if italic else ''
        hl = ' paint-order="stroke" stroke="#fff" stroke-width="4" stroke-linejoin="round"' if halo else ''
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ''
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{c}" text-anchor="{anchor}" font-weight="{weight}"{st}{hl}{tr}>{rich(s)}</text>')

    def lines(self, x, y, rows, size=13, lh=None, **kw):
        lh = lh or size * 1.5
        for i, r in enumerate(rows):
            if isinstance(r, tuple):
                s, opt = r
                k = dict(kw); k.update(opt)
                self.text(x, y + i * lh, s, size=k.pop('size', size), **k)
            else:
                self.text(x, y + i * lh, r, size=size, **kw)

    def box(self, x, y, w, h, rows, c=C['ink'], fill='#fff', size=13, title_c=None, rx=9, lh=None, dy=None):
        self.rect(x, y, w, h, c=c, fill=fill, rx=rx)
        lh = lh or size * 1.55
        n = len(rows)
        y0 = y + h / 2 - (n - 1) * lh / 2 + size * 0.36 if dy is None else y + dy
        for i, r in enumerate(rows):
            s, opt = (r if isinstance(r, tuple) else (r, {}))
            k = dict(size=size, c=C['ink'], anchor='middle')
            if i == 0 and title_c:
                k.update(c=title_c, weight='bold')
            k.update(opt)
            self.text(x + w / 2, y0 + i * lh, s, **k)

    def diamond(self, cx, cy, w, h, rows, c=C['orange'], fill=C['orange2'], size=13):
        pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
        self.poly(pts, c=c, fill=fill, close=True, w=1.8)
        n = len(rows); lh = size * 1.45
        for i, r in enumerate(rows):
            s, opt = (r if isinstance(r, tuple) else (r, {}))
            k = dict(size=size, c=C['ink'], anchor='middle'); k.update(opt)
            self.text(cx, cy - (n - 1) * lh / 2 + size * 0.36 + i * lh, s, **k)

    def render(self):
        cols = dict(C)
        defs = []
        body = '\n'.join(self.el)
        for name, col in cols.items():
            if name.endswith('2') or name in ('grid',):
                continue
            if f'#{self.id}-a-{name})' not in body and f'#{self.id}-s-{name})' not in body:
                continue
            defs.append(f'<marker id="{self.id}-a-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
            defs.append(f'<marker id="{self.id}-s-{name}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
        t = f'<title>{esc(self.title)}</title>' if self.title else ''
        return (f'<svg data-fig="{self.id}" viewBox="0 0 {self.w} {self.h}" width="{self.w}" xmlns="http://www.w3.org/2000/svg" role="img">{t}'
                f'<defs>{"".join(defs)}</defs>' + '\n'.join(self.el) + '</svg>')


class Axes:
    """Linear plot area mapping data -> pixels."""
    def __init__(self, f, x, y, w, h, xr, yr):
        self.f, self.x, self.y, self.w, self.h = f, x, y, w, h
        self.xr, self.yr = xr, yr

    def X(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def P(self, a, b):
        return (self.X(a), self.Y(b))

    def frame(self, xt, yt, xlab='', ylab='', xfmt='{:g}', yfmt='{:g}', grid=True, size=11.5):
        f = self.f
        if grid:
            for v in yt:
                f.line(self.x, self.Y(v), self.x + self.w, self.Y(v), c=C['grid'], w=1)
            for v in xt:
                f.line(self.X(v), self.y, self.X(v), self.y + self.h, c=C['grid'], w=1)
        f.line(self.x, self.y + self.h, self.x + self.w + 6, self.y + self.h, c=C['axis'], w=1.4)
        f.line(self.x, self.y + self.h, self.x, self.y - 6, c=C['axis'], w=1.4)
        for v in xt:
            f.text(self.X(v), self.y + self.h + 17, xfmt.format(v), size=size, c=C['mut'], anchor='middle')
        for v in yt:
            f.text(self.x - 7, self.Y(v) + 4, yfmt.format(v), size=size, c=C['mut'], anchor='end')
        if xlab:
            f.text(self.x + self.w / 2, self.y + self.h + 37, xlab, size=12.5, c=C['mut'], anchor='middle')
        if ylab:
            f.text(self.x, self.y - 14, ylab, size=12.5, c=C['mut'], anchor='middle')

    def curve(self, xs, ys, **kw):
        pts = [self.P(a, b) for a, b in zip(xs, ys)]
        self.f.poly(pts, **kw)


import numpy as np
pi = np.pi
g = 981.0  # cm/s2


def Sa5(T):
    return np.minimum(0.8, 0.48 / T)


def Sd(T, B=1.0):
    return Sa5(T) * g * T ** 2 / (4 * pi ** 2) / B


# ------------------------------------------------------------------ §0
def fig_spectrum():
    f = Fig('f0', 900, 430, '同一張設計反應譜上的加速度與位移')
    # left: Sa
    a = Axes(f, 70, 60, 330, 250, (0, 4), (0, 0.9))
    f.text(235, 30, '加速度反應譜 S_a（＝力）', 15, C['red'], 'middle', 'bold')
    a.frame([0, 1, 2, 3, 4], [0, 0.2, 0.4, 0.6, 0.8], '週期 T（s）', 'S_a（g）', yfmt='{:.1f}')
    T = np.linspace(0.02, 4, 400)
    a.curve(T, Sa5(T), c=C['red'], w=2.6)
    Tl = np.linspace(0.6, 4, 300)
    a.curve(Tl, Sa5(Tl) / 1.5, c=C['orange'], w=2.2, dash='7 5')
    # corner
    f.line(a.X(0.6), a.Y(0), a.X(0.6), a.Y(0.8), c=C['axis'], w=1, dash='3 3')
    f.text(a.X(0.6) + 4, a.Y(0) - 8, 'T=0.6', 10.5, C['mut'])
    f.text(a.X(1.25), a.Y(0.43), 'ξ=5%：S_a = 0.48/T ≤ 0.8', 11.5, C['red'], weight='bold')
    f.text(a.X(0.7), a.Y(0.05), 'ξ=20%：÷B_1=1.5', 11.5, C['orange'], weight='bold')
    p1, p2, p3 = a.P(0.5, 0.8), a.P(2.5, 0.192), a.P(2.5, 0.128)
    f.line(p2[0] + 12, p2[1] + 2, p3[0] + 12, p3[1] - 2, c=C['orange'], w=1.6, arrow='orange')
    for p, col in ((p1, C['ink']), (p2, C['red']), (p3, C['orange'])):
        f.circle(*p, r=5.5, fill=col)
    f.line(p1[0] + 6, p1[1] + 4, a.X(1.2) - 4, a.Y(0.70) - 4, c=C['axis'], w=1)
    f.lines(a.X(1.2), a.Y(0.70) + 6, [('固定基礎 T=0.5 s', {'weight': 'bold'}), 'S_a=0.80 → V=4000 kN'], 11.5, lh=16)
    f.lines(p2[0] + 24, p2[1] - 40, [('隔震 T=2.5 s', {'weight': 'bold', 'c': C['red']}), ('0.192 → 960 kN（24%）', {'c': C['red']})], 11.5, lh=16)
    f.text(p3[0] + 24, p3[1] + 30, '+ξ=20%：0.128 → 640 kN', 11.5, C['orange'], weight='bold')

    # right: Sd
    b = Axes(f, 530, 60, 330, 250, (0, 4), (0, 50))
    f.text(695, 30, '位移反應譜 S_d（＝代價）', 15, C['green'], 'middle', 'bold')
    b.frame([0, 1, 2, 3, 4], [0, 10, 20, 30, 40, 50], '週期 T（s）', 'S_d（cm）')
    b.curve(T, Sd(T), c=C['green'], w=2.6)
    b.curve(Tl, Sd(Tl, 1.5), c=C['teal'], w=2.2, dash='7 5')
    f.line(b.X(0.6), b.Y(0), b.X(0.6), b.Y(Sd(0.6)), c=C['axis'], w=1, dash='3 3')
    f.text(b.X(0.18), b.Y(14), '∝T^2', 11, C['mut'])
    f.text(b.X(3.3), b.Y(Sd(3.3)) - 12, '∝T（等速度段：線性）', 11.5, C['green'], 'end')
    q1, q2, q3 = b.P(0.5, Sd(0.5)), b.P(2.5, Sd(2.5)), b.P(2.5, Sd(2.5, 1.5))
    f.line(q2[0], q2[1] + 7, q3[0], q3[1] - 8, c=C['teal'], w=1.6, arrow='teal')
    for p, col in ((q1, C['ink']), (q2, C['green']), (q3, C['teal'])):
        f.circle(*p, r=5.5, fill=col)
    f.text(q1[0] + 12, q1[1] + 22, '4.97 cm（T=0.5 s）', 11.5, C['ink'], weight='bold', halo=True)
    f.text(q2[0] - 12, q2[1] - 12, '29.8 cm（×6.0）', 11.5, C['green'], 'end', 'bold', halo=True)
    f.text(q3[0] + 12, q3[1] + 18, '+ξ=20%：19.9 cm', 11.5, C['teal'], weight='bold', halo=True)
    # formula
    f.text(b.X(4), b.Y(2) , 'S_d = S_a·g·T^2/(4π^2)', 11, C['mut'], 'end')

    f.box(70, 362, 330, 52, [('往右走：力一路下降', {'c': C['red'], 'weight': 'bold'}), '0.5→2.5 s：4000 → 960 kN（−76%）'], c='#ef9a9a', fill=C['red2'], size=12.5)
    f.box(530, 362, 330, 52, [('往右走：位移一路上升', {'c': C['green'], 'weight': 'bold'}), '0.5→2.5 s：4.97 → 29.8 cm（×6.0）'], c='#a5d6a7', fill=C['green2'], size=12.5)
    f.text(465, 393, '同一個 T', 12, C['purple'], 'middle', 'bold')
    f.line(408, 400, 522, 400, c=C['purple'], w=1.4, arrow='purple', start_arrow='purple')
    return f.render()


# ------------------------------------------------------------------ §1.1 (new)
def spring(f, x, y1, y2, c=C['ink'], n=6, amp=9):
    L = y2 - y1; lead = L * 0.18
    pts = [(x, y1), (x, y1 + lead)]
    seg = (L - 2 * lead) / (2 * n)
    for i in range(2 * n):
        pts.append((x + (amp if i % 2 == 0 else -amp), y1 + lead + seg * (i + 0.5)))
    pts += [(x, y2 - lead), (x, y2)]
    f.poly(pts, c=c, w=1.8)


def fig_series():
    f = Fig('f1s', 900, 350, '隔震層與上部結構串聯')
    # left model
    gx = 120; gy = 290
    f.line(40, gy, 200, gy, c=C['ink'], w=2.5)
    for i in range(9):
        f.line(45 + i * 18, gy, 35 + i * 18, gy + 10, c=C['mut'], w=1)
    f.text(205, gy + 4, 'u_g(t)', 12, C['mut'])
    spring(f, gx, gy, 215, C['green'])
    f.text(gx + 16, 258, 'k_b', 14, C['green'], weight='bold')
    f.rect(gx - 45, 190, 90, 25, c=C['green'], fill=C['green2'], rx=4)
    f.text(gx, 207, 'm_b = 0', 12, C['green'], 'middle', 'bold')
    spring(f, gx, 190, 110, C['blue'])
    f.text(gx + 16, 155, 'k', 14, C['blue'], weight='bold')
    f.rect(gx - 50, 70, 100, 40, c=C['blue'], fill=C['blue2'], rx=4)
    f.text(gx, 95, 'm', 15, C['blue'], 'middle', 'bold')
    f.line(gx + 62, 90, gx + 100, 90, c=C['blue'], w=1.4, arrow='blue'); f.text(gx + 104, 94, 'x_2', 12, C['blue'])
    f.line(gx + 52, 202, gx + 90, 202, c=C['green'], w=1.4, arrow='green'); f.text(gx + 94, 206, 'x_1', 12, C['green'])
    f.text(gx, 40, '2-DOF 模型', 14, C['ink'], 'middle', 'bold')
    # arrow
    f.line(255, 180, 320, 180, c=C['purple'], w=2.2, arrow='purple')
    f.lines(287, 150, [('m_b=0', {'anchor': 'middle'}), ('靜態束制', {'anchor': 'middle'})], 11.5, c=C['purple'], lh=15)
    # right model
    gx = 400
    f.line(330, gy, 470, gy, c=C['ink'], w=2.5)
    for i in range(8):
        f.line(335 + i * 18, gy, 325 + i * 18, gy + 10, c=C['mut'], w=1)
    spring(f, gx, gy, 150, C['purple'], n=8)
    f.text(gx + 16, 225, 'k_{eq}', 14, C['purple'], weight='bold')
    f.rect(gx - 50, 110, 100, 40, c=C['blue'], fill=C['blue2'], rx=4)
    f.text(gx, 135, 'm', 15, C['blue'], 'middle', 'bold')
    f.text(gx, 40, '等效 SDOF', 14, C['ink'], 'middle', 'bold')
    f.text(gx, 70, '1/k_{eq} = 1/k + 1/k_b', 13, C['purple'], 'middle', 'bold')
    # right plot: k_eq/k_b vs k_b/k
    a = Axes(f, 560, 50, 300, 200, (0, 0.5), (0.6, 1.0))
    a.frame([0, 0.1, 0.2, 0.3, 0.4, 0.5], [0.6, 0.7, 0.8, 0.9, 1.0], 'k_b / k（隔震層有多軟）', 'k_{eq} / k_b', xfmt='{:.1f}', yfmt='{:.1f}')
    r = np.linspace(0, 0.5, 200)
    a.curve(r, 1 / (1 + r), c=C['purple'], w=2.4)
    for rv, lab in ((1 / 20, '1/20 → 0.952'), (1 / 10, '1/10 → 0.909'), (1 / 5, '1/5 → 0.833')):
        p = a.P(rv, 1 / (1 + rv)); f.circle(*p, r=4.5, fill=C['purple'])
        f.text(p[0] + 8, p[1] - 8, lab, 11.5, C['purple'], halo=True)
    f.line(a.X(0), a.Y(0.95), a.X(0.5), a.Y(0.95), c=C['red'], w=1, dash='4 3')
    f.text(a.X(0.5), a.Y(0.95) - 5, '誤差 5%', 10.5, C['red'], 'end')
    f.text(a.X(0.25), 335, 'k_{eq}/k_b = 1/(1 + k_b/k)：k_b 越軟，k_{eq} 越貼近 k_b', 12, C['ink'], 'middle')
    return f.render()


# ------------------------------------------------------------------ §1.2
def shear_modes(Ms, Ks):
    n = len(Ms); K = np.zeros((n, n))
    for i in range(n):
        K[i, i] += Ks[i]
        if i + 1 < n:
            K[i, i] += Ks[i + 1]; K[i, i + 1] -= Ks[i + 1]; K[i + 1, i] -= Ks[i + 1]
    Mh = np.diag(1 / np.sqrt(Ms))
    w2, V = np.linalg.eigh(Mh @ K @ Mh)
    V = Mh @ V
    return np.sqrt(w2), V


def fig_rigid():
    f = Fig('f1r', 900, 480, '固定基礎與隔震的第一振態')
    wF, VF = shear_modes([1] * 5, [1] * 5)
    pF = VF[:, 0] / VF[-1, 0]
    kb = 1 / 30
    wI, VI = shear_modes([1] * 6, [kb] + [1] * 5)
    pI = VI[:, 0] / VI[-1, 0]
    meF = pF.sum() ** 2 / (pF @ pF) / 5
    meI = pI.sum() ** 2 / (pI @ pI) / 6
    Tr = wF[0] / wI[0]

    def frame(x0, shape, iso, col, title):
        gy = 380; hs = 52; amp = 110; hb = 40
        f.text(x0 + 180, 34, title, 15, col, 'middle', 'bold')
        f.line(x0 - 20, gy, x0 + 230, gy, c=C['ink'], w=3)
        nlev = len(shape)
        if iso:
            ys = [gy - hb] + [gy - hb - hs * (i + 1) for i in range(nlev - 1)]
        else:
            ys = [gy - hs * (i + 1) for i in range(nlev)]
        f.poly([(x0, gy)] + [(x0, y) for y in ys], c='#cfd8dc', w=1.5, dash='4 3')
        f.poly([(x0 + 90, gy)] + [(x0 + 90, y) for y in ys], c='#cfd8dc', w=1.5, dash='4 3')
        xs = [x0 + amp * s for s in shape]
        if iso:
            f.poly([(x0 - 6, gy), (x0 + 96, gy), (xs[0] + 96, ys[0]), (xs[0] - 6, ys[0])], c=C['green'], fill=C['green2'], close=True, w=1.6)
            f.text((x0 + xs[0]) / 2 + 45, gy - 15, '隔震層', 11, C['green'], 'middle', 'bold')
            f.line(x0, gy + 18, xs[0], gy + 18, c=C['green'], w=1.4, arrow='green', start_arrow='green')
            f.text((x0 + xs[0]) / 2, gy + 36, f'隔震層吃掉 {shape[0]*100:.0f}%', 11.5, C['green'], 'middle', 'bold')
            pts = list(zip(xs, ys))
        else:
            pts = [(x0, gy)] + list(zip(xs, ys))
        for dx in (0, 90):
            f.poly([(x + dx, y) for x, y in pts], c=col, w=2.4)
        for x, y in zip(xs, ys):
            f.line(x - 6, y, x + 96, y, c=C['ink'], w=4)
        drifts = np.diff(np.concatenate([[0], shape]))
        bx = x0 + 280
        f.text(bx + 50, 70, '層間位移 ÷ 屋頂位移', 11.5, C['mut'], 'middle')
        labels = (['隔震層'] + [f'{i}F' for i in range(1, nlev)]) if iso else [f'{i}F' for i in range(1, nlev + 1)]
        for i, (d, y) in enumerate(zip(drifts, ys)):
            yy = (y + (gy if i == 0 else ys[i - 1])) / 2
            f.text(bx - 6, yy + 4, labels[i], 11, C['mut'], 'end')
            bc = C['green'] if (iso and i == 0) else col
            f.rect(bx, yy - 8, max(1.5, 90 * d), 16, c=bc, fill=bc, rx=2, sw=0, op=0.85)
            f.text(bx + 90 * d + 5, yy + 4, f'{d*100:.1f}%', 11, C['ink'])
        f.line(bx, 80, bx, gy, c=C['axis'], w=1)

    frame(50, pF, False, C['red'], '固定基礎：變形分散在每一層')
    frame(490, pI, True, C['blue'], '基礎隔震：變形集中在隔震層')
    f.line(462, 50, 462, 400, c='#cfd8dc', w=1.2, dash='5 5')
    f.text(230, 440, f'第一振態有效質量 {meF*100:.0f}%', 12.5, C['red'], 'middle', 'bold')
    f.text(670, 440, f'第一振態有效質量 {meI*100:.1f}%　週期 ×{Tr:.1f}', 12.5, C['blue'], 'middle', 'bold')
    f.text(450, 468, '均勻 5 層剪力屋架（各層 m、k 相同）的特徵向量實算，屋頂位移正規化為 1；隔震例取 m_b=m、k_b=k/30', 11.5, C['mut'], 'middle')
    return f.render(), dict(meF=meF, meI=meI, Tr=Tr, iso=(pI[0]), fixed1=pF[0])


import numpy as np
pi = np.pi


def B1(x):
    return float(np.interp(x, [0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50], [0.8, 1.0, 1.25, 1.5, 1.63, 1.70, 1.75]))


def shoelace(p):
    p = np.array(p); x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


# ------------------------------------------------------------------ §2.2 loops
def fig_loops():
    f = Fig('f22', 900, 420, '三種遲滯迴圈')
    titles = [('① 橢圓：線性黏滯（速度型）', C['blue'], C['blue2']),
              ('② 矩形：庫倫摩擦（位移型）', C['orange'], C['orange2']),
              ('③ 平行四邊形：雙線性（LRB／BRB）', C['green'], C['green2'])]
    xs0 = [20, 315, 610]
    for k, (x0, (tt, col, fill)) in enumerate(zip(xs0, titles)):
        a = Axes(f, x0 + 25, 55, 220, 200, (-1.35, 1.35), (-1.35, 1.35))
        f.text(x0 + 135, 30, tt, 13.5, col, 'middle', 'bold')
        f.line(a.X(-1.3), a.Y(0), a.X(1.3), a.Y(0), c=C['axis'], w=1.2, arrow='axis')
        f.line(a.X(0), a.Y(-1.3), a.X(0), a.Y(1.3), c=C['axis'], w=1.2, arrow='axis')
        f.text(a.X(1.3) - 2, a.Y(0) + 16, 'u', 12, C['mut'], 'end', italic=True)
        f.text(a.X(0) + 7, a.Y(1.3) + 6, 'F', 12, C['mut'], italic=True)
        if k == 0:
            t = np.linspace(0, 2 * pi, 200)
            pts = [a.P(np.cos(s), -0.75 * np.sin(s)) for s in t]
            f.poly(pts, c=col, fill=fill, w=2.4, close=True)
            tip = (1, 0)
            f.text(a.X(0.05), a.Y(0.75) - 7, 'cωD', 11, col)
        elif k == 1:
            P = [(1, 0.6), (1, -0.6), (-1, -0.6), (-1, 0.6)]
            f.poly([a.P(*p) for p in P], c=col, fill=fill, w=2.4, close=True)
            tip = (1, 0.6)
            f.text(a.X(-1) + 4, a.Y(0.6) - 6, 'μW', 11, col)
        else:
            k0, Fy, al, D = 3.0, 0.6, 0.2, 1.0
            Dy = Fy / k0; Q = Fy * (1 - al); Fm = Q + al * k0 * D
            P = [(D, Fm), (D - 2 * Dy, Fm - 2 * Fy), (-D, -Fm), (-D + 2 * Dy, -Fm + 2 * Fy)]
            f.poly([a.P(*p) for p in P], c=col, fill=fill, w=2.4, close=True)
            f.line(*a.P(0, 0), *a.P(Dy, Fy), c=C['mut'], w=1.4, dash='4 3')
            f.text(a.X(Dy / 2) - 6, a.Y(Fy / 2) - 4, 'k_0', 11, C['mut'], 'end')
            tip = (D, Fm)
        # secant
        f.line(*a.P(0, 0), *a.P(*tip), c=C['red'], w=2.2)
        f.circle(*a.P(*tip), r=4.5, fill=C['red'])
        rows = {0: [('割線勁度 = 0（u=D 時 F=0）', {'c': C['red']}), ('W_D = π·D·(cωD) = πcωD^2', {'c': col, 'weight': 'bold'}), 'ξ_{eq} 只看 ω，與振幅 D 無關'],
                1: [('割線勁度 = μW/D（隨 D 遞減）', {'c': C['red']}), ('W_D = 4·D·μW', {'c': col, 'weight': 'bold'}), 'ξ_{eq} 與 ω 無關、與 D 成反比'],
                2: [('割線勁度 = Q/D + αk_0', {'c': C['red']}), ('W_D = 4Q(D − D_y)', {'c': col, 'weight': 'bold'}), 'ξ_{eq} 與 ω 無關、隨 D 先升後降']}[k]
        f.lines(x0 + 135, 288, rows, 12.5, anchor='middle', lh=21)
    f.line(305, 40, 305, 345, c='#cfd8dc', w=1, dash='5 5')
    f.line(600, 40, 600, 345, c='#cfd8dc', w=1, dash='5 5')
    f.box(60, 360, 780, 50, [('形狀 → 面積公式 → ξ 依賴什麼', {'c': C['purple'], 'weight': 'bold'}),
                             'ξ_{eq} = W_D /(4π W_S)，W_S = ½K_{eff}D^2（一律用「系統」割線勁度，不是消能器勁度）'],
          c='#ce93d8', fill=C['purple2'], size=12.5)
    return f.render()


# ------------------------------------------------------------------ §2.4 B1 (new)
def fig_B():
    f = Fig('f24', 900, 360, '阻尼修正係數 B 與阻尼比')
    a = Axes(f, 80, 40, 520, 250, (0, 50), (0.7, 1.85))
    a.frame([0, 5, 10, 20, 30, 40, 50], [0.8, 1.0, 1.2, 1.4, 1.6, 1.8], '等效阻尼比 ξ（%）', 'B', yfmt='{:.1f}')
    f.rect(a.X(10), a.y, a.X(25) - a.X(10), a.h, c='none', fill=C['green2'], rx=0, sw=0, op=0.7)
    f.text(a.X(17.5), a.y + 16, '隔震層典型 10~25%', 11, C['green'], 'middle', 'bold')
    xs = [2, 5, 10, 20, 30, 40, 50]; bs = [0.8, 1.0, 1.25, 1.5, 1.63, 1.70, 1.75]
    a.curve(xs, bs, c=C['blue'], w=2.6)
    for x, b in zip(xs, bs):
        f.circle(*a.P(x, b), r=3.5, fill=C['blue'], sw=1)
    a.curve([2, 5, 10, 20], [0.8, 1.0, 1.33, 1.6], c=C['mut'], w=1.8, dash='6 4')
    f.text(a.X(20) + 6, a.Y(1.6) - 4, 'B_S（短週期）', 11.5, C['mut'])
    f.text(a.X(50), a.Y(1.58), 'B_1（長週期，隔震一律用這條）', 11.5, C['blue'], 'end', 'bold')
    f.line(a.X(0), a.Y(1), a.X(5), a.Y(1), c=C['axis'], w=1, dash='3 3')
    f.text(a.X(5) + 5, a.Y(1) + 15, '5% → B=1（譜的基準）', 11, C['mut'])
    pts = [(16.86, '範例 D', C['orange'], -1), (20.5, '範例 B', C['green'], 1), (38.7, '範例 C', C['purple'], -1)]
    offs = {'範例 D': (-8, 18, 'end'), '範例 B': (8, 18, 'start'), '範例 C': (-8, -12, 'end')}
    for x, lab, col, side in pts:
        b = B1(x / 100); p = a.P(x, b)
        f.line(p[0], p[1], p[0], a.Y(0.7), c=col, w=1, dash='3 3')
        f.line(a.X(0), p[1], p[0], p[1], c=col, w=1, dash='3 3')
        f.circle(*p, r=5, fill=col)
        ox, oy, an = offs[lab]
        f.text(p[0] + ox, p[1] + oy, f'{lab}：{x:g}% → {b+1e-6:.3f}', 11.5, col, an, 'bold', halo=True)
    # right panel: marginal returns
    x0 = 640
    f.text(x0 + 120, 50, '邊際效益遞減', 14, C['red'], 'middle', 'bold')
    rows = [(5, 20), (20, 40)]
    for i, (p, q) in enumerate(rows):
        bp, bq = B1(p / 100), B1(q / 100)
        red = 1 - bp / bq
        y = 80 + i * 90
        f.box(x0, y, 240, 72, [(f'ξ：{p}% → {q}%', {'weight': 'bold'}), f'B：{bp:.2f} → {bq:.2f}', (f'位移再折減 {red*100:.0f}%', {'c': C['red'], 'weight': 'bold'})], c='#ef9a9a', fill=C['red2'], size=12.5, lh=20)
    f.lines(x0, 270, ['阻尼加倍到 40% 只多換 12%', '→ 隔震層取 10~25% 就夠', '　代價（加速度回升）卻持續增加'], 12, c=C['ink'], lh=19)
    return f.render()


# ------------------------------------------------------------------ §2.5 iteration flow
def fig_iter():
    f = Fig('f25', 900, 300, '等效線性化迭代流程')
    f.text(450, 28, '迴圈閉不起來：D 決定 K_{eff}，K_{eff} 決定 T 與 ξ，T 與 ξ 又決定 D', 14.5, C['purple'], 'middle', 'bold')
    y, h = 110, 74
    B = [(20, 120, ['假設 D', ('初猜 20~30 cm', {'c': C['mut'], 'size': 11.5})], C['blue'], C['blue2']),
         (170, 160, ['① 割線勁度', 'K_{eff} = F(D)/D', ('→ T_{eff} = 2π√(W/gK_{eff})', {'size': 11.5})], C['green'], C['green2']),
         (360, 160, ['② 等效阻尼', 'W_D → ξ_{eq}', ('→ 查表得 B_1', {'size': 11.5})], C['orange'], C['orange2']),
         (550, 175, ['③ 新位移', 'D_{new} = (g/4π^2)', ('× S_a(T_{eff})·T_{eff}^2 / B_1', {'size': 11.5})], C['purple'], C['purple2'])]
    for x, w, rows, c, fl in B:
        f.box(x, y, w, h, rows, c=c, fill=fl, size=12.5, title_c=c, lh=19)
    for (x1, w1, *_), (x2, *_r) in zip(B[:-1], B[1:]):
        f.line(x1 + w1 + 2, y + h / 2, x2 - 4, y + h / 2, c=C['ink'], w=1.8, arrow='ink')
    f.line(727, y + h / 2, 742, y + h / 2, c=C['ink'], w=1.8, arrow='ink')
    f.diamond(810, y + h / 2, 130, 84, [('|D_{new}−D|/D', {'weight': 'bold', 'size': 12}), ('< 5%？', {'weight': 'bold', 'size': 12})])
    # no -> loop top
    f.poly([(810, y + h / 2 - 42), (810, 72), (80, 72), (80, y - 4)], c=C['red'], w=1.8, arrow='red')
    f.text(445, 64, '否：以 D_{new} 當新的假設值再跑一輪', 12.5, C['red'], 'middle', 'bold')
    # yes -> down
    f.line(810, y + h / 2 + 42, 810, 236, c=C['green'], w=1.8, arrow='green')
    f.text(818, 222, '是', 12.5, C['green'], weight='bold')
    f.box(740, 240, 140, 40, [('D_D 定案', {'c': C['green'], 'weight': 'bold'})], c=C['green'], fill=C['green2'], size=13)
    f.lines(20, 230, [('收斂行為（§3.2 實測）', {'weight': 'bold', 'c': C['ink']}),
                      '從 30 cm 起算：22.95 → 20.93 → 20.24 → 20.04 cm，單調收斂、不震盪',
                      '固定點 19.97 cm；初猜越接近，輪數越少'], 12, c=C['mut'], lh=19)
    return f.render()


# ------------------------------------------------------------------ §3.1 LRB
def fig_lrb():
    f = Fig('f31', 900, 485, 'LRB 雙線性遲滯迴圈')
    k0, Fy, al, D = 1.0, 1.0, 0.2, 4.0
    Dy = Fy / k0; Q = Fy * (1 - al); Fm = Q + al * k0 * D
    P = [(D, Fm), (D - 2 * Dy, Fm - 2 * Fy), (-D, -Fm), (-D + 2 * Dy, -Fm + 2 * Fy)]
    area = shoelace(P); assert abs(area - 4 * Q * (D - Dy)) < 1e-9
    a = Axes(f, 40, 50, 460, 300, (-4.8, 4.8), (-2.0, 2.0))
    f.text(270, 28, 'LRB 雙線性遲滯迴圈（示意 α=0.2）', 14.5, C['green'], 'middle', 'bold')
    f.line(a.X(-4.7), a.Y(0), a.X(4.7), a.Y(0), c=C['axis'], w=1.2, arrow='axis')
    f.line(a.X(0), a.Y(-1.95), a.X(0), a.Y(1.95), c=C['axis'], w=1.2, arrow='axis')
    f.text(a.X(4.7), a.Y(0) + 16, 'u', 12, C['mut'], 'end', italic=True)
    f.text(a.X(0) + 8, a.Y(1.95) + 8, 'F', 12, C['mut'], italic=True)
    f.poly([a.P(*p) for p in P], c=C['green'], fill=C['green2'], w=2.6, close=True)
    # initial loading
    f.line(*a.P(0, 0), *a.P(Dy, Fy), c=C['green'], w=2.2, dash='5 3')
    # Q extension
    f.line(*a.P(0, Q), *a.P(Dy, Fy), c=C['mut'], w=1.3, dash='3 3')
    f.circle(*a.P(0, Q), r=4, fill=C['mut'])
    f.text(a.X(0) - 8, a.Y(Q) - 12, 'Q = F_y(1−α)', 12, C['mut'], 'end', 'bold', halo=True)
    # secant
    f.line(*a.P(0, 0), *a.P(D, Fm), c=C['red'], w=2.2)
    f.text(a.X(1.6), a.Y(1.6 * Fm / D) + 26, 'K_{eff} = F_{max}/D', 12, C['red'], 'middle', 'bold', halo=True)
    # points
    f.circle(*a.P(Dy, Fy), r=5, fill=C['green'])
    f.text(a.X(Dy) - 6, a.Y(Fy) - 10, '(D_y , F_y)', 12, C['green'], 'end', 'bold', halo=True)
    f.circle(*a.P(D, Fm), r=5, fill=C['red'])
    f.text(a.X(D) + 8, a.Y(Fm) - 6, '(D , F_{max})', 12, C['red'], 'start', 'bold', halo=True)
    # slopes labels
    f.text(a.X(2.6), a.Y(Q + al * 2.6) - 9, '斜率 αk_0（降伏後）', 11.5, C['green'], 'middle', halo=True, rot=-np.degrees(np.arctan(al * (a.h / 4.0) / (a.w / 9.6))))
    f.text(a.X(3.05) + 8, a.Y(0.6) + 4, '斜率 k_0（卸載）', 11.5, C['green'], halo=True)
    # D ticks
    for v, lab in ((Dy, 'D_y'), (D, 'D'), (-D, '−D')):
        f.line(a.X(v), a.Y(0) - 3, a.X(v), a.Y(0) + 3, c=C['axis'], w=1.2)
        f.text(a.X(v), a.Y(0) + 17, lab, 11.5, C['mut'], 'middle')
    f.line(a.X(D), a.Y(Fm), a.X(D), a.Y(0), c=C['axis'], w=1, dash='3 3')
    f.text(a.X(-1.2), a.Y(-0.3), '面積 W_D = 4Q(D − D_y)', 12.5, C['green'], 'middle', 'bold', halo=True)
    f.text(a.X(-1.2), a.Y(-0.3) + 18, f'= 4×{Q:g}×{D-Dy:g} = {area:g}（鞋帶公式驗算 ✓）', 11, C['mut'], 'middle', halo=True)
    # right: xi(D) with example B
    Q_, k0_, al_ = 54.0, 5200.0, 0.10
    Dy_ = 60 / k0_
    Ds = np.linspace(Dy_ * 1.0001, 0.45, 400)
    xi = 2 * Q_ * (Ds - Dy_) / (pi * Ds * (Q_ + al_ * k0_ * Ds))
    b = Axes(f, 580, 60, 280, 220, (0, 45), (0, 40))
    f.text(720, 28, 'ξ_{eq} 隨 D 先升後降（範例 B 參數）', 13.5, C['orange'], 'middle', 'bold')
    b.frame([0, 10, 20, 30, 40], [0, 10, 20, 30, 40], 'D（cm）', 'ξ_{eq}（%）')
    b.curve(Ds * 100, xi * 100, c=C['orange'], w=2.4)
    im = int(np.argmax(xi)); pk = b.P(Ds[im] * 100, xi[im] * 100)
    f.circle(*pk, r=4.5, fill=C['orange'])
    f.text(pk[0] + 6, pk[1] - 8, f'峰值 {xi[im]*100:.1f}% @ D={Ds[im]*100:.1f} cm', 11, C['orange'], halo=True)
    x20 = 2 * Q_ * (0.2 - Dy_) / (pi * 0.2 * (Q_ + al_ * k0_ * 0.2))
    p20 = b.P(20, x20 * 100); f.circle(*p20, r=4.5, fill=C['green'])
    f.text(p20[0] + 6, p20[1] + 18, f'D=20 cm → {x20*100:.1f}%', 11, C['green'], 'start', 'bold', halo=True)
    f.text(720, 352, 'ξ = 2Q(D−D_y) / [πD(Q+αk_0D)]', 11.5, C['mut'], 'middle')
    f.text(720, 370, 'D 小：剛過降伏，面積小；D 大：橡膠彈性能 αk_0D^2 主宰', 11, C['mut'], 'middle')
    f.box(40, 395, 400, 76, [('單支 LRB 的兩條主公式', {'c': C['green'], 'weight': 'bold'}),
                            'K_e = Q/D + αk_0　（割線，隨 D 遞減）', 'W_D = 4Q(D − D_y)　（D ≤ D_y 時為 0）'],
          c='#a5d6a7', fill=C['green2'], size=12.5, lh=21)
    f.box(460, 395, 400, 76, [('Q 的幾何意義', {'c': C['ink'], 'weight': 'bold'}),
                             '降伏後直線延伸回 u=0 的截距（灰虛線）',
                             'LRB ≈ 橡膠彈簧 αk_0 ＋ 定值抗力 Q 的元件並聯'],
          c='#cfd8dc', fill=C['gray2'], size=12.5, lh=21)
    return f.render(), dict(peak=(Ds[im], xi[im]), x20=x20)


# ------------------------------------------------------------------ §3.2 cobweb (new)
G_SI = 9.81
def lrb_map(D):
    W, n, k0, Fy, a = 20000, 16, 5200, 60, 0.10
    Q = Fy * (1 - a); Dy = Fy / k0
    Ke = n * (Q / D + a * k0); T = 2 * pi * np.sqrt(W / (G_SI * Ke))
    A = 4 * n * Q * (D - Dy); xi = A / (2 * pi * Ke * D * D)
    return G_SI / (4 * pi ** 2) * (0.48 / T) * T * T / B1(xi)


def fig_cobweb():
    f = Fig('f32', 900, 390, '迭代收斂的蛛網圖')
    a = Axes(f, 80, 40, 420, 280, (16, 32), (16, 32))
    a.frame([16, 20, 24, 28, 32], [16, 20, 24, 28, 32], '假設的 D（cm）', 'D_{new}（cm）')
    Ds = np.linspace(16, 32, 200)
    a.curve(Ds, [lrb_map(d / 100) * 100 for d in Ds], c=C['purple'], w=2.6)
    a.curve([16, 32], [16, 32], c=C['mut'], w=1.4, dash='5 4')
    f.text(a.X(27), a.Y(28.3), 'D_{new} = D（45° 線）', 11.5, C['mut'], 'end')
    f.text(a.X(31.5), a.Y(lrb_map(0.315) * 100) - 10, 'D_{new}(D)', 12, C['purple'], 'end', 'bold')
    d = 30.0; its = [d]
    pts = [a.P(d, 16)]
    for i in range(5):
        dn = lrb_map(d / 100) * 100
        pts += [a.P(d, dn), a.P(dn, dn)]
        d = dn; its.append(d)
    f.poly(pts, c=C['orange'], w=1.6)
    for x in its[:5]:
        f.circle(*a.P(x, lrb_map(x / 100) * 100), r=4, fill=C['orange'])
    from scipy.optimize import brentq
    fp = brentq(lambda x: lrb_map(x) - x, 0.1, 0.4) * 100
    f.circle(*a.P(fp, fp), r=6, fill=C['green'])
    f.text(a.X(fp) - 8, a.Y(fp) + 22, f'固定點 {fp:.2f} cm', 12, C['green'], 'end', 'bold', halo=True)
    f.text(a.X(30) + 6, a.Y(16) - 8, '起點 30', 11.5, C['orange'], weight='bold')
    # table
    x0 = 560
    f.text(x0 + 140, 50, '從 30 cm 起算的每一輪', 14, C['orange'], 'middle', 'bold')
    f.text(x0 + 20, 80, '輪', 12, C['mut'], weight='bold'); f.text(x0 + 70, 80, 'D 假設', 12, C['mut'], weight='bold')
    f.text(x0 + 160, 80, 'D_{new}', 12, C['mut'], weight='bold'); f.text(x0 + 230, 80, '誤差', 12, C['mut'], weight='bold')
    for i in range(5):
        y = 106 + i * 26
        e = abs(its[i + 1] - its[i]) / its[i] * 100
        ok = e < 1
        f.text(x0 + 25, y, str(i + 1), 12.5, C['ink'], 'middle')
        f.text(x0 + 70, y, f'{its[i]:.2f}', 12.5)
        f.text(x0 + 160, y, f'{its[i+1]:.2f}', 12.5, C['purple'], weight='bold')
        f.text(x0 + 230, y, f'{e:.1f}%', 12.5, C['green'] if ok else C['red'], weight='bold')
    f.lines(x0, 250, ['曲線斜率 0 < s < 1（約 0.3~0.4）→ 單調收斂',
                      '每輪誤差約縮小為上一輪的 0.3~0.4 倍',
                      ('從 20 cm 起算：一輪就 0.1%（§3.2 範例）', {'c': C['green'], 'weight': 'bold'})], 12, c=C['ink'], lh=21)
    f.text(450, 380, '曲線由範例 B 的參數實算（16 支 LRB、W=20,000 kN、S_a=0.48/T、B_1 內插）；與對角線的交點就是設計位移 D_D', 11.5, C['mut'], 'middle')
    slope = (lrb_map(0.205) - lrb_map(0.195)) / 0.01
    return f.render(), dict(fp=fp, its=its, slope=slope)


# ------------------------------------------------------------------ §3.3 FPS
def fig_fps():
    f = Fig('f33', 900, 470, 'FPS 力學')
    O = (230, 55); r = 300; th = np.radians(20)
    f.text(230, 28, 'FPS：一個倒過來的單擺', 14.5, C['blue'], 'middle', 'bold')
    angs = np.radians(np.linspace(-38, 38, 120))
    f.poly([(O[0] + (r + 14) * np.sin(t), O[1] + (r + 14) * np.cos(t)) for t in angs], c=C['ink'], w=7)
    f.poly([(O[0] + r * np.sin(t), O[1] + r * np.cos(t)) for t in angs], c='#b0bec5', w=1, dash='3 3')
    f.circle(*O, r=4.5, fill=C['ink'])
    f.text(O[0] + 10, O[1] + 4, '曲率中心 O', 12, C['ink'])
    P = (O[0] + r * np.sin(th), O[1] + r * np.cos(th))
    B0 = (O[0], O[1] + r)
    f.line(*O, *B0, c=C['axis'], w=1.2, dash='5 4')
    f.line(*O, *P, c=C['axis'], w=1.2, dash='5 4')
    f.path(f'M{O[0]:.1f},{O[1]+60:.1f} A60,60 0 0 0 {O[0]+60*np.sin(th):.1f},{O[1]+60*np.cos(th):.1f}', c=C['purple'], w=1.8)
    f.text(O[0] + 12, O[1] + 84, 'θ', 14, C['purple'], weight='bold')
    f.text((O[0] + P[0]) / 2 + 8, (O[1] + P[1]) / 2, 'r', 14, C['ink'], italic=True, weight='bold')
    # slider (rotated rect tangent)
    deg = -np.degrees(th)
    f.add(f'<g transform="translate({P[0]:.1f},{P[1]:.1f}) rotate({deg:.2f})"><rect x="-28" y="-12" width="56" height="24" rx="4" fill="#90a4ae" stroke="{C["ink"]}" stroke-width="1.5"/></g>')
    # forces at P: W down, N toward O
    Wl = 85
    f.line(P[0], P[1], P[0], P[1] + Wl, c=C['red'], w=2.6, arrow='red')
    f.text(P[0] + 8, P[1] + Wl - 4, 'W', 13, C['red'], weight='bold')
    Nl = Wl / np.cos(th); u = ((O[0] - P[0]) / r, (O[1] - P[1]) / r)
    f.line(P[0], P[1], P[0] + Nl * u[0], P[1] + Nl * u[1], c=C['blue'], w=2.6, arrow='blue')
    f.text(P[0] + Nl * u[0] + 8, P[1] + Nl * u[1] - 2, 'N = W/cosθ', 12.5, C['blue'], weight='bold', halo=True)
    Rl = Wl * np.tan(th)
    f.line(P[0], P[1] - 34, P[0] - Rl, P[1] - 34, c=C['green'], w=2.6, arrow='green')
    f.text(P[0] - Rl - 6, P[1] - 30, '復位力 W tanθ', 12.5, C['green'], 'end', 'bold', halo=True)
    # x marker
    yx = B0[1] + 40
    f.line(B0[0], yx, P[0], yx, c=C['purple'], w=1.5, arrow='purple', start_arrow='purple')
    f.line(P[0], P[1] + 14, P[0], yx + 6, c=C['purple'], w=0.8, dash='2 2')
    f.text((B0[0] + P[0]) / 2, yx + 18, 'x = r sinθ', 12, C['purple'], 'middle', 'bold')
    # force triangle inset
    tx, ty, s = 70, 150, 0.9
    f.text(tx + 20, ty - 34, '力三角形', 12, C['mut'], 'middle', weight='bold')
    A0 = (tx + 40, ty)
    A1 = (A0[0], A0[1] + Wl * s)
    A2 = (A0[0] - Rl * s, A0[1])
    f.line(*A0, *A1, c=C['red'], w=2.2, arrow='red')
    f.line(*A1, *A2, c=C['blue'], w=2.2, arrow='blue')
    f.line(*A0, *A2, c=C['green'], w=2.2, arrow='green')
    f.text(A0[0] + 6, (A0[1] + A1[1]) / 2, 'W', 11.5, C['red'], weight='bold')
    f.text(A2[0] - 4, (A1[1] + A2[1]) / 2 + 4, 'N', 11.5, C['blue'], 'end', weight='bold')
    f.text((A0[0] + A2[0]) / 2, A0[1] - 6, 'W tanθ', 11, C['green'], 'middle', weight='bold')
    # right boxes
    x0 = 500
    f.box(x0, 40, 380, 130, [('三行推完（先忽略摩擦）', {'c': C['blue'], 'weight': 'bold'}),
                            ('鉛直：N cosθ = W　→　N = W/cosθ', {}),
                            ('水平：m ẍ = −N sinθ = −W tanθ', {}),
                            ('小角度 tanθ ≈ sinθ = x/r → ẍ + (g/r)x = 0', {'c': C['red'], 'weight': 'bold'}),
                            ('（單擺方程；唯一的近似是小角度）', {'c': C['mut'], 'size': 11.5})],
          c='#90caf9', fill=C['blue2'], size=12.5, lh=22)
    f.box(x0, 185, 380, 70, [('T = 2π√(r/g)　　k = W/r', {'c': C['red'], 'weight': 'bold', 'size': 15}),
                            ('週期只看曲率半徑，與上部重量無關', {})],
          c='#ef9a9a', fill=C['red2'], size=12.5, lh=24)
    f.box(x0, 270, 380, 90, [('為什麼與質量無關？', {'c': C['purple'], 'weight': 'bold'}),
                            '重的結構 k = W/r 較大，慣性 m = W/g 也等比例大',
                            '兩者在 √(k/m) = √(g/r) 中相消',
                            ('→ 同一批支承可用在不同重量的柱下', {'c': C['red'], 'weight': 'bold'})],
          c='#ce93d8', fill=C['purple2'], size=12.5, lh=19)
    f.box(x0, 375, 380, 80, [('加上摩擦 μW（在 D 處與復位力同向）', {'c': C['orange'], 'weight': 'bold'}),
                            'F_{max} = W(D/R + μ)　K_{eff} = W/R + μW/D',
                            'ξ_e = 2μ /(πA)，A = D/R + μ'],
          c='#ffcc80', fill=C['orange2'], size=12.5, lh=21)
    f.text(250, 455, '示意 θ=20°（放大以便看清）；真實 FPS 的 D/R 約 0.1，θ ≈ 6°', 11.5, C['mut'], 'middle')
    return f.render()


# ------------------------------------------------------------------ §3.4 R-mu (new)
def fig_Rmu():
    f = Fig('f34', 900, 352, 'R 對 μ 的敏感度')
    D, A = 25.0, 0.08
    a = Axes(f, 80, 40, 470, 240, (0.02, 0.08), (0, 2000))
    a.frame([0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08], [0, 500, 1000, 1500, 2000], '摩擦係數 μ', 'R（cm）', xfmt='{:.2f}')
    mus = np.linspace(0.02, 0.0675, 300)
    a.curve(mus, D / (A - mus), c=C['blue'], w=2.6)
    f.line(a.X(A), a.y, a.X(A), a.y + a.h, c=C['red'], w=1.4, dash='5 4')
    f.text(a.X(A) - 6, a.y + 14, 'μ → A=0.08：R → ∞', 11.5, C['red'], 'end', 'bold')
    f.text(a.X(0.025), a.Y(800), 'R = D/(A − μ)', 13, C['blue'], weight='bold')
    mu0 = pi * A * (0.30 + (1.6910615 - 1.63) / 0.07 * 0.10) / 2
    for mu, col, lab, dx, dy, anc in ((mu0, C['green'], f'未進位 μ={mu0:.4f} → R={D/(A-mu0):.0f}', 14, 44, 'start'), (0.049, C['orange'], f'講義取 μ=0.049 → R={D/(A-0.049):.0f}', -10, -16, 'end')):
        p = a.P(mu, D / (A - mu))
        f.line(p[0], p[1], p[0], a.Y(0), c=col, w=1, dash='3 3')
        f.circle(*p, r=5, fill=col)
        f.text(p[0] + dx, p[1] + dy, lab, 11.5, col, anc, 'bold', halo=True)
    x0 = 600
    f.text(x0 + 130, 50, '為什麼這麼敏感', 14, C['red'], 'middle', 'bold')
    f.lines(x0, 82, ['分母 A − μ 是兩個相近數的差：', '　0.080 − 0.049 = 0.031',
                     ('相對放大係數 = μ /(A − μ) ≈ 1.6', {'c': C['red'], 'weight': 'bold'}),
                     '→ μ 差 1%，R 差約 1.6%'], 12.5, lh=22)
    for i, mu in enumerate((0.048, 0.049, 0.050)):
        f.text(x0 + 10, 190 + i * 22, f'μ = {mu:.3f}　→　R = {D/(A-mu):.0f} cm', 12.5, C['ink'])
    f.text(x0, 272, '答題：ξ_e 內插算到小數第三位，', 12, C['mut'])
    f.text(x0, 292, '並註明「R 對 μ 敏感」', 12, C['mut'])
    f.text(450, 342, 'SD-2018-4：D=25 cm、A=0.08g；由 T_e=3.548 s → B=1.691 → ξ_e=38.7% → μ=πAξ_e/2', 11.5, C['mut'], 'middle')
    return f.render()


import numpy as np
pi = np.pi


def bilinear_force(u, k0, Fy, al):
    """Kinematic-hardening bilinear (return mapping)."""
    F = np.zeros_like(u); f = 0.0; kh = al * k0
    for i in range(1, len(u)):
        du = u[i] - u[i - 1]
        ftr = f + k0 * du
        # yield surface shifts with hardening: |f - kh*u| <= Fy(1-al)
        back = kh * u[i]
        lim = Fy * (1 - al)
        if ftr - back > lim:
            ftr = back + lim
        elif ftr - back < -lim:
            ftr = back - lim
        f = ftr; F[i] = f
    return F


# ------------------------------------------------------------------ §4.1 phase
def fig_phase():
    f = Fig('f41', 900, 470, '位移型與速度型阻尼力的相位')
    f.text(450, 26, '位移型與速度型出力差 90°：同一時刻不會同時到最大', 14.5, C['purple'], 'middle', 'bold')
    t = np.linspace(0, 1.5, 601)
    u = np.sin(2 * pi * t)
    Fb = bilinear_force(u, 4.0, 1.0, 0.1); Fb = Fb / np.abs(Fb).max()
    Fv = np.cos(2 * pi * t)
    rows = [('位移 u(t)', u, C['blue']), ('位移型出力（BRB）', Fb, C['orange']), ('速度型出力（FVD）F=cu̇', Fv, C['teal'])]
    x0, w = 175, 470
    axs = []
    for i, (lab, y, col) in enumerate(rows):
        a = Axes(f, x0, 55 + i * 115, w, 80, (0, 1.5), (-1.2, 1.2))
        axs.append(a)
        f.line(a.X(0), a.Y(0), a.X(1.5), a.Y(0), c=C['grid'], w=1.2)
        a.curve(t, y, c=col, w=2.4)
        f.lines(x0 - 12, a.Y(0) - 2, [(lab.split('（')[0], {'weight': 'bold'}), ('（' + lab.split('（')[1]) if '（' in lab else ''], 12, c=col, anchor='end', lh=17)
    # time markers
    for tm, col, lab in ((0.25, C['red'], 'u 最大'), (0.5, C['teal'], 'u = 0（速度最大）'), (0.75, C['red'], 'u 最小'), (1.25, C['red'], 'u 最大')):
        X = axs[0].X(tm)
        f.line(X, 48, X, 55 + 2 * 115 + 86, c=col, w=1.1, dash='4 3')
        f.text(X, 44, lab, 11, col, 'middle', 'bold')
    i25 = 100; i50 = 200
    f.circle(*axs[0].P(0.25, u[i25]), r=5, fill=C['blue'])
    f.circle(*axs[1].P(0.25, Fb[i25]), r=5, fill=C['orange'])
    f.circle(*axs[2].P(0.25, Fv[i25]), r=5, fill=C['teal'])
    f.text(axs[1].X(0.25) + 8, axs[1].Y(Fb[i25]) - 4, '最大', 11.5, C['orange'], weight='bold', halo=True)
    f.text(axs[2].X(0.25) + 8, axs[2].Y(0) - 8, '= 0', 11.5, C['teal'], weight='bold', halo=True)
    f.circle(*axs[2].P(0.5, Fv[i50]), r=5, fill=C['teal'])
    f.text(axs[2].X(0.5) + 8, axs[2].Y(Fv[i50]) + 4, '最大（反向）', 11.5, C['teal'], weight='bold', halo=True)
    # right: loops from same signals
    for i, (lab, F, col, fill) in enumerate((('BRB：F 對 u', Fb, C['orange'], C['orange2']), ('FVD：F 對 u', Fv, C['teal'], C['teal2']))):
        b = Axes(f, 700, 75 + i * 175, 150, 120, (-1.25, 1.25), (-1.25, 1.25))
        f.line(b.X(-1.25), b.Y(0), b.X(1.25), b.Y(0), c=C['axis'], w=1)
        f.line(b.X(0), b.Y(-1.25), b.X(0), b.Y(1.25), c=C['axis'], w=1)
        sel = t >= 0.5
        b.curve(u[sel], F[sel], c=col, w=2.2, fill=fill)
        f.circle(*b.P(1, F[i25]), r=4.5, fill=col)
        f.text(b.X(0), b.y - 8, lab, 12, col, 'middle', 'bold')
        f.text(b.X(1.25), b.Y(0) + 14, 'u', 11, C['mut'], 'end', italic=True)
    f.text(775, 410, '● = u 最大的時刻', 11, C['mut'], 'middle')
    f.box(175, 420, 470, 40, [('最大位移時：位移型出力最大、速度型出力為零 → 兩者的內力峰值不同時發生', {'size': 12.5})],
          c='#ce93d8', fill=C['purple2'], size=12.5)
    return f.render()


# ------------------------------------------------------------------ §4.2 brace (new)
def fig_brace():
    f = Fig('f42', 900, 360, '斜撐投影 cos²θ')
    th = np.radians(30); H = 150; L = H / np.tan(th); x0, y0 = 50, 300; d = 40
    f.text(x0 + L / 2 + 20, 30, '幾何：位移投影一次、力再投影一次', 14, C['ink'], 'middle', 'bold')
    f.line(x0 - 20, y0, x0 + L + 40, y0, c=C['ink'], w=3)
    # undeformed
    f.poly([(x0, y0), (x0, y0 - H), (x0 + L, y0 - H), (x0 + L, y0)], c='#cfd8dc', w=2, dash='5 4')
    # deformed frame
    f.poly([(x0, y0), (x0 + d, y0 - H), (x0 + L + d, y0 - H), (x0 + L, y0)], c=C['ink'], w=2.5)
    f.line(x0, y0, x0 + L + d, y0 - H, c=C['teal'], w=4)
    f.line(x0, y0, x0 + L, y0 - H, c=C['teal'], w=1.4, dash='4 3', op=0.6)
    # theta arc
    f.path(f'M{x0+60:.1f},{y0:.1f} A60,60 0 0 0 {x0+60*np.cos(th):.1f},{y0-60*np.sin(th):.1f}', c=C['purple'], w=1.6)
    f.text(x0 + 68, y0 - 12, 'θ', 14, C['purple'], weight='bold')
    # delta arrow
    f.line(x0 + L, y0 - H - 26, x0 + L + d, y0 - H - 26, c=C['red'], w=2, arrow='red')
    f.text(x0 + L + d / 2, y0 - H - 34, 'δ', 15, C['red'], 'middle', 'bold')
    # projection: from (x0+L, y0-H) drop perpendicular onto extended brace direction
    P0 = np.array([x0 + L, y0 - H]); e = np.array([np.cos(th), -np.sin(th)])
    P1 = P0 + d * np.cos(th) * e
    f.line(*P0, *P1, c=C['orange'], w=3)
    f.line(x0 + L + d, y0 - H, *P1, c=C['orange'], w=1, dash='2 2')
    f.text(P1[0] + 12, P1[1] + 18, 'δ_d = δ cosθ（伸長量）', 12, C['orange'], weight='bold', halo=True)
    f.text(x0 + L / 2 - 10, y0 - H / 2 + 26, '阻尼器（斜撐）', 12, C['teal'], 'middle', 'bold', halo=True, rot=-30)
    # force inset
    fx, fy = 470, 215
    f.text(fx + 30, 140, '力：沿軸向出力 F_d', 13, C['ink'], 'middle', 'bold')
    Fd = 100
    f.line(fx - 40, fy, fx - 40 + Fd * np.cos(th), fy - Fd * np.sin(th), c=C['teal'], w=3, arrow='teal')
    f.line(fx - 40, fy, fx - 40 + Fd * np.cos(th), fy, c=C['red'], w=2.4, arrow='red')
    f.line(fx - 40 + Fd * np.cos(th), fy, fx - 40 + Fd * np.cos(th), fy - Fd * np.sin(th), c=C['mut'], w=1, dash='3 3')
    f.text(fx - 40 + Fd * np.cos(th) / 2 - 10, fy - Fd * np.sin(th) / 2 - 12, 'F_d', 12.5, C['teal'], 'end', 'bold')
    f.text(fx - 40 + Fd * np.cos(th) / 2, fy + 20, 'F_d cosθ（水平有效）', 12, C['red'], 'middle', 'bold')
    f.lines(fx - 40, 268, ['F_d = c·δ̇_d = c·δ̇ cosθ', ('水平：c·cos^2θ·δ̇', {'c': C['red'], 'weight': 'bold'})], 12.5, lh=21)
    # cos^2 plot
    a = Axes(f, 650, 60, 220, 200, (0, 90), (0, 1))
    f.text(760, 30, 'C_{eff}/C = cos^2θ', 13.5, C['red'], 'middle', 'bold')
    a.frame([0, 30, 45, 60, 90], [0, 0.25, 0.5, 0.75, 1.0], 'θ（°）', '', yfmt='{:.2f}')
    f.rect(a.X(30), a.y, a.X(40) - a.X(30), a.h, c='none', fill=C['green2'], rx=0, sw=0, op=0.9)
    tt = np.linspace(0, 90, 181)
    a.curve(tt, np.cos(np.radians(tt)) ** 2, c=C['red'], w=2.4)
    for v in (30, 45, 60):
        c2 = np.cos(np.radians(v)) ** 2; p = a.P(v, c2)
        f.circle(*p, r=4.5, fill=C['red'])
        f.text(p[0] + 7, p[1] - 6, f'{c2:.2f}', 11.5, C['red'], weight='bold', halo=True)
    f.text(a.X(35), a.y + a.h - 6, '實務 30~40°', 10.5, C['green'], 'middle', 'bold')
    f.text(450, 345, 'δ 的幾何為放大示意；能量 = 力 × 位移，兩者各打一次 cosθ 折扣 → cos^2θ（BRB 的 k_{eff} = k_{brace}cos^2θ 同理）', 11.5, C['mut'], 'middle')
    return f.render()


# ------------------------------------------------------------------ §4.5 TMD
def tmd_amp(r, mu, fr, z):
    num = (2 * z * r) ** 2 + (r * r - fr * fr) ** 2
    den = (2 * z * r) ** 2 * (r * r - 1 + mu * r * r) ** 2 + (mu * fr * fr * r * r - (r * r - 1) * (r * r - fr * fr)) ** 2
    return np.sqrt(num / den)


def fig_tmd():
    f = Fig('f45', 900, 440, 'TMD 頻率響應')
    mu = 0.05; fopt = 1 / (1 + mu); zopt = np.sqrt(3 * mu / (8 * (1 + mu) ** 3))
    a = Axes(f, 75, 50, 560, 300, (0.7, 1.35), (0, 14))
    f.text(450, 24, 'TMD 兩個機制：反共振（挖成谷）＋ 頻率分裂（一峰變兩矮峰）　μ = 5%', 14, C['purple'], 'middle', 'bold')
    a.frame([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3], [0, 2, 4, 6, 8, 10, 12, 14], '頻率比 r = Ω/ω_n', '|X/X_{st}|', xfmt='{:.1f}')
    clip = f'{f.id}-clip'
    f.add(f'<clipPath id="{clip}"><rect x="{a.x}" y="{a.y}" width="{a.w}" height="{a.h}"/></clipPath>')
    r = np.linspace(0.7, 1.35, 1301)
    no = 1 / np.sqrt((1 - r * r) ** 2 + (2 * 0.02 * r) ** 2)
    und = tmd_amp(r, mu, 1.0, 1e-9)
    opt = tmd_amp(r, mu, fopt, zopt)
    ext = f' clip-path="url(#{clip})"'
    for ys, col, w, dash in ((no, C['red'], 2.4, None), (und, C['orange'], 2, '6 4'), (opt, C['green'], 2.8, None)):
        ys = np.minimum(ys, 30)
        # break at huge values for undamped
        pts = [a.P(x, y) for x, y in zip(r, ys)]
        f.poly(pts, c=col, w=w, dash=dash, extra=ext)
    # undamped asymptotes
    for rr in (np.sqrt(1 + mu / 2 - np.sqrt(mu + mu * mu / 4)), np.sqrt(1 + mu / 2 + np.sqrt(mu + mu * mu / 4))):
        f.line(a.X(rr), a.y, a.X(rr), a.y + a.h, c=C['orange'], w=0.8, dash='2 3')
        f.text(a.X(rr), a.y - 4, f'r={rr:.3f} → ∞', 10.5, C['orange'], 'middle', 'bold')
    f.text(a.X(1.0), a.y - 4, '↑ 無 TMD 峰值 25', 10.5, C['red'], 'middle', 'bold')
    f.circle(*a.P(1.0, 0), r=5, fill=C['orange'])
    f.text(a.X(1.0) + 8, a.Y(0) - 8, '反共振 r=1：主結構位移 = 0', 11.5, C['orange'], weight='bold', halo=True)
    from scipy.signal import argrelmax
    idx = argrelmax(opt)[0]
    for i in idx:
        f.circle(*a.P(r[i], opt[i]), r=4.5, fill=C['green'])
    hp = np.sqrt(1 + 2 / mu)
    f.line(a.X(0.83), a.Y(hp), a.X(1.12), a.Y(hp), c=C['green'], w=1, dash='3 3')
    f.text(a.X(0.83), a.Y(hp) - 7, f'兩峰 ≈ √(1+2/μ) = {hp:.2f}', 11.5, C['green'], weight='bold', halo=True)
    # legend
    lx, ly = 655, 70
    f.rect(lx, ly - 22, 225, 108, c='#cfd8dc', fill='#fff', rx=8, sw=1)
    for i, (col, dash, lab) in enumerate(((C['red'], None, '無 TMD（ξ=2%）'), (C['orange'], '6 4', 'TMD 無阻尼（f=1）'), (C['green'], None, f'TMD 最佳：f={fopt:.3f}、ξ_d={zopt*100:.1f}%'))):
        y = ly + i * 28
        f.line(lx + 12, y, lx + 42, y, c=col, w=2.6, dash=dash)
        f.text(lx + 50, y + 4, lab, 11.5, col)
    f.box(655, 190, 225, 70, [('無阻尼 TMD', {'c': C['orange'], 'weight': 'bold'}), '靠「反力抵消」在調頻點歸零', '代價：兩側生出無限峰、頻帶極窄'], c='#ffcc80', fill=C['orange2'], size=11.5, lh=18)
    f.box(655, 272, 225, 70, [('最佳阻尼 TMD', {'c': C['green'], 'weight': 'bold'}), '放棄完全消振，換兩峰等高', 'Den Hartog：最小化兩峰較高者'], c='#a5d6a7', fill=C['green2'], size=11.5, lh=18)
    f.text(450, 425, '主結構無阻尼時的 Den Hartog 解析式實算；紅線為對照用的無 TMD、ξ=2% SDOF（峰值 1/(2ξ)=25 超出圖框）', 11.5, C['mut'], 'middle')
    return f.render(), dict(peaks=[(r[i], opt[i]) for i in idx])


# ------------------------------------------------------------------ §5.1 D_D vs D_TM (new)
def fig_dtm():
    f = Fig('f51', 900, 380, 'D_D 與 D_TM')
    Lx, By = 30.0, 20.0; e = 0.05 * Lx; yv = Lx / 2
    fac = 1 + yv * 12 * e / (By ** 2 + Lx ** 2)
    s = 7.0
    def panel(cx, cy, title, col, torsion):
        f.text(cx, 34, title, 14, col, 'middle', 'bold')
        w, h = Lx * s, By * s
        # moat
        if torsion:
            m = 26
            f.rect(cx - w / 2 - m, cy - h / 2 - m - 34, w + 2 * m, h + 2 * m + 34, c=C['mut'], fill='none', rx=2, sw=2.5, dash='8 4')
            f.text(cx + w / 2 + m - 4, cy - h / 2 - m - 40, '隔震溝（moat）', 11.5, C['mut'], 'end', 'bold')
        f.rect(cx - w / 2, cy - h / 2, w, h, c='#b0bec5', fill='none', rx=0, sw=1.5, dash='4 3')
        D = 22.0 if not torsion else 30.0
        ang = 0 if not torsion else -np.arctan((fac - 1) * D / (w / 2))
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        rp = [(cx + x * np.cos(ang) - y * np.sin(ang), cy - D + x * np.sin(ang) + y * np.cos(ang)) for x, y in pts]
        f.poly(rp, c=col, fill=C['blue2'] if not torsion else C['red2'], close=True, w=2.2, op=0.6)
        f.circle(cx, cy, r=4, fill=C['mut'])
        f.circle(cx, cy - D, r=5, fill=col)
        f.line(cx, cy, cx, cy - D + 6, c=col, w=2, arrow='blue' if not torsion else 'red')
        f.text(cx + 8, cy - D / 2 + 4, 'D_D' if not torsion else 'D_M', 12.5, col, weight='bold', halo=True)
        f.text(cx + 8, cy + 16, '質心', 11, C['mut'])
        if torsion:
            cxr, cyr = cx + w / 2, cy - h / 2
            px, py = rp[1]
            f.line(cxr, cyr, px, py, c=C['red'], w=2.4, arrow='red')
            f.circle(px, py, r=5, fill=C['red'])
            f.text(px + 6, py + 26, 'D_{TM}', 13, C['red'], weight='bold', halo=True)
            f.text(px + 6, py + 42, '最不利角落', 11, C['red'], halo=True)
            f.line(cx, cy + h / 2 + 18, cx + w / 2, cy + h / 2 + 18, c=C['purple'], w=1.3, arrow='purple', start_arrow='purple')
            f.text(cx + w / 4, cy + h / 2 + 34, f'y = {yv:g} m', 11.5, C['purple'], 'middle', 'bold')
        else:
            f.text(cx, cy + h / 2 + 30, 'DBE（475 年）、質心、純平移', 12, col, 'middle', 'bold')
            f.text(cx, cy + h / 2 + 50, '→ 設計支承本體（剪切變形容量）', 12, C['ink'], 'middle')
    panel(220, 200, '設計位移 D_D', C['blue'], False)
    panel(640, 200, '最大總位移 D_{TM}', C['red'], True)
    f.text(640, 345, f'D_{{TM}} = D_M[1 + y·12e/(b^2+L^2)]　例：b=20、L=30、e=1.5 m → ×{fac:.2f}', 12, C['red'], 'middle', 'bold')
    f.text(640, 365, 'MCE（2475 年）＋ 扭轉 → 決定隔震溝淨距（撞到即脆性失效）', 12, C['ink'], 'middle')
    f.text(220, 345, '位移與轉角皆為放大示意（角落增量依右式比例繪製）', 11, C['mut'], 'middle')
    return f.render(), dict(fac=fac)


# ------------------------------------------------------------------ §6 decision
def fig_flow():
    f = Fig('f6', 900, 820, '解題決策流程')
    def arrow(pts, col=C['ink']):
        f.poly(pts, c=col, w=1.8, arrow='ink' if col == C['ink'] else {C['red']: 'red', C['green']: 'green'}[col])
    f.box(330, 12, 240, 36, [('這一題在動哪一顆旋鈕？', {'weight': 'bold'})], c=C['ink'], fill=C['gray2'], size=13)
    arrow([(450, 48), (450, 66)])
    f.diamond(450, 102, 250, 70, [('結構有隔震層嗎？', {'weight': 'bold'})])
    # yes -> left
    arrow([(325, 102), (155, 102), (155, 150)], C['green']); f.text(240, 95, '是', 12.5, C['green'], 'middle', 'bold')
    # no -> right
    arrow([(575, 102), (745, 102), (745, 141)], C['red']); f.text(660, 95, '否', 12.5, C['red'], 'middle', 'bold')
    # ---- left column
    LX, LW = 20, 270
    f.box(LX, 152, LW, 56, ['隔震：先認出裝置', 'LRB（雙線性）／FPS（摩擦單擺）'], c=C['green'], fill=C['green2'], title_c=C['green'], size=12.5, lh=20)
    arrow([(155, 208), (155, 224)])
    f.box(LX, 226, LW, 78, ['LRB：K = Q/D + αk_0，W_D = 4Q(D − D_y)', 'FPS：K = W/R + μW/D，W_D = 4μWD', ('FPS 另有 A = D/R + μ、ξ = 2μ/(πA)', {'c': C['mut']})], c=C['green'], fill='#fff', size=12, lh=21)
    arrow([(155, 304), (155, 320)])
    f.box(LX, 322, LW, 70, [('假設 D → K_{eff} → T_{eff}', {'weight': 'bold', 'c': C['green']}), ('→ W_D → ξ_{eff} → B_1 → D_{new}', {'weight': 'bold', 'c': C['green']}), ('（同時給 D 與 A 時可直接反算，§3.4）', {'c': C['mut'], 'size': 11})], c=C['green'], fill=C['green2'], size=12.5, lh=20)
    arrow([(155, 392), (155, 410)])
    f.diamond(155, 444, 200, 64, [('|ΔD|/D < 5%？', {'weight': 'bold'})])
    arrow([(55, 444), (10, 444), (10, 357), (LX - 2, 357)], C['red']); f.text(30, 437, '否', 12, C['red'], 'middle', 'bold')
    arrow([(155, 476), (155, 500)], C['green']); f.text(165, 493, '是', 12, C['green'], weight='bold')
    f.box(LX, 502, LW, 56, [('量級檢查（三個都要過）', {'weight': 'bold', 'c': C['teal']}), 'T 2~4 s　D 15~40 cm　ξ 10~25%'], c=C['teal'], fill=C['teal2'], size=12.5, lh=20)
    arrow([(155, 558), (155, 574)])
    f.box(LX, 576, LW, 80, [('規範層（§5）', {'weight': 'bold', 'c': C['purple']}), '靜力法適用條件過了嗎？', "動力分析：D'_D = D_D/√(1+(T/T_{eD})^2)", ('隔震溝一律用 D_{TM}（MCE＋扭轉）', {'c': C['red']})], c=C['purple'], fill=C['purple2'], size=12, lh=18)
    # ---- right column TMD
    f.diamond(745, 176, 210, 66, [('是 TMD 嗎？', {'weight': 'bold'})])
    RX, RW = 610, 270
    arrow([(745, 209), (745, 236)], C['green']); f.text(755, 228, '是', 12, C['green'], weight='bold')
    f.box(RX, 238, RW, 56, [('調頻', {'weight': 'bold', 'c': C['purple']}), 'f_{opt} = 1/(1+μ)，目標是主結構原本的 ω_n'], c=C['purple'], fill=C['purple2'], size=12, lh=20)
    arrow([(745, 294), (745, 310)])
    f.box(RX, 312, RW, 56, [('最佳阻尼（Den Hartog）', {'weight': 'bold', 'c': C['purple']}), 'ξ_{d,opt} = √(3μ / 8(1+μ)^3)'], c=C['purple'], fill=C['purple2'], size=12, lh=20)
    arrow([(745, 368), (745, 384)])
    f.box(RX, 386, RW, 70, [('兩個機制都要講', {'weight': 'bold', 'c': C['purple']}), '① 反力抵消（不靠消能）', '② 阻尼消能（壓平分裂的兩峰）'], c=C['purple'], fill='#fff', size=12, lh=19)
    arrow([(745, 456), (745, 472)])
    f.box(RX, 474, RW, 82, [('質量比 μ 的三重代價', {'weight': 'bold', 'c': C['red']}), '行程 ≈ 靜位移 / μ', '有效頻帶 ≈ √μ', '殘餘放大 = √(1+2/μ)'], c=C['red'], fill=C['red2'], size=12, lh=18)
    # ---- middle column
    arrow([(640, 176), (450, 176), (450, 224)], C['red']); f.text(560, 169, '否', 12.5, C['red'], 'middle', 'bold')
    f.diamond(450, 258, 250, 66, [('位移型還是速度型？', {'weight': 'bold'})])
    MX, MW = 315, 270
    arrow([(395, 280), (380, 314)]); f.text(368, 300, '位移型', 11.5, C['orange'], 'end', 'bold')
    arrow([(505, 280), (520, 314)]); f.text(532, 300, '速度型', 11.5, C['teal'], 'start', 'bold')
    f.box(MX, 316, 130, 84, [('BRB／摩擦', {'weight': 'bold', 'c': C['orange']}), '勁度增加', '→ T 縮短', ('→ S_a 要重算', {'c': C['red']})], c=C['orange'], fill=C['orange2'], size=12, lh=17)
    f.box(MX + 140, 316, 130, 84, [('黏滯 FVD', {'weight': 'bold', 'c': C['teal']}), '勁度不變', '→ T 不變', ('→ 只除以 B', {'c': C['green']})], c=C['teal'], fill=C['teal2'], size=12, lh=17)
    arrow([(380, 400), (380, 410), (450, 410), (450, 424)])
    f.poly([(520, 400), (520, 410), (450, 410)], c=C['ink'], w=1.8)
    f.box(MX, 426, MW, 48, [('斜裝乘 cos^2θ', {'weight': 'bold'}), ('（力與位移各投影一次）', {'c': C['mut'], 'size': 11})], c='#90a4ae', fill='#fff', size=12.5, lh=18)
    arrow([(450, 474), (450, 488)])
    f.box(MX, 490, MW, 66, [('能量法', {'weight': 'bold', 'c': C['blue']}), 'Δξ = W_D /(4πW_S)，ξ_{eff} = ξ_0 + Δξ', ('橢圓 πab／矩形 4ab／平行四邊形', {'c': C['mut'], 'size': 11})], c=C['blue'], fill=C['blue2'], size=12, lh=19)
    arrow([(450, 556), (450, 570)])
    f.box(MX, 572, MW, 40, [('查 B_1 折減 → 位移與內力', {'weight': 'bold'})], c='#90a4ae', fill='#fff', size=12.5)
    arrow([(450, 612), (450, 626)])
    f.box(MX, 628, MW, 66, [('速度型：三種變位情況取包絡', {'weight': 'bold', 'c': C['red']}), 'Δ_D（樑柱）／V_D（阻尼器、柱軸力）', '／A_D（基底剪力、非結構物）'], c=C['red'], fill=C['red2'], size=12, lh=18)
    # bottom
    for x, ytop in ((155, 656), (450, 694), (745, 556)):
        arrow([(x, ytop), (x, 726)])
    f.box(20, 728, 860, 74, [('三條路最後都收在同一處：等效線性化的兩條公式 ＋ 阻尼修正係數 B', {'weight': 'bold', 'c': C['purple']}),
                            'K_{eff} = F(D)/D（割線）　　ξ_{eq} = W_D /(4πW_S)', 'S_{a,eff} = S_a(5%)/B　　D = (g/4π^2)·S_a·T^2/B'],
          c='#ce93d8', fill=C['purple2'], size=12.5, lh=20)
    return f.render()


FIGS = {}
for _fn in (fig_spectrum, fig_series, fig_rigid, fig_loops, fig_B, fig_iter, fig_lrb, fig_cobweb,
            fig_fps, fig_Rmu, fig_phase, fig_brace, fig_tmd, fig_dtm, fig_flow):
    _r = _fn(); _r = _r[0] if isinstance(_r, tuple) else _r
    FIGS[re.search(r'data-fig="([^"]+)"', _r).group(1)] = _r

if __name__ == '__main__':
    p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'study/lecture-SD-U3-2.html')
    s = p.read_text(encoding='utf-8'); n = 0
    for k, v in FIGS.items():
        s, c = re.subn(r'<svg data-fig="%s".*?</svg>' % re.escape(k), lambda m: v, s, flags=re.S); n += c
    p.write_text(s, encoding='utf-8')
    print(f'replaced {n}/{len(FIGS)} figures in {p}')
