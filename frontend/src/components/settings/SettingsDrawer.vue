<template>
  <!-- 夜间 zzz：zenless-ui 抽屉面板。Teleport 到 body，避免父级 .hud-fade-in 的 transform 破坏 z-modal 的 position:fixed 上下文 -->
  <Teleport v-if="theme.isZzz && visible" to="body">
    <z-modal
      :model-value="visible"
      mode="drawer"
      title="设置 · BYOK"
      :show-footer="false"
      @close="emit('onClose')"
    >
    <div class="settings__body">
      <div
        class="settings__status-card"
        :class="settings.hasKey ? 'settings__status-card--ok' : 'settings__status-card--warn'"
      >
        <span class="settings__status-dot" />
        <div>
          <p class="settings__status-title">
            {{ settings.hasKey ? `已接入 ${settings.preset.label}` : '未配置 API Key' }}
          </p>
          <p class="settings__status-sub">
            {{ settings.hasKey ? '不限次数提问，Key 仅保存在本浏览器' : '当前使用平台免费额度：30 次/日，5 次/分钟' }}
          </p>
        </div>
      </div>

      <ol v-if="!settings.hasKey" class="settings__steps">
        <li class="settings__step">
          <span class="settings__step-num">1</span>
          <span>点击下方链接，打开 {{ settings.preset.label }} 开放平台</span>
        </li>
        <li class="settings__step">
          <span class="settings__step-num">2</span>
          <span>注册并创建一个新的 API Key（复制备用）</span>
        </li>
        <li class="settings__step">
          <span class="settings__step-num">3</span>
          <span>粘贴到下方输入框，点「测试连接」确认可用</span>
        </li>
      </ol>

      <p class="settings__hint">Key 仅保存在本浏览器本地存储，不会上传到服务器保存。</p>

      <div class="settings__field">
        <span class="settings__label">模型服务商</span>
        <!-- zenless-ui 下拉选择 -->
        <z-select
          :model-value="settings.provider"
          class="settings__zctrl"
          @change="onProviderChange"
        >
          <z-option
            v-for="p in PROVIDER_PRESETS"
            :key="p.key"
            :value="p.key"
            :label="p.label"
          />
        </z-select>
      </div>

      <div class="settings__field">
        <span class="settings__label">API Key</span>
        <!-- zenless-ui 密码输入框（自带明暗切换） -->
        <z-input
          v-model="settings.apiKey"
          class="settings__zctrl"
          type="password"
          placeholder="sk-..."
          autocomplete="off"
          @input="settings.save()"
        />
      </div>

      <div class="settings__field">
        <span class="settings__label">Base URL{{ settings.provider === 'custom' ? '（必填）' : '' }}</span>
        <z-input
          v-model="settings.baseUrl"
          class="settings__zctrl"
          type="text"
          :placeholder="settings.preset.baseUrl || 'https://your-openai-compatible-endpoint/v1'"
          :disabled="settings.provider !== 'custom'"
          @input="settings.save()"
        />
      </div>

      <div class="settings__field">
        <span class="settings__label">模型名</span>
        <z-input
          v-model="settings.model"
          class="settings__zctrl"
          type="text"
          :placeholder="settings.preset.model || 'model-name'"
          @input="settings.save()"
        />
      </div>

      <div class="settings__actions settings__zactions">
        <z-button
          type="primary"
          class="settings__zbtn"
          :disabled="!settings.hasKey || verifying"
          @click="onVerify"
        >{{ verifying ? '验证中…' : '测试连接' }}</z-button>
        <z-button
          class="settings__zbtn"
          :disabled="!settings.hasKey"
          @click="onClear"
        >清除 Key</z-button>
      </div>

      <p
        v-if="verifyResult"
        class="settings__verify"
        :class="verifyResult.valid ? 'settings__verify--ok' : 'settings__verify--fail'"
      >
        {{ verifyResult.message }}
      </p>

      <div class="settings__help">
        <a
          v-if="settings.preset.keyHelpUrl"
          class="settings__help-cta"
          :href="settings.preset.keyHelpUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          <NeonIcon name="external" :size="16" />
          打开 {{ settings.preset.label }} 开放平台，免费创建 Key
        </a>
        <p class="settings__help-text">未配置 Key 时使用平台免费额度（30 次/日/IP），配置后不受限制。</p>
      </div>

      <p v-if="health" class="settings__status">
        服务状态：{{ health.status === 'up' ? '在线' : '异常' }} · 知识块 {{ health.chunks }} ·
        平台免费额度{{ health.platform_key_configured ? '已开放' : '未开放' }}
      </p>
    </div>
    </z-modal>
  </Teleport>

  <!-- 日间 ak：原版右侧滑入面板 -->
  <Teleport v-else to="body">
    <Transition name="settings">
      <div v-if="visible" class="settings-mask" @click.self="emit('onClose')">
        <aside class="settings" role="dialog" aria-label="设置">
          <header class="settings__header">
            <h2 class="settings__title">设置 · BYOK</h2>
            <button class="settings__close" aria-label="关闭" @click="emit('onClose')">
              <NeonIcon name="close" :size="18" />
            </button>
          </header>

          <div class="settings__body">
            <!-- 当前状态 -->
            <div
              class="settings__status-card"
              :class="settings.hasKey ? 'settings__status-card--ok' : 'settings__status-card--warn'"
            >
              <span class="settings__status-dot" />
              <div>
                <p class="settings__status-title">
                  {{ settings.hasKey ? `已接入 ${settings.preset.label}` : '未配置 API Key' }}
                </p>
                <p class="settings__status-sub">
                  {{ settings.hasKey ? '不限次数提问，Key 仅保存在本浏览器' : '当前使用平台免费额度：30 次/日，5 次/分钟' }}
                </p>
              </div>
            </div>

            <!-- 三步指引 -->
            <ol v-if="!settings.hasKey" class="settings__steps">
              <li class="settings__step">
                <span class="settings__step-num">1</span>
                <span>点击下方链接，打开 {{ settings.preset.label }} 开放平台</span>
              </li>
              <li class="settings__step">
                <span class="settings__step-num">2</span>
                <span>注册并创建一个新的 API Key（复制备用）</span>
              </li>
              <li class="settings__step">
                <span class="settings__step-num">3</span>
                <span>粘贴到下方输入框，点「测试连接」确认可用</span>
              </li>
            </ol>

            <p class="settings__hint">
              Key 仅保存在本浏览器本地存储，不会上传到服务器保存。
            </p>

            <label class="settings__field">
              <span class="settings__label">模型服务商</span>
              <select
                class="settings__input"
                :value="settings.provider"
                @change="onProviderChange(($event.target as HTMLSelectElement).value)"
              >
                <option v-for="p in PROVIDER_PRESETS" :key="p.key" :value="p.key">{{ p.label }}</option>
              </select>
            </label>

            <label class="settings__field">
              <span class="settings__label">API Key</span>
              <input
                v-model="settings.apiKey"
                class="settings__input"
                type="password"
                placeholder="sk-..."
                autocomplete="off"
                @input="settings.save()"
              />
            </label>

            <label class="settings__field">
              <span class="settings__label">Base URL{{ settings.provider === 'custom' ? '（必填）' : '' }}</span>
              <input
                v-model="settings.baseUrl"
                class="settings__input"
                type="text"
                :placeholder="settings.preset.baseUrl || 'https://your-openai-compatible-endpoint/v1'"
                :disabled="settings.provider !== 'custom'"
                @input="settings.save()"
              />
            </label>

            <label class="settings__field">
              <span class="settings__label">模型名</span>
              <input
                v-model="settings.model"
                class="settings__input"
                type="text"
                :placeholder="settings.preset.model || 'model-name'"
                @input="settings.save()"
              />
            </label>

            <div class="settings__actions">
              <button
                class="settings__btn settings__btn--primary"
                :disabled="!settings.hasKey || verifying"
                @click="onVerify"
              >
                {{ verifying ? '验证中…' : '测试连接' }}
              </button>
              <button
                class="settings__btn"
                :disabled="!settings.hasKey"
                @click="onClear"
              >
                清除 Key
              </button>
            </div>

            <p
              v-if="verifyResult"
              class="settings__verify"
              :class="verifyResult.valid ? 'settings__verify--ok' : 'settings__verify--fail'"
            >
              {{ verifyResult.message }}
            </p>

            <div class="settings__help">
              <a
                v-if="settings.preset.keyHelpUrl"
                class="settings__help-cta"
                :href="settings.preset.keyHelpUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                <NeonIcon name="external" :size="16" />
                打开 {{ settings.preset.label }} 开放平台，免费创建 Key
              </a>
              <p class="settings__help-text">未配置 Key 时使用平台免费额度（30 次/日/IP），配置后不受限制。</p>
            </div>

            <p v-if="health" class="settings__status">
              服务状态：{{ health.status === 'up' ? '在线' : '异常' }} · 知识块 {{ health.chunks }} ·
              平台免费额度{{ health.platform_key_configured ? '已开放' : '未开放' }}
            </p>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import NeonIcon from '@/components/common/NeonIcon.vue';
