import { createRouter, createWebHistory } from 'vue-router'

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
    meta: { title: '上传图片' }
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
    meta: { title: '我的' }
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
    path: '/encyclopedia',
    name: 'BirdEncyclopedia',
    component: () => import('@/pages/BirdEncyclopedia/BirdEncyclopedia.vue'),
    meta: { title: '图鉴' }
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

// 全局路由守卫：更新页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 众翼云鉴` : '众翼云鉴 - 智能鸟类摄享平台'
  next()
})

export default router
