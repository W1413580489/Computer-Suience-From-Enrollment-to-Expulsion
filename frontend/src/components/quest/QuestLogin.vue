<template>
  <div class="login-root">
    <!-- Welcome banner -->
    <div class="login-banner">
      <span class="login-banner__icon">🏫</span>
      <div class="login-banner__text">
        <strong>欢迎来到新手村</strong>
        <span>这里是暨大番禺校区新生入学攻略 — 检查装备、分配技能、开启你的大学冒险！</span>
      </div>
    </div>

    <!-- Header -->
    <div class="login-header">
      <span class="login-header__tag">CHARACTER CREATION</span>
      <h1 class="login-header__title">新玩家账号登录</h1>
      <p class="login-header__sub">
        入学前请打开你的「角色背包」，检查以下装备是否齐全
      </p>
      <div class="login-header__steps">
        <span class="login-header__step login-header__step--active">👤 登录</span>
        <span class="login-header__step-arrow">→</span>
        <span class="login-header__step">🗺️ 探索</span>
        <span class="login-header__step-arrow">→</span>
        <span class="login-header__step">📖 研读</span>
      </div>
    </div>

    <!-- Equipment Checklist -->
    <section class="login-section">
      <h2 class="section-title">
        <span class="section-title__num">01</span>
        装备清单
      </h2>
      <div class="equip-grid">
        <button
          v-for="item in equipment"
          :key="item.id"
          class="equip-card"
          :class="{ 'equip-card--done': isEquipped(item.id) }"
          @click="toggleEquip(item.id)"
        >
          <span class="equip-card__icon">{{ isEquipped(item.id) ? '✅' : '⬜' }}</span>
          <div class="equip-card__body">
            <span class="equip-card__name">{{ item.name }}</span>
            <span class="equip-card__hint">{{ item.hint }}</span>
          </div>
        </button>
      </div>
      <p class="section-hint">💡 勾选你已准备好的装备，至少准备 1 件即可出发</p>
    </section>

    <!-- Skill Points -->
    <section class="login-section">
      <h2 class="section-title">
        <span class="section-title__num">02</span>
        技能预加点
        <span class="section-title__badge">剩余 {{ remainingPoints }} 点</span>
      </h2>
      <p class="section-hint">💡 总共 6 点可分配，每个技能最多 2 点</p>
      <div class="skill-list">
        <div
          v-for="skill in skills"
          :key="skill.id"
          class="skill-row"
          :class="{ 'skill-row--max': currentSkill(skill.id) >= skill.max }"
        >
          <div class="skill-row__info">
            <span class="skill-row__name">{{ skill.name }}</span>
            <span class="skill-row__desc">{{ skill.desc }}</span>
          </div>
          <div class="skill-row__ctrl">
            <button
              class="skill-btn"
              :disabled="currentSkill(skill.id) <= 0"
              @click="adjustSkill(skill.id, -1)"
            >−</button>
            <span class="skill-row__val">{{ currentSkill(skill.id) }}</span>
            <button
              class="skill-btn"
              :disabled="currentSkill(skill.id) >= skill.max || remainingPoints <= 0"
              @click="adjustSkill(skill.id, 1)"
            >+</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Action -->
    <div class="login-action">
      <button class="login-btn" :disabled="equippedCount === 0" @click="complete">
        <span class="login-btn__main">确认登录，开始探索</span>
        <span class="login-btn__arrow">→</span>
        <span class="login-btn__hint">(已备 {{ equippedCount }}/{{ equipment.length }} 件装备)</span>
      </button>
      <button class="skip-btn" @click="skip">跳过引导，以后再说</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue';
import { loadProgress, saveProgress, MAX_SKILL_POINTS } from '@/composables/useQuest';

const emit = defineEmits<{ done: [] }>();

const equipment = [
  { id: 'notice', name: '录取通知书', hint: '全文复印1份备用' },
  { id: 'idcard', name: '身份证件', hint: '正反面打印在同一面' },
  { id: 'photo', name: '证件照', hint: '按入学要求规格准备' },
  { id: 'league', name: '团组织档案', hint: '高中副本结算掉落' },
  { id: 'jnuid', name: 'JNUID 账号', hint: '8月下旬关注官方服务号激活' },
];

