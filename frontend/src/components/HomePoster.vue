<template>
  <div class="poster-item" @click="handleItemClick">
    <img
      :src="imageUrl"
      :style="{ height: posterData.imageHeight + 'px' }"
      class="poster-image"
      alt="鸟类图片"
      @error="handleImageError"
      @load="handleImageLoad"
    />

    <div v-if="imageLoading" class="image-loading">
      <div class="loading-spinner"></div>
    </div>

    <div class="poster-info">
      <div class="poster-description">{{ posterData.description }}</div>
      <div class="poster-stats">
        <div class="stat-item" v-if="posterData.views">
          <span class="stat-icon">👁</span>
          <span class="stat-text">{{ formatNumber(posterData.views) }}</span>
        </div>
        <div class="stat-item" v-if="posterData.likes">
          <span class="stat-icon">❤️</span>
          <span class="stat-text">{{ formatNumber(posterData.likes) }}</span>
        </div>
        <div class="stat-item" v-if="posterData.accuracy">
          <span class="accuracy-text">{{ posterData.accuracy }}</span>
        </div>
        <div class="stat-item" v-if="posterData.date">
          <span class="date-text">{{ posterData.date }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getOSSUrl } from '@/config/oss.js'

export default {
  name: 'HomePoster',
  props: {
    posterData: {
      type: Object,
      required: true,
      default: () => ({ id: '', imageUrl: '', imageHeight: 200, description: '', views: 0, likes: 0, accuracy: '', date: '' })
    }
  },
  emits: ['item-click', 'image-error'],
  data() {
    return { imageLoading: true, imageError: false }
  },
  computed: {
    imageUrl() {
      if (!this.posterData.imageUrl && !this.posterData.src) {
        return this.posterData.imageUrl || ''
      }
      const filename = this.posterData.imageUrl || this.posterData.src
      if (!filename) return ''
      if (filename.startsWith('http') || filename.startsWith('blob:')) return filename
      return getOSSUrl(filename, 'medium')
    }
  },
  methods: {
    handleImageLoad() {
      this.imageLoading = false
      this.imageError = false
    },
    handleImageError() {
      this.imageLoading = false
      this.imageError = true
      this.$emit('image-error', this.posterData)
    },
    handleItemClick() {
      this.$emit('item-click', this.posterData)
    },
    formatNumber(num) {
      if (!num) return '0'
      if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
      if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
      return num.toString()
    }
  }
}
</script>

<style scoped>
.poster-item {
  position: relative;
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}
.poster-item:active { transform: scale(0.98); }
.poster-image {
  width: 100%;
  display: block;
  background-color: #f5f5f5;
  object-fit: cover;
  transition: all 0.3s ease;
}
.poster-image:hover { transform: scale(1.02); }
.image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #2EA3B7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.poster-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  padding: 16px 12px 12px;
  transition: all 0.3s ease;
}
.poster-item:hover .poster-info {
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 20px 12px 16px;
}
.poster-description {
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.poster-stats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.stat-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 8px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}
.stat-icon { font-size: 12px; margin-right: 4px; }
.stat-text { font-size: 12px; color: rgba(255, 255, 255, 0.9); }
.accuracy-text {
  font-size: 12px;
  color: #4CAF50;
  font-weight: bold;
  background: rgba(76, 175, 80, 0.2);
  padding: 2px 6px;
  border-radius: 8px;
}
.date-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}
@media (max-width: 480px) {
  .poster-info { padding: 12px 8px 8px; }
  .poster-description { font-size: 13px; }
}
@media (prefers-color-scheme: dark) {
  .poster-item { background: #1a1a1a; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); }
  .poster-image { background-color: #2a2a2a; }
}
</style>
