# -*- coding: utf-8 -*-
import json, urllib.request, urllib.parse, sys, os, time
EP = "https://overpass-api.de/api/interpreter"
BBOX = "35.648,139.744,35.782,139.826"
OUT = os.path.dirname(os.path.abspath(__file__))

Q = {
 "ward": '[out:json][timeout:90];rel["boundary"="administrative"]["admin_level"="7"]["name"~"台東区|荒川区|墨田区|文京区|千代田区|中央区|江東区|北区"](%s);out geom;' % BBOX,
 "water": '[out:json][timeout:90];(way["natural"="water"](%s);way["waterway"="riverbank"](%s);rel["natural"="water"](%s););out geom;' % (BBOX,BBOX,BBOX),
 "river": '[out:json][timeout:60];way["waterway"="river"](%s);out geom;' % BBOX,
 "rail":  '[out:json][timeout:90];way["railway"~"^(rail|subway)$"]["service"!~"."](%s);out geom;' % BBOX,
 "road":  '[out:json][timeout:90];way["highway"~"^(trunk|primary|secondary)$"](%s);out geom;' % BBOX,
 "park":  '[out:json][timeout:90];(way["leisure"~"^(park|garden)$"](%s);rel["leisure"="park"](%s););out geom;' % (BBOX,BBOX),
}
for name, q in Q.items():
    p = os.path.join(OUT, name + ".json")
    if os.path.exists(p) and os.path.getsize(p) > 200:
        print("skip", name); continue
    t = time.time()
    try:
        req = urllib.request.Request(EP, data=urllib.parse.urlencode({"data": q}).encode(),
                                     headers={"User-Agent": "tokyo-sozoro-dev"})
        raw = urllib.request.urlopen(req, timeout=120).read()
        open(p, "wb").write(raw)
        d = json.loads(raw)
        print("%-6s %6.1fs  %6d elements  %8d bytes" % (name, time.time()-t, len(d.get("elements",[])), len(raw)))
    except Exception as e:
        print("%-6s FAILED: %s" % (name, e)); sys.exit(1)
