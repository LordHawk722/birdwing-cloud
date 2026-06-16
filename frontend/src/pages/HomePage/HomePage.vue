<template>
  <div class="home">
    <!-- Hero Banner：占满宽度，深色氛围 -->
    <section class="hero">
      <div class="hero-slides">
        <div v-for="(banner, i) in bannerList" :key="i" class="hero-slide" :class="{ active: currentBanner === i }">
          <div class="hero-bg" :style="{ backgroundImage: `url(${banner.imageUrl})` }"></div>
          <div class="hero-overlay"></div>
        </div>
      </div>
      <div class="hero-text">
        <h1>{{ bannerList[currentBanner].title }}</h1>
        <p>{{ bannerList[currentBanner].subtitle }}</p>
      </div>
      <div class="hero-dots">
        <button v-for="(_, i) in bannerList" :key="i" class="dot" :class="{ active: currentBanner === i }" @click="goToSlide(i)"></button>
      </div>
    </section>

    <!-- 搜索栏：悬浮在 Hero 底部 -->
    <div class="search-strip">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input v-model="searchText" placeholder="搜索鸟类名称、特征、栖息地..." @input="onSearchInput" @keyup.enter="handleSearch" />
        <button v-if="searchText" class="search-clr" @click="searchText='';resetPosters()">×</button>
        <button class="search-go" @click="handleSearch">搜索</button>
      </div>
    </div>

    <!-- 主体双栏 -->
    <div class="main-layout">
      <!-- 左侧：瀑布流（浅绿背景区） -->
      <section class="feed-section">
        <div class="section-header">
          <div class="section-header-left">
            <h2>📸 社区发现</h2>
            <span class="section-sub">探索鸟友们的最新记录</span>
          </div>
          <button class="create-post-btn" @click="openCreatePost">✚ 发布动态</button>
        </div>

        <div v-if="isLoading" class="loading-zone">
          <div class="skeleton" style="height:200px;"></div>
          <div class="skeleton" style="height:160px;margin-top:12px;"></div>
        </div>

        <div v-else-if="posterList.length > 0" class="masonry">
          <div class="masonry-col">
            <div v-for="p in leftColumn" :key="p.id" class="masonry-item fade-in">
              <EnhancedPoster :poster-data="p" @like="onLike" @view="onView" />
            </div>
          </div>
          <div class="masonry-col">
            <div v-for="p in rightColumn" :key="p.id" class="masonry-item fade-in">
              <EnhancedPoster :poster-data="p" @like="onLike" @view="onView" />
            </div>
          </div>
        </div>

        <div v-else class="empty-zone">
          <span class="empty-icon">🐦</span>
          <h3>还没有鸟类记录</h3>
          <p>快去发现并记录你的第一次邂逅吧</p>
        </div>
      </section>

      <!-- 右侧：信息面板（彩色背景卡片） -->
      <aside class="side-section">
        <!-- 快捷操作 -->
        <div class="quick-group">
          <router-link to="/upload" class="quick-item q-upload">
            <span class="q-icon">📸</span>
            <div class="q-body">
              <strong>上传识别</strong>
              <span>拍照识别鸟类品种</span>
            </div>
            <span class="q-arrow">→</span>
          </router-link>
          <router-link to="/ai-chat" class="quick-item q-chat">
            <span class="q-icon">🤖</span>
            <div class="q-body">
              <strong>AI 问答</strong>
              <span>智能咨询鸟类知识</span>
            </div>
            <span class="q-arrow">→</span>
          </router-link>
          <router-link to="/encyclopedia" class="quick-item q-encyclopedia">
            <span class="q-icon">📚</span>
            <div class="q-body">
              <strong>鸟类图鉴</strong>
              <span>浏览鸟类百科全书</span>
            </div>
            <span class="q-arrow">→</span>
          </router-link>
        </div>

        <!-- 热门排行：暖色背景 -->
        <div class="panel panel-warm">
          <div class="panel-head">
            <h4>🔥 本周热门鸟类</h4>
            <router-link to="/ranking" class="panel-link">完整排行 →</router-link>
          </div>
          <div v-if="rankLoading" class="panel-loading">加载中...</div>
          <div v-else class="hot-rows">
            <div v-for="(bird, i) in hotBirds" :key="bird.id" class="hot-row">
              <span class="hot-idx" :class="{ podium: i < 3 }">{{ i + 1 }}</span>
              <span class="hot-name">{{ bird.name }}</span>
              <span class="hot-val">{{ fmtNum(bird.search_count) }}</span>
            </div>
          </div>
        </div>

        <!-- 观鸟贴士：绿色背景 -->
        <div class="panel panel-tip">
          <div class="tip-header">
            <span class="tip-badge">💡 观鸟小贴士</span>
          </div>
          <p class="tip-body">{{ currentTip }}</p>
          <div class="tip-dots">
            <span v-for="(_, i) in tips" :key="i" class="tip-dot" :class="{ active: tipIndex === i }"></span>
          </div>
        </div>
      </aside>
    </div>

    <CreatePostModal v-model:visible="showCreateModal" @created="loadPosts" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import EnhancedPoster from '@/components/EnhancedPoster.vue'
