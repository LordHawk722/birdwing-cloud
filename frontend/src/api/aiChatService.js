/**
 * @deprecated AI 聊天当前由 AIChat.vue 页面本地处理（模拟响应）。
 * 后端暂无 /chat 端点。图片识别请使用 api/services/recognition.js。
 * 此文件保留为未来 AI 集成的占位符。
 */
import RecognitionService from './services/recognition.js'

class AIChatService {
  constructor() {
    this.conversationContext = []
    this.maxContextLength = 10
    this.sessionId = null
  }

  /** @deprecated 使用 RecognitionService.analyzeWithImage() 代替 */
  async analyzeImageWithAI(file, question) {
    return RecognitionService.analyzeWithImage(file)
  }

  /** 以下方法后端暂未实现，保留供将来使用 */
  async initChatSession() { throw new Error('AI chat not yet available — backend has no chat endpoint') }
  async sendMessage() { throw new Error('AI chat not yet available') }
  async getQuickReplySuggestions() { throw new Error('AI chat not yet available') }
  async getChatHistory() { throw new Error('AI chat not yet available') }
  async clearChatHistory() { throw new Error('AI chat not yet available') }
  resetSession() { this.conversationContext = []; this.sessionId = null }
  setSystemPrompt() {}
  getSessionStatus() { return null }
}

export default new AIChatService()
