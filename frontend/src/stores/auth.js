/**
 * 认证状态管理 — 基于 Vue 3 reactive() + computed()
 * 零额外依赖，兼容 Pinia 风格 API
 */
import { reactive, computed } from 'vue'
import { getStorageSync, setStorageSync, removeStorageSync } from '@/utils/storage.js'

const STORAGE_TOKEN_KEY = 'access_token'
const STORAGE_USER_KEY = 'user_info'

const state = reactive({
  token: getStorageSync(STORAGE_TOKEN_KEY) || null,
  user: getStorageSync(STORAGE_USER_KEY) || null,
})

export function useAuthStore() {
  const isAuthenticated = computed(() => !!state.token)
  const user = computed(() => state.user)
  const token = computed(() => state.token)

  function setAuth(tokenVal, userVal) {
    state.token = tokenVal
    state.user = userVal
    setStorageSync(STORAGE_TOKEN_KEY, tokenVal)
    setStorageSync(STORAGE_USER_KEY, userVal)
  }

  function clearAuth() {
    state.token = null
    state.user = null
    removeStorageSync(STORAGE_TOKEN_KEY)
    removeStorageSync('refresh_token')
    removeStorageSync(STORAGE_USER_KEY)
  }

  function updateUser(userVal) {
    state.user = { ...state.user, ...userVal }
    setStorageSync(STORAGE_USER_KEY, state.user)
  }

  return { isAuthenticated, user, token, setAuth, clearAuth, updateUser, state }
}
