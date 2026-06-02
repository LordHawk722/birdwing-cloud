<template>
  <div class="encyclopedia-container">
    <!-- 导航栏 -->
    <div class="custom-navbar">
      <div class="navbar-left" @click="goBack">
        <span class="back-icon">←</span>
      </div>
      <span class="navbar-title">鸟类图鉴</span>
      <div class="navbar-right">
        <div class="mode-switch" :class="{ 'mode-switch-active': currentMode === 'general' }" @click="toggleMode">
          <span class="mode-icon">{{ currentMode === 'search' ? '📖' : '🔍' }}</span>
        </div>
      </div>
    </div>

    <!-- 搜索模式 -->
    <div v-if="currentMode === 'search'" class="search-mode">
      <div class="search-section">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input type="text" placeholder="搜索鸟类名称或特征..." v-model="searchKeyword" @input="onSearchInput" @keyup.enter="handleSearchConfirm" class="search-input" />
          <div v-if="searchKeyword" class="clear-btn" @click="clearSearch">
            <span class="clear-icon">×</span>
          </div>
        </div>
      </div>

      <div class="search-results">
        <div v-if="isSearching" class="loading-container">
          <div class="loading-spinner"></div>
          <span class="loading-text">搜索中...</span>
        </div>

        <div v-else-if="searchResults.length > 0" class="results-grid">
          <div v-for="(bird, index) in searchResults" :key="bird.id" class="result-card" @click="selectBird(bird)" :style="{ animationDelay: `${index * 0.1}s` }">
            <img :src="getOSSUrl(bird.imageUrl, 'medium')" class="result-image" alt="鸟类图片" />
            <div class="result-content">
              <span class="result-name">{{ bird.name }}</span>
              <span class="result-scientific">{{ bird.scientificName }}</span>
              <div class="result-tags">
                <span v-for="tag in bird.tags" :key="tag" class="result-tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="searchKeyword && !isSearching" class="no-results">
          <span class="no-results-icon">🔍</span>
          <span class="no-results-text">未找到相关鸟类</span>
          <span class="no-results-subtitle">尝试搜索其他关键词</span>
        </div>

        <div v-else class="search-placeholder">
          <span class="placeholder-icon">📚</span>
          <span class="placeholder-text">输入鸟类名称开始搜索</span>
          <span class="placeholder-subtitle">支持中文名、英文名或特征描述</span>
        </div>
      </div>
    </div>

    <!-- 通识模式 - 卡片翻阅 -->
    <div v-else class="general-mode">
      <div class="progress-indicator">
        <span class="progress-text">{{ currentDisplayPage }} / {{ safeTotalCards }}</span>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${safeTotalCards > 0 ? (currentDisplayPage / safeTotalCards) * 100 : 0}%` }"></div>
        </div>
      </div>

      <div class="card-stack-container" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd">
        <div class="card-stack">
          <div v-if="safeCurrentIndex < safeTotalCards - 1 && safeTotalCards > 1" class="card-item background-card" :style="backgroundCardStyle">
            <BirdKnowledgeCard :bird-data="birdCards[safeCurrentIndex + 1]" :is-active="false" @like="onCardLike" @share="onCardShare" />
          </div>
          <div v-if="safeTotalCards > 0 && birdCards[safeCurrentIndex]" class="card-item current-card" :style="currentCardStyle" :class="{ 'card-flipping': isFlipping }">
            <BirdKnowledgeCard :bird-data="birdCards[safeCurrentIndex]" :is-active="true" @like="onCardLike" @share="onCardShare" />
          </div>
        </div>
      </div>

      <div class="bottom-actions">
        <div class="action-button prev-btn" :class="{ 'btn-disabled': !canGoPrevious }" @click="previousCard">
          <span>←</span><span class="action-text">上一张</span>
        </div>
        <div class="card-counter">
          <span class="counter-text">{{ currentDisplayPage }}</span>
          <span class="counter-divider">/</span>
          <span class="counter-total">{{ safeTotalCards }}</span>
        </div>
        <div class="action-button next-btn" :class="{ 'btn-disabled': !canGoNext }" @click="nextCard">
          <span class="action-text">下一张</span><span>→</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import BirdKnowledgeCard from '@/components/BirdKnowledgeCard.vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'
import { vibrate } from '@/utils/helpers.js'

const router = useRouter()
const currentMode = ref('search')
const searchKeyword = ref('')
const isSearching = ref(false)
const searchResults = ref([])
const currentCardIndex = ref(0)
const birdCards = ref([])

const isFlipping = ref(false)
const touchStartY = ref(0)
const touchCurrentY = ref(0)
const cardTranslateY = ref(0)
const cardOpacity = ref(1)
const cardScale = ref(1)
const backgroundCardScale = ref(0.95)
const backgroundCardOpacity = ref(0.7)

const mockBirdData = [
  { id: 1, name: '巨嘴鸟', scientificName: 'Ramphastos sulfuratus', imageUrl: 'static/birds/toucan.jpg', tags: ['热带鸟类', '彩色', '大型'], habitat: '热带雨林', size: '体长50-65cm', weight: '500-860克', wingspan: '109-152cm', diet: '主要以果实为食，偶尔捕食小型动物', behavior: '群居性鸟类，善于飞行和攀爬', distribution: '中美洲和南美洲的热带雨林', conservationStatus: '无危', characteristics: ['拥有巨大而彩色的喙', '羽毛色彩鲜艳', '飞行能力强', '社交性强'], funFacts: ['巨嘴鸟的大喙实际上很轻，内部充满了气囊', '它们的喙可以占到身体长度的1/3', '巨嘴鸟睡觉时会将喙折叠到背上'], callDescription: '发出低沉的咕咕声和尖锐的叫声', lifespan: '野外约15-20年' },
  { id: 2, name: '蜂鸟', scientificName: 'Trochilidae', imageUrl: 'static/birds/hummingbird.jpg', tags: ['小型鸟类', '快速', '悬停'], habitat: '花园、森林边缘', size: '体长5-25cm', weight: '2-20克', wingspan: '5-25cm', diet: '花蜜、小昆虫', behavior: '能够悬停飞行，翅膀拍打频率极高', distribution: '南北美洲', conservationStatus: '大多数种类稳定', characteristics: ['世界上最小的鸟类', '能够悬停和倒飞', '心跳频率极快', '新陈代谢旺盛'], funFacts: ['蜂鸟的翅膀每秒可拍打80次', '它们的心跳每分钟可达1260次', '蜂鸟可以倒着飞行'], callDescription: '发出细小的吱吱声', lifespan: '野外约3-5年' },
  { id: 3, name: '孔雀', scientificName: 'Pavo cristatus', imageUrl: 'static/birds/peacock.jpg', tags: ['大型鸟类', '华丽', '地栖'], habitat: '森林、公园、农田', size: '体长100-115cm', weight: '4-6公斤', wingspan: '120-160cm', diet: '种子、昆虫、小型爬行动物', behavior: '雄鸟会展开尾羽进行求偶炫耀', distribution: '南亚、东南亚', conservationStatus: '无危', characteristics: ['雄鸟有华丽的尾羽', '能够短距离飞行', '叫声洪亮', '具有强烈的领域性'], funFacts: ['孔雀的尾羽可以长达1.5米', '尾羽上的眼斑叫做"眼状斑"', '孔雀实际上可以飞行，但不擅长长距离飞行'], callDescription: '发出尖锐的叫声，特别是在求偶季节', lifespan: '野外约15-20年' },
  { id: 4, name: '老鹰', scientificName: 'Aquila chrysaetos', imageUrl: 'static/birds/eagle.jpg', tags: ['猛禽', '大型', '捕食者'], habitat: '山地、草原、森林', size: '体长75-100cm', weight: '3-7公斤', wingspan: '180-280cm', diet: '小型哺乳动物、鸟类、鱼类', behavior: '优秀的猎手，视力极佳', distribution: '全球各大洲（除南极洲）', conservationStatus: '部分种类濒危', characteristics: ['视力是人类的8倍', '强有力的爪子和喙', '飞行能力极强', '领域性强'], funFacts: ['老鹰可以从3公里外发现猎物', '它们的俯冲速度可达每小时300公里', '老鹰可以活到30岁以上'], callDescription: '发出尖锐的啸叫声', lifespan: '野外约20-30年' }
]

const safeCurrentIndex = computed(() => {
  const index = parseInt(currentCardIndex.value) || 0
  const total = parseInt(birdCards.value.length) || 0
  if (total === 0) return 0
  return Math.max(0, Math.min(index, total - 1))
})
const safeTotalCards = computed(() => parseInt(birdCards.value.length) || 0)
const currentDisplayPage = computed(() => safeCurrentIndex.value + 1)
const canGoPrevious = computed(() => safeCurrentIndex.value > 0 && !isFlipping.value && safeTotalCards.value > 0)
const canGoNext = computed(() => safeCurrentIndex.value < safeTotalCards.value - 1 && !isFlipping.value && safeTotalCards.value > 0)
const currentCardStyle = computed(() => ({ transform: `translateY(${cardTranslateY.value}px) scale(${cardScale.value})`, opacity: cardOpacity.value, zIndex: 10 }))
const backgroundCardStyle = computed(() => ({ transform: `scale(${backgroundCardScale.value})`, opacity: backgroundCardOpacity.value, zIndex: 5 }))

const onTouchStart = (event) => {
  if (isFlipping.value) return
  touchStartY.value = event.touches[0].clientY
  touchCurrentY.value = event.touches[0].clientY
}
const onTouchMove = (event) => {
  if (isFlipping.value || birdCards.value.length === 0) return
  touchCurrentY.value = event.touches[0].clientY
  const deltaY = touchCurrentY.value - touchStartY.value
  if (deltaY < 0 && currentCardIndex.value < birdCards.value.length - 1) {
    const progress = Math.min(Math.abs(deltaY) / 200, 1)
    cardTranslateY.value = deltaY
    cardOpacity.value = 1 - progress * 0.7
    cardScale.value = 1 - progress * 0.1
    backgroundCardScale.value = 0.95 + progress * 0.05
    backgroundCardOpacity.value = 0.7 + progress * 0.3
  }
}
const onTouchEnd = () => {
  if (isFlipping.value || birdCards.value.length === 0) return
  const deltaY = touchCurrentY.value - touchStartY.value
  if (deltaY < -100 && currentCardIndex.value < birdCards.value.length - 1) {
    nextCard()
  } else {
    resetCardPosition()
  }
}
const resetCardPosition = () => {
  cardTranslateY.value = 0; cardOpacity.value = 1; cardScale.value = 1
  backgroundCardScale.value = 0.95; backgroundCardOpacity.value = 0.7
}

const goBack = () => router.back()

const toggleMode = () => {
  currentMode.value = currentMode.value === 'search' ? 'general' : 'search'
  vibrate('short')
  if (currentMode.value === 'general' && birdCards.value.length === 0) initGeneralMode()
}

const onSearchInput = () => {
  if (searchKeyword.value.trim()) performSearch()
  else searchResults.value = []
}
const handleSearchConfirm = () => { if (searchKeyword.value.trim()) performSearch() }
const clearSearch = () => { searchKeyword.value = ''; searchResults.value = [] }

const selectBird = (bird) => {
  currentMode.value = 'general'
  const index = birdCards.value.findIndex(card => card.id === bird.id)
  if (index !== -1) currentCardIndex.value = index
  searchKeyword.value = ''; searchResults.value = []
  resetCardPosition()
}

const previousCard = () => {
  const idx = parseInt(currentCardIndex.value) || 0
  if (idx > 0 && !isFlipping.value && birdCards.value.length > 0) {
    isFlipping.value = true
    cardTranslateY.value = 50; cardOpacity.value = 0
    setTimeout(() => { currentCardIndex.value = Math.max(0, idx - 1); resetCardPosition(); isFlipping.value = false }, 300)
  }
}

const nextCard = () => {
  const idx = parseInt(currentCardIndex.value) || 0
  const total = parseInt(birdCards.value.length) || 0
  if (idx < total - 1 && !isFlipping.value && total > 0) {
    isFlipping.value = true
    cardTranslateY.value = -200; cardOpacity.value = 0; cardScale.value = 0.8
    setTimeout(() => { currentCardIndex.value = Math.min(total - 1, idx + 1); resetCardPosition(); isFlipping.value = false }, 300)
    vibrate('short')
  }
}

const onCardLike = () => { showToast('已收藏', 'success') }
const onCardShare = (bird) => {
  if (navigator.share) {
    navigator.share({ title: `鸟类：${bird.name}`, text: `${bird.name} (${bird.scientificName})`, url: window.location.href }).catch(() => {})
  } else {
    showToast('已复制链接', 'success')
  }
}

const performSearch = async () => {
  isSearching.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
    const keyword = searchKeyword.value.toLowerCase()
    searchResults.value = mockBirdData.filter(b => b.name.toLowerCase().includes(keyword) || b.scientificName.toLowerCase().includes(keyword) || b.tags.some(t => t.includes(keyword)) || b.habitat.includes(keyword))
  } finally { isSearching.value = false }
}

const initGeneralMode = () => { birdCards.value = [...mockBirdData]; currentCardIndex.value = 0; resetCardPosition() }
const loadBirdData = async () => { birdCards.value = [...mockBirdData] }

watch([birdCards, currentCardIndex], ([cards, idx]) => {
  const total = parseInt(cards.length) || 0
  const index = parseInt(idx) || 0
  if (total > 0) {
    const valid = Math.max(0, Math.min(index, total - 1))
    if (valid !== index) currentCardIndex.value = valid
  } else { currentCardIndex.value = 0 }
})

onMounted(async () => {
  await loadBirdData()
  resetCardPosition()
})
</script>

<style scoped>
.encyclopedia-container { min-height: 100vh; background: linear-gradient(180deg, #f8fffe, #ffffff); }
.custom-navbar { height: 44px; background: linear-gradient(135deg, #4caf50, #43a047); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; z-index: 100; box-shadow: 0 1px 8px rgba(76,175,80,0.2); }
.navbar-left, .navbar-right { width: 40px; height: 30px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.back-icon { font-size: 18px; color: white; }
.navbar-title { font-size: 16px; font-weight: 600; color: white; }
.mode-switch { width: 30px; height: 30px; background: rgba(255,255,255,0.2); border-radius: 15px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
.mode-switch:hover { background: rgba(255,255,255,0.3); }
.mode-switch-active { background: rgba(255,255,255,0.3); }
.mode-icon { font-size: 16px; }

.search-mode { padding: 12px 16px; }
.search-section { margin-bottom: 16px; }
.search-input-wrapper { display: flex; align-items: center; height: 44px; background: white; border-radius: 22px; padding: 0 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; }
.search-input-wrapper:focus-within { border-color: #4caf50; box-shadow: 0 2px 12px rgba(76,175,80,0.15); }
.search-icon { font-size: 16px; margin-right: 8px; opacity: 0.6; }
.search-input { flex: 1; font-size: 14px; color: #333; border: none; outline: none; background: transparent; }
.clear-btn { width: 24px; height: 24px; background: rgba(0,0,0,0.05); border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; }

.loading-container { display: flex; flex-direction: column; align-items: center; padding: 60px 0; }
.loading-spinner { width: 30px; height: 30px; border: 2px solid #e0e0e0; border-top-color: #4caf50; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 14px; color: #666; }

.results-grid { display: flex; flex-direction: column; gap: 10px; }
.result-card { display: flex; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.2s; animation: slideInUp 0.5s ease both; }
.result-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
@keyframes slideInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
.result-image { width: 100px; height: 100px; object-fit: cover; flex-shrink: 0; }
.result-content { padding: 12px; flex: 1; }
.result-name { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 4px; display: block; }
.result-scientific { font-size: 12px; color: #666; font-style: italic; margin-bottom: 6px; display: block; }
.result-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.result-tag { background: rgba(76,175,80,0.1); color: #4caf50; padding: 2px 6px; border-radius: 6px; font-size: 10px; }

.no-results, .search-placeholder { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; text-align: center; }
.no-results-icon, .placeholder-icon { font-size: 60px; margin-bottom: 12px; opacity: 0.5; }
.no-results-text, .placeholder-text { font-size: 14px; color: #666; font-weight: 500; margin-bottom: 4px; }
.no-results-subtitle, .placeholder-subtitle { font-size: 12px; color: #999; }

.general-mode { display: flex; flex-direction: column; height: calc(100vh - 44px); }
.progress-indicator { padding: 10px 16px; background: white; }
.progress-text { font-size: 12px; color: #666; text-align: center; margin-bottom: 6px; display: block; }
.progress-bar { height: 3px; background: #f0f0f0; border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4caf50, #66bb6a); border-radius: 2px; transition: width 0.3s ease; }

.card-stack-container { flex: 1; position: relative; padding: 10px 16px; margin-bottom: 10px; }
.card-stack { position: relative; width: 100%; height: 100%; }
.card-item { position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 16px; transition: all 0.3s ease; }
.current-card { z-index: 10; }
.background-card { z-index: 5; filter: blur(1px); }

.bottom-actions { height: 60px; background: white; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-top: 1px solid #f0f0f0; box-shadow: 0 -1px 5px rgba(0,0,0,0.05); }
.action-button { display: flex; align-items: center; gap: 4px; padding: 8px 12px; background: rgba(76,175,80,0.1); border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.action-button:hover:not(.btn-disabled) { background: rgba(76,175,80,0.2); transform: scale(1.05); }
.action-button.btn-disabled { opacity: 0.3; cursor: not-allowed; }
.action-text { font-size: 12px; color: #4caf50; font-weight: 500; }
.card-counter { display: flex; align-items: center; gap: 4px; }
.counter-text { font-size: 18px; font-weight: 600; color: #4caf50; }
.counter-divider { color: #ddd; }
.counter-total { font-size: 18px; font-weight: 600; color: #333; }

@media screen and (max-width: 375px) {
  .card-stack-container { padding: 8px 12px; }
  .bottom-actions { padding: 0 16px; }
}
</style>
