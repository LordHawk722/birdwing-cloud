<template>
  <div class="profile-root">
    <!-- 顶部个人信息横幅（全宽绿色背景） -->
    <div class="profile-banner">
      <div class="banner-inner">
        <div class="banner-avatar" @click="handleAvatarClick">
          <img :src="userAvatarUrl" alt="头像" @error="handleAvatarError" />
          <div class="avatar-overlay">📷</div>
        </div>
        <div class="banner-info">
          <div class="banner-name-row">
            <h1>{{ userInfo.nickname }}</h1>
            <span class="banner-level">Lv.{{ userInfo.level }}</span>
          </div>
          <p class="banner-bio" @click="handleEditBio">
            {{ userInfo.bio || '✏️ 点击添加个人介绍，让大家更了解你...' }}
          </p>
          <div class="banner-stats">
            <div><strong>{{ userInfo.postsCount }}</strong> 发布</div>
            <div class="stat-divider"></div>
            <div><strong>{{ userInfo.likesCount }}</strong> 获赞</div>
            <div class="stat-divider"></div>
            <div><strong>128</strong> 粉丝</div>
            <div class="stat-divider"></div>
            <div><strong>56</strong> 关注</div>
          </div>
        </div>
        <button class="banner-edit-btn" @click="handleEditProfile">✏️ 编辑资料</button>
      </div>
    </div>

    <!-- 成就条（浅金色背景） -->
    <div class="achievement-strip">
      <div class="strip-inner">
        <span class="strip-label">🏅 成就</span>
        <span class="achievement-tag earned">🐣 初级观鸟员</span>
        <span class="achievement-tag earned">📸 摄影新手</span>
        <span class="achievement-tag locked">🔒 资深摄影师</span>
        <span class="achievement-tag locked">🔒 鸟类专家</span>
      </div>
    </div>

    <!-- 内容区：标签页 + 网格（浅灰背景） -->
    <div class="content-section">
      <div class="section-inner">
        <!-- 标签栏 -->
        <div class="content-tabs">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="content-tab"
            :class="{ active: activeTab === t.key }"
            @click="switchTab(t.key)"
          >
            <span class="tab-emoji">{{ t.icon }}</span>
            {{ t.label }}
            <span v-if="t.count" class="tab-badge">{{ t.count }}</span>
          </button>
        </div>

        <!-- 内容 -->
        <div class="content-body">
          <div v-if="isLoading" class="loading-block">
            <div class="skeleton" style="height:200px;"></div>
          </div>
          <div v-else-if="currentContent.length === 0" class="empty-block">
            <span class="empty-emoji">📭</span>
            <h3>{{ emptyText }}</h3>
          </div>
          <div v-else class="content-grid">
            <div v-for="item in currentContent" :key="item.id" class="grid-cell fade-in">
              <HomePoster :poster-data="item" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HomePoster from '@/components/HomePoster.vue'
import { UserService } from '@/api/services/user.js'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showEditableModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'

const userService = new UserService()

