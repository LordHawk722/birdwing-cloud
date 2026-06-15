<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-brand-icon">🦜</div>
        <h1>众翼云鉴</h1>
        <p>登录以探索更多鸟类世界</p>
      </div>

      <div class="auth-body">
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input
              v-model="form.username"
              class="input-field"
              placeholder="请输入用户名"
              autocomplete="username"
              :disabled="loading"
            />
            <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <input
              v-model="form.password"
              type="password"
              class="input-field"
              placeholder="请输入密码"
              autocomplete="current-password"
              :disabled="loading"
              @keyup.enter="handleLogin"
            />
            <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
          </div>

          <div v-if="serverError" class="error-banner">
            {{ serverError }}
          </div>

          <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="auth-switch">
          还没有账号？
          <router-link to="/register">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import UserService from '@/api/services/user.js'
import { useAuthStore } from '@/stores/auth.js'
import { showToast } from '@/utils/toast.js'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const loading = ref(false)
const serverError = ref('')
const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })

function validate() {
  let valid = true
  errors.username = ''
  errors.password = ''

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    valid = false
  } else if (form.username.trim().length < 3 || form.username.trim().length > 50) {
    errors.username = '用户名长度为 3-50 个字符'
    valid = false
  }

  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  } else if (form.password.length < 6 || form.password.length > 50) {
    errors.password = '密码长度为 6-50 个字符'
    valid = false
  }

  return valid
}

async function handleLogin() {
  serverError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    const res = await UserService.login(form.username.trim(), form.password)
    const { token, user } = res.data?.data || {}
    if (token && user) {
      auth.setAuth(token, user)
      showToast('登录成功', 'success')
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      serverError.value = '登录失败，服务器返回数据异常'
    }
  } catch (err) {
    const status = err?.statusCode
    if (status === 401) {
      serverError.value = '用户名或密码错误'
    } else if (status === 422) {
      serverError.value = '输入格式不正确，请检查'
    } else {
      serverError.value = err?.message || '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center;
  min-height: calc(100vh - 80px); padding: 40px 20px;
  background: var(--color-bg);
}

.auth-card {
  width: 100%; max-width: 400px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.auth-header {
  text-align: center;
  padding: 40px 24px 32px;
  background: linear-gradient(160deg, #064e3b 0%, #047857 40%, #059669 100%);
}
.auth-brand-icon { font-size: 48px; margin-bottom: 8px; }
.auth-header h1 { font-size: 24px; color: #fff; font-weight: 800; margin-bottom: 4px; }
.auth-header p { font-size: 14px; color: rgba(255,255,255,0.75); }

.auth-body { padding: 32px 24px; }

.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: var(--color-text); margin-bottom: 6px; }

.input-field {
  width: 100%; padding: 12px 16px;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  font-size: 14px; color: var(--color-text); background: var(--color-bg);
  transition: border-color var(--transition-fast); outline: none; box-sizing: border-box;
}
.input-field:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(5,150,105,0.1); }
.input-field:disabled { opacity: 0.6; cursor: not-allowed; }

.error-text { display: block; color: #ef4444; font-size: 12px; margin-top: 4px; }
.error-banner {
  background: #fef2f2; color: #dc2626; padding: 10px 14px;
  border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 16px;
  border: 1px solid #fecaca;
}

.btn-block { width: 100%; display: block; box-sizing: border-box; }

.auth-switch { text-align: center; font-size: 13px; color: var(--color-text-muted); margin-top: 20px; }
.auth-switch a { color: var(--color-primary); font-weight: 600; text-decoration: none; }
.auth-switch a:hover { text-decoration: underline; }
</style>
