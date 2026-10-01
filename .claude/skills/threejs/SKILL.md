---
name: threejs
description: Build 3D scenes, WebGL/WebGPU graphics, product showcases, particle systems, shaders and interactive 3D web pages with Three.js (r186). Use whenever the user asks for anything 3D in the browser — 3D场景、三维可视化、3D产品展示、粒子效果、着色器、WebGL、模型加载(glTF)、相机动画 — or names three.js / THREE. Covers CDN import maps, the render loop, lighting and color management, performance, post-processing and common black-screen pitfalls.
---

# Three.js (r186)

Pinned version: **three@0.186.1**. A working starter lives at `templates/scene.html` —
copy it and build from there instead of writing boilerplate from memory.

## 1. Loading (no build step)

Three.js is ES-module only. Use an import map; `three/addons/` maps to `examples/jsm/`.

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"
  }
}
</script>
<script type="module">
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
</script>
```

- Always pin the version in both entries; addons and core must match.
- Never use the old `build/three.min.js` global build or `examples/js/` — both are gone.
- In a bundler project: `npm i three` and `import * as THREE from 'three'`,
  `import { OrbitControls } from 'three/addons/controls/OrbitControls.js'`.

Common addon paths (all under `three/addons/`): `controls/OrbitControls.js`,
`loaders/GLTFLoader.js`, `loaders/DRACOLoader.js`, `loaders/HDRLoader.js`,
`environments/RoomEnvironment.js`, `postprocessing/EffectComposer.js`,
`postprocessing/RenderPass.js`, `postprocessing/UnrealBloomPass.js`,
`postprocessing/OutputPass.js`, `utils/BufferGeometryUtils.js`.

## 2. Core skeleton

```js
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // cap: 3x DPR kills fill rate
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;          // or AgXToneMapping / NeutralToneMapping
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(3, 2, 5);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;            // requires controls.update() every frame

const timer = new THREE.Timer();          // THREE.Clock is deprecated since r183
timer.connect(document);                  // pauses delta while the tab is hidden

