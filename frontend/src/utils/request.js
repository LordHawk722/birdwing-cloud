/**
 * 网络请求工具 - Web版本
 * 基于axios封装，替换 uni.request / uni.uploadFile
 */
import axios from 'axios'
import { API_CONFIG, STATUS_CODES, ERROR_MESSAGES, STORAGE_KEYS } from '@/config/api.js'
import { getStorageSync, setStorageSync, removeStorageSync } from './storage.js'
import { showToast, showLoading, hideLoading } from './toast.js'
import eventBus from './eventBus.js'

// 创建axios实例
const http = axios.create({
  timeout: API_CONFIG.TIMEOUT || 10000,
  headers: {
    ...API_CONFIG.HEADERS
  }
})

// 请求队列（防重复）
const requestQueue = new Map()
const loadingStates = new Set()

// 生成请求标识
function generateRequestId(config) {
  const { url, method, data } = config
  const dataStr = data ? JSON.stringify(data) : ''
  return `${method}_${url}_${dataStr}`.replace(/[^a-zA-Z0-9]/g, '_')
}

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 添加Token
    const token = getStorageSync(STORAGE_KEYS.TOKEN)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加客户端信息
    config.headers['X-Client-Type'] = 'web'
    config.headers['X-Client-Version'] = '1.0.0'

    // 显示loading
    const requestId = generateRequestId(config)
    if (config.showLoading !== false) {
      loadingStates.add(requestId)
      showLoading(config.loadingText || '加载中...')
    }

    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    const { status, data } = response

    // 隐藏loading
    const requestId = generateRequestId(response.config)
    loadingStates.delete(requestId)
    if (loadingStates.size === 0) hideLoading()

    if (status >= 200 && status < 300) {
      return { data, statusCode: status, success: true }
    } else {
      return Promise.reject({
        statusCode: status,
        data,
        message: data?.message || ERROR_MESSAGES[status] || ERROR_MESSAGES.UNKNOWN_ERROR
      })
    }
  },
  (error) => {
    // 隐藏loading
    loadingStates.clear()
    hideLoading()

    if (error.response) {
      const { status } = error.response

      // 处理401未授权
      if (status === STATUS_CODES.UNAUTHORIZED) {
        removeStorageSync(STORAGE_KEYS.TOKEN)
        removeStorageSync(STORAGE_KEYS.REFRESH_TOKEN)
        removeStorageSync(STORAGE_KEYS.USER_INFO)
        eventBus.emit('tokenExpired')
        showToast('登录已过期，请重新登录', 'error')
        return Promise.reject(new Error(ERROR_MESSAGES.INVALID_TOKEN))
      }

      // 处理403
      if (status === STATUS_CODES.FORBIDDEN) {
        showToast(ERROR_MESSAGES.FORBIDDEN, 'error')
        return Promise.reject(new Error(ERROR_MESSAGES.FORBIDDEN))
      }

      return Promise.reject({
        statusCode: status,
        message: ERROR_MESSAGES[status] || ERROR_MESSAGES.UNKNOWN_ERROR
      })
    }

    // 网络错误
    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        statusCode: STATUS_CODES.REQUEST_TIMEOUT,
        message: ERROR_MESSAGES.TIMEOUT_ERROR,
        isTimeout: true
      })
    }

    return Promise.reject({
      statusCode: 0,
      message: ERROR_MESSAGES.NETWORK_ERROR,
      isNetworkError: true
    })
  }
)

// 导出便捷方法
export const request = http
export const get = http.get
export const post = http.post
export const put = http.put
export const del = http.delete

/**
 * 上传文件
 * @param {string} url - 上传地址
 * @param {File} file - 文件对象
 * @param {Function} onProgress - 进度回调
 * @returns {Promise}
 */
export function uploadFile(url, file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  return http.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 30000,
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
        onProgress(progress)
      }
    }
  })
}

export default http
