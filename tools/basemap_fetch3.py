import json, urllib.request, urllib.parse, os, time, sys
EPS=["https://overpass-api.de/api/interpreter","https://overpass.private.coffee/api/interpreter"]
BBOX="35.648,139.744,35.782,139.826"
G=os.path.dirname(os.path.abspath(__file__))
q='[out:json][timeout:180];way["highway"~"^(trunk|primary)$"]["area"!~"yes"](%s);out geom;'%BBOX
for ep in EPS:
    t=time.time()
    try:
        req=urllib.request.Request(ep,data=urllib.parse.urlencode({"data":q}).encode(),headers={"User-Agent":"tokyo-sozoro-dev"})
        raw=urllib.request.urlopen(req,timeout=200).read()
        json.loads(raw); open(os.path.join(G,"road.json"),"wb").write(raw)
        print("road ok %.1fs %d bytes (%s)"%(time.time()-t,len(raw),ep.split("/")[2])); sys.exit(0)
    except Exception as e: print("road retry:",e)
print("road failed")
