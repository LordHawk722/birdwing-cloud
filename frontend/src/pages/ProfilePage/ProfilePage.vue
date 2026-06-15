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
            <h1>{{ userInfo.nickname || '用户' }}</h1>
            <span v-if="userInfo.id" class="banner-level">观鸟爱好者</span>
          </div>
          <p class="banner-bio" @click="handleEditBio">
            {{ userInfo.bio || '✏️ 点击添加个人介绍，让大家更了解你...' }}
          </p>
          <div class="banner-stats">
            <div><strong>{{ posts.length }}</strong> 发布</div>
            <div class="stat-divider"></div>
            <div><strong>{{ userInfo.like_count || 0 }}</strong> 获赞</div>
            <div class="stat-divider"></div>
            <div><strong>{{ records.length }}</strong> 识别</div>
          </div>
        </div>
        <button class="banner-edit-btn" @click="handleEditProfile">✏️ 编辑资料</button>
      </div>
    </div>

    <!-- 内容区：标签页 + 网格 -->
    <div class="content-section">
      <div class="section-inner">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-block">
          <div class="skeleton" style="height:200px;"></div>
        </div>

        <!-- 标签栏 -->
        <template v-else>
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
            <div v-if="currentContent.length === 0" class="empty-block">
              <span class="empty-emoji">📭</span>
              <h3>{{ emptyText }}</h3>
            </div>
            <div v-else class="content-grid">
              <div v-for="item in currentContent" :key="item.id" class="grid-cell fade-in">
                <HomePoster :poster-data="item" />
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 编辑资料弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="cancelEditProfile">
      <div class="edit-profile-modal">
        <h3>✏️ 编辑资料</h3>
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input
            v-model="editForm.nickname"
            class="input-field"
            placeholder="输入昵称（最多 100 字）"
            maxlength="100"
          />
        </div>
        <div class="form-group">
          <label class="form-label">个人介绍</label>
          <textarea
            v-model="editForm.bio"
            class="input-field input-textarea"
            placeholder="介绍一下自己，让大家更了解你..."
            maxlength="500"
            rows="3"
          ></textarea>
        </div>
        <div v-if="editError" class="error-banner">{{ editError }}</div>
        <div class="modal-buttons">
          <button class="btn btn-secondary" @click="cancelEditProfile" :disabled="editSaving">取消</button>
          <button class="btn btn-primary" @click="saveEditProfile" :disabled="editSaving">
            {{ editSaving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import HomePoster from '@/components/HomePoster.vue'
import UserService from '@/api/services/user.js'
import PostService from '@/api/services/post.js'
import RecognitionService from '@/api/services/recognition.js'
import UploadService from '@/api/services/upload.js'
import { useAuthStore } from '@/stores/auth.js'
import { getOSSUrl } from '@/config/oss.js'
import { showToast, showEditableModal } from '@/utils/toast.js'
import { chooseImages } from '@/utils/helpers.js'

const auth = useAuthStore()

// ---- 状态 ----
const isLoading = ref(true)
const activeTab = ref('posts')
const userInfo = ref({ avatar: '', nickname: '用户', bio: '', level: 1, like_count: 0 })
const posts = ref([])
const likes = ref([])
const records = ref([])

const tabs = computed(() => [
  { key: 'posts', label: '发布', icon: '📷', count: posts.value.length || 0 },
  { key: 'likes', label: '点赞', icon: '❤️', count: likes.value.length || 0 },
  { key: 'records', label: '识别', icon: '🔍', count: records.value.length || 0 },
])

const currentContent = computed(() => {
  if (activeTab.value === 'posts') return posts.value
  if (activeTab.value === 'likes') return likes.value
  return records.value
})

const emptyText = computed(() => ({
  posts: '还没有发布过内容',
  likes: '还没有点赞过内容',
  records: '还没有识别记录',
}[activeTab.value] || '暂无内容'))

const userAvatarUrl = computed(() => {
  const a = userInfo.value.avatar || ''
  if (!a) return 'static/default-avatar.png'
  if (a.startsWith('http') || a.startsWith('blob:')) return a
  // getOSSUrl 已内置处理：uploads/ → 直接相对路径，static/ → 本地静态资源，其他 → OSS
  return getOSSUrl(a, 'avatar')
})

// ---- API 加载 ----
async function loadUserProfile() {
  try {
    const res = await UserService.getCurrentUser()
    const data = res.data?.data
    if (data) {
      userInfo.value = data
      auth.updateUser(data)
    }
  } catch {
    // 静默处理
  }
}

async function loadUserPosts() {
  try {
    const res = await PostService.getPostList(1, 50)
    const items = res.data?.data?.items || []
    const currentUserId = userInfo.value.id
    // 过滤当前用户自己的帖子
    const userPosts = items.filter(p => p.author_id === currentUserId)
    posts.value = userPosts.map(p => ({
      id: p.id,
      imageUrl: p.images?.length ? p.images[0] : '',
      imageHeight: 200 + Math.floor(Math.random() * 80),
      description: p.title,
      views: p.like_count || 0,
      likes: p.comment_count || 0,
    }))
  } catch {
    posts.value = []
  }
}

async function loadRecognitionRecords() {
  try {
    const res = await RecognitionService.getRecords(1, 50)
    const items = res.data?.data?.items || []
    records.value = items.map(r => ({
      id: r.id,
      imageUrl: r.image_url || '',
      imageHeight: 200,
      description: r.result?.length
        ? r.result.map(b => `${b.name} ${Math.round((b.confidence || 0) * 100)}%`).join(' · ')
        : '识别结果',
      accuracy: r.result?.[0] ? `${Math.round(r.result[0].confidence * 100)}%` : '',
      date: r.created_at || '',
      views: 0,
      likes: 0,
    }))
  } catch {
    records.value = []
  }
}

async function loadAllData() {
  isLoading.value = true
  await loadUserProfile()
  await Promise.all([loadUserPosts(), loadRecognitionRecords()])
  isLoading.value = false
}

// ---- 操作 ----
async function handleAvatarClick() {
  try {
    const result = await chooseImages({ count: 1 })
    if (!result.files?.length) return

    // axios 拦截器会自动显示/隐藏 loading，无需手动 showToast
    const uploadRes = await UploadService.uploadImage(result.files[0])
    const uploadedUrl = uploadRes.data?.data?.url
    if (!uploadedUrl) {
      showToast('上传失败：服务器未返回图片地址', 'error')
      return
    }
    // 先本地预览
    userInfo.value.avatar = result.tempFilePaths[0]
    // 更新到后端
    await UserService.updateProfile({ avatar: uploadedUrl })
    // 重新拉取确保数据一致
    await loadUserProfile()
    showToast('头像已更新', 'success')
  } catch (err) {
    showToast(err?.message || '上传失败', 'error')
  }
}

function handleAvatarError() {
  userInfo.value.avatar = ''
}

async function handleEditBio() {
  const r = await showEditableModal('编辑个人介绍', userInfo.value.bio || '')
  if (r.confirm) {
    try {
      await UserService.updateProfile({ bio: r.content || '' })
      userInfo.value.bio = r.content || ''
      auth.updateUser({ bio: r.content || '' })
      showToast('已更新', 'success')
    } catch (err) {
      showToast(err?.message || '更新失败', 'error')
    }
  }
}

// ---- 编辑资料弹窗 ----
const showEditModal = ref(false)
const editSaving = ref(false)
const editError = ref('')
const editForm = reactive({ nickname: '', bio: '' })

function handleEditProfile() {
  editForm.nickname = userInfo.value.nickname || ''
  editForm.bio = userInfo.value.bio || ''
  editError.value = ''
  showEditModal.value = true
}

function cancelEditProfile() {
  if (editSaving.value) return
  showEditModal.value = false
}

async function saveEditProfile() {
  editError.value = ''
  editSaving.value = true
  try {
    const updateData = {}
    const nn = editForm.nickname.trim()
    if (nn && nn !== userInfo.value.nickname) {
      if (nn.length > 100) { editError.value = '昵称不能超过 100 个字符'; editSaving.value = false; return }
      updateData.nickname = nn
    }
    if (editForm.bio !== (userInfo.value.bio || '')) {
      updateData.bio = editForm.bio || ''
    }

    if (Object.keys(updateData).length === 0) {
      showEditModal.value = false
      editSaving.value = false
      return
    }

    await UserService.updateProfile(updateData)
    userInfo.value.nickname = updateData.nickname ?? userInfo.value.nickname
    userInfo.value.bio = updateData.bio ?? userInfo.value.bio
    auth.updateUser({ nickname: userInfo.value.nickname, bio: userInfo.value.bio })
    showEditModal.value = false
    showToast('资料已更新', 'success')
  } catch (err) {
    editError.value = err?.message || '保存失败，请稍后重试'
  } finally {
    editSaving.value = false
  }
}

function switchTab(key) {
  if (activeTab.value !== key) {
    activeTab.value = key
  }
}

onMounted(() => {
  loadAllData()
})
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
  .section-inner { padding: 20px 16px 40px; }
  .content-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
@media (max-width: 480px) {
  .content-grid { grid-template-columns: 1fr; }
  .banner-name-row { flex-direction: column; gap: 6px; }
}

/* ========== 编辑资料弹窗 ========== */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.edit-profile-modal {
  width: 100%; max-width: 420px;
  background: var(--color-surface); border-radius: var(--radius-xl);
  padding: 28px 24px; box-shadow: var(--shadow-xl);
}
.edit-profile-modal h3 {
  font-size: 18px; font-weight: 700; color: var(--color-text);
  margin-bottom: 20px;
}
.form-label {
  display: block; font-size: 13px; font-weight: 600;
  color: var(--color-text); margin-bottom: 6px;
}
.input-field {
  width: 100%; padding: 10px 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  font-size: 14px; color: var(--color-text); background: var(--color-bg);
  transition: border-color var(--transition-fast); outline: none; box-sizing: border-box;
}
.input-field:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(5,150,105,0.1); }
.input-textarea { resize: vertical; min-height: 80px; }
.error-banner {
  background: #fef2f2; color: #dc2626; padding: 10px 14px;
  border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 16px;
  border: 1px solid #fecaca;
}
.modal-buttons {
  display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;
}
.modal-buttons .btn { padding: 8px 20px; font-size: 14px; }
</style>
