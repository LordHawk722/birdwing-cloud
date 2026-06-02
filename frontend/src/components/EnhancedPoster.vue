<template>
  <div
    class="enhanced-poster"
    @click="handlePosterClick"
    :class="{ 'poster-pressed': isPressed }"
    @mousedown="onTouchStart"
    @mouseup="onTouchEnd"
    @mouseleave="onTouchEnd"
  >
    <div class="image-container">
      <img
        :src="posterImageUrl"
        class="poster-image"
        alt="鸟类海报"
        :style="{ height: imageHeight + 'px' }"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div v-if="imageLoading" class="image-loading">
        <div class="loading-skeleton"></div>
      </div>
      <div class="image-overlay">
        <div v-if="posterData.location" class="location-tag">
          <span class="location-text">{{ posterData.location }}</span>
        </div>
      </div>
    </div>

    <div class="content-container">
      <div class="author-info">
        <img :src="authorAvatarUrl" class="author-avatar" alt="头像" />
        <div class="author-details">
          <span class="author-name">{{ posterData.author?.name || '匿名用户' }}</span>
          <span class="publish-time">{{ posterData.publishTime || '刚刚' }}</span>
        </div>
      </div>

      <div class="description-container">
        <span class="description-text" :class="{ 'text-expanded': isTextExpanded }">
          {{ posterData.description }}
        </span>
        <span v-if="isTextTruncated" class="expand-btn" @click.stop="toggleTextExpansion">
          {{ isTextExpanded ? '收起' : '全文' }}
        </span>
      </div>

      <div class="interaction-area">
        <div class="stats-container">
          <div class="stat-item">
            <span class="stat-icon">👁</span>
            <span class="stat-text">{{ formatNumber(posterData.views) }}</span>
          </div>
        </div>
        <div class="action-buttons">
          <div class="action-btn like-btn" :class="{ 'like-active': isLiked }" @click.stop="handleLike">
            <span class="action-icon like-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
            <span class="action-text">{{ formatNumber(posterData.likes) }}</span>
            <div v-if="showLikeAnimation" class="like-animation">
              <span class="like-thumb">👍</span>
            </div>
          </div>
          <div class="action-btn share-btn" @click.stop="handleShare">
            <span class="action-icon">↗</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import { vibrate } from '@/utils/helpers.js'
import { showToast, showActionSheet } from '@/utils/toast.js'

const props = defineProps({
  posterData: {
    type: Object,
    required: true,
    default: () => ({ id: '', imageUrl: '', imageHeight: 200, description: '', views: 0, likes: 0, author: { name: '', avatar: '' }, location: '', publishTime: '' })
  }
})

const emit = defineEmits(['like', 'view', 'share'])

const imageLoading = ref(true)
const isPressed = ref(false)
const isTextExpanded = ref(false)
const isLiked = ref(false)
const showLikeAnimation = ref(false)

const imageHeight = computed(() => props.posterData.imageHeight || 200)
const isTextTruncated = computed(() => props.posterData.description && props.posterData.description.length > 50)

const posterImageUrl = computed(() => {
  if (!props.posterData.imageUrl) return ''
  if (props.posterData.imageUrl.startsWith('http') || props.posterData.imageUrl.startsWith('blob:')) {
    return props.posterData.imageUrl
  }
  return getOSSUrl(props.posterData.imageUrl, 'medium')
})

const authorAvatarUrl = computed(() => {
  const avatarPath = props.posterData.author?.avatar || 'static/default-avatar.png'
  if (avatarPath.startsWith('http') || avatarPath.startsWith('blob:')) return avatarPath
  return getOSSUrl(avatarPath, 'avatar')
})

watch(() => props.posterData.imageUrl, (newUrl) => {
  if (newUrl) imageLoading.value = true
})

const onImageLoad = () => { imageLoading.value = false }
const onImageError = () => { imageLoading.value = false }
const onTouchStart = () => { isPressed.value = true }
const onTouchEnd = () => { isPressed.value = false }

const handlePosterClick = () => {
  emit('view', props.posterData)
  vibrate('light')
}

const toggleTextExpansion = () => { isTextExpanded.value = !isTextExpanded.value }

const handleLike = () => {
  if (isLiked.value) return
  isLiked.value = true
  showLikeAnimation.value = true
  emit('like', props.posterData)
  vibrate('medium')
  setTimeout(() => { showLikeAnimation.value = false }, 1000)
}

