<template>
  <div class="homepage-container">
    <!-- 顶部轮播Banner -->
    <div class="banner-section">
      <div class="banner-swiper" @mouseenter="pauseSwiper" @mouseleave="resumeSwiper">
        <div
          v-for="(banner, index) in bannerList"
          :key="index"
          class="swiper-item"
          :class="{ active: currentBannerIndex === index }"
        >
          <img :src="getOSSUrl(banner.imageUrl, 'banner')" class="banner-image" alt="banner" />
          <div class="banner-overlay">
            <div class="banner-content">
              <span class="banner-title">{{ banner.title }}</span>
              <span class="banner-subtitle">{{ banner.subtitle }}</span>
            </div>
          </div>
        </div>
        <div class="swiper-dots">
          <span
            v-for="(_, i) in bannerList"
            :key="i"
            class="swiper-dot"
            :class="{ active: i === currentBannerIndex }"
            @click="goToSlide(i)"
          ></span>
        </div>
      </div>
    </div>

    <!-- 搜索和导航区域 -->
    <div class="search-nav-section">
      <div class="search-wrapper">
        <div class="search-input-container">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            placeholder="搜索鸟类名称..."
            v-model="searchText"
            @input="onSearch"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
            class="search-input"
          />
        </div>
        <div class="search-btn" :class="{ 'search-btn-active': isSearchFocused }" @click="handleSearch">
          <span class="search-btn-icon">→</span>
        </div>
      </div>

      <div class="nav-actions">
        <router-link to="/ranking" class="action-btn ranking-btn">
          <div class="action-icon-wrapper"><span class="action-icon">🏆</span></div>
          <span class="action-text">排行榜</span>
        </router-link>
        <router-link to="/guide" class="action-btn guide-btn">
          <div class="action-icon-wrapper"><span class="action-icon">📖</span></div>
          <span class="action-text">引导</span>
        </router-link>
        <router-link to="/encyclopedia" class="action-btn encyclopedia-btn">
          <div class="action-icon-wrapper"><span class="action-icon">📚</span></div>
          <span class="action-text">鸟类图鉴</span>
        </router-link>
        <router-link to="/ai-chat" class="action-btn ai-chat-btn">
          <div class="action-icon-wrapper"><span class="action-icon">🤖</span></div>
          <span class="action-text">智能助手</span>
        </router-link>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <span class="loading-text">加载中...</span>
      </div>

      <div v-else class="waterfall-container">
        <div class="waterfall-column left-column">
          <div v-for="(poster, index) in leftColumn" :key="poster.id" class="poster-wrapper" :style="{ animationDelay: `${index * 0.1}s` }">
            <EnhancedPoster :poster-data="poster" @like="onLike" @view="onView" />
          </div>
        </div>
        <div class="waterfall-column right-column">
          <div v-for="(poster, index) in rightColumn" :key="poster.id" class="poster-wrapper" :style="{ animationDelay: `${(index + 1) * 0.1}s` }">
            <EnhancedPoster :poster-data="poster" @like="onLike" @view="onView" />
          </div>
        </div>
      </div>

      <div v-if="!isLoading && posterList.length === 0" class="empty-state">
        <span class="empty-icon">🐦</span>
        <span class="empty-text">暂无鸟类记录</span>
        <span class="empty-subtitle">快去记录你的第一次发现吧！</span>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TabBar from '@/components/TabBar.vue'
import EnhancedPoster from '@/components/EnhancedPoster.vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'
import { vibrate } from '@/utils/helpers.js'

const router = useRouter()

const searchText = ref('')
const isSearchFocused = ref(false)
const isLoading = ref(true)
const posterList = ref([])
const leftColumn = ref([])
const rightColumn = ref([])
const currentBannerIndex = ref(0)
let swiperTimer = null

const bannerList = ref([
  { imageUrl: 'static/banner/toucan-banner.jpg', title: '发现自然之美', subtitle: '记录每一次与鸟类的美妙邂逅' },
  { imageUrl: 'static/banner/eagle-banner.jpg', title: '翱翔天际', subtitle: '见证猛禽的威武与优雅' },
  { imageUrl: 'static/banner/peacock-banner.jpg', title: '绚烂羽翼', subtitle: '感受大自然的色彩魅力' },
  { imageUrl: 'static/banner/hummingbird-banner.jpg', title: '精灵悬停', subtitle: '捕捉蜂鸟的瞬间之美' }
])

