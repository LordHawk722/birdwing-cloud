/**
 * AI配置文件 - Web版本
 * 统一管理AI相关的配置
 */

const AI_PROVIDERS = {
  openai: {
    BASE_URL: 'https://api.openai.com/v1',
    MODEL_NAME: 'gpt-4o-mini',
    API_KEY: import.meta.env.VITE_OPENAI_API_KEY || ''
  },
  claude: {
    BASE_URL: 'https://api.anthropic.com/v1',
    MODEL_NAME: 'claude-3-sonnet-20240229',
    API_KEY: import.meta.env.VITE_ANTHROPIC_API_KEY || ''
  },
  custom: {
    BASE_URL: import.meta.env.VITE_CUSTOM_AI_BASE_URL || 'http://localhost:8000/v1',
    MODEL_NAME: import.meta.env.VITE_CUSTOM_AI_MODEL || 'llama-3-8b-instruct',
    API_KEY: import.meta.env.VITE_CUSTOM_AI_API_KEY || ''
  }
}

const CURRENT_PROVIDER = import.meta.env.VITE_AI_PROVIDER || 'custom'

export const AI_CONFIG = {
  ...AI_PROVIDERS[CURRENT_PROVIDER],

  MODEL_CONFIG: {
    TEMPERATURE: 0.7,
    MAX_TOKENS: 2048,
    TOP_P: 0.9,
    FREQUENCY_PENALTY: 0.1,
    PRESENCE_PENALTY: 0.1
  },

  SYSTEM_PROMPT: `你是一个专业的鸟类专家和观鸟向导，名叫"小羽"。你的任务是帮助用户识别鸟类、了解鸟类知识、学习观鸟技巧。

你的特点：
1. 拥有丰富的鸟类学知识，熟悉全球各地的鸟类种类
2. 善于用简单易懂的语言解释复杂的鸟类行为和生态知识
3. 热情友好，对用户的每个问题都耐心回答
4. 能够根据用户描述的特征准确识别鸟类
5. 擅长给出实用的观鸟建议和保护意见

回答要求：
- 回答要准确、详细但不冗长
- 使用温和友好的语气
- 适当加入有趣的鸟类小知识
- 如果不确定，请诚实说明并提供可能的选项
- 鼓励用户保护鸟类和环境`,

  REQUEST_CONFIG: {
    REQUEST_TIMEOUT: 30000,
    STREAM_TIMEOUT: 60000,
    VISION_TIMEOUT: 45000,
    SPEECH_TIMEOUT: 30000,
    RETRY_COUNT: 3,
    RETRY_DELAY: 1000
  },

  VISION_CONFIG: {
    SUPPORTED_FORMATS: ['jpg', 'jpeg', 'png', 'webp'],
    MAX_IMAGE_SIZE: 20,
    COMPRESSION_QUALITY: 0.8,
    MAX_RESOLUTION: 2048,
    CONFIDENCE_THRESHOLD: 0.7
  },

  CONVERSATION_CONFIG: {
    MAX_CONTEXT_LENGTH: 20,
    SESSION_TIMEOUT: 30,
    MESSAGE_HISTORY_DAYS: 30,
    ENABLE_CONTEXT_COMPRESSION: true,
    COMPRESSION_THRESHOLD: 15
  },

  SAFETY_CONFIG: {
    CONTENT_FILTER_LEVEL: 'medium',
    ENABLE_SENSITIVE_WORD_DETECTION: true,
    SENSITIVE_WORD_ACTION: 'warn',
    MAX_INPUT_LENGTH: 2000,
    RATE_LIMIT_INTERVAL: 1
  },

  FEATURE_FLAGS: {
    ENABLE_STREAMING: true,
    ENABLE_VISION: true,
    ENABLE_SPEECH: true,
    ENABLE_MULTIMODAL: true,
    ENABLE_CONTEXT_LEARNING: true,
    ENABLE_QUICK_REPLY: true,
    ENABLE_SENTIMENT_ANALYSIS: false,
    ENABLE_CONVERSATION_SUMMARY: true
  }
}

export const QUICK_REPLY_TEMPLATES = {
  GREETING: [
    '你好！我想了解鸟类知识',
    '帮我识别一下这只鸟',
    '推荐一些观鸟地点',
    '教我观鸟的基础知识'
  ],
  IDENTIFICATION: [
    '告诉我更多细节',
    '这种鸟有什么特别之处？',
    '它们通常在哪里出现？',
    '有相似的鸟类吗？'
  ],
  FOLLOW_UP: [
    '非常有用，谢谢！',
    '我想了解更多',
    '有相关的图片吗？',
    '还有其他问题'
  ]
}

export function detectAICapabilities() {
  return {
    textGeneration: true,
    imageAnalysis: AI_CONFIG.FEATURE_FLAGS.ENABLE_VISION,
    speechToText: AI_CONFIG.FEATURE_FLAGS.ENABLE_SPEECH,
    textToSpeech: AI_CONFIG.FEATURE_FLAGS.ENABLE_SPEECH,
    streaming: AI_CONFIG.FEATURE_FLAGS.ENABLE_STREAMING,
    multimodal: AI_CONFIG.FEATURE_FLAGS.ENABLE_MULTIMODAL
  }
}

export function getModelConfig(overrides = {}) {
  return { ...AI_CONFIG.MODEL_CONFIG, ...overrides }
}

export function getSystemPrompt(customPrompt = '') {
  return customPrompt || AI_CONFIG.SYSTEM_PROMPT
}

export function validateAIConfig() {
  const errors = []
  if (!AI_CONFIG.API_KEY) errors.push('AI API密钥未配置')
  if (!AI_CONFIG.BASE_URL) errors.push('AI服务地址未配置')
  if (!AI_CONFIG.MODEL_NAME) errors.push('AI模型名称未配置')
  return errors.length === 0
}

export function getProviderConfig(provider = CURRENT_PROVIDER) {
  return AI_PROVIDERS[provider] || AI_PROVIDERS.openai
}

export function switchAIProvider(provider) {
  if (!AI_PROVIDERS[provider]) {
    throw new Error(`不支持的AI提供商: ${provider}`)
  }
  Object.assign(AI_CONFIG, AI_PROVIDERS[provider])
  return AI_CONFIG
}

export default AI_CONFIG
