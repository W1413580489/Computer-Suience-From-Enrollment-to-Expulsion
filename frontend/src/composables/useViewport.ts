import { onMounted, onUnmounted, ref } from 'vue';

export function useViewport() {
  const isMobile = ref(false);

  const mq = window.matchMedia('(max-width: 767px)');
  const update = () => {
    isMobile.value = mq.matches;
  };

  onMounted(() => {
    update();
    mq.addEventListener('change', update);
  });
  onUnmounted(() => mq.removeEventListener('change', update));

  return { isMobile };
}

/** 外链统一新窗口打开（FR-NAV-07） */
export function openExternal(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}
