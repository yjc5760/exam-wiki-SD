#!/usr/bin/env python3
"""SD-U3-2 專用的像素座標繪圖小工具（建在 structdraw.Canvas 之上）。

Canvas 一律以 sx=1, ox=0, oy=0 建立，於是「模型座標 = 像素座標、y 向上」，
本檔的 Plot 只負責把資料座標映射到那個 y-up 像素空間。
"""
import sys, math
sys.path.insert(0, "/root/.claude/skills/synced/"
                   "6983ec08-a01a-44e4-a131-56c9e592c524_ab4f317b-1625-4c71-b32d-871e33fbc9cc/"
                   "struct-diagram/scripts")
from structdraw import Canvas, C, compose, esc   # noqa: E402,F401


def canvas(w, h, bg="#FFFFFF"):
    """y 向上的像素畫布（預設白底，pptx 不吃透明背景）。"""
    return Canvas(w, h, sx=1.0, ox=0.0, oy=0.0, bg=bg)


class Plot:
    """資料座標 → y-up 像素座標的線性映射，附座標框、刻度與標籤。

    (x0, y0) 為圖框左下角的像素位置（y 由畫布底部起算）。
    """

    def __init__(self, cv, x0, y0, w, h, xlim, ylim):
        self.cv, self.x0, self.y0, self.w, self.h = cv, x0, y0, w, h
        self.xa, self.xb = xlim
        self.ya, self.yb = ylim

    # ---- 映射 ----
    def X(self, x):
        return self.x0 + (x - self.xa) / (self.xb - self.xa) * self.w

    def Y(self, y):
        return self.y0 + (y - self.ya) / (self.yb - self.ya) * self.h

    def P(self, p):
        return (self.X(p[0]), self.Y(p[1]))

    # ---- 座標框 ----
    def frame(self, xticks=(), yticks=(), xlabel=None, ylabel=None,
              xfmt="{:g}", yfmt="{:g}", grid=True, tick_size=12.5,
              label_size=13.5, ylabel_dx=-4):
        cv = self.cv
        x0, y0, w, h = self.x0, self.y0, self.w, self.h
        cv.rect_px(x0, cv.h - (y0 + h), w, h, "#FFFFFF", 0, C["border"], 1.2)
        for t in xticks:
            X = self.X(t)
            if grid:
                cv.line((X, y0), (X, y0 + h), C["border"], 1, dash="3 4")
            cv.line((X, y0), (X, y0 - 5), C["muted"], 1.2)
            cv.text_px(X, cv.h - y0 + 18, xfmt.format(t), tick_size, C["muted"])
        for t in yticks:
            Y = self.Y(t)
            if grid:
                cv.line((x0, Y), (x0 + w, Y), C["border"], 1, dash="3 4")
            cv.line((x0, Y), (x0 - 5, Y), C["muted"], 1.2)
            cv.text_px(x0 - 10, cv.h - Y, yfmt.format(t), tick_size,
                       C["muted"], anchor="end")
        if xlabel:
            cv.text_px(x0 + w / 2, cv.h - y0 + 44, xlabel, label_size, C["text"])
        if ylabel:
            cv.text_px(x0 + ylabel_dx, cv.h - (y0 + h) - 15, ylabel,
                       label_size, C["text"], anchor="start")

    # ---- 圖形 ----
    def curve(self, pts, color=C["member"], w=2.4, dash=None, fill=None):
        self.cv.poly([self.P(p) for p in pts], color, w, dash,
                     fill=fill or "none")

    def curve_clip(self, pts, color=C["member"], w=2.4, dash=None):
        """超出 y 上限的段落直接斷開，不畫成假的水平頂蓋。"""
        seg = []
        for x, y in pts:
            if y <= self.yb:
                seg.append((x, y))
            elif seg:
                self.curve(seg, color, w, dash)
                seg = []
        if seg:
            self.curve(seg, color, w, dash)

    def area(self, pts, fill, stroke="none", w=1):
        self.cv.polygon([self.P(p) for p in pts], fill, stroke, w)

    def seg(self, p0, p1, color=C["muted"], w=1.6, dash=None):
        self.cv.line(self.P(p0), self.P(p1), color, w, dash=dash)

    def arrow(self, p0, p1, color=C["load"], w=2.6, head=9, dash=None):
        self.cv.arrow(self.P(p0), self.P(p1), color, w, head, dash)

    def dot(self, p, r=5.0, fill=C["accent"], stroke="#FFFFFF", w=1.8):
        self.cv.dot(self.P(p), r, fill, stroke, w)

    def tag(self, p, s, size=13, color=C["text"], dx=0, dy=0,
            anchor="middle", weight="700", math=False):
        X, Y = self.P(p)
        f = self.cv.math_px if math else self.cv.text_px
        f(X + dx, self.cv.h - Y + dy, s, size, color, anchor, weight)

    def vline(self, x, color=C["muted"], w=1.4, dash="5 5", y=None):
        self.seg((x, self.ya), (x, y if y is not None else self.yb),
                 color, w, dash)

    def hline(self, y, color=C["muted"], w=1.4, dash="5 5", x=None):
        self.seg((self.xa, y), (x if x is not None else self.xb, y),
                 color, w, dash)


def sampled(f, a, b, n=240):
    return [(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]


def badge(cv, x, y, w, h, text_lines, fill="#F5F7FA", stroke=C["border"],
          size=12.5, color=C["muted"], title=None, title_color=None,
          lh=18, pad=14):
    """左上角 (x, y) 以「由上而下的像素」計；供說明方塊使用。"""
    cv.rect_px(x, y, w, h, fill, 10, stroke, 1.2)
    yy = y + pad + 4
    if title:
        cv.text_px(x + pad, yy, title, size + 1.5, title_color or C["text"],
                   "start", weight="700")
        yy += lh + 3
    for ln in text_lines:
        cv.text_px(x + pad, yy, ln, size, color, "start")
        yy += lh
