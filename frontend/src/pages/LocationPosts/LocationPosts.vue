<template>
  <div class="location-posts-page">
    <!-- 顶部导航 -->
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">← 返回地图</button>
      <h2>📍 {{ locationName }}</h2>
      <span class="post-count">共 {{ posts.length }} 篇帖子</span>
    </div>

    <!-- 加载中 -->
    <div v-if="isLoading" class="loading-zone">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <!-- 帖子列表 -->
    <div v-else-if="posts.length > 0" class="posts-grid">
      <div v-for="p in posts" :key="p.id" class="post-item fade-in" @click="$router.push('/post/' + p.id)">
        <div v-if="p.images?.length" class="post-img-wrap">
          <img :src="resolveUrl(p.images[0])" alt="" class="post-img" />
        </div>
        <div class="post-body">
          <h3 class="post-title">{{ p.title }}</h3>
          <p class="post-content">{{ truncate(p.content, 120) }}</p>
          <div class="post-meta">
            <span class="author">{{ p.author_name || '匿名用户' }}</span>
            <span class="time">{{ formatTime(p.created_at) }}</span>
            <span class="stats">
              ❤️ {{ p.like_count || 0 }} · 💬 {{ p.comment_count || 0 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空 -->
    <div v-else class="empty-zone">
      <span class="empty-icon">📭</span>
      <h3>该位置暂无帖子</h3>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PostService from '@/api/services/post.js'
import { formatRelativeTime } from '@/utils/helpers.js'

const route = useRoute()
const locationName = ref(route.query.name || '')
const posts = ref([])
const isLoading = ref(true)

function resolveUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('blob:')) return url
  if (url.startsWith('/')) return url
  return '/' + url
}

function truncate(text, max) {
  if (!text) return ''
  return text.length > max ? text.slice(0, max) + '...' : text
}

function formatTime(t) {
  if (!t) return ''
  return formatRelativeTime(t)
}

onMounted(async () => {
  try {
    // 分页拉取所有帖子，过滤出匹配位置的
    let allItems = []
    let page = 1
    const pageSize = 50
    while (true) {
      const res = await PostService.getPostList(page, pageSize)
      const data = res.data?.data
      const items = data?.items || []
      allItems.push(...items)
      if (!data?.pagination || page >= data.pagination.total_pages) break
      page++
    }
    posts.value = allItems.filter(p => p.location === locationName.value)
  } catch (e) {
    console.error('load posts error:', e)
  }
  isLoading.value = false
})
</script>

<style scoped>
.location-posts-page { max-width: 720px; margin: 0 auto; padding: 24px 20px 80px; }

.page-header { margin-bottom: 24px; }
.back-btn {
  background: none; border: none; font-size: 14px; color: var(--color-primary);
  cursor: pointer; padding: 4px 0; margin-bottom: 12px; font-weight: 600;
}
.back-btn:hover { text-decoration: underline; }
.page-header h2 { font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.post-count { font-size: 13px; color: var(--color-text-muted); }

.loading-zone {
  display: flex; flex-direction: column; align-items: center; padding: 80px 20px; gap: 12px;
}
.loading-spinner {
  width: 28px; height: 28px;
  border: 3px solid var(--color-border); border-top-color: var(--color-primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.posts-grid { display: flex; flex-direction: column; gap: 16px; }
.post-item {
  display: flex; gap: 16px;
  background: var(--color-surface); border-radius: var(--radius-lg);
  border: 1px solid var(--color-border); padding: 16px;
  cursor: pointer; transition: all 0.2s;
}
.post-item:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }

.post-img-wrap { flex-shrink: 0; }
.post-img {
  width: 120px; height: 90px; object-fit: cover;
  border-radius: var(--radius-md); background: var(--color-bg);
}

.post-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.post-body .post-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; color: var(--color-text); }
.post-body .post-content {
  font-size: 13px; color: var(--color-text-muted); line-height: 1.5;
  flex: 1; margin-bottom: 8px;
}
.post-meta { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--color-text-muted); }
.stats { color: var(--color-primary); }

.empty-zone { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 48px; opacity: 0.4; display: block; margin-bottom: 12px; }
.empty-zone h3 { font-size: 16px; color: var(--color-text-secondary); }

.fade-in { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .location-posts-page { padding: 16px 12px 80px; }
  .post-item { flex-direction: column; }
  .post-img { width: 100%; height: 180px; }
}
</style>
