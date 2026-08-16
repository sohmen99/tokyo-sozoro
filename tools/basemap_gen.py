# -*- coding: utf-8 -*-
"""OSM の実データから、既存の意匠のまま広域ベースマップを起こす。
   北を上にした正距円筒。1px = 16m。canvas 402x874 で約 6.4km x 14.0km。"""
import json, math, os, sys
G = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0 = 35.7152, 139.7849          # 上野公園と浅草寺の中点
CX, CY, MPP = 201.0, 437.0, 16.0
KX = 111320 * math.cos(math.radians(LAT0)) / MPP
KY = 111132 / MPP
BOX = (-80.0, -80.0, 482.0, 954.0)      # 少し外まで持って、viewBox で切る

def prj(lat, lon): return (CX + (lon - LON0) * KX, CY - (lat - LAT0) * KY)

def load(name):
    p = os.path.join(G, name + ".json")
    if not os.path.exists(p): return None
    return json.load(open(p, encoding="utf-8"))

# ── 折れ線の簡約（Douglas-Peucker） ──
def simplify(pts, tol):
    if len(pts) < 3: return pts
    def seg(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0: return math.hypot(x - x1, y - y1)
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        dmax, idx = 0, i
        for k in range(i + 1, j):
            d = seg(pts[k], pts[i], pts[j])
            if d > dmax: dmax, idx = d, k
        if dmax > tol:
            keep[idx] = True; stack += [(i, idx), (idx, j)]
    return [p for p, kp in zip(pts, keep) if kp]

# ── 多角形を矩形でクリップ（Sutherland-Hodgman） ──
def clip_poly(pts, box):
    x0, y0, x1, y1 = box
    def cl(poly, inside, inter):
        out = []
        for i in range(len(poly)):
            a, b = poly[i - 1], poly[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia: out.append(inter(a, b))
                out.append(b)
            elif ia:
                out.append(inter(a, b))
        return out
    def ix(a, b, X): t = (X - a[0]) / (b[0] - a[0]); return (X, a[1] + t * (b[1] - a[1]))
    def iy(a, b, Y): t = (Y - a[1]) / (b[1] - a[1]); return (a[0] + t * (b[0] - a[0]), Y)
    p = pts
    p = cl(p, lambda q: q[0] >= x0, lambda a, b: ix(a, b, x0))
    if not p: return []
    p = cl(p, lambda q: q[0] <= x1, lambda a, b: ix(a, b, x1))
    if not p: return []
    p = cl(p, lambda q: q[1] >= y0, lambda a, b: iy(a, b, y0))
    if not p: return []
    p = cl(p, lambda q: q[1] <= y1, lambda a, b: iy(a, b, y1))
    return p

def d_poly(pts, prec=1):
    if len(pts) < 3: return ""
    f = "%%.%df" % prec
    return "M" + " ".join((f + " " + f) % p for p in pts) + "Z"

def d_line(pts, prec=1):
    if len(pts) < 2: return ""
    f = "%%.%df" % prec
    return "M" + " ".join((f + " " + f) % p for p in pts)

def split_outside(pts, box, pad=40):
    """線を、描画域の外へ大きく出る部分で切る。"""
    x0, y0, x1, y1 = box[0]-pad, box[1]-pad, box[2]+pad, box[3]+pad
    runs, cur = [], []
    for p in pts:
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1: cur.append(p)
        else:
            if len(cur) > 1: runs.append(cur)
            cur = []
    if len(cur) > 1: runs.append(cur)
    return runs

# ── リレーションの outer メンバーを環に繋ぐ ──
def rings(rel):
    ways = []
    for m in rel.get("members", []):
        if m.get("role") != "outer": continue
        g = m.get("geometry")
        if not g or len(g) < 2: continue
        ways.append([(p["lat"], p["lon"]) for p in g])
    out, used = [], [False] * len(ways)
    for i in range(len(ways)):
        if used[i]: continue
        used[i] = True; chain = list(ways[i])
        grew = True
        while grew:
            grew = False
            for j in range(len(ways)):
                if used[j]: continue
                w = ways[j]
                if   chain[-1] == w[0]:  chain += w[1:];              used[j] = grew = True
                elif chain[-1] == w[-1]: chain += w[::-1][1:];        used[j] = grew = True
                elif chain[0]  == w[-1]: chain = w[:-1] + chain;      used[j] = grew = True
                elif chain[0]  == w[0]:  chain = w[::-1][:-1] + chain; used[j] = grew = True
        out.append(chain)
    return [r for r in out if len(r) > 3]

def area(pts):
    a = 0
    for i in range(len(pts)): 
        x1,y1 = pts[i-1]; x2,y2 = pts[i]; a += x1*y2 - x2*y1
    return abs(a) / 2

# ═══════════ 生成 ═══════════
layers = {}

# 1 · 区界
wd = load("ward")
ward_paths, taito = {}, None
for rel in wd["elements"]:
    name = rel.get("tags", {}).get("name")
    rs = rings(rel)
    ds = []
    for r in rs:
        p = [prj(la, lo) for la, lo in r]
        p = clip_poly(p, BOX)
        if len(p) < 3 or area(p) < 60: continue
        ds.append(d_poly(simplify(p, 0.7)))
    ward_paths[name] = " ".join(ds)
layers["ward_taito"] = ward_paths.pop("台東区")
layers["ward_others"] = " ".join(v for v in ward_paths.values() if v)

# 2 · 水面
for key, src, kind in [("water", "water", "poly"), ("river", "river", "line")]:
    d = load(src)
    if not d: layers[key] = ""; continue
    out = []
    for e in d["elements"]:
        g = e.get("geometry")
        if not g or len(g) < 2: continue
        p = [prj(q["lat"], q["lon"]) for q in g]
        if kind == "poly":
            p = clip_poly(p, BOX)
            if len(p) < 3 or area(p) < 25: continue
            out.append(d_poly(simplify(p, 0.6)))
        else:
            for run in split_outside(p, BOX):
                s = simplify(run, 0.6)
                if len(s) > 1: out.append(d_line(s))
    layers[key] = " ".join(out)

# 3 · 線のレイヤ
for key, src, tol, minlen in [("rail", "rail", 1.3, 10), ("road", "road", 0.8, 5), ("park", "park", 1.0, 0)]:
    d = load(src)
    if not d: layers[key] = ""; continue
    out = []
    for e in d["elements"]:
        g = e.get("geometry")
        if not g or len(g) < 2: continue
        p = [prj(q["lat"], q["lon"]) for q in g]
        if key == "park":
            p = clip_poly(p, BOX)
            if len(p) < 3 or area(p) < 20: continue
            out.append(d_poly(simplify(p, tol)))
        else:
            for run in split_outside(p, BOX):
                s = simplify(run, tol)
                if len(s) > 1 and sum(math.dist(s[i], s[i+1]) for i in range(len(s)-1)) >= minlen:
                    out.append(d_line(s))
    layers[key] = " ".join(out)

json.dump(layers, open(os.path.join(G, "layers.json"), "w"), ensure_ascii=False)
for k, v in layers.items():
    print("%-12s %8d chars" % (k, len(v)))
print("\n投影の検算:")
for nm, la, lo in [("浅草寺",35.7148,139.7967),("上野公園",35.7156,139.7730),("谷中銀座",35.7276,139.7663),
                   ("蔵前",35.7005,139.7912),("スカイツリー",35.7101,139.8107),("秋葉原",35.6984,139.7731),
                   ("清澄白河",35.6817,139.8000),("町屋",35.7420,139.7820)]:
    x,y = prj(la,lo); print("  %-8s (%6.0f,%6.0f)%s" % (nm,x,y," ← 画面外" if not(0<=x<=402 and 0<=y<=874) else ""))
