<template>
  <div class="knowledge-card" :class="{ 'card-active': isActive }">
    <div class="card-header">
      <img :src="birdImageUrl" class="bird-image" alt="鸟类图片" @load="onImageLoad" @error="onImageError" />
      <div class="image-overlay">
        <div class="bird-title-section">
          <span class="bird-name">{{ birdData.name }}</span>
          <span class="scientific-name">{{ birdData.scientificName }}</span>
        </div>
        <div class="action-buttons">
          <div class="action-btn like-btn" :class="{ liked: isLiked }" @click="handleLike">
            <span class="action-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
          </div>
          <div class="action-btn share-btn" @click="handleShare">
            <span class="action-icon">↗</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card-content">
      <div class="basic-info-grid">
        <div class="info-card">
          <span class="info-icon">🏠</span>
          <div class="info-content">
            <span class="info-label">栖息地</span>
            <span class="info-value">{{ birdData.habitat }}</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">📏</span>
          <div class="info-content">
            <span class="info-label">体型</span>
            <span class="info-value">{{ birdData.size }}</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">⚖️</span>
          <div class="info-content">
            <span class="info-label">体重</span>
            <span class="info-value">{{ birdData.weight }}</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">🕊</span>
          <div class="info-content">
            <span class="info-label">翼展</span>
            <span class="info-value">{{ birdData.wingspan }}</span>
          </div>
        </div>
      </div>

      <div class="characteristics-section">
        <span class="section-title">主要特征</span>
        <div class="characteristics-tags">
          <span v-for="(c, i) in birdData.characteristics?.slice(0,4)" :key="i" class="characteristic-tag" :style="{ animationDelay: `${i*0.1}s` }">{{ c }}</span>
        </div>
      </div>

      <div class="habits-section">
        <div class="habit-item">
          <div class="habit-header">
            <span class="habit-icon">🍽</span>
            <span class="habit-title">饮食</span>
          </div>
          <span class="habit-desc">{{ birdData.diet }}</span>
        </div>
        <div class="habit-item">
          <div class="habit-header">
            <span class="habit-icon">🎯</span>
            <span class="habit-title">行为</span>
          </div>
          <span class="habit-desc">{{ birdData.behavior }}</span>
        </div>
      </div>

      <div class="fun-facts-section">
        <span class="section-title">趣味知识</span>
        <div class="fun-facts-compact">
          <div v-for="(fact, i) in birdData.funFacts?.slice(0,2)" :key="i" class="fun-fact" :style="{ animationDelay: `${i*0.15}s` }">
            <div class="fact-bullet">{{ i + 1 }}</div>
            <span class="fact-text">{{ fact }}</span>
          </div>
        </div>
      </div>

      <div class="status-section">
        <div class="distribution-info">
          <span class="distribution-icon">📍</span>
          <div class="distribution-content">
            <span class="distribution-label">分布区域</span>
            <span class="distribution-text">{{ birdData.distribution }}</span>
          </div>
        </div>
        <div class="conservation-status" :class="getConservationClass(birdData.conservationStatus)">
          <span class="conservation-icon">🛡</span>
          <span class="conservation-text">{{ birdData.conservationStatus }}</span>
        </div>
      </div>

      <div class="bottom-info">
        <div class="sound-info">
          <span class="sound-icon">🔊</span>
          <span class="sound-text">{{ birdData.callDescription }}</span>
          <div class="play-sound-btn" @click="playBirdCall">
            <span class="play-icon">▶</span>
          </div>
        </div>
        <div class="lifespan-info">
          <span class="lifespan-icon">⏳</span>
          <span class="lifespan-text">{{ birdData.lifespan }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import { vibrate } from '@/utils/helpers.js'
import { showToast } from '@/utils/toast.js'

const props = defineProps({
  birdData: { type: Object, required: true },
  isActive: { type: Boolean, default: false }
})
const emit = defineEmits(['like', 'share'])

const isLiked = ref(false)
const imageLoaded = ref(false)

const birdImageUrl = computed(() => getOSSUrl(props.birdData.imageUrl, 'large'))

const getConservationClass = (status) => {
  const map = { '无危': 'status-safe', '近危': 'status-near-threatened', '易危': 'status-vulnerable', '濒危': 'status-endangered', '极危': 'status-critical' }
  return map[status] || 'status-unknown'
}

const onImageLoad = () => { imageLoaded.value = true }
const onImageError = () => { console.error('鸟类图片加载失败') }

const handleLike = () => {
  isLiked.value = !isLiked.value
  emit('like', props.birdData)
  vibrate('short')
}

const handleShare = () => { emit('share', props.birdData) }

const playBirdCall = () => {
  showToast('播放鸟鸣声', 'none')
  vibrate('short')
}
</script>

<style scoped>
.knowledge-card {
  height: 100%;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.12);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}
