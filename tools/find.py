import json, urllib.request, urllib.parse, sys
def api(q, rows=30):
    u = "https://catalog.data.metro.tokyo.lg.jp/api/3/action/package_search?q=%s&rows=%d" % (urllib.parse.quote(q), rows)
    return json.load(urllib.request.urlopen(u, timeout=40))["result"]["results"]
want = [("観光ポイント 台東区","台東区","観光ポイント"),
        ("台東区伝統工芸職人一覧","台東区","伝統工芸"),
        ("食品衛生営業施設一覧 台東区","台東区","食品衛生"),
        ("観光客数等実態調査","東京都産業労働局","観光客数")]
out = {}
for q, org, key in want:
    for p in api(q):
        if org in p.get("organization",{}).get("title","") and key in p.get("title",""):
            res = [r for r in p["resources"] if (r.get("format") or "").upper() in ("CSV","XLSX")]
            if not res: continue
            out.setdefault(key, []).append({"title": p["title"], "org": p["organization"]["title"],
                "res": [{"name": r.get("name"), "url": r.get("url"), "fmt": r.get("format")} for r in res]})
for k, v in out.items():
    print("════", k)
    for p in v[:3]:
        print("  ", p["title"][:60], "|", p["org"])
        for r in p["res"][:3]: print("      -", (r["name"] or "")[:44], r["fmt"], r["url"][:110])
json.dump(out, open("od/found.json","w"), ensure_ascii=False, indent=1)
