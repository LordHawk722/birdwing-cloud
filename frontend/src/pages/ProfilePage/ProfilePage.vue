<template>
  <div class="profile-container">
    <!-- 顶部个人信息区 -->
    <div class="profile-header">
      <div class="header-content">
        <div class="avatar-section" @click="handleAvatarClick">
          <img :src="userAvatarUrl" class="avatar" alt="头像" @error="handleAvatarError" />
          <div class="edit-hint">点击修改</div>
        </div>
        <div class="user-info">
          <div class="nickname-row">
            <span class="nickname">{{ userInfo.nickname }}</span>
            <span class="edit-icon" @click="handleEditProfile">✏️</span>
          </div>
          <div class="bio" @click="handleEditBio">{{ userInfo.bio || '点击添加个人介绍...' }}</div>
          <div class="stats">
            <div class="stat-item"><span class="stat-num">{{ userInfo.postsCount }}</span><span class="stat-label">发布</span></div>
            <div class="stat-item"><span class="stat-num">{{ userInfo.likesCount }}</span><span class="stat-label">获赞</span></div>
            <div class="stat-item"><span class="stat-num">{{ userInfo.level }}</span><span class="stat-label">等级</span></div>
          </div>
        </div>
      </div>

      <div class="achievements">
        <div v-for="a in achievements" :key="a.id" class="achievement-item">
          <span class="achievement-icon">{{ a.id === 1 ? '🐣' : '📸' }}</span>
          <span class="achievement-name">{{ a.name }}</span>
        </div>
      </div>
    </div>

    <!-- 内容分类标签页 -->
    <div class="content-tabs">
      <div class="tab-item" :class="{ active: activeTab === 'posts' }" @click="switchTab('posts')">历史发布</div>
      <div class="tab-item" :class="{ active: activeTab === 'likes' }" @click="switchTab('likes')">我的点赞</div>
      <div class="tab-item" :class="{ active: activeTab === 'records' }" @click="switchTab('records')">识别记录</div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-else-if="currentContent.length === 0" class="empty-hint">
        <div class="empty-icon">📷</div>
        <span class="empty-text">{{ emptyText }}</span>
      </div>
      <div v-else class="waterfall">
        <div class="column">
          <HomePoster v-for="poster in leftColumn" :key="poster.id" :poster-data="poster" />
        </div>
        <div class="column">
          <HomePoster v-for="poster in rightColumn" :key="poster.id" :poster-data="poster" />
        </div>
      </div>
    </div>

    <TabBar />
  </div>
</template>

<script>
import TabBar from '@/components/TabBar.vue'
import HomePoster from '@/components/HomePoster.vue'
import { UserService } from '@/api/services/user.js'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showEditableModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'

const userService = new UserService()

