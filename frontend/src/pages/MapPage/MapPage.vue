<template>
  <div class="container">
    <!-- Search Bar -->
    <div class="search-container">
      <div class="search-box">
        <span class="icon-search">🔍</span>
        <input type="text" class="search-input" placeholder="搜索目的地/鸟类名称" v-model="searchText" @keyup.enter="handleSearch" />
        <div class="search-btn" v-if="searchText" @click="handleSearch">
          <span class="search-btn-text">搜索</span>
        </div>
      </div>
    </div>

    <!-- Info Bar -->
    <div class="stats-bar">
      <div class="stat-item"><span class="stat-num">{{ birdLocations.length }}</span><span class="stat-label">观测点</span></div>
      <div class="stat-item"><span class="stat-num">{{ totalSpecies }}</span><span class="stat-label">鸟种</span></div>
      <div class="stat-divider"></div>
      <span class="location-hint" v-if="currentLocation">📍 {{ currentLocation }}</span>
      <span class="location-hint" v-else>📍 定位中...</span>
    </div>

    <!-- Map placeholder (Web version - using a styled representation) -->
    <div class="map-container">
      <div class="map-placeholder">
        <div class="map-grid">
          <div v-for="loc in birdLocations" :key="loc.id" class="map-marker"
            :style="{ left: ((loc.longitude - 121.4) / 0.15 * 100) + '%', top: ((31.25 - loc.latitude) / 0.05 * 100) + '%' }"
            @click="selectLocation(loc)"
          >
            <div class="marker-dot" :class="loc.category === '湿地公园' || loc.category === '湖泊湿地' ? 'marker-blue' : loc.category === '城市公园' || loc.category === '城市绿地' ? 'marker-green' : loc.category === '恢复性湿地' ? 'marker-orange' : 'marker-gray'"></div>
            <span class="marker-label">{{ loc.name }}</span>
          </div>
        </div>
      </div>

      <!-- Control Buttons -->
      <div class="control-buttons">
        <div class="control-btn" @click="moveToCurrentLocation" title="我的位置"><span>📍</span></div>
        <div class="control-btn" @click="zoomIn" title="放大"><span>+</span></div>
        <div class="control-btn" @click="zoomOut" title="缩小"><span>−</span></div>
        <div class="control-btn" @click="switchMapLayer" title="切换图层"><span>🗺️</span></div>
      </div>

      <!-- Legend -->
      <div class="map-legend" v-if="showLegend">
        <div class="legend-header">
          <span class="legend-title">🗺️ 地图图例</span>
          <span class="legend-close" @click="showLegend = false">×</span>
        </div>
        <div class="legend-items">
          <div class="legend-item"><span class="legend-dot marker-blue"></span><span>湿地公园</span></div>
          <div class="legend-item"><span class="legend-dot marker-green"></span><span>城市公园/绿地</span></div>
          <div class="legend-item"><span class="legend-dot marker-orange"></span><span>恢复性湿地</span></div>
          <div class="legend-item"><span class="legend-dot marker-gray"></span><span>居民区</span></div>
        </div>
      </div>
    </div>

    <!-- Info Card -->
    <div class="info-card-overlay" v-if="showInfoCard" @click="closeInfoCard">
      <div class="info-card" @click.stop>
        <div class="info-card-header">
          <button class="info-card-close" @click="closeInfoCard">×</button>
          <div class="info-card-badge">{{ selectedLocation.category }}</div>
        </div>
        <div class="info-card-content">
          <div class="info-card-title">{{ selectedLocation.name }}</div>
          <div class="info-card-description">{{ selectedLocation.description }}</div>

          <div class="bird-stats" v-if="selectedLocation.birdStats">
            <div class="stats-title">📊 观测统计</div>
            <div class="stats-row">
              <div class="stat-item"><span class="stat-value">{{ selectedLocation.birdStats.species }}</span><span class="stat-label">鸟种数量</span></div>
              <div class="stat-item"><span class="stat-value">{{ selectedLocation.birdStats.observations }}</span><span class="stat-label">观测次数</span></div>
              <div class="stat-item"><span class="stat-value">{{ selectedLocation.birdStats.rareSpecies }}</span><span class="stat-label">珍稀鸟种</span></div>
            </div>
          </div>

          <div class="best-time" v-if="selectedLocation.bestTime">
            <div class="time-title">⏰ 最佳观鸟时间</div>
            <div class="time-content">{{ selectedLocation.bestTime }}</div>
          </div>

          <div class="common-birds" v-if="selectedLocation.commonBirds">
            <div class="birds-title">🐦 常见鸟类</div>
            <div class="birds-list">
              <span v-for="bird in selectedLocation.commonBirds" :key="bird.id" class="bird-tag">{{ bird.name }}</span>
            </div>
          </div>

          <div class="action-buttons">
            <button class="action-btn navigate-btn" @click="navigateToLocation">🧭 导航前往</button>
            <button class="action-btn share-btn" @click="shareLocation">📤 分享位置</button>
          </div>
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TabBar from '@/components/TabBar.vue'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'
import { vibrate, getCurrentLocation } from '@/utils/helpers.js'

