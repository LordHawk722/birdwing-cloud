<template>
  <div class="ranking-page">
    <div class="page-header">
      <h1>🏆 热门鸟类排行榜</h1>
      <p>基于社区搜索和观测数据的实时排行</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-zone">
      <div class="skeleton" style="height:80px;" v-for="i in 5" :key="i"></div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="errorMsg" class="error-zone">
      <span class="error-icon">⚠️</span>
      <p>{{ errorMsg }}</p>
      <button class="btn btn-secondary" @click="loadRankings">重试</button>
    </div>

    <!-- 排行榜列表 -->
    <div v-else class="ranking-list">
      <div v-for="(bird, i) in rankedBirds" :key="bird.id" class="rank-item fade-in" :style="{ animationDelay: `${i * 0.08}s` }">
        <div class="rank-num" :class="`rank-${i + 1}`">{{ i + 1 }}</div>
        <img :src="getBirdImg(bird.image_url)" :alt="bird.name" class="rank-img" @error="onImgError" />
        <div class="rank-info">
          <div class="rank-name">{{ bird.name }}</div>
          <div class="rank-meta">{{ bird.region || '' }}<span v-if="bird.habits"> · {{ bird.habits }}</span></div>
          <p class="rank-desc">{{ bird.description }}</p>
        </div>
        <div class="rank-count">
          <span class="count-num">{{ fmtNum(bird.search_count) }}</span>
          <span class="count-label">搜索量</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import BirdApiService from '@/api/services/bird.js'

const isLoading = ref(true)
const errorMsg = ref('')
const rankedBirds = ref([])

function fmtNum(n) {
  if (!n) return '0'
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toLocaleString()
}

function getBirdImg(url) {
  if (!url) return ''
  return getOSSUrl(url, 'medium')
}

function onImgError(e) {
  e.target.src = 'data:image/svg+xml,' + encodeURIComponent('<svg width="80" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" fill="#f0f0f0"/><text x="40" y="44" text-anchor="middle" fill="#999" font-size="12">暂无</text></svg>')
}

async function loadRankings() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await BirdApiService.getRankings(10)
    rankedBirds.value = res.data?.data || []
  } catch (err) {
    errorMsg.value = err?.message || '加载失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadRankings()
})
</script>

<style scoped>
.ranking-page { max-width: 800px; margin: 0 auto; padding: 24px 20px; }
.page-header { text-align: center; margin-bottom: 28px; }
.page-header h1 { font-size: 24px; color: var(--color-text); margin-bottom: 4px; }
.page-header p { font-size: 14px; color: var(--color-text-secondary); }

.loading-zone { display: flex; flex-direction: column; gap: 10px; }
.error-zone { text-align: center; padding: 60px 20px; }
.error-icon { font-size: 48px; display: block; margin-bottom: 12px; opacity: 0.5; }
.error-zone p { font-size: 14px; color: var(--color-text-muted); margin-bottom: 16px; }

.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.rank-item {
  display: flex; align-items: center; gap: 16px;
  background: var(--color-surface); border-radius: var(--radius-md);
  padding: 16px 20px; border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  animation: fadeIn 0.4s ease both;
}
.rank-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(4px);
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

.rank-num {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800;
  border-radius: var(--radius-sm);
  background: var(--color-bg); color: var(--color-text-secondary);
  flex-shrink: 0;
}
.rank-num.rank-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; font-size: 20px; }
.rank-num.rank-2 { background: linear-gradient(135deg, #c0c0c0, #9ca3af); color: #fff; }
.rank-num.rank-3 { background: linear-gradient(135deg, #d97706, #b45309); color: #fff; }

.rank-img {
  width: 64px; height: 64px; border-radius: var(--radius-sm);
  object-fit: cover; flex-shrink: 0; background: var(--color-bg);
}
.rank-info { flex: 1; min-width: 0; }
.rank-name { font-size: 16px; font-weight: 700; color: var(--color-text); margin-bottom: 3px; }
.rank-meta { font-size: 12px; color: var(--color-text-muted); margin-bottom: 4px; }
.rank-desc { font-size: 12px; color: var(--color-text-secondary); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.rank-count {
  text-align: center; flex-shrink: 0;
  padding: 8px 14px; background: var(--color-primary-bg);
  border-radius: var(--radius-sm);
}
.count-num { display: block; font-size: 16px; font-weight: 700; color: var(--color-primary); }
.count-label { font-size: 10px; color: var(--color-text-muted); }

@media (max-width: 768px) {
  .ranking-page { padding: 16px 12px; }
  .rank-item { padding: 12px 14px; gap: 10px; }
  .rank-img { width: 48px; height: 48px; }
  .rank-name { font-size: 14px; }
}
</style>
