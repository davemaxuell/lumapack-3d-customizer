import '@fontsource/barlow-condensed/400.css';
import '@fontsource/barlow-condensed/500.css';
import '@fontsource/barlow-condensed/600.css';
import '@fontsource/barlow-condensed/700.css';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import './styles.css';

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const canvas = document.querySelector('#product-canvas');
const stage = document.querySelector('.stage-wrap');
const loadingState = document.querySelector('#loading-state');
const loadProgress = document.querySelector('#load-progress');
const selectedColor = document.querySelector('#selected-color');
const autoRotateButton = document.querySelector('#auto-rotate');
const toast = document.querySelector('#toast');
const toastDetail = document.querySelector('#toast-detail');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
const initialCameraPosition = new THREE.Vector3(4.7, 2.15, 6.9);
camera.position.copy(initialCameraPosition);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: true,
  powerPreference: 'high-performance'
});
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.065;
controls.enablePan = false;
controls.minDistance = 4.7;
controls.maxDistance = 10;
controls.minPolarAngle = Math.PI * 0.22;
controls.maxPolarAngle = Math.PI * 0.68;
controls.target.set(0, -0.02, 0);
controls.autoRotateSpeed = 1.45;

const pmremGenerator = new THREE.PMREMGenerator(renderer);
const roomEnvironment = new RoomEnvironment();
const environmentMap = pmremGenerator.fromScene(roomEnvironment, 0.04).texture;
scene.environment = environmentMap;
roomEnvironment.dispose();
pmremGenerator.dispose();

const hemisphere = new THREE.HemisphereLight(0xf6ffd2, 0x343a2b, 2.3);
scene.add(hemisphere);

const keyLight = new THREE.DirectionalLight(0xf5ffd8, 5.8);
keyLight.position.set(4.6, 7, 5.2);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(1024, 1024);
keyLight.shadow.camera.near = 0.5;
keyLight.shadow.camera.far = 20;
keyLight.shadow.camera.left = -4;
keyLight.shadow.camera.right = 4;
keyLight.shadow.camera.top = 5;
keyLight.shadow.camera.bottom = -4;
keyLight.shadow.bias = -0.0005;
scene.add(keyLight);

const rimLight = new THREE.DirectionalLight(0xaecbff, 2.6);
rimLight.position.set(-4, 3.2, -4.5);
scene.add(rimLight);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(3.25, 72),
  new THREE.ShadowMaterial({ color: 0x050604, opacity: 0.28 })
);
floor.name = 'Contact_Shadow';
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1.9;
floor.receiveShadow = true;
scene.add(floor);

let productModel = null;
let shellMaterials = [];
let shellEdgeMaterials = [];
let targetRotation = -0.18;
let currentColorName = 'Lichen Signal';
let rafId = 0;
let pageVisible = true;
let toastTimer = 0;

const featureContent = {
  shell: {
    index: '01',
    title: 'WEATHER SHELL',
    copy: '발수 코팅된 립스탑 셸이 일상의 변수로부터 장비를 보호합니다.'
  },
  strap: {
    index: '02',
    title: 'MODULAR SIDE',
    copy: '압축 스트랩과 확장 포켓으로 물병부터 삼각대까지 단단히 고정합니다.'
  },
  hardware: {
    index: '03',
    title: 'ALLOY HARDWARE',
    copy: '장갑을 낀 상태에서도 조작하기 쉬운 저온 단조 알루미늄 버클입니다.'
  }
};

