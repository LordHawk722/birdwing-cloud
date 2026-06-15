<template>
  <div class="ai-chat-container">
    <!-- 自定义导航栏 -->
    <div class="custom-navbar">
      <div class="navbar-left" @click="goBack">
        <span class="back-icon">←</span>
      </div>
      <div class="navbar-center">
        <div class="ai-avatar-wrapper">
          <span class="ai-avatar">🦜</span>
          <div class="status-indicator" :class="{ 'status-online': isAIOnline, 'status-typing': isAITyping }"></div>
        </div>
        <div class="ai-info">
          <span class="ai-name">鸟类智能助手</span>
          <span class="ai-status">{{ getAIStatus() }}</span>
        </div>
      </div>
      <div class="navbar-right">
        <div class="menu-btn" @click="showMenu">
          <span class="menu-icon">⋯</span>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <!-- 欢迎消息 -->
      <div v-if="messageList.length === 0" class="welcome-section">
        <div class="welcome-card">
          <span class="welcome-icon">🦜</span>
          <span class="welcome-title">欢迎来到鸟类智能助手！</span>
          <span class="welcome-subtitle">我可以帮助您解答关于鸟类的任何问题</span>
          <div class="suggestion-buttons">
            <div v-for="s in quickSuggestions" :key="s.id" class="suggestion-btn" @click="sendSuggestion(s)">
              <span class="suggestion-icon">{{ s.emoji }}</span>
              <span class="suggestion-text">{{ s.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息项 -->
      <div v-for="(message, index) in messageList" :key="message.id" class="message-item" :class="{ 'message-user': message.type === 'user', 'message-ai': message.type === 'ai' }">
        <!-- AI消息 -->
        <div v-if="message.type === 'ai'" class="ai-message-wrapper">
          <span class="message-avatar">🦜</span>
          <div class="message-content">
            <div class="message-bubble ai-bubble">
              <div v-if="message.isTyping" class="typing-indicator">
                <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
              </div>
              <div v-else class="message-text" v-html="formatMessageContent(message.content)"></div>
              <div v-if="!message.isTyping" class="message-toolbar">
                <span class="toolbar-btn" @click="copyMessage(message)" title="复制">📋</span>
                <span class="toolbar-btn" @click="likeMessage(message)" title="点赞">{{ message.isLiked ? '❤️' : '🤍' }}</span>
              </div>
            </div>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="user-message-wrapper">
          <div class="message-content">
            <div class="message-bubble user-bubble">
              <span class="message-text">{{ message.content }}</span>
            </div>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
          <span class="message-avatar">👤</span>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-section">
      <div v-if="quickReplies.length > 0" class="quick-replies">
        <div class="quick-reply-scroll">
          <span v-for="reply in quickReplies" :key="reply.id" class="quick-reply-item" @click="sendQuickReply(reply)">{{ reply.text }}</span>
        </div>
      </div>
      <div class="input-wrapper">
        <div class="input-container">
          <div class="extra-actions">
            <span class="action-btn" @click="selectImage" title="上传图片">🖼</span>
          </div>
          <input
            v-model="inputText"
            placeholder="输入您想了解的鸟类问题..."
            class="text-input"
            maxlength="500"
            @keyup.enter="sendMessage"
          />
          <div class="send-btn" :class="{ 'send-btn-active': canSend }" @click="sendMessage">
            <span class="send-icon">↑</span>
          </div>
        </div>
        <div v-if="inputText.length > 0" class="char-count">
          <span class="char-count-text">{{ inputText.length }}/500</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showActionSheet, showModal } from '@/utils/toast.js'
import { chooseImages, vibrate } from '@/utils/helpers.js'
import RecognitionService from '@/api/services/recognition.js'

const router = useRouter()
const inputText = ref('')
const messageList = ref([])
const isAIOnline = ref(true)
const isAITyping = ref(false)
const isInputFocused = ref(false)
const quickReplies = ref([])
const messageListRef = ref(null)

const quickSuggestions = ref([
  { id: 1, text: '鸟类识别', emoji: '🔍' },
  { id: 2, text: '鸟类习性', emoji: '🐦' },
  { id: 3, text: '观鸟指南', emoji: '📖' },
  { id: 4, text: '保护知识', emoji: '🛡' }
])

const canSend = computed(() => inputText.value.trim().length > 0 && !isAITyping.value)

const goBack = () => router.back()
const getAIStatus = () => {
  if (isAITyping.value) return '正在输入...'
  return isAIOnline.value ? '在线' : '离线'
}

const showMenu = () => {
  showActionSheet(['清空聊天记录', '导出聊天记录', '设置']).then(index => {
    if (index === 0) clearChatHistory()
    else if (index === 1) showToast('导出功能开发中', 'none')
    else if (index === 2) showToast('设置功能开发中', 'none')
  })
}

const sendMessage = async () => {
  if (!canSend.value) return
  const userMessage = { id: Date.now(), type: 'user', content: inputText.value.trim(), timestamp: new Date() }
  messageList.value.push(userMessage)
  const currentInput = inputText.value.trim()
  inputText.value = ''
  await nextTick()
  scrollToBottom()
  await sendToAI(currentInput)
}

const sendSuggestion = (suggestion) => {
  inputText.value = suggestion.text
  sendMessage()
}

const sendQuickReply = (reply) => {
  inputText.value = reply.text
  sendMessage()
}

const selectImage = async () => {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.tempFilePaths.length > 0 && result.files.length > 0) {
      handleImageRecognition(result.tempFilePaths[0], result.files[0])
    }
  } catch (error) {
    showToast('选择图片失败', 'error')
  }
}