export default {
  name: 'ProfilePage',
  components: { HomePoster },
  data() {
    return {
      isLoading: false,
      activeTab: 'posts',
      tabs: [
        { key: 'posts', label: '发布', icon: '📷', count: 12 },
        { key: 'likes', label: '点赞', icon: '❤️', count: 88 },
        { key: 'records', label: '识别', icon: '🔍', count: 5 },
      ],
      userInfo: { avatar: 'static/default-avatar.png', nickname: '鸟类爱好者', bio: '', postsCount: 12, likesCount: 256, level: 5 },
      posts: [],
      likes: [],
      records: [],
    }
  },
  computed: {
    currentContent() { return this[this.activeTab] || [] },
    emptyText() { return { posts: '还没有发布过内容', likes: '还没有点赞过内容', records: '还没有识别记录' }[this.activeTab] || '暂无内容' },
    userAvatarUrl() {
      const a = this.userInfo.avatar || 'static/default-avatar.png'
      if (a.startsWith('http') || a.startsWith('blob:')) return a
      return getOSSUrl(a, 'medium')
    }
  },
  async mounted() {
    try { this.userInfo.bio = await userService.getIntro() || '' } catch {}
    this.loadContent()
  },
  methods: {
    async handleAvatarClick() {
      try { const r = await chooseImages({ count: 1 }); if (r.tempFilePaths.length) { this.userInfo.avatar = r.tempFilePaths[0]; showToast('头像已更新', 'success') } } catch { showToast('上传失败', 'error') }
    },
    handleAvatarError() { this.userInfo.avatar = 'static/default-avatar.png' },
    async handleEditBio() {
      const r = await showEditableModal('编辑个人介绍', this.userInfo.bio)
      if (r.confirm) { this.userInfo.bio = r.content || ''; showToast('已更新', 'success') }
    },
    handleEditProfile() { showToast('编辑功能开发中', 'none') },
    switchTab(key) { if (this.activeTab !== key) { this.activeTab = key; this.loadContent() } },
    async loadContent() {
      this.isLoading = true
      await new Promise(r => setTimeout(r, 400))
      const mockPosts = [
        { id: 1, imageUrl: 'static/posts/bird1.jpg', imageHeight: 200, description: '今天拍到的小鸟，太可爱了！', views: 1234, likes: 88 },
        { id: 2, imageUrl: 'static/posts/bird2.jpg', imageHeight: 240, description: '清晨的候鸟迁徙场景', views: 2567, likes: 189 },
        { id: 3, imageUrl: 'static/posts/bird3.jpg', imageHeight: 180, description: '蜂鸟悬停采蜜的瞬间', views: 543, likes: 23 },
        { id: 4, imageUrl: 'static/posts/bird4.jpg', imageHeight: 260, description: '金刚鹦鹉的绚烂色彩', views: 876, likes: 45 },
        { id: 5, imageUrl: 'static/posts/bird1.jpg', imageHeight: 210, description: '春天的白头鹎', views: 320, likes: 16 },
        { id: 6, imageUrl: 'static/posts/bird2.jpg', imageHeight: 230, description: '翠鸟捕鱼精彩瞬间', views: 410, likes: 28 },
      ]
      const mockLikes = [
        { id: 7, imageUrl: 'static/posts/bird2.jpg', imageHeight: 220, description: '好漂亮的鸟儿！', views: 2567, likes: 189 },
        { id: 8, imageUrl: 'static/posts/bird3.jpg', imageHeight: 200, description: '太可爱了，收藏了', views: 890, likes: 67 },
      ]
      const mockRecords = [
        { id: 9, imageUrl: 'static/recognition/bird1.jpg', imageHeight: 220, description: '红头长尾山雀', accuracy: '98%', date: '2024-03-20' },
        { id: 10, imageUrl: 'static/recognition/bird2.jpg', imageHeight: 200, description: '白头硬尾鹎', accuracy: '97%', date: '2024-03-18' },
      ]
      if (this.activeTab === 'posts') this.posts = mockPosts
      else if (this.activeTab === 'likes') this.likes = mockLikes
      else this.records = mockRecords
      this.isLoading = false
    },
  }
}
</script>

<style scoped>
.profile-root { background: var(--color-bg); min-height: 100vh; }

