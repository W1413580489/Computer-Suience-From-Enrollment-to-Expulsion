<template>
  <section class="data-section">
    <SectionHeader num="03" title="数据面板" en="DATA PANEL" />

    <div class="stats">
      <!-- 左：网站完成度 -->
      <div class="stat">
        <div class="stat__value">87%</div>
        <div class="stat__label">SITE COMPLETION</div>
        <div class="stat__bar"><div class="stat__fill" /></div>
      </div>

      <!-- 中：最新更新时间 -->
      <div class="stat stat--center">
        <div class="stat__value stat__value--date">{{ updatedAt }}</div>
        <div class="stat__label">LAST UPDATE</div>
        <div class="stat__sub">网站最新更新时间</div>
      </div>

      <!-- 右：致谢名单（逐个放映） -->
      <div class="stat stat--credits">
        <div class="stat__label stat__label--credits">CREDITS · 致谢名单</div>
        <div class="credits">
          <ul class="credits__list">
            <li v-for="(name, i) in credits" :key="i">{{ name }}</li>
            <li v-for="(name, i) in credits" :key="'dup-' + i" aria-hidden="true">{{ name }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useNavStore } from '@/stores/navStore';
import SectionHeader from './SectionHeader.vue';

const nav = useNavStore();

const updatedAt = computed(() => nav.changelog[0]?.date ?? '2026-08-13');

const credits = [
  '王叔',
  '高书记',
  '林家络',
  '大暨王朝1566',
  '鸟破苍穹',
  'Ssr老板',
  '研究生牢唐',
  '小孩',
  '扩列与点赞之神',
  '不知名的好心人',
  '深圳科创学院',
  'QQ',
  '少女暴君',
  '沪上哈基',
  '谢总',
  '乔伊皇',
  '木宁习习',
  '北极熊女王',
  '小企鹅',
  '锦瑟无端五十弦',
  '社恐哥',
  '米居',
  '网安梵某学长',
];
</script>

<style scoped>
.data-section {
  padding: 80px 32px 96px;
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
}

.stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1.4fr;
  gap: 14px;
}

.stat {
  position: relative;
  background: var(--bg-panel-2);
  padding: 18px 20px;
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
  border-bottom: 2px solid var(--amber);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat--center {
  align-items: center;
  justify-content: center;
  text-align: center;
}

.stat__value {
  font-family: var(--font-display);
  font-size: 38px;
  font-weight: 900;
  line-height: 1;
  color: var(--amber);
}

.stat__value--date {
  font-family: var(--font-mono);
  font-size: 22px;
  letter-spacing: 1px;
}

.stat__label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.stat__sub {
  font-size: 12px;
  color: var(--text-muted);
}

.stat__bar {
  margin-top: 8px;
  width: 100%;
  height: 8px;
  background: var(--bg-panel-3);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
  overflow: hidden;
}

.stat__fill {
  width: 87%;
  height: 100%;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan));
}

.stat--credits {
  border-bottom-color: var(--neon-cyan);
}

.stat__label--credits {
  color: var(--neon-cyan);
}

.credits {
  margin-top: 4px;
  height: 56px;
  overflow: hidden;
  position: relative;
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 16%, black 84%, transparent 100%);
  mask-image: linear-gradient(to bottom, transparent 0%, black 16%, black 84%, transparent 100%);
}

.credits__list {
  list-style: none;
  margin: 0;
  padding: 0;
  animation: credits-scroll 30s linear infinite;
}

.credits__list li {
  font-size: 13.5px;
  line-height: 30px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes credits-scroll {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.credits:hover .credits__list {
  animation-play-state: paused;
}

@media (max-width: 767px) {
  .data-section {
    padding: 48px 16px 64px;
  }

  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
