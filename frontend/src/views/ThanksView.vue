<template>
  <!-- 鸣谢 · 贡献者档案馆：移植自独立 Demo，沿用站点 tokens.css 双主题 + PageShell 全局背景层 -->
  <PageShell title="" subtitle="JNU / GUIDE ARCHIVE · ACKNOWLEDGEMENT" active-key="thanks" wide>
    <div class="thanks">
      <div class="thanks__hero-row">
        <div>
          <h1 class="thanks__title">鸣谢</h1>
          <p class="thanks__lead">15 万字指南不是一个人写出来的。这里把原本的一串名字，变成一份可以继续补充的「贡献者档案馆」：点击名字，打开属于 TA 的小档案。</p>
        </div>
        <div class="thanks__counter">共 {{ people.length }} 位贡献者</div>
      </div>

      <!-- 贡献者网格：主创者（王叔）置顶大卡，核心贡献者高亮 -->
      <section class="thanks__grid">
        <button
          v-for="(p, i) in people"
          :key="p.id"
          class="thanks__card"
          :class="{ 'thanks__card--featured': isFeatured(p), 'thanks__card--hero': p.id === 1 }"
          @click="open(i)"
        >
          <span class="thanks__serial">{{ '#' + String(p.id).padStart(2, '0') }}{{ p.id === 1 ? ' · 主创' : '' }}</span>
          <span class="thanks__name">{{ p.name }}</span>
          <span class="thanks__mini-role">{{ p.role }}</span>
          <span class="thanks__arrow">↗</span>
        </button>
      </section>

      <div class="thanks__note"><strong>特别说明：</strong>名单顺序沿用原文的参与时间线；头像、人物说明、贡献章节、联系方式等字段，建议由本人确认后再公开。没有留言的位置留空，等 TA 本人来写。</div>
      <div class="thanks__footer">
        <span>共同创作与贡献 · 排名仅为参与时间线先后</span>
        <strong>祝你不被开除！</strong>
      </div>
    </div>

    <!-- 弹窗：夜间 zzz 用 zenless-ui z-modal，日间 ak 用自定义弹窗。
         Teleport 到 body，避免父级 clip-path / transform 破坏 fixed 定位 -->
    <Teleport to="body">
      <!-- 夜间 zzz -->
      <z-modal
        v-if="theme.isZzz && sel"
        class="thanks-archive-modal"
        :model-value="!!sel"
        :title="sel.name + ' · ARCHIVE'"
        :show-footer="false"
        @close="close"
      >
        <div class="arc">
          <div class="arc__head">
            <span class="arc__slash">//</span>
            <span class="arc__title">CONTRIBUTOR ARCHIVE</span>
            <span class="arc__line" />
          </div>
          <div class="arc__top">
            <div class="arc__badge">{{ String(sel.id).padStart(2, '0') }}</div>
            <div>
              <div class="arc__name">{{ sel.name }}</div>
              <span class="arc__role">{{ sel.role }}</span>
            </div>
          </div>
          <div v-if="sel.quote" class="arc__quote">“{{ sel.quote }}”</div>
          <div class="arc__grid">
            <div class="arc__box">
              <div class="arc__label">贡献身份</div>
              <div class="arc__value">{{ sel.role }}</div>
            </div>
            <div class="arc__box">
              <div class="arc__label">联系方式</div>
              <div class="arc__value">{{ sel.contact }}</div>
            </div>
            <div class="arc__box" :class="{ 'arc__box--full': sel.contribution.length >= 5 }">
              <div class="arc__label">{{ contLabel }}</div>
              <div v-if="sel.contribution.length >= 5" class="arc__chips">
                <span v-for="t in sel.contribution" :key="t" class="arc__chip">{{ t }}</span>
              </div>
              <div v-else class="arc__value">{{ sel.contribution.join('，') }}</div>
            </div>
            <div class="arc__box" :class="{ 'arc__box--full': (sel.person || '').length > 28 }">
              <div class="arc__label">人物说明</div>
              <div v-if="sel.person" class="arc__value" v-html="linkify(sel.person)" />
              <div v-else class="arc__value arc__value--placeholder">待补充</div>
            </div>
          </div>
          <div class="arc__actions">
            <z-button @click="copyName()">复制昵称</z-button>
            <z-button @click="close()">返回名单</z-button>
          </div>
          <div class="arc__small">联系方式建议采用本人主动提供的 QQ、GitHub、邮箱或其他公开渠道，不建议后台默认展示私人手机号、微信等信息。</div>
        </div>
      </z-modal>

      <!-- 日间 ak：自定义居中弹窗 -->
      <div v-else-if="sel" class="ak-mask" @click.self="close">
        <div class="ak-sheet" role="dialog" aria-label="贡献者档案">
          <button class="ak-close" aria-label="关闭" @click="close">×</button>
          <div class="ak-top">
            <div class="ak-badge">{{ String(sel.id).padStart(2, '0') }}</div>
            <div>
              <div class="ak-name">{{ sel.name }}</div>
              <div class="ak-role">{{ sel.role }}</div>
            </div>
          </div>
          <div v-if="sel.quote" class="ak-quote">“{{ sel.quote }}”</div>
          <div class="ak-grid">
            <div class="ak-box">
              <div class="ak-label">贡献身份</div>
              <div class="ak-value">{{ sel.role }}</div>
            </div>
            <div class="ak-box">
              <div class="ak-label">联系方式</div>
              <div class="ak-value">{{ sel.contact }}</div>
            </div>
            <div class="ak-box" :class="{ 'ak-box--full': sel.contribution.length >= 5 }">
              <div class="ak-label">{{ contLabel }}</div>
              <div v-if="sel.contribution.length >= 5" class="ak-chips">
                <span v-for="t in sel.contribution" :key="t" class="ak-chip">{{ t }}</span>
              </div>
              <div v-else class="ak-value">{{ sel.contribution.join('，') }}</div>
            </div>
            <div class="ak-box" :class="{ 'ak-box--full': (sel.person || '').length > 28 }">
              <div class="ak-label">人物说明</div>
              <div v-if="sel.person" class="ak-value" v-html="linkify(sel.person)" />
              <div v-else class="ak-value ak-value--placeholder">待补充</div>
            </div>
          </div>
          <div class="ak-actions">
            <button class="ak-btn ak-btn--primary" @click="copyName()">复制昵称</button>
            <button class="ak-btn" @click="close()">返回名单</button>
          </div>
          <div class="ak-small">联系方式建议采用本人主动提供的 QQ、GitHub、邮箱或其他公开渠道，不建议后台默认展示私人手机号、微信等信息。</div>
        </div>
      </div>
    </Teleport>
  </PageShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import PageShell from '@/components/common/PageShell.vue';
