import json, html, os
data = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'targets.json')))
order = sorted(data.items(), key=lambda kv: -len(kv[1]['places']))
LAYER = {'体験する':('exp','体'), '街を見る':('see','街'), '静かに歩く':('walk','静')}
total = sum(len(v['places']) for _, v in order)

def esc(s): return html.escape(s or '')

sections = []
for m, v in order:
    ps = v['places']
    rows = []
    for i, p in enumerate(ps, 1):
        cls, mark = LAYER[p['layer']]
        cats = '・'.join(p['cats'])
        dup = f'<span class="dup">同一地点で{len(p["ids"])}行</span>' if len(p['ids']) > 1 else ''
        desc = '<span class="has">説明あり</span>' if p['hd'] else ''
        key = f'{m}-{i}'
        rows.append(f'''<li class="row" data-key="{key}">
<span class="num">{i}</span>
<span class="lay {cls}" title="{esc(p['layer'])}">{mark}</span>
<span class="who"><b>{esc(p['name'])}</b><span class="cat">{esc(cats)}{dup}{desc}</span>
<a class="addr" href="https://maps.google.com/?q={p['lat']},{p['lon']}" target="_blank" rel="noopener">{esc(p['address'])}</a>
<span class="tea">現在：{esc(p['teaser'])}</span></span>
<span class="chk">
<label><input type="checkbox" data-k="{key}:p"><span>写真</span></label>
<label><input type="checkbox" data-k="{key}:t"><span>一行</span></label>
<label><input type="checkbox" data-k="{key}:d"><span>説明</span></label>
</span></li>''')
    sections.append(f'''<section class="ward" id="w-{esc(m)}">
<h2><span class="wname">{esc(m)}</span><span class="wmeta"><b>{len(ps)}</b>地点 ／ 歩行 <b>{v['walk']:,}</b>m ／ <span class="prog" data-ward="{esc(m)}">0/{len(ps)*3}</span></span></h2>
<ol class="rows">{''.join(rows)}</ol></section>''')

nav = ''.join(f'<a href="#w-{esc(m)}">{esc(m)}<i>{len(v["places"])}</i></a>' for m, v in order)

open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'yacho.html'),'w').write(f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Tokyo sozoro の撮影と取材の割り当て表。台東区24町字・157地点、徒歩順路つき。">
<meta name="theme-color" content="#EFF2F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11151A" media="(prefers-color-scheme: dark)">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22><text y=%2226%22 font-size=%2226%22>&#128247;</text></svg>">
<title>そぞろ野帳</title>
<style>
:root{{
  --ground:#EFF2F1; --surface:#FBFCFB; --raise:#E4E9E7;
  --ink:#12181C; --mid:#4E5A63; --faint:#7E8A91; --rule:#D3DAD8;
  --accent:#22417F; --exp:#22417F; --see:#8A4B2E; --walk:#3F6F4F;
  --warn:#8C2F26; --warnbg:#F6E7E4;
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  --ground:#11151A; --surface:#181E24; --raise:#222A31;
  --ink:#E4E9E7; --mid:#A6B2B8; --faint:#7C888E; --rule:#2B343B;
  --accent:#8FAEE6; --exp:#8FAEE6; --see:#D89574; --walk:#7FBE92;
  --warn:#E89184; --warnbg:#2C1D1B;
}} }}
:root[data-theme="dark"]{{
  --ground:#11151A; --surface:#181E24; --raise:#222A31;
  --ink:#E4E9E7; --mid:#A6B2B8; --faint:#7C888E; --rule:#2B343B;
  --accent:#8FAEE6; --exp:#8FAEE6; --see:#D89574; --walk:#7FBE92;
  --warn:#E89184; --warnbg:#2C1D1B;
}}
*{{box-sizing:border-box}}
body{{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP",system-ui,sans-serif;
  font-size:15px; line-height:1.7; -webkit-text-size-adjust:100%;
}}
.wrap{{max-width:760px; margin:0 auto; padding:0 18px 96px}}
h1,h2,.mincho{{font-family:"Hiragino Mincho ProN","Yu Mincho",YuMincho,"Noto Serif JP",serif; font-weight:600}}
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-variant-numeric:tabular-nums}}