const searchText = ref('')
const scale = ref(14)
const showInfoCard = ref(false)
const selectedLocation = ref({})
const showLegend = ref(false)
const currentLocation = ref('')
const currentMapLayer = ref('standard')
const isLoading = ref(false)

const birdLocations = ref([
  { id: 1, name: '嘉定紫藤园', category: '湿地公园', latitude: 31.2354, longitude: 121.4617, description: '嘉定紫藤园是上海市著名的观鸟地点，拥有丰富的湿地生态系统。园内有专门的观鸟平台，每年春秋两季是最佳观鸟时间。', birdStats: { species: 42, observations: 186, rareSpecies: 3 }, bestTime: '春秋两季（3-5月，9-11月）清晨5-8点，傍晚4-6点', commonBirds: [{ id: 1, name: '白鹭' }, { id: 2, name: '夜鹭' }, { id: 3, name: '小䴙䴘' }, { id: 4, name: '绿头鸭' }] },
  { id: 2, name: '新城公园', category: '城市公园', latitude: 31.2404, longitude: 121.4837, description: '新城公园是市区内难得的鸟类栖息地，常见麻雀、白头鹎、黑尾蜡嘴雀等鸟类。', birdStats: { species: 18, observations: 94, rareSpecies: 0 }, bestTime: '全年适宜，早晨6-9点最佳', commonBirds: [{ id: 5, name: '白头鹎' }, { id: 6, name: '麻雀' }, { id: 7, name: '乌鸫' }, { id: 8, name: '珠颈斑鸠' }] },
  { id: 3, name: '环城河绿带', category: '河流湿地', latitude: 31.2284, longitude: 121.4527, description: '环城河绿带沿线栽种了大量水生植物，吸引了多种水鸟前来觅食和栖息。', birdStats: { species: 26, observations: 132, rareSpecies: 1 }, bestTime: '春夏季节（4-8月）早晚时分', commonBirds: [{ id: 9, name: '白鹭' }, { id: 10, name: '绿头鸭' }, { id: 11, name: '翠鸟' }, { id: 12, name: '黑水鸡' }] },
  { id: 4, name: '嘉宝花园别墅', category: '居民区', latitude: 31.2234, longitude: 121.4637, description: '嘉宝花园别墅区内绿化良好，可以观察到柳莺、绣眼鸟等小型鸟类。', birdStats: { species: 13, observations: 67, rareSpecies: 0 }, bestTime: '春季（3-5月）清晨时分', commonBirds: [{ id: 13, name: '柳莺' }, { id: 14, name: '绣眼鸟' }, { id: 15, name: '红嘴蓝鹊' }, { id: 16, name: '白头鹎' }] },
  { id: 5, name: '梦花湖', category: '湖泊湿地', latitude: 31.2454, longitude: 121.4557, description: '梦花湖是一个人工湖泊，周围植被茂盛，是多种水鸟和涉禽的栖息地。', birdStats: { species: 35, observations: 158, rareSpecies: 2 }, bestTime: '全年适宜，迁徙季节（春秋）最佳', commonBirds: [{ id: 17, name: '苍鹭' }, { id: 18, name: '小䴙䴘' }, { id: 19, name: '赤膀鸭' }, { id: 20, name: '白骨顶' }] },
  { id: 6, name: '垃圾填埋场湿地', category: '恢复性湿地', latitude: 31.2194, longitude: 121.4867, description: '原垃圾填埋场经生态修复后成为重要鸟类栖息地，常见猛禽包括红隼、普通鵟等。', birdStats: { species: 22, observations: 76, rareSpecies: 2 }, bestTime: '秋冬季节（10-2月）中午时分', commonBirds: [{ id: 21, name: '红隼' }, { id: 22, name: '普通鵟' }, { id: 23, name: '灰伯劳' }, { id: 24, name: '田鹨' }] },
  { id: 7, name: '绿地嘉尚国际广场', category: '城市绿地', latitude: 31.2284, longitude: 121.4987, description: '周边有精心设计的城市绿地，常见鸟类包括珠颈斑鸠、树麻雀、白头鹎等。', birdStats: { species: 16, observations: 83, rareSpecies: 0 }, bestTime: '全年适宜，早晨和傍晚最佳', commonBirds: [{ id: 25, name: '珠颈斑鸠' }, { id: 26, name: '树麻雀' }, { id: 27, name: '白头鹎' }, { id: 28, name: '八哥' }] }
])