const copyMessage = async (message) => {
  try {
    await navigator.clipboard.writeText(message.content)
    showToast('已复制', 'success')
  } catch { showToast('复制失败', 'error') }
}

const likeMessage = (message) => {
  message.isLiked = !message.isLiked
  vibrate('short')
}

const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const formatMessageContent = (content) => {
  return content.replace(/\n/g, '<br/>')
}

const formatTime = (timestamp) => {
  const now = new Date()
  const date = new Date(timestamp)
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

const sendToAI = async (message) => {
  try {
    const aiMessage = { id: Date.now() + 1, type: 'ai', content: '', timestamp: new Date(), isTyping: true }
    messageList.value.push(aiMessage)
    isAITyping.value = true
    await nextTick(); scrollToBottom()
    await new Promise(resolve => setTimeout(resolve, 1500))
    const response = generateAIResponse(message)
    const idx = messageList.value.findIndex(m => m.id === aiMessage.id)
    if (idx !== -1) {
      messageList.value[idx].content = response
      messageList.value[idx].isTyping = false
      isAITyping.value = false
    }
    generateQuickReplies(response)
    await nextTick(); scrollToBottom()
  } catch (error) {
    isAITyping.value = false
    showToast('AI响应失败，请重试', 'error')
  }
}

const generateAIResponse = (msg) => {
  const responses = {
    '鸟类识别': '我可以帮您识别鸟类！请描述一下鸟的特征，比如大小、颜色、叫声等，或者您可以上传照片让我来识别。',
    '鸟类习性': '不同鸟类有着各自独特的习性。您想了解哪种鸟类的习性呢？比如觅食习惯、繁殖行为、迁徙路线等。',
    '观鸟指南': '观鸟是一项很有趣的活动！建议选择清晨或傍晚时间，准备好双筒望远镜，选择公园、湿地等鸟类活动频繁的地方。保持安静，避免惊扰鸟类。',
    '保护知识': '鸟类保护非常重要。我们可以通过保护栖息地、减少污染、不干扰繁殖等方式来保护鸟类。您想了解具体哪个方面的保护知识呢？'
  }
  for (const [keyword, response] of Object.entries(responses)) {
    if (msg.includes(keyword)) return response
  }
  return '这是一个很好的问题！作为鸟类专家，我很乐意为您解答。您能提供更多具体信息吗？这样我可以给出更准确的回答。'
}

const generateQuickReplies = (aiResponse) => {
  const defaults = [{ id: 1, text: '告诉我更多' }, { id: 2, text: '有相关图片吗？' }, { id: 3, text: '谢谢' }]
  if (aiResponse.includes('识别')) {
    quickReplies.value = [{ id: 1, text: '上传照片识别' }, { id: 2, text: '描述特征识别' }, { id: 3, text: '常见鸟类有哪些？' }]
  } else if (aiResponse.includes('保护')) {
    quickReplies.value = [{ id: 1, text: '如何参与保护？' }, { id: 2, text: '濒危鸟类有哪些？' }, { id: 3, text: '保护法律法规' }]
  } else {
    quickReplies.value = defaults
  }
  setTimeout(() => { quickReplies.value = [] }, 5000)
}

const handleImageRecognition = async (imagePath, file) => {
  try {
    showToast('识别中...', 'loading')
    const res = await RecognitionService.analyzeWithImage(file)
    const data = res.data?.data
    if (data?.results?.length) {
      const topResult = data.results[0]
      const resultLines = data.results.map((r, i) =>
        `${i + 1}. ${r.name}（置信度 ${Math.round(r.confidence * 100)}%）`
      ).join('<br/>')
      const result = `根据图片分析，最可能是 <b>${topResult.name}</b>，置信度 ${Math.round(topResult.confidence * 100)}%。<br/><br/>完整识别结果：<br/>${resultLines}`
      messageList.value.push({ id: Date.now(), type: 'ai', content: `图片识别结果：<br/><br/>${result}`, timestamp: new Date(), isTyping: false })
    } else {
      messageList.value.push({ id: Date.now(), type: 'ai', content: '未能识别出图片中的鸟类，请尝试更清晰的照片。', timestamp: new Date(), isTyping: false })
    }
    await nextTick(); scrollToBottom()
  } catch (error) {
    const msg = error?.statusCode === 401 ? '请先登录后再使用识别功能' : '识别失败，请重试'
    showToast(msg, 'error')
  }
}

const clearChatHistory = async () => {
  const confirmed = await showModal('确认清空', '确定要清空所有聊天记录吗？')
  if (confirmed) {
    messageList.value = []
    showToast('已清空', 'success')
  }
}

watch(messageList, () => { nextTick(() => scrollToBottom()) }, { deep: true })

onMounted(() => { isAIOnline.value = true })
</script>

<style scoped>
.ai-chat-container { height: 100vh; display: flex; flex-direction: column; background: linear-gradient(180deg, #f8fffe, #ffffff); }
.custom-navbar { height: 44px; background: linear-gradient(135deg, #9c27b0, #ab47bc); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; box-shadow: 0 1px 8px rgba(156,39,176,0.2); }
.navbar-left, .navbar-right { width: 40px; height: 30px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.back-icon { font-size: 18px; color: white; }
.navbar-center { flex: 1; display: flex; align-items: center; gap: 8px; }
.ai-avatar-wrapper { position: relative; }
.ai-avatar { font-size: 24px; }
.status-indicator { position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; border-radius: 50%; border: 2px solid white; background: #666; }
.status-online { background: #4caf50; }
.status-typing { background: #ff9800; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.3); } }
.ai-name { font-size: 14px; font-weight: 600; color: white; display: block; }
.ai-status { font-size: 10px; color: rgba(255,255,255,0.8); display: block; }
.menu-icon { font-size: 18px; color: white; }

.message-list { flex: 1; padding: 12px 16px; overflow-y: auto; }
.welcome-section { display: flex; justify-content: center; padding: 40px 0; }
.welcome-card { background: white; border-radius: 16px; padding: 24px 16px; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.08); max-width: 320px; }
.welcome-icon { font-size: 60px; display: block; margin-bottom: 12px; }
.welcome-title { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 6px; display: block; }
.welcome-subtitle { font-size: 13px; color: #666; margin-bottom: 16px; display: block; }
.suggestion-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.suggestion-btn { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px 8px; background: linear-gradient(135deg, #f3e5f5, #fce4ec); border-radius: 10px; border: 1px solid rgba(156,39,176,0.1); cursor: pointer; transition: all 0.2s ease; }
.suggestion-btn:hover { transform: translateY(-1px); background: linear-gradient(135deg, #e1bee7, #f8bbd9); }
.suggestion-icon { font-size: 16px; }
.suggestion-text { font-size: 11px; color: #9c27b0; font-weight: 500; }

.message-item { margin-bottom: 16px; animation: fadeInUp 0.3s ease; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.ai-message-wrapper { display: flex; align-items: flex-start; gap: 8px; }
.user-message-wrapper { display: flex; align-items: flex-start; gap: 8px; flex-direction: row-reverse; }
.message-avatar { font-size: 24px; flex-shrink: 0; }
.message-content { flex: 1; max-width: calc(100% - 40px); }
.message-bubble { padding: 10px 12px; border-radius: 12px; margin-bottom: 4px; word-wrap: break-word; }
.ai-bubble { background: white; border: 1px solid rgba(156,39,176,0.1); border-bottom-left-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.user-bubble { background: linear-gradient(135deg, #9c27b0, #ab47bc); color: white; border-bottom-right-radius: 4px; }
.message-text { font-size: 14px; line-height: 1.6; color: #333; }
.user-bubble .message-text { color: white; }
.message-time { font-size: 10px; color: #999; margin-left: 12px; }
.user-message-wrapper .message-time { text-align: right; margin-left: 0; margin-right: 12px; display: block; }

.typing-indicator { display: flex; align-items: center; gap: 4px; padding: 4px 0; }
.typing-dot { width: 8px; height: 8px; background: #9c27b0; border-radius: 50%; animation: typingDot 1.4s infinite; }
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes typingDot { 0%,80%,100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }

.message-toolbar { display: flex; gap: 4px; margin-top: 6px; opacity: 0.5; transition: opacity 0.2s; }
.ai-bubble:hover .message-toolbar { opacity: 1; }
.toolbar-btn { cursor: pointer; font-size: 12px; padding: 2px 4px; border-radius: 4px; }
.toolbar-btn:hover { background: rgba(156,39,176,0.1); }

.quick-replies { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.quick-reply-scroll { display: flex; gap: 6px; padding: 0 16px; overflow-x: auto; white-space: nowrap; }
.quick-reply-item { display: inline-block; padding: 6px 10px; background: rgba(156,39,176,0.1); border: 1px solid rgba(156,39,176,0.2); border-radius: 10px; font-size: 12px; color: #9c27b0; cursor: pointer; transition: all 0.2s; }
.quick-reply-item:hover { background: rgba(156,39,176,0.2); }

.input-section { background: white; border-top: 1px solid #f0f0f0; padding: 8px 16px; padding-bottom: env(safe-area-inset-bottom); }
.input-container { display: flex; align-items: center; gap: 8px; background: #f8f9fa; border-radius: 14px; padding: 6px 8px; border: 1px solid transparent; transition: all 0.3s ease; }
.input-container:focus-within { border-color: #9c27b0; background: white; box-shadow: 0 0 0 4px rgba(156,39,176,0.1); }
.extra-actions { display: flex; gap: 4px; }
.action-btn { width: 28px; height: 28px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 14px; cursor: pointer; transition: all 0.2s; }
.action-btn:hover { background: rgba(156,39,176,0.1); }
.text-input { flex: 1; min-height: 28px; font-size: 14px; color: #333; border: none; outline: none; background: transparent; padding: 4px 6px; }
.send-btn { width: 28px; height: 28px; background: rgba(156,39,176,0.3); border-radius: 14px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; }
.send-btn-active { background: linear-gradient(135deg, #9c27b0, #ab47bc); box-shadow: 0 2px 8px rgba(156,39,176,0.3); }
.send-btn-active:active { transform: scale(0.9); }
.send-icon { font-size: 14px; color: white; font-weight: bold; }
.char-count { text-align: right; margin-top: 4px; }
.char-count-text { font-size: 10px; color: #999; }
</style>
