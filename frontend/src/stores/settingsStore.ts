// settingsStore：BYOK 设置。Key 仅存浏览器 localStorage（FR-BY-02），不上传、不落服务端日志。
import { defineStore } from 'pinia';

const LS_KEY = 'xkz_settings_v1';

export interface ProviderPreset {
  key: string;
  label: string;
  baseUrl: string;
  model: string;
  keyHelpUrl: string;
}

// 与后端 config.PROVIDERS 保持一致的服务商预设（FR-BY-01 / FR-BY-MODEL-04）
export const PROVIDER_PRESETS: ProviderPreset[] = [
  {
    key: 'deepseek',
    label: 'DeepSeek-V4（默认）',
    baseUrl: 'https://api.deepseek.com/v1',
    model: 'deepseek-v4-flash',
    keyHelpUrl: 'https://platform.deepseek.com/api_keys',
  },
  {
    key: 'qwen',
    label: '通义千问 Qwen',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model: 'qwen-plus',
    keyHelpUrl: 'https://bailian.console.aliyun.com/#/api-key',
  },
  {
    key: 'kimi',
    label: 'Kimi（Moonshot）',
    baseUrl: 'https://api.moonshot.cn/v1',
    model: 'moonshot-v1-8k',
    keyHelpUrl: 'https://platform.moonshot.cn/console/api-keys',
  },
  {
    key: 'zhipu',
    label: '智谱 GLM',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    model: 'glm-4-flash',
    keyHelpUrl: 'https://open.bigmodel.cn/usercenter/apikeys',
  },
  {
    key: 'custom',
    label: '自定义（OpenAI 兼容）',
    baseUrl: '',
    model: '',
    keyHelpUrl: '',
  },
];

interface SettingsState {
  provider: string;
  apiKey: string;
  baseUrl: string;
  model: string;
}

function loadFromLocal(): SettingsState {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        provider: parsed.provider ?? 'deepseek',
        apiKey: parsed.apiKey ?? '',
        baseUrl: parsed.baseUrl ?? '',
        model: parsed.model ?? '',
      };
    }
  } catch {
    /* localStorage 不可用时忽略 */
  }
  // FR-BY-MODEL-03：首次打开预选 DeepSeek-V4
  return { provider: 'deepseek', apiKey: '', baseUrl: '', model: '' };
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => loadFromLocal(),
  getters: {
    hasKey: (s) => s.apiKey.trim().length > 0,
    preset: (s) => PROVIDER_PRESETS.find((p) => p.key === s.provider) ?? PROVIDER_PRESETS[0],
    effectiveBaseUrl(): string {
      const s = this as unknown as SettingsState & { preset: ProviderPreset };
      return s.provider === 'custom' ? s.baseUrl : s.preset.baseUrl;
    },
    effectiveModel(): string {
      const s = this as unknown as SettingsState & { preset: ProviderPreset };
      return s.model || s.preset.model;
    },
  },
  actions: {
    save() {
      localStorage.setItem(
        LS_KEY,
        JSON.stringify({
          provider: this.provider,
          apiKey: this.apiKey,
          baseUrl: this.baseUrl,
          model: this.model,
        }),
      );
    },
    clearKey() {
      this.apiKey = '';
      this.save();
    },
    setProvider(key: string) {
      this.provider = key;
      // FR-BY-MODEL-04：切换服务商时自动填充对应 BaseURL 示例
      const preset = PROVIDER_PRESETS.find((p) => p.key === key);
      if (preset && key !== 'custom') {
        this.baseUrl = preset.baseUrl;
        this.model = preset.model;
      }
      this.save();
    },
  },
});
