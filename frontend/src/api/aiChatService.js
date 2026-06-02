/**
 * AI聊天服务 - Web版本
 */
import { request } from '@/utils/request.js'
import { AI_CONFIG } from '@/config/ai.js'

class AIChatService {
  constructor() {
    this.conversationContext = []
    this.maxContextLength = 10
    this.sessionId = null
  }

  async initChatSession() {
    try {
      const response = await request.post(`${AI_CONFIG.BASE_URL}/chat/session/init`, {
        model: AI_CONFIG.MODEL_NAME,
        system_prompt: AI_CONFIG.SYSTEM_PROMPT,
        temperature: AI_CONFIG.MODEL_CONFIG.TEMPERATURE,
        max_tokens: AI_CONFIG.MODEL_CONFIG.MAX_TOKENS
      })
      this.sessionId = response.data.session_id
      return { code: 200, data: response.data, message: '会话初始化成功' }
    } catch (error) {
      console.error('初始化聊天会话失败:', error)
      throw new Error('初始化聊天会话失败')
    }
  }

  async sendMessage(message, options = {}) {
    try {
      if (!message || message.trim() === '') throw new Error('消息内容不能为空')
      if (!this.sessionId) await this.initChatSession()
      const { context = [] } = options
      const response = await request.post(`${AI_CONFIG.BASE_URL}/chat/completions`, {
        session_id: this.sessionId,
        message: message.trim(),
        context: [...this.conversationContext, ...context],
        model_config: {
          temperature: AI_CONFIG.MODEL_CONFIG.TEMPERATURE,
          max_tokens: AI_CONFIG.MODEL_CONFIG.MAX_TOKENS
        }
      })
      this.updateConversationContext(message, response.data.reply)
      return { code: 200, data: response.data, message: '发送成功' }
    } catch (error) {
      console.error('发送消息失败:', error)
      throw new Error('发送消息失败，请重试')
    }
  }

  async analyzeImageWithAI(imageFile, question = '请识别这张图片中的鸟类并介绍相关信息') {
    try {
      if (!imageFile) throw new Error('图片文件不能为空')
      if (!this.sessionId) await this.initChatSession()
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('session_id', this.sessionId)
      formData.append('question', question)
      formData.append('analysis_type', 'bird_identification')
      const response = await request.post(`${AI_CONFIG.BASE_URL}/vision/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: AI_CONFIG.REQUEST_CONFIG.VISION_TIMEOUT
      })
      this.updateConversationContext(`[图片分析] ${question}`, response.data.analysis)
      return { code: 200, data: response.data, message: '图片分析成功' }
    } catch (error) {
      console.error('图片分析失败:', error)
      throw new Error('图片分析失败，请重试')
    }
  }

  async getQuickReplySuggestions(lastMessage) {
    try {
      if (!lastMessage) return []
      const response = await request.post(`${AI_CONFIG.BASE_URL}/suggestions/quick-replies`, {
        last_message: lastMessage,
        context: this.conversationContext.slice(-3)
      })
      return response.data.suggestions || []
    } catch (error) {
      console.error('获取快速回复建议失败:', error)
      return []
    }
  }

  async getChatHistory(params = {}) {
    try {
      const { page = 1, size = 50 } = params
      if (!this.sessionId) return { code: 200, data: { messages: [], total: 0 }, message: '暂无聊天记录' }
      const response = await request.get(`${AI_CONFIG.BASE_URL}/chat/history`, {
        params: { session_id: this.sessionId, page, size }
      })
      return { code: 200, data: response.data, message: '获取成功' }
    } catch (error) {
      console.error('获取聊天历史失败:', error)
      throw new Error('获取聊天历史失败')
    }
  }

  async clearChatHistory() {
    try {
      if (this.sessionId) {
        await request.delete(`${AI_CONFIG.BASE_URL}/chat/history/clear`, {
          data: { session_id: this.sessionId }
        })
      }
      this.conversationContext = []
      return { code: 200, message: '聊天记录已清空' }
    } catch (error) {
      console.error('清除聊天历史失败:', error)
      throw new Error('清除聊天历史失败')
    }
  }

  updateConversationContext(userMessage, aiReply) {
    this.conversationContext.push(
      { role: 'user', content: userMessage },
      { role: 'assistant', content: aiReply }
    )
    if (this.conversationContext.length > this.maxContextLength * 2) {
      this.conversationContext = this.conversationContext.slice(-this.maxContextLength * 2)
    }
  }

  getSessionStatus() {
    return {
      sessionId: this.sessionId,
      contextLength: this.conversationContext.length,
      isActive: !!this.sessionId,
      lastActivity: new Date().toISOString()
    }
  }

  resetSession() {
    this.sessionId = null
    this.conversationContext = []
  }

  setSystemPrompt(systemPrompt) {
    AI_CONFIG.SYSTEM_PROMPT = systemPrompt
  }
}

export default new AIChatService()
