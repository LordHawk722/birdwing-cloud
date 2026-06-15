<template>
  <div class="detail-page">
    <!-- 导航栏 -->
    <div class="detail-nav">
      <button class="back-btn" @click="goBack">← 返回</button>
      <span class="nav-title">帖子详情</span>
      <span class="nav-spacer"></span>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="loading-zone">
      <div class="skeleton" style="height:240px;"></div>
      <div class="skeleton" style="height:100px;margin-top:12px;"></div>
    </div>

    <!-- 内容 -->
    <template v-else-if="post">
      <!-- 图片 -->
      <div v-if="post.images?.length" class="image-section">
        <img :src="imgUrl(post.images[0])" :alt="post.title" class="detail-image" @error="imgError = true" />
      </div>

      <!-- 标题 & 内容 -->
      <div class="content-section">
        <h1 class="post-title">{{ post.title }}</h1>
        <p v-if="post.content" class="post-body">{{ post.content }}</p>

        <!-- 元信息 -->
        <div class="meta-row">
          <div class="author-info" v-if="post.author">
            <span class="author-avatar">{{ post.author.nickname?.[0] || '👤' }}</span>
            <span class="author-name">{{ post.author.nickname || post.author.username }}</span>
          </div>
          <div class="meta-right">
            <span v-if="post.location" class="meta-location">📍 {{ post.location }}</span>
            <span class="meta-time">{{ fmtTime(post.created_at) }}</span>
          </div>
        </div>

        <!-- 操作栏 -->
        <div class="action-bar">
          <button class="action-btn" :class="{ liked: post.is_liked }" @click="toggleLike">
            {{ post.is_liked ? '❤️' : '🤍' }} {{ post.like_count || 0 }}
          </button>
          <span class="action-info">💬 {{ comments.length }} 条评论</span>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="comments-section">
        <h3>评论 ({{ comments.length }})</h3>

        <!-- 发表评论 -->
        <div class="comment-input-row" v-if="auth.isAuthenticated.value">
          <input
            v-model="commentText"
            class="comment-input"
            placeholder="写下你的评论..."
            maxlength="500"
            @keyup.enter="addComment"
          />
          <button class="btn btn-primary comment-btn" @click="addComment" :disabled="!commentText.trim() || commentSubmitting">
            发送
          </button>
        </div>
        <div v-else class="login-hint">
          <router-link to="/login">登录</router-link>后即可发表评论
        </div>

        <!-- 评论列表 -->
        <div v-if="commentsLoading" class="load-more">加载评论中...</div>
        <div v-else-if="comments.length === 0" class="no-comments">暂无评论，来说两句吧</div>
        <div v-else class="comment-list">
          <div v-for="c in comments" :key="c.id" class="comment-item">
            <span class="comment-avatar">{{ c.user?.nickname?.[0] || '👤' }}</span>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-author">{{ c.user?.nickname || c.user?.username || '用户' }}</span>
                <span class="comment-time">{{ fmtTime(c.created_at) }}</span>
              </div>
              <p class="comment-content">{{ c.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 错误 -->
    <div v-else class="error-zone">
      <span>😕</span>
      <p>{{ errorMsg || '帖子不存在' }}</p>
      <button class="btn btn-secondary" @click="goBack">返回</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PostService from '@/api/services/post.js'
import { useAuthStore } from '@/stores/auth.js'
import { getOSSUrl } from '@/config/oss.js'
import { showToast } from '@/utils/toast.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const postId = computed(() => route.params.id)
const loading = ref(true)
const errorMsg = ref('')
const post = ref(null)
const imgError = ref(false)
const comments = ref([])
const commentsLoading = ref(false)
const commentText = ref('')
const commentSubmitting = ref(false)

function imgUrl(url) {
  if (!url) return ''
  if (imgError.value) return ''
  if (url.startsWith('http') || url.startsWith('blob:')) return url
  return getOSSUrl(url, 'large')
}

function fmtTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goBack() { router.back() }

async function loadPost() {
  loading.value = true
  try {
    const res = await PostService.getPostDetail(postId.value)
    post.value = res.data?.data
  } catch (err) {
    errorMsg.value = err?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  commentsLoading.value = true
  try {
    const res = await PostService.getComments(postId.value, 1, 50)
    comments.value = res.data?.data?.items || []
  } catch { /* ignore */ }
  finally { commentsLoading.value = false }
}

async function toggleLike() {
  if (!auth.isAuthenticated.value) { router.push('/login'); return }
  try {
    const res = await PostService.toggleLike(postId.value)
    const data = res.data?.data
    if (data) {
      post.value.is_liked = data.is_liked
      post.value.like_count = data.like_count
    }
  } catch { /* ignore */ }
}

async function addComment() {
  if (!commentText.value.trim()) return
  commentSubmitting.value = true
  try {
    await PostService.createComment(postId.value, commentText.value.trim())
    commentText.value = ''
    showToast('评论成功', 'success')
    await loadComments()
  } catch (err) {
    showToast(err?.message || '评论失败', 'error')
  } finally {
    commentSubmitting.value = false
  }
}

onMounted(() => {
  loadPost()
  loadComments()
})
</script>

<style scoped>
.detail-page { max-width: 680px; margin: 0 auto; min-height: 100vh; background: var(--color-bg); }

/* 导航 */
.detail-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky; top: 0; z-index: 10;
}
.back-btn {
  background: none; border: none; font-size: 14px; color: var(--color-primary);
  cursor: pointer; padding: 4px 0;
}
.nav-title { font-size: 15px; font-weight: 600; color: var(--color-text); }
.nav-spacer { width: 48px; }

/* 图片 */
.image-section { background: #000; }
.detail-image { width: 100%; max-height: 400px; object-fit: contain; display: block; }

/* 内容 */
.content-section { padding: 20px 20px 0; background: var(--color-surface); }
.post-title { font-size: 20px; font-weight: 800; color: var(--color-text); margin-bottom: 12px; }
.post-body { font-size: 15px; line-height: 1.7; color: var(--color-text); white-space: pre-wrap; margin-bottom: 16px; }

.meta-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-top: 1px solid var(--color-border); }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--color-primary-bg); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
}
.author-name { font-size: 14px; font-weight: 600; color: var(--color-text); }
.meta-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.meta-location { font-size: 12px; color: var(--color-text-muted); }
.meta-time { font-size: 12px; color: var(--color-text-muted); }