const totalSpecies = computed(() => birdLocations.value.reduce((t, l) => t + l.birdStats.species, 0))
const totalObservations = computed(() => birdLocations.value.reduce((t, l) => t + l.birdStats.observations, 0))

const moveToCurrentLocation = async () => {
  vibrate('light')
  try {
    const pos = await getCurrentLocation()
    currentLocation.value = `${pos.latitude.toFixed(4)}, ${pos.longitude.toFixed(4)}`
    scale.value = 16
    showToast('定位成功', 'success', 1500)
  } catch {
    showToast('获取位置失败', 'none')
  }
}

const zoomIn = () => { if (scale.value < 20) { scale.value += 2; vibrate('light') } }
const zoomOut = () => { if (scale.value > 5) { scale.value -= 2; vibrate('light') } }

const switchMapLayer = () => {
  currentMapLayer.value = currentMapLayer.value === 'standard' ? 'satellite' : 'standard'
  vibrate('medium')
  showToast(currentMapLayer.value === 'standard' ? '标准地图' : '卫星地图', 'none', 1000)
}

const handleSearch = () => {
  if (!searchText.value.trim()) { showToast('请输入搜索内容', 'none'); return }
  vibrate('light')
  const results = birdLocations.value.filter(loc => loc.name.includes(searchText.value) || loc.category.includes(searchText.value))
  if (results.length > 0) {
    selectLocation(results[0])
    showToast(`找到${results.length}个相关地点`, 'success')
  } else {
    showToast('未找到相关地点', 'none')
  }
}

const selectLocation = (loc) => {
  selectedLocation.value = loc
  showInfoCard.value = true
  vibrate('medium')
}

const closeInfoCard = () => {
  showInfoCard.value = false
  selectedLocation.value = {}
  vibrate('light')
}

const navigateToLocation = () => {
  const loc = selectedLocation.value
  window.open(`https://uri.amap.com/marker?position=${loc.longitude},${loc.latitude}&name=${loc.name}`, '_blank')
}

const shareLocation = () => {
  const loc = selectedLocation.value
  if (navigator.share) {
    navigator.share({ title: `${loc.name} - 观鸟地点推荐`, text: loc.description, url: window.location.href }).catch(() => {})
  } else {
    showToast('已复制链接', 'success')
  }
}

onMounted(() => {
  moveToCurrentLocation()
  setTimeout(() => { showLegend.value = true; setTimeout(() => showLegend.value = false, 5000) }, 2000)
})
</script>

