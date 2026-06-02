<template>
  <div class="map-page">
    <!-- 搜索 -->
    <div class="map-search">
      <div class="search-box">
        <span>🔍</span>
        <input v-model="searchText" placeholder="搜索观鸟地点..." @keyup.enter="handleSearch" />
        <button v-if="searchText" class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </div>

    <!-- 统计 -->
    <div class="stats-strip">
      <div class="stat"><strong>{{ birdLocations.length }}</strong> 观测点</div>
      <div class="stat"><strong>{{ totalSpecies }}</strong> 鸟种</div>
      <div class="stat"><strong>{{ totalObservations }}</strong> 记录</div>
    </div>

    <!-- 地图 -->
    <div class="map-area">
      <div class="map-canvas">
        <div v-for="loc in birdLocations" :key="loc.id" class="marker"
          :style="{ left: ((loc.longitude - 121.4) / 0.13 * 100) + '%', top: ((31.25 - loc.latitude) / 0.05 * 100) + '%' }"
          @click="selectLocation(loc)">
          <div class="marker-dot" :class="categoryClass(loc.category)"></div>
          <span class="marker-label">{{ loc.name }}</span>
        </div>
      </div>
      <div class="map-legend">
        <span class="legend-item"><i class="dot wetland"></i>湿地</span>
        <span class="legend-item"><i class="dot park"></i>公园</span>
        <span class="legend-item"><i class="dot urban"></i>城区</span>
        <span class="legend-item"><i class="dot other"></i>其他</span>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showCard" class="card-overlay" @click.self="showCard = false">
      <div class="detail-card">
        <button class="close-btn" @click="showCard = false">×</button>
        <span class="card-badge">{{ selected.category }}</span>
        <h3>{{ selected.name }}</h3>
        <p class="desc">{{ selected.description }}</p>
        <div v-if="selected.birdStats" class="card-stats">
          <div><strong>{{ selected.birdStats.species }}</strong><span>鸟种</span></div>
          <div><strong>{{ selected.birdStats.observations }}</strong><span>观测</span></div>
          <div><strong>{{ selected.birdStats.rareSpecies }}</strong><span>珍稀</span></div>
        </div>
        <div v-if="selected.commonBirds" class="bird-tags">
          <span v-for="b in selected.commonBirds" :key="b.id" class="tag">{{ b.name }}</span>
        </div>
        <div class="card-actions">
          <button class="btn btn-primary" @click="navigateTo">🧭 导航</button>
          <button class="btn btn-secondary" @click="shareLocation">📤 分享</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from '@/utils/toast.js'
import { getCurrentLocation } from '@/utils/helpers.js'

const searchText = ref('')
const showCard = ref(false)
const selected = ref({})
const currentPos = ref('定位中...')

const birdLocations = ref([
  { id: 1, name: '嘉定紫藤园', category: '湿地公园', latitude: 31.2354, longitude: 121.4617, description: '上海市著名观鸟地点，拥有丰富的湿地生态系统，园内有专门的观鸟平台。', birdStats: { species: 42, observations: 186, rareSpecies: 3 }, commonBirds: [{ id: 1, name: '白鹭' }, { id: 2, name: '夜鹭' }, { id: 3, name: '小䴙䴘' }, { id: 4, name: '绿头鸭' }] },
  { id: 2, name: '新城公园', category: '城市公园', latitude: 31.2404, longitude: 121.4837, description: '市区内难得的鸟类栖息地，常见麻雀、白头鹎、乌鸫等鸟类。', birdStats: { species: 18, observations: 94, rareSpecies: 0 }, commonBirds: [{ id: 5, name: '白头鹎' }, { id: 6, name: '麻雀' }, { id: 7, name: '乌鸫' }] },
  { id: 3, name: '环城河绿带', category: '河流湿地', latitude: 31.2284, longitude: 121.4527, description: '沿线有大量水生植物，是多种水鸟的栖息地。', birdStats: { species: 26, observations: 132, rareSpecies: 1 }, commonBirds: [{ id: 8, name: '白鹭' }, { id: 9, name: '翠鸟' }] },
  { id: 4, name: '梦花湖', category: '湖泊湿地', latitude: 31.2454, longitude: 121.4557, description: '人工湖泊，周围植被茂盛，是多种水鸟和涉禽的栖息地。', birdStats: { species: 35, observations: 158, rareSpecies: 2 }, commonBirds: [{ id: 10, name: '苍鹭' }, { id: 11, name: '赤膀鸭' }] },
  { id: 5, name: '嘉宝花园', category: '居民区', latitude: 31.2234, longitude: 121.4637, description: '绿化良好，吸引多种小型鸟类筑巢，可观察到柳莺、绣眼鸟等。', birdStats: { species: 13, observations: 67, rareSpecies: 0 }, commonBirds: [{ id: 12, name: '柳莺' }, { id: 13, name: '绣眼鸟' }] },
  { id: 6, name: '填埋场湿地', category: '恢复湿地', latitude: 31.2194, longitude: 121.4867, description: '生态修复后的重要鸟类栖息地，常见猛禽包括红隼、普通鵟。', birdStats: { species: 22, observations: 76, rareSpecies: 2 }, commonBirds: [{ id: 14, name: '红隼' }, { id: 15, name: '普通鵟' }] },
])

