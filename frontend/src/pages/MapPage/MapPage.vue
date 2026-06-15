<template>
  <div class="map-page">
    <!-- 搜索 -->
    <div class="map-search">
      <div class="search-box">
        <span>🔍</span>
        <input v-model="searchText" placeholder="搜索观鸟地点..." @input="filterMarkers" />
      </div>
    </div>

    <!-- 统计 -->
    <div class="stats-strip">
      <div class="stat"><strong>{{ locations.length }}</strong> 观测点</div>
      <div class="stat"><strong>{{ totalPosts }}</strong> 帖子</div>
    </div>

    <!-- 地图 -->
    <div class="map-area">
      <div ref="mapContainer" class="baidu-map"></div>
      <div v-if="!mapReady" class="map-loading">
        <div class="loading-spinner"></div>
        <span>地图加载中...</span>
      </div>
    </div>

    <!-- 详情面板 -->
    <div v-if="selectedLoc" class="info-panel">
      <div class="info-header">
        <h3>{{ selectedLoc.name }}</h3>
        <button class="close-btn" @click="selectedLoc = null">×</button>
      </div>
      <div class="info-stat">
        <strong>{{ selectedLoc.count }}</strong> 篇帖子
      </div>
      <div class="info-actions">
        <button class="btn btn-primary" @click="viewPosts(selectedLoc.name)">查看相关帖子</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from '@/utils/toast.js'
import PostService from '@/api/services/post.js'

const router = useRouter()

const BAIDU_MAP_KEY = import.meta.env.VITE_BAIDU_MAP_API_KEY || ''

const searchText = ref('')
const mapContainer = ref(null)
const mapReady = ref(false)
const locations = ref([])
const selectedLoc = ref(null)
const allMarkers = ref([])

let mapInstance = null

const totalPosts = computed(() => locations.value.reduce((s, l) => s + l.count, 0))

