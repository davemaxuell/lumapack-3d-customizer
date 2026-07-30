import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputPath = path.resolve(__dirname, '../public/models/lumapack.glb');

globalThis.FileReader = class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then((result) => {
      this.result = result;
      this.onloadend?.({ target: this });
    });
  }

  readAsDataURL(blob) {
    blob.arrayBuffer().then((buffer) => {
      const mime = blob.type || 'application/octet-stream';
      this.result = `data:${mime};base64,${Buffer.from(buffer).toString('base64')}`;
      this.onloadend?.({ target: this });
    });
  }
};

const scene = new THREE.Scene();
scene.name = 'LumaPack_01_Scene';

const product = new THREE.Group();
product.name = 'LumaPack_01';
product.userData = {
  title: 'LumaPack 01',
  designer: 'Luma Objects, Seoul',
  generatedFor: 'Three.js Final Project 23-1'
};
scene.add(product);

const materials = {
  shell: new THREE.MeshStandardMaterial({
    name: 'MAT_SHELL',
    color: 0xc9dd3c,
    roughness: 0.46,
    metalness: 0.04
  }),
  shellEdge: new THREE.MeshStandardMaterial({
    name: 'MAT_SHELL_EDGE',
    color: 0x87951f,
    roughness: 0.58,
    metalness: 0.02
  }),
  graphite: new THREE.MeshStandardMaterial({
    name: 'MAT_GRAPHITE',
    color: 0x181b17,
    roughness: 0.72,
    metalness: 0.06
  }),
  webbing: new THREE.MeshStandardMaterial({
    name: 'MAT_WEBBING',
    color: 0x292d26,
    roughness: 0.92,
    metalness: 0
  }),
  hardware: new THREE.MeshStandardMaterial({
    name: 'MAT_HARDWARE',
    color: 0xbfc5b5,
    roughness: 0.24,
    metalness: 0.78
  }),
  accent: new THREE.MeshStandardMaterial({
    name: 'MAT_ACCENT',
    color: 0xf1ff8a,
    roughness: 0.36,
    metalness: 0
  })
};

function addMesh(name, geometry, material, position, rotation = [0, 0, 0], parent = product) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  mesh.position.set(...position);
  mesh.rotation.set(...rotation);
  parent.add(mesh);
  return mesh;
}

function rounded(name, size, radius, material, position, rotation = [0, 0, 0], parent = product) {
  return addMesh(
    name,
    new RoundedBoxGeometry(size[0], size[1], size[2], 5, radius),
    material,
    position,
    rotation,
    parent
  );
}

// Core body and structural panels.
rounded('Shell_Main', [2.55, 3.18, 1.1], 0.28, materials.shell, [0, 0, 0]);
rounded('Shell_TopFlap', [2.28, 0.9, 0.24], 0.18, materials.shellEdge, [0, 1.18, 0.61], [-0.11, 0, 0]);
rounded('Shell_FrontPocket', [2.05, 1.22, 0.48], 0.2, materials.shell, [0, -0.65, 0.74], [-0.02, 0, 0]);
rounded('Shell_BaseGuard', [2.42, 0.62, 1.02], 0.2, materials.graphite, [0, -1.36, 0.02]);
rounded('Back_Panel', [2.18, 2.55, 0.24], 0.22, materials.graphite, [0, -0.05, -0.6]);

// Side pockets and compression straps.
rounded('Shell_SidePocket_L', [0.42, 1.42, 0.82], 0.16, materials.shellEdge, [-1.4, -0.28, 0.02]);
rounded('Shell_SidePocket_R', [0.42, 1.42, 0.82], 0.16, materials.shellEdge, [1.4, -0.28, 0.02]);
rounded('Webbing_Side_L', [0.12, 2.2, 0.06], 0.035, materials.webbing, [-1.44, 0.2, 0.22], [0, 0, -0.05]);
rounded('Webbing_Side_R', [0.12, 2.2, 0.06], 0.035, materials.webbing, [1.44, 0.2, 0.22], [0, 0, 0.05]);

