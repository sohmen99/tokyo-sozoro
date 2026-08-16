# -*- coding: utf-8 -*-
"""同じ形を2度描く（縁取り＋本体）ので、d は defs に一度だけ置いて use で参照する。"""
import json, os, io
G = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(G, "layers.json"), encoding="utf-8"))
def d(k): return L.get(k, "") or "M0 0"

svg = '''              <svg viewBox="0 0 402 874" aria-label="上野・浅草を中心とした広域図。混雑度つき">
                <defs>
                  <clipPath id="cp-ward"><path id="clip-ward-path"/></clipPath>
                  <filter id="f-heat" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="26"/></filter>
                  <path id="g-river" d="%(river)s"/>
                  <path id="g-road"  d="%(road)s"/>
                  <path id="g-rail"  d="%(rail)s"/>
                </defs>

                <!-- 周辺の区 -->
                <rect width="402" height="874" fill="var(--map-out)"/>
                <path d="%(others)s" fill="none" stroke="var(--map-case)" stroke-width="0.9" opacity="0.7"/>

                <!-- 緑地 -->
                <path d="%(park)s" fill="var(--map-green)"/>

                <!-- 台東区。ここだけ地色が明るい -->
                <path id="ward-fill" d="%(taito)s" fill="var(--map-land)"/>
                <g clip-path="url(#cp-ward)"><g id="buildings" fill="var(--map-block)"></g></g>

                <!-- 水面 -->
                <use href="#g-river" fill="none" stroke="var(--map-water)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
                <use href="#g-river" fill="none" stroke="var(--map-water-2)" stroke-width="0.9" opacity="0.7"/>

                <!-- 幹線 -->
                <use href="#g-road" fill="none" stroke="var(--map-case)" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/>
                <use href="#g-road" fill="none" stroke="var(--map-road)" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/>

                <!-- 鉄道 -->
                <use href="#g-rail" fill="none" stroke="var(--map-rail)" stroke-width="2.2"/>
                <use href="#g-rail" fill="none" stroke="var(--map-land)" stroke-width="0.9" stroke-dasharray="4 5"/>

                <!-- 区界 -->
                <path id="ward-line" d="%(taito)s" fill="none" stroke="var(--ai)" stroke-width="1.4" stroke-dasharray="6 4" opacity="0.7"/>

                <!-- 混雑ヒート。凡例・グラフと同じスケール -->
                <g id="heat" style="mix-blend-mode:multiply" filter="url(#f-heat)" opacity="0.85"></g>

                <!-- 地名 -->
                <g id="place-labels" font-family="Hiragino Sans, Yu Gothic, system-ui, sans-serif" font-size="9" font-weight="600" fill="#6D7581" letter-spacing="0.5"></g>
                <g id="minor-labels" font-family="Hiragino Sans, Yu Gothic, system-ui, sans-serif" font-size="7.5" fill="#8B929E" letter-spacing="0.3"></g>
              </svg>''' % {
  "others": d("ward_others"), "taito": d("ward_taito"), "park": d("park"),
  "river": d("river"), "road": d("road"), "rail": d("rail") }
io.open(os.path.join(G, "map.svg.txt"), "w", encoding="utf-8").write(svg)
print("svg", len(svg), "chars")
