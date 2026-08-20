<template>
  <div class="login" :class="theme.isZzz ? 'login--zzz' : 'login--ak'">
    <!-- ZZZ 夜间：装饰几何元素 -->
    <div v-if="theme.isZzz" class="login__deco">
      <span class="login__deco-diamond" />
      <span class="login__deco-diamond login__deco-diamond--2" />
      <span class="login__deco-line" />
      <span class="login__deco-line login__deco-line--2" />
      <span class="login__deco-dot" />
      <span class="login__deco-dot login__deco-dot--2" />
    </div>
    <!-- AK 日间：背景装饰 -->
    <div v-else class="login__ak-bg">
      <span class="login__ak-stripe" />
      <span class="login__ak-stripe login__ak-stripe--2" />
      <span class="login__ak-diamond" />
    </div>

    <div class="login__card">
      <!-- 标题区 -->
      <div class="login__header">
        <!-- ZZZ 夜间：zenless-ui 标签 -->
        <z-tag v-if="theme.isZzz" type="fire" class="login__ztag">JNU INFORMATION</z-tag>
        <!-- AK 日间：文本标签 -->
        <span v-else class="login__ak-kicker">JNU INFORMATION</span>
        <h1 class="login__title">信科院指南</h1>
        <p class="login__subtitle">选择你的身份，开启个性化指南</p>
      </div>

      <!-- 昵称 -->
      <div class="login__field">
        <label class="login__label">
          <span class="login__label-dot" />
          昵称
        </label>
        <!-- ZZZ 夜间：zenless-ui ZInput -->
        <z-input
          v-if="theme.isZzz"
          v-model="nickname"
          placeholder="输入你的昵称"
          maxlength="20"
          clearable
          class="login__zinput"
        />
        <!-- AK 日间：自定义输入 -->
        <input
          v-else
          v-model="nickname"
          class="login__ak-input"
          :class="{ 'login__ak-input--filled': nickname }"
          placeholder="输入你的昵称"
          maxlength="20"
        />
      </div>

      <!-- 专业类别 (zenless-ui 组件) -->
      <div class="login__field">
        <label class="login__label">
          <span class="login__label-dot" />
          专业类别
        </label>
        <z-radio-group v-model="major" class="login__radio-group">
          <z-radio-button value="software" size="large">软件类</z-radio-button>
          <z-radio-button value="hardware" size="large">硬件类</z-radio-button>
          <z-radio-button value="other" size="large">其他类</z-radio-button>
        </z-radio-group>
      </div>

      <!-- 年级 (zenless-ui 组件) -->
      <div class="login__field">
        <label class="login__label">
          <span class="login__label-dot" />
          年级
        </label>
        <z-radio-group v-model="grade" class="login__radio-group login__radio-group--4">
          <z-radio-button :value="1" size="large">大一</z-radio-button>
          <z-radio-button :value="2" size="large">大二</z-radio-button>
          <z-radio-button :value="3" size="large">大三</z-radio-button>
          <z-radio-button :value="4" size="large">大四</z-radio-button>
        </z-radio-group>
      </div>

      <!-- 进入按钮 -->
      <!-- ZZZ 夜间：zenless-ui ZButton -->
      <z-button
        v-if="theme.isZzz"
        type="primary"
        size="large"
        class="login__zenter"
        :disabled="!canEnter"
        @click="handleLogin"
      >
        进 入
      </z-button>
      <!-- AK 日间：自定义按钮 -->
      <button
        v-else
        class="login__ak-enter"
        :class="{ 'login__ak-enter--disabled': !canEnter }"
        :disabled="!canEnter"
        @click="handleLogin"
      >
        <span>进 入</span>
        <span class="login__ak-enter-arrow">→</span>
      </button>

      <!-- 游客模式 -->
      <button class="login__guest" @click="handleGuest">
        游客模式浏览
        <span class="login__guest-arrow">→</span>
      </button>

      <p class="login__note">数据仅保存在本浏览器，不会上传</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import type { Grade, MajorCategory } from '@/stores/userStore';