/* ========== 个人信息横幅 ========== */
.profile-banner {
  background: linear-gradient(160deg, #064e3b 0%, #047857 30%, #059669 60%, #10b981 100%);
  padding: 48px 0 36px;
}
.banner-inner {
  max-width: 1000px; margin: 0 auto; padding: 0 32px;
  display: flex; align-items: center; gap: 28px;
  position: relative;
}
.banner-avatar {
  position: relative; cursor: pointer; flex-shrink: 0;
}
.banner-avatar img {
  width: 88px; height: 88px; border-radius: 50%;
  border: 4px solid rgba(255,255,255,0.3); object-fit: cover;
  transition: transform 0.2s;
}
.banner-avatar:hover img { transform: scale(1.05); }
.avatar-overlay {
  position: absolute; bottom: 0; right: 0;
  width: 26px; height: 26px; background: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.banner-info { flex: 1; color: #fff; }
.banner-name-row { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.banner-name-row h1 { font-size: 26px; font-weight: 800; }
.banner-level {
  background: rgba(255,255,255,0.2); backdrop-filter: blur(4px);
  padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;
}
.banner-bio {
  font-size: 14px; opacity: 0.8; margin-bottom: 14px;
  cursor: pointer; transition: opacity 0.2s; max-width: 500px;
}
.banner-bio:hover { opacity: 1; }
.banner-stats { display: flex; align-items: center; gap: 16px; font-size: 13px; }
.banner-stats strong { font-size: 16px; margin-right: 3px; }
.stat-divider { width: 1px; height: 16px; background: rgba(255,255,255,0.25); }

.banner-edit-btn {
  padding: 8px 18px; border-radius: 20px;
  background: rgba(255,255,255,0.15); color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
  flex-shrink: 0;
}
.banner-edit-btn:hover { background: rgba(255,255,255,0.25); }

/* ========== 成就条 ========== */
.achievement-strip {
  background: linear-gradient(90deg, #fffbeb, #fef3c7, #fffbeb);
  border-bottom: 2px solid rgba(245,158,11,0.1);
  padding: 0;
}
.strip-inner {
  max-width: 1000px; margin: 0 auto; padding: 12px 32px;
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
}
.strip-label { font-size: 13px; font-weight: 700; color: #92400e; margin-right: 4px; }
.achievement-tag {
  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
.achievement-tag.earned { background: rgba(245,158,11,0.15); color: #92400e; }
.achievement-tag.locked { background: rgba(0,0,0,0.04); color: #b0b0b0; }

/* ========== 内容区 ========== */
.content-section {
  background: linear-gradient(180deg, #f9fafb 0%, #f3f4f6 100%);
  min-height: 500px;
}
.section-inner { max-width: 1000px; margin: 0 auto; padding: 24px 32px 48px; }

.content-tabs {
  display: flex; gap: 2px;
  background: #fff; border-radius: 12px; padding: 3px;
  margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  width: fit-content;
}
.content-tab {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 20px; border-radius: 10px;
  background: transparent; color: var(--color-text-secondary);
  font-size: 13px; font-weight: 600; cursor: pointer; border: none;
  transition: all 0.2s;
}
.content-tab.active { background: var(--color-primary); color: #fff; }
.content-tab:not(.active):hover { background: var(--color-bg); }
.tab-emoji { font-size: 15px; }
.tab-badge {
  background: rgba(255,255,255,0.25); padding: 1px 7px;
  border-radius: 10px; font-size: 10px; font-weight: 700;
}
.content-tab.active .tab-badge { background: rgba(255,255,255,0.3); }

.content-body { min-height: 400px; }

.content-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.loading-block { padding: 20px 0; }
.empty-block {
  text-align: center; padding: 80px 40px;
  background: #fff; border-radius: 16px;
  border: 1px dashed #ddd;
}
.empty-emoji { font-size: 56px; display: block; margin-bottom: 16px; opacity: 0.35; }
.empty-block h3 { font-size: 15px; color: var(--color-text-secondary); }

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .content-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
  .banner-inner { flex-direction: column; text-align: center; gap: 16px; padding: 0 20px; }
  .banner-stats { justify-content: center; }
  .banner-bio { margin-left: auto; margin-right: auto; }
  .banner-edit-btn { position: static; }
  .strip-inner { padding: 12px 20px; }
  .section-inner { padding: 20px 16px 40px; }
  .content-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
@media (max-width: 480px) {
  .content-grid { grid-template-columns: 1fr; }
  .banner-name-row { flex-direction: column; gap: 6px; }
}
</style>
