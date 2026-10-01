---
name: d3js
description: Build custom, interactive data visualizations with D3.js v7 — bar/line/area/scatter charts, network/force graphs, trees, treemaps, sunbursts, maps, chord diagrams, animated transitions, zoom/brush and tooltips. Use whenever the user asks for 数据可视化、图表、交互式图表、力导向图、关系图、树图、地图可视化、仪表盘 that need more control than a charting library, or names d3 / D3.js. Covers loading, the margin convention, scales/axes, data joins, transitions, layouts, responsiveness, accessibility and v7 pitfalls.
---

# D3.js (v7)

Pinned version: **d3@7.9.0**. A working starter lives at `templates/chart.html` —
copy it and build from there. For chart-type choice, color palettes and dashboard
layout, also load the `dataviz` skill if it is available; this skill covers D3 mechanics.

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>   <!-- global d3 -->
```
```js
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";             // ES module
```
npm: `npm i d3`, then `import * as d3 from "d3"`. Map data in TopoJSON needs
`topojson-client` separately.

## 1. v7 pitfalls (old tutorials are v3–v5)

- No `d3.event`: listeners get `(event, d)` → `.on("click", (event, d) => ...)`.
- No `d3.mouse`/`d3.touch`: use `d3.pointer(event, container)`.
- Data loaders return Promises: `const data = await d3.csv(url, d3.autoType)`.
- `d3.nest` is gone: use `d3.group`, `d3.rollup`, `d3.index`, `d3.groups`, `d3.rollups`.
- Prefer `selection.join(...)` over manual enter/append/merge/exit.
- Arrow functions do not bind `this`; use `event.currentTarget` instead of `this`.

## 2. Margin convention + responsive SVG

```js
const width = 720, height = 420;
const margin = { top: 24, right: 24, bottom: 40, left: 48 };

const svg = d3.select("#chart").append("svg")
  .attr("viewBox", [0, 0, width, height])        // scales with container
  .attr("style", "max-width: 100%; height: auto;")
  .attr("role", "img")
  .attr("aria-label", "Monthly revenue, 2025");

const x = d3.scaleBand().domain(data.map(d => d.month)).range([margin.left, width - margin.right]).padding(0.2);
const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).nice().range([height - margin.bottom, margin.top]);

svg.append("g").attr("transform", `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x));
svg.append("g").attr("transform", `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(5, "~s"))
   .call(g => g.select(".domain").remove())
   .call(g => g.selectAll(".tick line").clone().attr("x2", width - margin.left - margin.right).attr("stroke-opacity", 0.1));
```

## 3. Scales cheat sheet

| Data | Scale |
|---|---|
| Quantity → position | `scaleLinear` (`.nice()`), `scaleLog`, `scaleSqrt` (use for circle area) |
| Dates | `scaleTime` / `scaleUtc` |
| Categories → position | `scaleBand` (bars), `scalePoint` (dots) |
| Categories → color | `scaleOrdinal(d3.schemeTableau10)` |
| Quantity → color | `scaleSequential(d3.interpolateViridis)`; diverging: `scaleDiverging(d3.interpolateRdBu)` |
| Bins | `scaleQuantize`, `scaleQuantile`, `scaleThreshold` |

Formatting: `d3.format(",.0f")`, `d3.format(".1%")`, `d3.format("~s")`, `d3.utcFormat("%b %Y")`.

## 4. Data join with keys and transitions (updatable charts)

```js
function update(data) {
  const t = svg.transition().duration(600).ease(d3.easeCubicOut);
  svg.select(".bars").selectAll("rect")
    .data(data, d => d.id)                       // key function = object constancy
    .join(
      enter => enter.append("rect")
        .attr("x", d => x(d.name)).attr("width", x.bandwidth())
        .attr("y", y(0)).attr("height", 0)
        .call(e => e.transition(t).attr("y", d => y(d.value)).attr("height", d => y(0) - y(d.value))),
      update => update.call(u => u.transition(t)
        .attr("x", d => x(d.name)).attr("width", x.bandwidth())
        .attr("y", d => y(d.value)).attr("height", d => y(0) - y(d.value))),
      exit => exit.call(e => e.transition(t).attr("height", 0).attr("y", y(0)).remove())
    );
}
```

Build static scaffolding (axes groups, `<g class="bars">`) once; on update change scale
domains, re-`call` axes with a transition, and re-join marks. Never rebuild the whole SVG.

## 5. Shapes and layouts

- Lines/areas: `d3.line().x(...).y(...).curve(d3.curveMonotoneX)`, `d3.area()`, `.defined(d => d.value != null)` for gaps.
- Stacks: `d3.stack().keys(keys)(data)`; pies: `d3.pie()` + `d3.arc()`.
- Force graph: `d3.forceSimulation(nodes).force("link", d3.forceLink(links).id(d => d.id)).force("charge", d3.forceManyBody().strength(-60)).force("center", d3.forceCenter(cx, cy)).force("collide", d3.forceCollide(r))`, update positions in `.on("tick", ...)`, add `d3.drag()` that sets `fx/fy` and `alphaTarget(0.3).restart()`.
- Hierarchy: `d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value)` then
  `d3.tree()`, `d3.cluster()`, `d3.treemap().tile(d3.treemapSquarify)`, `d3.pack()`, `d3.partition()` (sunburst). Tabular parent/child data → `d3.stratify()`.
- Maps: `d3.geoPath(d3.geoNaturalEarth1().fitSize([w, h], geojson))`; Chinese provinces
  etc. work with any GeoJSON (`fitSize` handles projection scale/center).
- Others: `d3.chord`, `d3.contourDensity`, `d3.Delaunay.from(points).voronoi([...])`
  (great for hover hit-areas on scatter plots), `d3.bin()` for histograms.

## 6. Interaction

- Tooltip: one absolutely positioned `<div>`; on `pointermove` set text and position from
  `event.pageX/pageY`; hide on `pointerleave`. Keep hit targets ≥ 24px (use Voronoi or
  invisible wider strokes for lines).
- Nearest point on a line chart: `d3.bisector(d => d.date).center(data, x.invert(px))`.
- Zoom/pan: `svg.call(d3.zoom().scaleExtent([1, 8]).on("zoom", ({ transform }) => g.attr("transform", transform)))`;
  for axes, rescale with `transform.rescaleX(x)`.
- Brush: `d3.brushX().extent([[x0, y0], [x1, y1]]).on("end", ({ selection }) => ...)`.

## 7. Scale & performance

- SVG is fine up to a few thousand marks. Beyond ~5k, draw marks on `<canvas>` (D3 shapes
  accept a canvas context: `d3.line().context(ctx)`, `d3.geoPath(projection, ctx)`) and keep
  SVG only for axes; use `d3.quadtree` for hit-testing.
- Run force simulations for large graphs with fewer ticks or in a Web Worker.

## 8. Accessibility & polish

- `role="img"` + `aria-label` (or `<title>`/`<desc>`) on the SVG; consider a visually
  hidden data table for screen readers.
- Label directly at the end of lines instead of a legend when there are ≤ 5 series.
- Remove chart junk: drop the y-axis domain line, use faint gridlines, start bar axes at
  zero, use `tabular-nums` for numbers, keep consistent color meaning across views.
- Respect `prefers-reduced-motion` by setting transition duration to 0.
- Support dark mode by using `currentColor` and CSS variables for text/gridline colors.