import { PROVIDER_PRESETS, useSettingsStore } from '@/stores/settingsStore';
import { useThemeStore } from '@/stores/themeStore';
import { fetchHealth, verifyKey } from '@/api/client';
import { useAchievementStore } from '@/stores/achievementStore';

const props = defineProps<{ visible: boolean }>();
const emit = defineEmits<{ onClose: [] }>();

const settings = useSettingsStore();
const theme = useThemeStore();
const verifying = ref(false);
const verifyResult = ref<{ valid: boolean; message: string } | null>(null);
const health = ref<{ status: string; chunks: number; platform_key_configured: boolean } | null>(null);

watch(
  () => props.visible,
  async (v) => {
    if (v) {
      verifyResult.value = null;
      health.value = await fetchHealth();
      // 成就：打开设置
      useAchievementStore().unlock('open_settings');
    }
  },
);

function onProviderChange(key: string) {
  settings.setProvider(key);
  verifyResult.value = null;
}

async function onVerify() {
  verifying.value = true;
  verifyResult.value = null;
  verifyResult.value = await verifyKey({
    api_key: settings.apiKey,
    provider: settings.provider,
    base_url: settings.effectiveBaseUrl || undefined,
    model: settings.effectiveModel || undefined,
  });
  verifying.value = false;
  // 成就：API Key 验证通过
  if (verifyResult.value?.valid) useAchievementStore().unlock('api_key');
}

