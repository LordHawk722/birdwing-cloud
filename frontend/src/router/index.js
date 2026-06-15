import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: () => import('@/pages/HomePage/HomePage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/upload',
    name: 'UploadPage',
    component: () => import('@/pages/UploadPage/UploadPage.vue'),
    meta: { title: '上传图片', requiresAuth: true }
  },
  {
    path: '/map',
    name: 'MapPage',
    component: () => import('@/pages/MapPage/MapPage.vue'),
    meta: { title: '地图' }
  },
  {
    path: '/profile',
    name: 'ProfilePage',
    component: () => import('@/pages/ProfilePage/ProfilePage.vue'),
    meta: { title: '我的', requiresAuth: true }
  },
  {
    path: '/ranking',
    name: 'RankingPage',
    component: () => import('@/pages/RankingPage/RankingPage.vue'),
    meta: { title: '排行榜' }
  },
  {
    path: '/guide',
    name: 'NoobPage',
    component: () => import('@/pages/NoobPage/NoobPage.vue'),
    meta: { title: '新手须知' }
  },
  {
    path: '/ai-chat',
    name: 'AIChat',
    component: () => import('@/pages/AIChat/AIChat.vue'),
    meta: { title: 'AI助理' }
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: () => import('@/pages/PostDetailPage/PostDetailPage.vue'),
    meta: { title: '帖子详情' }
  },
  {
    path: '/encyclopedia',
    name: 'BirdEncyclopedia',
    component: () => import('@/pages/BirdEncyclopedia/BirdEncyclopedia.vue'),
    meta: { title: '图鉴' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/LoginPage/LoginPage.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/RegisterPage/RegisterPage.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 众翼云鉴` : '众翼云鉴 - 智能鸟类摄享平台'

  const auth = useAuthStore()

  // 需要登录的页面 → 未登录则跳转登录页
  if (to.meta.requiresAuth && !auth.isAuthenticated.value) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 已登录用户访问登录/注册页 → 重定向到首页
  if ((to.name === 'Login' || to.name === 'Register') && auth.isAuthenticated.value) {
    next({ name: 'HomePage' })
    return
  }

  next()
})

export default router
