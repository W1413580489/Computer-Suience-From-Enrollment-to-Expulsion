<template>
  <Teleport to="body">
    <!-- ZZZ 夜间：ZModal 全屏 -->
    <z-modal
      v-if="theme.isZzz && visible"
      :is-visible="visible"
      is-fullscreen
      :show-close="false"
      @close="handleClose"
    >
      <div class="badge badge--zzz">
        <!-- 扫描线装饰 -->
        <div class="badge__scanline" />
        <div class="badge__grid-bg" />

        <!-- 头部 -->
        <div class="badge__header badge__header--zzz">
          <span class="badge__logo-text">TERMINAL CONNECT</span>
          <span class="badge__status">● ACTIVE</span>
        </div>

        <!-- 主体 -->
        <div class="badge__body">
          <!-- 头像区 -->
          <div class="badge__avatar-wrap badge__avatar-wrap--zzz">
            <img v-if="user?.avatar" :src="user.avatar" alt="头像" class="badge__avatar-img" />
            <div v-else class="badge__avatar-placeholder">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M12 12a4 4 0 100-8 4 4 0 000 8zm0 2c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" fill="currentColor" opacity="0.4"/>
              </svg>
            </div>
          </div>

          <!-- 信息区 -->
          <div class="badge__info">
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">代理人</span>
              <span class="badge__info-value">{{ user?.nickname || '未知' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">等级</span>
              <span class="badge__info-value">{{ userStore.gradeLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">职业</span>
              <span class="badge__info-value">{{ userStore.majorLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">UID</span>
              <span class="badge__info-value badge__info-value--mono">{{ user?.uid || '---' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">建号日期</span>
              <span class="badge__info-value">{{ user?.createdAt || '---' }}</span>
            </div>
          </div>
        </div>

        <!-- 按钮区 -->
        <div class="badge__actions">
          <button class="badge__btn badge__btn--primary-zzz" @click="handlePrimary">
            {{ mode === 'create' ? '确认，进入主页' : '确认，关闭' }}
          </button>
          <button v-if="mode === 'view'" class="badge__btn badge__btn--secondary-zzz" @click="handleSwitch">
            切换身份
          </button>
        </div>
      </div>
    </z-modal>

    <!-- AK 日间：自定义弹窗 -->
    <div v-if="!theme.isZzz && visible" class="badge-overlay badge-overlay--ak" @click.self="handleClose">
      <div class="badge badge--ak">
        <!-- 左侧红色竖条 -->
        <div class="badge__left-bar" />
        <!-- 四角标记 -->
        <span class="badge__corner badge__corner--tl" />
        <span class="badge__corner badge__corner--tr" />
        <span class="badge__corner badge__corner--bl" />
        <span class="badge__corner badge__corner--br" />

        <!-- 头部 -->
        <div class="badge__header badge__header--ak">
          <span class="badge__logo-text badge__logo-text--ak">MEMBER ARCHIVE</span>
          <span class="badge__archive-id">#{{ user?.uid?.slice(-4) || '----' }}</span>
        </div>

        <!-- 主体 -->
        <div class="badge__body badge__body--ak">
          <!-- 头像区 -->
          <div class="badge__avatar-wrap badge__avatar-wrap--ak">
            <img v-if="user?.avatar" :src="user.avatar" alt="头像" class="badge__avatar-img" />
            <div v-else class="badge__avatar-placeholder badge__avatar-placeholder--ak">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M12 12a4 4 0 100-8 4 4 0 000 8zm0 2c-4 0-8 2-8 6v2h16v-2c0-4-4-6-8-6z" fill="currentColor" opacity="0.3"/>
              </svg>
            </div>
          </div>

          <!-- 信息区 -->
          <div class="badge__info">
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">昵称</span>
              <span class="badge__info-value">{{ user?.nickname || '未知' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">年级</span>
              <span class="badge__info-value">{{ userStore.gradeLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">专业</span>
              <span class="badge__info-value">{{ userStore.majorLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">入职日期</span>
              <span class="badge__info-value">{{ user?.createdAt || '---' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">身份权限</span>
              <span class="badge__info-value">LEVEL {{ user?.grade || 1 }}</span>
            </div>
          </div>
        </div>

        <!-- 按钮区 -->
        <div class="badge__actions badge__actions--ak">
          <button class="badge__btn badge__btn--primary-ak" @click="handlePrimary">
            {{ mode === 'create' ? '确认，进入主页' : '确认，关闭' }}
          </button>
          <button v-if="mode === 'view'" class="badge__btn badge__btn--secondary-ak" @click="handleSwitch">
            切换身份
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useThemeStore } from '@/stores/themeStore';
import { useUserStore } from '@/stores/userStore';

const props = withDefaults(
  defineProps<{
    visible: boolean;
    mode?: 'create' | 'view';
  }>(),
  { mode: 'create' },
);

const emit = defineEmits<{ close: [] }>();

const router = useRouter();
const theme = useThemeStore();
const userStore = useUserStore();

const user = userStore.user;

function handleClose() {
  emit('close');
}

function handlePrimary() {
  emit('close');
  if (props.mode === 'create') {
    router.push('/');
  }
}

function handleSwitch() {
  emit('close');
  userStore.logout();
  router.push('/login');
}
</script>

<style scoped>
/* ============================================
   通用
   ============================================ */
.badge {
  position: relative;
  width: 100%;
  max-width: 420px;
  margin: auto;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-sizing: border-box;
}

.badge__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.badge__logo-text {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 18px;
  letter-spacing: 3px;
}

.badge__status {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
}

.badge__body {
  display: flex;
  gap: 20px;
  align-items: center;
}

.badge__avatar-wrap {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.badge__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge__avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.badge__info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge__info-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  width: 70px;
  flex-shrink: 0;
}

.badge__info-value {
  font-size: 14px;
  font-weight: 600;
}

.badge__info-value--mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

.badge__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.badge__btn {
  width: 100%;
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  border: none;
  cursor: pointer;
  transition: filter 200ms, transform 160ms, box-shadow 200ms;
  box-sizing: border-box;
}

/* ============================================
   ZZZ 夜间模式
   ============================================ */
.badge--zzz {
  background: #101114;
  border: 1px solid #FFD93D;
  box-shadow: 0 0 30px rgba(255, 217, 61, 0.2);
  clip-path: polygon(var(--cut-md) 0, 100% 0, 100% calc(100% - var(--cut-md)), calc(100% - var(--cut-md)) 100%, 0 100%, 0 var(--cut-md));
}

.badge__grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 217, 61, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 217, 61, 0.02) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
  clip-path: inherit;
}

.badge__scanline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #FFD93D, transparent);
  animation: badge-scan 3s linear infinite;
  pointer-events: none;
}

@keyframes badge-scan {
  0% { top: 0; opacity: 0.6; }
  50% { top: 100%; opacity: 0.6; }
  100% { top: 0; opacity: 0; }
}

.badge__header--zzz .badge__logo-text {
  color: #FFD93D;
}

.badge__header--zzz .badge__status {
  color: #4ECCA3;
}

.badge__avatar-wrap--zzz {
  border-radius: 50%;
  border: 2px solid #FFD93D;
  box-shadow: 0 0 12px rgba(255, 217, 61, 0.3);
}

.badge__avatar-placeholder {
  color: #4C4C4C;
}

.badge__info-label--zzz {
  color: rgba(255, 217, 61, 0.6);
}

.badge__header--zzz ~ .badge__body .badge__info-value,
.badge--zzz .badge__info-value {
  color: #F5F5F5;
}

.badge__btn--primary-zzz {
  background: #FFD93D;
  color: #0A0A0A;
  clip-path: var(--clip-sm);
}
.badge__btn--primary-zzz:hover {
  filter: brightness(1.1);
  box-shadow: 0 0 16px rgba(255, 217, 61, 0.4);
}

.badge__btn--secondary-zzz {
  background: transparent;
  color: #FFD93D;
  border: 1px solid rgba(255, 217, 61, 0.4);
  clip-path: var(--clip-sm);
}
.badge__btn--secondary-zzz:hover {
  background: rgba(255, 217, 61, 0.08);
  border-color: #FFD93D;
}

/* ============================================
   AK 日间模式
   ============================================ */
.badge-overlay--ak {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(234, 237, 240, 0.85);
  backdrop-filter: blur(4px);
}

.badge--ak {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(200, 50, 63, 0.2);
  box-shadow: 0 4px 24px rgba(60, 80, 120, 0.1);
  overflow: hidden;
}

.badge__left-bar {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 3px;
  background: #C8323F;
}

.badge__corner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 1px solid rgba(200, 50, 63, 0.3);
}
.badge__corner--tl { top: 8px; left: 12px; border-right: none; border-bottom: none; }
.badge__corner--tr { top: 8px; right: 8px; border-left: none; border-bottom: none; }
.badge__corner--bl { bottom: 8px; left: 12px; border-right: none; border-top: none; }
.badge__corner--br { bottom: 8px; right: 8px; border-left: none; border-top: none; }

.badge__header--ak {
  border-bottom: 1px solid rgba(200, 50, 63, 0.1);
  padding-bottom: 16px;
}

.badge__logo-text--ak {
  font-family: 'Noto Serif SC', serif;
  color: #C8323F;
  font-size: 16px;
  font-weight: 700;
}

.badge__archive-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: rgba(200, 50, 63, 0.5);
}

.badge__avatar-wrap--ak {
  border-radius: 4px;
  border: 1px solid rgba(200, 50, 63, 0.2);
  background: #E0E4E8;
}

.badge__avatar-placeholder--ak {
  color: #B0B8C4;
}

.badge__info-label--ak {
  color: rgba(200, 50, 63, 0.6);
}

.badge--ak .badge__info-value {
  color: #1A1D24;
}

.badge__btn--primary-ak {
  background: #C8323F;
  color: #FFFFFF;
}
.badge__btn--primary-ak:hover {
  filter: brightness(1.1);
  box-shadow: 0 2px 12px rgba(200, 50, 63, 0.2);
}

.badge__btn--secondary-ak {
  background: transparent;
  color: #C8323F;
  border: 1px solid rgba(200, 50, 63, 0.3);
}
.badge__btn--secondary-ak:hover {
  background: rgba(200, 50, 63, 0.06);
  border-color: #C8323F;
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 767px) {
  .badge {
    max-width: calc(100vw - 32px);
    padding: 24px 20px;
    gap: 20px;
  }

  .badge__body {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .badge__avatar-wrap {
    width: 64px;
    height: 64px;
  }
}
</style>
