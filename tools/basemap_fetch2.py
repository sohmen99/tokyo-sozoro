# -*- coding: utf-8 -*-
import json, urllib.request, urllib.parse, sys, os, time
EPS = ["https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter"]
BBOX = "35.648,139.744,35.782,139.826"
OUT = os.path.dirname(os.path.abspath(__file__))
Q = {
 "water": '[out:json][timeout:120];(way["natural"="water"](%s);way["waterway"="riverbank"](%s););out geom;' % (BBOX,BBOX),
 "river": '[out:json][timeout:120];way["waterway"="river"](%s);out geom;' % BBOX,
 "rail":  '[out:json][timeout:120];way["railway"="rail"]["service"!~"."](%s);out geom;' % BBOX,
 "road":  '[out:json][timeout:120];way["highway"~"^(trunk|primary)$"](%s);out geom;' % BBOX,
 "park":  '[out:json][timeout:120];way["leisure"~"^(park|garden)$"](%s);out geom;' % BBOX,
}
for name, q in Q.items():
    p = os.path.join(OUT, name + ".json")
    if os.path.exists(p) and os.path.getsize(p) > 200:
        print("skip", name); continue
    ok = False
    for ep in EPS:
        t = time.time()
        try:
            req = urllib.request.Request(ep, data=urllib.parse.urlencode({"data": q}).encode(),
                                         headers={"User-Agent": "tokyo-sozoro-dev"})
            raw = urllib.request.urlopen(req, timeout=150).read()
            d = json.loads(raw)
            open(p, "wb").write(raw)
            print("%-6s %6.1fs  %5d elements  %8d bytes  (%s)" % (name, time.time()-t, len(d.get("elements",[])), len(raw), ep.split("/")[2]))
            ok = True; break
        except Exception as e:
            print("%-6s  retry (%s): %s" % (name, ep.split("/")[2], e))
    if not ok: print("%-6s GAVE UP" % name)