renderer.setAnimationLoop((time) => {     // prefer over manual requestAnimationFrame (needed for WebXR)
  timer.update(time);
  const dt = timer.getDelta(), t = timer.getElapsed();
  controls.update();
  renderer.render(scene, camera);
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

## 3. Color, light and materials (where most "looks bad" comes from)

- **Color management is on by default.** Output is sRGB. Textures that hold color
  (`map`, `emissiveMap`) need `texture.colorSpace = THREE.SRGBColorSpace`; data textures
  (normal, roughness, metalness, AO) stay linear. `GLTFLoader` sets this for you.
- **Lights use physical units** (since r155). `PointLight`/`SpotLight` decay is 2 by
  default, so they need intensities in the tens to hundreds at scene scale of a few
  meters. `DirectionalLight` ~1–3, `AmbientLight`/`HemisphereLight` ~0.3–1.
- **The fastest route to good PBR is an environment map**, not more lights:
  ```js
  import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  ```
  Then add one `DirectionalLight` as a key light for shadows and direction.
- `MeshStandardMaterial` is the default choice; `MeshPhysicalMaterial` for glass
  (`transmission`, `thickness`, `ior`), clearcoat, sheen, iridescence. `MeshBasicMaterial`
  ignores lights. `MeshNormalMaterial` is a good debug material.
- Shadows: `renderer.shadowMap.enabled = true`, `light.castShadow = true`,
  `mesh.castShadow / receiveShadow = true`, and tighten the directional light's
  `shadow.camera` left/right/top/bottom to the scene, or shadows are blurry or missing.
  `PCFSoftShadowMap` was removed in r186 (falls back with a warning); keep the default
  `PCFShadowMap` and soften with `light.shadow.radius`, or use `VSMShadowMap`.

## 4. Performance rules

- Many copies of one object → `InstancedMesh` (set `setMatrixAt` + `instanceMatrix.needsUpdate = true`;
  per-instance color via `setColorAt`). Many different objects → `BatchedMesh`.
- Particles → one `Points` with a `BufferGeometry` and a `Float32Array` position attribute;
  update in place and set `attribute.needsUpdate = true`. Never one Mesh per particle.
- Never allocate (`new Vector3`, geometries, materials) inside the animation loop; reuse
  scratch objects declared outside.
- Share geometries and materials between meshes. Call `.dispose()` on geometries,
  materials, textures and render targets you remove.
- Static scene with no animation → render on demand (`controls.addEventListener('change', render)`)
  instead of a loop.

## 5. Interaction

```js
const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
renderer.domElement.addEventListener('pointermove', (e) => {
  const r = renderer.domElement.getBoundingClientRect();
  pointer.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
});
// in the loop:
raycaster.setFromCamera(pointer, camera);
const hit = raycaster.intersectObjects(pickables, false)[0];
```

## 6. Custom shaders

`ShaderMaterial` keeps three's built-in uniforms/attributes (`projectionMatrix`,
`modelViewMatrix`, `position`, `uv`, `normal`); `RawShaderMaterial` provides none.

```js
const material = new THREE.ShaderMaterial({
  uniforms: { uTime: { value: 0 }, uColor: { value: new THREE.Color('#ff6a3d') } },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: /* glsl */`
    uniform float uTime; uniform vec3 uColor; varying vec2 vUv;
    void main() { gl_FragColor = vec4(uColor * (0.6 + 0.4 * sin(uTime + vUv.x * 10.0)), 1.0); }`,
});
// loop: material.uniforms.uTime.value = t;
```

To tweak a built-in material instead of rewriting it, use `material.onBeforeCompile`.

**WebGPU / TSL (optional, advanced):** add `"three/webgpu": ".../build/three.webgpu.js"`
and `"three/tsl": ".../build/three.tsl.js"` to the import map, then
`import * as THREE from 'three/webgpu'` and `new THREE.WebGPURenderer()`. It falls back
to WebGL2 automatically. Node materials (`MeshStandardNodeMaterial`) + TSL replace GLSL
strings. Do not mix `three` and `three/webgpu` imports in one page. Default to
`WebGLRenderer` unless the user asks for WebGPU or compute shaders.

## 7. Post-processing

```js
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.6, 0.4, 0.85));
composer.addPass(new OutputPass());   // last: applies tone mapping + sRGB conversion
// loop: composer.render() instead of renderer.render(); on resize also composer.setSize(w, h)
```

## 8. Loading models

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const gltf = await new GLTFLoader().loadAsync(url);
scene.add(gltf.scene);
// center & scale unknown models:
const box = new THREE.Box3().setFromObject(gltf.scene);
const size = box.getSize(new THREE.Vector3()).length();
gltf.scene.position.sub(box.getCenter(new THREE.Vector3()));
camera.position.setLength(size * 1.2); camera.near = size / 100; camera.far = size * 100;
camera.updateProjectionMatrix();
```

Animated glTF → `new THREE.AnimationMixer(gltf.scene)`, `mixer.clipAction(gltf.animations[0]).play()`,
`mixer.update(dt)` each frame. Draco-compressed files need `DRACOLoader` with
`setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/libs/draco/')`.

## 9. Black screen / nothing visible — check in this order

1. Console errors (wrong import path, version mismatch between core and addons, CORS on a texture).
2. Camera inside the object or looking away → move it back, `camera.lookAt(0, 0, 0)`.
3. Object outside `near`/`far`.
4. Lit material but no light and no `scene.environment` → all black.
5. Canvas has zero height (parent without height) → give the container explicit size and
   size the renderer from the container, not `window`, when embedded.
6. Back faces: plane seen from behind → `side: THREE.DoubleSide`.

## 10. Design guidance for good-looking results

- Use a restrained palette: one background tone, one hero color, one accent. Set
  `scene.background` and matching `scene.fog = new THREE.Fog(color, near, far)` for depth.
- Product shots: FOV 30–45, three-point lighting (key directional + environment + rim
  light behind the subject), soft contact shadow on a ground plane (`ShadowMaterial`
  with low opacity).
- Motion: ease everything (damping, lerp `x += (target - x) * (1 - Math.exp(-k * dt))`),
  keep idle motion slow and small. Respect `prefers-reduced-motion`.
- Abstract/generative: instanced geometry + noise-driven transforms + bloom on a dark
  background reads as "premium" with very little code.
- Always handle resize and touch (OrbitControls already supports touch).
