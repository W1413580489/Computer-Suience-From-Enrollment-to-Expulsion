<template>
  <Teleport v-if="theme.isZzz && visible" to="body">
    <!-- ZZZ 夜间：zenless-ui ZModal -->
    <z-modal
      :model-value="visible"
      :show-footer="false"
      @close="handleClose"
    >
      <div class="badge badge--zzz">
        <!-- 扫描线装饰 -->
        <div class="badge__scanline" />
        <div class="badge__grid-bg" />
        <!-- CRT 噪点纹理 -->
        <div class="badge__crt-noise" />

        <!-- 头部 -->
        <div class="badge__header badge__header--zzz">
          <div class="badge__header-left">
            <span class="badge__logo-text">TERMINAL CONNECT</span>
            <span class="badge__header-sub">PROXY ACCESS CARD</span>
          </div>
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
            <!-- 监控录制指示器 -->
            <span class="badge__rec-indicator" />
          </div>

          <!-- 信息区 -->
          <div class="badge__info">
            <div class="badge__info-row badge__info-row--neon">
              <span class="badge__info-label badge__info-label--zzz">代号</span>
              <span class="badge__info-value">{{ user?.nickname || '未知' }}</span>
            </div>
            <div class="badge__info-row badge__info-row--neon">
              <span class="badge__info-label badge__info-label--zzz">等级</span>
              <span class="badge__info-value">{{ userStore.gradeLabel }}</span>
            </div>
            <div class="badge__info-row badge__info-row--neon">
              <span class="badge__info-label badge__info-label--zzz">资质</span>
              <span class="badge__info-value">{{ userStore.majorLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">UID</span>
              <span class="badge__info-value badge__info-value--mono">{{ user?.uid || '---' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--zzz">注册</span>
              <span class="badge__info-value">{{ user?.createdAt || '---' }}</span>
            </div>
          </div>
        </div>

        <!-- 条形码区 -->
        <div class="badge__barcode-area">
          <div class="badge__barcode">
            <span v-for="i in 30" :key="i" class="badge__barcode-bar" :style="{ width: (i % 3 === 0 ? 3 : 1) + 'px' }" />
          </div>
          <span class="badge__barcode-text">{{ user?.uid || 'XKZ-00000000-0000' }}</span>
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
  </Teleport>

  <!-- AK 日间：自定义弹窗 -->
  <Teleport v-else-if="!theme.isZzz && visible" to="body">
    <div class="badge-overlay badge-overlay--ak" @click.self="handleClose">
      <div class="badge badge--ak">
        <!-- 左侧红色竖条（加粗） -->
        <div class="badge__left-bar" />
        <!-- 四角标记（双线战术风格） -->
        <span class="badge__corner badge__corner--tl" />
        <span class="badge__corner badge__corner--tr" />
        <span class="badge__corner badge__corner--bl" />
        <span class="badge__corner badge__corner--br" />
        <span class="badge__corner-inner badge__corner-inner--tl" />
        <span class="badge__corner-inner badge__corner-inner--tr" />
        <span class="badge__corner-inner badge__corner-inner--bl" />
        <span class="badge__corner-inner badge__corner-inner--br" />

        <!-- 头部 -->
        <div class="badge__header badge__header--ak">
          <div class="badge__header-left">
            <span class="badge__logo-text badge__logo-text--ak">MEMBER ARCHIVE</span>
            <span class="badge__header-sub badge__header-sub--ak">PERSONNEL FILE</span>
          </div>
          <span class="badge__archive-id">ARK-{{ user?.uid?.slice(-8) || '--------' }}</span>
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
            <!-- 评级装饰 -->
            <div class="badge__rating">
              <span v-for="i in 5" :key="i" class="badge__rating-star" :class="{ 'badge__rating-star--filled': i <= (user?.grade || 1) }" />
            </div>
          </div>

          <!-- 信息区 -->
          <div class="badge__info">
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">代号</span>
              <span class="badge__info-value">{{ user?.nickname || '未知' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">职级</span>
              <span class="badge__info-value">{{ userStore.gradeLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">专长</span>
              <span class="badge__info-value">{{ userStore.majorLabel }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">入职日期</span>
              <span class="badge__info-value">{{ user?.createdAt || '---' }}</span>
            </div>
            <div class="badge__info-row">
              <span class="badge__info-label badge__info-label--ak">权限等级</span>
              <span class="badge__info-value badge__info-value--ak-level">LEVEL {{ user?.grade || 1 }}</span>
            </div>
          </div>
        </div>

        <!-- 档案编号区 -->
        <div class="badge__archive-area">
          <div class="badge__archive-line" />
          <span class="badge__archive-no">FILE NO. {{ user?.uid?.replace('XKZ-', 'ARK-') || 'ARK-00000000-0000' }}</span>
          <div class="badge__archive-line" />
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
/* 隐藏 z-modal 默认头部和关闭按钮，工牌自带按钮 */
:deep(.z-modal__header) {
  display: none;
}
:deep(.z-modal__body) {
  padding: 0;
}

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

/* ZZZ CRT 噪点纹理 */
.badge__crt-noise {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255, 217, 61, 0.02) 0%, transparent 8%),
    radial-gradient(circle at 70% 60%, rgba(0, 240, 255, 0.015) 0%, transparent 6%);
  background-size: 60px 60px, 50px 50px;
  pointer-events: none;
  clip-path: inherit;
}

/* ZZZ 头部副标题 */
.badge__header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.badge__header-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  color: rgba(255, 217, 61, 0.4);
  text-transform: uppercase;
}

/* ZZZ 监控录制指示器 */
.badge__rec-indicator {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FF3B3B;
  box-shadow: 0 0 6px rgba(255, 59, 59, 0.8);
  animation: badge-rec-blink 1.2s ease-in-out infinite;
  z-index: 2;
}

@keyframes badge-rec-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

/* ZZZ 霓虹下划线信息行 */
.badge__info-row--neon {
  position: relative;
  padding-bottom: 4px;
}

.badge__info-row--neon::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 217, 61, 0.4), transparent);
  box-shadow: 0 0 4px rgba(255, 217, 61, 0.2);
}

/* ZZZ 条形码区 */
.badge__barcode-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 217, 61, 0.15);
  border-bottom: 1px solid rgba(255, 217, 61, 0.15);
}

.badge__barcode {
  display: flex;
  gap: 1px;
  height: 32px;
  align-items: center;
}

.badge__barcode-bar {
  height: 100%;
  background: #FFD93D;
  opacity: 0.7;
}

.badge__barcode-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  letter-spacing: 2px;
  color: rgba(255, 217, 61, 0.5);
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
  width: 5px;
  background: linear-gradient(180deg, #C8323F, #8B1F2A);
  box-shadow: 1px 0 4px rgba(200, 50, 63, 0.2);
}

/* AK 双线战术角标内框 */
.badge__corner-inner {
  position: absolute;
  width: 10px;
  height: 10px;
  border: 1px solid rgba(200, 50, 63, 0.2);
  pointer-events: none;
}

.badge__corner-inner--tl { top: 14px; left: 18px; border-right: none; border-bottom: none; }
.badge__corner-inner--tr { top: 14px; right: 14px; border-left: none; border-bottom: none; }
.badge__corner-inner--bl { bottom: 14px; left: 18px; border-right: none; border-top: none; }
.badge__corner-inner--br { bottom: 14px; right: 14px; border-left: none; border-top: none; }

/* AK 头部副标题 */
.badge__header-sub--ak {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  color: rgba(200, 50, 63, 0.4);
  text-transform: uppercase;
}

/* AK 评级装饰（星级） */
.badge__rating {
  position: absolute;
  bottom: -14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
}

.badge__rating-star {
  width: 8px;
  height: 8px;
  background: rgba(200, 50, 63, 0.15);
  clip-path: polygon(50% 0, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
}

.badge__rating-star--filled {
  background: #C8323F;
  box-shadow: 0 0 4px rgba(200, 50, 63, 0.4);
}

/* AK 权限等级值 */
.badge__info-value--ak-level {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #C8323F;
  font-weight: 700;
  letter-spacing: 1px;
}

/* AK 档案编号区 */
.badge__archive-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.badge__archive-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(200, 50, 63, 0.2), transparent);
}

.badge__archive-no {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: rgba(200, 50, 63, 0.5);
  white-space: nowrap;
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