import { useThemeStore } from '@/stores/themeStore';

interface Contributor {
  id: number;
  name: string;
  role: string;
  contact: string;
  quote: string;
  person: string;
  contribution: string[];
}

const people: Contributor[] = [
  { id: 1, name: '王叔', role: '主创者', contact: '自行寻找', quote: '能持剑向人，不解持照身', person: '保密', contribution: ['《新生指南补缺》', '《常用链接》', '《大学政策简解》', '《学生组织介绍》', '《学术发展规划》', '《就业发展规划》', '《竞赛指导》', '《情感与生活》', '《效率工具推荐》', '《和我组一辈子战队吧》', '《学代工作篇》', '《邪修的学习指南》', '《大学反诈篇》', '《复习资料》', '《追求策略的多元视角实证研究》', '《财富与贫穷规划》', '《全流程踩坑复盘副本》', '《RAG知识库问答实战指南》', '《新生选课教程》', '《申请github token教程》'] },
  { id: 2, name: '高书记', role: '核心贡献者', contact: '待本人确认', quote: '按理来说，你这个级别还无权调查我', person: '目前于华南理工大学攻读学位', contribution: ['港澳台考研网站'] },
  { id: 3, name: '本地刀枪炮林家络', role: '核心贡献者', contact: '待本人确认', quote: '得到和失去，只在一念之间', person: '扫黑除恶后就业中', contribution: ['《林家络的恋爱教学笔记》', '《Git使用指南》'] },
  { id: 4, name: '《大暨王朝1566》', role: '共同创作者', contact: '待本人确认', quote: '练得身形似鹤形，千株松下两函经', person: '正在买泡芙', contribution: ['《常用链接》', '《学生组织》'] },
  { id: 5, name: '鸟破苍穹', role: '共同创作者', contact: '待本人确认', quote: '《中国鸟类观察手册里不是这样的！》', person: '征战广州大师赛', contribution: ['ptcg战队'] },
  { id: 6, name: 'SSR老板', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['SSR战队'] },
  { id: 7, name: '研究生牢唐', role: '核心贡献者', contact: '待本人确认', quote: 'Man!What can I say', person: '', contribution: ['《不知来源的焚决》'] },
  { id: 8, name: '小孩', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《效率工具推荐》', '《美食娱乐篇》'] },
  { id: 9, name: '扩列与点赞之神', role: '共同创作者', contact: '待本人确认', quote: '扩列dd', person: '', contribution: ['《美食娱乐篇》', '《复习资料》'] },
  { id: 10, name: '不知名的好心人', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《美食娱乐篇》'] },
  { id: 11, name: '深圳科创学院官方客服', role: '核心贡献者', contact: '待本人确认', quote: '', person: '', contribution: ['《深圳科创学院》'] },
  { id: 12, name: '谢总', role: '共同创作者', contact: '待本人确认', quote: '', person: '无限战队招新！', contribution: ['《和我组一辈子战队吧》'] },
  { id: 13, name: '展背掌控白昼黑夜之神', role: '核心贡献者', contact: '待本人确认', quote: '那我问你，那我问你', person: '想要健身搭子请找我', contribution: ['《用脚打的水猴子也能看懂的健身指北》'] },
  { id: 14, name: '花怜99（原沪上哈基）', role: '共同创作者', contact: '待本人确认', quote: '', person: '目前于复旦大学攻读学位，等待一个185泪痣温柔俏皮小坏会逗人有仪式感喜欢小惊喜薄肌老二次元愿意陪玩c尊重自己喜好三观一致目标一致带点s会做饭的帅哥', contribution: ['《情感与生活指南》'] },
  { id: 15, name: 'QQ', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 16, name: '少女暴君', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 17, name: '木宁习习', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 18, name: '北极熊女王', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 19, name: '学代团小企鹅', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 20, name: '锦瑟无端五十弦', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 21, name: '社恐哥', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 22, name: '米居', role: '共同创作者', contact: '待本人确认', quote: '', person: '', contribution: ['《情感与生活指南》'] },
  { id: 23, name: '热美式学长', role: '核心贡献者', contact: '待本人确认', quote: '', person: '可入驻GITHUB仓库：https://github.com/YUK1207', contribution: ['《从入门到入狱的科研全流程》'] },
  { id: 24, name: '网安梵某学长', role: '核心贡献者', contact: '待本人确认', quote: '', person: '', contribution: ['《笔记本电脑推荐——面向所有大学生的推荐向》'] },
];

const theme = useThemeStore();
/** 当前打开的人物对象（null = 未打开） */
const sel = ref<Contributor | null>(null);

const contLabel = computed(() =>
  sel.value && sel.value.contribution.length >= 5 ? `主要贡献 · ${sel.value.contribution.length} 篇` : '主要贡献',
);

function open(i: number) {
  sel.value = people[i];
}
function close() {
  sel.value = null;
}

/** 主创者 / 核心贡献者 → 高亮卡 */
function isFeatured(p: Contributor) {
  return p.role === '主创者' || p.role === '核心贡献者';
}

/** HTML 转义（人物说明进入 v-html 前必须转义，防 XSS） */
function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
/** 转义后把 URL 链接化（仅 http/https） */
function linkify(s: string) {
  return esc(s).replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
}

async function copyName() {
  if (!sel.value) return;
  try {
    await navigator.clipboard.writeText(sel.value.name);
  } catch {
    /* 剪贴板不可用时忽略 */
  }
}
</script>

<style scoped>
/* ============ 页面布局（max-width 1180，比默认容器宽） ============ */
.thanks {
  max-width: 1180px;
  margin: 0 auto;
  padding: 8px 0 24px;
}

.thanks__hero-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-end;
  margin-bottom: 30px;
}

.thanks__title {
  font-family: var(--font-display);
  font-size: clamp(46px, 7vw, 86px);
  line-height: 0.95;
  margin: 12px 0 18px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.thanks__lead {
  max-width: 760px;
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1.8;
}

.thanks__counter {
  font-family: var(--font-mono);
  font-size: 12px;
  letter-spacing: 0.12em;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 12px 16px;
  background: var(--card-surface);
  flex-shrink: 0;
}

.thanks__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

/* ============ 人物卡（zzz 切角 / ak 直角） ============ */
.thanks__card {
  appearance: none;
  text-align: left;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  min-height: 118px;
  padding: 18px;
  background: var(--card-surface);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  color: var(--text-primary);
  transition: border-color 200ms, background 200ms, transform 160ms, box-shadow 200ms;
}

.thanks__card:hover:not(.thanks__card--hero) {
  transform: translateY(-4px);
  border-color: var(--amber);
  background: var(--card-surface-hover);
  box-shadow: var(--shadow-glow);
}

.thanks__card--featured {
  background: linear-gradient(145deg, var(--card-surface-hover), var(--amber-soft));
  border-color: var(--card-border);
}

.thanks__serial {
  display: block;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.12em;
  color: var(--amber);
  margin-bottom: 14px;
  font-weight: 700;
}

.thanks__card:not(.thanks__card--featured) .thanks__serial {
  color: var(--text-muted);
}

.thanks__name {
  display: block;
  font-size: 20px;
  line-height: 1.25;
  font-weight: 800;
  padding-right: 28px;
}

.thanks__mini-role {
  display: inline-block;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--amber);
  border: 1px solid var(--amber-faint);
  padding: 3px 9px;
  clip-path: var(--clip-sm);
}

.thanks__arrow {
  position: absolute;
  right: 15px;
  top: 15px;
  font-size: 20px;
  color: var(--text-muted);
}

/* 主创者（王叔）置顶大卡 */
.thanks__card--hero {
  grid-column: 1 / -1;
  min-height: 0;
  padding: 24px 28px;
  background: linear-gradient(120deg, var(--card-surface-hover) 0%, var(--amber-soft) 60%);
  border-color: var(--amber-faint);
  clip-path: var(--clip-md);
}

.thanks__card--hero:hover {
  box-shadow: var(--shadow-glow);
  border-color: var(--amber);
}

.thanks__card--hero .thanks__serial {
  font-size: 12px;
  color: var(--amber);
  margin-bottom: 12px;
}

.thanks__card--hero .thanks__name {
  font-family: var(--font-display);
  font-size: clamp(30px, 4vw, 40px);
  line-height: 1.05;
  margin-bottom: 6px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.thanks__card--hero .thanks__mini-role {
  background: var(--amber);
  color: var(--on-amber);
  border-color: var(--amber);
  padding: 4px 12px;
  clip-path: var(--clip-sm);
}

.thanks__note {
  margin-top: 30px;
  padding: 18px 20px;
  border-left: 3px solid var(--amber);
  background: var(--card-surface);
  color: var(--text-secondary);
  line-height: 1.8;
}

.thanks__footer {
  margin-top: 48px;
  padding-top: 22px;
  border-top: 1px dashed var(--border-subtle);
  font-size: 13px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  gap: 15px;
  flex-wrap: wrap;
}

/* ============ 夜间 zzz 弹窗内容 ============ */
.arc {
  padding: 2px 2px 0;
}

.arc__head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.arc__slash {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--amber);
}

.arc__title {
  font-family: var(--font-display);
  font-size: 16px;
  letter-spacing: 0.2em;
  color: var(--amber);
}

.arc__line {
  flex: 1;
  height: 1px;
  background: var(--amber);
  opacity: 0.35;
}

.arc__top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 6px;
}

