import { ref } from 'vue';

const LS_KEY = 'xkz_bg_image_v1';
const LS_POS_KEY = 'xkz_bg_pos_v1';
const CSS_VAR = '--user-bg-url';
const CSS_POS_VAR = '--user-bg-pos';
const DATA_ATTR = 'data-has-user-bg';
const MAX_DIM = 1920;
const QUALITY = 0.82;

const dataUrl = ref<string | null>(null);
const pendingUrl = ref<string | null>(null);
const error = ref<string | null>(null);
// 背景图位置（百分比，0~100，默认居中 50/50）
const bgX = ref(50);
const bgY = ref(50);

function load() {
  try {
    const saved = localStorage.getItem(LS_KEY);
    if (saved) {
      dataUrl.value = saved;
      applyCss(saved);
    }
    const savedPos = localStorage.getItem(LS_POS_KEY);
    if (savedPos) {
      const p = JSON.parse(savedPos);
      if (typeof p.x === 'number' && typeof p.y === 'number') {
        bgX.value = p.x;
        bgY.value = p.y;
      }
    }
    applyPos();
  } catch { /* 忽略 */ }
}

function applyCss(url: string | null) {
  const root = document.documentElement;
  if (url) {
    root.style.setProperty(CSS_VAR, `url(${url})`);
    root.setAttribute(DATA_ATTR, '');
  } else {
    root.style.removeProperty(CSS_VAR);
    root.removeAttribute(DATA_ATTR);
  }
}

function applyPos() {
  const root = document.documentElement;
  root.style.setProperty(CSS_POS_VAR, `${bgX.value}% ${bgY.value}%`);
}

function savePos() {
  try {
    localStorage.setItem(LS_POS_KEY, JSON.stringify({ x: bgX.value, y: bgY.value }));
  } catch { /* 忽略 */ }
}

function compressImage(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const objUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objUrl);

      let { width, height } = img;
      if (width > MAX_DIM || height > MAX_DIM) {
        if (width >= height) {
          height = Math.round((height / width) * MAX_DIM);
          width = MAX_DIM;
        } else {
          width = Math.round((width / height) * MAX_DIM);
          height = MAX_DIM;
        }
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) { reject(new Error('无法创建 canvas 上下文')); return; }
      ctx.drawImage(img, 0, 0, width, height);

      let out: string;
      try {
        out = canvas.toDataURL('image/webp', QUALITY);
        if (out.length > 4_000_000) out = canvas.toDataURL('image/jpeg', QUALITY);
      } catch {
        out = canvas.toDataURL('image/jpeg', QUALITY);
      }
      resolve(out);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objUrl);
      reject(new Error('图片格式不支持或已损坏'));
    };

    img.src = objUrl;
  });
}

async function previewImage(file: File): Promise<void> {
  error.value = null;
  try {
    const compressed = await compressImage(file);
    pendingUrl.value = compressed;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '图片处理失败';
    throw err;
  }
}

function applyPending() {
  if (!pendingUrl.value) return;
  dataUrl.value = pendingUrl.value;
  try {
    localStorage.setItem(LS_KEY, pendingUrl.value);
  } catch {
    error.value = '图片过大，无法持久保存（刷新后会丢失），但当前会话可正常显示';
  }
  applyCss(pendingUrl.value);
  pendingUrl.value = null;
}

function cancelPending() {
  pendingUrl.value = null;
  error.value = null;
}

function removeImage() {
  dataUrl.value = null;
  pendingUrl.value = null;
  error.value = null;
  bgX.value = 50;
  bgY.value = 50;
  try {
    localStorage.removeItem(LS_KEY);
    localStorage.removeItem(LS_POS_KEY);
  } catch { /* 忽略 */ }
  applyCss(null);
  applyPos();
}

/** 设置位置（实时拖拽时调用） */
function setPos(x: number, y: number) {
  bgX.value = Math.max(0, Math.min(100, x));
  bgY.value = Math.max(0, Math.min(100, y));
  applyPos();
}

/** 持久化当前位置（拖拽结束时调用） */
function persistPos() {
  savePos();
}

/** 重置位置到居中 */
function resetPos() {
  bgX.value = 50;
  bgY.value = 50;
  applyPos();
  savePos();
}

load();

export function useBgImage() {
  return {
    dataUrl, pendingUrl, error, bgX, bgY,
    previewImage, applyPending, cancelPending, removeImage,
    setPos, persistPos, resetPos,
  };
}