const mockData = [
  { id: 1, imageUrl: 'static/posts/bird1.jpg', imageHeight: 200, description: '今天在公园拍到的小鸟，真的太可爱了！', views: 1223, likes: 12, author: { name: '鸟类爱好者', avatar: 'static/avatars/user1.png' }, location: '北京·朝阳公园', publishTime: '2小时前' },
  { id: 2, imageUrl: 'static/posts/bird2.jpg', imageHeight: 280, description: '清晨6点，记录到了珍贵的候鸟迁徙场景', views: 25678, likes: 1892, author: { name: '自然摄影师', avatar: 'static/avatars/user2.png' }, location: '上海·世纪公园', publishTime: '5小时前' },
  { id: 3, imageUrl: 'static/posts/bird3.jpg', imageHeight: 220, description: '蜂鸟悬停采蜜的瞬间，大自然的精灵', views: 5432, likes: 234, author: { name: '野生动物保护者', avatar: 'static/avatars/user3.png' }, location: '云南·西双版纳', publishTime: '1天前' },
  { id: 4, imageUrl: 'static/posts/bird4.jpg', imageHeight: 300, description: '金刚鹦鹉的绚烂色彩，热带雨林的瑰宝', views: 8765, likes: 456, author: { name: '生态研究员', avatar: 'static/avatars/user4.jpg' }, location: '海南·亚龙湾', publishTime: '2天前' }
]

const startSwiper = () => {
  swiperTimer = setInterval(() => {
    currentBannerIndex.value = (currentBannerIndex.value + 1) % bannerList.value.length
  }, 4000)
}
const pauseSwiper = () => { if (swiperTimer) clearInterval(swiperTimer) }
const resumeSwiper = () => startSwiper()
const goToSlide = (index) => { currentBannerIndex.value = index; resumeSwiper() }

const onSearch = () => {
  if (searchText.value.trim()) {
    searchBirds(searchText.value)
  } else {
    resetPosterList()
  }
}
const onSearchFocus = () => { isSearchFocused.value = true }
const onSearchBlur = () => { isSearchFocused.value = false }

const handleSearch = () => {
  if (searchText.value.trim()) {
    searchBirds(searchText.value)
    vibrate('short')
  }
}

const onLike = (posterData) => {
  const poster = posterList.value.find(p => p.id === posterData.id)
  if (poster) {
    poster.likes += 1
    redistributePosters()
    showToast('点赞成功', 'success', 1000)
  }
}

const onView = (posterData) => {
  const poster = posterList.value.find(p => p.id === posterData.id)
  if (poster) poster.views += 1
}

const searchBirds = async (keyword) => {
  isLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    const filteredData = mockData.filter(item => item.description.includes(keyword) || item.location.includes(keyword))
    posterList.value = filteredData
    redistributePosters()
  } catch (error) {
    showToast('搜索失败，请重试', 'error')
  } finally {
    isLoading.value = false
  }
}

const resetPosterList = () => {
  posterList.value = [...mockData]
  redistributePosters()
}

const redistributePosters = () => {
  leftColumn.value = []
  rightColumn.value = []
  let leftHeight = 0, rightHeight = 0
  posterList.value.forEach(poster => {
    const estimatedHeight = poster.imageHeight + 120
    if (leftHeight <= rightHeight) {
      leftColumn.value.push(poster)
      leftHeight += estimatedHeight
    } else {
      rightColumn.value.push(poster)
      rightHeight += estimatedHeight
    }
  })
}