.action-bar { display: flex; align-items: center; gap: 20px; padding: 12px 0; border-top: 1px solid var(--color-border); margin-top: 12px; }
.action-btn {
  background: none; border: none; font-size: 16px; cursor: pointer; padding: 4px 8px;
  border-radius: var(--radius-sm); transition: background 0.15s;
}
.action-btn:hover { background: var(--color-bg); }
.action-btn.liked { animation: pop 0.3s ease; }
@keyframes pop { 0%,100% { transform: scale(1); } 50% { transform: scale(1.3); } }
.action-info { font-size: 14px; color: var(--color-text-muted); }

/* 评论 */
.comments-section { padding: 20px; background: var(--color-surface); margin-top: 8px; }
.comments-section h3 { font-size: 16px; font-weight: 700; color: var(--color-text); margin-bottom: 16px; }

.comment-input-row { display: flex; gap: 8px; margin-bottom: 20px; }
.comment-input {
  flex: 1; padding: 10px 14px; border: 1px solid var(--color-border);
  border-radius: 20px; font-size: 14px; outline: none; background: var(--color-bg);
}
.comment-input:focus { border-color: var(--color-primary); }
.comment-btn { flex-shrink: 0; padding: 8px 18px; border-radius: 20px; font-size: 13px; }

.login-hint { text-align: center; font-size: 13px; color: var(--color-text-muted); margin-bottom: 20px; }
.login-hint a { color: var(--color-primary); font-weight: 600; }

.no-comments { text-align: center; padding: 30px; color: var(--color-text-muted); font-size: 14px; }

.comment-list { display: flex; flex-direction: column; gap: 16px; }
.comment-item { display: flex; gap: 10px; }
.comment-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: var(--color-primary-bg); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
}
.comment-body { flex: 1; }
.comment-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.comment-author { font-size: 13px; font-weight: 600; color: var(--color-text); }
.comment-time { font-size: 11px; color: var(--color-text-muted); }
.comment-content { font-size: 14px; color: var(--color-text); line-height: 1.5; }

.loading-zone, .error-zone, .load-more { text-align: center; padding: 60px 20px; color: var(--color-text-muted); }
.error-zone span { font-size: 48px; display: block; margin-bottom: 12px; }
.error-zone p { margin-bottom: 16px; }
</style>
