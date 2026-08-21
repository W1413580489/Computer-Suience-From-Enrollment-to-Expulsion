<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import { unlockAchievement } from '@/data/achievements';

const theme = useThemeStore();

onMounted(() => {
  // 同步持久化的主题到 <html data-theme>（index.html 内联脚本已提前设置，避免首屏闪烁）
  theme.apply();
  // 成就：默认夜间 zzz 模式即解锁「欢迎来到新艾利都」
  if (theme.isZzz) unlockAchievement('welcome_new_eridu');
});
</script>