const skills = [
  { id: 'info', name: '信息检索 Lv.1', desc: '关注公众号、保存重要公告截图', max: 2 },
  { id: 'luggage', name: '行李收纳 Lv.Max', desc: '大件寄快递到菜鸟驿站', max: 2 },
  { id: 'anti_fraud', name: '防诈骗 Lv.1', desc: '只信官方群通知；涉及金钱需核实', max: 2 },
];

const progress = reactive(loadProgress());
const remainingPoints = computed(() => MAX_SKILL_POINTS - progress.skillPointsSpent);
const equippedCount = computed(() => progress.equipment.length);

function isEquipped(id: string) { return progress.equipment.includes(id); }
function toggleEquip(id: string) {
  const idx = progress.equipment.indexOf(id);
  if (idx >= 0) progress.equipment.splice(idx, 1);
  else progress.equipment.push(id);
}

function currentSkill(id: string) { return progress.skills[id] ?? 0; }
function adjustSkill(id: string, delta: number) {
  const cur = currentSkill(id);
  const skill = skills.find(s => s.id === id)!;
  if (delta > 0) {
    if (progress.skillPointsSpent >= MAX_SKILL_POINTS) return;
    if (cur >= skill.max) return;
    progress.skillPointsSpent++;
    progress.skills[id] = cur + 1;
  } else {
    if (cur <= 0) return;
    progress.skillPointsSpent--;
    progress.skills[id] = cur - 1;
  }
}

function complete() {
  saveProgress({ ...progress });
  emit('done');
}

function skip() {
  progress.hasSeenIntro = true;
  saveProgress({ ...progress });
  emit('done');
}
</script>

<style scoped>
.login-root {
  max-width: 640px;
  margin: 0 auto;
  padding: clamp(20px, 4vw, 32px) clamp(16px, 3vw, 24px) clamp(40px, 8vw, 60px);
  overflow-y: auto;
  height: 100%;
  -webkit-overflow-scrolling: touch;
}

/* ---- Welcome Banner ---- */
.login-banner {
  display: flex; align-items: flex-start; gap: 12px;
  padding: clamp(10px, 2vw, 14px) clamp(12px, 2vw, 16px);
  background: var(--amber-soft);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-md);
  margin-bottom: clamp(16px, 3vw, 24px);
}
.login-banner__icon { font-size: clamp(20px, 3vw, 24px); flex-shrink: 0; }
.login-banner__text {
  display: flex; flex-direction: column; gap: 4px;
  font-size: clamp(12px, 2vw, 14px); color: var(--text-secondary); line-height: 1.5;
}
.login-banner__text strong {
  font-size: clamp(14px, 2.2vw, 16px); color: var(--amber);
}

/* ---- Header ---- */
.login-header {
  text-align: center;
  margin-bottom: clamp(24px, 4vw, 40px);
}
.login-header__tag {
  display: inline-block;
  font-family: var(--font-display);
  font-size: clamp(11px, 1.8vw, 12px);
  letter-spacing: clamp(2px, 0.5vw, 4px);
  color: var(--amber);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  padding: 4px 12px;
  margin-bottom: 14px;
}
.login-header__title {
  font-size: clamp(22px, 4vw, 28px);
  font-weight: 700;
  color: var(--amber);
  margin-bottom: 8px;
}
.login-header__sub {
  font-size: clamp(13px, 2vw, 14px);
  color: var(--text-secondary);
  line-height: 1.6;
}
.login-header__steps {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  margin-top: 14px;
  font-size: clamp(11px, 1.8vw, 13px);
  color: var(--text-muted);
}
.login-header__step { opacity: .5; }
.login-header__step--active { opacity: 1; color: var(--amber); font-weight: 600; }
.login-header__step-arrow { opacity: .3; }

