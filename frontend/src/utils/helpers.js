/**
 * 通用工具函数 - Web版本
 * 移除 uni 依赖，使用浏览器原生API
 */

// ========== 防抖节流 ==========
export function debounce(func, wait, immediate = false) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func.apply(this, args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func.apply(this, args)
  }
}

export function throttle(func, limit) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// ========== 深拷贝 ==========
export function deepClone(obj) {
  if (obj === null || typeof obj !== "object") return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === "object") {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) clonedObj[key] = deepClone(obj[key])
    }
    return clonedObj
  }
}

// ========== 文件大小格式化 ==========
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

// ========== 时间格式化 ==========
export function formatRelativeTime(timestamp) {
  const now = new Date()
  const date = new Date(timestamp)
  const diff = now - date
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day
  const year = 365 * day

  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  if (diff < week) return `${Math.floor(diff / day)}天前`
  if (diff < month) return `${Math.floor(diff / week)}周前`
  if (diff < year) return `${Math.floor(diff / month)}个月前`
  return `${Math.floor(diff / year)}年前`
}

export function formatDate(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  const date = new Date(timestamp)
  const formatMap = {
    YYYY: date.getFullYear(),
    MM: String(date.getMonth() + 1).padStart(2, '0'),
    DD: String(date.getDate()).padStart(2, '0'),
    HH: String(date.getHours()).padStart(2, '0'),
    mm: String(date.getMinutes()).padStart(2, '0'),
    ss: String(date.getSeconds()).padStart(2, '0')
  }
  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, match => formatMap[match])
}

// ========== 随机字符串/UUID ==========
export function randomString(length = 8, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

// ========== 验证函数 ==========
export function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function validatePhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

export function validateIdCard(idCard) {
  return /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(idCard)
}

// ========== 数组工具 ==========
export function uniqueArray(arr, key = null) {
  if (!key) return [...new Set(arr)]
  const seen = new Set()
  return arr.filter(item => {
    const value = item[key]
    if (seen.has(value)) return false
    seen.add(value)
    return true
  })
}

export function groupBy(arr, key) {
  return arr.reduce((groups, item) => {
    const group = typeof key === 'function' ? key(item) : item[key]
    groups[group] = groups[group] || []
    groups[group].push(item)
    return groups
  }, {})
}

export function paginate(arr, page = 1, size = 10) {
  const startIndex = (page - 1) * size
  const endIndex = startIndex + size
  return {
    data: arr.slice(startIndex, endIndex),
    total: arr.length,
    page,
    size,
    totalPages: Math.ceil(arr.length / size),
    hasNext: endIndex < arr.length,
    hasPrev: page > 1
  }
}

// ========== URL工具 ==========
export function objectToQueryString(obj) {
  return Object.keys(obj)
    .filter(key => obj[key] !== undefined && obj[key] !== null)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
    .join('&')
}

export function getUrlParam(name, url = window.location.href) {
  const urlParams = new URLSearchParams(new URL(url).search)
  return urlParams.get(name)
}

// ========== 格式化 ==========
export function formatCurrency(amount, currency = '¥', decimals = 2) {
  return currency + Number(amount).toFixed(decimals).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}

export function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

// ========== 设备信息（Web版本） ==========
export function getDeviceInfo() {
  const ua = navigator.userAgent
  return {
    platform: /Mobile/.test(ua) ? 'mobile' : 'desktop',
    system: navigator.platform || 'web',
    screenWidth: window.innerWidth,
    screenHeight: window.innerHeight,
    pixelRatio: window.devicePixelRatio || 1,
    language: navigator.language
  }
}

// ========== 图片工具（Web版本） ==========
export function chooseImages(options = {}) {
  const { count = 1, accept = 'image/*' } = options
  return new Promise((resolve, reject) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = accept
    input.multiple = count > 1
    input.onchange = (e) => {
      const files = Array.from(e.target.files)
      const urls = files.map(f => URL.createObjectURL(f))
      resolve({ tempFilePaths: urls, files })
    }
    input.onerror = reject
    input.click()
  })
}

export function previewImages(urls, current = 0) {
  const urlArray = Array.isArray(urls) ? urls : [urls]
  // 简单的图片预览 - 创建全屏覆盖层
  const overlay = document.createElement('div')
  overlay.style.cssText = `
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.9); z-index: 10000;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
  `
  const img = document.createElement('img')
  img.src = urlArray[current] || urlArray[0]
  img.style.cssText = 'max-width: 90vw; max-height: 90vh; object-fit: contain;'
  overlay.appendChild(img)
  overlay.onclick = () => overlay.remove()
  document.body.appendChild(overlay)
}

// ========== 剪贴板 ==========
export async function copyToClipboard(data) {
  try {
    await navigator.clipboard.writeText(data)
    return true
  } catch (error) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = data
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    return true
  }
}

// ========== 振动反馈（Web版本） ==========
export function vibrate(type = 'short') {
  if (navigator.vibrate) {
    if (type === 'short') {
      navigator.vibrate(15)
    } else if (type === 'medium') {
      navigator.vibrate(30)
    } else if (type === 'long') {
      navigator.vibrate(200)
    }
  }
}

// ========== 地理位置（Web版本） ==========
export function getCurrentLocation(options = {}) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('浏览器不支持地理定位'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          speed: position.coords.speed
        })
      },
      (error) => reject(error),
      {
        enableHighAccuracy: options.enableHighAccuracy || false,
        timeout: options.timeout || 10000,
        maximumAge: 0
      }
    )
  })
}

// ========== 网络状态（Web版本） ==========
export function getNetworkInfo() {
  return {
    networkType: navigator.onLine ? 'wifi' : 'none',
    isConnected: navigator.onLine
  }
}

export default {
  debounce,
  throttle,
  deepClone,
  formatFileSize,
  formatRelativeTime,
  formatDate,
  randomString,
  generateUUID,
  validateEmail,
  validatePhone,
  validateIdCard,
  uniqueArray,
  groupBy,
  paginate,
  objectToQueryString,
  getUrlParam,
  formatCurrency,
  formatNumber,
  getDeviceInfo,
  chooseImages,
  previewImages,
  copyToClipboard,
  vibrate,
  getCurrentLocation,
  getNetworkInfo
}