const router = useRouter();
const theme = useThemeStore();
const userStore = useUserStore();

const nickname = ref('');
const major = ref<MajorCategory | null>(null);
const grade = ref<Grade | null>(null);

const canEnter = computed(() => nickname.value.trim() && major.value !== null && grade.value !== null);

function handleLogin() {
  if (!canEnter.value) return;
  userStore.login({
    nickname: nickname.value.trim(),
    grade: grade.value!,
    major: major.value!,
  });
  router.push('/');
}

function handleGuest() {
  router.push('/?guest=1');
}
</script>

<style scoped>
/* ============================================
   基础盒模型
   ============================================ */
.login,
.login__card,
.login__card *,
.login__radio-group,
.login__radio-group * {
  box-sizing: border-box;
}

/* ============================================
   登录页 — 外层容器
   ============================================ */
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  overflow-x: hidden;
  position: relative;
  transition: background 300ms;
}

/* ---- ZZZ 夜间模式 ---- */
.login--zzz {
  background: var(--bg-body);
}

/* ---- AK 日间模式 ---- */
.login--ak {
  background: var(--bg-body);
}

/* ============================================
   ZZZ 装饰元素
   ============================================ */
.login__deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.login__deco-diamond {
  position: absolute;
  width: 80px;
  height: 80px;
  border: 1.5px solid var(--amber);
  opacity: 0.12;
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
  top: 8%;
  left: 6%;
  animation: login-float 8s ease-in-out infinite;
}

.login__deco-diamond--2 {
  width: 120px;
  height: 120px;
  top: auto;
  bottom: 10%;
  right: 5%;
  left: auto;
  animation-delay: -4s;
  border-color: var(--neon-cyan);
  opacity: 0.08;
}

.login__deco-line {
  position: absolute;
  width: 1px;
  height: 200px;
  background: linear-gradient(to bottom, transparent, var(--amber), transparent);
  opacity: 0.1;
  top: 50%;
  left: 12%;
  transform: translateY(-50%) rotate(15deg);
}

.login__deco-line--2 {
  left: auto;
  right: 15%;
  transform: translateY(-50%) rotate(-10deg);
  background: linear-gradient(to bottom, transparent, var(--neon-cyan), transparent);
}

.login__deco-dot {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--amber);
  border-radius: 50%;
  opacity: 0.2;
  top: 20%;
  right: 25%;
  animation: login-pulse 3s ease-in-out infinite;
}

.login__deco-dot--2 {
  width: 3px;
  height: 3px;
  background: var(--neon-cyan);
  top: 75%;
  left: 20%;
  animation-delay: -1.5s;
}

@keyframes login-float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(5deg); }
}

@keyframes login-pulse {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.5); }
}

/* ============================================
   AK 日间装饰
   ============================================ */
.login__ak-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.login__ak-stripe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--amber), var(--neon-cyan), transparent 80%);
  opacity: 0.3;
}

.login__ak-stripe--2 {
  top: auto;
  bottom: 0;
  background: linear-gradient(90deg, transparent 20%, var(--neon-cyan), var(--amber));
}

.login__ak-diamond {
  position: absolute;
  width: 180px;
  height: 180px;
  border: 1px solid var(--border-subtle);
  opacity: 0.25;
  transform: rotate(45deg);
  top: -60px;
  right: -60px;
}

/* ============================================
   Radio Group 适配双主题
   ============================================ */
.login__radio-group {
  width: 100%;
  display: flex;
  gap: 8px;
}

.login__radio-group--4 {
  justify-content: space-between;
}

.login__radio-group :deep(.z-radio-button) {
  flex: 1;
  justify-content: center;
  font-family: var(--font-body);
}

.login__radio-group--4 :deep(.z-radio-button) {
  max-width: none;
}