header{{padding:44px 0 26px; border-bottom:1px solid var(--rule)}}
h1{{margin:0; font-size:34px; letter-spacing:.06em; line-height:1.25; text-wrap:balance}}
.sub{{margin:.5rem 0 0; color:var(--mid); font-size:14px}}
.stat{{display:flex; gap:26px; margin-top:20px; flex-wrap:wrap}}
.stat div{{display:flex; flex-direction:column}}
.stat b{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-variant-numeric:tabular-nums;
  font-size:26px; font-weight:600; line-height:1.1}}
.stat span{{font-size:11px; letter-spacing:.14em; color:var(--faint)}}

.brief{{display:flex; flex-direction:column; gap:14px; margin:26px 0 8px}}
.rule{{background:var(--warnbg); border-left:3px solid var(--warn); padding:14px 16px; border-radius:0 4px 4px 0}}
.rule h3{{margin:0 0 4px; font-size:14px; color:var(--warn); letter-spacing:.04em}}
.rule p{{margin:0; font-size:13.5px; color:var(--ink)}}
.rule code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.5px;
  background:var(--surface); padding:1px 5px; border-radius:3px}}
.set{{background:var(--surface); border:1px solid var(--rule); border-radius:5px; padding:14px 16px}}
.set h3{{margin:0 0 6px; font-size:14px; letter-spacing:.04em}}
.set p{{margin:0; font-size:13.5px; color:var(--mid)}}

nav{{display:flex; flex-wrap:wrap; gap:5px; margin:26px 0 4px}}
nav a{{display:inline-flex; align-items:baseline; gap:5px; padding:4px 9px; border:1px solid var(--rule);
  border-radius:3px; background:var(--surface); color:var(--ink); text-decoration:none; font-size:12.5px}}
nav a i{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-style:normal;
  font-variant-numeric:tabular-nums; font-size:11px; color:var(--faint)}}
nav a:hover,nav a:focus-visible{{border-color:var(--accent); color:var(--accent); outline:none}}

.ward{{margin-top:34px}}
.ward h2{{display:flex; align-items:baseline; justify-content:space-between; gap:14px; flex-wrap:wrap;
  margin:0 0 8px; padding-bottom:7px; border-bottom:1px solid var(--rule); font-size:21px; letter-spacing:.05em}}
.wmeta{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-variant-numeric:tabular-nums;
  font-size:11.5px; letter-spacing:0; color:var(--faint); font-weight:400}}
.wmeta b{{color:var(--mid); font-weight:600}}
.prog{{color:var(--accent)}}

.rows{{list-style:none; margin:0; padding:0; display:flex; flex-direction:column}}
.row{{display:grid; grid-template-columns:26px 22px 1fr auto; gap:10px; align-items:start;
  padding:11px 0; border-bottom:1px solid var(--rule)}}
.row:last-child{{border-bottom:none}}
.num{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-variant-numeric:tabular-nums;
  font-size:12px; color:var(--faint); padding-top:3px; text-align:right}}
.lay{{width:22px; height:22px; border-radius:3px; display:grid; place-items:center;
  font-size:12px; color:var(--surface); margin-top:1px}}
.lay.exp{{background:var(--exp)}} .lay.see{{background:var(--see)}} .lay.walk{{background:var(--walk)}}
:root[data-theme="dark"] .lay, :root:not([data-theme="light"]) .lay{{color:var(--ground)}}
.who{{display:flex; flex-direction:column; gap:1px; min-width:0}}
.who b{{font-size:15px; font-weight:600; line-height:1.45}}
.cat{{font-size:12px; color:var(--faint)}}
.dup{{margin-left:7px; color:var(--warn)}}
.has{{margin-left:7px; color:var(--walk)}}
.addr{{font-size:12px; color:var(--mid); text-decoration:none; border-bottom:1px dotted var(--rule); align-self:flex-start}}
.addr:hover,.addr:focus-visible{{color:var(--accent); border-bottom-color:var(--accent); outline:none}}
.tea{{font-size:11.5px; color:var(--faint); margin-top:2px}}
.chk{{display:flex; gap:4px; padding-top:2px}}
.chk label{{cursor:pointer; user-select:none}}
.chk input{{position:absolute; opacity:0; width:0; height:0}}
.chk span{{display:block; font-size:10.5px; letter-spacing:.06em; padding:3px 6px; border-radius:3px;
  border:1px solid var(--rule); color:var(--faint); background:var(--surface); white-space:nowrap}}
