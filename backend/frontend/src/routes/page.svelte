<script>
  import { onMount } from 'svelte';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
  import * as THREE from 'three';

  let scene, camera, renderer, avatar;

  async function loadAvatar() {
    const loader = new GLTFLoader();
    loader.load('/avatar.glb', (gltf) => {
      avatar = gltf.scene;
      scene.add(avatar);
    });
  }

  async function pollBackend() {
    while (true) {
      const res = await fetch('http://localhost:5000/api/get_text');
      const data = await res.json();
      if (data.glosas.length > 0) {
        console.log("Señales:", data.glosas);
        // Aquí puedes animar avatar según glosa
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

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }
    animate();
    pollBackend();
  });
</script>