<style scoped>
.container { position: relative; min-height: 100vh; background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding-bottom: 60px; }
.search-container { padding: 10px 12px; }
.search-box { display: flex; align-items: center; background: white; border-radius: 25px; padding: 8px 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.icon-search { font-size: 16px; margin-right: 8px; color: #64748b; }
.search-input { flex: 1; font-size: 14px; color: #1e293b; border: none; outline: none; background: transparent; }
.search-btn { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 6px 10px; border-radius: 15px; margin-left: 5px; cursor: pointer; }
.search-btn-text { font-size: 12px; color: white; }

.stats-bar { display: flex; align-items: center; gap: 12px; padding: 8px 16px; background: white; margin: 0 12px; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.stat-item { display: flex; align-items: center; gap: 4px; }
.stat-num { font-size: 18px; font-weight: 700; color: #3b82f6; }
.stat-label { font-size: 11px; color: #666; }
.stat-divider { width: 1px; height: 20px; background: #e5e7eb; }
.location-hint { font-size: 11px; color: #666; }

.map-container { position: relative; margin: 10px 12px; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.map-placeholder { height: 420px; background: linear-gradient(135deg, #dbeafe, #bfdbfe); position: relative; overflow: hidden; }
.map-grid { position: relative; width: 100%; height: 100%; }
.map-marker { position: absolute; transform: translate(-50%, -50%); cursor: pointer; text-align: center; z-index: 10; }
.marker-dot { width: 12px; height: 12px; border-radius: 50%; margin: 0 auto 2px; box-shadow: 0 1px 4px rgba(0,0,0,0.3); transition: transform 0.2s ease; }
.map-marker:hover .marker-dot { transform: scale(1.4); }
.marker-blue { background: #3b82f6; }
.marker-green { background: #22c55e; }
.marker-orange { background: #f59e0b; }
.marker-gray { background: #6b7280; }
.marker-label { font-size: 9px; color: #1e293b; background: rgba(255,255,255,0.9); padding: 1px 4px; border-radius: 4px; white-space: nowrap; display: inline-block; }

.control-buttons { position: absolute; right: 8px; bottom: 80px; display: flex; flex-direction: column; gap: 6px; z-index: 20; }
.control-btn { width: 36px; height: 36px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.2s ease; font-size: 16px; }
.control-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.control-btn:active { transform: scale(0.9); }

.map-legend { position: absolute; top: 8px; left: 8px; background: white; border-radius: 8px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 20; max-width: 180px; }
.legend-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.legend-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.legend-close { font-size: 18px; color: #64748b; cursor: pointer; }
.legend-items { display: flex; flex-direction: column; gap: 5px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #475569; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

.info-card-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 100; display: flex; align-items: flex-end; animation: fadeIn 0.2s ease; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.info-card { background: white; border-radius: 16px 16px 0 0; width: 100%; max-height: 70vh; overflow-y: auto; padding: 16px; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.info-card-header { display: flex; justify-content: flex-end; align-items: center; margin-bottom: 8px; }
.info-card-close { width: 28px; height: 28px; background: #e5e7eb; border: none; border-radius: 50%; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.info-card-badge { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px; }
.info-card-title { font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 8px; }
.info-card-description { font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 12px; }
.bird-stats { background: #f0f9ff; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.stats-title { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
.stats-row { display: flex; justify-content: space-between; }
.stats-row .stat-item { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-value { font-size: 18px; font-weight: bold; color: #3b82f6; }
.best-time { background: #fef3c7; border-radius: 8px; padding: 10px; margin-bottom: 12px; }
.time-title { font-size: 12px; font-weight: 600; color: #92400e; margin-bottom: 4px; }
.time-content { font-size: 11px; color: #a16207; line-height: 1.4; }
.common-birds { background: #f0fdf4; border-radius: 8px; padding: 10px; margin-bottom: 12px; }
.birds-title { font-size: 12px; font-weight: 600; color: #166534; margin-bottom: 6px; }
.birds-list { display: flex; flex-wrap: wrap; gap: 5px; }
.bird-tag { background: rgba(34,197,94,0.1); color: #166534; padding: 3px 8px; border-radius: 10px; font-size: 10px; }
.action-buttons { display: flex; gap: 8px; }
.action-btn { flex: 1; height: 40px; border-radius: 20px; border: none; font-size: 13px; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; gap: 4px; }
.action-btn:active { transform: scale(0.95); }
.navigate-btn { background: linear-gradient(135deg, #22c55e, #16a34a); color: white; }
.share-btn { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; }
</style>