/* ---- Sections ---- */
.login-section {
  margin-bottom: clamp(24px, 4vw, 36px);
}
.section-title {
  display: flex;
  align-items: center;
  gap: clamp(6px, 1.5vw, 10px);
  font-size: clamp(16px, 2.5vw, 18px);
  font-weight: 600;
  margin-bottom: clamp(10px, 2vw, 16px);
  color: var(--text-primary);
}
.section-title__num {
  font-family: var(--font-display);
  font-size: clamp(11px, 1.5vw, 12px);
  color: var(--amber);
}
.section-title__badge {
  font-size: clamp(11px, 1.5vw, 12px);
  font-weight: 400;
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid var(--success-border);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  margin-left: auto;
}
.section-hint {
  font-size: clamp(11px, 1.5vw, 12px);
  color: var(--text-muted);
  margin-top: 8px;
  opacity: .7;
}

/* ---- Equipment ---- */
.equip-grid {
  display: flex;
  flex-direction: column;
  gap: clamp(6px, 1vw, 8px);
}
.equip-card {
  display: flex;
  align-items: center;
  gap: clamp(10px, 2vw, 14px);
  padding: clamp(12px, 2vw, 14px) clamp(12px, 2vw, 16px);
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 200ms, background 200ms, transform 150ms;
  text-align: left;
}
.equip-card:hover { border-color: var(--accent-bright); transform: translateX(2px); }
.equip-card--done {
  border-color: var(--success-border);
  background: var(--success-soft);
}
.equip-card__icon { font-size: clamp(18px, 2.5vw, 20px); flex-shrink: 0; }
.equip-card__body { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.equip-card__name { font-size: clamp(14px, 2vw, 15px); font-weight: 500; }
.equip-card__hint { font-size: clamp(11px, 1.5vw, 12px); color: var(--text-muted); }

/* ---- Skills ---- */
.skill-list {
  display: flex;
  flex-direction: column;
  gap: clamp(8px, 1.5vw, 10px);
}
.skill-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(8px, 1.5vw, 12px);
  padding: clamp(12px, 2vw, 14px) clamp(12px, 2vw, 16px);
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.skill-row__info { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.skill-row__name { font-size: clamp(14px, 2vw, 15px); font-weight: 500; }
.skill-row__desc {
  font-size: clamp(11px, 1.5vw, 12px); color: var(--text-muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.skill-row__ctrl { display: flex; align-items: center; gap: clamp(6px, 1vw, 8px); flex-shrink: 0; }
.skill-btn {
  width: clamp(28px, 5vw, 32px); height: clamp(28px, 5vw, 32px);
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: clamp(16px, 2.5vw, 18px);
  cursor: pointer;
  transition: border-color 150ms;
  min-width: 28px; min-height: 28px;
}
.skill-btn:hover:not(:disabled) { border-color: var(--accent-bright); }
.skill-btn:disabled { opacity: .3; cursor: default; }
.skill-row__val {
  font-family: var(--font-display);
  font-size: clamp(16px, 2.5vw, 18px);
  font-weight: 700;
  color: var(--amber);
  min-width: 24px; text-align: center;
}
.skill-row--max .skill-row__val { color: var(--success); }

/* ---- Action ---- */
.login-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-top: clamp(30px, 5vw, 40px);
}
.login-btn {
  width: 100%; max-width: 400px;
  padding: clamp(12px, 2vw, 14px);
  background: var(--amber);
  color: var(--on-amber);
  border-radius: var(--radius-md);
  font-size: clamp(15px, 2.5vw, 17px);
  font-weight: 700;
  cursor: pointer;
  transition: opacity 200ms, transform 150ms;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  flex-wrap: wrap;
}
.login-btn:hover:not(:disabled) { opacity: .9; transform: translateY(-1px); }
.login-btn:disabled { opacity: .4; cursor: default; }
.login-btn__main { flex-shrink: 0; }
.login-btn__arrow {
  font-size: clamp(18px, 3vw, 20px);
  transition: transform 200ms;
}
.login-btn:hover:not(:disabled) .login-btn__arrow { transform: translateX(3px); }
.login-btn__hint {
  width: 100%;
  font-size: clamp(11px, 1.5vw, 12px); font-weight: 400; opacity: .7;
}
.skip-btn {
  font-size: clamp(12px, 1.8vw, 13px);
  color: var(--text-muted);
  cursor: pointer;
  transition: color 150ms;
}
.skip-btn:hover { color: var(--text-primary); }

/* ---- Mobile ---- */
@media (max-width: 480px) {
  .login-root { padding: 16px 14px 40px; }
  .skill-row__desc { display: none; }
}
</style>
