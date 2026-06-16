<template>
  <main class="ranking-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">Bird Hot List</p>
        <h1>热门鸟类排行榜</h1>
        <p class="subtitle">根据图鉴搜索和详情查看次数实时排序。</p>
      </div>
      <router-link class="encyclopedia-link" to="/encyclopedia">进入图鉴</router-link>
    </header>

    <section class="controls" aria-label="排行榜数量切换">
      <div class="limit-tabs" role="tablist" aria-label="选择排行榜展示数量">
        <button
          v-for="option in limitOptions"
          :key="option"
          type="button"
          role="tab"
          :aria-selected="limit === option"
          :class="{ active: limit === option }"
          @click="changeLimit(option)"
        >
          Top {{ option }}
        </button>
      </div>
      <span v-if="!isLoading && !errorMsg" class="result-count">
        已展示 {{ rankedBirds.length }} / {{ limit }} 项
      </span>
    </section>

    <section v-if="isLoading" class="ranking-list">
      <div v-for="i in skeletonCount" :key="i" class="skeleton rank-skeleton"></div>
    </section>

    <section v-else-if="errorMsg" class="state-box">
      <strong>排行榜加载失败</strong>
      <p>{{ errorMsg }}</p>
      <button class="btn btn-primary" type="button" @click="loadRankings">重试</button>
    </section>

    <section v-else-if="rankedBirds.length" class="ranking-list">
      <article
        v-for="bird in rankedBirds"
        :key="bird.id"
        class="rank-item"
        :class="`rank-card-${bird.rank}`"
      >
        <div class="rank-num">{{ bird.rank }}</div>
        <img :src="getBirdImg(bird.image_url)" :alt="bird.name" @error="onImgError" />
        <div class="rank-info">
          <div class="rank-title">
            <h2>{{ bird.name }}</h2>
            <span>{{ bird.latin_name || '学名待补充' }}</span>
          </div>
          <p class="meta">{{ [bird.region, bird.habits].filter(Boolean).join(' · ') || '暂无分布与习性记录' }}</p>
          <p class="desc">{{ bird.description || '暂无简介' }}</p>
        </div>
        <div class="score">
          <strong>{{ fmtNum(bird.search_count) }}</strong>
          <span>热度</span>
        </div>
      </article>
    </section>

    <section v-else class="state-box empty-state">
      <div class="state-icon" aria-hidden="true">🏆</div>
      <strong>暂无排行数据</strong>
      <p>当前 Top {{ limit }} 还没有可展示的鸟类热度记录。搜索或查看图鉴详情后，这里会自动更新。</p>
      <router-link class="btn btn-primary" to="/encyclopedia">先去图鉴看看</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { getOSSUrl } from '@/config/oss.js'
import BirdApiService from '@/api/services/bird.js'

const isLoading = ref(true)
const errorMsg = ref('')
const rankedBirds = ref([])
const limit = ref(10)
const limitOptions = [10, 20, 50]
let currentRequestId = 0

const skeletonCount = computed(() => Math.min(limit.value, 10))

