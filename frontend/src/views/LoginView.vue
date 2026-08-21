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

    <div class="login__layout">
      <!-- 左侧：建号表单 -->
      <div class="login__card">
        <div class="login__header">
          <z-tag v-if="theme.isZzz" type="fire" class="login__ztag">JNU INFORMATION</z-tag>
          <span v-else class="login__ak-kicker">JNU INFORMATION</span>
          <h1 class="login__title">建号</h1>
          <p class="login__subtitle">选择你的身份，开启个性化指南</p>
        </div>

        <!-- 头像上传 -->
        <div class="login__field">
          <label class="login__label">
            <span class="login__label-dot" />
            头像
          </label>
          <div class="login__avatar-upload" @click="triggerFileInput">
            <img v-if="avatarBase64" :src="avatarBase64" alt="头像" class="login__avatar-img" />
            <div v-else class="login__avatar-placeholder" :class="theme.isZzz ? 'login__avatar-placeholder--zzz' : 'login__avatar-placeholder--ak'">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
              <span class="login__avatar-hint">点击上传</span>
            </div>
          </div>
          <input ref="fileInputRef" type="file" accept="image/*" class="login__file-input" @change="handleFileChange" />
          <button v-if="avatarBase64" class="login__avatar-remove" @click="removeAvatar">移除</button>
        </div>

        <!-- 昵称 -->
        <div class="login__field">
          <label class="login__label">
            <span class="login__label-dot" />
            昵称
          </label>
          <z-input
            v-if="theme.isZzz"
            v-model="nickname"
            placeholder="输入你的昵称"
            maxlength="20"
            clearable
            class="login__zinput"
          />
          <input
            v-else
            v-model="nickname"
            class="login__ak-input"
            :class="{ 'login__ak-input--filled': nickname }"
            placeholder="输入你的昵称"
            maxlength="20"
          />
        </div>

        <!-- 专业类别 -->
        <div class="login__field">
          <label class="login__label">
            <span class="login__label-dot" />
            专业类别
          </label>
          <div class="login__radio-group">
            <z-radio v-if="theme.isZzz" v-model="major" shape="button" value="software" size="large">软件类</z-radio>
            <z-radio v-if="theme.isZzz" v-model="major" shape="button" value="hardware" size="large">硬件类</z-radio>
            <z-radio v-if="theme.isZzz" v-model="major" shape="button" value="other" size="large">其他类</z-radio>
            <template v-else>
              <button
                v-for="m in majorOptions"
                :key="m.value"
                class="login__ak-radio"
                :class="{ 'login__ak-radio--active': major === m.value }"
                @click="major = m.value"
              >{{ m.label }}</button>
            </template>
          </div>
        </div>

        <!-- 年级 -->
        <div class="login__field">
          <label class="login__label">
            <span class="login__label-dot" />
            年级
          </label>
          <div class="login__radio-group login__radio-group--4">
            <z-radio v-if="theme.isZzz" v-model="grade" shape="button" :value="1" size="large">大一</z-radio>
            <z-radio v-if="theme.isZzz" v-model="grade" shape="button" :value="2" size="large">大二</z-radio>
            <z-radio v-if="theme.isZzz" v-model="grade" shape="button" :value="3" size="large">大三</z-radio>
            <z-radio v-if="theme.isZzz" v-model="grade" shape="button" :value="4" size="large">大四</z-radio>
            <template v-else>
              <button
                v-for="g in gradeOptions"
                :key="g.value"
                class="login__ak-radio"
                :class="{ 'login__ak-radio--active': grade === g.value }"
                @click="grade = g.value"
              >{{ g.label }}</button>
            </template>
          </div>
        </div>

        <!-- 建号按钮 -->
        <z-button
          v-if="theme.isZzz"
          type="primary"
          size="large"
          class="login__zenter"
          :disabled="!canEnter"
          @click="handleLogin"
        >
          建 号
        </z-button>
        <button
          v-else
          class="login__ak-enter"
          :class="{ 'login__ak-enter--disabled': !canEnter }"
          :disabled="!canEnter"
          @click="handleLogin"
        >
          <span>建 号</span>
          <span class="login__ak-enter-arrow">→</span>
        </button>

        <button class="login__guest" @click="handleGuest">
          游客模式浏览
          <span class="login__guest-arrow">→</span>
        </button>

        <p class="login__note">数据仅保存在本浏览器，不会上传</p>
      </div>

      <!-- 右侧：工牌预览 -->
      <div class="login__preview">
        <div class="login__preview-label">工牌预览</div>
        <div class="login__preview-card" :class="theme.isZzz ? 'login__preview-card--zzz' : 'login__preview-card--ak'">
          <div v-if="theme.isZzz" class="login__preview-grid" />
          <div class="login__preview-header">
            <span v-if="theme.isZzz" class="login__preview-logo login__preview-logo--zzz">TERMINAL CONNECT</span>
            <span v-else class="login__preview-logo login__preview-logo--ak">MEMBER ARCHIVE</span>
            <span v-if="!theme.isZzz" class="login__preview-id">#{{ previewUid.slice(-4) }}</span>
          </div>
          <div class="login__preview-body">
            <div class="login__preview-avatar" :class="theme.isZzz ? 'login__preview-avatar--zzz' : 'login__preview-avatar--ak'">
              <img v-if="avatarBase64" :src="avatarBase64" alt="" class="login__preview-avatar-img" />
              <div v-else class="login__preview-avatar-ph">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 12a4 4 0 100-8 4 4 0 000 8zm0 2c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" fill="currentColor" opacity="0.3"/>
                </svg>
              </div>
            </div>
            <div class="login__preview-info">
              <div class="login__preview-row">
                <span class="login__preview-key" :class="theme.isZzz ? 'login__preview-key--zzz' : 'login__preview-key--ak'">{{ theme.isZzz ? '代理人' : '昵称' }}</span>
                <span class="login__preview-val">{{ nickname || '---' }}</span>
              </div>
              <div class="login__preview-row">
                <span class="login__preview-key" :class="theme.isZzz ? 'login__preview-key--zzz' : 'login__preview-key--ak'">{{ theme.isZzz ? '等级' : '年级' }}</span>
                <span class="login__preview-val">{{ gradeLabel || '---' }}</span>
              </div>
              <div class="login__preview-row">
                <span class="login__preview-key" :class="theme.isZzz ? 'login__preview-key--zzz' : 'login__preview-key--ak'">{{ theme.isZzz ? '职业' : '专业' }}</span>
                <span class="login__preview-val">{{ majorLabel || '---' }}</span>
              </div>
            </div>
          </div>
          <div class="login__preview-footer">
            <span class="login__preview-uid">UID: {{ previewUid }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 身份工牌弹窗（建号完成） -->
    <IdentityBadge :visible="showBadge" mode="create" @close="handleBadgeClose" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';
import type { Grade, MajorCategory } from '@/stores/userStore';
import IdentityBadge from '@/components/login/IdentityBadge.vue';

const router = useRouter();
const theme = useThemeStore();
const userStore = useUserStore();

const nickname = ref('');
const major = ref<MajorCategory | null>(null);
const grade = ref<Grade | null>(null);
const avatarBase64 = ref<string>('');
const showBadge = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

const majorOptions = [
  { value: 'software' as MajorCategory, label: '软件类' },
  { value: 'hardware' as MajorCategory, label: '硬件类' },
  { value: 'other' as MajorCategory, label: '其他类' },
];
const gradeOptions = [
  { value: 1 as Grade, label: '大一' },
  { value: 2 as Grade, label: '大二' },
  { value: 3 as Grade, label: '大三' },
  { value: 4 as Grade, label: '大四' },
];

const canEnter = computed(() => nickname.value.trim() && major.value !== null && grade.value !== null);

const gradeLabel = computed(() => {
  if (grade.value === null) return '';
  return { 1: '大一', 2: '大二', 3: '大三', 4: '大四' }[grade.value];
});

const majorLabel = computed(() => {
  if (major.value === null) return '';
  return { software: '软件类', hardware: '硬件类', other: '其他类' }[major.value];
});

const previewUid = computed(() => {
  const d = new Date();
  const ymd = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
  return `XKZ-${ymd}-****`;
});

function triggerFileInput() {
  fileInputRef.value?.click();
}

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (file.size > 2 * 1024 * 1024) {
    alert('图片不能超过 2MB');
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    avatarBase64.value = reader.result as string;
  };
  reader.readAsDataURL(file);
  // reset input so same file can be re-selected
  target.value = '';
}