function setRendererSize() {
  const width = Math.max(stage.clientWidth, 1);
  const height = Math.max(stage.clientHeight, 1);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

const resizeObserver = new ResizeObserver(setRendererSize);
resizeObserver.observe(stage);
setRendererSize();

function frameModel(model) {
  const bounds = new THREE.Box3().setFromObject(model);
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  const scale = 3.65 / size.y;

  model.scale.setScalar(scale);
  model.position.set(-center.x * scale, -center.y * scale - 0.03, -center.z * scale);
  model.rotation.y = targetRotation;
}

function configureMaterial(material) {
  material.envMapIntensity = material.name === 'MAT_HARDWARE' ? 1.45 : 0.82;
  material.needsUpdate = true;

  if (material.name === 'MAT_SHELL' && !shellMaterials.includes(material)) {
    shellMaterials.push(material);
  }
  if (material.name === 'MAT_SHELL_EDGE' && !shellEdgeMaterials.includes(material)) {
    shellEdgeMaterials.push(material);
  }
}

function revealModel() {
  loadProgress.textContent = '100%';
  window.setTimeout(() => {
    loadingState.classList.add('is-hidden');
    stage.classList.add('model-ready');
  }, prefersReducedMotion.matches ? 0 : 260);
}

const loader = new GLTFLoader();
loader.load(
  '/models/lumapack.glb',
  (gltf) => {
    productModel = gltf.scene;
    productModel.name = 'LumaPack_01_Loaded';

    productModel.traverse((object) => {
      if (!object.isMesh) return;
      object.castShadow = true;
      object.receiveShadow = true;

      if (Array.isArray(object.material)) {
        object.material.forEach(configureMaterial);
      } else {
        configureMaterial(object.material);
      }
    });

    frameModel(productModel);
    scene.add(productModel);
    revealModel();
  },
  (event) => {
    if (!event.total) return;
    const percent = Math.min(99, Math.round((event.loaded / event.total) * 100));
    loadProgress.textContent = `${percent}%`;
  },
  (error) => {
    console.error('Could not load the LumaPack model.', error);
    loadingState.classList.add('has-error');
    loadingState.querySelector('p').textContent = '3D OBJECT UNAVAILABLE';
    loadProgress.textContent = 'RETRY';
  }
);

function updateHotspots() {
  if (!productModel) return;

  document.querySelectorAll('.hotspot').forEach((hotspot) => {
    const localPosition = new THREE.Vector3(
      Number(hotspot.dataset.x),
      Number(hotspot.dataset.y),
      Number(hotspot.dataset.z)
    );
    const projected = localPosition
      .applyMatrix4(productModel.matrixWorld)
      .project(camera);

    const x = (projected.x * 0.5 + 0.5) * stage.clientWidth;
    const y = (-projected.y * 0.5 + 0.5) * stage.clientHeight;
    const inFront = projected.z > -1 && projected.z < 1;

    hotspot.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
    hotspot.classList.toggle('is-visible', inFront);
  });
}

function animate() {
  if (!pageVisible) return;

  if (productModel && !controls.autoRotate) {
    const speed = prefersReducedMotion.matches ? 1 : 0.085;
    productModel.rotation.y += (targetRotation - productModel.rotation.y) * speed;
  }

  controls.update();
  scene.updateMatrixWorld();
  updateHotspots();
  renderer.render(scene, camera);
  rafId = window.requestAnimationFrame(animate);
}

rafId = window.requestAnimationFrame(animate);

function stopAutoRotate() {
  controls.autoRotate = false;
  autoRotateButton.classList.remove('is-active');
  autoRotateButton.setAttribute('aria-pressed', 'false');
}

function rotateProduct(direction) {
  if (!productModel) return;
  stopAutoRotate();
  targetRotation += direction * (Math.PI / 4);
}

document.querySelector('#rotate-left').addEventListener('click', () => rotateProduct(-1));
document.querySelector('#rotate-right').addEventListener('click', () => rotateProduct(1));

autoRotateButton.addEventListener('click', () => {
  if (prefersReducedMotion.matches) {
    rotateProduct(1);
    return;
  }
  controls.autoRotate = !controls.autoRotate;
  autoRotateButton.classList.toggle('is-active', controls.autoRotate);
  autoRotateButton.setAttribute('aria-pressed', String(controls.autoRotate));
});

document.querySelector('#reset-view').addEventListener('click', () => {
  stopAutoRotate();
  targetRotation = -0.18;
  if (productModel && prefersReducedMotion.matches) {
    productModel.rotation.y = targetRotation;
  }
  camera.position.copy(initialCameraPosition);
  controls.target.set(0, -0.02, 0);
  controls.update();
});

controls.addEventListener('start', stopAutoRotate);

document.querySelectorAll('.swatch').forEach((swatch) => {
  swatch.addEventListener('click', () => {
    const color = new THREE.Color(swatch.dataset.color);
    const edgeColor = color.clone().offsetHSL(0, -0.04, -0.13);
    currentColorName = swatch.dataset.name;

    shellMaterials.forEach((material) => {
      material.color.copy(color);
    });
    shellEdgeMaterials.forEach((material) => {
      material.color.copy(edgeColor);
    });

    document.querySelectorAll('.swatch').forEach((button) => {
      const active = button === swatch;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-checked', String(active));
    });
    selectedColor.textContent = currentColorName;
  });
});

document.querySelectorAll('.hotspot').forEach((hotspot) => {
  hotspot.addEventListener('click', () => {
    const content = featureContent[hotspot.dataset.feature];
    document.querySelector('#feature-index').textContent = content.index;
    document.querySelector('#feature-title').textContent = content.title;
    document.querySelector('#feature-copy').textContent = content.copy;
    document.querySelectorAll('.hotspot').forEach((item) => {
      item.classList.toggle('is-active', item === hotspot);
    });
    document.querySelector('#feature-note').classList.add('is-emphasized');
    window.setTimeout(() => {
      document.querySelector('#feature-note').classList.remove('is-emphasized');
    }, 420);
  });
});

function hideToast() {
  toast.classList.remove('is-visible');
}

document.querySelector('#add-to-cart').addEventListener('click', (event) => {
  const button = event.currentTarget;
  button.classList.add('is-confirmed');
  button.querySelector('span:first-child').textContent = 'Added to field kit';
  toastDetail.textContent = `${currentColorName} · 1 item`;
  toast.classList.add('is-visible');
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(hideToast, 4200);

  window.setTimeout(() => {
    button.classList.remove('is-confirmed');
    button.querySelector('span:first-child').textContent = 'Add to field kit';
  }, 2200);
});

document.querySelector('#close-toast').addEventListener('click', hideToast);

document.addEventListener('visibilitychange', () => {
  pageVisible = !document.hidden;
  if (pageVisible) {
    window.cancelAnimationFrame(rafId);
    rafId = window.requestAnimationFrame(animate);
  }
});

prefersReducedMotion.addEventListener('change', (event) => {
  if (event.matches) stopAutoRotate();
});

window.addEventListener('pagehide', () => {
  window.cancelAnimationFrame(rafId);
  resizeObserver.disconnect();
  controls.dispose();
  environmentMap.dispose();
  scene.traverse((object) => {
    if (!object.isMesh) return;
    object.geometry?.dispose();
    if (Array.isArray(object.material)) {
      object.material.forEach((material) => material.dispose());
    } else {
      object.material?.dispose();
    }
  });
  renderer.dispose();
});

window.addEventListener('load', () => {
  document.body.classList.add('is-ready');
});