// Front webbing rails, logo plate, and buckles.
for (const x of [-0.72, 0.72]) {
  rounded(`Webbing_Front_${x < 0 ? 'L' : 'R'}`, [0.13, 2.28, 0.07], 0.03, materials.webbing, [x, -0.06, 0.89]);
  rounded(`Hardware_Buckle_${x < 0 ? 'L' : 'R'}`, [0.34, 0.28, 0.12], 0.05, materials.hardware, [x, -0.74, 1.0]);
  rounded(`Hardware_BuckleSlot_${x < 0 ? 'L' : 'R'}`, [0.16, 0.08, 0.03], 0.02, materials.graphite, [x, -0.74, 1.07]);
}

rounded('Logo_Plate', [0.92, 0.31, 0.08], 0.05, materials.graphite, [0, 0.43, 1.03]);
for (const x of [-0.22, 0, 0.22]) {
  addMesh('Logo_Mark', new THREE.CylinderGeometry(0.045, 0.045, 0.04, 16), materials.accent, [x, 0.43, 1.09], [Math.PI / 2, 0, 0]);
}

// Zipper tracks and pulls.
rounded('Zipper_Main', [1.85, 0.055, 0.05], 0.025, materials.graphite, [0, 0.74, 1.00]);
rounded('Zipper_Pocket', [1.62, 0.055, 0.05], 0.025, materials.graphite, [0, -0.18, 1.03]);
for (const [name, x, y] of [['Main', 0.62, 0.74], ['Pocket', -0.48, -0.18]]) {
  addMesh(`Hardware_ZipPull_${name}`, new THREE.TorusGeometry(0.085, 0.018, 8, 18), materials.hardware, [x, y - 0.08, 1.08]);
}

// Top carry handle.
addMesh(
  'Webbing_Handle',
  new THREE.TorusGeometry(0.55, 0.09, 10, 36, Math.PI),
  materials.webbing,
  [0, 1.66, -0.04]
);
rounded('Handle_Anchor_L', [0.24, 0.34, 0.18], 0.06, materials.graphite, [-0.54, 1.48, -0.02]);
rounded('Handle_Anchor_R', [0.24, 0.34, 0.18], 0.06, materials.graphite, [0.54, 1.48, -0.02]);

// Contoured shoulder straps on the back.
for (const side of [-1, 1]) {
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(side * 0.56, 1.18, -0.75),
    new THREE.Vector3(side * 0.84, 0.54, -0.91),
    new THREE.Vector3(side * 0.94, -0.42, -0.9),
    new THREE.Vector3(side * 0.78, -1.32, -0.72)
  ]);
  addMesh(
    `Webbing_Shoulder_${side < 0 ? 'L' : 'R'}`,
    new THREE.TubeGeometry(curve, 28, 0.145, 8, false),
    materials.webbing,
    [0, 0, 0]
  );
  rounded(
    `Hardware_StrapAdjuster_${side < 0 ? 'L' : 'R'}`,
    [0.37, 0.28, 0.11],
    0.05,
    materials.hardware,
    [side * 0.82, -1.08, -0.78],
    [0.1, 0, side * -0.06]
  );
}

// Air-channel back padding.
for (const x of [-0.62, 0, 0.62]) {
  rounded('Back_AirChannel', [0.38, 1.92, 0.13], 0.12, materials.webbing, [x, -0.14, -0.78]);
}

// Small utility loops create a crafted silhouette.
for (const side of [-1, 1]) {
  for (const y of [-0.65, 0.15, 0.9]) {
    addMesh(
      'Webbing_UtilityLoop',
      new THREE.TorusGeometry(0.15, 0.035, 8, 18, Math.PI),
      materials.webbing,
      [side * 1.27, y, 0.55],
      [0, side * Math.PI / 2, Math.PI / 2]
    );
  }
}

product.rotation.set(0, 0, 0);

const exporter = new GLTFExporter();
const arrayBuffer = await exporter.parseAsync(scene, {
  binary: true,
  onlyVisible: true,
  trs: false,
  maxTextureSize: 1024
});

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, Buffer.from(arrayBuffer));

const stats = await fs.stat(outputPath);
console.log(`Generated ${path.relative(process.cwd(), outputPath)} (${(stats.size / 1024).toFixed(1)} KB)`);