function fmtNum(value) {
  const count = Number(value || 0)
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万`
  return count.toLocaleString()
}

function placeholderImage() {
  return 'data:image/svg+xml,' + encodeURIComponent('<svg width="96" height="96" xmlns="http://www.w3.org/2000/svg"><rect width="96" height="96" rx="12" fill="#ecfdf5"/><text x="48" y="53" text-anchor="middle" fill="#047857" font-size="13" font-family="Arial">暂无图片</text></svg>')
}

function getBirdImg(url) {
  return url ? getOSSUrl(url, 'medium') : placeholderImage()
}

function onImgError(event) {
  event.target.src = placeholderImage()
}

async function loadRankings() {
  const requestId = ++currentRequestId
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await BirdApiService.getRankings(limit.value)
    if (requestId !== currentRequestId) return
    rankedBirds.value = res.data?.data || []
  } catch (err) {
    if (requestId !== currentRequestId) return
    errorMsg.value = err?.message || '请检查后端服务是否已启动。'
  } finally {
    if (requestId === currentRequestId) {
      isLoading.value = false
    }
  }
}

function changeLimit(value) {
  if (limit.value === value) return
  limit.value = value
  loadRankings()
}

onMounted(loadRankings)
</script>

<style scoped>
.ranking-page {
  width: min(980px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 28px 20px 96px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-header h1 {
  margin: 0 0 6px;
  color: var(--color-text);
  font-size: 30px;
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.encyclopedia-link {
  flex: 0 0 auto;
  padding: 10px 16px;
  border-radius: var(--radius-full);
  color: #fff;
  background: var(--color-primary);
  font-size: 14px;
  font-weight: 800;
  box-shadow: var(--shadow-sm);
}

.controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 16px;
}

.limit-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.limit-tabs button {
  padding: 8px 14px;
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  font-weight: 800;
  transition: color var(--transition-fast), background var(--transition-fast), border-color var(--transition-fast);
}

.limit-tabs button:hover {
  color: var(--color-primary);
  border-color: rgba(5,150,105,0.35);
}

.limit-tabs button.active {
  color: var(--color-primary);
  background: var(--color-primary-bg);
  border-color: rgba(5,150,105,0.25);
}

.result-count {
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.ranking-list {
  display: grid;
  gap: 12px;
}

.rank-item {
  display: grid;
  grid-template-columns: 46px 88px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.rank-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.rank-num {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  background: var(--color-bg);
  font-size: 18px;
  font-weight: 900;
}

.rank-card-1 .rank-num {
  color: #fff;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.rank-card-2 .rank-num {
  color: #fff;
  background: linear-gradient(135deg, #9ca3af, #d1d5db);
}

.rank-card-3 .rank-num {
  color: #fff;
  background: linear-gradient(135deg, #b45309, #d97706);
}

.rank-item img {
  width: 88px;
  height: 88px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  background: var(--color-primary-bg);
}

.rank-info {
  min-width: 0;
}

.rank-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 5px;
}

.rank-title h2 {
  margin: 0;
  color: var(--color-text);
  font-size: 18px;
}

.rank-title span {
  color: var(--color-text-muted);
  font-size: 12px;
  font-style: italic;
}

.meta,
.desc {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.desc {
  margin-top: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.score {
  min-width: 88px;
  padding: 10px 14px;
  text-align: center;
  border-radius: var(--radius-sm);
  background: var(--color-primary-bg);
}

.score strong {
  display: block;
  color: var(--color-primary);
  font-size: 20px;
}

.score span {
  color: var(--color-text-muted);
  font-size: 12px;
}

.rank-skeleton {
  height: 122px;
}

.state-box {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 300px;
  padding: 36px;
  text-align: center;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.state-box p {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.state-icon {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-full);
  background: var(--color-primary-bg);
  font-size: 26px;
}

.empty-state {
  max-width: 640px;
  margin: 0 auto;
}

@media (max-width: 720px) {
  .ranking-page {
    padding: 18px 12px 84px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .controls {
    align-items: flex-start;
    flex-direction: column;
  }

  .result-count {
    font-size: 12px;
  }

  .rank-item {
    grid-template-columns: 36px 64px minmax(0, 1fr);
    gap: 10px;
    padding: 12px;
  }

  .rank-num {
    width: 34px;
    height: 34px;
    font-size: 15px;
  }

  .rank-item img {
    width: 64px;
    height: 64px;
  }

  .rank-title {
    display: block;
  }

  .rank-title h2 {
    font-size: 16px;
  }

  .score {
    grid-column: 2 / 4;
    justify-self: start;
    min-width: 0;
    padding: 6px 10px;
  }

  .score strong,
  .score span {
    display: inline;
    font-size: 13px;
  }
}
</style>
