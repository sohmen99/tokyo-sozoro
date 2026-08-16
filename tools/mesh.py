# -*- coding: utf-8 -*-
"""国土交通省「全国の人流オープンデータ」(1kmメッシュ) から、地図の範囲だけ取り出す。
   2019年10月＝コロナ前の平常月を使う。"""
import csv, io, json, math, os, collections
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = "od/mesh/13/2019/10/monthly_mdp_mesh1km.csv"

def mesh_center(code):
    c = str(code)
    p, u = int(c[0:2]), int(c[2:4])
    q, v = int(c[4]), int(c[5])
    r, w = int(c[6]), int(c[7])
    lat = (p*40 + q*5 + r*0.5) / 60
    lon = 100 + u + v*7.5/60 + w*45/3600
    return lat + 0.25/60, lon + 22.5/3600          # セル中心

LAT0, LON0, CX, CY, MPP = 35.7152, 139.7849, 201.0, 437.0, 16.0
KX = 111320*math.cos(math.radians(LAT0))/MPP; KY = 111132/MPP

cells = collections.defaultdict(dict)
for row in csv.DictReader(io.open(SRC, encoding="utf-8")):
    mid = row["mesh1kmid"]
    key = (row["dayflag"], row["timezone"])
    cells[mid][key] = int(row["population"])

out = []
for mid, v in cells.items():
    la, lo = mesh_center(mid)
    x = CX + (lo-LON0)*KX; y = CY - (la-LAT0)*KY
    if not (-60 <= x <= 462 and -60 <= y <= 934): continue
    hd = v.get(("2","1"), 0)      # 休日・昼
    wd = v.get(("1","1"), 0)      # 平日・昼
    nt = v.get(("0","2"), 0)      # 全日・夜
    out.append({"m": mid, "la": round(la,5), "lo": round(lo,5), "hd": hd, "wd": wd, "nt": nt})

out.sort(key=lambda r: -r["hd"])
json.dump(out, open("od/mesh_taito.json","w"), separators=(",",":"))
print("範囲内のメッシュ %d 個   %d bytes" % (len(out), os.path.getsize("od/mesh_taito.json")))

def near(la, lo):
    best = min(out, key=lambda r: (r["la"]-la)**2 + ((r["lo"]-lo)*0.81)**2)
    return best

LM = [("浅草寺",35.7148,139.7967),("スカイツリー",35.7101,139.8107),("アメ横",35.7089,139.7741),
      ("秋葉原",35.6984,139.7731),("上野公園",35.7156,139.7730),("上野駅",35.7141,139.7774),
      ("錦糸町",35.6966,139.8145),("両国",35.6970,139.7933),("湯島天満宮",35.7076,139.7679),
      ("北千住",35.7497,139.8047),("浅草橋",35.6989,139.7860),("谷中銀座",35.7276,139.7663),
      ("かっぱ橋",35.7133,139.7887),("蔵前",35.7005,139.7912),("日暮里繊維街",35.7263,139.7734),
      ("根津神社",35.7203,139.7607),("清澄白河",35.6817,139.8000),("町屋",35.7420,139.7820),
      ("向島百花園",35.7264,139.8146)]
print("\n%-13s %8s %8s %8s   %s" % ("", "休日昼", "平日昼", "夜", "休日昼/夜（外から来る度合い）"))
rows=[]
for nm, la, lo in LM:
    c = near(la, lo)
    ratio = c["hd"] / max(c["nt"], 1)
    rows.append((nm, c, ratio))
for nm, c, ratio in sorted(rows, key=lambda r: -r[2]):
    print("  %-12s %8d %8d %8d   %5.2f  %s" % (nm, c["hd"], c["wd"], c["nt"], ratio, "█"*int(min(ratio,6)*6)))
