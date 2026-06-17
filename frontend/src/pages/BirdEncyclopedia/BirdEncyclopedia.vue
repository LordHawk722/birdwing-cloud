<template>
  <main class="encyclopedia-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">‹</button>
      <div>
        <h1>鸟类图鉴</h1>
        <p>搜索鸟名、学名，或浏览热门鸟类卡片。</p>
      </div>
      <button class="mode-btn" type="button" @click="toggleMode">
        {{ mode === 'search' ? '卡片' : '搜索' }}
      </button>
    </header>

    <section class="search-panel">
      <div class="search-box">
        <span>⌕</span>
        <input
          v-model.trim="keyword"
          type="search"
          placeholder="输入鸟名或学名，如 麻雀 / Pica"
          @input="handleInput"
          @keyup.enter="searchBirds"
        />
        <button v-if="keyword" type="button" @click="clearSearch">清空</button>
      </div>
      <div class="quick-tags">
        <button v-for="tag in quickTags" :key="tag" type="button" @click="useQuickTag(tag)">{{ tag }}</button>
      </div>
    </section>

    <section v-if="mode === 'search'" class="results-section">
      <div class="section-head">
        <h2>{{ keyword ? '搜索结果' : '热门鸟类' }}</h2>
        <span v-if="!loading">{{ activeList.length }} 条</span>
      </div>

      <div v-if="loading" class="grid">
        <div v-for="i in 6" :key="i" class="skeleton result-skeleton"></div>
      </div>

      <div v-else-if="errorMsg" class="state-box">
        <strong>加载失败</strong>
        <p>{{ errorMsg }}</p>
        <button class="btn btn-primary" type="button" @click="loadInitialBirds">重试</button>
      </div>

      <div v-else-if="activeList.length" class="grid">
        <article v-for="bird in activeList" :key="bird.id" class="bird-tile" @click="openBird(bird)">
          <img :src="getBirdImage(bird)" :alt="bird.name" @error="onTileImageError" />
          <div class="tile-body">
            <h3>{{ bird.name }}</h3>
            <p class="latin">{{ bird.scientificName || '学名待补充' }}</p>
            <p>{{ bird.description || '暂无简介' }}</p>
            <div class="tile-tags">
              <span v-for="tag in bird.tags" :key="tag">{{ tag }}</span>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="state-box">
        <strong>没有找到相关鸟类</strong>
        <p>换一个中文名、学名或更短的关键词试试。</p>
      </div>
    </section>

    <section v-else class="card-section">
      <div class="card-toolbar">
        <div>
          <strong>{{ currentIndex + 1 }}</strong>
          <span>/ {{ cards.length }}</span>
        </div>
        <div class="progress">
          <i :style="{ width: `${progressPercent}%` }"></i>
        </div>
      </div>

      <div class="card-stage" @touchstart="onTouchStart" @touchend="onTouchEnd">
        <BirdKnowledgeCard
          v-if="currentBird"
          :bird-data="currentBird"
          :is-active="true"
          @like="onLike"
        />
        <div v-else class="state-box">
          <strong>暂无图鉴数据</strong>
          <p>请稍后重试。</p>
        </div>
      </div>

      <div class="card-actions">
        <button type="button" :disabled="currentIndex === 0" @click="previousCard">上一张</button>
        <button type="button" @click="mode = 'search'">返回列表</button>
        <button type="button" :disabled="currentIndex >= cards.length - 1" @click="nextCard">下一张</button>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BirdKnowledgeCard from '@/components/BirdKnowledgeCard.vue'
import BirdApiService from '@/api/services/bird.js'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'
import { vibrate } from '@/utils/helpers.js'

const router = useRouter()
const mode = ref('search')
const keyword = ref('')
const loading = ref(false)
const errorMsg = ref('')
const searchResults = ref([])
const cards = ref([])
const currentIndex = ref(0)
const touchStartX = ref(0)
let searchTimer = null

const quickTags = ['麻雀', '喜鹊', '翠鸟', '白鹭', '孔雀']