const totalSpecies = computed(() => birdLocations.value.reduce((s, l) => s + l.birdStats.species, 0))
const totalObservations = computed(() => birdLocations.value.reduce((s, l) => s + l.birdStats.observations, 0))

const categoryClass = (cat) => ({
  '湿地公园': 'wetland', '湖泊湿地': 'wetland', '河流湿地': 'wetland',
  '城市公园': 'park', '城市绿地': 'park',
  '居民区': 'urban',
}[cat] || 'other')

const selectLocation = (loc) => { selected.value = loc; showCard.value = true }
const handleSearch = () => {
  if (!searchText.value.trim()) return
  const found = birdLocations.value.find(l => l.name.includes(searchText.value))
  if (found) { selectLocation(found); showToast('已找到', 'success') }
  else showToast('未找到', 'none')
}
const navigateTo = () => {
  const l = selected.value
  window.open(`https://uri.amap.com/marker?position=${l.longitude},${l.latitude}&name=${l.name}`, '_blank')
}
const shareLocation = () => {
  if (navigator.share) navigator.share({ title: selected.value.name, text: selected.value.description }).catch(() => {})
  else showToast('已复制链接', 'success')
}

onMounted(async () => {
  try {
    const pos = await getCurrentLocation()
    currentPos.value = `${pos.latitude.toFixed(2)}, ${pos.longitude.toFixed(2)}`
  } catch {}
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
.search-box input { flex: 1; border: none; font-size: 14px; background: transparent; }
.search-btn {
  padding: 6px 16px; background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-full); font-size: 12px; font-weight: 600; cursor: pointer;
}

.stats-strip {
  display: flex; gap: 20px; padding: 12px 16px;
  background: var(--color-surface); border-radius: var(--radius-md);
  border: 1px solid var(--color-border); margin-bottom: 16px;
}
.stats-strip .stat { font-size: 13px; color: var(--color-text-secondary); }
.stats-strip .stat strong { font-size: 18px; color: var(--color-primary); margin-right: 4px; }

.map-area {
  position: relative;
  background: linear-gradient(135deg, #e0f2fe, #dcfce7);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}
.map-canvas { position: relative; height: 460px; }
.marker {
  position: absolute; transform: translate(-50%, -50%);
  cursor: pointer; text-align: center; z-index: 10;
  transition: transform 0.2s;
}
.marker:hover { transform: translate(-50%, -50%) scale(1.3); z-index: 20; }
.marker-dot { width: 14px; height: 14px; border-radius: 50%; margin: 0 auto 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.25); border: 2px solid #fff; }
.marker-dot.wetland { background: #3b82f6; }
.marker-dot.park { background: #22c55e; }
.marker-dot.urban { background: #f59e0b; }
.marker-dot.other { background: #6b7280; }
.marker-label {
  font-size: 10px; color: #1e293b;
  background: rgba(255,255,255,0.9); padding: 2px 6px;
  border-radius: 4px; white-space: nowrap; display: inline-block;
}
.map-legend { position: absolute; top: 12px; right: 12px; background: rgba(255,255,255,0.9); padding: 8px 12px; border-radius: 8px; display: flex; flex-wrap: wrap; gap: 10px; font-size: 11px; }
.legend-item { display: flex; align-items: center; gap: 4px; color: var(--color-text-secondary); }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.wetland { background: #3b82f6; } .dot.park { background: #22c55e; } .dot.urban { background: #f59e0b; } .dot.other { background: #6b7280; }

.card-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 200; display: flex; align-items: flex-end; justify-content: center; }
.detail-card {
  background: var(--color-surface); border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  width: 100%; max-width: 500px; max-height: 70vh; overflow-y: auto;
  padding: 28px 24px 32px; position: relative;
  animation: slideUp 0.3s ease;
  box-shadow: var(--shadow-xl);
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.close-btn { position: absolute; top: 12px; right: 16px; width: 32px; height: 32px; border-radius: 50%; background: var(--color-bg); font-size: 18px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.card-badge { background: var(--color-primary-bg); color: var(--color-primary); font-size: 11px; padding: 3px 10px; border-radius: var(--radius-full); font-weight: 600; }
.detail-card h3 { font-size: 20px; margin: 10px 0 8px; }
.desc { font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 16px; }
.card-stats { display: flex; gap: 20px; padding: 12px; background: var(--color-primary-bg); border-radius: var(--radius-md); margin-bottom: 12px; }
.card-stats div { text-align: center; flex: 1; }
.card-stats strong { display: block; font-size: 20px; color: var(--color-primary); }
.card-stats span { font-size: 11px; color: var(--color-text-secondary); }
.bird-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
.card-actions { display: flex; gap: 10px; }

@media (max-width: 768px) {
  .map-page { padding: 12px; }
  .map-canvas { height: 340px; }
  .stats-strip { gap: 12px; }
}
</style>
