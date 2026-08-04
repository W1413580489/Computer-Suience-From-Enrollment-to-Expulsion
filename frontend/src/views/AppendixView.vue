<template>
  <PageShell title="附录" subtitle="DATABASE · 资源集合库" active-key="appendix">
    <AppendixList :items="nav.appendix" @on-item-click="(i) => openExternal(i.url)" />
    <p v-if="nav.loaded && !nav.appendix.length" class="empty">暂无附录条目</p>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from '@/components/common/PageShell.vue';
import AppendixList from '@/components/list/AppendixList.vue';
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
