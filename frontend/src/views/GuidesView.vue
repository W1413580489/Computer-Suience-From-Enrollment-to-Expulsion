<template>
  <PageShell title="攻略" subtitle="GUIDE · 新生成长路线" active-key="guide">
    <GuidesList :items="nav.guides" @on-item-click="(i) => openExternal(i.url)" />
    <p v-if="nav.loaded && !nav.guides.length" class="empty">暂无攻略章节</p>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
import GuidesList from '@/components/list/GuidesList.vue';
import { useNavStore } from '@/stores/navStore';
import { openExternal } from '@/composables/useViewport';

const nav = useNavStore();
</script>

<style scoped>
.empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 32px 0;
}
</style>
