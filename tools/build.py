# -*- coding: utf-8 -*-
"""東京都オープンデータ（各区の文化財一覧・台東区伝統工芸職人一覧）を、
   アプリに載せる形へ落とす。地図の範囲内だけ、必要な列だけ。"""
import csv, io, json, glob, os, math, re
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LAT0, LON0, CX, CY, MPP = 35.7152, 139.7849, 201.0, 437.0, 16.0
KX = 111320*math.cos(math.radians(LAT0))/MPP; KY = 111132/MPP
def inrange(la, lo):
    x = CX+(lo-LON0)*KX; y = CY-(la-LAT0)*KY
    return -30 <= x <= 432 and -30 <= y <= 904

def load(p):
    raw = open(p, "rb").read()
    for enc in ("utf-8-sig", "cp932"):
        try: return list(csv.DictReader(io.StringIO(raw.decode(enc))))
        except Exception: pass
    return []

# 指定の重み。国のものほど遠くから人を呼ぶ。
def weight(cls, kind):
    t = (cls or "") + (kind or "")
    if "国" in t or "重要文化財" in t or "登録有形" in t: return 1.0
    if "都" in t or "東京都" in t: return 0.7
    return 0.45

# 訪ねられるもの＝建造物・史跡。美術工芸品は館の中なので行き先にはしない。
def visitable(cls, kind):
    t = (cls or "") + (kind or "")
    return ("建造物" in t) or ("史跡" in t) or ("名勝" in t) or ("天然記念物" in t)

heritage, spots = [], []
WARD = {"arakawa":"荒川区","chiyoda":"千代田区","chuo":"中央区","koto":"江東区","sumida":"墨田区"}
for p in glob.glob("od/bunka_*.csv"):
    w = WARD.get(os.path.basename(p)[6:-4])
    if not w: continue
    for r in load(p):
        try: la = float(r["緯度"]); lo = float(r["経度"])
        except Exception: continue
        if not inrange(la, lo): continue
        cls, kind = (r.get("文化財分類") or ""), (r.get("種類") or "")
        wt = weight(cls, kind)
        heritage.append([round(la,5), round(lo,5), wt])
        if visitable(cls, kind):
            nm = re.sub(r"\s+", "", (r.get("名称") or "").strip())
            if not nm: continue
            spots.append({"n": nm, "la": round(la,5), "lo": round(lo,5), "w": wt,
                          "k": (kind or cls or "文化財").strip()[:12], "ward": w})

craft = []
for r in load("od/craft.csv"):
    try: la = float(r["緯度"]); lo = float(r["経度"])
    except Exception: continue
    craft.append({"n": (r.get("屋号・会社名") or "").strip(), "la": round(la,5), "lo": round(lo,5),
                  "k": (r.get("業種名") or "").strip(), "ward": "台東区"})

# 同じ座標に複数あるものは1つに寄せる
def dedupe(rows, keyf):
    seen, out = set(), []
    for r in rows:
        k = keyf(r)
        if k in seen: continue
        seen.add(k); out.append(r)
    return out
spots = dedupe(spots, lambda r: (round(r["la"],4), round(r["lo"],4)))
craft = dedupe(craft, lambda r: (round(r["la"],4), round(r["lo"],4)))

json.dump({"heritage": heritage, "spots": spots, "craft": craft},
          open("od/od.json","w"), ensure_ascii=False, separators=(",",":"))
print("密度用の文化財 %d件 / 行き先になる文化財 %d件 / 職人の工房 %d件" % (len(heritage), len(spots), len(craft)))
print("od.json", os.path.getsize("od/od.json"), "bytes")

# ── 各ランドマークでの文化財密度を確かめる ──
LM = [("浅草寺",35.7148,139.7967),("スカイツリー",35.7101,139.8107),("アメ横",35.7089,139.7741),
      ("秋葉原",35.6984,139.7731),("上野動物園",35.7167,139.7714),("上野公園",35.7156,139.7730),
      ("東京国立博物館",35.7188,139.7766),("上野駅",35.7141,139.7774),("錦糸町",35.6966,139.8145),
      ("両国",35.6970,139.7933),("湯島天満宮",35.7076,139.7679),("北千住",35.7497,139.8047),
      ("浅草橋",35.6989,139.7860),("谷中銀座",35.7276,139.7663),("かっぱ橋",35.7133,139.7887),
      ("蔵前",35.7005,139.7912),("日暮里繊維街",35.7263,139.7734),("根津神社",35.7203,139.7607),
      ("清澄白河",35.6817,139.8000),("町屋",35.7420,139.7820),("向島百花園",35.7264,139.8146)]
R = 6371000.0
def dist(a,b,c,d):
    dla=math.radians(c-a); dlo=math.radians(d-b)
    s=math.sin(dla/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(s))
SIG = 380.0
res=[]
for nm,la,lo in LM:
    s=0.0
    for h in heritage:
        d=dist(la,lo,h[0],h[1])
        if d<1200: s += h[2]*math.exp(-(d*d)/(2*SIG*SIG))
    res.append((nm,s))
mx=max(r[1] for r in res) or 1
print("\n── 指定文化財の重み付き密度（正規化）")
for nm,s in sorted(res,key=lambda r:-r[1]):
    print("  %-13s %5.2f  %s" % (nm, s/mx, "█"*int(s/mx*36)))
