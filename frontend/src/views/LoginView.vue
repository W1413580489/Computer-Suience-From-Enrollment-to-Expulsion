<template>
  <div class="login" :class="theme.isZzz ? 'login--zzz' : 'login--ak'">
    <!-- ZZZ 夜间：涂鸦装饰 + 几何元素 + CRT扫描线 -->
    <div v-if="theme.isZzz" class="login__deco">
      <span class="login__deco-diamond" />
      <span class="login__deco-diamond login__deco-diamond--2" />
      <span class="login__deco-line" />
      <span class="login__deco-line login__deco-line--2" />
      <span class="login__deco-dot" />
      <span class="login__deco-dot login__deco-dot--2" />
      <!-- 涂鸦飞溅 -->
      <span class="login__graffiti-splash login__graffiti-splash--1" />
      <span class="login__graffiti-splash login__graffiti-splash--2" />
      <!-- 胶带贴纸 -->
      <span class="login__tape login__tape--1">NEW ERIDU</span>
      <span class="login__tape login__tape--2">PROXY NET</span>
      <!-- 手写圈标记 -->
      <svg class="login__graffiti-circle" viewBox="0 0 200 80" fill="none">
        <path d="M20,40 Q40,15 100,20 T180,40 Q160,65 100,60 T20,40 Z" stroke="#FFD93D" stroke-width="2" opacity="0.15" stroke-linecap="round" />
      </svg>
      <!-- CRT扫描线 -->
      <div class="login__crt-overlay" />
    </div>
    <!-- AK 日间：档案夹底纹 + 战术装饰 -->
    <div v-else class="login__ak-bg">
      <span class="login__ak-stripe" />
      <span class="login__ak-stripe login__ak-stripe--2" />
      <span class="login__ak-diamond" />
      <!-- 档案夹条纹底纹 -->
      <div class="login__ak-archive-bg" />
      <!-- 战术角标 -->
      <span class="login__ak-tac-corner login__ak-tac-corner--tl" />
      <span class="login__ak-tac-corner login__ak-tac-corner--br" />
      <!-- 数据流装饰 -->
      <div class="login__ak-data-stream">
        <span v-for="i in 5" :key="i" class="login__ak-data-line" :style="{ animationDelay: (i * -0.5) + 's' }">
          REC_{{ String(i).padStart(3, '0') }} :: ARCHIVE
        </span>
      </div>
    </div>

    <div class="login__layout">
      <!-- 左侧：建号表单 -->
      <div class="login__card">
        <div class="login__header">
          <z-tag v-if="theme.isZzz" type="fire" class="login__ztag">JNU INFORMATION</z-tag>
          <span v-else class="login__ak-kicker">JNU INFORMATION</span>
          <h1 v-if="theme.isZzz" class="login__title">建 号</h1>
          <div v-else class="login__title-wrap">
            <h1 class="login__title login__title--ak">档案初始化</h1>
            <span class="login__title-en">ARCHIVE INITIALIZATION</span>
          </div>
          <p class="login__subtitle">选择你的身份，开启个性化指南</p>
        </div>

        <!-- 头像上传 -->
        <div class="login__field">
          <label class="login__label">
            <span class="login__label-dot" />
            头像
          </label>
          <div class="login__avatar-upload" :class="theme.isZzz ? 'login__avatar-upload--monitor' : 'login__avatar-upload--archive'" @click="triggerFileInput">
            <img v-if="avatarBase64" :src="avatarBase64" alt="头像" class="login__avatar-img" />
            <div v-else class="login__avatar-placeholder" :class="theme.isZzz ? 'login__avatar-placeholder--zzz' : 'login__avatar-placeholder--ak'">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
              <span class="login__avatar-hint">点击上传</span>
            </div>
            <!-- ZZZ 监控录制指示器 -->
            <span v-if="theme.isZzz" class="login__rec-dot" />
            <!-- ZZZ 监控网格叠加 -->
            <div v-if="theme.isZzz" class="login__monitor-grid" />
            <!-- ZZZ 扫描线 -->
            <div v-if="theme.isZzz" class="login__monitor-scan" />
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

      <!-- 移动端下滑提示 -->
      <div class="login__scroll-hint">
        <span class="login__scroll-hint-text">下滑查看工牌预览</span>
        <svg class="login__scroll-hint-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 5v14M19 12l-7 7-7-7"/>
        </svg>
      </div>

      <!-- 右侧：工牌预览 -->
      <div class="login__preview">
        <div class="login__preview-label">
          {{ theme.isZzz ? 'CH.01 // 工牌预览' : '工牌预览 // PREVIEW' }}
        </div>
        <div class="login__preview-card" :class="theme.isZzz ? 'login__preview-card--zzz' : 'login__preview-card--ak'">
          <div v-if="theme.isZzz" class="login__preview-grid" />
          <!-- ZZZ CRT 扫描线 -->
          <div v-if="theme.isZzz" class="login__preview-scanline" />
          <!-- AK 四角标记 -->
          <template v-if="!theme.isZzz">
            <span class="login__preview-corner login__preview-corner--tl" />
            <span class="login__preview-corner login__preview-corner--tr" />
            <span class="login__preview-corner login__preview-corner--bl" />
            <span class="login__preview-corner login__preview-corner--br" />
          </template>
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
import { useAchievementStore } from '@/stores/achievementStore';

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
  // 成就：完成建号
  useAchievementStore().unlock('id_card');
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
  position: fixed;
  inset: 0;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
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

