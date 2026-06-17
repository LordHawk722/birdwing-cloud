<template>
  <div class="app-layout">
    <!-- 桌面端侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🦜</span>
        <div class="brand-text">
          <span class="brand-name">众翼云鉴</span>
          <span class="brand-sub">BirdWing Cloud</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <!-- 已登录：显示用户信息 -->
        <div v-if="auth.isAuthenticated.value" class="user-mini" @click="$router.push('/profile')">
          <img
            v-if="auth.user.value?.avatar"
            :src="sidebarAvatar"
            class="user-avatar-img"
            @error="e => e.target.style.display='none'"
          />
          <span v-else class="user-avatar">{{ auth.user.value?.nickname?.charAt(0) || '👤' }}</span>
          <span class="user-name">{{ auth.user.value?.nickname || '用户' }}</span>
        </div>
        <!-- 未登录：显示登录/注册按钮 -->
        <div v-else class="auth-buttons">
          <button class="sidebar-btn sidebar-btn-primary" @click="$router.push('/login')">登录</button>
          <button class="sidebar-btn sidebar-btn-secondary" @click="$router.push('/register')">注册</button>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <!-- 移动端底部导航 -->
    <nav class="mobile-tabbar">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="tabbar-item"
        :class="{ active: isActive(item.path) }"
      >
        <span class="tabbar-icon">{{ item.icon }}</span>
        <span class="tabbar-label">{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { getOSSUrl } from '@/config/oss.js'
import eventBus from '@/utils/eventBus.js'

const route = useRoute()
const auth = useAuthStore()

const sidebarAvatar = computed(() => {
  const a = auth.user.value?.avatar
  if (!a) return ''
  if (a.startsWith('http') || a.startsWith('blob:')) return a
  return getOSSUrl(a, 'avatar')
})

function handleTokenExpired() {
  auth.clearAuth()
}

onMounted(() => {
  eventBus.on('tokenExpired', handleTokenExpired)
})

onUnmounted(() => {
  eventBus.off('tokenExpired', handleTokenExpired)
})

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/map', label: '地图', icon: '🗺️' },
  { path: '/upload', label: '识别', icon: '📤' },
  { path: '/encyclopedia', label: '图鉴', icon: '📚' },
  { path: '/ai-chat', label: 'AI问答', icon: '🤖', badge: 'AI' },
  { path: '/ranking', label: '排行榜', icon: '🏆' },
  { path: '/guide', label: '新手指南', icon: '📖' },
  { path: '/profile', label: '我的', icon: '👤' },
]

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style>
/* ========== 整体布局 ========== */
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ========== 侧边栏 ========== */
.sidebar {
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  padding: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--color-border);
}
.brand-icon { font-size: 28px; }
.brand-text { display: flex; flex-direction: column; }
.brand-name {
  font-size: 15px; font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.5px;
}
.brand-sub {
  font-size: 10px;
  color: var(--color-text-muted);
  font-weight: 500;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: all var(--transition-fast);
  text-decoration: none;
  position: relative;
}
.nav-item:hover {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 20px;
  background: var(--color-primary);
  border-radius: 2px;
}
.nav-icon { font-size: 18px; width: 24px; text-align: center; flex-shrink: 0; }
.nav-label { flex: 1; }
.nav-badge {
  background: var(--color-purple);
  color: #fff;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  font-weight: 700;
}

.sidebar-footer {
  padding: 12px 14px;
  border-top: 1px solid var(--color-border);
}
.user-mini {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.user-mini:hover { background: var(--color-bg); }
.user-avatar {
  width: 32px; height: 32px;
  background: var(--color-primary-bg);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.user-name { font-size: 13px; color: var(--color-text); font-weight: 500; }
.user-avatar-img {
  width: 32px; height: 32px;
  border-radius: 50%; object-fit: cover;
}

/* 未登录按钮 */
.auth-buttons {
  display: flex; flex-direction: column; gap: 6px;
}
.sidebar-btn {
  width: 100%; padding: 8px 0;
  border-radius: var(--radius-sm); border: none;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all var(--transition-fast);
}
.sidebar-btn-primary {
  background: var(--color-primary); color: #fff;
}
.sidebar-btn-primary:hover { background: var(--color-primary-dark); }
.sidebar-btn-secondary {
  background: var(--color-bg); color: var(--color-text); border: 1px solid var(--color-border);
}
.sidebar-btn-secondary:hover { background: var(--color-border); }

/* ========== 主内容区 ========== */
.main-content {
  margin-left: var(--sidebar-width);
  flex: 1;
  min-height: 100vh;
  padding-bottom: 0;
}

/* ========== 移动端底部导航 ========== */
.mobile-tabbar {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 56px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}
.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: all var(--transition-fast);
  font-size: 10px;
}
.tabbar-item.active { color: var(--color-primary); }
.tabbar-icon { font-size: 20px; }

/* ========== 页面过渡 ========== */
.page-enter-active,
.page-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to { opacity: 0; transform: translateY(-8px); }

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main-content {
    margin-left: 0;
    padding-bottom: 56px;
    /* safe area for bottom tabbar */
  }
  .mobile-tabbar {
    display: flex;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  :root { --sidebar-width: 180px; }
  .sidebar { width: var(--sidebar-width); }
  .main-content { margin-left: var(--sidebar-width); }
  .nav-item { padding: 8px 12px; font-size: 13px; }
  .brand-name { font-size: 14px; }
}
</style>
