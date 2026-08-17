import React, { useEffect, useRef } from 'react';
import leafRedUrl from '../assets/leaf-red.png';
import leafGoldUrl from '../assets/leaf-gold.png';
import leafCopperLgUrl from '../assets/leaf-copper-lg.png';
import leafCopperTrUrl from '../assets/leaf-copper-tr.png';
import leafCopperBlUrl from '../assets/leaf-copper-bl.png';
import leafCopperSmUrl from '../assets/leaf-copper-sm.png';
import styles from './FallingLeaves.module.css';

const LEAF_SOURCES = [
  leafRedUrl,
  leafGoldUrl,
  leafCopperLgUrl,
  leafCopperTrUrl,
  leafCopperBlUrl,
  leafCopperSmUrl,
];

const LEAF_COUNT = 18;
const TARGET_HEIGHT_MIN = 22;
const TARGET_HEIGHT_MAX = 52;
const FADE_ZONE = 0.38;

function fadeOpacity(baseOpacity, leafY, leafHeight, viewportHeight) {
  const fadeStart = viewportHeight * (1 - FADE_ZONE);
  const leafCenterY = leafY + leafHeight / 2;
  if (leafCenterY <= fadeStart) return baseOpacity;

  const progress = (leafCenterY - fadeStart) / (viewportHeight - fadeStart);
  return baseOpacity * (1 - Math.min(1, progress));
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });
}

function pickSpriteIndex() {
  return Math.floor(Math.random() * LEAF_SOURCES.length);
}

function sizeForSprite(sprite, targetHeight) {
  const scale = targetHeight / sprite.naturalHeight;
  return {
    width: sprite.naturalWidth * scale,
    height: sprite.naturalHeight * scale,
  };
}

function createLeaf(width, height, sprites, spriteIndex) {
  const sprite = sprites[spriteIndex];
  const targetHeight =
    TARGET_HEIGHT_MIN + Math.random() * (TARGET_HEIGHT_MAX - TARGET_HEIGHT_MIN);
  const { width: leafWidth, height: leafHeight } = sizeForSprite(sprite, targetHeight);

  return {
    spriteIndex,
    x: Math.random() * width,
    y: Math.random() * height - height * 0.2,
    width: leafWidth,
    height: leafHeight,
    speedY: 0.35 + Math.random() * 0.75,
    swayPhase: Math.random() * Math.PI * 2,
    swaySpeed: 0.012 + Math.random() * 0.018,
    swayAmp: 0.4 + Math.random() * 1.1,
    rotation: Math.random() * Math.PI * 2,
    rotSpeed: (Math.random() - 0.5) * 0.025,
    baseOpacity: 0.55 + Math.random() * 0.4,
  };
}

function resetLeaf(leaf, width, height, sprites) {
  const spriteIndex = pickSpriteIndex();
  const next = createLeaf(width, height, sprites, spriteIndex);
  Object.assign(leaf, next);
  leaf.x = Math.random() * width;
  leaf.y = -next.height - Math.random() * height * 0.15;
}

export default function FallingLeaves() {
  const canvasRef = useRef(null);
  const stateRef = useRef({ leaves: [], sprites: [], raf: 0, reducedMotion: false });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    stateRef.current.reducedMotion = reducedMotion;

    const ctx = canvas.getContext('2d');
    if (!ctx) return undefined;

    let width = 0;
    let height = 0;
    let cancelled = false;

    function resize() {
      const parent = canvas.parentElement;
      if (!parent) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = parent.clientWidth;
      height = parent.clientHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = true;

      if (stateRef.current.leaves.length === 0 && stateRef.current.sprites.length > 0) {
        stateRef.current.leaves = Array.from({ length: LEAF_COUNT }, (_, i) =>
          createLeaf(width, height, stateRef.current.sprites, i % LEAF_SOURCES.length),
        );
      }
    }

    function drawFrame() {
      if (stateRef.current.sprites.length === 0 || width === 0 || height === 0) return;

      ctx.clearRect(0, 0, width, height);

      for (const leaf of stateRef.current.leaves) {
        if (!reducedMotion) {
          leaf.y += leaf.speedY;
          leaf.swayPhase += leaf.swaySpeed;
          leaf.x += Math.sin(leaf.swayPhase) * leaf.swayAmp;
          leaf.rotation += leaf.rotSpeed;

          if (leaf.y > height + leaf.height) {
            resetLeaf(leaf, width, height, stateRef.current.sprites);
          }
        }

        const sprite = stateRef.current.sprites[leaf.spriteIndex];
        ctx.save();
        ctx.globalAlpha = fadeOpacity(leaf.baseOpacity, leaf.y, leaf.height, height);
        ctx.translate(leaf.x + leaf.width / 2, leaf.y + leaf.height / 2);
        ctx.rotate(leaf.rotation);
        ctx.drawImage(
          sprite,
          -leaf.width / 2,
          -leaf.height / 2,
          leaf.width,
          leaf.height,
        );
        ctx.restore();
      }

      ctx.globalAlpha = 1;
    }

    function tick() {
      drawFrame();
      if (!reducedMotion) {
        stateRef.current.raf = window.requestAnimationFrame(tick);
      }
    }

    function start() {
      if (cancelled) return;
      resize();
      drawFrame();
      if (!reducedMotion) {
        stateRef.current.raf = window.requestAnimationFrame(tick);
      }
    }

    Promise.all(LEAF_SOURCES.map(loadImage))
      .then((sprites) => {
        if (cancelled) return;
        stateRef.current.sprites = sprites;
        start();
      })
      .catch(() => {});

    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement);

    return () => {
      cancelled = true;
      ro.disconnect();
      window.cancelAnimationFrame(stateRef.current.raf);
    };
  }, []);

  return (
    <div className={styles.root} aria-hidden="true">
      <canvas ref={canvasRef} className={styles.canvas} />
    </div>
  );
}