function loadBaiduScript() {
  return new Promise((resolve, reject) => {
    if (window.BMap) { resolve(); return }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${BAIDU_MAP_KEY}&callback=onBaiduMapReady`
    window.onBaiduMapReady = () => { resolve() }
    script.onerror = () => reject(new Error('百度地图加载失败'))
    document.head.appendChild(script)
  })
}

function initMap() {
  mapInstance = new BMap.Map(mapContainer.value)
  mapInstance.centerAndZoom(new BMap.Point(121.47, 31.23), 12)
  mapInstance.enableScrollWheelZoom(true)
  mapInstance.addControl(new BMap.NavigationControl())
  mapReady.value = true
}

function geocode(locationName) {
  return new Promise((resolve) => {
    const geocoder = new BMap.Geocoder()
    geocoder.getPoint(locationName, function (point) {
      resolve(point)
    }, '上海市')
  })
}

function getMarkerSize(count) {
  return Math.max(10, Math.min(50, 10 + count * 4))
}

function addMarker(point, loc) {
  const size = getMarkerSize(loc.count)

  // 自定义覆盖物：圆点+标签
  function CircleMarker(center, size, locData) {
    this._center = center
    this._size = size
    this._locData = locData
  }
  CircleMarker.prototype = new BMap.Overlay()
  CircleMarker.prototype.initialize = function (map) {
    this._map = map
    const div = document.createElement('div')
    div.style.cssText = `
      position:absolute;width:${size}px;height:${size}px;
      background:rgba(5,150,105,0.7);border:2px solid #fff;
      border-radius:50%;cursor:pointer;transform:translate(-50%,-50%);
      box-shadow:0 2px 8px rgba(0,0,0,0.3);
      display:flex;align-items:center;justify-content:center;
      color:#fff;font-size:${Math.max(10, size / 3)}px;font-weight:700;
      transition:transform 0.2s;
    `
    div.textContent = this._locData.count
    div.onmouseenter = () => { div.style.transform = 'translate(-50%,-50%) scale(1.2)' }
    div.onmouseleave = () => { div.style.transform = 'translate(-50%,-50%)' }
    div.onclick = (e) => {
      e.stopPropagation()
      showInfoWindow(this._center, this._locData)
    }
    map.getPanes().markerPane.appendChild(div)
    this._div = div
    return div
  }
  CircleMarker.prototype.draw = function () {
    const pos = this._map.pointToOverlayPixel(this._center)
    this._div.style.left = pos.x + 'px'
    this._div.style.top = pos.y + 'px'
  }

  const marker = new CircleMarker(point, size, loc)
  mapInstance.addOverlay(marker)
  allMarkers.value.push({ marker, loc, point })
}

function showInfoWindow(point, loc) {
  selectedLoc.value = loc
  mapInstance.panTo(point)
}

function filterMarkers() {
  const kw = searchText.value.trim().toLowerCase()
  allMarkers.value.forEach(({ marker, loc }) => {
    const match = !kw || loc.name.toLowerCase().includes(kw)
    marker._div && (marker._div.style.display = match ? '' : 'none')
  })
}

function viewPosts(locationName) {
  selectedLoc.value = null
  router.push({ path: '/location-posts', query: { name: locationName } })
}

async function loadLocations() {
  try {
    const res = await PostService.getLocations()
    locations.value = res.data?.data || []
    if (locations.value.length === 0) {
      showToast('暂无位置数据', 'none')
      return
    }
    let geocoded = 0
    for (const loc of locations.value) {
      const point = await geocode(loc.name)
      if (point) { addMarker(point, loc); geocoded++ }
    }
    if (geocoded === 0) showToast('位置解析失败，请检查地图服务', 'error')
  } catch (e) {
    console.error('loadLocations error:', e)
    showToast('加载位置数据失败', 'error')
  }
}

onMounted(async () => {
  try {
    await loadBaiduScript()
    initMap()
    await loadLocations()
  } catch (e) {
    console.error('Map init failed:', e)
    showToast('地图初始化失败', 'error')
  }
})

onUnmounted(() => {
  mapInstance = null
  allMarkers.value = []
  delete window.onBaiduMapReady
})
</script>

<style scoped>
.map-page { max-width: 1100px; margin: 0 auto; padding: 20px; }

.map-search { margin-bottom: 12px; }
.search-box {
  display: flex; align-items: center; gap: 10px;
  background: var(--color-surface); padding: 8px 16px;
  border-radius: var(--radius-full); border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
.search-box input { flex: 1; border: none; font-size: 14px; background: transparent; outline: none; }

.stats-strip {
  display: flex; gap: 20px; padding: 12px 16px;
  background: var(--color-surface); border-radius: var(--radius-md);
  border: 1px solid var(--color-border); margin-bottom: 16px;
}
.stats-strip .stat { font-size: 13px; color: var(--color-text-secondary); }
.stats-strip .stat strong { font-size: 18px; color: var(--color-primary); margin-right: 4px; }

.map-area {
  position: relative;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}
.baidu-map { width: 100%; height: 500px; }
.map-loading {
  position: absolute; inset: 0; background: rgba(255,255,255,0.8);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;
  z-index: 100; font-size: 14px; color: var(--color-text-secondary);
}
.loading-spinner {
  width: 28px; height: 28px;
  border: 3px solid var(--color-border); border-top-color: var(--color-primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.info-panel {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 200;
  background: var(--color-surface); border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  padding: 24px; box-shadow: var(--shadow-xl);
  animation: slideUp 0.3s ease;
  max-width: 500px; margin: 0 auto;
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.info-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.info-header h3 { font-size: 20px; }
.close-btn { width: 32px; height: 32px; border-radius: 50%; background: var(--color-bg); border: none; font-size: 18px; cursor: pointer; }
.info-stat { text-align: center; padding: 16px; background: var(--color-primary-bg); border-radius: var(--radius-md); margin-bottom: 16px; }
.info-stat strong { font-size: 28px; color: var(--color-primary); display: block; }
.info-actions { text-align: center; }

@media (max-width: 768px) {
  .map-page { padding: 12px; }
  .baidu-map { height: 380px; }
}
</style>