.chk input:checked+span{{background:var(--accent); border-color:var(--accent); color:var(--surface)}}
:root[data-theme="dark"] .chk input:checked+span,
:root:not([data-theme="light"]) .chk input:checked+span{{color:var(--ground)}}
.chk input:focus-visible+span{{outline:2px solid var(--accent); outline-offset:1px}}

footer{{margin-top:44px; padding-top:16px; border-top:1px solid var(--rule); font-size:12px; color:var(--faint)}}
footer p{{margin:.35rem 0}}
@media (max-width:560px){{
  .row{{grid-template-columns:22px 20px 1fr; gap:8px}}
  .chk{{grid-column:3; padding-top:5px}}
  h1{{font-size:27px}}
}}
</style>
</head>
<body>
<div class="wrap">
<header>
<h1>そぞろ野帳</h1>
<p class="sub">Tokyo sozoro ／ 撮影と取材の割り当て　—　台東区 {len(order)}町字・{total}地点</p>
<div class="stat">
<div><b>{total}</b><span>地点</span></div>
<div><b>{len(order)}</b><span>町字</span></div>
<div><b>{total*3}</b><span>作業</span></div>
<div><b class="prog-all">0</b><span>完了</span></div>
</div>
</header>

<div class="brief">
<div class="rule">
<h3>浅草・上野・雷門・上野公園・西浅草・花川戸では撮らない</h3>
<p>混雑除外で候補から消えるため、撮っても1枚も使われません。実測で確認済み（雷門起点75案・上野起点45案、一度も出ない）。<b>谷中・池之端・上野桜木も除外</b>しています。月係数の高い11月には混雑判定に入り、消えるためです。</p>
</div>
<div class="set">
<h3>1地点につき3つ。写真だけでは画面は変わりません</h3>
<p><b>写真</b>… 横位置1枚。看板より、通りから見た佇まいを。抽選カードでは<b>ぼかして</b>出るので、色と明るさが伝わればいい。<br>
<b>一行</b>… 正体を伏せたまま「行ってみるか」と思わせる一行。現在は3文を6,052件で使い回しています。<br>
<b>説明</b>… 到着後に名前と一緒に出す2〜3行。何の店か、何を作っているか、いつからあるか。</p>
</div>
</div>

<nav>{nav}</nav>
{''.join(sections)}

<footer>
<p>対象は「体験する・街を見る・静かに歩く」のうち写真が無く、抽選に出る町字にあるもの。重複行は同一地点として統合済み（173行→{total}地点）。</p>
<p>順番は各町字の最北から最近傍でつないだ徒歩順路です。住所をタップすると地図が開きます。チェックはこの端末に保存されます。</p>
<p>出典：台東区オープンデータ（CC-BY表示4.0国際）。本作品の内容について、台東区は一切保証しないものとする。</p>
</footer>
</div>
<script>
(function(){{
  var K='sozoro-yacho-v1';
  var st={{}}; try{{ st=JSON.parse(localStorage.getItem(K)||'{{}}'); }}catch(e){{}}
  var boxes=[].slice.call(document.querySelectorAll('.chk input'));
  boxes.forEach(function(b){{
    if(st[b.dataset.k]) b.checked=true;
    b.addEventListener('change',function(){{
      if(b.checked) st[b.dataset.k]=1; else delete st[b.dataset.k];
      try{{ localStorage.setItem(K,JSON.stringify(st)); }}catch(e){{}}
      paint();
    }});
  }});
  function paint(){{
    var all=0;
    [].forEach.call(document.querySelectorAll('.ward'),function(w){{
      var bs=w.querySelectorAll('.chk input'), n=0;
      [].forEach.call(bs,function(b){{ if(b.checked) n++; }});
      all+=n;
      w.querySelector('.prog').textContent=n+'/'+bs.length;
    }});
    document.querySelector('.prog-all').textContent=all;
  }}
  paint();
}})();
</script>
</body>
</html>
''')
print('written')
