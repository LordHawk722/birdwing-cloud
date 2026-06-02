/**
 * 本地存储工具 - Web版本
 * 替换 uni.getStorageSync / uni.setStorageSync / uni.removeStorageSync
 */

export const STORAGE_KEYS = {
  TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  SETTINGS: 'app_settings',
  SEARCH_HISTORY: 'search_history',
  FAVORITE_BIRDS: 'favorite_birds',
  UPLOAD_DRAFTS: 'upload_drafts',
  CHAT_HISTORY: 'chat_history'
}

/**
 * 获取存储值
 * @param {string} key
 * @returns {any}
 */
export function getStorageSync(key) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : null
  } catch (error) {
    console.error('读取存储失败:', error)
    return null
  }
}

/**
 * 设置存储值
 * @param {string} key
 * @param {any} value
 */
export function setStorageSync(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error('写入存储失败:', error)
  }
}

/**
 * 移除存储值
 * @param {string} key
 */
export function removeStorageSync(key) {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error('删除存储失败:', error)
  }
}

/**
 * 获取Token
 * @returns {string|null}
 */
export function getToken() {
  return getStorageSync(STORAGE_KEYS.TOKEN)
}

/**
 * 设置Token
 * @param {string} token
 */
export function setToken(token) {
  setStorageSync(STORAGE_KEYS.TOKEN, token)
}

/**
 * 清除Token
 */
export function clearToken() {
  removeStorageSync(STORAGE_KEYS.TOKEN)
  removeStorageSync(STORAGE_KEYS.REFRESH_TOKEN)
  removeStorageSync(STORAGE_KEYS.USER_INFO)
}

export default {
  getStorageSync,
  setStorageSync,
  removeStorageSync,
  getToken,
  setToken,
  clearToken
}