.arc__badge {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  flex: none;
  background: var(--amber);
  color: var(--on-amber);
  font-family: var(--font-display);
  font-size: 24px;
  clip-path: var(--clip-sm);
}

.arc__name {
  font-family: var(--font-display);
  font-size: 38px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.arc__role {
  display: inline-block;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.24em;
  color: var(--amber);
  border: 1px solid var(--amber);
  padding: 3px 9px;
  clip-path: var(--clip-sm);
}

.arc__quote {
  margin: 20px 0 0;
  padding: 14px 16px;
  background: var(--bg-panel-2);
  border-left: 3px solid var(--amber);
  font-style: italic;
  color: var(--text-secondary);
  line-height: 1.7;
}

.arc__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 18px;
}

.arc__box {
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  padding: 14px;
}

.arc__box--full {
  grid-column: 1 / -1;
}

.arc__label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.arc__value {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
  overflow-wrap: break-word;
}

.arc__value--placeholder {
  color: var(--text-muted);
  font-style: italic;
}

/* v-html 注入的链接（无 scoped 属性，用 :deep 命中） */
.arc__value :deep(a) {
  color: var(--text-link);
  text-decoration: underline;
}

.arc__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.arc__chip {
  border: 1px solid var(--card-border);
  background: var(--accent-soft);
  color: var(--text-secondary);
  padding: 5px 11px;
  font-size: 13px;
}