/* ZZZ CRT扫描线覆盖层 */
.login__crt-overlay {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0px,
    transparent 2px,
    rgba(255, 217, 61, 0.015) 2px,
    rgba(255, 217, 61, 0.015) 3px
  );
  pointer-events: none;
  z-index: 1;
}

/* 涂鸦飞溅 */
.login__graffiti-splash {
  position: absolute;
  border-radius: 50%;
  filter: blur(8px);
  pointer-events: none;
}

.login__graffiti-splash--1 {
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(255, 217, 61, 0.06) 0%, transparent 70%);
  top: 15%;
  right: 8%;
}

.login__graffiti-splash--2 {
  width: 90px;
  height: 90px;
  background: radial-gradient(circle, rgba(0, 240, 255, 0.05) 0%, transparent 70%);
  bottom: 20%;
  left: 5%;
}

/* 胶带贴纸 */
.login__tape {
  position: absolute;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: rgba(255, 217, 61, 0.25);
  background: rgba(255, 217, 61, 0.06);
  padding: 3px 10px;
  pointer-events: none;
  z-index: 1;
}

.login__tape--1 {
  top: 8%;
  left: 4%;
  transform: rotate(-8deg);
  clip-path: polygon(4px 0, calc(100% - 4px) 0, 100% 100%, 0 100%);
}

.login__tape--2 {
  bottom: 12%;
  right: 6%;
  transform: rotate(6deg);
  color: rgba(0, 240, 255, 0.25);
  background: rgba(0, 240, 255, 0.05);
  clip-path: polygon(4px 0, calc(100% - 4px) 0, 100% 100%, 0 100%);
}

/* 手写圈标记 */
.login__graffiti-circle {
  position: absolute;
  width: 180px;
  height: 70px;
  top: 40%;
  right: 3%;
  pointer-events: none;
  z-index: 1;
}

/* ZZZ 监控风格头像 */
.login__avatar-upload--monitor {
  position: relative;
  border-radius: 8px !important;
  border: 1px solid rgba(255, 217, 61, 0.4) !important;
  box-shadow: 0 0 16px rgba(255, 217, 61, 0.15), inset 0 0 20px rgba(0, 0, 0, 0.5) !important;
  overflow: hidden;
}

.login__avatar-upload--archive {
  position: relative;
  border-radius: 2px !important;
  border: 1px solid rgba(200, 50, 63, 0.3) !important;
  box-shadow: 0 1px 4px rgba(200, 50, 63, 0.08) !important;
}

.login__rec-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FF3B3B;
  box-shadow: 0 0 6px rgba(255, 59, 59, 0.8);
  animation: login-rec-blink 1.2s ease-in-out infinite;
  z-index: 2;
}

@keyframes login-rec-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

.login__monitor-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 217, 61, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 217, 61, 0.06) 1px, transparent 1px);
  background-size: 12px 12px;
  pointer-events: none;
  z-index: 1;
}

.login__monitor-scan {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(255, 217, 61, 0.08) 50%, transparent 100%);
  background-size: 100% 8px;
  pointer-events: none;
  z-index: 1;
  animation: login-monitor-scan 3s linear infinite;
}

@keyframes login-monitor-scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

/* AK 档案夹条纹底纹 */
.login__ak-archive-bg {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    135deg,
    transparent 0px,
    transparent 60px,
    rgba(200, 50, 63, 0.015) 60px,
    rgba(200, 50, 63, 0.015) 61px
  );
  pointer-events: none;
}

/* AK 战术角标 */
.login__ak-tac-corner {
  position: absolute;
  width: 60px;
  height: 60px;
  border: 1px solid rgba(200, 50, 63, 0.15);
  pointer-events: none;
}

.login__ak-tac-corner--tl {
  top: 20px;
  left: 20px;
  border-right: none;
  border-bottom: none;
}