onMounted(async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    posterList.value = mockData.map(item => ({
      ...item,
      imageUrl: getOSSUrl(item.imageUrl, 'post-thumb'),
      author: { ...item.author, avatar: getOSSUrl(item.author.avatar, 'avatar') }
    }))
    redistributePosters()
    startSwiper()
  } catch (error) {
    showToast('加载失败，请重试', 'error')
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.homepage-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f9f0 0%, #ffffff 100%);
  padding-bottom: 60px;
}
.banner-section { position: relative; height: 120px; width: 100%; overflow: hidden; border-radius: 0 0 16px 16px; box-shadow: 0 4px 16px rgba(76,175,80,0.15); }
.banner-swiper { width: 100%; height: 100%; position: relative; }
.swiper-item { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; transition: opacity 0.6s ease; }
.swiper-item.active { opacity: 1; }
.banner-image { width: 100%; height: 100%; object-fit: cover; }
.banner-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(76,175,80,0.7) 0%, rgba(67,160,71,0.8) 100%); display: flex; align-items: center; justify-content: center; }
.banner-content { text-align: center; color: white; }
.banner-title { display: block; font-size: 18px; font-weight: 700; margin-bottom: 4px; text-shadow: 0 1px 4px rgba(0,0,0,0.3); }
.banner-subtitle { display: block; font-size: 12px; opacity: 0.9; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }
.swiper-dots { position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%); display: flex; gap: 6px; z-index: 5; }
.swiper-dot { width: 6px; height: 6px; border-radius: 50%; background: rgba(255,255,255,0.5); cursor: pointer; transition: all 0.3s ease; }
.swiper-dot.active { background: #fff; width: 18px; border-radius: 3px; }

.search-nav-section { padding: 12px 16px; background: white; border-radius: 16px 16px 0 0; margin-top: -8px; position: relative; z-index: 10; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }
.search-wrapper { display: flex; align-items: center; margin-bottom: 12px; gap: 8px; }
.search-input-container { flex: 1; height: 40px; background: #f8f9fa; border-radius: 20px; display: flex; align-items: center; padding: 0 12px; border: 1px solid transparent; transition: all 0.3s ease; }
.search-input-container:focus-within { border-color: #4caf50; background: white; box-shadow: 0 0 0 4px rgba(76,175,80,0.1); }
.search-icon { font-size: 16px; margin-right: 8px; opacity: 0.6; }
.search-input { flex: 1; height: 100%; font-size: 14px; color: #333; background: transparent; border: none; outline: none; }
.search-btn { width: 40px; height: 40px; background: linear-gradient(135deg, #4caf50, #43a047); border-radius: 20px; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(76,175,80,0.3); cursor: pointer; }
.search-btn:active { transform: scale(0.95); }
.search-btn-active { background: linear-gradient(135deg, #43a047, #388e3c); box-shadow: 0 3px 10px rgba(76,175,80,0.4); }
.search-btn-icon { font-size: 18px; color: white; }

.nav-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.action-btn { height: 48px; background: linear-gradient(135deg, #e8f5e8, #f1f8e9); border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; border: 1px solid rgba(76,175,80,0.1); transition: all 0.3s ease; text-decoration: none; cursor: pointer; }
.action-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(76,175,80,0.15); border-color: rgba(76,175,80,0.2); }
.action-icon-wrapper { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; background: rgba(76,175,80,0.1); border-radius: 12px; }
.action-icon { font-size: 14px; }
.action-text { font-size: 12px; color: #4caf50; font-weight: 600; }
.encyclopedia-btn { background: linear-gradient(135deg, #e3f2fd, #f0f8ff); border-color: rgba(33,150,243,0.1); }
.encyclopedia-btn .action-icon-wrapper { background: rgba(33,150,243,0.1); }
.encyclopedia-btn .action-text { color: #2196f3; }
.ai-chat-btn { background: linear-gradient(135deg, #f3e5f5, #fce4ec); border-color: rgba(156,39,176,0.1); }
.ai-chat-btn .action-icon-wrapper { background: rgba(156,39,176,0.1); }
.ai-chat-btn .action-text { color: #9c27b0; }

.content-section { padding: 0 12px 30px; min-height: 60vh; }
.loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 0; }
.loading-spinner { width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top-color: #4caf50; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 14px; color: #666; }
.waterfall-container { display: flex; gap: 8px; align-items: flex-start; }
.waterfall-column { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.poster-wrapper { animation: slideInUp 0.6s ease both; }
@keyframes slideInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; text-align: center; }
.empty-icon { font-size: 80px; margin-bottom: 16px; opacity: 0.6; }
.empty-text { font-size: 16px; color: #666; font-weight: 600; margin-bottom: 6px; }
.empty-subtitle { font-size: 13px; color: #999; }

@media screen and (max-width: 375px) {
  .banner-section { height: 100px; }
  .banner-title { font-size: 16px; }
  .banner-subtitle { font-size: 11px; }
  .content-section { padding: 0 8px 30px; }
  .action-btn { height: 44px; }
  .action-text { font-size: 11px; }
}
</style>
