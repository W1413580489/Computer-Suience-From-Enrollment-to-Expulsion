<template>
  <PageShell title="攻略" subtitle="GUIDE · 新生成长路线" active-key="guide">
    <GuidesList :items="nav.guides" @on-item-click="onItemClick" />
    <p v-if="nav.loaded && !nav.guides.length" class="empty">暂无攻略章节</p>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
import GuidesList from '@/components/list/GuidesList.vue';
import { useNavStore } from '@/stores/navStore';
import { openExternal } from '@/composables/useViewport';
import { useRouter } from 'vue-router';
import type { GuideItem } from '@/types/nav';

const nav = useNavStore();
const router = useRouter();

function onItemClick(i: GuideItem) {
  if (i.url.startsWith('/')) router.push(i.url);
  else openExternal(i.url);
}
</script>

<style scoped>
.empty {
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 32px 0;
}
</style>