.arc__chip:hover {
  border-color: var(--amber);
  color: var(--amber);
}

.arc__actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.arc__small {
  margin-top: 14px;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.6;
}

/* ============ 日间 ak 弹窗 ============ */
.ak-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-light);
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.ak-sheet {
  width: min(720px, 100%);
  max-height: 86vh;
  overflow: auto;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  box-shadow: var(--shadow-card);
  padding: 28px;
  position: relative;
}

.ak-close {
  position: absolute;
  right: 14px;
  top: 10px;
  font-size: 26px;
  color: var(--text-muted);
  cursor: pointer;
}

.ak-close:hover {
  color: var(--amber);
}

.ak-top {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  padding-right: 40px;
}

.ak-badge {
  width: 68px;
  height: 68px;
  display: grid;
  place-items: center;
  flex: none;
  background: var(--text-primary);
  color: var(--bg-primary);
  font-weight: 900;
  font-size: 20px;
  border-radius: 6px;
}

.ak-name {
  font-size: 31px;
  font-weight: 900;
  line-height: 1.1;
}

.ak-role {
  color: var(--amber);
  font-size: 12px;
  letter-spacing: 0.12em;
  font-weight: 800;
  margin-top: 8px;
}

.ak-quote {
  margin: 22px 0 0;
  padding: 14px 16px;
  background: var(--bg-panel-2);
  border-left: 3px solid var(--amber);
  font-style: italic;
  color: var(--text-secondary);
}

