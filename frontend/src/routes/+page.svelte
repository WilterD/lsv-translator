<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

  let scene, camera, renderer, avatar, clock;
  let bones = {};

  async function loadAvatar() {
    const loader = new GLTFLoader();
    loader.load('http://localhost:5000/static/avatar.glb', (gltf) => {
      avatar = gltf.scene;
      scene.add(avatar);

      avatar.traverse(obj => {
        if (obj.isBone) bones[obj.name] = obj;
      });
    });
  }

  async function applyPose(glosa) {
    const res = await fetch(`http://localhost:5000/api/pose/${glosa}`);
    const pose = await res.json();

    for (const [boneName, angles] of Object.entries(pose)) {
      const bone = bones[boneName];
      if (bone) {
        bone.rotation.set(...angles);
      }
    }
  }

  async function pollBackend() {
    while (true) {
      const res = await fetch('http://localhost:5000/api/get_text');
      const data = await res.json();
      for (const glosa of data.glosas) {
        await applyPose(glosa);
        await new Promise(r => setTimeout(r, 1500));
      }
      await new Promise(r => setTimeout(r, 1000));
    }
  }

  onMount(() => {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    loadAvatar();

    clock = new THREE.Clock();

    function animate() {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }

    animate();
    pollBackend();
  });
</script>
