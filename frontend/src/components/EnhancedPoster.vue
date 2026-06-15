<template>
  <div class="poster-card" @click="$emit('view', posterData)">
    <div class="card-img-wrap">
      <img :src="posterImageUrl" :style="{ height: imgHeight + 'px' }" alt="" @load="loaded = true" @error="loaded = true" />
      <div v-if="!loaded" class="card-img-skeleton skeleton"></div>
      <div class="card-img-overlay">
        <span v-if="posterData.location" class="location-tag">📍 {{ posterData.location }}</span>
      </div>
    </div>

    <div class="card-body">
      <div class="card-author">
        <img :src="authorAvatarUrl" class="author-avatar" alt="" />
        <div>
          <div class="author-name">{{ posterData.author?.name || '匿名用户' }}</div>
          <div class="author-time">{{ posterData.publishTime || '刚刚' }}</div>
        </div>
      </div>

      <p class="card-desc" :class="{ expanded: expanded }">{{ posterData.description }}</p>
      <button v-if="longText" class="expand-btn" @click.stop="expanded = !expanded">{{ expanded ? '收起' : '展开全文' }}</button>

      <div class="card-footer">
        <div class="card-actions">
          <button class="action like" :class="{ liked }" @click.stop="handleLike">
            {{ liked ? '❤️' : '🤍' }} {{ fmt(posterData.likeCount) }}
          </button>
          <button class="action share" @click.stop="handleShare">↗</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showActionSheet } from '@/utils/toast.js'
import { vibrate } from '@/utils/helpers.js'

const props = defineProps({
  posterData: { type: Object, required: true }
})
const emit = defineEmits(['like', 'view', 'share'])

const loaded = ref(false)
const expanded = ref(false)
const liked = computed(() => props.posterData.isLiked || false)

const imgHeight = computed(() => props.posterData.imageHeight || 200)
const longText = computed(() => props.posterData.description?.length > 60)

const posterImageUrl = computed(() => {
  const url = props.posterData.imageUrl
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('blob:')) return url
  return getOSSUrl(url, 'medium')
})
const authorAvatarUrl = computed(() => {
  const url = props.posterData.author?.avatar
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('blob:')) return url
  return getOSSUrl(url, 'avatar')
})

const handleLike = () => {
  emit('like', props.posterData)
  vibrate('medium')
}
const handleShare = () => {
  emit('share', props.posterData)
  showActionSheet(['分享链接', '保存图片', '举报']).then(i => {
    if (i >= 0) showToast('已处理', 'success')
  })
}
const fmt = (n) => {
  if (!n) return '0'
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}
</script>

<style scoped>
.poster-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-normal);
}
.poster-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-img-wrap { position: relative; overflow: hidden; }
.card-img-wrap img { width: 100%; object-fit: cover; display: block; transition: transform 0.4s ease; }
.poster-card:hover .card-img-wrap img { transform: scale(1.03); }
.card-img-skeleton { position: absolute; inset: 0; }
.card-img-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 20px 10px 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.35));
}
.location-tag {
  font-size: 11px; color: #fff;
  background: rgba(0,0,0,0.35); backdrop-filter: blur(4px);
  padding: 3px 8px; border-radius: var(--radius-full);
}

.card-body { padding: 12px; }
.card-author { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.author-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  object-fit: cover; border: 2px solid var(--color-border);
}
.author-name { font-size: 13px; font-weight: 600; color: var(--color-text); }
.author-time { font-size: 11px; color: var(--color-text-muted); }

.card-desc {
  font-size: 13px; color: var(--color-text-secondary);
  line-height: 1.5; margin-bottom: 6px;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-desc.expanded { -webkit-line-clamp: unset; }
.expand-btn {
  background: none; border: none;
  font-size: 12px; color: var(--color-primary);
  font-weight: 600; cursor: pointer; padding: 0; margin-bottom: 10px;
}
.expand-btn:hover { text-decoration: underline; }

.card-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding-top: 8px; border-top: 1px solid var(--color-border);
}
.stat { font-size: 12px; color: var(--color-text-muted); }
.card-actions { display: flex; gap: 6px; }
.action {
  background: var(--color-bg); border: none;
  padding: 5px 10px; border-radius: var(--radius-sm);
  font-size: 12px; cursor: pointer;
  transition: all var(--transition-fast);
  display: flex; align-items: center; gap: 3px;
}
.action:hover { background: var(--color-border); }
.action.liked { background: #fee2e2; color: #ef4444; }
</style>