const fallbackBirds = [
  {
    id: 'local-1',
    name: '麻雀',
    scientificName: 'Passer montanus',
    region: '全国广泛分布',
    behavior: '群居，适应力强，常见于城市和乡村',
    description: '麻雀是城市中最常见的小型鸟类之一，常在建筑物周边、灌木和农田活动。',
    imageUrl: '',
    searchCount: 1520,
  },
  {
    id: 'local-2',
    name: '喜鹊',
    scientificName: 'Pica pica',
    region: '全国广泛分布',
    behavior: '留鸟，常成对或小群活动',
    description: '喜鹊黑白分明，尾羽较长，叫声响亮，是很多人熟悉的城市鸟类。',
    imageUrl: '',
    searchCount: 1280,
  },
  {
    id: 'local-3',
    name: '翠鸟',
    scientificName: 'Alcedo atthis',
    region: '南方水域常见',
    behavior: '栖息于水边，俯冲捕鱼',
    description: '翠鸟羽色鲜亮，常停在水边枝条上等待小鱼靠近。',
    imageUrl: '',
    searchCount: 620,
  },
]

const activeList = computed(() => keyword.value ? searchResults.value : cards.value)
const currentBird = computed(() => cards.value[currentIndex.value])
const progressPercent = computed(() => {
  if (!cards.value.length) return 0
  return ((currentIndex.value + 1) / cards.value.length) * 100
})

function normalizeBird(raw) {
  const region = raw.region || ''
  const habits = raw.habits || raw.behavior || ''
  return {
    id: raw.id,
    name: raw.name || '未知鸟类',
    scientificName: raw.latin_name || raw.scientificName || '',
    region,
    distribution: region,
    behavior: habits,
    description: raw.description || '',
    imageUrl: raw.image_url || raw.imageUrl || '',
    searchCount: raw.search_count ?? raw.searchCount ?? 0,
    conservationStatus: raw.conservationStatus || '常见记录',
    tags: [region, habits].filter(Boolean).slice(0, 3),
  }
}

function getBirdImage(bird) {
  if (!bird.imageUrl) return placeholderImage()
  return getOSSUrl(bird.imageUrl, 'medium')
}

function placeholderImage() {
  return 'data:image/svg+xml,' + encodeURIComponent('<svg width="300" height="220" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="220" fill="#ecfdf5"/><text x="150" y="116" text-anchor="middle" fill="#047857" font-size="18" font-family="Arial">暂无图片</text></svg>')
}

function onTileImageError(event) {
  event.target.src = placeholderImage()
}

async function loadInitialBirds() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await BirdApiService.getRankings(50)
    const birds = res.data?.data || []
    cards.value = birds.length ? birds.map(normalizeBird) : fallbackBirds.map(normalizeBird)
  } catch (err) {
    cards.value = fallbackBirds.map(normalizeBird)
    errorMsg.value = ''
  } finally {
    loading.value = false
  }
}

async function searchBirds() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await BirdApiService.searchBirds(keyword.value, 1, 30)
    const birds = (res.data?.data?.birds || []).map(normalizeBird)
    if (keyword.value) {
      searchResults.value = birds
    } else {
      cards.value = birds.length ? birds : cards.value
      searchResults.value = []
    }
  } catch (err) {
    if (!keyword.value) {
      searchResults.value = []
      return
    }
    const lower = keyword.value.toLowerCase()
    searchResults.value = cards.value.filter((bird) =>
      [bird.name, bird.scientificName, bird.region, bird.behavior, bird.description]
        .some((value) => String(value || '').toLowerCase().includes(lower))
    )
  } finally {
    loading.value = false
  }
}

function handleInput() {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(searchBirds, 300)
}

function clearSearch() {
  keyword.value = ''
  searchResults.value = []
  searchBirds()
}

function useQuickTag(tag) {
  keyword.value = tag
  searchBirds()
}

function openBird(bird) {
  const index = cards.value.findIndex((item) => item.id === bird.id)
  if (index >= 0) {
    currentIndex.value = index
  } else {
    cards.value = [bird, ...cards.value]
    currentIndex.value = 0
  }
  mode.value = 'cards'
}