function removeAvatar() {
  avatarBase64.value = '';
}

function handleLogin() {
  if (!canEnter.value) return;
  userStore.login({
    nickname: nickname.value.trim(),
    grade: grade.value!,
    major: major.value!,
    avatar: avatarBase64.value || undefined,
  });
  showBadge.value = true;
}

function handleBadgeClose() {
  showBadge.value = false;
  router.push('/');
}

function handleGuest() {
  userStore.logout();
  router.push('/?guest=1');
}
</script>

<style scoped>
.login,
.login__card,
.login__card *,
.login__radio-group,
.login__radio-group *,
.login__layout,
.login__preview,
.login__preview * {
  box-sizing: border-box;
}

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

.login--zzz, .login--ak {
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
   双栏布局
   ============================================ */
.login__layout {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 32px;
  align-items: stretch;
  width: 100%;
  max-width: 880px;
}

/* ============================================
   建号表单卡片
   ============================================ */
.login__card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 36px 32px;
  background: var(--bg-panel);
  border: 1px solid var(--border-subtle);
  transition: background 300ms, border-color 300ms;
  overflow-x: hidden;
}

.login--zzz .login__card {
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

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

.login__ztag { margin-bottom: 4px; }

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
   头像上传
   ============================================ */
.login__avatar-upload {
  width: 80px;
  height: 80px;
  cursor: pointer;
  overflow: hidden;
  flex-shrink: 0;
}

.login--zzz .login__avatar-upload {
  border-radius: 50%;
  border: 2px solid var(--amber);
  box-shadow: 0 0 12px var(--amber-glow);
}

.login--ak .login__avatar-upload {
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
}

.login__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login__avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.login__avatar-placeholder--zzz {
  color: var(--text-muted);
  background: var(--bg-panel-2);
}

.login__avatar-placeholder--ak {
  color: var(--text-muted);
  background: var(--bg-panel-2);
}

.login__avatar-hint {
  font-size: 10px;
  letter-spacing: 1px;
}

.login__file-input {
  display: none;
}

.login__avatar-remove {
  align-self: flex-start;
  font-size: 12px;
  color: var(--danger);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 0;
}

.login__avatar-remove:hover {
  text-decoration: underline;
}

/* ============================================
   Radio Group
   ============================================ */
.login__radio-group {
  width: 100%;
  display: flex;
  gap: 8px;
}

.login__radio-group--4 {
  justify-content: space-between;
}

.login__radio-group :deep(.z-radio) {
  flex: 1;
}

.login__radio-group :deep(.z-radio__label) {
  font-family: var(--font-body);
}

/* AK 日间：自定义卡片式单选 */
.login__ak-radio {
  flex: 1;
  padding: 10px 14px;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  border-bottom: 2px solid var(--border-subtle);
  cursor: pointer;
  transition: all 200ms;
  text-align: center;
}

.login__ak-radio:hover {
  border-color: var(--amber);
  color: var(--amber);
}

.login__ak-radio--active {
  color: var(--amber);
  border-color: var(--amber);
  border-bottom-color: var(--amber);
  background: var(--amber-soft);
}

/* ============================================
   昵称输入
   ============================================ */
.login__zinput { width: 100%; }

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
   建号按钮
   ============================================ */
.login__zenter {
  width: 100%;
  margin-top: 4px;
}

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
   工牌预览
   ============================================ */
.login__preview {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login__preview-label {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.login__preview-card {
  position: relative;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.login__preview-card--zzz {
  background: #101114;
  border: 1px solid rgba(255, 217, 61, 0.3);
  clip-path: polygon(var(--cut-sm) 0, 100% 0, 100% calc(100% - var(--cut-sm)), calc(100% - var(--cut-sm)) 100%, 0 100%, 0 var(--cut-sm));
}

.login__preview-card--ak {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(200, 50, 63, 0.15);
  border-left: 3px solid #C8323F;
}

.login__preview-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 217, 61, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 217, 61, 0.02) 1px, transparent 1px);
  background-size: 16px 16px;
  pointer-events: none;
}

.login__preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.login__preview-logo--zzz {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
  color: #FFD93D;
}

.login__preview-logo--ak {
  font-family: 'Noto Serif SC', serif;
  font-size: 13px;
  font-weight: 700;
  color: #C8323F;
}

.login__preview-id {
  font-family: var(--font-mono);
  font-size: 11px;
  color: rgba(200, 50, 63, 0.5);
}

.login__preview-body {
  display: flex;
  gap: 14px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.login__preview-avatar {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login__preview-avatar--zzz {
  border-radius: 50%;
  border: 2px solid #FFD93D;
}

.login__preview-avatar--ak {
  border-radius: 4px;
  border: 1px solid rgba(200, 50, 63, 0.2);
  background: #E0E4E8;
}

.login__preview-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login__preview-avatar-ph {
  color: var(--text-muted);
}

.login__preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login__preview-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login__preview-key {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  width: 50px;
  flex-shrink: 0;
}

.login__preview-key--zzz { color: rgba(255, 217, 61, 0.5); }
.login__preview-key--ak { color: rgba(200, 50, 63, 0.5); }

.login__preview-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.login__preview-footer {
  position: relative;
  z-index: 1;
}

.login__preview-uid {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 1px;
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 879px) {
  .login__layout {
    flex-direction: column;
    max-width: 440px;
  }

  .login__preview {
    width: 100%;
  }
}

@media (max-width: 767px) {
  .login {
    padding: 16px 12px;
  }

  .login__card {
    padding: 28px 20px;
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