const handleShare = () => {
  emit('share', props.posterData)
  showActionSheet(['分享到微信', '分享到朋友圈', '复制链接']).then((index) => {
    const actions = ['微信', '朋友圈', '复制链接']
    if (index >= 0) showToast(`已${actions[index]}`, 'success', 1500)
  })
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

onMounted(() => {
  if (props.posterData.imageUrl) imageLoading.value = true
})
</script>

<style scoped>
.enhanced-poster {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
  margin-bottom: 8px;
  cursor: pointer;
}
.enhanced-poster:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
}
.enhanced-poster.poster-pressed {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}
.poster-image {
  width: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.enhanced-poster:hover .poster-image { transform: scale(1.05); }
.image-loading {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loading-skeleton {
  width: 30px; height: 30px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 50%;
}
@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.image-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, transparent 60%, rgba(0,0,0,0.3) 100%);
  pointer-events: none;
}
.location-tag {
  position: absolute;
  top: 8px; left: 8px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(5px);
  border-radius: 10px;
  padding: 4px 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.location-text { font-size: 10px; color: #666; font-weight: 500; }
.content-container { padding: 12px; }
.author-info {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}
.author-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  border: 2px solid #f0f0f0;
  object-fit: cover;
}
.author-details { flex: 1; }
.author-name { display: block; font-size: 13px; color: #333; font-weight: 600; margin-bottom: 2px; }
.publish-time { display: block; font-size: 11px; color: #999; }
.description-container { margin-bottom: 10px; position: relative; }
.description-text {
  font-size: 14px; color: #333; line-height: 1.6;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.3s ease;
}
.description-text:not(.text-expanded) { -webkit-line-clamp: 3; }
.description-text.text-expanded { -webkit-line-clamp: unset; }
.expand-btn { color: #4caf50; font-size: 12px; font-weight: 600; margin-left: 4px; cursor: pointer; }
.expand-btn:active { opacity: 0.7; }
.interaction-area { display: flex; align-items: center; justify-content: space-between; }
.stats-container { display: flex; gap: 12px; }
.stat-item { display: flex; align-items: center; gap: 4px; }
.stat-icon { font-size: 14px; opacity: 0.6; }
.stat-text { font-size: 12px; color: #666; font-weight: 500; }
.action-buttons { display: flex; gap: 8px; }
.action-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 8px; border-radius: 10px;
  transition: all 0.3s ease; position: relative;
}
.action-btn:active { transform: scale(0.95); }
.like-btn {
  background: linear-gradient(135deg, #fff3e0, #fff8f0);
  border: 1px solid #ffcc80;
}
.like-btn.like-active {
  background: linear-gradient(135deg, #ffcc80, #ffb74d);
  border-color: #ff9800;
}
.like-btn.like-active .action-text { color: #e65100; font-weight: 600; }
.like-btn:hover { background: linear-gradient(135deg, #ffcc80, #ffb74d); transform: translateY(-1px); box-shadow: 0 3px 10px rgba(255,152,0,0.25); }
.share-btn {
  background: linear-gradient(135deg, #e3f2fd, #f0f8ff);
  border: 1px solid #bbdefb;
  padding: 6px;
}
.share-btn:hover { background: linear-gradient(135deg, #bbdefb, #e1f5fe); transform: translateY(-1px); }
.action-icon { font-size: 16px; transition: transform 0.3s ease; }
.like-animation { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); pointer-events: none; animation: likeFloatUp 1s ease-out forwards; }
.like-thumb { font-size: 16px; display: block; }
@keyframes likeFloatUp {
  0% { opacity: 1; transform: translateX(-50%) translateY(0) scale(0.8) rotate(0deg); }
  30% { opacity: 1; transform: translateX(-50%) translateY(-5px) scale(1.2) rotate(-5deg); }
  100% { opacity: 0; transform: translateX(-50%) translateY(-20px) scale(0.8) rotate(0deg); }
}
@media screen and (max-width: 375px) {
  .content-container { padding: 10px; }
  .author-avatar { width: 26px; height: 26px; }
  .author-name { font-size: 12px; }
  .description-text { font-size: 13px; }
  .action-btn { padding: 5px 7px; }
}
</style>
