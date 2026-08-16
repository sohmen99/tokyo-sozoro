import json, urllib.request, urllib.parse, os, time, sys
G=os.path.dirname(os.path.abspath(__file__))
EPS=["https://overpass-api.de/api/interpreter","https://overpass.private.coffee/api/interpreter"]
AROUND="around:3600,35.7152,139.7849"
Q=('[out:json][timeout:180];('
   'nwr["amenity"~"^(cafe|restaurant|fast_food|bar|pub|ice_cream)$"]["name"](%s);'
   'nwr["shop"~"^(bakery|confectionery|greengrocer|tea|coffee)$"]["name"](%s);'
   'nwr["leisure"~"^(park|garden)$"]["name"](%s);'
   ');out center 4000;') % (AROUND,AROUND,AROUND)
for ep in EPS:
    t=time.time()
    try:
        r=urllib.request.Request(ep,data=urllib.parse.urlencode({"data":Q}).encode(),headers={"User-Agent":"tokyo-sozoro-dev"})
        raw=urllib.request.urlopen(r,timeout=200).read()
        json.loads(raw); open(os.path.join(G,"poi.json"),"wb").write(raw)
        print("ok %.1fs %d bytes (%s)"%(time.time()-t,len(raw),ep.split("/")[2])); sys.exit(0)
    except Exception as e: print("retry:",e)
print("failed"); sys.exit(1)
