<template>
  <article class="knowledge-card">
    <div class="cover">
      <img :src="imageSrc" :alt="birdData.name" @error="onImageError" />
      <div class="cover-shade">
        <div>
          <h2>{{ birdData.name }}</h2>
          <p>{{ birdData.scientificName || '学名待补充' }}</p>
        </div>
        <button class="icon-btn" type="button" :class="{ active: isLiked }" @click.stop="handleLike">
          {{ isLiked ? '♥' : '♡' }}
        </button>
      </div>
    </div>

    <div class="content">
      <div class="meta-grid">
        <div class="meta-item">
          <span class="label">分布</span>
          <strong>{{ birdData.distribution || '暂无记录' }}</strong>
        </div>
        <div class="meta-item">
          <span class="label">习性</span>
          <strong>{{ birdData.behavior || '暂无记录' }}</strong>
        </div>
        <div class="meta-item">
          <span class="label">热度</span>
          <strong>{{ formatCount(birdData.searchCount) }}</strong>
        </div>
        <div class="meta-item">
          <span class="label">状态</span>
          <strong>{{ birdData.conservationStatus || '常见记录' }}</strong>
        </div>
      </div>

      <section>
        <h3>简介</h3>
        <p>{{ birdData.description || '这只鸟的详细介绍还在整理中。' }}</p>
      </section>

      <section v-if="birdData.tags?.length">
        <h3>标签</h3>
        <div class="tags">
          <span v-for="tag in birdData.tags" :key="tag">{{ tag }}</span>
        </div>
      </section>

      <div class="actions">
        <button class="secondary-btn" type="button" @click.stop="emit('share', birdData)">分享</button>
        <button class="primary-btn" type="button" @click.stop="playBirdCall">鸟鸣示例</button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'
import { vibrate } from '@/utils/helpers.js'

const props = defineProps({
  birdData: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
})

const emit = defineEmits(['like', 'share'])
const isLiked = ref(false)
const imageFailed = ref(false)

const placeholder = 'data:image/svg+xml,' + encodeURIComponent(`
<svg width="900" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#ecfdf5"/><stop offset="1" stop-color="#dbeafe"/></linearGradient></defs>
  <rect width="900" height="600" fill="url(#g)"/>
  <circle cx="450" cy="250" r="86" fill="#10b981" opacity=".18"/>
  <text x="450" y="330" text-anchor="middle" fill="#047857" font-family="Arial" font-size="34" font-weight="700">暂无鸟类图片</text>
</svg>`)

const imageSrc = computed(() => {
  if (imageFailed.value || !props.birdData.imageUrl) return placeholder
  return getOSSUrl(props.birdData.imageUrl, 'large')
})

function formatCount(value) {
  const count = Number(value || 0)
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万`
  return count.toLocaleString()
}

function onImageError() {
  imageFailed.value = true
}

function handleLike() {
  isLiked.value = !isLiked.value
  emit('like', props.birdData)
  vibrate('short')
}

function playBirdCall() {
  showToast('鸟鸣音频功能待接入', 'none')
  vibrate('short')
}
</script>

<style scoped>
.knowledge-card {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.cover {
  position: relative;
  height: 230px;
  min-height: 180px;
  background: var(--color-primary-bg);
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-shade {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  color: #fff;
  background: linear-gradient(180deg, rgba(0,0,0,0.08), rgba(0,0,0,0.68));
}

.cover h2 {
  margin: 0 0 4px;
  font-size: 28px;
  line-height: 1.15;
}

.cover p {
  margin: 0;
  font-size: 14px;
  font-style: italic;
  opacity: 0.9;
}

.icon-btn {
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  border-radius: 50%;
  color: #fff;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.36);
  font-size: 24px;
  backdrop-filter: blur(8px);
}

.icon-btn.active {
  color: #fecaca;
  background: rgba(239,68,68,0.32);
}

.content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 18px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}

.meta-item {
  min-width: 0;
  padding: 12px;
  border-radius: var(--radius-sm);
  background: #f9fafb;
  border: 1px solid var(--color-border);
}

.label {
  display: block;
  margin-bottom: 4px;
  color: var(--color-text-muted);
  font-size: 12px;
}

.meta-item strong {
  display: block;
  color: var(--color-text);
  font-size: 13px;
  line-height: 1.45;
}

section {
  margin-top: 16px;
}

h3 {
  margin: 0 0 8px;
  color: var(--color-text);
  font-size: 15px;
}

section p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.7;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags span {
  padding: 5px 10px;
  border-radius: var(--radius-full);
  color: var(--color-primary);
  background: var(--color-primary-bg);
  font-size: 12px;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.primary-btn,
.secondary-btn {
  flex: 1;
  height: 40px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 700;
}

.primary-btn {
  color: #fff;
  background: var(--color-primary);
}

.secondary-btn {
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

@media (max-width: 640px) {
  .cover {
    height: 190px;
  }

  .cover h2 {
    font-size: 22px;
  }

  .content {
    padding: 14px;
  }
}
</style>