import CreatePostModal from '@/components/CreatePostModal.vue'

import { showToast } from '@/utils/toast.js'
import BirdApiService from '@/api/services/bird.js'
import PostService from '@/api/services/post.js'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const POSTS_CACHE_KEY = 'homepage_posts_cache'

const searchText = ref('')
const isLoading = ref(true)
const rankLoading = ref(true)
const posterList = ref([])
const allPosters = ref([])
const leftColumn = ref([])
const rightColumn = ref([])
const currentBanner = ref(0)
const tipIndex = ref(0)
const hotBirds = ref([])
let swiperTimer = null
let tipTimer = null
let searchTimer = null

// ---- 发布动态 ----
const showCreateModal = ref(false)

function openCreatePost() {
  if (!auth.isAuthenticated.value) {
    router.push('/login')
    return
  }
  showCreateModal.value = true
}

const tips = [
  '清晨 5-8 点是观鸟的黄金时段，鸟儿们最活跃！',
  '穿灰/绿/棕色衣服更容易接近鸟类，荧光色是大忌！',
  '8×42 望远镜是最适合新手的规格，轻便又清晰。',
  '春、秋两季是候鸟迁徙高峰，湿地公园是好去处。',
  '保持安静、耐心等待，是观鸟最重要的法则。',
]
const currentTip = computed(() => tips[tipIndex.value])

const bannerList = [
  { imageUrl: '/banner/1.jpg', title: '发现自然之美', subtitle: '记录每一次与鸟类的美妙邂逅' },
  { imageUrl: '/banner/2.jpg', title: '翱翔天际', subtitle: '见证猛禽的威武与优雅' },
  { imageUrl: '/banner/3.jpg', title: '绚烂羽翼', subtitle: '感受大自然的色彩魅力' },
  { imageUrl: '/banner/4.jpg', title: '精灵悬停', subtitle: '捕捉蜂鸟的瞬间之美' },
]

function fmtNum(n) {
  if (!n) return '0'
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toLocaleString()
}

/** 将后端帖子数据转为前端组件期望格式 */
function mapPostItem(p) {
  return {
    id: p.id,
    imageUrl: p.images?.length ? p.images[0] : '',
    imageHeight: 200 + Math.floor(Math.random() * 120),
    description: p.title,
    likeCount: p.like_count || 0,
    commentCount: p.comment_count || 0,
    isLiked: p.is_liked || false,
    author: { name: p.author_name || '用户', avatar: p.author_avatar || '' },
    location: p.location || '',
    publishTime: p.created_at || '',
  }
}

async function loadPosts() {
  // 先从缓存加载
  try {
    const cached = sessionStorage.getItem(POSTS_CACHE_KEY)
    if (cached) {
      const parsed = JSON.parse(cached)
      allPosters.value = parsed
      posterList.value = [...allPosters.value]
      distribute()
      isLoading.value = false
    }
  } catch { /* ignore cache errors */ }

  try {
    const res = await PostService.getPostList(1, 20)
    const items = res.data?.data?.items || []
    const mapped = items.map(mapPostItem)
    // 更新缓存
    sessionStorage.setItem(POSTS_CACHE_KEY, JSON.stringify(mapped))
    allPosters.value = mapped
    posterList.value = [...allPosters.value]
    distribute()
  } catch {
    // 静默失败，显示缓存或空状态
  } finally {
    isLoading.value = false
  }
}

async function loadRankings() {
  rankLoading.value = true
  try {
    const res = await BirdApiService.getRankings(5)
    hotBirds.value = res.data?.data || []
  } catch {
    // 静默失败
  } finally {
    rankLoading.value = false
  }
}

const startSwiper = () => { swiperTimer = setInterval(() => { currentBanner.value = (currentBanner.value + 1) % bannerList.length }, 5000) }
const goToSlide = (i) => { currentBanner.value = i; clearInterval(swiperTimer); startSwiper() }