.ak-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 18px;
}

.ak-box {
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel);
  border-radius: 6px;
  padding: 14px;
}

.ak-box--full {
  grid-column: 1 / -1;
}

.ak-label {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.ak-value {
  font-size: 15px;
  line-height: 1.6;
  overflow-wrap: break-word;
}

.ak-value--placeholder {
  color: var(--text-muted);
  font-style: italic;
}

.ak-value :deep(a) {
  color: var(--text-link);
  text-decoration: underline;
}

.ak-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.ak-chip {
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel-2);
  padding: 5px 11px;
  font-size: 13px;
}

.ak-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.ak-btn {
  padding: 11px 16px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel-2);
  color: var(--text-primary);
  font-weight: 700;
  border-radius: 6px;
  transition: 0.2s;
}

.ak-btn:hover {
  border-color: var(--amber);
  color: var(--amber);
}

.ak-btn--primary {
  background: var(--amber);
  border-color: var(--amber);
  color: var(--on-amber);
}

.ak-btn--primary:hover {
  background: var(--amber-deep);
  border-color: var(--amber-deep);
  color: var(--on-amber);
}

.ak-small {
  margin-top: 14px;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.6;
}
</style>

<!-- 全局（非 scoped）：鸣谢弹窗 z-modal 本体宽度。z-modal 内部 class 无组件 scoped 属性，
     且 responsive.css 的全局规则带 !important，需同类 specificity + !important 且后加载才能覆盖 -->
<style>
.thanks-archive-modal.z-modal .z-modal__wrap {
  width: min(720px, calc(100vw - 32px)) !important;
  max-width: min(720px, calc(100vw - 32px)) !important;
  max-height: 84vh;
  overflow: auto;
}

@media (max-width: 767px) {
  .thanks-archive-modal.z-modal .z-modal__wrap {
    width: 300px !important;
    max-width: calc(100vw - 24px) !important;
  }
}
</style>