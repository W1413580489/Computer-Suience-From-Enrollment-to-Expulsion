<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';

const theme = useThemeStore();

onMounted(() => {
  // 同步持久化的主题到 <html data-theme>（index.html 内联脚本已提前设置，避免首屏闪烁）
  theme.apply();
});
</script>