/* ============================================
   卡片
   ============================================ */
.login__card {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 40px 36px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  transition: background 300ms, border-color 300ms;
  overflow-x: hidden;
}

/* ZZZ 夜间卡片 — 切角 */
.login--zzz .login__card {
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

/* AK 日间卡片 — 无切角，用发丝细线 + 轻微阴影 */
.login--ak .login__card {
  box-shadow: 0 2px 16px rgba(60, 80, 120, 0.06);
}

/* ============================================
   标题区
   ============================================ */
.login__header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

/* ZZZ 夜间标签 */
.login__ztag {
  margin-bottom: 4px;
}

/* AK 日间标签 */
.login__ak-kicker {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--amber);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.login__title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 900;
  letter-spacing: 2px;
  color: var(--text-primary);
  text-align: center;
  margin: 0;
  line-height: 1.1;
}

.login__subtitle {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  margin: 0;
  letter-spacing: 0.5px;
}

/* ============================================
   字段
   ============================================ */
.login__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.login__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.login__label-dot {
  width: 5px;
  height: 5px;
  background: var(--amber);
  flex-shrink: 0;
}

.login--zzz .login__label-dot {
  clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%);
}

/* ============================================
   昵称输入
   ============================================ */
/* ZZZ 夜间：ZInput 覆盖 */
.login__zinput {
  width: 100%;
}

/* AK 日间：自定义输入 */
.login__ak-input {
  width: 100%;
  padding: 12px 14px;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  border-bottom: 2px solid var(--border-subtle);
  outline: none;
  transition: border-color 200ms, background 200ms;
  box-sizing: border-box;
  font-family: var(--font-body);
}

.login__ak-input:focus {
  border-color: var(--amber);
  border-bottom-color: var(--amber);
  background: var(--bg-panel-3);
}

.login__ak-input--filled {
  border-bottom-color: var(--amber);
}

.login__ak-input::placeholder {
  color: var(--text-muted);
}

/* ============================================
   进入按钮
   ============================================ */
/* ZZZ 夜间：ZButton 覆盖 */
.login__zenter {
  width: 100%;
  margin-top: 4px;
}

/* AK 日间：自定义按钮 */
.login__ak-enter {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px 20px;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 4px;
  color: var(--on-amber);
  background: var(--amber);
  border: none;
  clip-path: polygon(0 0, 100% 0, 100% 0, 100% 100%, 18px 100%, 0 calc(100% - 18px));
  cursor: pointer;
  transition: filter 200ms, transform 160ms, box-shadow 200ms;
  margin-top: 4px;
  box-sizing: border-box;
}

.login__ak-enter:hover:not(:disabled) {
  filter: brightness(1.08);
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 var(--neon-cyan);
}

.login__ak-enter-arrow {
  transition: transform 160ms;
  font-size: 20px;
}

.login__ak-enter:hover:not(:disabled) .login__ak-enter-arrow {
  transform: translateX(4px);
}

.login__ak-enter--disabled {
  opacity: 0.35;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

/* ============================================
   游客模式
   ============================================ */
.login__guest {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-muted);
  text-align: center;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  transition: color 200ms, gap 200ms;
  box-sizing: border-box;
}

.login__guest:hover {
  color: var(--amber);
  gap: 10px;
}

.login__guest-arrow {
  transition: transform 200ms;
}

.login__guest:hover .login__guest-arrow {
  transform: translateX(3px);
}

.login__note {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  margin: 0;
  letter-spacing: 0.3px;
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 767px) {
  .login {
    padding: 16px 12px;
  }

  .login__card {
    padding: 32px 20px;
    gap: 16px;
  }

  .login__title {
    font-size: 26px;
  }

  .login__radio-group {
    gap: 6px;
  }

  .login__radio-group--4 {
    flex-wrap: wrap;
  }

  .login__ak-enter {
    font-size: 16px;
    padding: 12px 18px;
  }
}
</style>