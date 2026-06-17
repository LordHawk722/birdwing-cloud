<template>
  <div class="post-detail-page">
    <div v-if="isLoading" class="loading-zone">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="error" class="error-zone">
      <span class="error-icon">😞</span>
      <h3>{{ error }}</h3>
      <button class="btn btn-primary" @click="$router.back()">返回</button>
    </div>

    <article v-else-if="post" class="post-article">
      <!-- 返回按钮 -->
      <button class="back-btn" @click="$router.back()">← 返回</button>

      <!-- 图片 -->
      <div v-if="post.images?.length" class="post-images">
        <img
          v-for="(img, i) in post.images"
          :key="i"
          :src="resolveImageUrl(img)"
          alt=""
          class="post-image"
          @error="$event.target.style.display='none'"
        />
      </div>

      <!-- 作者信息 -->
      <div class="post-author">
        <img
          v-if="post.author?.avatar"
          :src="post.author.avatar"
          class="author-avatar"
          alt=""
          @error="($event.target).style.display='none'"
        />
        <span v-else class="author-avatar author-avatar-text">{{ post.author?.nickname?.charAt(0) || '用' }}</span>
        <div class="author-info">
          <div class="author-name">{{ post.author?.nickname || '匿名用户' }}</div>
          <div class="post-time">{{ formatTime(post.created_at) }}</div>
        </div>
        <span v-if="post.location" class="location-tag">📍 {{ post.location }}</span>
      </div>

      <!-- 标题 -->
      <h1 class="post-title">{{ post.title }}</h1>

      <!-- 正文 -->
      <div class="post-content">{{ post.content || '暂无内容' }}</div>

      <!-- 交互栏 -->
      <div class="post-actions">
        <button class="action-btn" @click="handleLike">
          {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count || 0 }}
        </button>
        <button class="action-btn">
          💬 {{ post.comment_count || 0 }}
        </button>
        <button class="action-btn" @click="handleShare">↗ 分享</button>
        <button v-if="isOwner" class="action-btn edit-btn" @click="openEditModal">✏️ 编辑</button>
        <button v-if="isOwner" class="action-btn delete-btn" @click="handleDelete">🗑 删除</button>
      </div>

      <!-- 评论区 -->
      <div class="comments-section">
        <h3>评论 ({{ post.comment_count || 0 }})</h3>

        <!-- 发表评论 -->
        <div class="comment-form">
          <textarea
            v-model="commentText"
            class="input-field"
            rows="3"
            placeholder="写下你的评论..."
            maxlength="500"
          ></textarea>
          <button
            class="btn btn-primary"
            :disabled="!commentText.trim() || commentSubmitting"
            @click="submitComment"
          >
            {{ commentSubmitting ? '发送中...' : '发表评论' }}
          </button>
        </div>

        <!-- 评论列表 -->
        <div v-if="comments.length > 0" class="comments-list">
          <div v-for="c in comments" :key="c.id" class="comment-item">
            <div class="comment-avatar">
              <img
                v-if="c.user?.avatar"
                :src="resolveImageUrl(c.user.avatar)"
                class="comment-avatar-img"
                @error="e => e.target.style.display = 'none'"
              />
              <span v-if="!c.user?.avatar" class="comment-avatar-text">{{ c.user?.nickname?.charAt(0) || '匿' }}</span>
            </div>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-author">{{ c.user?.nickname || '匿名用户' }}</span>
                <span class="comment-time">{{ formatTime(c.created_at) }}</span>
              </div>
              <p class="comment-content">{{ c.content }}</p>
            </div>
          </div>
        </div>
        <div v-else class="comments-empty">暂无评论，来说点什么吧</div>
      </div>
    </article>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="edit-modal">
        <div class="edit-header">
          <h3>编辑帖子</h3>
          <button class="close-btn" @click="closeEditModal">×</button>
        </div>
        <div class="edit-body">
          <div class="form-group">
            <label>标题</label>
            <input v-model="editForm.title" class="input-field" maxlength="200" />
          </div>
          <div class="form-group">
            <label>内容</label>
            <textarea v-model="editForm.content" class="input-field" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>图片</label>
            <div class="edit-images">
              <div v-for="(img, i) in editForm.images" :key="i" class="edit-img-item">
                <img :src="resolveImageUrl(img)" alt="" />
                <button class="img-remove" @click="editForm.images.splice(i, 1)">×</button>
              </div>
              <button class="add-img-btn" @click="uploadEditImage">+ 添加图片</button>
            </div>
          </div>
          <div class="form-group">
            <label>位置</label>
            <div class="location-input-wrap">
              <input
                ref="editLocationInput"
                v-model="editForm.location"
                class="input-field"
                placeholder="输入位置名称（从下拉建议中选择）..."
                autocomplete="off"
                @input="editLocationConfirmed = false"
              />
              <div v-if="editLocationSuggestions.length > 0" class="location-dropdown">
                <div
                  v-for="(s, i) in editLocationSuggestions"
                  :key="i"
                  class="location-item"
                  @mousedown.prevent="selectEditLocation(s)"
                >
                  <span class="loc-name">{{ s.name }}</span>
                  <span class="loc-addr">{{ s.address }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="edit-footer">
          <button class="btn btn-secondary" @click="closeEditModal">取消</button>
          <button class="btn btn-primary" :disabled="editSubmitting" @click="submitEdit">
            {{ editSubmitting ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showActionSheet, showModal } from '@/utils/toast.js'
import { formatRelativeTime, chooseImages } from '@/utils/helpers.js'
import { useAuthStore } from '@/stores/auth.js'
import PostService from '@/api/services/post.js'
import UploadService from '@/api/services/upload.js'

const BAIDU_MAP_KEY = import.meta.env.VITE_BAIDU_MAP_API_KEY || ''

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const post = ref(null)
const comments = ref([])
const isLoading = ref(true)
const error = ref('')
const commentText = ref('')
const commentSubmitting = ref(false)

// 编辑相关
const showEditModal = ref(false)
const editSubmitting = ref(false)
const editForm = ref({ title: '', content: '', images: [], location: '' })
const editLocationInput = ref(null)
const editLocationSuggestions = ref([])
const editLocationConfirmed = ref(false)
let editAcInstance = null

const isOwner = computed(() => {
  const uid = auth.user.value?.id
  const authorId = post.value?.author?.id
  // 兼容 id 为数字或字符串的情况
  return uid != null && authorId != null && String(uid) === String(authorId)
})

function resolveImageUrl(img) {
  if (!img) return ''
  if (img.startsWith('http') || img.startsWith('blob:')) return img
  if (img.startsWith('/')) return img
  return '/' + img
}

function formatTime(t) {
  if (!t) return ''
  return formatRelativeTime(t)
}

async function loadPost() {
  isLoading.value = true
  error.value = ''
  try {
    const res = await PostService.getPostDetail(route.params.id)
    post.value = res.data?.data
  } catch (err) {
    if (err?.statusCode === 404) error.value = '帖子不存在或已被删除'
    else error.value = '加载失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

async function loadComments() {
  try {
    const res = await PostService.getComments(route.params.id, 1, 50)
    comments.value = res.data?.data?.items || []
  } catch { /* 静默失败 */ }
}

async function handleLike() {
  if (!post.value) return
  try {
    const res = await PostService.toggleLike(post.value.id)
    const d = res.data?.data
    if (d) {
      post.value.is_liked = d.is_liked
      post.value.like_count = d.like_count
    }
  } catch (err) {
    if (err?.statusCode === 401) showToast('请先登录', 'none')
  }
}

function handleShare() {
  const url = `${window.location.origin}/post/${post.value.id}`
  const title = post.value.title || '分享帖子'
  // 手机：原生分享
  if (navigator.share) {
    navigator.share({ title, url }).catch(() => {})
    return
  }
  // HTTPS / localhost：Clipboard API
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(url).then(() => {
      showToast('链接已复制到剪贴板', 'success')
    }).catch(() => {
      showToast('复制失败，请手动复制链接', 'error')
    })
    return
  }
  // HTTP 环境：降级用 textarea + execCommand
  const textarea = document.createElement('textarea')
  textarea.value = url
  textarea.style.position = 'fixed'; textarea.style.left = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
    showToast('链接已复制到剪贴板', 'success')
  } catch {
    showToast('复制失败，请手动复制链接', 'error')
  } finally {
    document.body.removeChild(textarea)
  }
}

async function submitComment() {
  if (!commentText.value.trim()) return
  commentSubmitting.value = true
  try {
    const res = await PostService.createComment(post.value.id, commentText.value.trim())
    const newComment = res.data?.data
    if (newComment) {
      comments.value.unshift(newComment)
      post.value.comment_count = (post.value.comment_count || 0) + 1
    }
    commentText.value = ''
    showToast('评论成功', 'success')
  } catch (err) {
    if (err?.statusCode === 401) showToast('请先登录后再评论', 'none')
    else showToast(err?.message || '评论失败', 'error')
  } finally {
    commentSubmitting.value = false
  }
}

// ===== 编辑功能 =====
function openEditModal() {
  editForm.value = {
    title: post.value.title || '',
    content: post.value.content || '',
    images: [...(post.value.images || [])],
    location: post.value.location || '',
  }
  editLocationConfirmed.value = true
  showEditModal.value = true
  nextTick(() => { initEditAutocomplete() })
}

function closeEditModal() {
  showEditModal.value = false
  editLocationSuggestions.value = []
  if (editAcInstance) { editAcInstance.dispose(); editAcInstance = null }
}

function loadBaiduScriptForEdit() {
  return new Promise((resolve) => {
    if (window.BMap) { resolve(); return }
    if (document.querySelector('script[src*="api.map.baidu.com"]')) {
      // 等待已存在的脚本加载
      const check = setInterval(() => { if (window.BMap) { clearInterval(check); resolve() } }, 200)
      return
    }
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${BAIDU_MAP_KEY}&callback=onBaiduMapForEdit`
    window.onBaiduMapForEdit = () => { resolve() }
    document.head.appendChild(script)
  })
}

async function initEditAutocomplete() {
  if (!BAIDU_MAP_KEY) return
  await loadBaiduScriptForEdit()
  await nextTick()
  if (!window.BMap || !editLocationInput.value) return
  if (editAcInstance) { editAcInstance.dispose(); editAcInstance = null }
  editAcInstance = new BMap.Autocomplete({ input: editLocationInput.value, location: '全国' })
  editAcInstance.addEventListener('onsearchcomplete', () => {
    const result = editAcInstance.getResults()
    if (result && result.getNumPois) {
      const n = result.getNumPois()
      const list = []
      for (let i = 0; i < n; i++) {
        const poi = result.getPoi(i)
        list.push({ name: poi.title || '', address: poi.address || '' })
      }
      editLocationSuggestions.value = list
    } else {
      editLocationSuggestions.value = []
    }
  })
  editAcInstance.addEventListener('onconfirm', (e) => {
    const val = e.item.value
    const parts = []
    if (val.province) parts.push(val.province)
    if (val.city) parts.push(val.city)
    if (val.district) parts.push(val.district)
    if (val.business) parts.push(val.business)
    if (val.street) parts.push(val.street)
    editForm.value.location = parts.join('') || val.business || e.item.value
    editLocationConfirmed.value = true
    editLocationSuggestions.value = []
  })
}

function selectEditLocation(s) {
  editForm.value.location = s.name
  editLocationConfirmed.value = true
  editLocationSuggestions.value = []
}

async function uploadEditImage() {
  try {
    const result = await chooseImages({ count: 1 })
    if (result.files.length) {
      showToast('上传中...', 'none')
      const res = await UploadService.uploadImage(result.files[0])
      const url = res.data?.data?.url
      if (url) editForm.value.images.push(url)
    }
  } catch { showToast('上传失败', 'error') }
}

async function submitEdit() {
  if (!editForm.value.title.trim()) return showToast('标题不能为空', 'none')
  editSubmitting.value = true
  try {
    const payload = {
      title: editForm.value.title.trim(),
      content: editForm.value.content.trim(),
      images: editForm.value.images,
      location: editForm.value.location.trim(),
    }
    await PostService.updatePost(post.value.id, payload)
    // 更新本地数据
    post.value.title = payload.title
    post.value.content = payload.content
    post.value.images = payload.images
    post.value.location = payload.location
    showToast('修改已保存', 'success')
    closeEditModal()
  } catch (err) {
    showToast(err?.message || '保存失败', 'error')
  } finally {
    editSubmitting.value = false
  }
}

async function handleDelete() {
  const ok = await showModal('确认删除', '删除后无法恢复，确定要删除这篇帖子吗？')
  if (!ok) return
  try {
    await PostService.deletePost(post.value.id)
    showToast('已删除', 'success')
    router.push('/')
  } catch (err) {
    showToast(err?.message || '删除失败', 'error')
  }
}

onMounted(() => {
  loadPost()
  loadComments()
})
</script>

<style scoped>
.post-detail-page { max-width: 720px; margin: 0 auto; padding: 24px 20px 80px; }

.loading-zone, .error-zone {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 20px; gap: 16px;
}
.error-icon { font-size: 48px; opacity: 0.6; }
.error-zone h3 { font-size: 16px; color: var(--color-text-secondary); }

.back-btn {
  background: none; border: none; font-size: 14px; color: var(--color-primary);
  cursor: pointer; padding: 8px 0; margin-bottom: 16px; font-weight: 600;
}
.back-btn:hover { text-decoration: underline; }

.post-images { margin-bottom: 20px; }
.post-image {
  width: 100%; max-height: 480px; object-fit: cover;
  border-radius: var(--radius-lg); background: var(--color-bg);
}

.post-author {
  display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
  flex-wrap: wrap;
}
.author-avatar {
  width: 44px; height: 44px; border-radius: 50%; object-fit: cover;
  border: 2px solid var(--color-border); flex-shrink: 0;
}
.author-avatar-text {
  background: var(--color-primary-bg); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; border: none;
}
.author-info { flex: 1; }
.author-name { font-size: 15px; font-weight: 600; color: var(--color-text); }
.post-time { font-size: 12px; color: var(--color-text-muted); }
.location-tag {
  font-size: 12px; color: var(--color-primary);
  background: var(--color-primary-bg); padding: 4px 10px;
  border-radius: var(--radius-full); font-weight: 500;
}

.post-title { font-size: 24px; font-weight: 800; margin-bottom: 16px; color: var(--color-text); }

.post-content {
  font-size: 15px; line-height: 1.8; color: var(--color-text-secondary);
  white-space: pre-wrap; margin-bottom: 24px;
}

.post-actions {
  display: flex; gap: 16px; padding: 16px 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 24px;
}
.action-btn {
  background: var(--color-bg); border: 1px solid var(--color-border);
  padding: 8px 16px; border-radius: var(--radius-md);
  font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.action-btn:hover { background: var(--color-border); }

/* 评论 */
.comments-section h3 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
.comment-form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.comment-form .input-field {
  width: 100%; padding: 10px 14px; font-size: 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-bg); outline: none; resize: vertical;
  box-sizing: border-box;
}
.comment-form .input-field:focus { border-color: var(--color-primary); }
.comment-form .btn { align-self: flex-end; }

.comments-list { display: flex; flex-direction: column; gap: 16px; }
.comment-item { display: flex; gap: 12px; }
.comment-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-primary-bg); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; flex-shrink: 0; overflow: hidden;
}
.comment-avatar-img {
  width: 100%; height: 100%; object-fit: cover;
}
.comment-avatar-text {
  font-size: 14px; font-weight: 700;
}
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; gap: 10px; align-items: baseline; margin-bottom: 4px; }
.comment-author { font-size: 13px; font-weight: 600; color: var(--color-text); }
.comment-time { font-size: 11px; color: var(--color-text-muted); }
.comment-content { font-size: 14px; color: var(--color-text-secondary); line-height: 1.6; }
.comments-empty { text-align: center; padding: 40px; color: var(--color-text-muted); font-size: 14px; }

.loading-spinner {
  width: 28px; height: 28px;
  border: 3px solid var(--color-border); border-top-color: var(--color-primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.edit-btn { color: var(--color-accent); border-color: var(--color-accent); }
.delete-btn { color: #ef4444; border-color: #ef4444; }

/* 编辑弹窗 */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 300;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.edit-modal {
  background: var(--color-surface); border-radius: var(--radius-xl);
  width: 100%; max-width: 560px; max-height: 85vh; overflow-y: auto;
  animation: modalIn 0.25s ease;
}
@keyframes modalIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

.edit-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px; border-bottom: 1px solid var(--color-border);
}
.edit-header h3 { font-size: 18px; font-weight: 700; }
.edit-header .close-btn {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: var(--color-bg); font-size: 18px; cursor: pointer;
}

.edit-body { padding: 20px 24px; }
.edit-body .form-group { margin-bottom: 16px; }
.edit-body label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--color-text); }
.edit-body .input-field {
  width: 100%; padding: 10px 12px; font-size: 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  background: var(--color-bg); outline: none; box-sizing: border-box;
}
.edit-body .input-field:focus { border-color: var(--color-primary); }
.edit-body textarea.input-field { resize: vertical; }

.edit-images { display: flex; flex-wrap: wrap; gap: 10px; }
.edit-img-item { position: relative; }
.edit-img-item img { width: 80px; height: 60px; object-fit: cover; border-radius: var(--radius-sm); }
.img-remove {
  position: absolute; top: -6px; right: -6px;
  width: 18px; height: 18px; border-radius: 50%; border: none;
  background: #ef4444; color: #fff; font-size: 12px; cursor: pointer;
}
.add-img-btn {
  width: 80px; height: 60px; border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm); background: var(--color-bg);
  cursor: pointer; font-size: 12px; color: var(--color-text-muted);
  transition: all 0.2s;
}
.add-img-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

.edit-body .location-input-wrap { position: relative; }
.edit-body .location-dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 310;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-lg);
  max-height: 180px; overflow-y: auto;
}
.edit-body .location-item {
  padding: 8px 12px; cursor: pointer; border-bottom: 1px solid var(--color-border);
}
.edit-body .location-item:last-child { border-bottom: none; }
.edit-body .location-item:hover { background: var(--color-primary-bg); }
.edit-body .loc-name { font-size: 13px; font-weight: 600; display: block; }
.edit-body .loc-addr { font-size: 11px; color: var(--color-text-muted); }

.edit-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .post-detail-page { padding: 16px 12px 80px; }
  .post-title { font-size: 20px; }
  .edit-modal { max-width: 100%; border-radius: var(--radius-xl) var(--radius-xl) 0 0; max-height: 90vh; }
}
</style>