const onSearchInput = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => searchText.value.trim() ? filterPosters(searchText.value) : resetPosters(), 300)
}
const handleSearch = () => { if (searchText.value.trim()) filterPosters(searchText.value) }
const filterPosters = (k) => {
  const kw = k.toLowerCase()
  posterList.value = allPosters.value.filter(p =>
    p.description?.toLowerCase().includes(kw) ||
    p.location?.toLowerCase().includes(kw)
  )
  distribute()
}
const resetPosters = () => { posterList.value = [...allPosters.value]; distribute() }
const onLike = async (p) => {
  try {
    const res = await PostService.toggleLike(p.id)
    const d = res.data?.data
    const x = posterList.value.find(y => y.id === p.id)
    if (x && d) {
      x.isLiked = d.is_liked
      x.likeCount = d.like_count
      distribute()
    }
  } catch (err) {
    if (err?.statusCode === 401) showToast('请先登录', 'none')
  }
}
const onView = (p) => {
  router.push('/post/' + p.id)
}
const distribute = () => {
  leftColumn.value = []; rightColumn.value = []
  let lh = 0, rh = 0
  posterList.value.forEach(p => { const h = (p.imageHeight || 200) + 130; if (lh <= rh) { leftColumn.value.push(p); lh += h } else { rightColumn.value.push(p); rh += h } })
}

onMounted(async () => {
  // 并行加载帖子和排行
  await Promise.all([loadPosts(), loadRankings()])
  startSwiper()
  tipTimer = setInterval(() => { tipIndex.value = (tipIndex.value + 1) % tips.length }, 8000)
})
onUnmounted(() => { clearInterval(swiperTimer); clearInterval(tipTimer) })
</script>

<style scoped>
.home { background: var(--color-bg); }