function toggleMode() {
  mode.value = mode.value === 'search' ? 'cards' : 'search'
  vibrate('short')
}

function previousCard() {
  if (currentIndex.value > 0) currentIndex.value -= 1
}

function nextCard() {
  if (currentIndex.value < cards.value.length - 1) currentIndex.value += 1
}

function onTouchStart(event) {
  touchStartX.value = event.touches[0].clientX
}

function onTouchEnd(event) {
  const delta = event.changedTouches[0].clientX - touchStartX.value
  if (Math.abs(delta) < 60) return
  if (delta < 0) nextCard()
  else previousCard()
}

function onLike() {
  showToast('已收藏到本地偏好', 'success')
}

onMounted(loadInitialBirds)
</script>

<style scoped>
.encyclopedia-page {
  width: min(1120px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 22px 20px 96px;
}

.page-header {
  display: grid;
  grid-template-columns: 48px 1fr auto;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.back-btn,
.mode-btn {
  height: 40px;
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.back-btn {
  font-size: 28px;
  line-height: 1;
}

.mode-btn {
  padding: 0 16px;
  font-weight: 700;
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 28px;
  color: var(--color-text);
}

.page-header p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.search-panel {
  margin-bottom: 18px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  height: 52px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.search-box span {
  color: var(--color-primary);
  font-size: 24px;
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: 0;
  background: transparent;
  font-size: 15px;
  color: var(--color-text);
}

.search-box button,
.quick-tags button {
  color: var(--color-primary);
  background: var(--color-primary-bg);
  border-radius: var(--radius-full);
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 18px 0 12px;
}

.section-head h2 {
  margin: 0;
  font-size: 18px;
}

.section-head span {
  color: var(--color-text-muted);
  font-size: 13px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.bird-tile {
  overflow: hidden;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.bird-tile:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.bird-tile img {
  width: 100%;
  height: 170px;
  object-fit: cover;
  background: var(--color-primary-bg);
}

.tile-body {
  padding: 14px;
}

.tile-body h3 {
  margin: 0 0 3px;
  font-size: 17px;
}

.latin {
  margin: 0 0 8px;
  color: var(--color-text-muted);
  font-size: 12px;
  font-style: italic;
}

.tile-body p:not(.latin) {
  display: -webkit-box;
  min-height: 40px;
  margin: 0;
  overflow: hidden;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.tile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.tile-tags span {
  padding: 4px 8px;
  border-radius: var(--radius-full);
  background: var(--color-primary-bg);
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 700;
}

.result-skeleton {
  height: 292px;
}

.state-box {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 240px;
  padding: 32px;
  text-align: center;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.state-box p {
  margin: 0;
  color: var(--color-text-secondary);
}

.card-section {
  display: grid;
  gap: 14px;
}

.card-toolbar {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 14px;
  color: var(--color-text-secondary);
}

.card-toolbar strong {
  color: var(--color-primary);
  font-size: 20px;
}

.progress {
  height: 6px;
  overflow: hidden;
  border-radius: var(--radius-full);
  background: var(--color-border);
}

.progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-primary);
  transition: width var(--transition-normal);
}

.card-stage {
  height: min(680px, calc(100vh - 260px));
  min-height: 520px;
}

.card-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.card-actions button {
  height: 44px;
  border-radius: var(--radius-sm);
  color: var(--color-primary);
  background: var(--color-primary-bg);
  font-weight: 800;
}

.card-actions button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .encyclopedia-page {
    padding: 14px 12px 84px;
  }

  .page-header {
    grid-template-columns: 40px 1fr auto;
  }

  .page-header h1 {
    font-size: 22px;
  }

  .page-header p {
    display: none;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .bird-tile {
    display: grid;
    grid-template-columns: 112px 1fr;
  }

  .bird-tile img {
    height: 100%;
    min-height: 142px;
  }

  .card-stage {
    height: calc(100vh - 240px);
    min-height: 480px;
  }
}
</style>