export default {
  name: 'ProfilePage',
  components: { HomePoster, TabBar },
  data() {
    return {
      isLoading: false,
      activeTab: 'posts',
      userInfo: { avatar: 'static/default-avatar.png', nickname: '鸟类爱好者', bio: '', postsCount: 0, likesCount: 0, level: 1 },
      achievements: [
        { id: 1, name: '初级观鸟员' },
        { id: 2, name: '摄影新手' }
      ],
      posts: [],
      likes: [],
      records: [],
      leftColumn: [],
      rightColumn: []
    }
  },
  computed: {
    currentContent() {
      switch(this.activeTab) {
        case 'posts': return this.posts
        case 'likes': return this.likes
        case 'records': return this.records
        default: return []
      }
    },
    emptyText() {
      const map = { posts: '还没有发布过内容~', likes: '还没有点赞过内容~', records: '还没有识别过哦~' }
      return map[this.activeTab] || '暂无内容'
    },
    userAvatarUrl() {
      const avatar = this.userInfo.avatar || 'static/default-avatar.png'
      if (avatar.startsWith('http') || avatar.startsWith('blob:')) return avatar
      return getOSSUrl(avatar, 'small')
    }
  },
  async mounted() {
    await this.loadUserInfo()
    this.loadContent()
  },
  methods: {
    async loadUserInfo() {
      try {
        const intro = await userService.getIntro()
        this.userInfo.bio = intro || ''
      } catch (error) {
        console.error('Failed to load user info:', error)
      }
    },
    async handleAvatarClick() {
      try {
        const result = await chooseImages({ count: 1 })
        if (result.tempFilePaths.length > 0) {
          this.userInfo.avatar = result.tempFilePaths[0]
          showToast('头像更新成功', 'success')
        }
      } catch (error) {
        showToast('头像上传失败', 'none')
      }
    },
    handleAvatarError() {
      this.userInfo.avatar = 'static/default-avatar.png'
    },
    handleEditProfile() {
      showToast('编辑资料功能开发中', 'none')
    },
    async handleEditBio() {
      const result = await showEditableModal('编辑个人介绍', this.userInfo.bio)
      if (result.confirm) {
        this.userInfo.bio = result.content || '点击添加个人介绍...'
        showToast('更新成功', 'success')
      }
    },
    switchTab(tab) {
      if (this.activeTab !== tab) {
        this.activeTab = tab
        this.loadContent()
      }
    },
    async loadContent() {
      this.isLoading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        let data
        switch(this.activeTab) {
          case 'posts':
            data = [{ id: 1, imageUrl: 'static/posts/bird1.jpg', imageHeight: 200, description: '今天拍到的小鸟', views: 1234, likes: 88 }]
            this.posts = data
            break
          case 'likes':
            data = [{ id: 2, imageUrl: 'static/posts/bird2.jpg', imageHeight: 280, description: '好漂亮的鸟儿！', views: 2567, likes: 189 }]
            this.likes = data
            break
          case 'records':
            data = [
              { id: 3, imageUrl: 'static/recognition/bird1.jpg', imageHeight: 240, description: '识别结果：红头长尾山雀', accuracy: '98%', date: '2024-03-20' },
              { id: 5, imageUrl: 'static/recognition/bird2.jpg', imageHeight: 220, description: '识别结果：白头硬尾鹎', accuracy: '97%', date: '2024-03-18' }
            ]
            this.records = data
            break
        }
        this.distributeContent()
      } catch (error) {
        showToast('加载失败', 'none')
      } finally {
        this.isLoading = false
      }
    },
    distributeContent() {
      this.leftColumn = []
      this.rightColumn = []
      this.currentContent.forEach((item, index) => {
        if (index % 2 === 0) this.leftColumn.push(item)
        else this.rightColumn.push(item)
      })
    }
  }
}
</script>

<style scoped>
.profile-container { min-height: 100vh; background-color: #FFF9E9; padding-bottom: 60px; }
.profile-header { padding: 20px 16px; background: #FFFFFF; border-radius: 0 0 16px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.header-content { display: flex; align-items: flex-start; }
.avatar-section { position: relative; margin-right: 16px; cursor: pointer; }
.avatar { width: 80px; height: 80px; border-radius: 50%; border: 2px solid #2EA3B7; object-fit: cover; }
.edit-hint { position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%); background: rgba(46,163,183,0.8); color: white; font-size: 10px; padding: 2px 6px; border-radius: 8px; white-space: nowrap; }
.user-info { flex: 1; }
.nickname-row { display: flex; align-items: center; margin-bottom: 8px; }
.nickname { font-size: 20px; font-weight: bold; color: #1D1D2B; margin-right: 8px; }
.edit-icon { font-size: 14px; cursor: pointer; opacity: 0.5; }
.edit-icon:hover { opacity: 1; }
.bio { font-size: 14px; color: #666; margin-bottom: 12px; line-height: 1.4; cursor: pointer; }
.bio:hover { color: #2EA3B7; }
.stats { display: flex; margin-top: 12px; }
.stats .stat-item { margin-right: 24px; text-align: center; }
.stat-num { font-size: 18px; font-weight: bold; color: #1D1D2B; display: block; }
.stat-label { font-size: 12px; color: #666; }

.achievements { display: flex; gap: 16px; margin-top: 16px; overflow-x: auto; }
.achievement-item { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.achievement-icon { font-size: 28px; margin-bottom: 4px; }
.achievement-name { font-size: 12px; color: #666; }

.content-tabs { display: flex; background: #FFFFFF; padding: 12px 16px; margin: 12px 0; }
.tab-item { flex: 1; text-align: center; padding: 8px 0; font-size: 14px; color: #666; cursor: pointer; position: relative; }
.tab-item.active { color: #2EA3B7; font-weight: bold; }
.tab-item.active::after { content: ''; position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); width: 20px; height: 2px; background: #2EA3B7; border-radius: 1px; }

.content-area { padding: 12px; min-height: 200px; }
.loading { display: flex; flex-direction: column; align-items: center; padding: 40px 0; color: #999; }
.loading-spinner { width: 24px; height: 24px; border: 2px solid #f3f3f3; border-top: 2px solid #2EA3B7; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 12px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.empty-hint { text-align: center; padding: 40px 0; color: #999; }
.empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }
.empty-text { font-size: 14px; line-height: 1.5; }
.waterfall { display: flex; justify-content: space-between; gap: 8px; }
.column { width: 48%; }
</style>