/* ===== Hero ===== */
.hero {
  position: relative; height: 320px; overflow: hidden;
}
.hero-slide { position: absolute; inset: 0; opacity: 0; transition: opacity 1.2s ease; }
.hero-slide.active { opacity: 1; }
.hero-bg { position: absolute; inset: 0; background-size: contain; background-position: center; background-repeat: no-repeat; background-color: #064e3b; transform: scale(1.05); transition: transform 6s ease; }
.hero-slide.active .hero-bg { transform: scale(1); }
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(5,100,70,0.8) 60%, rgba(2,50,35,0.9) 100%);
}
.hero-text { position: absolute; bottom: 60px; left: 48px; color: #fff; z-index: 2; max-width: 600px; }
.hero-text h1 { font-size: 36px; font-weight: 800; letter-spacing: -1px; margin-bottom: 8px; text-shadow: 0 2px 16px rgba(0,0,0,0.3); }
.hero-text p { font-size: 16px; opacity: 0.85; text-shadow: 0 1px 8px rgba(0,0,0,0.3); }
.hero-dots { position: absolute; bottom: 24px; right: 48px; display: flex; gap: 10px; z-index: 2; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.35); border: none; cursor: pointer; transition: all 0.3s; padding: 0; }
.dot.active { background: #fff; width: 28px; border-radius: 4px; }

/* ===== Search ===== */
.search-strip {
  max-width: 680px; margin: -26px auto 0; padding: 0 20px;
  position: relative; z-index: 10;
}
.search-box {
  display: flex; align-items: center; gap: 0;
  background: #fff; border-radius: 50px; padding: 5px 5px 5px 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.search-icon { opacity: 0.35; font-size: 18px; margin-right: 8px; }
.search-box input {
  flex: 1; border: none; outline: none; font-size: 14px;
  color: var(--color-text); background: transparent; padding: 10px 0;
}
.search-clr { background: none; border: none; font-size: 18px; color: #bbb; cursor: pointer; padding: 6px 8px; }
.search-go {
  padding: 10px 28px; background: var(--color-primary); color: #fff;
  border: none; border-radius: 50px; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.search-go:hover { background: var(--color-primary-dark); }

/* ===== 双栏 ===== */
.main-layout {
  display: flex; gap: 28px;
  max-width: 1200px; margin: 0 auto; padding: 32px 24px 48px;
  align-items: flex-start;
}

/* ===== 左侧 Feed ===== */
.feed-section {
  flex: 1; min-width: 0;
  background: linear-gradient(180deg, #f0fdf4 0%, #f9fafb 100%);
  border-radius: var(--radius-xl);
  padding: 24px 20px;
}
.section-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px;
}
.section-header-left { flex: 1; }
.section-header h2 { font-size: 18px; font-weight: 700; color: var(--color-text); margin-bottom: 4px; }
.section-sub { font-size: 13px; color: var(--color-text-muted); }
.create-post-btn {
  padding: 8px 16px; background: var(--color-primary); color: #fff;
  border: none; border-radius: 20px; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.2s; white-space: nowrap;
}
.create-post-btn:hover { background: var(--color-primary-dark); }
.masonry { display: flex; gap: 14px; align-items: flex-start; }
.masonry-col { flex: 1; display: flex; flex-direction: column; gap: 14px; }
.loading-zone { padding: 10px 0; }
.empty-zone {
  text-align: center; padding: 80px 40px;
}
.empty-icon { font-size: 64px; display: block; margin-bottom: 16px; opacity: 0.4; }
.empty-zone h3 { font-size: 16px; color: var(--color-text); margin-bottom: 6px; }
.empty-zone p { font-size: 13px; color: var(--color-text-muted); }

/* ===== 右侧面板 ===== */
.side-section { width: 290px; flex-shrink: 0; display: flex; flex-direction: column; gap: 16px; }

.quick-group { display: flex; flex-direction: column; gap: 6px; }
.quick-item {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; border-radius: var(--radius-md);
  text-decoration: none; transition: all 0.2s; cursor: pointer;
}
.q-upload { background: linear-gradient(135deg, #ecfdf5, #d1fae5); }
.q-upload:hover { background: linear-gradient(135deg, #d1fae5, #a7f3d0); }
.q-chat { background: linear-gradient(135deg, #f5f3ff, #ede9fe); }
.q-chat:hover { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.q-encyclopedia { background: linear-gradient(135deg, #eff6ff, #dbeafe); }
.q-encyclopedia:hover { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
.q-icon { font-size: 26px; flex-shrink: 0; }
.q-body { flex: 1; min-width: 0; }
.q-body strong { display: block; font-size: 13px; color: var(--color-text); margin-bottom: 2px; }
.q-body span { font-size: 11px; color: var(--color-text-muted); }
.q-arrow { color: var(--color-text-muted); transition: transform 0.2s; }
.quick-item:hover .q-arrow { transform: translateX(4px); }

/* 面板 */
.panel { border-radius: var(--radius-lg); padding: 18px; }
.panel-warm { background: linear-gradient(135deg, #fffbeb, #fef3c7); }
.panel-tip { background: linear-gradient(135deg, #ecfdf5, #d1fae5); }
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-head h4 { font-size: 14px; font-weight: 700; color: #92400e; }
.panel-link { font-size: 11px; color: #b45309; font-weight: 600; text-decoration: none; }
.panel-link:hover { text-decoration: underline; }
.panel-loading { text-align: center; font-size: 13px; color: #78716c; padding: 12px 0; }

.hot-rows { display: flex; flex-direction: column; gap: 2px; }
.hot-row { display: flex; align-items: center; gap: 10px; padding: 7px 10px; border-radius: 6px; transition: background 0.15s; }
.hot-row:hover { background: rgba(255,255,255,0.5); }
.hot-idx { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; background: rgba(0,0,0,0.05); color: #78716c; flex-shrink: 0; }
.hot-idx.podium { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; }
.hot-name { flex: 1; font-size: 13px; color: var(--color-text); font-weight: 500; }
.hot-val { font-size: 11px; color: #78716c; }

.tip-header { margin-bottom: 8px; }
.tip-badge { font-size: 13px; font-weight: 700; color: #065f46; }
.tip-body { font-size: 13px; line-height: 1.6; color: #065f46; margin-bottom: 10px; }
.tip-dots { display: flex; gap: 6px; justify-content: center; }
.tip-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(6,95,70,0.2); transition: all 0.3s; }
.tip-dot.active { background: #065f46; width: 18px; border-radius: 3px; }

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .side-section { display: none; }
}
@media (max-width: 768px) {
  .hero { height: 220px; }
  .hero-text { left: 20px; bottom: 48px; }
  .hero-text h1 { font-size: 24px; }
  .hero-text p { font-size: 13px; }
  .hero-dots { right: 20px; bottom: 18px; }
  .main-layout { padding: 20px 12px 32px; }
  .feed-section { padding: 16px 12px; }
  .section-header { flex-direction: column; gap: 12px; }
  .masonry { gap: 10px; }
  .masonry-col { gap: 10px; }
}

</style>
