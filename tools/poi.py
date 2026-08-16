import json, urllib.request, urllib.parse, os, time, sys
G=os.path.dirname(os.path.abspath(__file__))
EPS=["https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter","https://overpass.private.coffee/api/interpreter"]
# 混雑の中心（浅草寺・上野公園）から徒歩67分ぶん＝直線4.2km。
# 60分を選んだ人の許容が ±7分なので、その外側まで候補を持っておく。
A=["around:4200,35.7148,139.7967","around:4200,35.71538,139.7734"]
Q=('[out:json][timeout:600];(' + ''.join(
   'nwr["amenity"~"^(cafe|restaurant|fast_food|bar|pub|ice_cream)$"]["name"](%s);'
   'nwr["shop"~"^(bakery|confectionery|greengrocer|tea|coffee)$"]["name"](%s);'
   'nwr["leisure"~"^(park|garden)$"]["name"](%s);'
   'nwr["tourism"~"^(attraction|museum|artwork|viewpoint)$"]["name"](%s);' % (a,a,a,a)
   for a in A) + ');out center 20000;')
for ep in EPS:
    t=time.time()
    try:
        r=urllib.request.Request(ep,data=urllib.parse.urlencode({"data":Q}).encode(),headers={"User-Agent":"tokyo-sozoro-dev"})
        raw=urllib.request.urlopen(r,timeout=200).read()
        json.loads(raw); open(os.path.join(G,"poi.json"),"wb").write(raw)
        print("ok %.1fs %d bytes (%s)"%(time.time()-t,len(raw),ep.split("/")[2])); sys.exit(0)
    except Exception as e: print("retry:",e)
print("failed"); sys.exit(1)