function onClear() {
  settings.clearKey();
  verifyResult.value = null;
}
</script>

<style scoped>
.settings-mask {
  position: fixed;
  inset: 0;
  background: var(--mask-light);
  z-index: 120;
  display: flex;
  justify-content: flex-end;
}

.settings {
  width: 380px;
  max-width: 92vw;
  height: 100%;
  background: var(--bg-panel);
  border-left: 1px solid var(--border-glow);
  display: flex;
  flex-direction: column;
}

.settings__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.settings__title {
  font-size: 16px;
  font-weight: 600;
}

.settings__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  clip-path: var(--clip-sm);
  color: var(--text-secondary);
}

.settings__close:hover {
  background: var(--bg-panel-2);
  color: var(--accent-bright);
}

.settings__body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.settings__hint {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  background: var(--bg-panel-2);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  padding: 10px 12px;
}

/* ---- Key 状态卡 ---- */
.settings__status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  clip-path: var(--clip-md);
  border: 1px solid var(--border-subtle);
  background: var(--bg-panel-2);
}

.settings__status-card--ok {
  border-color: var(--success-strong);
}

.settings__status-card--warn {
  border-color: var(--amber);
  background: linear-gradient(135deg, var(--amber-soft), var(--amber-deep-soft));
}

.settings__status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--amber);
  box-shadow: 0 0 8px var(--amber-glow);
  animation: status-pulse 1.8s infinite;
}

.settings__status-card--ok .settings__status-dot {
  background: var(--success);
  box-shadow: 0 0 8px var(--success-strong);
}

@keyframes status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.settings__status-title {
  font-size: 14px;
  font-weight: 600;
}

.settings__status-sub {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* ---- 三步指引 ---- */
.settings__steps {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border: 1px dashed var(--border-glow);
  clip-path: var(--clip-md);
  background: var(--accent-soft);
}

.settings__step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
}

.settings__step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--amber);
  color: var(--on-amber);
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-display);
  flex-shrink: 0;
}

.settings__field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.settings__label {
  font-size: 12px;
  color: var(--text-secondary);
}

.settings__input {
  width: 100%;
  min-height: 48px;
  padding: 12px 14px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  clip-path: var(--clip-sm);
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-mono);
  outline: none;
  transition: border-color 200ms;
}

.settings__input:focus {
  border-color: var(--accent-primary);
}

.settings__input:disabled {
  opacity: 0.55;
}

select.settings__input {
  font-family: var(--font-body);
}

/* zenless-ui 表单控件：铺满字段 */
.settings__zctrl {
  width: 100%;
}

.settings__zactions {
  margin-top: 0;
}

.settings__zbtn {
  flex: 1;
}

.settings__actions {
  display: flex;
  gap: 10px;
}

.settings__btn {
  flex: 1;
  min-height: 44px;
  clip-path: var(--clip-sm);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  transition: border-color 200ms, color 200ms;
}

.settings__btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-bright);
}

.settings__btn--primary {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #fff;
}

.settings__btn--primary:hover:not(:disabled) {
  background: var(--accent-bright);
  color: #fff;
}

.settings__btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.settings__verify {
  font-size: 12px;
  padding: 8px 12px;
  clip-path: var(--clip-sm);
}

.settings__verify--ok {
  color: var(--success);
  background: var(--success-soft);
  border: 1px solid var(--success-border);
}

.settings__verify--fail {
  color: var(--danger);
  background: var(--danger-soft);
  border: 1px solid var(--danger-border);
}

.settings__help {
  border-top: 1px solid var(--border-subtle);
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.settings__help-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 48px;
  clip-path: var(--clip-sm);
  background: var(--amber);
  color: var(--on-amber);
  font-size: 14px;
  font-weight: 600;
  transition: background 200ms, box-shadow 200ms;
}

.settings__help-cta:hover {
  background: var(--amber);
  box-shadow: 0 0 16px var(--amber-glow);
}

.settings__help-text {
  font-size: 12px;
  color: var(--text-muted);
}

.settings__status {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.settings-enter-active,
.settings-leave-active {
  transition: opacity 250ms;
}
.settings-enter-active .settings,
.settings-leave-active .settings {
  transition: transform 250ms ease-out;
}
.settings-enter-from,
.settings-leave-to {
  opacity: 0;
}
.settings-enter-from .settings,
.settings-leave-to .settings {
  transform: translateX(100%);
}
</style>