.knowledge-card.card-active {
  transform: scale(1.02);
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
}
.card-header {
  position: relative;
  height: 120px;
  overflow: hidden;
}
.bird-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.card-active .bird-image { transform: scale(1.05); }
.image-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.6) 100%);
  display: flex; flex-direction: column; justify-content: space-between; padding: 10px;
}
.bird-title-section { align-self: flex-end; text-align: right; }
.bird-name { display: block; font-size: 18px; font-weight: 700; color: white; text-shadow: 0 1px 4px rgba(0,0,0,0.5); margin-bottom: 3px; }
.scientific-name { display: block; font-size: 11px; color: rgba(255,255,255,0.9); font-style: italic; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
.action-buttons { display: flex; gap: 6px; align-self: flex-start; }
.action-btn {
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(5px);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.3);
  cursor: pointer;
}
.action-btn:active { transform: scale(0.9); }
.like-btn.liked { background: rgba(255,107,107,0.3); border-color: rgba(255,107,107,0.5); }
.action-icon { font-size: 14px; }
.card-content { flex: 1; padding: 12px 10px; display: flex; flex-direction: column; gap: 10px; overflow-y: auto; }
.basic-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.info-card {
  background: #f8f9fa; border-radius: 6px; padding: 8px;
  display: flex; align-items: center; gap: 5px; transition: all 0.3s ease;
}
.info-card:hover { background: #f0f7f0; transform: translateY(-1px); }
.info-icon { font-size: 12px; opacity: 0.7; flex-shrink: 0; }
.info-content { flex: 1; min-width: 0; }
.info-label { font-size: 9px; color: #666; display: block; margin-bottom: 1px; }
.info-value { font-size: 10px; color: #333; font-weight: 500; display: block; line-height: 1.3; }
.characteristics-section .section-title {
  font-size: 12px; font-weight: 600; color: #333; margin-bottom: 6px; display: block;
  position: relative; padding-left: 6px;
}
.characteristics-section .section-title::before {
  content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 2px; height: 9px; background: linear-gradient(180deg, #4caf50, #66bb6a); border-radius: 1px;
}
.characteristics-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.characteristic-tag {
  background: linear-gradient(135deg, #e8f5e8, #f0f7f0); color: #4caf50;
  padding: 3px 6px; border-radius: 6px; font-size: 9px; font-weight: 500;
  border: 1px solid rgba(76,175,80,0.2); animation: slideInLeft 0.5s ease both;
}
@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-5px); }
  to { opacity: 1; transform: translateX(0); }
}
.habits-section { display: flex; gap: 6px; }
.habit-item {
  flex: 1; background: linear-gradient(135deg, #f8fff8, #f0f9f0);
  border-radius: 6px; padding: 8px; border: 1px solid rgba(76,175,80,0.1);
}
.habit-header { display: flex; align-items: center; gap: 4px; margin-bottom: 4px; }
.habit-icon { font-size: 10px; }
.habit-title { font-size: 10px; font-weight: 600; color: #4caf50; }
.habit-desc {
  font-size: 9px; color: #555; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.fun-facts-section .section-title {
  font-size: 12px; font-weight: 600; color: #333; margin-bottom: 6px; display: block;
  position: relative; padding-left: 6px;
}
.fun-facts-section .section-title::before {
  content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 2px; height: 9px; background: linear-gradient(180deg, #ff9800, #ffb74d); border-radius: 1px;
}
.fun-facts-compact { display: flex; flex-direction: column; gap: 5px; }
.fun-fact {
  display: flex; gap: 6px; background: linear-gradient(135deg, #fff3e0, #ffeaa7);
  border-radius: 6px; padding: 6px; animation: bounceIn 0.6s ease both;
}
@keyframes bounceIn {
  0% { opacity: 0; transform: scale(0.9); }
  50% { transform: scale(1.02); }
  100% { opacity: 1; transform: scale(1); }
}
.fact-bullet {
  width: 16px; height: 16px; background: linear-gradient(135deg, #ff9800, #ffb74d);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 8px; font-weight: 600; color: white; flex-shrink: 0;
}
.fact-text { flex: 1; font-size: 9px; color: #555; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.status-section { display: flex; gap: 6px; align-items: center; }
.distribution-info { flex: 1; display: flex; align-items: center; gap: 5px; background: #f8f9fa; border-radius: 6px; padding: 6px; }
.distribution-icon { font-size: 12px; flex-shrink: 0; }
.distribution-content { flex: 1; min-width: 0; }
.distribution-label { font-size: 8px; color: #666; display: block; margin-bottom: 1px; }
.distribution-text { font-size: 9px; color: #333; font-weight: 500; display: block; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.conservation-status {
  display: flex; align-items: center; gap: 3px; padding: 4px 6px; border-radius: 6px; border: 1px solid; flex-shrink: 0;
}
.conservation-status.status-safe { background: rgba(76,175,80,0.1); border-color: rgba(76,175,80,0.3); color: #4caf50; }
.conservation-status.status-near-threatened { background: rgba(255,193,7,0.1); border-color: rgba(255,193,7,0.3); color: #ffc107; }
.conservation-status.status-vulnerable { background: rgba(255,152,0,0.1); border-color: rgba(255,152,0,0.3); color: #ff9800; }
.conservation-status.status-endangered { background: rgba(244,67,54,0.1); border-color: rgba(244,67,54,0.3); color: #f44336; }
.conservation-status.status-critical { background: rgba(156,39,176,0.1); border-color: rgba(156,39,176,0.3); color: #9c27b0; }
.conservation-icon { font-size: 8px; }
.conservation-text { font-size: 9px; font-weight: 500; }
.bottom-info { display: flex; gap: 6px; }
.sound-info {
  flex: 2; display: flex; align-items: center; gap: 4px;
  background: linear-gradient(135deg, #e8f5e8, #f1f8e9); border-radius: 6px; padding: 6px;
}
.sound-icon { font-size: 10px; flex-shrink: 0; }
.sound-text { flex: 1; font-size: 8px; color: #555; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.play-sound-btn {
  width: 16px; height: 16px; background: rgba(76,175,80,0.2); border-radius: 8px;
  display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; flex-shrink: 0; cursor: pointer;
}
.play-sound-btn:active { transform: scale(0.9); background: rgba(76,175,80,0.3); }
.play-icon { font-size: 8px; }
.lifespan-info {
  flex: 1; display: flex; align-items: center; gap: 4px;
  background: linear-gradient(135deg, #f3e5f5, #fce4ec); border-radius: 6px; padding: 6px;
}
.lifespan-icon { font-size: 10px; flex-shrink: 0; }
.lifespan-text { flex: 1; font-size: 8px; color: #555; font-weight: 500; line-height: 1.3; }
</style>
