<template>
  <router-view />
  <!-- 成就解锁提示（全局） -->
  <AchievementToast />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import { useAchievementStore } from '@/stores/achievementStore';
import AchievementToast from '@/components/common/AchievementToast.vue';

const theme = useThemeStore();

onMounted(() => {
  // 同步持久化的主题到 <html data-theme>（index.html 内联脚本已提前设置，避免首屏闪烁）
  theme.apply();
  // 成就：凌晨 0:00-5:00 访问
  const hour = new Date().getHours();
  if (hour >= 0 && hour < 5) {
    useAchievementStore().unlock('meaningless_night');
  }
});
</script>