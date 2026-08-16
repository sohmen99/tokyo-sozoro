import json, urllib.request, urllib.parse, os, time, sys
G=os.path.dirname(os.path.abspath(__file__))
A="around:3600,35.7152,139.7849"
Q='[out:json][timeout:180];(nwr["leisure"~"^(park|garden)$"]["name"](%s);nwr["tourism"="attraction"]["name"](%s););out center 2500;'%(A,A)
for ep in ["https://overpass-api.de/api/interpreter","https://overpass.private.coffee/api/interpreter"]:
    try:
        r=urllib.request.Request(ep,data=urllib.parse.urlencode({"data":Q}).encode(),headers={"User-Agent":"tokyo-sozoro-dev"})
        raw=urllib.request.urlopen(r,timeout=200).read(); json.loads(raw)
        open(os.path.join(G,"green.json"),"wb").write(raw); print("ok",len(raw),"bytes"); sys.exit(0)
    except Exception as e: print("retry:",e)
sys.exit(1)
