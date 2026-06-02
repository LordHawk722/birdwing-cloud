<template>
  <div class="tab-bar">
    <div
      v-for="(item, index) in tabList"
      :key="index"
      class="tab-item"
      :class="{ active: currentPath === item.path }"
      @click="switchTab(item.path)"
    >
      <div class="tab-icon-container">
        <span class="tab-icon-fallback">{{ item.fallbackIcon }}</span>
      </div>
      <span class="tab-text">{{ item.text }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { vibrate } from '@/utils/helpers.js'

const router = useRouter()
const route = useRoute()

const currentPath = ref('/')

const tabList = [
  { path: '/', text: '首页', fallbackIcon: '🏠' },
  { path: '/map', text: '地图', fallbackIcon: '🗺️' },
  { path: '/upload', text: '上传', fallbackIcon: '📤' },
  { path: '/profile', text: '我的', fallbackIcon: '👤' }
]

const switchTab = (path) => {
  currentPath.value = path
  vibrate('light')
  router.push(path).catch(() => {})
}

const initCurrentPath = () => {
  const path = route.path
  const matched = tabList.find(tab => tab.path === path)
  if (matched) {
    currentPath.value = matched.path
  }
}

onMounted(() => {
  initCurrentPath()
})
</script>

<style scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  display: flex;
  background-color: #ffffff;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 0;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.tab-item:active {
  transform: scale(0.95);
  background-color: rgba(46, 163, 183, 0.05);
}

.tab-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #2EA3B7;
  border-radius: 1px;
  transition: width 0.3s ease;
}

.tab-item.active::before {
  width: 20px;
}

.tab-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-bottom: 2px;
}

.tab-icon-fallback {
  font-size: 20px;
  line-height: 1;
  transition: all 0.3s ease;
  opacity: 0.7;
}

.tab-item.active .tab-icon-fallback {
  opacity: 1;
  transform: scale(1.1);
}

.tab-text {
  font-size: 10px;
  color: #666;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab-item.active .tab-text {
  color: #2EA3B7;
  font-weight: 600;
}

@media (hover: hover) {
  .tab-item:hover {
    background-color: rgba(46, 163, 183, 0.03);
  }
  .tab-item:hover .tab-text {
    color: #2EA3B7;
  }
}

@supports (bottom: env(safe-area-inset-bottom)) {
  .tab-bar {
    height: calc(50px + env(safe-area-inset-bottom));
  }
}
</style>
