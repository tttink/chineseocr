---
name: p5js
description: Create generative art, creative-coding sketches, interactive animations, flow fields, particle systems, posters and algorithmic visuals with p5.js (2.x). Use whenever the user asks for 生成艺术、算法艺术、创意编程、互动动画、粒子、噪声图案、海报背景、视觉实验, Processing-style sketches, or names p5 / p5.js. Covers the p5 2.x API changes from 1.x (async loading, splineVertex, bezierOrder), seeded reproducibility, performance and a design workflow for striking results.
---

# p5.js (2.x)

Pinned version: **p5@2.3.4**. A working starter lives at `templates/sketch.html` —
copy it and build from there.

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2.3.4/lib/p5.min.js"></script>
```

ESM is also shipped: `https://cdn.jsdelivr.net/npm/p5@2.3.4/lib/p5.esm.min.js`
(`import p5 from '...'`, then instance mode). npm: `npm i p5`.

## 1. p5 2.x vs 1.x — do not write 1.x code

Most examples online are 1.x. These differ in 2.x:

| 1.x (wrong now) | 2.x (use this) |
|---|---|
| `function preload() { img = loadImage(...) }` | `async function setup() { img = await loadImage(...); createCanvas(...) }` — every `loadX()` returns a Promise |
| `curveVertex(x, y)` / `curve()` / `curveTightness(t)` | `splineVertex(x, y)` / `spline()` / `splineProperty('tightness', t)` |
| `bezierVertex(cx1, cy1, cx2, cy2, x, y)` (6 args) | one point per call: start with `bezierVertex(x0, y0)` (or `vertex`), then 3 calls per cubic segment; `bezierOrder(2)` for quadratic |
| `if (mouseButton === LEFT)` | `if (mouseButton.left)` (object of booleans: `left`, `right`, `center`) |
| `p5.sound` bundled | separate add-on library; load it only if audio is needed |

`colorMode()` now also accepts `OKLCH`, `OKLAB`, `LCH`, `LAB` in addition to `RGB`,
`HSB`, `HSL`. OKLCH gives perceptually even palettes — prefer it for generative color.

If you must target 1.x (e.g. an existing project on `p5@1.11.x`), use 1.x syntax
consistently and say so.

## 2. Skeleton

```js
let seed;

function setup() {
  createCanvas(windowWidth, windowHeight);
  pixelDensity(Math.min(2, displayDensity()));
  seed = floor(random(1e9));
  regenerate();
}

function regenerate() {
  randomSeed(seed);
  noiseSeed(seed);
  // build the composition here; call redraw() if using noLoop()
}

function draw() { /* animate, or noLoop() for a static piece */ }

function windowResized() { resizeCanvas(windowWidth, windowHeight); regenerate(); }

function keyPressed() {
  if (key === 's') save(`art-${seed}.png`);
  if (key === 'r') { seed = floor(random(1e9)); regenerate(); }
}
```

**Instance mode** (use when embedding in a page with other code, multiple sketches,
or ES modules — avoids polluting globals):

```js
new p5((p) => {
  p.setup = () => { p.createCanvas(400, 400); };
  p.draw = () => { p.background(20); p.circle(p.mouseX, p.mouseY, 40); };
}, document.getElementById('sketch'));
```

## 3. Reproducibility is a feature

- Always seed both `randomSeed()` and `noiseSeed()` from one stored seed; show or log it
  and put it in saved filenames, so a good output can be regenerated.
- Expose a few meaningful parameters (density, palette, scale, turbulence) as constants
  at the top, or as sliders (`createSlider`) when the user wants to explore.

## 4. Core generative techniques (pick and combine)

- **Flow field:** angle = `noise(x * s, y * s, t) * TAU * k`; move many particles along
  it and draw short translucent strokes; never clear the background for trails.
- **Particle systems:** arrays of plain objects `{x, y, vx, vy}`; integrate with velocity
  + forces; cull dead ones by swap-and-pop rather than `splice` in hot loops.
- **Recursive subdivision:** split rectangles/triangles with a probability that falls
  with depth → Mondrian / brutalist grids.
- **Circle packing:** random candidates, reject overlaps, grow radii; use a spatial grid
  for speed past ~1k circles.
- **Noise landscapes / contour lines:** sample `noise()` on a grid, draw iso-lines or
  stacked offset lines (Joy-Division style).
- **Shape grammars / L-systems / truchet tiles** for pattern work.
- **Typography:** `font = await loadFont(url)`, then `textFont(font); textSize(160);`
  and `font.textToPoints(str, x, y, { sampleFactor: 0.2 })` to turn text into particles
  (2.x takes the size from `textSize()`; the 1.x `size` argument is gone). Points are
  `{ x, y, alpha }`.
- **WEBGL:** `createCanvas(w, h, WEBGL)`, `orbitControl()`, `normalMaterial()`,
  `buildGeometry(() => { ... })` to bake many primitives into one geometry,
  `createFilterShader(fragSrc)` + `filter(shader)` for full-screen GLSL effects.

## 5. Performance

- Use `noLoop()` for static pieces; render once, then `redraw()` on change.
- Avoid `get()`/`set()` per pixel. Use `loadPixels()`, write the `pixels` array
  (4 bytes per pixel, scaled by `pixelDensity()²`), then `updatePixels()`.
- Draw static layers once into `createGraphics()` buffers and `image()` them each frame.
- Batch many shapes inside one `beginShape()/endShape()` where possible.
- `drawingContext` exposes the raw Canvas2D context for gradients, `shadowBlur` glows,
  `globalCompositeOperation` blend tricks, and `filter = 'blur(4px)'`.
- Keep particle counts proportional to canvas area so phones stay smooth.

## 6. Design workflow for striking output

1. Decide the **concept** in one sentence (e.g. "ink drifting in a slow current"), then
   choose the technique that expresses it — technique serves concept.
2. **Palette:** 3–5 colors, one dominant background, one accent used sparingly. Work in
   OKLCH or HSB; vary lightness more than hue.
3. **Composition:** leave negative space, use margins (~8–10% of the short side), and
   bias density toward a focal area instead of uniform noise.
4. **Texture & finish:** low-alpha layering, subtle grain (random dots at alpha 5–15),
   `blendMode(MULTIPLY|SCREEN|ADD)` for richness.
5. **Iterate with seeds:** generate several seeds, keep the best, and save at high
   resolution (`pixelDensity(3)` or a larger offscreen `createGraphics`) for print.
6. Add `describe('...')` for an accessible text description of the canvas.
