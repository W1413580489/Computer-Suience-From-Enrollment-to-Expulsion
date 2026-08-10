<template>
  <div class="login-root">
    <!-- Header -->
    <div class="login-header">
      <span class="login-header__tag">CHARACTER CREATION</span>
      <h1 class="login-header__title">新玩家账号登录</h1>
      <p class="login-header__sub">
        入学前请打开你的「角色背包」，检查以下装备是否齐全
      </p>
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
    </section>

    <!-- Skill Points -->
    <section class="login-section">
      <h2 class="section-title">
        <span class="section-title__num">02</span>
        技能预加点
        <span class="section-title__badge">剩余 {{ remainingPoints }} 点</span>
      </h2>
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
        确认登录
        <span class="login-btn__hint">(已备 {{ equippedCount }}/{{ equipment.length }} 件装备)</span>
      </button>
      <button class="skip-btn" @click="skip">跳过，直接进入 >> </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { loadProgress, saveProgress, canAllocateSkill, MAX_SKILL_POINTS } from '@/composables/useQuest';

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
  progress.hasSeenIntro = true;
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
  max-width: 600px;
  margin: 0 auto;
  padding: 32px 24px 60px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}
.login-header__tag {
  display: inline-block;
  font-family: var(--font-display);
  font-size: 12px;
  letter-spacing: 4px;
  color: var(--amber);
  border: 1px solid var(--amber-glow);
  border-radius: var(--radius-sm);
  padding: 4px 12px;
  margin-bottom: 14px;
}
.login-header__title {
  font-size: 28px;
  font-weight: 700;
  color: var(--amber);
  margin-bottom: 8px;
}
.login-header__sub {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.login-section {
  margin-bottom: 36px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}
.section-title__num {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--amber);
}
.section-title__badge {
  font-size: 12px;
  font-weight: 400;
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid var(--success-border);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  margin-left: auto;
}

.equip-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.equip-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 200ms, background 200ms;
  text-align: left;
}
.equip-card:hover { border-color: var(--accent-bright); }
.equip-card--done {
  border-color: var(--success-border);
  background: var(--success-soft);
}
.equip-card__icon { font-size: 20px; flex-shrink: 0; }
.equip-card__body { display: flex; flex-direction: column; gap: 2px; }
.equip-card__name { font-size: 15px; font-weight: 500; }
.equip-card__hint { font-size: 12px; color: var(--text-muted); }

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skill-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.skill-row__info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.skill-row__name { font-size: 15px; font-weight: 500; }
.skill-row__desc { font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.skill-row__ctrl { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.skill-btn {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-panel-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
  transition: border-color 150ms;
}
.skill-btn:hover:not(:disabled) { border-color: var(--accent-bright); }
.skill-btn:disabled { opacity: .3; cursor: default; }
.skill-row__val {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--amber);
  min-width: 24px; text-align: center;
}
.skill-row--max .skill-row__val { color: var(--success); }

.login-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-top: 40px;
}
.login-btn {
  width: 100%; max-width: 360px;
  padding: 14px;
  background: var(--amber);
  color: var(--on-amber);
  border-radius: var(--radius-md);
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 200ms, transform 150ms;
  display: flex; flex-direction: column; align-items: center; gap: 2px;
}
.login-btn:hover:not(:disabled) { opacity: .9; transform: translateY(-1px); }
.login-btn:disabled { opacity: .4; cursor: default; }
.login-btn__hint { font-size: 12px; font-weight: 400; opacity: .7; }
.skip-btn {
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 150ms;
}
.skip-btn:hover { color: var(--text-primary); }
</style>