.login__ak-tac-corner--br {
  bottom: 20px;
  right: 20px;
  border-left: none;
  border-top: none;
}

/* AK 数据流装饰 */
.login__ak-data-stream {
  position: absolute;
  right: 20px;
  top: 80px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: rgba(200, 50, 63, 0.12);
  pointer-events: none;
  overflow: hidden;
  height: 200px;
  mask-image: linear-gradient(to bottom, transparent, black 30%, black 70%, transparent);
  -webkit-mask-image: linear-gradient(to bottom, transparent, black 30%, black 70%, transparent);
}

.login__ak-data-line {
  white-space: nowrap;
  animation: login-data-scroll 8s linear infinite;
}

@keyframes login-data-scroll {
  0% { transform: translateY(0); opacity: 0; }
  20% { opacity: 1; }
  80% { opacity: 1; }
  100% { transform: translateY(-60px); opacity: 0; }
}

/* AK 双行标题 */
.login__title-wrap {
  text-align: center;
}

.login__title-en {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--amber);
  opacity: 0.5;
  margin-top: 2px;
}

/* AK 预览四角标记 */
.login__preview-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border: 1px solid rgba(200, 50, 63, 0.3);
  pointer-events: none;
}

.login__preview-corner--tl { top: 6px; left: 6px; border-right: none; border-bottom: none; }
.login__preview-corner--tr { top: 6px; right: 6px; border-left: none; border-bottom: none; }
.login__preview-corner--bl { bottom: 6px; left: 6px; border-right: none; border-top: none; }
.login__preview-corner--br { bottom: 6px; right: 6px; border-left: none; border-top: none; }

/* ZZZ 预览扫描线 */
.login__preview-scanline {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0px,
    transparent 2px,
    rgba(255, 217, 61, 0.02) 2px,
    rgba(255, 217, 61, 0.02) 3px
  );
  pointer-events: none;
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
   移动端下滑提示
   ============================================ */
.login__scroll-hint {
  display: none;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 0 4px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.login__scroll-hint-arrow {
  animation: login-hint-bounce 1.6s ease-in-out infinite;
}

@keyframes login-hint-bounce {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(4px); opacity: 1; }
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

  /* 下滑提示：仅移动端可见 */
  .login__scroll-hint {
    display: flex;
  }
}

@media (max-width: 767px) {
  .login {
    padding: 12px 10px;
    align-items: flex-start;
  }

  .login__card {
    padding: 20px 16px;
    gap: 12px;
  }

  .login__header {
    gap: 4px;
    margin-bottom: 0;
  }

  .login__title {
    font-size: 22px;
  }

  .login__subtitle {
    font-size: 12px;
  }

  .login__field {
    gap: 6px;
  }

  .login__label {
    font-size: 11px;
    letter-spacing: 1.5px;
  }

  .login__avatar-upload {
    width: 64px;
    height: 64px;
  }

  .login__avatar-hint {
    font-size: 9px;
  }

  .login__radio-group {
    gap: 6px;
  }

  .login__radio-group--4 {
    flex-wrap: wrap;
  }

  .login__radio-group :deep(.z-radio) {
    min-width: calc(50% - 3px);
  }

  .login__ak-radio {
    padding: 8px 10px;
    font-size: 13px;
  }

  .login__ak-enter {
    font-size: 15px;
    padding: 12px 16px;
    letter-spacing: 3px;
  }

  .login__zenter {
    padding: 10px 16px;
  }

  .login__guest {
    font-size: 12px;
    padding: 6px;
  }

  .login__note {
    font-size: 10px;
  }

  .login__preview {
    gap: 8px;
  }

  .login__preview-label {
    font-size: 10px;
  }

  .login__preview-card {
    padding: 16px 14px;
    gap: 12px;
  }

  .login__preview-body {
    gap: 10px;
  }

  .login__preview-avatar {
    width: 44px;
    height: 44px;
  }

  .login__preview-key {
    font-size: 9px;
    width: 42px;
  }

  .login__preview-val {
    font-size: 12px;
  }

  .login__tape {
    font-size: 8px;
    padding: 2px 6px;
  }

  .login__graffiti-circle {
    width: 120px;
    height: 50px;
  }

  .login__ak-data-stream {
    display: none;
  }
}

@media (max-width: 380px) {
  .login__card {
    padding: 16px 12px;
    gap: 10px;
  }

  .login__title {
    font-size: 20px;
  }

  .login__radio-group--4 .login__ak-radio,
  .login__radio-group--4 :deep(.z-radio) {
    min-width: calc(50% - 3px);
    font-size: 12px;
    padding: 6px 8px;
  }

  .login__avatar-upload {
    width: 56px;
    height: 56px;
  }
}
</style>
